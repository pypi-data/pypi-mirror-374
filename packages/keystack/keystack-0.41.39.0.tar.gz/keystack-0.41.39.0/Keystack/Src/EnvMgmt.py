import os, sys, traceback, json
from re import search
from glob import glob
from time import sleep
from operator import itemgetter
from keystackUtilities import readYaml, readJson, writeToJson, mkdir2, chownChmodFolder
from commonLib import logSession, logDebugMsg
from db import DB
from globalVars import GlobalVars
from pprint import pprint
from copy import deepcopy

currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, f'{currentDir}/KeystackUI/topbar/utilizations')
from EnvUtilizationDB import EnvUtilizationDB
from LoggingAssistants import TestSessionLoggerAssistant
from RedisMgr import RedisMgr
from PortGroupMgmt import ManagePortGroup


class Vars:
    collectionName = 'envMgmt'

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
           
def isActiveUserRunning(overallSummaryFile: str) -> bool:
    """ 
    If a pipeline session process ID is terminated, the memory is still running.
    It leaves behind a reservation in activeUsers and it just sits there when the
    pipeline is already dead.  
    
    When a new pipeline task wants to reserve the env, it needs to check if the
    active-user is terminated or aborted.  In this case, remove from activeUsers
    list to allow new tasks to use the env.
    """
    if os.path.exists(overallSummaryFile) is False:
        # The active-user sesison could be deleted already.
        # So the overallSummaryFile does not exists
        return False
    
    data = readJson(overallSummaryFile)
    if data['status'] == 'Running':
        return True
    else:
        return False
    
    
class ManageEnv():
    def __init__(self, env=None, mongoDBDockerInternalIp=None):
        """
        Create a env mgmt file for each env in KeystackSystem/.DataLake/.EnvMgmt
        
        env: <str>|<str(None)>: EX: DOMAIN=Communal/<group>/<env>.yml
        """  
        self.keystackLogger = None
                               
        if mongoDBDockerInternalIp:
            # For production                       
            self.mongoDBInternalIp = mongoDBDockerInternalIp
        else:
            # For dev localhost mongoDB setup
            self.mongoDBInternalIp = keystackSettings.get('mongoDbIp', 'localhost')

        if env == 'None':
            env = None
        
        if env:
            # /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bringup.yml -> DOMAIN=Communal/Samples/bringup.yml
            # DOMAIN=Communal/<group>/<env>.yml -> DOMAIN=Communal/<group>/<env>
            env = env.split(f'{GlobalVars.envPath}/')[-1]
            env = env.split('.')[0]
                  
        self._setenv = env
        self.keystackTestRootPath = GlobalVars.keystackTestRootPath   
        self.keystackSystemPath   = GlobalVars.keystackSystemPath
        self.envPath = GlobalVars.envPath
        
        if env:
            self.setenvFiles()
            
        if DB.name is None:
            import db
            dbName  = db.ConnectMongoDB(ip=self.mongoDBInternalIp,
                                        port=int(keystackSettings.get('dbIpPort', 27017)),
                                        dbName=db.DB.dbName)
            DB.name = dbName

    @property
    def setenv(self):
        # getter function
        return self._setenv

    @setenv.setter
    def setenv(self, env):
        """
        Let users reset the env
        
        Usage:
            envObj = ManageEnv()
            envObj.setenv = DOMAIN=Communal/<group>/<env>.yml
        """
        if env is None:
            # None if the task doesn't use an Env
            return 

        self._setenv = env.split('.')[0]
        self._setenv = self._setenv.replace(f'{GlobalVars.envPath}/', '')
        self.setenvFiles()
         
    def setenvFiles(self):
        if '-' in self.setenv:
            env = self.setenv.replace('-', '/')
        else:
            env = self.setenv
            
        self.envFullPath = f'{GlobalVars.envPath}/{env}.yml'

    def setupLogger(self, logFile):
        self.keystackLogger = TestSessionLoggerAssistant(testSessionLogFile=logFile)

    '''
    def redisAddPipelineToEnvQueue(self, env, timestampFolderName):
        """ 
        env: DOMAIN=<domain>-<envNamespace>-<env>
        timestampFolderName: <timestamp>
        """
        if RedisMgr.redis:
            data = RedisMgr.redis.getCachedKeyData(keyName='envQueue')
            if data == {}:
                data.update({env: [timestampFolderName]})
            else:
                if env in data.keys():
                    if timestampFolderName not in data[env]:
                        data[env].append(timestampFolderName)
                else:
                    data.update({env: [timestampFolderName]})
                       
            RedisMgr.redis.write(keyName='envQueue', data=data)

    def redisIsPipelineNextInEnvQueue(self, env, timestampFolderName):
        if RedisMgr.redis:
            data = RedisMgr.redis.getCachedKeyData(keyName='envQueue')
            pprint(data)
            
            if data != {}:
                if env in data.keys():
                    nextInQueue = data[env][0]
                    if timestampFolderName == nextInQueue:
                        return True
                    else:
                        return False
                                
    def redisRemovePipelineFromEnvQueue(self, env, timestampFolderName):
        if RedisMgr.redis:
            data = RedisMgr.redis.getCachedKeyData(keyName='envQueue')
            if data != {}:
                if env in data:
                    if timestampFolderName in data[env]:
                        index = data[env].index(timestampFolderName)
                        data[env].pop(index)
                        RedisMgr.redis.write(keyName='envQueue', data=data)
                        if len(data[env]) == 0:
                            del data[env]
                        
                        if data == {}:
                            RedisMgr.redis.deleteKey(keyName='envQueue')
    '''
                                                                                      
    def isEnvExists(self):
        try:
            # Returns True|False
            dbObj = DB.name.isDocumentExists(Vars.collectionName, key='env', value=self._setenv, regex=False)
            return dbObj

        except Exception as errMsg:
            return errMsg
    
    def getEnvDomain(self):
        regexMatch = search('.*DOMAIN=(.+?)/.*', self.envFullPath)
        if regexMatch:
            return regexMatch.group(1)
        
    def addEnv(self):
        if self._setenv is None:
            return
        
        try:
            data = {'env': self._setenv,
                    'fullPath': self.envFullPath,
                    'available': True,
                    'shareable': False,
                    'loadBalanceGroups':[],
                    'activeUsers': [],
                    'waitList': []}  
            
            dbObj = DB.name.insertOne(collectionName=Vars.collectionName, data=data)
            return data
               
        except Exception as errMsg:
            print('\nEnvMgmt:addEnv exception: {traceback.format_exc(None, errMsg)}')
            return None
                      
    def isEnvParallelUsage(self):
        """ 
        If keystackUI is not running, the linux host CLI usage defaults
        env to not shareable
        """
        if self._setenv is None:
            # task doesn't use an Env
            return True 
        
        dbObj = self.getEnvDetails()
        if dbObj:
            return dbObj['shareable']
        
        return False

    def setEnvParallelUsage(self, parallelUsage: str):
        """ 
        parallelUsage: Yes| No
        """
        DB.name.updateDocument(Vars.collectionName,
                               queryFields={'env': self._setenv}, 
                               updateFields={'shareable': parallelUsage})        
      
    def getEnvDetails(self):
        """ 
        Note: This will not work if test was executed on CLI because DB.name is not set.
              DB.name is set in the web server. 
        """
        try:
            if self.setenv is None:
                if self.keystackLogger: self.keystackLogger.error(f'setenv: env=None!')
                return None

            dbObj = DB.name.getDocuments(Vars.collectionName, fields={'env': self.setenv}, includeFields={'_id':0})
            countX = deepcopy(dbObj)
            count = len(list(countX))
            
            if count == 0:
                if self.keystackLogger:
                    if self.keystackLogger: self.keystackLogger.debug(f'Env has no data: {self.setenv}. Calling addEnv()')
                    
                self.addEnv()
                
                # Verify
                dbObj = DB.name.getDocuments(Vars.collectionName, fields={'env': self.setenv}, includeFields={'_id':0})
                if len(list(dbObj)) == 0:
                    if self.keystackLogger: self.keystackLogger.failed(f'Verifying env data in DB. Called addEnv(), but still no data for env: {self.setenv}')
                else:
                    if self.keystackLogger: self.keystackLogger.info(f'Verifying env data in DB after calling addEnv(). Data verified!')

            if count != 0:
                return dbObj[0]
                  
        except Exception as errMsg:
            if self.keystackLogger:
                self.keystackLogger.error(traceback.format_exc(None, errMsg))
            return None

    def getPortGroups(self):
        if os.path.exists(self.envFullPath):
            data = readYaml(self.envFullPath)
            if data:
                return data.get('portGroups', [])
            else:
                return []
        else:
            return []
            
    def getLoadBalanceGroups(self):
        try:
            dbObj = DB.name.getOneDocument(Vars.collectionName, fields={'env': self._setenv})
            return dbObj.get('loadBalanceGroups', None)
  
        except Exception as errMsg:
            return None
                    
    def removeEnv(self):
        try:
            dbObj = DB.name.deleteOneDocument(Vars.collectionName, key='env', value=self._setenv)

        except Exception as errMsg:
            return None

    def isEnvAvailable(self):
        try:
            if self.isEnvParallelUsage():
                return True

            self.refreshEnv()  
            envData = self.getEnvDetails()
            if envData:
                if envData['available']:
                    return True
                else:
                    return False
            else:
                return False

        except Exception as errMsg:
            return False
                
    def isEnvNextInLine(self, sessionId, user=None, stage=None, task=None):
        """ 
        Check the env waitlist if the sessionId is next.
        If it is next:
            - Remove the sessionid from the wait list
            - Add the sessionId to the activeUsers list
            - set 'available' to False
        """
        try:
            envData = self.getEnvDetails()
            iAmNext = False
            
            if envData is None:
                # envData is None if the task doesn't use an Env
                return True
            
            for index,nextWaiting in enumerate(envData['waitList']):
                # {"task": "LoadCore",
                #  "stage": "Test",
                #  "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                #  "user": "rocky"}
                nextSessionId = nextWaiting['sessionId']
                nextUser = nextWaiting['User']
                nextStage = nextWaiting['stage']
                nextTask = nextWaiting['task']
                
                if sessionId == nextSessionId:
                    if stage is None:
                        # Manually reserved env is next to use it
                        iAmNext = True
                        break
                    
                    if user == nextUser and stage == nextStage and task == nextTask:
                        iAmNext = True
                        break
                    
            if iAmNext:
                dbObj1 = DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, 
                                               updateFields={'activeUsers': {'user': user, 
                                                                             'sessionId': sessionId, 
                                                                             'task': task},
                                                                             'available': False}, 
                                               appendToList=True)
                
                dbObj2 = DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, 
                                               updateFields={'waitList': {'sessionId': nextSessionId, 'user': nextUser,
                                                                          'stage': nextStage, 'task': nextTask}}, 
                                               removeFromList=True)
                if dbObj1 and dbObj2:
                    EnvUtilizationDB().insert(self._setenv, user)
                    return True
                else:
                    return False
            else:
                return False
                   
        except Exception as errMsg:
            return False
        
    def getActiveUsers(self):
        """
        Return a list of user or test sessions using the env.
        
        "activeUsers": [{"task": "LoadCore",
                         "sessionId": "11-01-2022-03:24:46:924785_rocky_1Test",
                         "user": "rocky"}]
                         
         envData with active users = {'_id': ObjectId('6445be5889e17be32c818fcc'), 'env': 'DOMAIN=Communal/Samples/hubert', 'available': False, 'activeUsers': [{'sessionId': '05-17-2023-15:49:07:297406_5432', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/05-17-2023-15:49:07:297406_5432/overallSummary.json', 'user': 'hgee', 'stage': 'Test', 'task': 'CustomPythonScripts2'}], 'waitList': [], 'loadBalanceGroups': []}
         
        envData with no active users = {'_id': ObjectId('64455f78f7b6150a4142c785'), 'env': 'DOMAIN=Communal/Samples/loadcoreSample', 'available': True, 'activeUsers': [], 'waitList': [], 'loadBalanceGroups': []}

        """
        try:
            envData = self.getEnvDetails()
            if envData is None:
                # envData is None if the task doesn't use an Env
                return []

            return envData['activeUsers']
        except Exception as errMsg:
            return errMsg
        
    def isUserInActiveUsersList(self, user):
        for eachUser in self.getActiveUsers():
            if eachUser['stage'] == None:
                if eachUser['user'] == user:
                    return True
                
    def isUserInWaitList(self, user):
        for eachUser in self.getWaitList():
            if eachUser['stage'] == None:
                if eachUser['user'] == user:
                    return True

    def isActiveUserHoldingEnvOnFailure(self, overallSummaryFile=None):
        """ 
        OverallSummaryFile: The requesting pipeline's overallSummary file
        """
        envData = self.getEnvDetails()
        if envData is None:
            return False
        
        if len(envData['activeUsers']) > 0:
            envWithDashes = self._setenv.replace('/', '-')
            
            # Env current status from MongoDB
            currentActiveUser = envData['activeUsers'][0]

            # Get the active-user task summary data
            activeUserSessionId          = currentActiveUser['sessionId']
            activeUserUser               = currentActiveUser['user']
            activeUserStage              = currentActiveUser['stage']
            activeUserTask               = currentActiveUser['task']
            activeUserOverallSummaryFile = currentActiveUser['overallSummaryFile']
            
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
 
            if activeUserEnvMgmtData == {}:
                # envMgmt in MongoDB activeUser is actively using env, but 
                # the session is done and the envMgmt is no longer exists
                envData['activeUsers'].pop(0)
                envData['available'] = True
                DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, updateFields=envData)
                return False
            else: 
                if activeUserEnvMgmtData['holdEnvsIfFailed']:
                    if activeUserEnvMgmtData['envIsReleased'] is False:
                        # holdEnvsIfFailed is True and user has not released the env 
                        return True 
                    else:
                        return False
                else:
                    return False       

    def amIRunning(self, user, sessionId, stage, task, overallSummaryFile):
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
                                  
            if self.isEnvParallelUsage():
                EnvUtilizationDB().insert(self._setenv, user)
                return True
            
            if self.isEnvParallelUsage() == False:
                # envData: From MongoDB envDMgmt
                # {'env': 'DOMAIN=Communal/Samples/demoEnv1', 'available': False, 'loadBalanceGroups': [], 
                #  'activeUsers': [{'sessionId': '08-25-2024-13:32:17:310980_310', 
                #                   'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/08-25-2024-13:32:17:310980_310/overallSummary.json', 'user': 'CLI: hgee', 'stage': 'Test', 'task': 'layer3'}],
                #  'waitList': [{'sessionId': '08-25-2024-13:32:17:310980_310', 
                #                'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/08-25-2024-13:32:17:310980_310/overallSummary.json', 'user': 'CLI: hgee', 'stage': 'Test', 'task': 'standAloneTests'}]}                            
                envData = self.getEnvDetails()
                
                if envData is None:
                    # envData is None if the task doesn't use an Env
                    return True
                
                if len(envData['activeUsers']) > 0:
                    # Env current status from MongoDB
                    currentActiveUser = envData['activeUsers'][0]
                    currentActiveUserOverallSummaryFile = currentActiveUser['overallSummaryFile']
                    
                    # This is added to remove the stale active-user in case it's completed or aborted and it was just sitting there
                    # envMgmtData:  {'user': 'hgee', 'sessionId': '05-25-2023-15:43:49:755851_2058', 'stage': 'Test', 'task': 'Demo2', 
                    #               'env': 'Samples/hubert', 'envIsReleased': True, 'holdEnvsIfFailed': True, 'result': 'Failed'}
                    envWithDashes = self._setenv.replace('/', '-')
                    envMgmtDataFile = f'{timestampResultRootPath}/.Data/EnvMgmt/STAGE={stage}_TASK={task}_ENV={envWithDashes}.json'

                    if currentActiveUserOverallSummaryFile is None:
                        # User manually reserved the port-group if there is no overallSummary file
                        return False
                                    
                    if RedisMgr.redis:
                        envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=f'envMgmt-{timestampFolderName}-STAGE={stage}_TASK={task}_ENV={envWithDashes}')
                    else:
                        envMgmtData = readJson(envMgmtDataFile)
                        
                    if envMgmtData != {} and envMgmtData['envIsReleased'] == True: 
                        # Check if the stage,task is still running
                        # if the activeUser session is not running, remove the active user
                        # self.refreshEnv below will get the next in line
                        
                        # Get the active-user task summary data
                        activeUserSessionId          = currentActiveUser['sessionId']
                        activeUserUser               = currentActiveUser['user']
                        activeUserOverallSummaryFile = currentActiveUser['overallSummaryFile']
                        activeUserResultsPath        = activeUserOverallSummaryFile.replace('/overallSummary.json', '')
                        activeUserStage              = currentActiveUser['stage']
                        activeUserTask               = currentActiveUser['task']
                        activeUserCurrentStageTaskSummaryFile = f'{activeUserResultsPath}/STAGE={activeUserStage}_TASK={activeUserTask}_ENV={envWithDashes}/taskSummary.json'
                        activeUserCurrentTaskSummary          = readJson(activeUserCurrentStageTaskSummaryFile)
                        if activeUserCurrentTaskSummary['status'] in ['Aborted', 'Completed', 'Incomplete', 'Terminated']:
                            self.removeFromActiveUsersList([{'user':activeUserUser, 'sessionId':activeUserSessionId, 'stage':activeUserStage, 'task':activeUserTask}])
                    
                    if user == currentActiveUser['user'] and \
                        sessionId == currentActiveUser['sessionId'] and \
                        stage == currentActiveUser['stage'] and \
                            task == currentActiveUser['task']:
                                
                        EnvUtilizationDB().insert(self._setenv, user)
                        return True
                    else:
                        return False
                    
                if len(envData['activeUsers']) == 0:
                    # refreshEnv will update the active-user list by getting the next
                    # queue in the wait-list.
                    self.refreshEnv(sessionLog=sessionLog)
                    envData = self.getEnvDetails()
                    
                    # Now the active-user list is updated. Check who is running
                    if len(envData['activeUsers']) > 0:
                        currentActiveUser = envData['activeUsers'][0]
                        if user == currentActiveUser['user'] and \
                            sessionId == currentActiveUser['sessionId'] and \
                            stage == currentActiveUser['stage'] and \
                                task == currentActiveUser['task']:
                                    
                            EnvUtilizationDB().insert(self._setenv, user)
                            return True
                        else:
                            return False
                        
                    elif len(envData['activeUsers']) == 0:
                        result = self.reserveEnv(sessionId=sessionId, overallSummaryFile=overallSummaryFile,
                                                 user=user, stage=stage, task=task, trackUtilization=True)
                        if result[0] == 'success':
                            return True
                        else:
                            return False
                        
        except Exception as errMsg:
            return ('failed', traceback.format_exc(None, errMsg))
            
    def goToWaitList(self, sessionId=None, user=None, stage=None, task=None):
        dbObj = DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, 
                                       updateFields={'waitList': {'sessionId': sessionId, 
                                                                  'user': user, 
                                                                  'stage': stage, 
                                                                  'task': task}},
                                      appendToList=True)
          
    def getWaitList(self):
        """
        Return a list of people or test sessions using the env.

        "waitList": [
        {
            "task": "LoadCore",
            "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
            "stage": "LoadCoreTest",
            "user": "rocky"
        }
        """
        try:
            envData = self.getEnvDetails()
            if envData:
                # envData is None if the task doesn't use an Env
                return envData['waitList']
            else:
                return []
        except Exception as errMsg:
            return errMsg
    
    def removeAllSessionIdFromWaitList(self, sessionId, logFile=None):
        """ 
        Called by terminateProcessId.
        Remove all sessionId from waitList
        """
        try:
            if logFile:
                self.setupLogger(logFile)
                self.keystackLogger.info(f'env={self._setenv}  sessionId={sessionId} envData={json.dumps(envData, indent=4)}')

            envData = self.getEnvDetails()
                            
            if envData is None:
                # envData is None if the task doesn't use an Env
                return
            
            for index, waitingSessionData in enumerate(envData['waitList']):
                nextUser = waitingSessionData['user']
                nextStage = waitingSessionData['stage']
                nextTask = waitingSessionData['task']
                
                if waitingSessionData['sessionId'] == sessionId:
                    dbObj = DB.name.updateDocument(Vars.collectionName, 
                                                   queryFields={'env': self._setenv},
                                                   updateFields={'waitList': {'sessionId':sessionId,
                                                                              'user': nextUser,
                                                                              'stage': nextStage,
                                                                              'task': nextTask}},
                                                   removeFromList=True)
                    
                    if logFile:
                        self.keystackLogger.info(f'Removed sessionId={sessionId} from waitlist. result={dbObj}')
                    
            # verify
            envData = self.getEnvDetails()
            if logFile:
                self.keystackLogger.info(f'verify envData: {json.dumps(envData, indent=4)}')
            
        except Exception as errMsg:
            if logFile:
                self.keystackLogger.error(traceback.format_exc(None, errMsg))
            return errMsg

    def removeAllSessionIdFromActiveUsersList(self, sessionId, logFile=None):
        """ 
        Called by terminateProcessId.
        Remove all sessionId from active users list
        """
        try:
            getSessionIdInWaitingList = None
            envData = self.getEnvDetails()    
            removeFlag = False

            if envData is None:
                # envData is None if the task doesn't use an Env
                return
                        
            if logFile:
                self.setupLogger(logFile)
                self.keystackLogger.info(f'env={self.setenv} sessionId={sessionId} envData={json.dumps(envData, indent=4)}')
            
            if len(envData['activeUsers']) > 0:
                for index, activeUser in enumerate(envData['activeUsers']):
                    if activeUser['sessionId'] == sessionId:
                        removeFlag = True
                        stage = activeUser['stage']
                        task = activeUser['task']
                        envData['activeUsers'].pop(index)
                        getSessionIdInWaitingList = sessionId
                        dbObj = DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, updateFields=envData)
                        if logFile:
                            self.keystackLogger.info(f'Removed sessionId {sessionId} in active-user. Active-user is {envData["activeUsers"]}')
                        
                        # Get the testSession.log file and update the session env tracker      
                        timestampFolderRootPath = activeUser["overallSummaryFile"].replace('/overallSummary.json', '')
                        timestampFolderName = timestampFolderRootPath.split('/')[-1]
                        envMgmtDataFile = f'{timestampFolderRootPath}/.Data/EnvMgmt/STAGE={stage}_TASK={task}_ENV={self._setenv.replace("/", "-")}.json'
                        
                        if RedisMgr.redis:
                            keyName = f'envMgmt-{timestampFolderName}-STAGE={stage}_TASK={task}_ENV={self._setenv.replace("/", "-")}'
                            sessionEnvTrackerData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                            sessionEnvTrackerData.update({'envIsReleased': True})
                            RedisMgr.redis.updateKey(keyName=keyName, data=sessionEnvTrackerData)      
                        else:
                            if os.path.exists(envMgmtDataFile):
                                sessionEnvTrackerData = readJson(envMgmtDataFile)
                                sessionEnvTrackerData.update({'envIsReleased': True})                  
                                writeToJson(envMgmtDataFile, sessionEnvTrackerData, mode='w')
                                                                        
                        timestampFolderRootPath = sessionEnvTrackerData['testResultRootPath']
                        sessionLog = f'{timestampFolderRootPath}/testSession.log'
                        if logFile:
                            self.keystackLogger.info(f'SessionId:{sessionId} Stage:{stage} task:{task} env:{self._setenv}')
                     
            result = self.refreshEnv(sessionLog, getSessionIdInWaitingList=getSessionIdInWaitingList)
            if result:
                # Verify
                envData = self.getEnvDetails()
                if logFile:
                    self.keystackLogger.info(f'verify envData: {json.dumps(envData, indent=4)}')
                    
        except Exception as errMsg:
            if logFile:
                self.keystackLogger.error(traceback.format_exc(None, errMsg))
            return errMsg
                            
    def removeFromWaitList(self, sessionId, user=None, stage=None, task=None):
        """ 
        For manual reserves, only sessionId is set.
        Automated test will include stage and task
        """
        try:
            envData = self.getEnvDetails()
            if envData is None:
                # envData is None if the task doesn't use an Env
                return
            
            for index,userData in enumerate(envData['waitList']):
                nextUser = userData['user']
                nextSessionId = userData['sessionId']
                nextStage = userData['stage']
                nextTask = userData['task']
                
                if stage in [None, 'None']:
                    # Manual user
                    if sessionId == nextSessionId and user == nextUser:
                        dbObj = DB.name.updateDocument(Vars.collectionName,
                                                       queryFields={'env': self._setenv},
                                                       updateFields={'waitList': {'sessionId':nextSessionId,
                                                                                  'user': nextUser,
                                                                                  'stage': nextStage,
                                                                                  'task': nextTask}},
                                                       removeFromList=True)
                        # {'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True} 
                        return dbObj['updatedExisting']
                else:
                    # Automated test
                    if sessionId == nextSessionId and stage == nextStage and task == nextTask:
                        dbObj = DB.name.updateDocument(Vars.collectionName, 
                                                       queryFields={'env': self._setenv},
                                                       updateFields={'waitList': {'sessionId':nextSessionId, 
                                                                                  'user': nextUser,
                                                                                  'stage': nextStage, 
                                                                                  'task': nextTask}},
                                                       removeFromList=True)
                        # {'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}                        
                        return dbObj['updatedExisting']                      
                    
        except Exception as errMsg:
            return str(errMsg)
       
    def removeFromActiveUsersList(self, removeList):
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

                # env data from MongoDB
                envData = self.getEnvDetails()
                
                # envData:
                #     envData: {'_id': ObjectId('6445be5889e17be32c818fcc'), 'env': 'DOMAIN=Communal/Samples/hubert', 'available': False, 'activeUsers': [{'sessionId': '04-23-2023-16:44:54:605093_hgee', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/04-23-2023-16:44:54:605093_hgee/overallSummary.json', 'user': 'hgee', 'stage': 'Bringup', 'task': 'CustomPythonScripts'}], 'waitList': []}
                if envData:
                    if len(envData['activeUsers']) > 0:
                        getSessionIdInWaitingList = None
                        for index, user in enumerate(envData['activeUsers']):
                            sessionLog = None
                            if user['sessionId'] == sessionId and \
                                user['stage'] == stage and \
                                user['task'] == task:
                                    envData['activeUsers'].pop(index)
                                    envData['available'] = True
                                    removeFlag = True
                                    getSessionIdInWaitingList = sessionId
                                    dbObj = DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, updateFields=envData)
                                    
                                    if user["overallSummaryFile"]:
                                        # Get the testSession.log file and update the session env tracker      
                                        timestampFolderRootPath = user["overallSummaryFile"].replace('/overallSummary.json', '')
                                        timestampFolderName = timestampFolderRootPath.split('/')[-1]
                                        envMgmtDataFile = f'{timestampFolderRootPath}/.Data/EnvMgmt/STAGE={stage}_TASK={task}_ENV={self._setenv.replace("/", "-")}.json'
                                        
                                        if RedisMgr.redis:            
                                            keyName = f'envMgmt-{timestampFolderName}-STAGE={stage}_TASK={task}_ENV={self._setenv.replace("/", "-")}'
                                            sessionEnvTrackerData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                                            if sessionEnvTrackerData:
                                                sessionEnvTrackerData.update({'envIsReleased': True})
                                                RedisMgr.redis.updateKey(keyName=keyName, data=sessionEnvTrackerData)
                                        else:
                                            if os.path.exists(envMgmtDataFile):
                                                sessionEnvTrackerData = readJson(envMgmtDataFile)
                                                sessionEnvTrackerData.update({'envIsReleased': True})                  
                                                writeToJson(envMgmtDataFile, sessionEnvTrackerData, mode='w')
                                        
                                        if 'testResultRootPath' in sessionEnvTrackerData.keys():                 
                                            timestampFolderRootPath = sessionEnvTrackerData['testResultRootPath']
                                            sessionLog = f'{timestampFolderRootPath}/{GlobalVars.sessionLogFilename}'
                                            self.setupLogger(sessionLog)
                                                             
                                    if sessionLog:
                                        self.keystackLogger.info(f'Removed and updated envData with: {json.dumps(envData, indent=4)}')
                                        envData = self.getEnvDetails()
                                        self.keystackLogger.info(f'Verifying updated envData: {json.dumps(envData, indent=4)}')
                                        verifyingUpdateResult = True
                                        for user in envData['activeUsers']: 
                                            if user['sessionId'] == sessionId and \
                                                user['stage'] == stage and \
                                                user['task'] == task:
                                                    verifyingUpdateResult = False
                                                    self.keystackLogger.info(f'Verifying updated active-user failed. The user session still in active-user list: {json.dumps(envData, indent=4)}')
                                                    
                                        if verifyingUpdateResult:
                                            self.keystackLogger.info(f'Verifying updated envData success! STAGE={stage}_TASK={task}_ENV={self._setenv} is removed in activeUsers')

                                    if removeFlag:
                                        # Get the next in waiting. Search for same sessionID from the waitList to give priority to 
                                        # the same pipeline session to go first
                                        return self.refreshEnv(sessionLog, getSessionIdInWaitingList=getSessionIdInWaitingList)
                    else:
                        return self.refreshEnv(sessionLog, getSessionIdInWaitingList=None)
                                        
            # if removeFlag:
            #     # Get the next in waiting. Search for same sessionID from the waitList to give priority to 
            #     # the same pipeline session to go first
            #     return self.refreshEnv(sessionLog, getSessionIdInWaitingList=getSessionIdInWaitingList)
        
        except Exception as errMsg:
            errorMsg = f'EnvMgmt.removeFromActiveUsersList: error: {traceback.format_exc(None, errMsg)}'
            print(traceback.format_exc(None, errMsg))
            if sessionLog: logSession(sessionLog, f'{errorMsg}')
            return errorMsg
                        
    def refreshEnv(self, sessionLog=None, getSessionIdInWaitingList=None):
        """ 
        Get the next user in the waitlist and set it as the activeUser.
        If getSessionIdInWaitingList, get the sessionId in the waitList to be the active-user
        """
        if sessionLog: self.setupLogger(sessionLog)
        try:
            if sessionLog and self.keystackLogger: 
                self.keystackLogger.info(f'envData=None. env={self.setenv}  Calling getEnvDetails()')
                
            envData = self.getEnvDetails()
            if envData is None:
                if sessionLog and self.keystackLogger:
                    self.keystackLogger.failed(f'envData is still None. env={self.setenv}.  Return False')
                return False

            if sessionLog and self.keystackLogger:
                self.keystackLogger.info(f'[INFO]: EnvMgmt.refreshEnv: envData={json.dumps(envData, indent=4)}')
                                                
            # Now get the next in line 
            # [{'sessionId': '05-07-2024-00:16:41:139282_5179', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/05-07-2024-00:16:41:139282_5179/overallSummary.json', 'user': 'fromCLI: hgee', 'stage': 'DynamicVariableSample', 'task': 'dynamicVariables'}, 
            #  {'sessionId': '05-06-2024-17:16:45:343167_8436', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/05-06-2024-17:16:45:343167_8436/overallSummary.json', 'user': 'fromCLI: hgee', 'stage': 'Test', 'task': 'standAloneTests'}]
            if self.keystackLogger:
                self.keystackLogger.info(f'env={self.setenv}:  waitList={envData["waitList"]}')

            # Get next in line
            if self.isEnvParallelUsage():
                envData['available'] = True
                envData['activeUsers'] += envData['waitList'][:]
                envData['waitList'] = []                
            else:
                # Somebody or a session is still using it. Set the availabe accurately.
                # envData: {'_id': ObjectId('6445be5889e17be32c818fcc'), 'env': 'DOMAIN=Communal/Samples/hubert', 'available': False, 'activeUsers': [{'sessionId': '04-23-2023-16:44:54:605093_hgee', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/04-23-2023-16:44:54:605093_hgee/overallSummary.json', 'user': 'hgee', 'stage': 'Bringup', 'task': 'CustomPythonScripts'}], 'waitList': []}
                if len(envData['activeUsers']) > 0:
                    envData['available'] = False
                    self.updateEnvMgmtActiveUserEnvIsReleased(envData['activeUsers'], envIsReleased=False)
                        
                    if sessionLog and self.keystackLogger:
                        self.keystackLogger.info('env={self.setenv}: activeUsers > 0')
                        
                if len(envData['activeUsers']) == 0 and len(envData['waitList']) == 0:
                    envData['available'] = True
                    if sessionLog and self.keystackLogger:
                        self.keystackLogger.info(f'env={self.setenv}: activeUsers=0  waitList=0')
                 
                # Active user is removed and there is no other active user using the env.
                # Check the waitList and get the next job waiting.   
                if len(envData['activeUsers']) == 0 and len(envData['waitList']) > 0:
                    if sessionLog and self.keystackLogger:
                        self.keystackLogger.info('env={self.setenv}: activeUsers=0')
                        
                    #if len(envData['waitList']) > 0:                    
                    if sessionLog and self.keystackLogger:
                        self.keystackLogger.info(f'env={self.setenv}: Working on waitList > 0')

                    # Get the next in line, but check for the sessionID that was just removed 
                    # from the activeUser's list.  We want the same sessionID to have priority.
                    if getSessionIdInWaitingList:
                        if self.keystackLogger: 
                            self.keystackLogger.info(f'env={self.setenv}: getSessionIdInWaitingList={getSessionIdInWaitingList}')
                        
                        foundSessionIdInWaitList = False
                        # Give priority to the sessionID in the waitlist to become the active-user that just got removed.
                        # Get the next task in the waitlist with the same sessionId
                        for index, inQueue in enumerate(envData['waitList']):
                            if inQueue['sessionId'] == getSessionIdInWaitingList:
                                envData['activeUsers'].append(envData['waitList'][index])
                                envData['waitList'].pop(index)
                                envData['available'] = False
                                foundSessionIdInWaitList = True
                                self.updateEnvMgmtActiveUserEnvIsReleased(envData['activeUsers'], envIsReleased=False)
                                if sessionLog and self.keystackLogger:
                                    self.keystackLogger.info('env={self.setenv}: Giving priority to the same sessionId from the waitList')
                                
                        if foundSessionIdInWaitList is False:
                            # Get the next sessionId in the wait-list
                            if sessionLog and self.keystackLogger:
                                self.keystackLogger.info('env={self.setenv}: getSessionIdInWaitingList=None. Getting the top-of-waitList to active-user: envData["waitList"][0]}')
                                
                            envData['activeUsers'].append(envData['waitList'][0])
                            envData['waitList'].pop(0)
                            envData['available'] = False 
                            self.updateEnvMgmtActiveUserEnvIsReleased(envData['activeUsers'], envIsReleased=False) 
                    else:
                        if sessionLog and self.keystackLogger:
                            self.keystackLogger.info('env={self.setenv}: getSessionIdInWaitingList=None. Getting the top-of-waitList to active-user: envData["waitList"][0]}')

                        envData['activeUsers'].append(envData['waitList'][0])
                        envData['waitList'].pop(0)
                        envData['available'] = False
                        self.updateEnvMgmtActiveUserEnvIsReleased(envData['activeUsers'], envIsReleased=False)
                                  
            if sessionLog and self.keystackLogger:
                self.keystackLogger.info(f'Updating DB: env={self.setenv}  envData={json.dumps(envData, indent=4)}') 
                   
            dbObj = DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, updateFields=envData)

            if dbObj:    
                # True|False
                return dbObj
            else:
                if sessionLog and self.keystackLogger:
                    self.keystackLogger.failed(f'env={self.setenv}:  Updating envData failed.')
                    
                return False
            
        except Exception as errMsg:
            if sessionLog and self.keystackLogger:
                self.keystackLogger.error(f'env={self.setenv}: {traceback.format_exc(None, errMsg)}')

    def updateEnvMgmtActiveUserEnvIsReleased(self, activeUsers: list, envIsReleased: bool):
        """ 
        # envData: {'_id': ObjectId('6445be5889e17be32c818fcc'), 'env': 'DOMAIN=Communal/Samples/hubert', 'available': False, 
        #           'activeUsers': [{'sessionId': '04-23-2023-16:44:54:605093_hgee', 
        #                            'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/04-23-2023-16:44:54:605093_hgee/overallSummary.json', 
        #                            'user': 'hgee', 'stage': 'Bringup', 'task': 'CustomPythonScripts'}], 
        #           'waitList': []}
        """
        for activeUser in activeUsers:
            if activeUser["overallSummaryFile"]:
                stage = activeUser['stage']
                task = activeUser['task']
                # Get the testSession.log file and update the session env tracker      
                timestampFolderRootPath = activeUser["overallSummaryFile"].replace('/overallSummary.json', '')
                timestampFolderName = timestampFolderRootPath.split('/')[-1]
                envMgmtDataFile = f'{timestampFolderRootPath}/.Data/EnvMgmt/STAGE={stage}_TASK={task}_ENV={self._setenv.replace("/", "-")}.json'
                
                if RedisMgr.redis:            
                    keyName = f'envMgmt-{timestampFolderName}-STAGE={stage}_TASK={task}_ENV={self._setenv.replace("/", "-")}'
                    sessionEnvTrackerData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                    if sessionEnvTrackerData:
                        sessionEnvTrackerData.update({'envIsReleased': envIsReleased})
                        RedisMgr.redis.updateKey(keyName=keyName, data=sessionEnvTrackerData)
                else:
                    if os.path.exists(envMgmtDataFile):
                        sessionEnvTrackerData = readJson(envMgmtDataFile)
                        sessionEnvTrackerData.update({'envIsReleased': envIsReleased})                  
                        writeToJson(envMgmtDataFile, sessionEnvTrackerData, mode='w')
    
    def update(self):
        """ 
        Self healing / update
        
        Every time user enters the Env page, this function will:
            - Verify all existing envMgmt-* to see if the sessionId exist in pipelines.
            - If the sessionId doesn't exists:
                - Remove the envMgmt key
                - Update MongoDB env envIsReleased=True and available=True
                
            - Check the self._setenv's wait-list
            - If the sessionId in each wait-list doesn't exists in pipelines, remove the env from wait-list
        """
        try:
            releasePortGroups = []
            if RedisMgr.redis:
                # ['overallSummary-domain=Communal-04-26-2025-02:23:34:287679_4393',]
                currentPipelines = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'overallSummary-domain=*')
                for eachEnvMgmt in RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'envMgmt-*'):
                    # eachEnvMgmt: envMgmt-04-25-2025-19:20:57:459441_558-STAGE=setup_TASK=bringup_ENV=DOMAIN=Communal-Samples-demoEnv1
                    envData = RedisMgr.redis.getCachedKeyData(keyName=eachEnvMgmt)
                    envSessionId = envData.get('sessionId', None)
                    stage = envData.get('stage', None)
                    env = envData.get('env', None)
                    portGroups = envData.get('portGroups', None)
                    envIsReleased = envData.get('envIsReleased', None)
                    holdEnvsIfFailed = envData.get('holdEnvsIfFailed', None)
                    domain = env.split('=')[-1].split('/')[0]
                     
                    # Release port-groups only if there is a stage.
                    # No stage means the port-group is manually reserved.                   
                    if portGroups and stage:
                        for portGroup in portGroups:
                            if portGroup not in releasePortGroups:
                                releasePortGroups.append((portGroup, envSessionId, domain))

                    if stage is None:
                        RedisMgr.redis.deleteKey(keyName=eachEnvMgmt)
                    else:                 
                        if envSessionId:
                            isEnvSessionIdInCurrentPipelines = False
                            
                            for pipeline in currentPipelines:
                                if envSessionId in pipeline:
                                    # The env is in active-user queue
                                    isEnvSessionIdInCurrentPipelines = pipeline
                                    # Check if the pipeline status is running and if the Env holdEnvsIfFailed=True
                                    pipelineData = RedisMgr.redis.getCachedKeyData(keyName=isEnvSessionIdInCurrentPipelines)
                                    if pipelineData['status'] != 'Running' and holdEnvsIfFailed is False:
                                        RedisMgr.redis.deleteKey(keyName=eachEnvMgmt)
                                        dbObj = DB.name.updateDocument(Vars.collectionName,
                                                                       queryFields={'env': env},
                                                                       updateFields={'envIsReleased': True, 'available': True})
                                                            
                            if isEnvSessionIdInCurrentPipelines is False:
                                # Remove the envMgmt from redis
                                RedisMgr.redis.deleteKey(keyName=eachEnvMgmt)

                                dbObj = DB.name.updateDocument(Vars.collectionName,
                                                               queryFields={'env': env},
                                                               updateFields={'envIsReleased': True, 'available': True})
                            
                # Get env's in waitlist
                # Check pipelines for the env's sessionId
                # If the sessionId doesn't exists in pipelines, remove from waitlist
                data = DB.name.getDocuments(Vars.collectionName, fields={'env': self._setenv}, includeFields={'_id':0})[0]
                if data:
                    if len(data['waitList']) > 0:
                        for sessionWaiting in data['waitList']:
                            if sessionWaiting['stage'] != '':
                                if sessionWaiting['sessionId'] not in currentPipelines:
                                    # Remove from waitlist
                                    self.removeFromWaitList(sessionId=sessionWaiting['sessionId'], 
                                                            user=sessionWaiting['user'], 
                                                            stage=sessionWaiting['stage'], 
                                                            task=sessionWaiting['task'])
                        
                for portGroup in releasePortGroups:
                    portGroupName = portGroup[0]
                    sessionId = portGroup[1]
                    domain = portGroup[2]
                    ManagePortGroup(domain, portGroupName).removeAllSessionIdFromWaitList(sessionId=sessionId)
                    ManagePortGroup(domain, portGroupName).removeAllSessionIdFromActiveUsersList(sessionId=sessionId)
                
                ManagePortGroup().selfUpdateActiveUsersAndWaitList()
                    
        except Exception as errMsg:
            #print('\n--- ManageEnv.update() error:', traceback.format_exc(None, errMsg))            
            pass
        
    def selfRecovery(self):
        """ 
        In a odd situation if there is no active-user and there are sessions stuck in the wait-list,
        need to create a link to put the next session to the the active-user
        """
        data = DB.name.getDocuments(Vars.collectionName, fields={}, includeFields={'_id':0})
        if data:
            # selfRecovery: {'env': '/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/airMosaicSample', 'available': True, 'loadBalanceGroups': [],
            #                'activeUsers': [{'sessionId': '09-12-2024-02:38:01:664230', 'overallSummaryFile': None, 'user': 'CLI: hgee', 'stage': None, 'task': None}], 
            #                'waitList': []}
            # for env in data:
            #     print('\n---- selfRecovery: data:', env)
            pass

    def goToWaitlistOnDB(self, envData):
        dbObj = DB.name.updateDocument(Vars.collectionName, queryFields={'env': self._setenv}, updateFields=envData)
                                                
    def reserveEnv(self, sessionId=None, overallSummaryFile=None, user=None, stage=None, task=None, trackUtilization=True):
        """ 
        Reserving an Env for both manual reserve and Keystack auto reserve.
        This function checks if the env active-user is actively running. It could be in an Aborted status.
        If it's not running, remove the active-user and make the new pipeline active-user.
        
        For manual reservation: Only sessionId and user is required
        
        trackUtilization <bool>: For keystack.py.lockAndWaitForEnv().  This function calls reserveEnv() and amIRunning().
                            Both functions increment env utilization. We want to avoid hitting it twice.
                            So exclude hitting it here in reserveEnv and let amIRunning hit it.
        """
        try:
            message = 'No Env used'
            updateDB = True
            # Env data from MongoDB
            envData = self.getEnvDetails()
            
            if overallSummaryFile:
                testResultRootPath = overallSummaryFile.replace('/overallSummary.json', '')
                timestampFolderName = overallSummaryFile.split('/overallSummary.json')[0].split('/')[-1]
                sessionLog = f'{testResultRootPath}/{GlobalVars.sessionLogFilename}'                        
                self.setupLogger(sessionLog)
                self.keystackLogger.info(f'sessionId={sessionId} stage={stage} task={task} env={self._setenv}: envData: {json.dumps(envData, indent=4)}')
                
            # EnvMgmt.py: reserveEnv envData: {'_id': ObjectId('64b3104341747cd3df011403'), 'env': 'DOMAIN=Communal/ixLoadDemo', 'available': True, 'loadBalanceGroups': ['qa'], 'activeUsers': [{'sessionId': '11-07-2023-15:17:40:317447_7216', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/11-07-2023-15:17:40:317447_7216/overallSummary.json', 'user': None, 'stage': 'PyTest', 'task': 'Demo'}, {'sessionId': '11-07-2023-15:21:33:433418_7689', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/11-07-2023-15:21:33:433418_7689/overallSummary.json', 'user': None, 'stage': 'PyTest', 'task': 'Demo'}], 'waitList': []}

            # envData is None if the task doesn't use an Env
            if envData:
                if self.isEnvParallelUsage():
                    if self.keystackLogger:
                        self.keystackLogger.info(f'env is parallelUsage=True: sessionId={sessionId}  stage={stage} task={task} env:{self._setenv}.  Reserved.')
                        
                    envData['available'] = True
                    envData['activeUsers'].append({'sessionId': sessionId, 'overallSummaryFile': overallSummaryFile,
                                                   'user': user, 'stage': stage, 'task': task, 'env': self._setenv})
                    message = f'Reserved env as active-user:{self._setenv} user:{user} session:{sessionId} stage:{stage} task:{task}'
                    if trackUtilization:
                        useObj = EnvUtilizationDB().insert(self._setenv, user) 
                else:
                    # Check if port-group(s) is available. 
                    self.portGroupObj = ManagePortGroup()
                    arePortGroupsAvailable = True
                    for eachPortGroup in self.getPortGroups():
                        self.portGroupObj.domain = self.getEnvDomain()
                        self.portGroupObj.portGroup = eachPortGroup 
                        if self.portGroupObj.isPortGroupAvailable() is False:
                            arePortGroupsAvailable = False
 
                    if len(envData['activeUsers']) == 0 and arePortGroupsAvailable:
                        if overallSummaryFile and self.keystackLogger:
                            self.keystackLogger.info(f'sessionId={sessionId} stage={stage} task={task} env={self._setenv}: activeUsers=0. Reserving.')

                        envData['available'] = False 
                        envData['activeUsers'].append({'sessionId': sessionId, 'overallSummaryFile': overallSummaryFile,
                                                       'user': user, 'stage': stage, 'task': task, 'env': self._setenv})
                        message = f'Reserving env as active-user: {self._setenv}  user:{user}  session:{sessionId}  stage:{stage}  task:{task}'
                        if trackUtilization:
                            useObj = EnvUtilizationDB().insert(self._setenv, user)
                    else:
                        updateDB = False
                        if overallSummaryFile and self.keystackLogger:
                            self.keystackLogger.info(f'activeUsers > 0. Go to wait-list.  sessionId={sessionId} stage={stage} task={task} env={self._setenv}')
                            
                        # Go to wait-list because someone is actively using the env
                        envData['waitList'].append({'sessionId': sessionId, 'overallSummaryFile': overallSummaryFile, 
                                                    'user': user, 'stage': stage, 'task': task, 'env': self._setenv})
                        self.goToWaitlistOnDB(envData)
                        # dbObj = DB.name.updateDocument(Vars.collectionName,
                        #                                queryFields={'env': self._setenv},
                        #                                updateFields=envData)

                        # If the env active-user is not running, remove the active-user. amINext() will make the new pipeline active-user.
                        if overallSummaryFile:
                            isEnvOnHold = self.isActiveUserHoldingEnvOnFailure(overallSummaryFile)
                            if isEnvOnHold is False:
                                data = readJson(overallSummaryFile)
                                pipelineSessionName = data['topLevelResultFolder']  
                                            
                                for activeUser in envData['activeUsers']:
                                    # Cannot expect the active-user have an overallSummaryFile because the user might have manually reserved the env.
                                    if activeUser['overallSummaryFile']:
                                        if pipelineSessionName != activeUser['overallSummaryFile'].split('/')[-1]:
                                            if isActiveUserRunning(overallSummaryFile=activeUser['overallSummaryFile']) is False:
                                                if overallSummaryFile:
                                                    self.keystackLogger.info(f"[EnvMgmt.isActiveUserRunning]: Not Running!  Calling removeFromActiveUsersList() to remove user={activeUser['user']} stage={activeUser['stage']} task={activeUser['task']} env={self._setenv}")
                                                    
                                                self.removeFromActiveUsersList([{'user': activeUser['user'], 
                                                                                'sessionId': activeUser['sessionId'], 
                                                                                'stage': activeUser['stage'], 
                                                                                'task': activeUser['task']}])
                                        else:
                                            # The active-user is me running. returning True
                                            return ('success', '')   
                                                                
                if updateDB:
                    if overallSummaryFile and self.keystackLogger:
                        self.keystackLogger.info(f'Updating DB: env={self._setenv}  envData: {json.dumps(envData, indent=4)}')
                      
                    dbObj = DB.name.updateDocument(Vars.collectionName,
                                                   queryFields={'env': self._setenv},
                                                   updateFields=envData)

                    if dbObj:
                        if overallSummaryFile and self.keystackLogger:
                            self.keystackLogger.info(f'Updated DB: sessionId={sessionId} stage={stage} task={task} env={self._setenv}')

                        return ('success', message)
                    else:
                        if overallSummaryFile and self.keystackLogger:
                            self.keystackLogger.error(f'Updating DB failed: sessionId={sessionId} stage={stage} task={task} env={self._setenv}')

                        return ('failed', '[EnvMgmt.reserveEnv]: Updating Env DB failed for reserveEnv')
                else:
                    return ('success', '')
            else:
                if overallSummaryFile and self.keystackLogger:
                    self.keystackLogger.error(f'mongoDB envMgmt for the env has no data: sessionId={sessionId} stage={stage} task={task} env={self._setenv}')
                    
                return ('failed', f'[EnvMgmt.reserveEnv]: mongoDB envMgmt for the env has no data: {self._setenv}')
            
        except Exception as errMsg:
            if overallSummaryFile and self.keystackLogger:
                self.keystackLogger.error(f'sessionId={sessionId} stage={stage} task={task} env={self._setenv}: Exception error: {traceback.format_exc(None, errMsg)}')

            return ('failed', traceback.format_exc(None, errMsg))
                                            
    def releaseEnv(self):
        """ 
        The Release button. For manual release only.
        Mostly likely the env is in a stuck or weird state that needs to be updated. 
        Release the current activeUsers session/person on the env
        """
        try:
            envData = self.getEnvDetails()
            if envData:
                if len(envData['activeUsers']) > 0:
                    envData['activeUsers'].pop(0)
                    if len(envData['waitList']) > 0:
                        envData['activeUsers'].append(envData['waitList'][0])
                        envData['waitList'].pop(0)
 
                        if self.isEnvParallelUsage():
                            envData.update({'available': True})
                        else:
                            envData.update({'available': False})
                    else:
                        envData.update({'available': True})

                dbObj = DB.name.updateDocument(Vars.collectionName,
                                               queryFields={'env': self._setenv},
                                               updateFields=envData)

                if dbObj:
                    return 'success'
                else:
                    return ('failed', 'Updating Env DB failed')
        
        except Exception as errMsg:
            return ('failed', str(errMsg))
        
    def resetEnv(self):
        """
        Blank out the env by removing it.
        
        Return
            True|False
        """
        result = DB.name.updateDocument(Vars.collectionName, queryFields={'env':self._setenv},
                                        updateFields={'available':True, 'activeUsers':[], 'waitList':[]})

    def syncEnvMgmtDBWithEnvYamlFiles(self):
        """ 
        Check if all the envs in EnvMgmt MongoDB exists in
        yml files.  If env yaml files don't exists in the filesystem /opt/KeystackTests/Envs, remove the
        env in MongoDB
        """
        dbObj = DB.name.getDocuments(Vars.collectionName,
                                    fields={},
                                    includeFields={'_id':0,
                                                   'available':0,
                                                   'loadBalanceGroups':0,
                                                   'activeUsers':0,
                                                   'waitList':0}
                                    )

        # self.envPath = f'{self.keystackTestRootPath}/Envs'
        for env in dbObj:
            if os.path.exists(f'{self.envPath}/{env["env"]}.yml') is False:
                DB.name.deleteOneDocument(collectionName=Vars.collectionName, fields={'env': env['env']})
        
    def syncTestcaseEnvMgmt(self):
        print('ManageEnv:syncTestcaseEnvMgmt')
        if RedisMgr.redis:
            envMgmtData = RedisMgr.redis.getAllPatternMatchingKeys(pattern="envMgmt*")
            
            # For each envMgmt in redis, verify if the overallSummary timestamp exists. 
            # If not, remove the envMgmt data from redis.
            for envMgmt in envMgmtData:
                # envMgmt-11-15-2024-12:15:16:774425_6145-STAGE=Test_TASK=standAloneTests_ENV=DOMAIN=Communal-Samples-demoEnv1
                regexMatch2 = search('envMgmt-(.+)-STAGE', envMgmt)
                if regexMatch2:
                    envMgmtTimestamp = regexMatch2.group(1)
                    overallSummaryData = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f"overallSummary-*-{envMgmtTimestamp}")
                    if len(overallSummaryData) == 0:
                        #print(f'syncTestcaseEnvMgmt: Deleting: {envMgmt}')
                        RedisMgr.redis.deleteKey(keyName=envMgmt)
            