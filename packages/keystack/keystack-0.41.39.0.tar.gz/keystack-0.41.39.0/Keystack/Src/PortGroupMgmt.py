import os, traceback, json
from pprint import pprint

from commonLib import logSession, logDebugMsg
from db import DB
from globalVars import GlobalVars
from LoggingAssistants import TestSessionLoggerAssistant
from keystackUtilities import readJson, writeToJson
from RedisMgr import RedisMgr

class Vars:
    webpage = 'portGroup'
    
    
def isActiveUserRunning(overallSummaryFile: str) -> bool:
    """ 
    overallSummaryFile: From MongoDB active-user's overallSummaryFile
    
    If a pipeline session process ID is terminated, the memory is still running.
    It leaves behind a reservation in activeUsers and it just sits there when the
    pipeline is already dead.  
    
    When a new pipeline task wants to reserve the env, it needs to check if the
    active-user is terminated or aborted.  In this case, remove from activeUsers
    list to allow new tasks to use the env.
    """
    if os.path.exists(overallSummaryFile) is False:
        # The MongodDB active-user sesison could be deleted already.
        # So the overallSummaryFile does not exists
        return False
    
    # The overallSummaryFile exists. Check the status
    data = readJson(overallSummaryFile)
    if data['status'] == 'Running':
        return True
    else:
        return False
        
        
class ManagePortGroup():
    def __init__(self, domain: str=None, portGroup: str=None):
        self.domain = domain
        self.portGroup = portGroup
        self.keystackLogger = None
    
    def setupLogger(self, logFile):
        self.keystackLogger = TestSessionLoggerAssistant(testSessionLogFile=logFile)

    def getPortGroupDetails(self):
        data = DB.name.getOneDocument(collectionName=Vars.webpage,
                                      fields={'domain': self.domain, 'name': self.portGroup},
                                      includeFields={'_id': 0})
        return data

    def removeDeviceFromPortGroup(self, deviceName):
        results = DB.name.removeKeyFromDocument(collectionName=Vars.webpage, 
                                                queryFields={'domain': self.domain, 'name': self.portGroup},
                                                updateFields={"$unset": {f'ports.{deviceName}': 1}})

    def removeDevicesFromPortGroupIfNoPorts(self):
        data = self.getPortGroupDetails()

        for device, properties in data['ports'].items():
            if len(properties['ports']) == 0:
                self.removeDeviceFromPortGroup(device)
                        
    def isActiveUserHoldingEnvOnFailure(self, overallSummaryFile=None):
        """
        OverallSummaryFile: The requesting pipeline's overallSummary file
        """
        data = self.getPortGroupDetails()
        if data is None:
            return False
        
        if len(data['activeUsers']) > 0:
            # Env current status from MongoDB
            currentActiveUser = data['activeUsers'][0]

            # Get the active-user task summary data
            activeUserSessionId          = currentActiveUser['sessionId']
            activeUserUser               = currentActiveUser['user']
            activeUserStage              = currentActiveUser['stage']
            activeUserTask               = currentActiveUser['task']
            env                          = currentActiveUser['env']
            activeUserOverallSummaryFile = currentActiveUser['overallSummaryFile']
            
            if env:
                envWithDashes = env.replace('/', '-')
            else:
                envWithDashes = 'None'
            
            if activeUserOverallSummaryFile:
                activeUserResultsPath    = activeUserOverallSummaryFile.replace('/overallSummary.json', '')
            else:
                # If active-user has no overallSummary file, this means the user manually reserved the env
                return False
            
            activeUserTimestampFolderName = activeUserOverallSummaryFile.replace('/overallSummary.json', '').split('/')[-1]
            activeUserTimestampRootPath = activeUserOverallSummaryFile.replace('/overallSummary.json', '')
            activeUserCurrentStageTaskSummaryFile = f'{activeUserResultsPath}/STAGE={activeUserStage}_TASK={activeUserTask}_ENV={envWithDashes}/taskSummary.json'
            redisEnvMgmtKeyName = f'envMgmt-{activeUserTimestampFolderName}-STAGE={activeUserStage}_TASK={activeUserTask}_ENV={envWithDashes}' 
            activeUserEnvMgmtFile = f'{activeUserTimestampRootPath}/.Data/EnvMgmt/STAGE={activeUserStage}_TASK={activeUserTask}_ENV={envWithDashes}.json'

            if overallSummaryFile == activeUserOverallSummaryFile:
                return False
            
            # Verify if the active-user has holdEnvsIfFailed = True and envIsReleased = False -> return False
            if RedisMgr.redis:
                activeUserEnvMgmtData = RedisMgr.redis.getCachedKeyData(keyName=redisEnvMgmtKeyName)
            else:
                activeUserEnvMgmtData = readJson(activeUserEnvMgmtFile)
 
            if activeUserEnvMgmtData['holdEnvsIfFailed']:
                if activeUserEnvMgmtData['envIsReleased'] is False:
                    # holdEnvsIfFailed is True and user has not released the env 
                    return True 
                else:
                    return False
            else:
                return False       
                                    
    def createPortGroup(self):
        response = DB.name.insertOne(collectionName=Vars.webpage, data={'name': self.portGroup,
                                                                        'ports': {},
                                                                        'domain': self.domain,
                                                                        'loadBalanceGroups': [],
                                                                        'available': True,
                                                                        'activeUsers': [],
                                                                        'waitList': []})
        return response.acknowledged

    def update(self, key: str=None, value: str=None, fields: dict=None) -> bool:
        """
        Pass in either key/value or fields.
         
        key:      <str>: The dict key to update along with the value 
        fields : <dict>: could contain multiple key: values
        """
        if key:
            return DB.name.updateDocument(collectionName=Vars.webpage,
                                          queryFields={'domain': self.domain, 'name': self.portGroup},
                                          updateFields={key: value})
        if fields:
            return DB.name.updateDocument(collectionName=Vars.webpage,
                                          queryFields={'domain': self.domain, 'name': self.portGroup},
                                          updateFields=fields)
                    
    def isPortGroupExists(self):
        return DB.name.isDocumentExists(collectionName=Vars.webpage, keyValue={'domain': self.domain, 'name': self.portGroup})
                        
    def getAllPortGroups(self, domain=None):
        if domain == 'all':
            portGroupsObj = DB.name.getDocuments(collectionName=Vars.webpage, fields={},
                                                includeFields={'_id':0, 'name':1, 'domain': 1, 'activeUsers': 1, 'waitList': 1}, 
                                                sortBy=[('name', 1)], limit=None)
        else:
            portGroupsObj = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': self.domain},
                                                includeFields={'_id':0, 'name':1}, sortBy=[('name', 1)], limit=None)
                                                                
        #Note: portGroupObj is an one-time use generator.
        #      Have to make a permanent copy for reuse in the for loop 
        portGroups = [pg for pg in portGroupsObj]
        # [{'name': 'port-group-2'}, {'name': 'portGroup1'}
        return portGroups

    def getAllPorts(self) -> dict:
        """ 
        Get all the ports associated with the port-group
        
        ports:
            device:
                domain: <domain>
                ports:
                    - 1/1
                    - 1/2   
        """
        data = self.getPortGroupDetails()
        if data:
            return data['ports']

    def getPortGroupPorts(self) -> dict:
        """ 
        {'activeUsers': [],
         'available': True,
         'domain': 'Communal',
         'loadBalanceGroups': [],
         'name': 'portGroup1',
         'ports': {'device_1': {'domain': 'Communal', 'ports': ['1/1', '1/2']}},
         'waitList': []}
        """
        data = self.getPortGroupDetails()
        if data:
            return data['ports']
        else:
            return {}
                                    
    def removePortGroup(self):
        """ 
        Return True on success
        Return False on failed
        """
        return DB.name.deleteOneDocument(collectionName=Vars.webpage, fields={'domain': self.domain, 'name': self.portGroup})

    def reservePortGroup(self, sessionId=None, overallSummaryFile=None, user=None, stage=None, task=None, env=None, trackUtilization=False):
        """ 
        Reserving a port-group for both manual button reserver and Keystack auto reserve.
        
        For manual reservation: Only sessionId and user is required
        
        overallSummaryFile: User requesting to use the port-group
        
        trackUtilization <bool>: For keystack.py.lockAndWaitForEnv().  This function calls reserveEnv() and amIRunning().
                            Both functions increment env utilization. We want to avoid hitting it twice.
                            So exclude hitting it here in reserveEnv and let amIRunning hit it.
        """
        try:
            message = 'No Port-Group used'
            updateDB = True
            
            # data is from MongoDB. active-users and waitlist
            data = self.getPortGroupDetails()

            if overallSummaryFile and self.keystackLogger:
                testResultRootPath = overallSummaryFile.replace('/overallSummary.json', '')
                sessionLog = f'{testResultRootPath}/{GlobalVars.sessionLogFilename}'                        
                self.setupLogger(sessionLog)
                self.keystackLogger.info(f'PortGroupMgmt.reservePortGroup: sessionId={sessionId} stage={stage} task={task} portGroup={self.portGroup}: data: {json.dumps(data, indent=4)}')

            # data is None if the task doesn't use an Env
            if data:
                if len(data['activeUsers']) == 0:
                    if overallSummaryFile and self.keystackLogger:
                        self.keystackLogger.info(f'reservePortGroup: Port-Group={self.portGroup} sessionId={sessionId} stage={stage} task={task}: activeUsers=0. Reserving.')
                        
                    data['available'] = False 
                    data['activeUsers'].append({'sessionId': sessionId, 'overallSummaryFile': overallSummaryFile,
                                                'user': user, 'stage': stage, 'task': task, 'env': env})
                    message = f'reservePortGroup: Reserving port-group as active-user: Port-Group:{self.portGroup}  user:{user}  session:{sessionId}  stage:{stage}  task:{task}'
                else:
                    updateDB = False
                    if overallSummaryFile and self.keystackLogger:
                        self.keystackLogger.info(f'reservePortGroup: activeUsers > 0. Go to wait-list.  sessionId={sessionId} stage={stage} task={task} portGroup={self.portGroup}')

                    # Go to wait list because someone is actively using the port-group
                    data['waitList'].append({'sessionId': sessionId, 'overallSummaryFile': overallSummaryFile, 
                                             'user': user, 'stage': stage, 'task': task, 'env': env})
                    dbObj = DB.name.updateDocument(Vars.webpage,
                                                   queryFields={'domain': self.domain, 'name': self.portGroup},
                                                   updateFields=data)

                    # overallSummaryFile: User requesting to use the port-group
                    if overallSummaryFile:
                        isEnvOnHold = self.isActiveUserHoldingEnvOnFailure(overallSummaryFile)
                        if isEnvOnHold is False:
                            overallSummaryData = readJson(overallSummaryFile)
                            pipelineSession = overallSummaryData['topLevelResultFolder']  

                            for activeUser in data['activeUsers']:
                                # Cannot expect the active-user have an overallSummaryFile because the user might have manually reserved the env.
                                if activeUser['overallSummaryFile']:
                                    if pipelineSession != activeUser['overallSummaryFile'].split('/')[-1]:
                                        if isActiveUserRunning(overallSummaryFile=activeUser['overallSummaryFile']) is False:
                                            if overallSummaryFile and self.keystackLogger:
                                                self.keystackLogger.info(f"[amIRunning]: Not Running!  Calling removeFromActiveUsersList() to remove user={activeUser['user']} stage={activeUser['stage']} task={activeUser['task']} portGroup={self.portGroup}")

                                            self.removeFromActiveUsersList([{'user': activeUser['user'], 
                                                                            'sessionId': activeUser['sessionId'], 
                                                                            'stage': activeUser['stage'], 
                                                                            'task': activeUser['task']}])
                                    else:
                                        # The active-user is me running. returning True
                                        return True                                               
                            
                if updateDB:
                    if overallSummaryFile and self.keystackLogger:
                        self.keystackLogger.info(f'PortGroupMgmt.reservePortGroup: Updating DB: Domain={self.domain} PortGroup={self.portGroup} data: {json.dumps(data, indent=4)}')

                    dbObj = DB.name.updateDocument(Vars.webpage,
                                                   queryFields={'domain': self.domain, 'name': self.portGroup},
                                                   updateFields=data)

                    if dbObj:
                        if overallSummaryFile and self.keystackLogger:
                            self.keystackLogger.info(f'PortGroupMgmt.reservePortGroup: Updated DB: sessionId={sessionId} stage={stage} task={task} Domain={self.domain} PortGroup={self.portGroup}')

                        return ('success', message)
                    else:
                        if overallSummaryFile and self.keystackLogger:
                            self.keystackLogger.error(f'PortGroupMgmt.reservePortGroup: Updating DB failed: sessionId={sessionId} stage={stage} task={task} Domain={self.domain}  PortGroup={self.portGroup}')
                            
                        return ('failed', 'PortGroupMgmt.reservePortGroup: Updating PortGroup DB failed')
                else:
                    return ('success', '')
            else:
                if overallSummaryFile and self.keystackLogger:
                    self.keystackLogger.error(f'PortGroupMgmt.reservePortGroup: PortGroup has no data: sessionId={sessionId} stage={stage} task={task} Domain={self.domain}  PortGroup={self.portGroup}')
                    
                return ('failed', f'[ReservePortGroup]: mongoDB portGroupMgmt has no data: domain={self.domain} port-group={self.portGroup}')
            
        except Exception as errMsg:
            if overallSummaryFile and self.keystackLogger:
                self.keystackLogger.error(f'PortGroupMgmt.reservePortGroup: sessionId={sessionId} stage={stage} task={task} Domain={self.domain}  PortGroup={self.portGroup}: {traceback.format_exc(None, errMsg)}')
            return ('failed', traceback.format_exc(None, errMsg))
                                            
    def releasePortGroup(self):
        """ 
        The Release button. For manual release only.
        Mostly likely the env is in a stuck or weird state that needs to be updated. 
        Release the current activeUsers session/person on the env
        """
        try:
            data = self.getPortGroupDetails()
            if data:
                if len(data['activeUsers']) > 0:
                    data['activeUsers'].pop(0)
                    
                    if len(data['waitList']) > 0:
                        data['activeUsers'].append(data['waitList'][0])
                        data['waitList'].pop(0)
                    else:
                        data.update({'available': True})

                dbObj = DB.name.updateDocument(Vars.webpage,
                                               queryFields={'domain': self.domain, 'name': self.portGroup},
                                               updateFields=data)

                if dbObj:
                    return 'success'
                else:
                    return ('failed', 'ReleasePortGroup: Updating Port-Group DB failed')
        
        except Exception as errMsg:
            return ('failed', str(errMsg))
        
    def resetPortGroup(self):
        """
        Blank out the Port-Group
        
        Return
            True|False
        """
        result = DB.name.updateDocument(Vars.webpage,
                                        queryFields={'domain': self.domain, 'name': self.portGroup},
                                        updateFields={'available':True, 'activeUsers':[], 'waitList':[]})
        return result

    def isPortGroupAvailable(self):
        try:
            self.refreshPortGroup()  
            data = self.getPortGroupDetails()
            if data:
                if data['available']:
                    return True
                else:
                    return False
            else:
                return False

        except Exception as errMsg:
            return False
    
    def isPortGroupActiveOrInWaitlist(self):
        """ 
        Verify if the port-group is actively used or if it's in the wait list
        
        Returns False if the port-group is completely free
        """
        data = self.getPortGroupDetails()
        if data:
            if len(data['activeUsers']) == 0 and len(data['waitList']) == 0:
                return False
            else:
                return True
        else:
            return True    
                                                          
    def isPortGroupNextInLine(self, sessionId, user=None, stage=None, task=None, env=None):
        """
        Check the waitlist if the sessionId is next.
        If it is next:
            - Remove the sessionid from the wait list
            - Add the sessionId to the activeUsers list
            - set 'available' to False
        """
        iAmNext = False
        data = self.getPortGroupDetails()
        if data:
            for index,nextWaiting in enumerate(data['waitList']):
                # {"task": "LoadCore",
                #  "stage": "Test",
                #  "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                #  "user": "rocky"}
                nextSessionId = nextWaiting['sessionId']
                nextUser = nextWaiting['User']
                nextStage = nextWaiting['stage']
                nextTask = nextWaiting['task']
                nextEnv = nextWaiting['env']
                
                if sessionId == nextSessionId:
                    if stage is None:
                        # Manually reserved env is next to use it
                        iAmNext = True
                        break
                    
                    if user == nextUser and stage == nextStage and task == nextTask:
                        iAmNext = True
                        break
        
            if iAmNext:
                # Update active-user
                DB.name.updateDocument(Vars.webpage,
                                       queryFields={'domain': self.domain, 'name': self.portGroup}, 
                                       updateFields={'activeUsers': {'user': user, 
                                                                       'sessionId': sessionId, 
                                                                       'task': task,
                                                                       'stage': stage,
                                                                       'env': env},
                                                                       'available': False}, 
                                       appendToList=True)
                
                # Update wait-list
                DB.name.updateDocument(Vars.webpage, 
                                       queryFields={'domain': self.domain, 'name': self.portGroup}, 
                                       updateFields={'waitList': {'sessionId': nextSessionId, 'user': nextUser,
                                                                  'stage': nextStage, 'task': nextTask, 'env': nextEnv}}, 
                                       removeFromList=True)

            else:
                return False
                
    def getActiveUsers(self):
        data = self.getPortGroupDetails()
        if data:
            return data['activeUsers']
    
    def isUserInActiveUsersList(self, user):
        for eachUser in self.getActiveUsers():
            if eachUser['stage'] == None:
                if eachUser['user'] == user:
                    return True

    def getWaitList(self):
        data = self.getPortGroupDetails()
        if data:
            return data['waitList']

    def isUserInWaitList(self, user):
        for eachUser in self.getWaitList():
            if eachUser['stage'] == None:
                if eachUser['user'] == user:
                    return True
                
    def goToWaitList(self, sessionId=None, user=None, stage=None, task=None, env=None):
        dbObj = DB.name.updateDocument(Vars.webpage,
                                       queryFields={'domain': self.domain, 'name': self.portGroup}, 
                                       updateFields={'waitList': {'sessionId': sessionId, 
                                                                  'user': user, 
                                                                  'stage': stage, 
                                                                  'task': task,
                                                                  'env': env}},
                                      appendToList=True)

    def selfUpdateActiveUsersAndWaitList(self):
        """ 
        Called by EnvMgmt.update()
        Remove all stale sessions in the wait-list
        """
        try:
            currentPipelines = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'overallSummary-domain=*')
            
            for portGroup in self.getAllPortGroups(domain='all'):
                self.portGroup = portGroup['name']
                self.domain = portGroup['domain']            
                data = self.getPortGroupDetails()

                if data is None:
                    # data is None if the task doesn't use an Env
                    continue
                
                for index, waitingSessionData in enumerate(data['waitList']):
                    # {'sessionId': '04-28-2025-11:26:08:335418_7269', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-28-2025-11:26:08:335418_7269/overallSummary.json', 'user': 'CLI: hgee', 'stage': 'setup', 'task': 'bringup', 'env': 'DOMAIN=Communal-Samples-demoEnv1'}

                    nextUser = waitingSessionData['user']
                    nextStage = waitingSessionData['stage']
                    nextTask = waitingSessionData['task']
                    nextSessionId = waitingSessionData['sessionId']

                    isEnvSessionIdInCurrentPipelines = False
                    
                    # Check if the waitlist sessionId is in the current pipelines
                    for pipeline in currentPipelines:
                        if nextSessionId in pipeline:
                            # The env is in active-user queue
                            isEnvSessionIdInCurrentPipelines = pipeline
                            # Check if the pipeline status is running and if the Env holdEnvsIfFailed=True
                            pipelineData = RedisMgr.redis.getCachedKeyData(keyName=isEnvSessionIdInCurrentPipelines)
                            if pipelineData['status'] != 'Running':
                                dbObj = DB.name.updateDocument(Vars.webpage, 
                                                               queryFields={'domain': self.domain, 'name': self.portGroup},
                                                               updateFields={'waitList': {'sessionId':nextSessionId,
                                                                                           'user': nextUser,
                                                                                           'stage': nextStage,
                                                                                           'task': nextTask}},
                                                               removeFromList=True)

                    # The env sessionId in the wait-list is not in the pipeline         
                    if isEnvSessionIdInCurrentPipelines is False:
                        dbObj = DB.name.updateDocument(Vars.webpage, 
                                                       queryFields={'domain': self.domain, 'name': self.portGroup},
                                                       updateFields={'waitList': {'sessionId':nextSessionId,
                                                                                   'user': nextUser,
                                                                                   'stage': nextStage,
                                                                                   'task': nextTask}},
                                                       removeFromList=True)
                        
                for index, activeSessionData in enumerate(data['activeUsers']):
                    # {'sessionId': '04-28-2025-11:26:08:335418_7269', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-28-2025-11:26:08:335418_7269/overallSummary.json', 'user': 'CLI: hgee', 'stage': 'setup', 'task': 'bringup', 'env': 'DOMAIN=Communal-Samples-demoEnv1'}

                    nextUser = activeSessionData['user']
                    nextStage = activeSessionData['stage']
                    nextTask = activeSessionData['task']
                    nextSessionId = activeSessionData['sessionId']

                    isEnvSessionIdInCurrentPipelines = False
                    
                    # Check if the waitlist sessionId is in the current pipelines
                    for pipeline in currentPipelines:
                        if nextSessionId in pipeline:
                            # The env is in active-user queue
                            isEnvSessionIdInCurrentPipelines = pipeline
                            # Check if the pipeline status is running and if the Env holdEnvsIfFailed=True
                            pipelineData = RedisMgr.redis.getCachedKeyData(keyName=isEnvSessionIdInCurrentPipelines)
                            
                            # Check if there is a stage name.  No stage name means the port-group is manually reserved
                            if pipelineData['status'] != 'Running' and nextStage:
                                dbObj = DB.name.updateDocument(Vars.webpage, 
                                                               queryFields={'domain': self.domain, 'name': self.portGroup},
                                                               updateFields={'activeUsers': {'sessionId':nextSessionId,
                                                                                             'user': nextUser,
                                                                                             'stage': nextStage,
                                                                                             'task': nextTask}},
                                                               removeFromList=True)

                    # The env sessionId in the wait-list is not in the pipeline  
                    # Check if there is a stage name.  No stage name means the port-group is manually reserved       
                    if isEnvSessionIdInCurrentPipelines is False and nextStage:
                        dbObj = DB.name.updateDocument(Vars.webpage, 
                                                       queryFields={'domain': self.domain, 'name': self.portGroup},
                                                       updateFields={'activeUsers': {'sessionId':nextSessionId,
                                                                                     'user': nextUser,
                                                                                     'stage': nextStage,
                                                                                     'task': nextTask}},
                                                       removeFromList=True)
                        
        except Exception as errMsg:
            print(f'PortGroupMgmt.self.UpdateWaitList: {traceback.format_exc(None, errMsg)}')
                    
    def removeAllSessionIdFromWaitList(self, sessionId, logFile=None):
        """ 
        Called by terminateProcessId.
        Remove all sessionId from waitList
        """
        try:
            if logFile:
                self.setupLogger(logFile)
            
            for portGroup in self.getAllPortGroups():
                self.portGroup = portGroup['name']            
 
                data = self.getPortGroupDetails()
                if logFile:
                    self.keystackLogger.info(f'PortGroupMgmt.removeAllSessionIdFromWaitList: PortGroup={self.portGroup} sessionId={sessionId} data={json.dumps(data, indent=4)}')
                
                if data is None:
                    # data is None if the task doesn't use an Env
                    return
                
                for index, waitingSessionData in enumerate(data['waitList']):
                    nextUser = waitingSessionData['user']
                    nextStage = waitingSessionData['stage']
                    nextTask = waitingSessionData['task']

                    if waitingSessionData['sessionId'] == sessionId:
                        dbObj = DB.name.updateDocument(Vars.webpage, 
                                                       queryFields={'domain': self.domain, 'name': self.portGroup},
                                                       updateFields={'waitList': {'sessionId':sessionId,
                                                                                   'user': nextUser,
                                                                                   'stage': nextStage,
                                                                                   'task': nextTask}},
                                                       removeFromList=True)
                        if logFile:
                            self.keystackLogger.info(f'PortGroupMgmt.removeAllSessionIdFromWaitList: Removed sessionId={sessionId} from Port-Group waitlist. result={dbObj}')
                        
                # verify
                if logFile:
                    data = self.getPortGroupDetails()
                    self.keystackLogger.info(f'PortGroupMgmt.removeAllSessionIdFromWaitListverify: data: {json.dumps(data, indent=4)}')
            
        except Exception as errMsg:
            if logFile:
                self.keystackLogger.error(f'PortGroupMgmt.removeAllSessionIdFromWaitList: {traceback.format_exc(None, errMsg)}')
            return errMsg
        
    def removeAllSessionIdFromActiveUsersList(self, sessionId, logFile=None):
        """ 
        Called by terminateProcessId.
        Remove all sessionId from active users list in all port-groups
        """
        try:
            getSessionIdInWaitingList = None
            removeFlag = False
            if logFile:
                self.setupLogger(logFile)

            for portGroup in self.getAllPortGroups():
                self.portGroup = portGroup['name']
                data = self.getPortGroupDetails()
                if logFile:
                    self.keystackLogger.info(f'PortGroupMgmt: removeAllSessionIdFromActiveUsersList: portGroup={portGroup} sessionId={sessionId} data={json.dumps(data, indent=4)}')
                
                if data is None:
                    #  None if the task doesn't use an Env
                    return
                      
                if len(data['activeUsers']) > 0:
                    for index, activeUser in enumerate(data['activeUsers']):
                        if activeUser['sessionId'] == sessionId:
                            removeFlag = True
                            stage = activeUser['stage']
                            task = activeUser['task']
                            data['activeUsers'].pop(index)
                            getSessionIdInWaitingList = sessionId
                            dbObj = DB.name.updateDocument(Vars.webpage, queryFields={'domain': self.domain, 'name': self.portGroup}, updateFields=data)
                            if logFile:
                                self.keystackLogger.info(f'PortGroupMgmt: removeAllSessionIdFromActiveUsersList: Removed sessionId {sessionId} in active-user. Active-user is {data["activeUsers"]}')
                            
                            # Get the testSession.log file and update the session env tracker      
                            timestampFolderRootPath = activeUser["overallSummaryFile"].replace('/overallSummary.json', '')
                            sessionLog = f'{timestampFolderRootPath}/{GlobalVars.sessionLogFilename}'
                            
                    result = self.refreshPortGroup(sessionLog, getSessionIdInWaitingList=getSessionIdInWaitingList)
                    if result:
                        # Verify
                        data = self.getPortGroupDetails()
                        if logFile:
                            self.keystackLogger.info(f'PortGroupMgmt: removeAllSessionIdFromActiveUsersList: verify data: {json.dumps(data, indent=4)}')
                    
        except Exception as errMsg:
            if logFile:
                self.keystackLogger.error(f'PortGroupMgmt: removeAllSessionIdFromActiveUsersList: {traceback.format_exc(None, errMsg)}')
            return errMsg

    def removeFromActiveUsersListUI(self, removeList):
        """ 
        This function will:
           - Remove the sessionId from the active list
           - Get the next sessionId in the wait list and put it into the active user list.
           - Set avaiable = False
           
        removeList: [{'user':user, 'sessionId':sessionId, 'stage':stage, 'task':task}]
        
        Return
            success | error message
        """
        try:
            removeFlag = False
            sessionLog = None
            
            # removeList:[{'sessionId': '16:26:22:473288_9750', 'stage': 'Test', 'task': 'standAloneTests', 'user': 'Hubert Gee'}] 
            for activeUser in removeList:
                sessionId = activeUser['sessionId']
                envData = None
                
                if activeUser['stage'] == 'None': 
                    stage = None
                else:
                    stage = activeUser['stage']
                    
                if activeUser['task'] == 'None':
                    task = None
                else:
                    task = activeUser['task']  

                data = self.getPortGroupDetails()
                # data:
                #     data: {'_id': ObjectId('6445be5889e17be32c818fcc'), 'env': 'DOMAIN=Communal/Samples/hubert', 'available': False, 'activeUsers': [{'sessionId': '04-23-2023-16:44:54:605093_hgee', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/04-23-2023-16:44:54:605093_hgee/overallSummary.json', 'user': 'hgee', 'stage': 'Bringup', 'task': 'CustomPythonScripts'}], 'waitList': []}
                if data:
                    if len(data['activeUsers']) > 0:
                        getSessionIdInWaitingList = None
                        for index, user in enumerate(data['activeUsers']):
                            sessionLog = None       
                            if user['sessionId'] == sessionId and \
                                user['stage'] == stage and \
                                user['task'] == task:
                                    data['activeUsers'].pop(index)
                                    removeFlag = True
                                    getSessionIdInWaitingList = sessionId
                                    dbObj = DB.name.updateDocument(Vars.webpage, 
                                                                   queryFields={'domain': self.domain, 
                                                                                'name': self.portGroup}, 
                                                                   updateFields=data)
                                    
                                    if user["overallSummaryFile"]:
                                        # Get the testSession.log file and update the session env tracker      
                                        timestampFolderRootPath = user["overallSummaryFile"].replace('/overallSummary.json', '')
                                        sessionLog = f'{timestampFolderRootPath}/{GlobalVars.sessionLogFilename}'
                                        self.setupLogger(sessionLog)                                    
                                                                                                           
                                    if sessionLog:
                                        self.keystackLogger.info(f'PortGroupMgmt.removeFromActiveUsersListUI: Removed and updated data with: {json.dumps(data, indent=4)}')
                                        data = self.getPortGroupDetails()
                                        self.keystackLogger.info(f'PortGroupMgmt.removeFromActiveUsersListUI: Verifying updated data: {json.dumps(data, indent=4)}')
                                        verifyingUpdateResult = True
                                        for user in data['activeUsers']: 
                                            if user['sessionId'] == sessionId and \
                                                user['stage'] == stage and \
                                                user['task'] == task:
                                                    verifyingUpdateResult = False
                                                    self.keystackLogger.info(f'PortGroupMgmt.removeFromActiveUsersListUI: Verifying updated active-user failed. The user session still in active-user list: {json.dumps(data, indent=4)}')
                                                    
                                        if verifyingUpdateResult:
                                            self.keystackLogger.info(f'PortGroupMgmt.removeFromActiveUsersListUI: Verifying updated data success! STAGE={stage}_TASK={task} Port-Group={self.portGroup} is removed in activeUsers')
            if removeFlag:
                # Get the next in waiting. Search for same sessionID from the waitList to give priority to 
                # the same pipeline session to go first
                return self.refreshPortGroup(sessionLog, getSessionIdInWaitingList=getSessionIdInWaitingList)
        
        except Exception as errMsg:
            errorMsg = f'PortGroupMgmt.removeFromActiveUsersList: error: {traceback.format_exc(None, errMsg)}'
            if sessionLog: logSession(sessionLog, f'{errorMsg}')
            return errorMsg

    def removeFromWaitList(self, sessionId, user=None, stage=None, task=None):
        """ 
        Remove a user/sessionId from the wait-list
        """
        try:
            data = self.getPortGroupDetails()
            if data is None:
                # Task doesn't use an Port-Group
                return
            
            for index,userData in enumerate(data['waitList']):
                nextUser = userData['user']
                nextSessionId = userData['sessionId']
                nextStage = userData['stage']
                nextTask = userData['task']
                
                if stage in [None, 'None']:
                    # Manual user
                    if sessionId == nextSessionId and user == nextUser:
                        dbObj = DB.name.updateDocument(Vars.webpage,
                                                       queryFields={'domain': self.domain, 'name': self.portGroup},
                                                       updateFields={'waitList': {'sessionId': nextSessionId,
                                                                                  'user': nextUser,
                                                                                  'stage': nextStage,
                                                                                  'task': nextTask}},
                                                       removeFromList=True)
                        # {'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True} 
                        return dbObj['updatedExisting']
                else:
                    # Automated test
                    if sessionId == nextSessionId and stage == nextStage and task == nextTask:
                        dbObj = DB.name.updateDocument(Vars.webpage, 
                                                       queryFields={'domain': self.domain, 'name': self.portGroup},
                                                       updateFields={'waitList': {'sessionId': nextSessionId, 
                                                                                  'user': nextUser,
                                                                                  'stage': nextStage, 
                                                                                  'task': nextTask}},
                                                       removeFromList=True)
                        # {'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}                        
                        return dbObj['updatedExisting']                      
                    
        except Exception as errMsg:
            return str(errMsg)
        
    def refreshPortGroup(self, sessionLog=None, getSessionIdInWaitingList=None):
        """ 
        Get the next user in the waitlist and set it as the activeUser.
        """
        if sessionLog:
            self.setupLogger(sessionLog)
            
        try:
            # Get latest port-group status from MongoDB
            portGroupData = self.getPortGroupDetails()
            if portGroupData is None:
                if sessionLog and self.keystackLogger: self.keystackLogger.failed(f'portGroupData is still None. portGroup={self.portGroup}.  Return False')
                return False
            
            if sessionLog and self.keystackLogger: self.keystackLogger.info(f'[INFO]: PorGroupMgmt.refreshPortGroup: portGroupData={json.dumps(portGroupData, indent=4)}')
                
            # Now get the next in line 
            # [{'sessionId': '05-07-2024-00:16:41:139282_5179', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/05-07-2024-00:16:41:139282_5179/overallSummary.json', 'user': 'fromCLI: hgee', 'stage': 'DynamicVariableSample', 'task': 'dynamicVariables'}, 
            #  {'sessionId': '05-06-2024-17:16:45:343167_8436', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/05-06-2024-17:16:45:343167_8436/overallSummary.json', 'user': 'fromCLI: hgee', 'stage': 'Test', 'task': 'standAloneTests'}]
            if sessionLog and self.keystackLogger: self.keystackLogger.info(f'portGroup={self.portGroup}:  waitList={portGroupData["waitList"]}')
            
            if len(portGroupData['activeUsers']) == 0 and len(portGroupData['waitList']) == 0:
                portGroupData['available'] = True
                if sessionLog and self.keystackLogger: self.keystackLogger.info(f'portGroup={self.portGroup}: activeUsers=0  waitList=0')
                
            # Somebody or a session is still using it. Set the availabe accurately.
            if len(portGroupData['activeUsers']) > 0:
                portGroupData['available'] = False
                if sessionLog and self.keystackLogger: self.keystackLogger.info('portGroup={self.portGroup}: activeUsers > 0')
            
            # Active user is removed and there is no other active user using the env.
            # Check the waitList and get the next job waiting.   
            if len(portGroupData['activeUsers']) == 0:
                if sessionLog and self.keystackLogger: self.keystackLogger.info('portGroup={self.portGroup}: activeUsers=0')
                if len(portGroupData['waitList']) > 0:                    
                    if sessionLog and self.keystackLogger: self.keystackLogger.info(f'portGroup={self.portGroup}: Working on waitList > 0')
                    # Get the next in line, but check for the sessionID that was just removed 
                    # from the activeUser's list.  We want the same sessionID to have priority.
                    if getSessionIdInWaitingList:
                        if sessionLog and self.keystackLogger: self.keystackLogger.info(f'portGroup={self.portGroup}: getSessionIdInWaitingList={getSessionIdInWaitingList}')
                        
                        foundSessionIdInWaitList = False
                        for index, inQueue in enumerate(portGroupData['waitList']):
                            if inQueue['sessionId'] == getSessionIdInWaitingList:
                                portGroupData['activeUsers'].append(portGroupData['waitList'][index])
                                portGroupData['waitList'].pop(index)
                                portGroupData['available'] = False
                                foundSessionIdInWaitList = True
                                if sessionLog and self.keystackLogger:
                                    self.keystackLogger.info('portGroup={self.portGroup}: Giving priority to the same sessionId from the waitList')
                                
                        if foundSessionIdInWaitList is False:
                            if sessionLog and self.keystackLogger:
                                self.keystackLogger.info('portGroup={self.portGroup}: getSessionIdInWaitingList=None. Getting the top-of-waitList to active-user: portGroupData["waitList"][0]}')
                                
                            portGroupData['activeUsers'].append(portGroupData['waitList'][0])
                            portGroupData['waitList'].pop(0)
                            portGroupData['available'] = False                                       
                    else:
                        if sessionLog and self.keystackLogger:
                            self.keystackLogger.info('portGroup={self.portGroup}: getSessionIdInWaitingList=None. Getting the top-of-waitList to active-user: portGroupData["waitList"][0]}')
                            
                        portGroupData['activeUsers'].append(portGroupData['waitList'][0])
                        portGroupData['waitList'].pop(0)
                        portGroupData['available'] = False
                                
            if sessionLog and self.keystackLogger: self.keystackLogger.info(f'Updating DB: portGroup={self.portGroup}  portGroupData={json.dumps(portGroupData, indent=4)}') 

            dbObj = DB.name.updateDocument(Vars.webpage, queryFields={'domain': self.domain, 'name': self.portGroup}, updateFields=portGroupData)
            if dbObj:    
                # True|False
                return dbObj
            else:
                if sessionLog and self.keystackLogger: self.keystackLogger.failed(f'portGroup={self.portGroup}:  Updating portGroupData failed.')
                return False
            
        except Exception as errMsg:
            if sessionLog and self.keystackLogger: self.keystackLogger.error(f'portGroup={self.portGroup}: {traceback.format_exc(None, errMsg)}')

    def amIRunning(self, user, sessionId, stage, task, env, overallSummaryFile):
        """ 
        (A.K.A = amINext)
        Check the top active user to see if it's me running.
        If not, call refreshEnv() to get the next waiting in line.
        
        Return
            True | False | ('failed', errMsg, traceback)
        """
        try:
            timestampResultRootPath = overallSummaryFile.replace('/overallSummary.json', '')
            timestampFolderName = timestampResultRootPath.split('/')[-1] 
            sessionLog = f'{timestampResultRootPath}/{GlobalVars.sessionLogFilename}' 
                  
            # envData: From MongoDB envDMgmt
            # {'env': 'DOMAIN=Communal/Samples/demoEnv1', 'available': False, 'loadBalanceGroups': [], 
            #  'activeUsers': [{'sessionId': '08-25-2024-13:32:17:310980_310', 
            #                   'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/08-25-2024-13:32:17:310980_310/overallSummary.json', 'user': 'CLI: hgee', 'stage': 'Test', 'task': 'layer3'}],
            #  'waitList': [{'sessionId': '08-25-2024-13:32:17:310980_310', 
            #                'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/08-25-2024-13:32:17:310980_310/overallSummary.json', 'user': 'CLI: hgee', 'stage': 'Test', 'task': 'standAloneTests'}]}                            
            portGroupData = self.getPortGroupDetails()

            if portGroupData is None:
                # envData is None if the task doesn't use an Env
                return True
                                    
            if len(portGroupData['activeUsers']) > 0:
                # Current status from MongoDB
                currentActiveUser = portGroupData['activeUsers'][0]
                currentActiveUserEnv = currentActiveUser['env']
                currentActiveUserOverallSummaryFile = currentActiveUser['overallSummaryFile']
                envMgmtDataFile = f'{timestampResultRootPath}/.Data/EnvMgmt/STAGE={stage}_TASK={task}_ENV={currentActiveUserEnv}.json'
                
                if currentActiveUserOverallSummaryFile is None:
                    # User manually reserved the port-group if there is no overallSummary file
                    return False

                if RedisMgr.redis:
                    envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=f'envMgmt-{timestampFolderName}-STAGE={stage}_TASK={task}_ENV={currentActiveUserEnv}')
                else:
                    envMgmtData = readJson(envMgmtDataFile)

                if envMgmtData != {} and envMgmtData['envIsReleased']: 
                    # Check if the stage,task is still running
                    # if the activeUser session is not running, remove the active user
                    # self.refreshEnv below will get the next in line
                    
                    # Get the active-user task summary data
                    activeUserSessionId                   = currentActiveUser['sessionId']
                    activeUserUser                        = currentActiveUser['user']
                    activeUserOverallSummaryFile          = currentActiveUser['overallSummaryFile']
                    activeUserResultsPath                 = activeUserOverallSummaryFile.replace('/overallSummary.json', '')
                    activeUserStage                       = currentActiveUser['stage']
                    activeUserTask                        = currentActiveUser['task']
                    activeUserCurrentStageTaskSummaryFile = f'{activeUserResultsPath}/STAGE={activeUserStage}_TASK={activeUserTask}_ENV={currentActiveUserEnv}/taskSummary.json'
                    activeUserCurrentTaskSummary          = readJson(activeUserCurrentStageTaskSummaryFile)
                    
                    if activeUserCurrentTaskSummary['status'] in ['Aborted', 'Completed', 'Incomplete', 'Terminated']:
                        self.removeFromActiveUsersList([{'user':activeUserUser, 'sessionId':activeUserSessionId, 'stage':activeUserStage, 'task':activeUserTask}]) 
                
                if user == currentActiveUser['user'] and \
                    sessionId == currentActiveUser['sessionId'] and \
                    stage == currentActiveUser['stage'] and \
                        task == currentActiveUser['task']:

                    return True
                else:
                    return False
                
            if len(portGroupData['activeUsers']) == 0:
                # refreshPortGroup updates the active-user list by getting the next
                # queue in the wait-list.
                self.refreshPortGroup(sessionLog=sessionLog)
                portGroupData = self.getPortGroupDetails()
                
                # Now the active-user list is updated. Check who is running.
                if len(portGroupData['activeUsers']) > 0:
                    currentActiveUser = portGroupData['activeUsers'][0]
                    if user == currentActiveUser['user'] and \
                        sessionId == currentActiveUser['sessionId'] and \
                        stage == currentActiveUser['stage'] and \
                            task == currentActiveUser['task']:
                            
                        return True
                    else:
                        return False
                    
                elif len(portGroupData['activeUsers']) == 0:
                    result = self.reservePortGroup(sessionId=sessionId, overallSummaryFile=overallSummaryFile,
                                                   user=user, stage=stage, task=task, env=env, trackUtilization=True)
                    if result[0] == 'success':
                        return True
                    else:
                        return False
                        
        except Exception as errMsg:
            return ('failed', traceback.format_exc(None, errMsg))            