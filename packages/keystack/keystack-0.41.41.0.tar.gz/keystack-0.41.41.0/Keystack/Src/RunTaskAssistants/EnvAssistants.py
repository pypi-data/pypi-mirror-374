import os, sys
import re
import json
import traceback
from copy import deepcopy
import time
from pydantic import Field, dataclasses
from pprint import pprint

from globalVars import GlobalVars
from commonLib import KeystackException, execCliCommand, ConnectTelnet, parseForDomain
from keystackUtilities import execSubprocess2, readYaml, readJson, writeToJson, chownChmodFolder, getDictIndexList, getDictIndexFromList
from PortGroupMgmt import ManagePortGroup
from LabInventory import InventoryMgmt
from RedisMgr import RedisMgr
import EnvMgmt
from sshAssistant import ConnectSSH

@dataclasses.dataclass
class EnvAssistant:
    runTaskObj: object

    def verifyServerResponse(self, response):
        try:
            response.json()
            return True
        except Exception as errMsg:
            errorMsg = 'Test Aborted!  Retried request 10x. Lost connection with the server.'
            self.runTaskObj.keystackLogger.error(errorMsg)
            self.runTaskObj.playbookObj.exitTest = True
            return False
                    
    def createEnvMgmtDataFile(self, stage, taskName, envFileFullPath):
        """ 
        This is a helper function that creates an env tracker file when a load balance 
        group selects an Env to use.
        
        Ex: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/05-18-2023-13:45:25:548001_2445/.Data/EnvMgmt
        """                             
        # Create an env mgmt file in:  /timestampFolder/.Data/EnvMgmt
        # Get the DOMAIN=<domain>/envName 
        regexMatch = re.search(f'.+/Envs/(.+)\.(yml|yaml)?', envFileFullPath)
        if regexMatch:
            env = regexMatch.group(1)
        
        envNameForResultPath = env.replace('/', '-')
         
        # NOTE! Adding/Subtracting parameters here must be done in EnvAssistants:playbook class also.
        #
        # Session ID Env tracker:                           
        #    Using envMgmt file to keep track of the env usage in case -holdEnvsIfFailed was included in the test.
        #    KeystackUI sessionMgmt creates an onclick button to release the envs when done debugging.
        #    Every stage/module/env has its own json envMgmt data file
        envMgmtData = {'user': self.runTaskObj.playbookObj.user,
                       'sessionId': self.runTaskObj.playbookObj.timestampFolderName,
                       'testResultRootPath': self.runTaskObj.playbookObj.timestampFolder,
                       'stage': stage, 
                       'task': taskName, 
                       'env': env,
                       'portGroups': [], 
                       'envIsReleased': False, 
                       'holdEnvsIfFailed': self.runTaskObj.playbookObj.holdEnvsIfFailed}
                
        if self.runTaskObj.playbookObj.isKeystackAlive:
            envMgmtDataFile = f'envMgmt-{self.runTaskObj.playbookObj.timestampFolderName}-STAGE={stage}_TASK={taskName}_ENV={envNameForResultPath}'
            self.runTaskObj.redisEnvMgmt = envMgmtDataFile
            self.runTaskObj.playbookObj.writeToRedisEnvMgmt(keyName=self.runTaskObj.redisEnvMgmt, data=envMgmtData)
        else:
            envMgmtDataFile = f'{self.runTaskObj.playbookObj.envMgmtDataFolder}/STAGE={stage}_TASK={taskName}_ENV={envNameForResultPath}.json'
            writeToJson(envMgmtDataFile, envMgmtData, mode='w') 
            chownChmodFolder(envMgmtDataFile, self.runTaskObj.playbookObj.user, GlobalVars.userGroup, stdout=False)

        self.runTaskObj.keystackLogger.debug(f'{envMgmtDataFile} -> {json.dumps(envMgmtData, indent=4)}')                        
        return envMgmtDataFile
                            
    def envHandler(self):
        """ 
        Check which env to use from Playbook parameters env and envLoadBalance. Reserve env.
        
        envMgmt: Object instance of EnvMgmt.ManageEnv()
        """
        try:
            # Update() will call ManagePortGroup().selfUpdateActiveUsersAndWaitList()
            self.runTaskObj.playbookObj.envMgmtObj.update()

            # Note: self.runTaskObj.env = DOMAIN=Communal/Samples/demoEnv1
            
            # self.runTaskObj.taskProperties: {'enable': True, 'abortOnFailure': False, 'bridgeEnvParams': True, 'env': 'Samples/loadcoreSample', 'loadBalanceGroup': 'qa', 'variables': {'serverName': 'regressionServer', 'serverIp': '10.10.10.1'}, 'playlist': ['/Modules/CustomPythonScripts/Samples/BridgeEnvParams/dynamicVariableSample.yml'], 'app': 'CustomPython', 'artifactsFolder': '/opt/KeystackTests/Results/GROUP=Default/PLAYBOOK=Samples-pythonSample/05-15-2023-12:02:54:277306_5565/Artifacts', 'envParams': {'parallelUsage': False, 'server1': '192.168.28.6', 'serverIp': '1.1.1.2', 'login': 'admin', 'description': 'test'}}
             
            # Using Load-Balance Groups
            if self.runTaskObj.taskProperties['env'] != 'not-required' \
                and self.runTaskObj.env is None and self.runTaskObj.taskSummaryData.get('loadBalanceGroup', None):
                if self.runTaskObj.playbookObj.isKeystackAlive:
                    # This will set self.runTaskObj.env with an available env to use
                    desiredLBG = self.runTaskObj.taskSummaryData.get('loadBalanceGroup', None)
                    self.runTaskObj.keystackLogger.debug(f"stage={self.runTaskObj.stage}  task={self.runTaskObj.task}  env={self.runTaskObj.env} - Requires loadBalanceGroup={desiredLBG}")
                    
                    # envLoadBalance() will set self.runTaskObj.env = env
                    # and set self.runTaskObj.envFile
                    self.envLoadBalance()
                else:
                    errorMsg = f'The task {self.runTaskObj.task} uses loadBalanceGroup {self.runTaskObj.taskSummaryData["loadBalanceGroup"]}, but this requires Keystack docker container which is not running. Either enable the docker container or use a static env.'
                    self.runTaskObj.keystackLogger.error(errorMsg)
                    self.runTaskObj.logTaskExceptionError(errorMsg=errorMsg)
                    
            # self.runTaskObj.env: Samples/loadcoreSample
            # envParams: {'parallelUsage': False, 'server1': '192.168.28.6', 'username': 'admin', 'password': 'admin', 'licenseServerIp': '10.10.10.1', 'licenseServerUser': 'admin', 'licenseServerPassword': 'admin'}
            if self.runTaskObj.envFile is None:
                self.runTaskObj.taskSummaryData.update({'env': self.runTaskObj.taskProperties['env']})
                writeToJson(self.runTaskObj.taskSummaryFile, self.runTaskObj.taskSummaryData, mode='w', threadLock=self.runTaskObj.statusFileLock)
                                                                   
            if self.runTaskObj.envFile:
                envFileData = readYaml(self.runTaskObj.envFile) 
                envDomain = parseForDomain(self.runTaskObj.envFile)
                     
                if self.runTaskObj.playbookObj.isKeystackAlive and self.runTaskObj.env and self.runTaskObj.env != 'not-required':
                    # Get all device details from the env yml file for scripts to digest
                    if 'devices' in envFileData.keys():
                        for device, deviceDetails in envFileData['devices'].items():                
                            if deviceDetails == " get_device_details_from_inventory":
                                deviceDetails = InventoryMgmt(domain=self.runTaskObj.playbookObj.domain, device=device).getDeviceDetails()
                                if deviceDetails is None:
                                    self.runTaskObj.logTaskExceptionError(f'The Env Yml file stated a device [{device}:  get_device_details_from_inventory] is not found in the Lab Inventory DB in domain [{self.runTaskObj.playbookObj.domain}]') 
                                else:   
                                    self.runTaskObj.devicesData.update(deviceDetails)
                            else:
                                self.runTaskObj.devicesData.update({device: deviceDetails})
                                
                    # PORT-GROUP HANDLINGS: Get Port-Group ports and port eetails to include in keystackEnv resources
                    self.includePortGroupResourcesHelper(envDomain, envFileData, self.runTaskObj.stage, self.runTaskObj.task, self.runTaskObj.env.replace('/', '-'))
   
                    # Only if the env is NOT parallel used (Not-Shareable), need to reserve and wait
                    if self.runTaskObj.taskProperties.get('parallelUsage', False) is False:  
                        if 'envParams' in self.runTaskObj.taskProperties:  
                            if self.runTaskObj.execRestApiObj:
                                self.reserveAndWaitForEnv(sessionId=self.runTaskObj.timestampFolderName,
                                                        overallSummaryFile=f'{self.runTaskObj.resultsTimestampFolder}/overallSummary.json', 
                                                        user=self.runTaskObj.user, 
                                                        stage=self.runTaskObj.stage,
                                                        task=self.runTaskObj.task)

                                self.reserveAndWaitForPortGroup(sessionId=self.runTaskObj.timestampFolderName,
                                                                overallSummaryFile=f'{self.runTaskObj.resultsTimestampFolder}/overallSummary.json', 
                                                                user=self.runTaskObj.user, 
                                                                stage=self.runTaskObj.stage, 
                                                                task=self.runTaskObj.task,
                                                                env=self.runTaskObj.env.replace('/',  '-'))

                            if self.runTaskObj.execRestApiObj is None:
                                if self.runTaskObj.taskProperties.get('parallelUsage', False) is False:
                                    errorMsg = f'The task "{self.runTaskObj.task}" uses Env {self.runTaskObj.env} that has parallelUsage=False.\nCannot run the task without Keystack docker container running.'
                                    self.runTaskObj.keystackLogger.error(errorMsg)
                                    self.runTaskObj.logTaskExceptionError(errorMsg)
                                
                    # The env is parallel used (shareable)                
                    if self.runTaskObj.taskProperties.get('parallelUsage', False) == True:
                        # Update env active user. If the mongodb has no data for the env, EnvMgmt.getEnvDetails will call addEnv()
                        if self.runTaskObj.execRestApiObj:
                            self.reserveEnv(overallSummaryFile=f'{self.runTaskObj.resultsTimestampFolder}/overallSummary.json',
                                            env=self.runTaskObj.taskProperties['env'])

                        # Reseve the port-group
                        for portGroup in self.runTaskObj.envPortGroups:
                            params = {'overallSummaryFile': f'{self.runTaskObj.resultsTimestampFolder}/overallSummary.json',
                                    'domain': self.runTaskObj.playbookObj.domain,
                                    'portGroup': portGroup, 
                                    'sessionId': self.runTaskObj.timestampFolderName, 
                                    'user': self.runTaskObj.user,
                                    'stage': self.runTaskObj.stage, 
                                    'task': self.runTaskObj.task,
                                    'env': self.runTaskObj.env.replace('/',  '-'),
                                    'trackUtilization': True, 
                                    'webhook': True}

                            self.reservePortGroup(portGroup, params)
                else:
                    if 'devices' in envFileData.keys():
                        for device, deviceDetails in envFileData['devices'].items():                
                            if deviceDetails == " get_device_details_from_inventory":
                                self.runTaskObj.logTaskExceptionError(f'The Env Yml file stated a device [{device}:  get_device_details_from_inventory], but the Keystack container is not running. Cannot retrieve device details from lab inventory') 
  
            # Note: The stage/task xpath were initialized in the playbook class in:
            #       executeStages().runTaskHelper() function
            self.runTaskObj.playbookObj.overallSummaryData['stages'][self.runTaskObj.stage]['tasks'].append(
                {self.runTaskObj.task: {'result':None, 'env': self.runTaskObj.taskProperties['env'], 'progress': '', 'currentlyRunning': None}})

            self.runTaskObj.taskSummaryData.update({'taskResultsFolder': self.runTaskObj.taskResultsFolder})
            writeToJson(self.runTaskObj.taskSummaryFile, self.runTaskObj.taskSummaryData, mode='w', threadLock=self.runTaskObj.statusFileLock)
            self.runTaskObj.playbookObj.updateOverallSummaryDataOnRedis()
            
            self.autoSetup(self.runTaskObj.envFile, keystackLogger=self.runTaskObj.keystackLogger)
            #self.configLayer1Interconnects()            
            
        except Exception as errMsg:
            print('\nenvHandler error:', traceback.format_exc(None, errMsg))
            self.runTaskObj.keystackLogger.error(f'EnvAssistant:envHandler: {traceback.format_exc(None, errMsg)}')

    def configLayer1Interconnects(self):
        """ 
        Layer1 interconnect
        
        Work-In-Progress:
            -  /Apps/Link_Layer/Cisco/connect.py
            
        from keystackEnv import keystack
        from PortGroupMgmt import ManagePortGroup
        from db import DB
        from RedisMgr import RedisMgr

        class Layer1:
            def __init__(self):
                keystack.logError(f'----- LinkLayer:Cisco:Cat6k:layer1.py ----'
        """
        self.runTaskObj.playbookObj.envMgmtObj.setenv = self.runTaskObj.env

        sys.path.insert(0, GlobalVars.keystackSystemPath)
        from Apps.Link_Layer.Cisco import connect

        for portGroup in self.runTaskObj.envPortGroups:
            x = connect.Layer1(self.runTaskObj.playbookObj.domain, 
                               portGroup, 
                               self.runTaskObj.keystackLogger)
            result = x.go()
            if result == 'failed':
                self.releaseEnv(self.runTaskObj.env)
                self.releasePortGroup()
                self.runTaskObj.logTaskExceptionError(f'configLayer1Interconnect failed')
                return
            
    def reserveEnv(self, overallSummaryFile, env):
        """ 
        Put sessionId into active-user
        
        env: <str>: <envName> | <envGroup>/<envName>
        """
        if self.runTaskObj.execRestApiObj:
            params = {'env': env, 'sessionId':self.runTaskObj.timestampFolderName, 'overallSummaryFile':overallSummaryFile, 
                      'user':self.runTaskObj.user, 'stage':self.runTaskObj.stage, 'task':self.runTaskObj.task, 'trackUtilization':True, 'webhook':True}
                        
            self.runTaskObj.keystackLogger.debug(f'EnvAssist.reserveEnv: stage:{self.runTaskObj.stage}   task:{self.runTaskObj.task}  env:{env}  Calling: /api/v1/env/reserve')
            # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
            response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/env/reserve', params=params, showApiOnly=True)
            if self.verifyServerResponse(response) is False:
                return
                
            self.runTaskObj.keystackLogger.debug(f'EnvAssist.reserveEnv: /api/v1/env/reserve status_code: {response.status_code}')
            if response.status_code != 200:
                self.runTaskObj.keystackLogger.error(f'EnvAssist.reserveEnv: {response.status_code}')
                self.runTaskObj.playbookObj.overallSummaryData['exceptionErrors'].append(f'status code: {response.status_code}')
                self.runTaskObj.playbookObj.updateOverallSummaryDataOnRedis()


    def reservePortGroup(self, portGroup, params):
        """ 
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        sessionId = request.data.get('sessionId', None)
        stage = request.data.get('stage', None)
        task = request.data.get('task', None)
        env = request.data.get('env', None)
        userReserving = request.data.get('user', None)
        overallSummaryFile = request.data.get('overallSummaryFile', None)
        """
        try:
            self.runTaskObj.keystackLogger.debug(f'EnvAssistants.reservePortGroup: stage:{self.runTaskObj.stage}   task:{self.runTaskObj.task}  portGroup:{portGroup}  Calling: /api/v1/portGroup/reserveUI')
            # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
            response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/portGroup/reserveUI', params=params, showApiOnly=True) 
            if self.verifyServerResponse(response) is False:
                return
                
            self.runTaskObj.keystackLogger.debug(f'EnvAssistants.reservePortGroup: reserv /api/v1/portGroup/reserveUI status_code: {response.status_code}')
            if response.status_code != 200:
                self.runTaskObj.keystackLogger.error(f'EnvAssistants.reservePortGroup: {response.json["errorMsg"]}')
                self.runTaskObj.playbookObj.overallSummaryData['exceptionErrors'].append(response.json["errorMsg"])
                self.runTaskObj.playbookObj.updateOverallSummaryDataOnRedis()
                raise KeystackException(f'EnvAssistants: reservePortGroup failed: {response.json["errorMsg"]}')
        except Exception as errMsg:
            self.runTaskObj.keystackLogger.error(f'EnvAssistants.reservePortGroup: {traceback.format_exc(None, errMsg)}')
                            
    def releaseEnv(self, env):
        """ 
        Remove the sessionId from active-user
        
        env: <str>: <envName> | <envGroup>/<envName>
        """
        if self.runTaskObj.execRestApiObj:
            params = {'env': env, 'sessionId':self.runTaskObj.timestampFolderName,
                      'user':self.runTaskObj.user, 'stage':self.runTaskObj.stage, 'task':self.runTaskObj.task, 'webhook':True}

            # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
            self.runTaskObj.keystackLogger.debug(f'EnvAssist.releaseEnv:  stage={self.runTaskObj.stage} task={self.runTaskObj.task} env:{env}  Calling: /api/v1/env/removeFromActiveUsersListUI')
            response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/env/removeFromActiveUsersListUI', showApiOnly=True, params=params)
            if self.verifyServerResponse(response) is False:
                return
                
            self.runTaskObj.keystackLogger.debug(f'EnvAssist.releaseEnv: status_code: {response.status_code}')
            if response.status_code != 200:
                self.runTaskObj.keystackLogger.error(response.json["errorMsg"])
                raise KeystackException(f'EnvAssistants: releaseEnv failed: {response.json["errorMsg"]}')
    
    def releasePortGroup(self):
        if len(self.runTaskObj.envPortGroups) == 0:
            return
    
        for portGroup in self.runTaskObj.envPortGroups:
            params = {'domain': self.runTaskObj.playbookObj.domain, 'portGroup': portGroup,
                      'sessionId': self.runTaskObj.timestampFolderName,
                      'user':self.runTaskObj.user, 'stage':self.runTaskObj.stage,
                      'task':self.runTaskObj.task, 'webhook':True}
                    
            # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
            self.runTaskObj.keystackLogger.debug(f'EnvAssist.releasePortGroup:  stage={self.runTaskObj.stage} task={self.runTaskObj.task} portGroup:{portGroup}  Calling: /api/v1/portGroup/removeFromActiveUsersListUI')

            response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/portGroup/removeFromActiveUsersListUI', showApiOnly=True, params=params)
            if self.verifyServerResponse(response) is False:
                return
                
            self.runTaskObj.keystackLogger.debug(f'EnvAssist.releasePortGroup: port-group={portGroup} status_code:{response.status_code}')
            if response.status_code != 200:
                self.runTaskObj.keystackLogger.error(response.json["errorMsg"])
                raise KeystackException(f'EnvAssistants: releasePortGroup failed: port-group={portGroup} {response.json["errorMsg"]}')        
                  
    def reserveAndWaitForEnv(self, sessionId, overallSummaryFile, user, stage, task):
        """ 
        Playbook tasks cannot expect envs are available
        This function checks if the env is avaiable.
        If not, go to wait-list and wait until 
        the test sessionId is next in line to use the env.
        """
        if self.runTaskObj.execRestApiObj is None:
            self.runTaskObj.keystackLogger.debug('EnvAssist:reserveAndWaitForEnv: execRestApiObj is None. Return.')
            return
        
        doOnce = False
        try:
            try:
                # env: DOMAIN=Communal/Samples/demoEnv1
                if '-' in self.runTaskObj.taskProperties['env']:
                    env = self.runTaskObj.taskProperties['env'].replace('-', '/')
                else:
                    env = self.runTaskObj.taskProperties['env']

                reserveEnvStatus = 'success'
                params = {'env':env, 'sessionId':sessionId, 'overallSummaryFile':overallSummaryFile, 
                          'user':user, 'stage':stage, 'task':task, 'trackUtilization':True, 'webhook':True}
                
                # reserve -> reserveEnv: Verifies if timestamp is next and if active-user == 0: go to active-user
                #                        else: go to waitlist
                # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
                # Reserve also checks if port-groups are available. If not available, put them in the wait-list.
                response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/env/reserve', params=params, showApiOnly=False)
                if self.verifyServerResponse(response) is False:
                    return
                
                self.runTaskObj.keystackLogger.debug(f'EnvAssist:reserveAndWaitForEnv: /api/v1/env/reserve: stage:{stage}  task:{task}  env:{env}  status_code:{response.status_code}')
                if response.status_code != 200:
                    self.runTaskObj.keystackLogger.error(f'EnvAssist:reserveAndWaitForEnv:  stage:{stage}  task:{task} env:{env} /api/v1/env/reserve response failed status code: {response.status_code}. ErrorMsg: {response.json()["errorMsg"]}')
                    reserveEnvStatus = 'failed'
                                        
            except Exception as errMsg:
                reserveEnvStatus = 'failed'
                
            if reserveEnvStatus == 'failed':
                self.runTaskObj.keystackLogger.error(f'EnvAssist:reserveAndWaitForEnv: env:{env} /api/v1/env/reserve response failed: {response.status_code}')
                self.runTaskObj.logTaskExceptionError(f'reserveAndWaitForEnv: Failed. Called /api/v1/env/reserve. Status code {response.status_code}')
                return
            
            params = {'overallSummaryFile': self.runTaskObj.playbookObj.overallSummaryDataFile,
                      'sessionId':sessionId, 'env': env, 'user': user, 'stage': stage, 'task': task, 'webhook': True} 

            self.runTaskObj.keystackLogger.debug(f'EnvAssist:reserveAndWaitForEnv: Entering while loop calling /env/amINext -> env:{env} stage:{stage} task:{task}')

            while True:
                """
                Calling /reserve has either put the job in active-user list or in the wait-list.
                This while loop keeps checking if the job is in the active-list, which means the job is next to run.
                Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
                amINext (envViews.py) -> amIRunning (EnvMgmt.py)->
                   if activeUser > 0:
                       if isActiveUserHoldingEnvOnFailure(): return False
                       if envMgmtData['envIsReleased'] == True:
                           removeFromActiveUsersList()
                               updateMongoEnvMgmt env: reoveActiveUser & available=True
                               refreshEnv()
                                   if len(envData['activeUsers']) == 0 and len(envData['waitList']) == 0: return True
                                   if activeUser > 0:
                                       if active-user-overallSummaryFile == False:
                                           envDataMongoDB['available'] = True
                                           envDataMongoDB['activeUsers'].pop(index)
                                       else:
                                            if overallSummaryData['status'] == 'Running':
                                                envDataMongoDB['available'] = False
                                            else:                            
                                                envDataMongoDB['activeUsers'].pop(index)
                                                envDataMongoDB['available'] = True
                                    else:
                                        if len(envData['waitList']) > 0:
                                            if getSessionIdInWaitingList:
                                                for index, inQueue in waitlist:
                                                    if inQueue['sessionId'] == getSessionIdInWaitingList:
                                                        envDataMongoDB['activeUsers'].append(envDataMongoDB['waitList'][index])
                                                        envDataMongoDB['waitList'].pop(index)
                                                        envDataMongoDB['available'] = False
                                                        foundSessionIdInWaitList = True
                                                        
                                                if foundSessionIdInWaitList is False:
                                                    # Get the next sessionId in the wait-list
                                                    envDataMongoDB['activeUsers'].append(envDataMongoDB['waitList'][0])
                                                    envDataMongoDB['waitList'].pop(0)
                                                    envDataMongoDB['available'] = False
                                            else:
                                                # Getting the top-of-waitList to active-user
                                                envDataMongoDB['activeUsers'].append(envDataMongoDB['waitList'][0])
                                                envDataMongoDB['waitList'].pop(0)
                                                envDataMongoDB['available'] = False
                                    updateEnvMgmtMongoDB
                            
                            # At this point, active-user and waitList are refreshed        
                            if user == currentActiveUser['user'] and \
                                sessionId == currentActiveUser['sessionId'] and \
                                stage == currentActiveUser['stage'] and \
                                    task == currentActiveUser['task']:
                                return True
                            else:
                                return False
                """
                response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/env/amINext', params=params, showApiOnly=False)
                if self.verifyServerResponse(response) is False:
                    return
                 
                # reponse: {'status': 'success', 'errorMsg': None, 'result': False}
                if response.json()['status'] == 'failed':
                    errorMsg = f'reserveAndWaitForEnv: Failed. Called /api/v1/env/amINext. Status code {response.status_code}'
                    self.runTaskObj.keystackLogger.error(errorMsg)
                    self.runTaskObj.logTaskExceptionError(errorMsg)
                    return
                
                if response.json()['result']:
                    # I am next to run
                    self.runTaskObj.taskSummaryData.update({'status': 'Running'})
                    self.runTaskObj.keystackLogger.info(f'env: {env} /api/v1/env/amINext: Yes. Status changed to Running -> stage:{stage} task:{task} env:{env} ')
                    break
                else:
                    if doOnce is False:
                        self.runTaskObj.taskSummaryData.update({'status': 'Waiting-For-Env'})
                        writeToJson(self.runTaskObj.taskSummaryFile, self.runTaskObj.taskSummaryData, mode='w', threadLock=self.runTaskObj.statusFileLock)
                        self.runTaskObj.keystackLogger.info(f'/api/v1/env/amINext: No. -> Waiting: stage:{stage} task:{task} env:{env} ')
                        doOnce = True

                    time.sleep(5)
                    continue
                
        except Exception as errMsg:
            self.runTaskObj.logTaskExceptionError(traceback.format_exc(None, errMsg))

    def reserveAndWaitForPortGroup(self, sessionId, overallSummaryFile, user, stage, task, env):
        """ 
        This is for runPlaybook only.
        Playbooks cannot expect the env is available for usage at any time.
        This function checks if the env is avaiable.
        If not, go to wait-list and wait until 
        the test sessionId is next in line to use the portGroup.
        """
        if self.runTaskObj.execRestApiObj is None:
            self.runTaskObj.keystackLogger.debug('EnvAssist:reserveAndWaitForPortGroup: execRestApiObj is None. Return.')
            return
        
        logMessageOnce = False
        
        try:
            # Put all port-groups in reservation first
            # Then use while loop to wait until all port-groups are set to active
            for portGroup in self.runTaskObj.envPortGroups:
                try:
                    params = {'domain': self.runTaskObj.playbookObj.domain, 'portGroup': portGroup, 'sessionId':sessionId,     
                              'overallSummaryFile':overallSummaryFile, 'user':user, 'stage':stage, 'task':task, 'env': env,
                              'trackUtilization':True, 'webhook':True}

                    self.runTaskObj.keystackLogger.debug(f'EnvAssist:reserveAndWaitForPortGroup: Calling: /api/v1/portGroup/reserveUI portGroup:{portGroup}')
                    # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
                    # reserve will ultimately call EnvMgmt reserveEnv(). If the env is actively used, then go to the wait-list.
                    
                    response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/portGroup/reserveUI', params=params, showApiOnly=True)
    
                    if self.verifyServerResponse(response) is False:
                        return
                    
                    self.runTaskObj.keystackLogger.debug(f'EnvAssist:reserveAndWaitForPortGroup: /api/v1/portGroup/reserveUI: stage:{stage}  task:{task}  portGroup:{portGroup}  status_code:{response.status_code}')
                    if response.status_code != 200:
                        self.runTaskObj.keystackLogger.error(f'EnvAssist:reserveAndWaitForPortGroup:  stage:{stage}  task:{task}  env:{env}  portGroup:{portGroup} /api/v1/portGroup/reserveUI response failed status code: {response.status_code}. ErrorMsg: {response.json()["errorMsg"]}')
                                                
                except Exception as errMsg:
                    self.runTaskObj.keystackLogger.error(f'EnvAssist:reserveAndWaitForPortGroup: portGroup:{portGroup} /api/v1/portGroup/reserveUI response failed: {response.status_code}')
                    self.runTaskObj.logTaskExceptionError(f'EnvAssist:reserveAndWaitForPortGroup: Failed. Called /api/v1/portGroup/reserveUI. Status code {response.status_code}')
                    return
      
            
            for portGroup in self.runTaskObj.envPortGroups:
                params = {'domain': self.runTaskObj.playbookObj.domain, 'portGroup': portGroup, 'sessionId':sessionId, 
                          'overallSummaryFile':overallSummaryFile, 'user':user, 'stage':stage, 'task':task, 'env': env,
                          'trackUtilization':True, 'webhook':True}
                            
                self.runTaskObj.keystackLogger.debug(f'EnvAssist:reserveAndWaitForPortGroup: Entering while loop calling /portGroup/amINext -> portGroup:{portGroup} stage:{stage} task:{task} env:{env}')

                while True:
                    # Calling /reserve has either put the job in active-user list or in the wait-list.
                    # This while loop keeps checking if the job is in the active-list, which means the job is next to run.
                    # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
                    response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/portGroup/amINext', params=params, showApiOnly=True)

                    if self.verifyServerResponse(response) is False:
                        return
                    
                    if response.json()['status'] == 'failed':
                        errorMsg = f'EnvAssist:reserveAndWaitForPortGroup: Failed. Called /api/v1/portGroup/amINext. Status code {response.status_code}'
                        self.runTaskObj.keystackLogger.error(errorMsg)
                        self.runTaskObj.logTaskExceptionError(errorMsg)
                        return
                    
                    if response.json()['amINext']:
                        # I am next to run
                        self.runTaskObj.taskSummaryData.update({'status': 'Running'})
                        self.runTaskObj.keystackLogger.debug(f'EnvAssist:reserveAndWaitForPortGroup: Status changed to Running -> portGroup:{portGroup} stage:{stage} task:{task} env:{env}')
                        break
                    else:
                        if logMessageOnce is False:
                            self.runTaskObj.taskSummaryData.update({'status': 'Waiting-For-PortGroup: {portGroup}'})
                            writeToJson(self.runTaskObj.taskSummaryFile, self.runTaskObj.taskSummaryData, mode='w', threadLock=self.runTaskObj.statusFileLock)
                            logMessageOnce = True

                        time.sleep(5)
                        continue
                
        except Exception as errMsg:
            self.runTaskObj.logTaskExceptionError(traceback.format_exc(None, errMsg))
                                    
    def envLoadBalance(self):
        """ 
        Using env load balance requires Keystack docker container.
        If this is not running, use static env.
        
        All this function does is get an available env from a load balance group.
        Still must reserve the env
        """
        isEnvAvailable = False
        waitInterval = 10
        showErrorOnce = 0
        showErrorOnce1 = True
        timeout = 10
        counter = 0

        try:
            if self.runTaskObj.execRestApiObj is None or self.runTaskObj.playbookObj.envMgmtObj is None:
                errorMsg = f'The task {self.runTaskObj.task} uses loadBalanceGroup {self.runTaskObj.taskSummaryData["loadBalanceGroup"]}, but this requires Keystack docker container which is not running. Either enable Keystack docker container or use a static envs in the playbook.'
                self.runTaskObj.keystackLogger.error(errorMsg)
                self.runTaskObj.logTaskExceptionError(errorMsg=errorMsg)
                return
        
            while True:
                # Get load balance group envs.  Select an env to use
                self.runTaskObj.keystackLogger.debug(f'stage={self.runTaskObj.stage}  task={self.runTaskObj.task} LBG={self.runTaskObj.taskSummaryData["loadBalanceGroup"]} - Calling: /api/v1/env/loadBalanceGroup/getEnvs')
                response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/env/loadBalanceGroup/getEnvs',
                                                            showApiOnly=False, 
                                                            params={'webhook':True, 
                                                                    'loadBalanceGroup': self.runTaskObj.taskSummaryData['loadBalanceGroup']})
                if self.verifyServerResponse(response) is False:
                    return
                    
                if response.status_code == 406:
                    # Could be no such load balance group
                    self.runTaskObj.keystackLogger.error(response.json()["errorMsg"])
                    self.runTaskObj.logTaskExceptionError(f'envLoadBalance error: {response.json()["errorMsg"]}')
                    return
                
                if response.status_code == 200:
                    if len(response.json()['loadBalanceGroupEnvs']) == 0:
                        if showErrorOnce1:
                            showErrorOnce1 = False
                            errorMsg = f'envLoadBalance error: The load balance group "{self.runTaskObj.taskSummaryData["loadBalanceGroup"]}" does not have any env configured for stage:{self.runTaskObj.stage} task:{self.runTaskObj.task}. Go to LBG page and add some envs for the LBG. Then the test will continue in 10 seconds.'
                            self.runTaskObj.taskSummaryData.update({"status': f'ERROR: LBG:{self.runTaskObj.taskSummaryData['loadBalanceGroup']} no-env-defined"})
                            self.runTaskObj.keystackLogger.debug(errorMsg)
                            self.runTaskObj.logTaskExceptionError(errorMsg)
                        time.sleep(10)
                        continue
                    
                    # Do some error checking with the json response first
                    for env in response.json()['loadBalanceGroupEnvs']:
                        envFile = f'{GlobalVars.keystackTestRootPath}/Envs/{env}.yml'
                        if os.path.exists(envFile) is False:
                            errorMsg = f'EnvAssistants envLoadBalance error: The load balance group {self.runTaskObj.taskSummaryData["loadBalanceGroup"]} provided the env "{self.runTaskObj.env}" to use, but the env file does not exists. Attempted to remove the env in the DB, but failed: {response.json["errorMsg"]}'
                            writeToJson(self.runTaskObj.taskSummaryFile, self.runTaskObj.taskSummaryData, mode='w', threadLock=self.runTaskObj.statusFileLock, retry=5)
                            self.runTaskObj.keystackLogger.error(errorMsg)
                            self.runTaskObj.logTaskExceptionError(errorMsg)
                            
                            # Remove the env from the DB since the env is removed
                            params = {'loadBalanceGroup': self.runTaskObj.taskSummaryData["loadBalanceGroup"], 'removeSelectedEnvs': env, 'webhook':True}
                            # Must use REST API instead of EnvMgmt. Has to go through the UI because this is where the DB is connected.
                            self.runTaskObj.keystackLogger.debug(f'Calling: /api/v1/env/loadBalanceGroup/removeEnvs  -> {params}')
                            response = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/env/loadBalanceGroup/removeEnvs', showApiOnly=True, params=params)
                            if self.verifyServerResponse(response) is False:
                                return
                    
                            if response.status_code != 200:
                                raise KeystackException(errorMsg)                                              
                    
                    self.runTaskObj.taskSummaryData.update({'status': 'Waiting-For-Env'})
                    writeToJson(self.runTaskObj.taskSummaryFile, self.runTaskObj.taskSummaryData, mode='w', threadLock=self.runTaskObj.statusFileLock)
                    self.runTaskObj.keystackLogger.debug(f'{self.runTaskObj.taskSummaryFile} -> status: Waiting-For-Env')
                                                                    
                    # ['loadcoreSample', 'pythonSample', 'Samples/bobafett']
                    # Verify which env is available
                    for env in response.json()['loadBalanceGroupEnvs']:
                        # isEnvAvaiable must know who the requester is.
                        # It uses the overallSummaryFile timestamp for priority in case two pipelines are waiting
                        # for the same env at the same time, especially when releaseEnvOnFailure is pressed.
                        result = self.runTaskObj.execRestApiObj.post(restApi='/api/v1/env/isEnvAvailable', showApiOnly=True, 
                                                                    params={'webhook':True, 
                                                                            'env': env})
                        if self.verifyServerResponse(result) is False:
                            return

                        # {'isAvailable': True, 'status': 'success', 'errorMsg': None}
                        isEnvAvailable = result.json()['isAvailable']
                        print(f'EnvAssistant: envLoadBalance: isEnvAvailable: env:{env} -> {isEnvAvailable} -> {self.runTaskObj.stage}, {self.runTaskObj.task} ')
                        self.runTaskObj.keystackLogger.debug(f'Is LBG={self.runTaskObj.taskSummaryData["loadBalanceGroup"]} env:{env} available?  {isEnvAvailable} ->  For stage={self.runTaskObj.stage}  task={self.runTaskObj.task}')
                        
                        if isEnvAvailable:
                            # DOMAIN=Communal/Samples/demoEnv1
                            self.runTaskObj.env = env
                            self.runTaskObj.envFile = f'{GlobalVars.keystackTestRootPath}/Envs/{env}.yml'
                            self.runTaskObj.taskProperties['envFile'] = self.runTaskObj.envFile 
                            self.runTaskObj.taskProperties['env'] = env

                            if self.runTaskObj.playbookObj.envMgmtObj:
                                self.runTaskObj.playbookObj.envMgmtObj.setenv = self.runTaskObj.env
                                if self.runTaskObj.playbookObj.envMgmtObj.isEnvParallelUsage() == 'Yes':
                                    isEnvParallelUsage = True
                                else:
                                    isEnvParallelUsage = False
                                                                                           
                            self.runTaskObj.taskProperties['parallelUsage'] = isEnvParallelUsage
                            # Assign the available Env from the load balance group
                            self.runTaskObj.taskProperties.update({'env':env})
                            contents = readYaml(self.runTaskObj.envFile)   
                            self.runTaskObj.taskProperties.update({'envParams': contents})
                            currentTaskResultsFolder = self.runTaskObj.taskResultsFolder
                                
                            # If RedisMgr.redis: returns envMgmt keyName
                            # If not RedisMgr.redis: returns envMgmt json file
                            taskEnvMgmtFileReplacement = self.createEnvMgmtDataFile(stage=self.runTaskObj.stage, taskName=self.runTaskObj.task,
                                                                                    envFileFullPath=self.runTaskObj.envFile)

                            if self.runTaskObj.playbookObj.isFromKeystackUI is False and self.runTaskObj.playbookObj.isKeystackAlive is False:
                                # Keystack was executed from CLI with no docker container and no localhost redis-db
                                self.runTaskObj.taskEnvMgmtFile = taskEnvMgmtFileReplacement      
                                taskEnvMgmtData = readJson(self.runTaskObj.taskEnvMgmtFile)
                                taskEnvMgmtData.update({'env': env})
                                writeToJson(self.runTaskObj.taskEnvMgmtFile, taskEnvMgmtData)
                                chownChmodFolder(self.runTaskObj.taskEnvMgmtFile, self.runTaskObj.user, GlobalVars.userGroup)
                            else:
                                # Keystack was executed from CLI with docker container
                                # Keystack was executed in KeystackUI (with docker) or through rest api
                                taskEnvMgmtData = self.runTaskObj.playbookObj.readRedisEnvMgmt(keyName=taskEnvMgmtFileReplacement)
                                taskEnvMgmtData.update({'env': env})
                                self.runTaskObj.playbookObj.writeToRedisEnvMgmt(keyName=taskEnvMgmtFileReplacement, data=taskEnvMgmtData)

                            # Update the result timestamp task folder ENV name
                            # taskResultsFolder: /Results/DOMAIN="Communal"/04-20-2022-12:34:22:409096_<sessionId>/STAGE=Test_MODULE=PythonScripts_ENV=None
                            envNameForResultFolder = env.replace('/', '-')
                            self.runTaskObj.taskResultsFolder = deepcopy(self.runTaskObj.taskResultsFolder.replace('ENV=None', f'ENV={envNameForResultFolder}'))
                            self.runTaskObj.keystackLogger.debug(f'Updating timestamp folder with updated env -> {self.runTaskObj.taskResultsFolder}')
                            execSubprocess2(['mv', currentTaskResultsFolder, self.runTaskObj.taskResultsFolder], shell=False, cwd=None, showStdout=False)
                            self.runTaskObj.taskTestReportFile = f'{self.runTaskObj.taskResultsFolder}/taskTestReport'
                            # Update the taskSummary file with the updated taskResulsFolder
                            self.runTaskObj.taskSummaryFile = f'{self.runTaskObj.taskResultsFolder}/taskSummary.json'
                            
                            self.runTaskObj.taskSummaryData.update({'env': env, 'envPath': self.runTaskObj.envFile})
                            writeToJson(self.runTaskObj.taskSummaryFile, data=self.runTaskObj.taskSummaryData, mode='w')
                            
                            # Update the runList: "runList": [{"stage": "Test", "task": "CustomPythonScripts","env": null}]
                            currentRunList = self.runTaskObj.playbookObj.overallSummaryData['runList']
                            for index, eachTest in enumerate(currentRunList):
                                if eachTest['stage'] == self.runTaskObj.stage and eachTest['task'] == self.runTaskObj.task:
                                    updates = {'stage':self.runTaskObj.stage, 'task':self.runTaskObj.task, 'env':env} 
                                    self.runTaskObj.playbookObj.overallSummaryData['runList'].pop(index)
                                    self.runTaskObj.playbookObj.overallSummaryData['runList'].insert(index, updates)
                                    break
                                
                            self.runTaskObj.playbookObj.updateOverallSummaryDataOnRedis()
                            envParallelUsage = self.runTaskObj.taskProperties.get('parallelUsage', False)
                            self.runTaskObj.taskSummaryData.update({'status': 'Waiting: LBG-Env', 'isEnvParallelUsed': envParallelUsage})
                            
                            # Handle port-group
                            envDomain = parseForDomain(self.runTaskObj.envFile)
                            envFileData = readYaml(self.runTaskObj.envFile)
                            self.includePortGroupResourcesHelper(envDomain, envFileData, self.runTaskObj.stage, self.runTaskObj.task, env.replace('/', '-'))

                            break
                else:
                    if showErrorOnce == 0:
                        self.runTaskObj.logTaskExceptionError(f'envLoadBalance error: Lost server connection waiting for LBG env. Stage={self.runTaskObj.stage} Task={self.runTaskObj.task}')
                        showErrorOnce = 1
                        
                    if counter < timeout:
                        time.sleep(waitInterval)
                        
                    if counter == timeout:
                        self.runTaskObj.logTaskExceptionError(f'envLoadBalance error: Giving up on connecting to server. Aborting test.')
                        return
                    
                if isEnvAvailable:
                    break
                else:    
                    # Wait 10 seconds to check again for an available env
                    time.sleep(waitInterval)
                    continue
        except Exception as errMsg:
            print('\nenvLoadBalance error:', traceback.format_exc(None, errMsg))
            
    def includePortGroupResourcesHelper(self, envDomain, envFileData, stage, task, env):
        """ 
        Get port-group and port details to include inside the Python scripts 
        
        env: Ex: DOMAIN=Communal-Samples-demoEnv1
        """
        if 'portGroups' in envFileData and type(envFileData['portGroups']) == list:
            self.runTaskObj.envPortGroups = envFileData['portGroups']
            if self.runTaskObj.playbookObj.isKeystackAlive:
                envMgmtDataFile = f'envMgmt-{self.runTaskObj.playbookObj.timestampFolderName}-STAGE={stage}_TASK={task}_ENV={env}'
                envMgmtData = self.runTaskObj.playbookObj.readRedisEnvMgmt(keyName=envMgmtDataFile)
                envMgmtData.update({'portGroups': envFileData['portGroups']})
                self.runTaskObj.playbookObj.writeToRedisEnvMgmt(keyName=self.runTaskObj.redisEnvMgmt, data=envMgmtData)
            else:
                envMgmtDataFile = f'{self.runTaskObj.playbookObj.envMgmtDataFolder}/STAGE={stage}_TASK={task}_ENV={env}.json'
                envMgmtData = readJson(envMgmtDataFile)
                envMgmtData.update({'portGroups': envFileData['portGroups']})
                writeToJson(envMgmtDataFile, envMgmtData, mode='w')
            
            for portGroup in envFileData['portGroups']:
                if self.runTaskObj.playbookObj.envMgmtObj and ManagePortGroup(domain=envDomain, portGroup=portGroup).isPortGroupExists():
                    self.runTaskObj.keystackLogger.info(f'Port-Group [{portGroup}] exists!')
                    # portGroupPorts: {'device-1': {'domain': 'Communal', 'ports': ['1/1', '1/2']}}
                    portGroupDetails = ManagePortGroup(domain=envDomain, portGroup=portGroup).getPortGroupPorts()
                    self.runTaskObj.portGroupsData.update(portGroupDetails)
                    for device, properties in portGroupDetails.items():
                        portDetails = InventoryMgmt(domain=envDomain, device=device).getPortsInPortMgmt(properties["ports"])
                        if len(portDetails) > 0:
                            self.runTaskObj.portsData.update({device: portDetails})
                else:
                    errorMsg = f'Stage={stage} Task={task}: The port-group [{portGroup}] in domain [{envDomain}] does not exists'
                    # To abort the task, use logTaskExceptionError instead of logError()
                    self.runTaskObj.logTaskExceptionError(errorMsg)

    def autoSetup(self, envFile: str, keystackLogger: object=None):
        if envFile is None:
            return
        
        self.setup(envFile, keystackLogger, 'Env-Auto-Setup')
        
    def autoTeardown(self, envFile: str, keystackLogger: object=None):
        if envFile is None:
            return
        
        self.setup(envFile, keystackLogger, 'Env-Auto-Teardown')
        
    def setup(self, envFile: str, keystackLogger: object=None, label: str='Env-Auto-Setup'):
        """ 
        This function is used in 2 places:
           1> Keystack:RunTask() -> EnvAssistant:envHandler()
           2> envViews.py:reserveEnv
           
        Params:
            envFile: Full path to the env Yaml file
            keystackLogger: Object created in Keystack.py
            
        Env Yaml file keywords:
            autoSetup:
                execCliCmdsOnKeystackServer:
                   - ls
                   
                execCliCmdsOnEnvDevices:
                   device1:
                      - configure int 0/1
                      - ip address 1.1.1.1
                      
                   device2:
                      - configure int 0/1
                      - ip address 1.1.1.2
        """
        try:
            # envFile: env file|not-required
            if envFile == 'not-required':
                return
                
            # envFile = self.runTaskObj.envFile 
            envData = readYaml(envFile)
            if 'autoSetup' in envData.keys():
                # {'execCliCmdsOnEnvDevices': {'device_1': ['ls']},
                #  'execCliCmdsOnKeystackServer': ['ls']}
                for localCliCmd in envData['autoSetup']['execCliCmdsOnKeystackServer']:
                    if keystackLogger:
                        self.runTaskObj.keystackLogger.debug(f'[Keystack-Server-Cmd]: {localCliCmd}') 
                         
                    execCliCommand(command=localCliCmd, keystackLogger=self.runTaskObj.keystackLogger)
            
                for remoteDevice in envData['autoSetup']['execCliCmdsOnEnvDevices'].keys():
                    if 'connectionProtocol' in self.runTaskObj.devicesData[remoteDevice].keys():
                        connectionProtocol = self.runTaskObj.devicesData[remoteDevice]['connectionProtocol']
                    else:
                        self.runTaskObj.logTaskExceptionError(f'{label}: Device [{remoteDevice}] connectionProtocol is not defined in the env yml file or in Lab Inventory')
                        continue
                        
                    if 'ipAddress' in self.runTaskObj.devicesData[remoteDevice].keys():
                        ipAddress = self.runTaskObj.devicesData[remoteDevice]['ipAddress']
                    else:
                        self.runTaskObj.logTaskExceptionError(f'{label}: Device [{remoteDevice}] does not contain an IP Address in the env yml file or in Lab Inventory')
                        continue                        
                        
                    if 'ipPort' in self.runTaskObj.devicesData[remoteDevice].keys():
                        if self.runTaskObj.devicesData[remoteDevice]['ipPort'] == 'None':
                            ipPort = None
                        else:
                            ipPort = self.runTaskObj.devicesData[remoteDevice]['ipPort']
                    else:
                        ipPort = None
                    
                    if connectionProtocol == 'ssh' and ipPort is None:
                        ipPort == 22
                        
                    if connectionProtocol == 'telnet' and ipPort is None:
                        ipPort == 23
                    
                    if 'loginName' not in self.runTaskObj.devicesData[remoteDevice].keys():
                        self.runTaskObj.logTaskExceptionError(f'{label}: Device [{remoteDevice}] does not contain a loginName in the env yml file or in Lab Inventory')
                        continue
                    else:
                        login = self.runTaskObj.devicesData[remoteDevice]['loginName']

                    if 'password' not in self.runTaskObj.devicesData[remoteDevice].keys():
                        self.runTaskObj.logTaskExceptionError(f'{label}: Device [{remoteDevice}] does not contain a login password in the env yml file or in Lab Inventory')
                        continue
                    else:
                        password = self.runTaskObj.devicesData[remoteDevice]['password']

                    if 'pkeyFile' in self.runTaskObj.devicesData[remoteDevice].keys():
                        pkeyFile = self.runTaskObj.devicesData[remoteDevice]['pkeyFile']
                    else:
                        pkeyFile = None

                    self.runTaskObj.keystackLogger.debug(f'{label}: ConnectToDevice: {connectionProtocol} {ipAddress} {ipPort}')
                    
                    if connectionProtocol == 'ssh':
                        sshObj = ConnectSSH(host=ipAddress, port=ipPort, username=login, password=password, pkeyFile=pkeyFile, timeout=10)
                        
                        for remoteCmd in envData['autoSetup']['execCliCmdsOnEnvDevices'][remoteDevice]:
                            self.runTaskObj.keystackLogger.debug(f'[Remove-Device:{remoteDevice}]: Command: {remoteCmd}')
                            stdoutString, stderrString = sshObj.sendCommand('ls')
                            if len(stdoutString) > 0:
                                stdoutReformatted = ''
                                for stdout in stdoutString:
                                    print(stdout.replace('\n', ''))

                            if len(stderrString) > 0:
                                stderrReformatted = ''
                                for stderr in stderrString:
                                    stderr = stderr.replace("\n", "")
                                    stderrReformatted += stderr
                                    
                                #print(stderrReformatted)
                                self.runTaskObj.logTaskExceptionError(stderrReformatted) 
                    
                    # TODO: Create a log file for autoSetup/autoTeardown    
                    if connectionProtocol == 'telnet':
                        telnetObj = ConnectTelnet(ip=ipAddress, port=ipPort, login=login, password=password)
                                       
                        for remoteCmd in envData['autoSetup']['execCliCmdsOnEnvDevices'][remoteDevice]:
                            self.runTaskObj.keystackLogger.debug(f'[Remove-Device:{remoteDevice}]: {remoteCmd}')
                            result = telnetObj.sendCliCommand(cmd=remoteCmd)
                            #print(result)
                                            
        except (KeystackException, Exception) as errMsg:
            self.runTaskObj.logTaskExceptionError(f'Env-Auto-Setup: Device [{remoteDevice}] Failed to telnet ip={ipAddress} port={ipPort}')
                                          
    def autoTeardown(self):
        pass
        
