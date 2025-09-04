"""
keystack.py

Description
   An automation test framework that runs Keysight test tools as tasks and manages automated testing.
   This framework also accepts plain Python scripts by using the CustomPythonScripts task.

Requirements
   - python 3.10
   - requirements.txt
   - keystackSetup_<version>.py

CLI Usage:
   Minimum: keystack -playbook <playbook.yml> 
   
   Other options: -sessionId myTest -awsS3 -jira -debug -emailResults

Keystack designed and developed by: Hubert Gee

"""
import sys, os, traceback, datetime, yaml, re, json, time, traceback, csv
from time import sleep
from dotenv import load_dotenv
import types
import subprocess, platform, operator, random
from zipfile import ZipFile
from shutil import rmtree, copy, copytree
from copy import deepcopy
from pathlib import Path
from platform import python_version
from glob import glob
from subprocess import Popen, PIPE
import threading
import yaml
import runpy
from os import fdopen
from pprint import pprint
from pydantic import Field, dataclasses, BaseModel
from typing import Optional

currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir)

from accountMgr import AccountMgr
from Services import Serviceware
from RedisMgr import RedisMgr
from EnvMgmt import ManageEnv
import db                
from globalVars import GlobalVars
from commonLib import createTestResultTimestampFolder, showVersion, generateManifestFile, informAwsS3ServiceForUploads, isCliInsideContainer
from commonLib import validatePlaylistExclusions, validatePlaybook, getRunList, envFileHelper, isKeystackUIAlive, getHttpIpAndPort, parseForDomain
from commonLib import logDebugMsg, isPipModuleExists, pipInstallModule, removePastFoldersBasedOnFolderTimestamp, syncTestResultsWithRedis

from keystackUtilities import execSubprocess2, mkdir2, readFile, writeToFile, writeToFileNoFileChecking, readYaml, writeToYamlFile, readJson, writeToJson, createNewFile, getDictItemFromList, sendEmail, getDictIndexList, getDictIndexFromList, convertStrToBoolean, convertNoneStringToNoneType
from keystackUtilities import execSubprocessInShellMode, execSubprocess, makeFolder, getTimestamp, updateLogFolder, getDate, chownChmodFolder, updateDict, getDockerNetworkServiceIpAddress

from KeystackUI.execRestApi import ExecRestApi
from KeystackUI.systemLogging import SystemLogsAssistant
from RunTaskAssistants.RunTask import RunTaskAssistant
from LoggingAssistants import TestSessionLoggerAssistant
from KeystackAssistants.TestReportAssistants import TestReportAssistant
from KeystackAssistants.ServiceAssistants import AwsAssistant
from KeystackAssistants.EmailAssistants import EmailAssistant
from KeystackAssistants.ValidatePlaybooks import ValidatePlaybookAssistant

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
            
            
@dataclasses.dataclass           
class Playbook:
    devMode:                       bool = Field(default=False)
    sessionId:                     Optional[str] = None
    # user: Passed in by KeystackUI. Internal use only.
    user:                          Optional[str] = None
    domain:                        Optional[str] = None
    # playbook: Samples/advance
    playbook:                      Optional[str] = None
    appArgs:                       Optional[str] = None
    abortTestOnFailure:            bool = Field(default=False)
    emailResults:                  bool = Field(default=False)
    debug:                         bool = Field(default=False)
    continuousIntegration:         bool = Field(default=False)
    timestampFolder:               Optional[str] = None
    pauseOnFailure:                bool = Field(default=False)
    holdEnvsIfFailed:              bool = Field(default=False)
    testConfigs:                   list = Field(default_factory=list)
    # if testConfigs != '', reconfigData = readYaml(testConfigs)
    reconfigData:                  dict = Field(default_factory=dict)
    includeLoopTestPassedResults:  bool = Field(default=False)
    isFromKeystackUI:              bool = Field(default=False)
    isKeystackAlive:               bool = Field(default=False)
    isKeystackUIExists:            bool = Field(default=False)
    trackResults:                  bool = Field(default=False)
    awsS3Upload:                   bool = Field(default=False)
    jira:                          bool = Field(default=False)
    currentVersion:                dict = Field(default_factory=lambda: readYaml(GlobalVars.versionFile)['keystackVersion'])
    exitTest:                      bool = Field(default=False)
    restApiMods:                   dict = Field(default_factory=dict)
    restApiModsFolder:             str = GlobalVars.restApiModsPath
    loginCredentialKey:            Optional[str] = None
    lock:                          Optional[object] = None
    mainLogFileLock:               Optional[object] = None
    playbookGlobalSettings:        dict = None    
    updateCsvDataFile:             bool = Field(default=False)
    envFileFullPath:               Optional[str] = None
    overallSummaryDataFile:        Optional[str] = None
    execRestApiObj:                Optional[object] = None
    status:                        str = Field(default='Started')
    startTime:                     Optional[object] = datetime.datetime.now()
    stopTime:                      Optional[str] = None
    duration:                      Optional[str] = None
    overallTestReportHeadings:     str = Field(default='')
    overallTestReport:             str = Field(default='')
    result:                        Optional[str] = None
    totalCases:                    int = Field(default=0)
    totalSkipped:                  int = Field(default=0)
    overallResultList:             list = Field(default_factory=list)
    exceptionErrors:               list = Field(default_factory=list)
    putFailureDetailsAfterResults: list = Field(default_factory=list)
    checkLoginCredentials:         bool = Field(default=False)
    cliUserLogin:                  Optional[str] = None
    cliUserPassword:               Optional[str] = None
    isUserApiKeyValid:             Optional[object] = None
    cliUserApiKey:                 Optional[str] = None
    cliSecuredMode:                bool = Field(default=False)
    redis:                         Optional[object] = None
    redisEnvMgmt:                  Optional[str] = None
    envMgmtObj:                    Optional[object] = None
    
    redisPipelineOverallSummaryKeyName: Optional[object] = None
    dbName:                             Optional[object] = None
                     
    def __post_init__(self):  
        try: 
            load_dotenv()
            self.devMode = convertStrToBoolean(os.getenv('DJANGO_DEBUG', False))

            if not self.sessionId:
                self.sessionId: str = str(random.sample(range(1,10000), 1)[0])
            
            self.isCliInsideContainer = isCliInsideContainer()
                
            # self.playbook = DOMAIN=Communal/Samples/advance
            # self.domain is defined here if user did not include DOMAIN in -playbook
            self.setPlaybookDomainAndGroup()
            
            # createTimestampFolder must be here at the top because if pipeline was executed by
            # KeystackUI, it loops for the overallSummary file. We don't want runPlaybook() to hold up the server.
            self.createTimestampFolder()
            self.initializeOverallSummaryData()

            # validatePlaybook will verify if envs are in different domains. 
            # If they are, check if the user running test is a member of the env domain.
            validatePlaybookObj = ValidatePlaybookAssistant(self)
            validatePlaybookObj.validatePlaybook()
            
            self.createSupportingFolders()
            # For test-session logs only.  Not for test-case logs: Example: Envs and port-groups auto-setup/teardowns
            self.keystackLogger = TestSessionLoggerAssistant(testSessionLogFile=self.testSessionLogFile)         
            self.verifyKeystackSystemSettingsFile()
            self.verifyIfKeystackUIIsAlive()
            self.getDomain()
            self.setUser()
            self.pipInstall()  

            if self.jira or self.awsS3Upload:
                self.checkLoginCredentials = True
 
            self.checkPointForPretestErrors()
            
            if self.isCliInsideContainer:
                self.connectToMongoDB()
            else:
                if self.devMode:
                    # Simulate dev testing inside KeystackUI container
                    self.connectToMongoDB()
                
            self.verifyUserCliApiKey() 
            self.connectToRedis()
            self.redisRemoveStaleTestcaseLogs()
            self.redisRemoveStaleEnvMgmt()
            self.testReportAssist = TestReportAssistant(self)
            self.awsAssist = AwsAssistant(self)
            self.emailAssist = EmailAssistant(self)
            self.readReconfigData()
                              
            # Dynamically reconfig playbooks via rest api:
            # getRestApiMods will update playbookTasks with rest api mods
            self.getRestApiMods()
            self.checkPointForPretestErrors()
            self.setPlaybookGlobalSettings()
            
            # All envs in the playbook needs to be in the same playbook domain
            # Cannot use envs in another domain
            self.runList = getRunList(self.domain, self.playbookTasks, user=self.user,
                                      userApiKey=self.cliUserApiKey, execRestApiObj=self.execRestApiObj, playbookObj=self)
           
            # This will verify if test includes -awsS3|-jira and if true, store login details in self.loginCredentials
            self.getLoginCredentials()
            self.checkPointForPretestErrors()
            
            if self.awsS3Upload:
                # For logging awsS3 messages
                self.awsS3ServiceObj = Serviceware.KeystackServices(typeOfService='keystackAwsS3',
                                                                    isFromKeystackUI=self.isFromKeystackUI)

            updateLogFolder(logFolderSearchPath=f'{GlobalVars.keystackServiceLogPath}/*',
                            removeAfterDays=keystackSettings.get('removeLogsAfterDays', 3))

            self.updateOverallSummaryData()
            self.makeKeystackFoldersPermissible()
            
            # self.testResultPlaybookPath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=<playbook>
            self.removePastFoldersBasedOnFolderTimestamp()
            
            if self.isCliInsideContainer:
                self.envMgmtObj = ManageEnv()
            else:
                # devMode is activated using Linux OS env DJANGO_DEBUG=True|False 
                if self.devMode:
                    if self.isKeystackAlive:
                        # Simulate dev testing inside KeystackUI container
                        self.envMgmtObj = ManageEnv()
                else:
                    try:
                        # In dev mode, mongoDB might not be present, and production mode
                        # needs the mongoDB container IP.  So if in dev mode and if there
                        # is no MongoDB present, this will pass the error and self.envMgmtObj is None.
                        from commonLib import getDockerInternalMongoDBIpAddress
                        keystackVersion = readYaml(GlobalVars.versionFile)['keystackVersion']
                        keystackVersion = keystackVersion.replace('.', '')
                        # keystacksetup_0200_keystack-net
                        dockerNetworkLS = f'keystacksetup_{keystackVersion}_.*'
                        mongoDockerInternalIp = getDockerInternalMongoDBIpAddress(searchPattern=dockerNetworkLS)
                        self.envMgmtObj = ManageEnv(mongoDBDockerInternalIp=mongoDockerInternalIp)
                    except:
                        pass
                       
            # stop printing to stdout
            # import io
            # text_trap = io.StringIO()
            # sys.stdout = text_trap
  
        except Exception as errMsg:
            # Playbook level exception
            self.abortTest(f'Playbook error: {str(errMsg)}', detailedLogs=traceback.format_exc(None, errMsg))

    def abortTest(self, errorMsg, detailedLogs=None):
        self.disconnectMongoDB()
        
        if self.overallSummaryDataFile:
            # Playbook might have syntax error. In this case, the 
            # overallSummaryDataFile has not been defined yet
            self.overallSummaryData.update({'testAborted': True, 'status': 'Aborted', 'result':'Aborted'})

            # This error message will be shown by pipelineView table data in the web UI 
            self.overallSummaryData['pretestErrors'].append(errorMsg)
            self.updateOverallSummaryFileAndRedis()
            self.closeRedisConnection()
            
        if detailedLogs:
            details = detailedLogs
        else:
            details = ''
        
        if self.isFromKeystackUI:
            SystemLogsAssistant().log(user=self.user,
                                      webPage='pipelines', 
                                      action='runPlaybook',
                                      msgType='Error',
                                      msg=f'sessionId: {self.sessionId} Errors:<br> {errorMsg}',
                                      forDetailLogs=details)
        try:
            self.keystackLogger.error(f'{errorMsg}\n{detailedLogs}')
        except:
            # The log object might not be created at the point of failure.
            pass 
        
        raise Exception(errorMsg)
    
    def connectToMongoDB(self):
        if self.isKeystackAlive:
            self.dbName  = db.ConnectMongoDB(ip=keystackSettings.get('mongoDbIp', 'localhost'),
                                             port=int(keystackSettings.get('dbIpPort', 27017)),
                                             dbName=db.DB.dbName)
            db.DB.name = self.dbName
    
    def disconnectMongoDB(self):
        if self.isKeystackAlive and self.dbName:
            self.dbName.mongoClient.close()

    def pipInstall(self):
        """ 
        User defined pip installs will be installed in docker container only.
        This will not install on native Linux host server
        """
        if self.isKeystackAlive:
            pipInstalls = keystackSettings.get('pipInstalls', None)
            if pipInstalls:
                for pipInstall in pipInstalls:
                    result = isPipModuleExists(pipInstall)
                    if result is False:
                        pipInstallModule(pipInstall)
                                            
    def makeKeystackFoldersPermissible(self):
        # Force all folders and files to be owned by group Keystack and permissions 770
        chownChmodFolder(GlobalVars.keystackTestRootPath, GlobalVars.user, GlobalVars.userGroup, stdout=False)
        if os.path.exists(f'{GlobalVars.appsFolder}/keystackEnv.py') is False:
            execSubprocessInShellMode(f'echo "keystackObj = None" > {GlobalVars.appsFolder}/keystackEnv.py', showStdout=False)
                    
        chownChmodFolder(GlobalVars.keystackSystemPath, GlobalVars.user, GlobalVars.userGroup, stdout=False)
                                    
    def connectToRedis(self):
        self.redisPipelineOverallSummaryKeyName = f'overallSummary-domain={self.domain}-{self.timestampFolderName}'
        
        if self.isKeystackAlive is False:
            return
   
        try:
            RedisMgr().connect(host='0.0.0.0', port=keystackSettings.get('redisPort', '6379'))
            if RedisMgr.redis:
                self.keystackLogger.info('Redis is alive')
            else:
                self.keystackLogger.warning('Redis is not alive')
                
        except Exception as errMsg:
            self.keystackLogger.error(f'keystack.py: connectToRedis error: {errMsg}')
        
    def closeRedisConnection(self):
        if self.isKeystackAlive and RedisMgr.redis:
            RedisMgr.redis.redisObj.close()
            
    def updateOverallSummaryDataOnRedis(self, threadLock=None):
        """ 
        overallSummary-domain={self.domain}-{self.timestampFolderName}
        """
        if self.isKeystackAlive and RedisMgr.redis:
            RedisMgr.redis.write(keyName=self.redisPipelineOverallSummaryKeyName,
                                 data=self.overallSummaryData)
        else:
            writeToJson(self.overallSummaryDataFile, data=self.overallSummaryData, mode='w', threadLock=threadLock)

        # If users using local host CLI (not container), the overallSummaryData needs to be transferred to redis in Docker
        if self.isFromKeystackUI is False and self.isKeystackAlive:
            params = {'keyName': self.redisPipelineOverallSummaryKeyName, 'data': self.overallSummaryData, 'webhook': True}
            self.execRestApiObj.post(restApi='/api/v1/redis/updateOverallSummaryData', params=params, showApiOnly=True)
             
    def updateOverallSummaryFileAndRedis(self, threadLock=None):
        """ 
        overallSummary-domain={self.domain}-{self.timestampFolderName}
        """  
         
        writeToJson(self.overallSummaryDataFile, data=self.overallSummaryData, mode='w', threadLock=threadLock)
        if RedisMgr.redis:
            RedisMgr.redis.write(keyName=self.redisPipelineOverallSummaryKeyName,
                                 data=self.overallSummaryData)
            return
    
        # If users using the CLI, the overallSummaryData needs to be transferred to redis in Docker
        if self.isFromKeystackUI is False and self.isKeystackAlive:
            # restapi to call the webUI to write to redis
            params = {'keyName': self.redisPipelineOverallSummaryKeyName, 'data': self.overallSummaryData, 'webhook': True}
            self.execRestApiObj.post(restApi='/api/v1/redis/updateOverallSummaryData', params=params, showApiOnly=True)

    def updateOverallSummaryDataFile(self, threadLock=None):
        writeToJson(self.overallSummaryDataFile, data=self.overallSummaryData, mode='w', threadLock=threadLock)
                    
    def writeToRedisEnvMgmt(self, keyName, data):
        if RedisMgr.redis:
            # Keystack local host may not be running Redis
            RedisMgr.redis.write(keyName=keyName, data=data)
            return

        # If users using the CLI, the redis envMgmt data needs to be transferred to redis in Docker
        if self.isFromKeystackUI is False and self.isKeystackAlive:
            # restapi to call the webUI to write to redis
            params = {'keyName': keyName, 'data': data, 'webhook': True}
            self.execRestApiObj.post(restApi='/api/v1/redis/updateEnvMgmt', params=params, showApiOnly=True)

    def readRedisEnvMgmt(self, keyName):
        if RedisMgr.redis:
            return RedisMgr.redis.getCachedKeyData(keyName=keyName)

        # If users using the CLI, the redis envMgmt data needs to be transferred to redis in Docker
        if self.isFromKeystackUI is False and self.isKeystackAlive:
            # restapi to call the webUI to write to redis
            params = {'keyName': keyName, 'webhook': True}
            response = self.execRestApiObj.post(restApi='/api/v1/redis/readEnvMgmt', params=params, showApiOnly=True)
            if response.status_code == 200:
                return response.json()['data']
            
            return {}

    def writeToRedisTaskSummaryData(self, keyName, data):
        if RedisMgr.redis:
            RedisMgr.redis.write(keyName=keyName, data=data)
            return

        # If users using the CLI, the redis task-summary-data needs to be transferred to redis in Docker
        if self.isFromKeystackUI is False and self.isKeystackAlive:
            # restapi to call the webUI to write to redis
            params = {'keyName': keyName, 'data': data, 'webhook': True}
            self.execRestApiObj.post(restApi='/api/v1/redis/updateTaskSummaryData', params=params, showApiOnly=True)

    def readRedisTaskSummaryData(self, keyName):
        if RedisMgr.redis:
            return RedisMgr.redis.getCachedKeyData(keyName=keyName)

        # If users using the CLI, the redis task-summary-data needs to be transferred to redis in Docker
        if self.isFromKeystackUI is False and self.isKeystackAlive:
            # restapi to call the webUI to write to redis
            params = {'keyName': keyName, 'webhook': True}
            response = self.execRestApiObj.post(restApi='/api/v1/redis/readTaskSummaryData', params=params, showApiOnly=True)
            if response.status_code == 200:
                return response.json()['data']
            
            return {}
                    
    def redisRemoveStaleTestcaseLogs(self):
        """ 
        For Keystack framework self clean up
        """
        if RedisMgr.redis:
            testcaseLogs = RedisMgr.redis.getAllPatternMatchingKeys(pattern='testcase*')
            if len(testcaseLogs) > 0:
                for testcaseLog in testcaseLogs:
                    # testcase-10-25-2024-09:11:20:213023_9168-STAGE=Test_TASK=layer3_ENV=DOMAIN=Communal-Samples-demoEnv1_TESTCASE=bgp_1x_1x
                    regexMatch = re.search('testcase-(.*)-STAGE.*', testcaseLog)
                    if regexMatch:
                        timestamp = regexMatch.group(1)
                        # Verify if the overallSummary pipeline timestamp still exists or not. 
                        # If not, the pipeline has been deleted.  Remove the stale testcase logs.
                        overallSummary = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'overallSummary*{timestamp}')
                        if len(overallSummary) == 0:
                            RedisMgr.redis.deleteKey(testcaseLog)

    def redisRemoveStaleEnvMgmt(self):
        """ 
        For Keystack framework self clean up
        """
        if RedisMgr.redis:
            envMgmts = RedisMgr.redis.getAllPatternMatchingKeys(pattern='envMgmt*')
            if len(envMgmts) > 0:
                for envMgmt in envMgmts:
                    # envMgmt-10-25-2024-09:40:12:083471_3172-STAGE=Test_TASK=layer3_ENV=DOMAIN=Communal-Samples-demoEnv1
                    regexMatch = re.search('envMgmt-(.*)-STAGE.*', envMgmt)
                    if regexMatch:
                        timestamp = regexMatch.group(1)
                        # Verify if the overallSummary pipeline timestamp still exists or not. 
                        # If not, the pipeline has been deleted.  Remove the stale envMgmt data.
                        overallSummary = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'overallSummary*{timestamp}')
                        if len(overallSummary) == 0:
                            RedisMgr.redis.deleteKey(envMgmt)
                                                                                    
    def setUser(self):
        if not self.user:
            # Docker container USER does not exists
            self.user = os.environ.get("USER", None)
            if self.user is	None:
                self.user = execSubprocessInShellMode("whoami", showStdout=False)[1].replace('\n', '')
                
            self.user = f'CLI: {self.user}'
            self.overallSummaryData.update({'user': self.user})  
                
    def setPlaybookGlobalSettings(self):
        # Set default settings: These parameters are all known options for playbooks.
        # Some of these settings could be overwritten in the stage and task properties
        self.playbookGlobalSettings = {'loginCredentialKey': None,
                                       'showResultDataLastDays': 10,
                                       'trackResults': False,
                                       'abortTaskOnFailure': False,
                                       'abortTestOnFailure': False,
                                       'abortStageOnFailure': True,
                                       'reportHeadingAdditions': None,
                                       'verifyFailurePatterns': [],
                                       'env': None,
                                       'loadBalanceGroup': None,
                                       'app': None
                                       }
        # Overwrite defaults . playbookTasks was created in ValidatePlaybook()  
        if self.playbookTasks is not None:
            if 'globalSettings' in self.playbookTasks.keys():
                self.playbookGlobalSettings.update(self.playbookTasks['globalSettings'])

        self.trackResults         = self.playbookGlobalSettings.get('trackResults', False)
        self.abortStageOnFailure  = self.playbookGlobalSettings.get('abortStageOnFailure', True)
        self.abortTaskOnFailure   = self.playbookGlobalSettings.get('abortTaskOnFailure', False)

        # Abort test if a testcase failed. Will not jump to Teardown
        # If this is set True, RunTask will set playbookObj.exitTest to True
        if self.playbookGlobalSettings.get('abortTestOnFailure', False) is False and self.abortTestOnFailure:
            self.abortTestOnFailure = True
        elif self.playbookGlobalSettings.get('abortTestOnFailure', False) is True and self.abortTestOnFailure is False:
            self.abortTestOnFailure = True
        else:
            self.abortTestOnFailure = False
                                    
    def writeToSessionLogs(self, msg):
        """
        Use this for logging debugs combined with rest api calls
        """
        timestamp = getTimestamp()
        logMsg = f'{timestamp}: {msg}'
        writeToFile(self.sessionLogs, msg=logMsg, mode='a+')
        
    def setPlaybookDomainAndGroup(self):
        # self.playbook: Samples/advance
        # DOMAIN=Communal/Samples/advance -> Samples-advance
        if bool(re.search('.*DOMAIN|domain.*', self.playbook)):
            regexMatch = re.search('.*(DOMAIN=.*?/)(.*)(\.yml)?', self.playbook)
            if regexMatch:
                playbookDomain = regexMatch.group(1).split('=')[-1].replace('/', '')
                self.playbookGroup = regexMatch.group(2).replace('.yml', '')
                self.domain = playbookDomain
        else:
            self.playbookGroup  = self.playbook.replace('/', '-')
            regexMatch = re.search('(.*)(\.yml)?', self.playbook)
            if regexMatch:
                playbookDomain = self.domain
                self.playbookGroup = regexMatch.group(1)
                
        self.playbook = f'DOMAIN={playbookDomain}/{self.playbookGroup}'
            
    def checkPointForPretestErrors(self):
        if len(self.overallSummaryData['pretestErrors']) > 0:
            errors = ''
            for line in self.overallSummaryData["pretestErrors"]:
                errors += f'- {line}\n'
                self.keystackLogger.error(line)                 

            raise Exception(f'Keystack pretest-errors:\n{errors}')        
           
    def verifyIfKeystackUIIsAlive(self):
        """
        ALL PRE-TEST VALIDATION MUST BE DONE WITH BELOW METHOD. 
           pipelineView.py getTableData looks for overallSummaryData['status'] = Aborted
            and shows the self.overallSummaryData['exceptionErrors']
              
        For env mgmt. Check if the webUI server is alive.
        If not, env mgmt including env load balancing won't work because they require the MongoDB.
        Only static env is supported
        
        keystackHttpIpAddress, keystackIpPort came from: verifyKeystackSystemSettingsFile()
        """   
        # isKeystackUIAlive returns passed|failed, http|https     
        self.isKeystackUIExists = isKeystackUIAlive(ip=self.keystackHttpIpAddress,
                                                    port=self.keystackIpPort,
                                                    timeout=3,
                                                    keystackLogger=self.keystackLogger
                                                    )
        if self.isKeystackUIExists[0] is False:
            if self.holdEnvsIfFailed:
                raise Exception('Error: Including the param -holdEnvsIfFailed to manage Envs will not work unless the KeystackUI docker container is running.') 
        else:
            self.isKeystackAlive = True
            self.execRestApiObj = self.isKeystackUIExists[1]

    def getDomain(self):
        """ 
        self.playbook: Gets converted to full path: 
             /opt/KeystackTests/Playbooks/DOMAIN=Communal/Samples/advance.yml 
        """
        self.domain = parseForDomain(self.playbook)
                                
    def verifyUserCliApiKey(self): 
        """ 
        If user is running test from the CLI in secured mode, verifythe user's API-Key.
        """
        self.cliSecuredMode = convertStrToBoolean(keystackSettings.get('cliSecuredMode', True))
        self.keystackLogger.debug(f'runPlaybook:getDomain:verifyUserCliApiKey: isFromKeystackUI:{self.isFromKeystackUI} isCliInsideContainer:{self.isCliInsideContainer} cliSecuredMode:{self.cliSecuredMode} cliUserApiKey:{self.cliUserApiKey}')
        
        if self.cliSecuredMode is False and self.cliUserApiKey is None:    
            return
        
        if self.cliSecuredMode is False and self.cliUserApiKey:
            return
        
        if self.isFromKeystackUI:
            return

        # CLI is inside of the container                                                                             
        if self.isCliInsideContainer and self.cliSecuredMode and self.cliUserApiKey is None:
            raise Exception(f'Inside container CLI: cliSecuredMode=True, but user did not include the api-key\n')

         # CLI is outside of the container                                                                            
        if self.isCliInsideContainer is False and self.cliSecuredMode and self.cliUserApiKey is None:
            raise Exception(f'Outside container CLI: cliSecuredMode={self.cliSecuredMode}, but user did not include the api-key\n')
        
        accountMgr = AccountMgr()
        self.isUserApiKeyValid = accountMgr.isApiKeyValid(apiKey=self.cliUserApiKey)
        if self.isUserApiKeyValid is None:
            raise Exception(f'\ncliSecuredMode={self.cliSecuredMode}. User API-Key is invalid\n')
                                      
    def createTimestampFolder(self):
        if not self.timestampFolder:
            # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples/advance/05-03-2024-17:11:59:091890_8716
            self.timestampFolder = createTestResultTimestampFolder(self.domain,
                                                                   self.playbookGroup,
                                                                   self.sessionId,
                                                                   self.debug)
            
        self.timestampFolderName = self.timestampFolder.split('/')[-1]
        self.overallSummaryDataFile = f'{self.timestampFolder}/overallSummary.json'
  
    def initializeOverallSummaryData(self):
        # Initilize the overSummaryData with pretestError so all verifications
        # could append pretest errors for the Keystack UI to show the pretest problems.

        self.overallSummaryData = {'sessionId': self.sessionId, 
                                   'user': self.user, 
                                   'topLevelResultFolder': self.timestampFolder,
                                   'playbook': self.playbook, 
                                   'status': 'Running',
                                   'testParameters': None, 
                                   'pretestErrors': [],
                                   'started': self.startTime.strftime('%m-%d-%Y %H:%M:%S'),
                                   'stopped': '',
                                   'testDuration': '',
                                   'totalFailures': 0,
                                   'totalPassed': 0,
                                   'totalFailed': 0,
                                   'totalSkipped': 0,
                                   'totalTestAborted': 0,
                                   'totalKpiPassed': 0,
                                   'totalKpiFailed': 0,
                                   'pausedOnFailure': None,
                                   'pausedOnFailureCounter': 0,
                                   'isFromKeystackUI': self.isFromKeystackUI,
                                   'notes': [],
                                   'warnings': [],
                                   'exceptionErrors': [],
                                   'testAborted': False,
                                   'stageFailAborted': False,
                                   'result': None,
                                   'domain': self.domain,
                                   'processId': os.getpid(),
                                   'stages': {}
                                  }
        self.updateOverallSummaryDataOnRedis()
        chownChmodFolder(self.timestampFolder, user=GlobalVars.user, userGroup=GlobalVars.userGroup) 

    def updateOverallSummaryData(self):
        self.overallSummaryData.update({'totalCases': self.totalCases,
                                        'keystackVersion': self.currentVersion,
                                        'playbook': self.playbook,
                                        'loginCredentialKey': self.loginCredentialKey,
                                        'trackResults': self.trackResults,
                                        'abortTestOnFailure': self.abortTestOnFailure,
                                        'holdEnvsIfFailed': self.holdEnvsIfFailed,
                                        'includeLoopTestPassedResults': self.includeLoopTestPassedResults,
                                        'runList': self.runList
                                    })
        self.overallSummaryDataFile = f'{self.timestampFolder}/overallSummary.json'
        self.updateOverallSummaryFileAndRedis()
        
    def createSupportingFolders(self):
        # Create supporting folders for test and internal usage.
        self.sessionDataFolder = f'{self.timestampFolder}/.Data'
        mkdir2(self.sessionDataFolder, stdout=False)
        chownChmodFolder(self.sessionDataFolder, GlobalVars.user, GlobalVars.userGroup, stdout=False)
        
        # /.Data/EnvMgmt: Each test session keeps track of all the envs being used.
        # EnvMgmt uses it for removeActiveUsersList and remove waitingList
        self.envMgmtDataFolder = f'{self.sessionDataFolder}/EnvMgmt'
        mkdir2(self.envMgmtDataFolder, stdout=False)
        
        # /path/<timestampFolder>/.Data/ResultsMeta/opt/KeystackTests/Modules/Demo/Samples/Testcases/<testcase>.yml_1_1
        self.resultsMetaFolder = f'{self.sessionDataFolder}/ResultsMeta'
        mkdir2(self.resultsMetaFolder, stdout=False)
        
        self.artifactsFolder = f'{self.timestampFolder}/Artifacts'
        mkdir2(self.artifactsFolder, stdout=False)
        # Session's REST API command calls
        self.sessionLogs = f'{self.timestampFolder}/{GlobalVars.sessionLogFilename}'
        self.testSessionLogFile = f'{self.timestampFolder}/testSession.log'
        writeToFile(self.sessionLogs, msg='', mode='w')
   
    def verifyKeystackSystemSettingsFile(self):
        self.keystackSystemSettingsFileNotFound = False 
        if os.path.exists(GlobalVars.keystackSystemSettingsFile):
            self.keystackHttpIpAddress, self.keystackIpPort = getHttpIpAndPort()
        else:
            self.keystackSystemSettingsFileNotFound = True
            errorMsg = f'Could not located keystack system file: {GlobalVars.keystackSystemSettingsFile}'
            self.overallSummaryData['pretestErrors'].append(errorMsg)

    def removePastFoldersBasedOnFolderTimestamp(self): 
        """
        Remove pipeline results that are not in the 'Runnning' status if left for over removeDaysOlderThan

        Examples:
        0 = Deleting starting with today
        1 = Keep today's results. Delete yesterday and beyond.

        Example:
            timestamp folder = /path/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/06-23-2022-12:06:22:953462_<sessionId>
        """
        if keystackSettings.get('removeResultsFolder', GlobalVars.removeResultFoldersAfterDays) == 'never':
            return

        folder = f'{GlobalVars.resultsFolder}/DOMAIN={self.domain}/PLAYBOOK/{self.playbook}'
        removeDaysOlderThan = keystackSettings.get('removeResultsFolder', GlobalVars.removeResultFoldersAfterDays)            
        today = datetime.datetime.now()

        # /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=Samples-pythonSample
        for root in glob(f'{folder}/*'):
            # /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample/06-23-2022-12:06:22:953462_pauseOnError3
            timestampFolderDate = '-'.join(root.split('/')[-1].split('_')[0].split('-')[:-1])
            format = '%m-%d-%Y'
            datetimeObj = datetime.datetime.strptime(timestampFolderDate, format)
            daysDelta = today.date() - datetimeObj.date()
            daysRecorded = daysDelta.days

            if int(daysRecorded) >= int(removeDaysOlderThan):
                try:
                    if os.path.exists(f'{root}/overallSummary.json'):
                        overallSummary = readJson(f'{root}/overallSummary.json')
                        timestampFolderName = overallSummary['topLevelResultFolder'].split('/')[-1]
                                           
                        # Pipeline is still actively Running
                        pid = overallSummary['processId']
                        isPidExists = execSubprocessInShellMode(f'pgrep {pid}', showStdout=True)[1]
                        if len(isPidExists) > 0 or overallSummary['status'] == 'Running':
                            continue
                                                        
                        print('removePastFoldersBasedOnFolderTimestamp:', root)
                        if os.path.isfile(root):
                            os.remove(root)
                            
                            if RedisMgr.redis:
                                redisOverallSummaryKeyName = f'overallSummary-domain={overallSummary["domain"]}-{timestampFolderName}'
                                RedisMgr.redis.deleteKey(keyName=redisOverallSummaryKeyName)
                            
                        if os.path.isdir(root):
                            rmtree(root)
                    else:
                        syncRedis = False
                        # No overallSummary file and it's past results.  Remove it.
                        if os.path.isfile(root):
                            os.remove(root)
                            syncRedis = True
                            
                        if os.path.isdir(root):
                            rmtree(root)
                            syncRedis = True
                            
                        if syncRedis:
                            syncTestResultsWithRedis()
                                       
                except Exception as errMsg:
                    #print(f'removePastFoldersBasedOnFolderTimestamp error: {root}\n{errMsg}')
                    pass
                                                       
    def executeStages(self):
        try:
            def runTasksHelper(stage):
                """ 
                Run the tasks in the current stage
                """
                # METADATA
                self.overallSummaryData['stages'].update({stage: {'result': None, 'tasks': []}})
                self.updateOverallSummaryDataOnRedis()
                self.runTasks(stage=stage)
                           
            runSetup = False
            runCustomStages = True
            self.abortedStages = []
            self.skippedStages = []
            anyStageFailed = False
            self.stageSetup = None
            self.stageTeardown = None
         
            if 'stages' in self.playbookTasks.keys():
                for key in self.playbookTasks['stages'].keys():
                    if bool(re.search('^Setup$', key)):
                        self.stageSetup = 'Setup'
                    if bool(re.search('^setup$', key)):
                        self.stageSetup = 'setup'
                    if bool(re.search('^Teardown$', key)):
                        self.stageTeardown = 'Teardown'
                    if bool(re.search('^teardown$', key)):
                        self.stageTeardown = 'teardown'
                                               
            for key in self.playbookTasks.keys():         
                if key == 'stages':
                    stageFailed = False
                    
                    if self.stageSetup:                            
                        if self.playbookTasks['stages'][self.stageSetup].get('enable', True) in [True, 'True', 'true', 'yes', 'Yes']:
                            self.keystackLogger.info(f'Stage: {self.stageSetup} is enabled.  Calling runTask')
                            runTasksHelper(self.stageSetup)
                            runSetup = True
                        else:
                            self.keystackLogger.debug(f'Stage {self.stageSetup} is disabled')
                                                                    
                    if runSetup:
                        # METADATA: Check setupup result
                        if self.overallSummaryData['stages'][self.stageSetup]['result'] == 'Failed':
                            self.keystackLogger.info('Setup stage failed')
                            runCustomStages = False
                            stageFailed = True
                        
                    if stageFailed is False and runCustomStages:
                        runStageList = []   
                        
                        for stageName in list(self.playbookTasks['stages'].keys()):
                            if self.playbookTasks['stages'][stageName].get('enable', True) in [True, 'True', 'true', 'yes', 'Yes']:
                                if stageName not in [self.stageSetup, self.stageTeardown]:
                                    self.keystackLogger.debug(f'Playbook Stage: {stageName} is enabled')
                                    # Abort immediately after a testcase failure. 
                                    # abortTestOnFailure=True RunTask.run() will set exitTest=True if test failed
                                    
                                    if self.exitTest:
                                        self.keystackLogger.debug(f'abortTestOnFailure=True : Playbook Stage failed: {stageName} : Exiting')
                                        stageFailed = True
                                        anyStageFailed = True
                                        self.abortedStages.append(stageName)
                                        self.skippedStages.append(stageName)
                                        continue

                                    # abortStageOnFailure default = True                                   
                                    if stageFailed and self.abortStageOnFailure:
                                        # run the rest of the task within the stage.
                                        # Then jump to teardown stage
                                        self.keystackLogger.debug(f'Skipping stage: {stageName} : abortStageOnFailure=True (default)')
                                        self.skippedStages.append(stageName)
                                        continue
                                    
                                    runStageList.append(stageName)
                                    runTasksHelper(stageName)
                                    stageResult = self.overallSummaryData['stages'][stageName]['result']
                                    
                                    # CI/CT/CD normally aborts when the stage fails    
                                    if stageFailed is False and stageResult in ['Failed', 'Aborted']:
                                        stageFailed = True
                                        anyStageFailed = True
                                        
                                        if self.abortStageOnFailure:
                                            self.keystackLogger.debug(f'Stage failed:{stageName}. Aborting stage')
                                            self.abortedStages.append(stageName)
                                            
                                    # Must have a small delay in case back-to-back stages task use the same env.
                                    # Give it time to sessionMgmt to get up-to-date EnvMgmt data.
                                    time.sleep(.5)
                            else:
                                self.keystackLogger.debug(f'Stage {stageName} is included in plabook, but disabled')
                                continue
                                                        
                    if self.stageTeardown:
                        if self.playbookTasks['stages'][self.stageTeardown].get('enable', True) in  [True, 'True', 'true', 'yes', 'Yes']:
                            tearDownOnFailure = self.playbookTasks['stages'][self.stageTeardown].get('teardownOnFailure', True)
                            self.keystackLogger.debug(f'Teardown stage is enabled')
                            
                            # self.exitTest: Abort immediately after a testcase failure. 
                            #                abortTestOnFailure=True RunTask.run() will set exitTest=True if test failed
                            if self.exitTest and tearDownOnFailure in [False, 'False', 'false', 'No', 'no']:
                                self.skippedStages.append(self.stageTeardown)
                                self.keystackLogger.debug(f'Teardown stage is exiting: teardownOnFailure={tearDownOnFailure}. abortTestOnFailure=True.')
                                continue
                            
                            if tearDownOnFailure in [True, 'True', 'true', 'Yes', 'yes']:
                                runTasksHelper(self.stageTeardown)
                                
                            elif tearDownOnFailure in [False, 'False', 'false', 'No', 'no']:
                                self.keystackLogger.debug(f'Teardown stage: tearDownOnFailure=False. Slipping Teardown stage.')
                                self.skippedStages.append(self.stageTeardown)
                                continue
                        else:
                            self.keystackLogger.debug('Teardown stage included in the playbook, but disabled')
                    else:
                        self.keystackLogger.debug('Teardown stage is not included')
                                                
            # --- At this point, all stages are done ---
            # Handle all post test procedures starting here
            self.postTest()
            
            # Incomplete | Passed | Failed
            return self.overallSummaryData['result']
                                             
        except Exception as errMsg:
            msg = f'Playbook executeStages exception: {traceback.format_exc(None, errMsg)}'
            stopTime = datetime.datetime.now()
            stopTime.strftime('%m-%d-%Y %H:%M:%S')
            self.overallSummaryData.update({'stopped': str(stopTime), 'status': 'Aborted'})
            self.updateOverallSummaryDataOnRedis()
            self.abortTest(errorMsg=msg) 
        finally:
            self.closeRedisConnection() 

    def postTest(self):
        if self.overallSummaryData['stageFailAborted'] == True:
            self.overallSummaryData['status'] = 'StageFailAborted'
        else:
 
            if self.overallSummaryData['totalTestAborted'] == 0 and self.overallSummaryData['totalSkipped'] == 0:
                self.overallSummaryData['status'] = 'Completed'
            else:
                self.overallSummaryData['status'] = 'Incomplete'
                    
        self.updateOverallSummaryDataOnRedis()
     
        try:
            chownChmodFolder(self.timestampFolder, self.user, GlobalVars.userGroup, stdout=False)
        except:
            pass

        if self.awsS3Upload:                                               
            self.s3ManifestFile = generateManifestFile(self.timestampFolder,
                                                        self.awsS3BucketName,
                                                        self.awsRegion)

            informAwsS3ServiceForUploads(playbookName=self.playbookAndNamespace,
                                            sessionId=self.sessionId,
                                            resultsTimestampFolder=self.timestampFolder,
                                            listOfFilesToUpload=[f'{self.timestampFolder}/MANIFEST.mf'],
                                            loginCredentialPath=self.credentialYmlFile,
                                            loginCredentialKey=self.loginCredentialKey)

        # Enable printing to stdout
        #sys.stdout = sys.__stdout__
        
        self.testReportAssist.createTestReport()
        chownChmodFolder(topLevelFolder=self.timestampFolder, user=self.user, userGroup=GlobalVars.userGroup)
        self.testReportAssist.recordResults()
        self.ciTestResultPath()
        
        if self.awsS3Upload:
            informAwsS3ServiceForUploads(playbookName=self.playbookAndNamespace,
                                         sessionId=self.sessionId, 
                                         resultsTimestampFolder=self.timestampFolder,
                                         listOfFilesToUpload=[f'{self.timestampFolder}/testReport'],
                                         loginCredentialPath=self.credentialYmlFile,
                                         loginCredentialKey=self.loginCredentialKey)
            
        self.emailAssist.emailReport()

        # This must be the last step
        if self.awsS3Upload and self.isFromKeystackUI:
            # For Docker, must wait for S3 to finish uploading.
            # Otherwise, the test exits too fast when done testing during S3 uploading .
            time.sleep(2)
            self.awsAssist.waitForS3UploadToComplete()
        
        self.disconnectMongoDB()        
    
    def runTasks(self, stage):
        """ 
        This function runs Setup task first.
        If Setup fails, the rest of the task will be skipped.
        Teardown task will be called if user included it in the playbook.
        """
        self.taskSetup = None
        self.taskTeardown = None
        
        for taskList in self.playbookTasks['stages'][stage]['tasks']:
            for task in taskList.keys():
                if bool(re.search('^Setup$', task)):
                    self.taskSetup = 'Setup'
                if bool(re.search('^setup$', task)):
                    self.taskSetup = 'setup'
                if bool(re.search('^Teardown$', task)):
                    self.taskTeardown = 'Teardown'
                if bool(re.search('^teardown$', task)):
                    self.taskTeardown = 'teardown'
        
        runTaskSetupList = []
        runTaskTeardownList = []
        runTaskList = []
        
        if self.taskSetup:
            for task in self.playbookTasks['stages'][stage]['tasks']:
                for taskName, taskProperties in task.items():
                    if taskName == self.taskSetup:
                        runTaskSetupList.append(task)
                        
        for task in self.playbookTasks['stages'][stage]['tasks']:
            for taskName, taskProperties in task.items():
                if taskName not in [self.taskSetup, self.taskTeardown]:
                    runTaskList.append(task)                            
                        
        if self.taskTeardown:
            for task in self.playbookTasks['stages'][stage]['tasks']:
                for taskName, taskProperties in task.items():
                    if taskName == self.taskTeardown:
                        runTaskTeardownList.append(task)
        
        taskSetupPassed = True
        if len(runTaskSetupList) > 0:
            self.runStageTasks(stage, runTaskSetupList) 
            
            regularTaskList = self.overallSummaryData['stages'][stage]['tasks']
            
            for task in regularTaskList:
                for taskName, taskProperties in task.items():
                    if taskName == self.taskSetup:
                        if taskProperties['result'] != 'Passed':
                           taskSetupPassed = False
                      
        if taskSetupPassed:                   
            self.runStageTasks(stage, runTaskList)
          
        self.runStageTasks(stage, runTaskTeardownList)
                                                         
    def runStageTasks(self, stage, runTaskOrderList):      
        try:
            if self.playbookTasks['stages'][stage].get('enable', True) in ['False', 'false', False, 'no', 'No']:
                return
            
            threadList = []
            envFile = None
            env = None 
            loadBalanceGroup = None
            doOnceFlagForParallelLocks = True
            self.envFileFullPath = None
            runTasksConcurrently = self.playbookTasks['stages'][stage].get('runTasksConcurrently', False)
            stageProperties = {'stage': {stage: {}}}
            globalEnv = None
            globalLoadBalanceGroup = None
            globalVerifyFailurePatterns = []
            globalPlaybookVars = None
                         
            # First, set environment parameters from globalSettings.
            # Then overwrite them in the stage level and then the task level
            if 'globalSettings' in self.playbookTasks:
                stageProperties['stage'][stage].update(self.playbookTasks['globalSettings'])
                globalEnv = self.playbookTasks['globalSettings'].get('env', None)
                globalEnv = envFileHelper(self.domain, globalEnv)
                globalLoadBalanceGroup = self.playbookTasks['globalSettings'].get('loadBalanceGroup', None)
                globalVerifyFailurePatterns = self.playbookTasks['globalSettings'].get('verifyFailurePatterns', [])
                globalPlaybookVars = self.playbookTasks['globalSettings'].get('playbookVars', {})
                
            # abortTaskOnfailure is only for runTasksConcurrently=False
            globalAbortTaskOnFailure = self.playbookGlobalSettings.get('abortTaskOnFailure', False)
                
            if self.playbookTasks['stages'][stage].get('env', None) not in ['None', 'none', None]:
                stageEnv = self.playbookTasks['stages'][stage]['env']
                stageEnv = envFileHelper(stageEnv)
            else:
                stageEnv = None

            if self.playbookTasks['stages'][stage].get('loadBalanceGroup', None) not in ['None', 'none', None]:
                stageLoadBalanceGroup = self.playbookTasks['stages'][stage]['loadBalanceGroup']
            else:
                stageLoadBalanceGroup= None
                            
            stageVerifyFailurePatterns = self.playbookTasks['stages'][stage].get('verifyFailurePatterns', [])
            stagePlaybookVars = self.playbookTasks['stages'][stage].get('playbookVars', {})
            didTaskFail = False
                                                                  
            for task in runTaskOrderList:
                self.taskSSummaryData = {}
                stageAbortTaskOnFailure = self.playbookTasks['stages'][stage].get('abortTaskOnFailure', False)
                
                if globalAbortTaskOnFailure is False and stageAbortTaskOnFailure is False: 
                    abortTaskOnFailure = False
                    
                elif globalAbortTaskOnFailure is True and stageAbortTaskOnFailure is False:
                    # stage settings supercedes globalSettings
                    abortTaskOnFailure = False
                    
                elif globalAbortTaskOnFailure is False and stageAbortTaskOnFailure is True:
                    abortTaskOnFailure = True
                         
                for taskName, taskProperties in task.items():
                    if self.exitTest:
                        break
                        
                    if taskProperties.get('enable', True) in [False, 'False', 'false', 'No', 'no']:
                        self.keystackLogger.debug(f'Stage:{stage}  Task:{taskName} is disabled in playbook')
                        continue
                    
                    if taskProperties.get('teardownOnFailure', True) == False:
                        self.keystackLogger.debug(f'Running stage:{stage}  task={taskName} teardownOnFailure=False')
                        continue
                     
                    self.keystackLogger.debug(f'Running stage:{stage}  task={taskName}')
                                
                    if 'abortTaskOnFailure' in taskProperties:
                        # task properties supercedes globalSettings and stage settings
                        abortTaskOnFailure = taskProperties['abortTaskOnFailure']

                    if taskProperties.get('env', None):
                        env = taskProperties['env']
                        env = envFileHelper(self.domain, env, bypassEnvDomainChecking=True)
                    elif stageEnv:
                        env = stageEnv
                    elif globalEnv:
                        env = globalEnv
                    else:
                        env = None

                    if taskProperties.get('loadBalanceGroup', None):
                        loadBalanceGroup = taskProperties['loadBalanceGroup']
                    elif stageLoadBalanceGroup:
                        loadBalanceGroup = stageLoadBalanceGroup
                    elif globalLoadBalanceGroup:
                        loadBalanceGroup = globalLoadBalanceGroup
                    else:
                        loadBalanceGroup = None
                    
                    if loadBalanceGroup in ['None', 'none', None]:
                        loadBalanceGroup = None
                    
                    # Static env has precedence over loadBalance group
                    if env and loadBalanceGroup:
                        loadBalanceGroup = None
                                                
                    if taskProperties.get('verifyFailurePatterns', []):
                        verifyFailurePatterns = taskProperties['verifyFailurePatterns'] 
                    elif stageVerifyFailurePatterns:
                        verifyFailurePatterns = stageVerifyFailurePatterns
                    elif globalVerifyFailurePatterns:
                        verifyFailurePatterns = globalVerifyFailurePatterns
                    else:
                        verifyFailurePatterns = []

                    if taskProperties.get('playbookVars', []):
                        playbookVars = taskProperties['playbookVars'] 
                    elif stagePlaybookVars:
                        playbookVars = stagePlaybookVars
                    elif globalPlaybookVars:
                        playbookVars = globalPlaybookVars
                    else:
                        playbookVars = {}
                    
                    # Use not-required because the env could be a globalSetting.                       
                    if env and env != 'not-required':
                        # Create an env mgmt file for each pipeline session to track all the
                        # envs used. This file is used in EnvMgmt to figure out which sessionID
                        # has priority to use the env next in line:  /timestampFolder/.Data/EnvMgmt
                        # env: /opt/KeystackTests/Envs/DOMAINS=Communal/Samples/qa.yml
                        self.envFileFullPath = env
                        # Get the env name with the namespace
                        regexMatch = re.search(f'.+/Envs/(.+)\.(yml|yaml)?', env)
                        if regexMatch:
                            env = regexMatch.group(1)

                        envNameForResultPath = env.replace('/', '-')

                        if self.isCliInsideContainer:
                            self.envMgmtObj._setenv = env
                            isEnvParallelUsed = self.envMgmtObj.isEnvParallelUsage()
                        else:
                            if self.isKeystackAlive:
                                if self.envMgmtObj:
                                    self.envMgmtObj._setenv = env
                                    isEnvParallelUsed = self.envMgmtObj.isEnvParallelUsage()
                                else:
                                    isEnvParallelUsed = True
                            else: 
                                # If running from Linux host CLI, defaults to True if container/keystackUI is not running                             
                                isEnvParallelUsed = True
                               
                        # NOTE! Adding/Subtracting envMgmtData parameters here must be done in EnvAssistants.createEnvMgmtDataFile() also.
                        #                           
                        # Using envMgmt file to keep track of the env usage especially if -holdEnvsIfFailed was included.
                        # Used by EnvMgmt.py
                        # KeystackUI sessionMgmt creates an onclick button to release the envs when done debugging.
                        # Every stage/task/env has its own json envMgmt data file
                        envMgmtData = {'user': self.user,
                                       'testResultRootPath': self.timestampFolder,
                                       'sessionId': self.timestampFolderName,
                                       'stage': stage, 
                                       'task': taskName,
                                       'env': env,
                                       'portGroups': [],
                                       'envIsReleased': False,
                                       'holdEnvsIfFailed': self.holdEnvsIfFailed}

                        # envNameForResultPath: DOMAIN=Communal-Samples-demoEnv
                        envMgmtDataFile = f'{self.envMgmtDataFolder}/STAGE={stage}_TASK={taskName}_ENV={envNameForResultPath}.json'
                        writeToJson(envMgmtDataFile, envMgmtData, mode='w') 
                        chownChmodFolder(envMgmtDataFile, self.user, GlobalVars.userGroup, stdout=False)
                        self.keystackLogger.debug(f'envMgmtDataFile: {envMgmtDataFile} -> {json.dumps(envMgmtData, indent=4)}') 
                        if RedisMgr.redis:
                            # envNameForResultPath: DOMAIN=Communal-Samples-demoEnv
                            self.redisEnvMgmt = f'envMgmt-{self.timestampFolderName}-STAGE={stage}_TASK={taskName}_ENV={envNameForResultPath}'
                            self.writeToRedisEnvMgmt(keyName=self.redisEnvMgmt, data=envMgmtData)
                    else:
                        envMgmtDataFile = f'{self.envMgmtDataFolder}/STAGE={stage}_TASK={taskName}_ENV=None'
                        self.keystackLogger.debug(f'envMgmtDataFile: {envMgmtDataFile}') 
                        isEnvParallelUsed = ''
                        envNameForResultPath = None
                        self.envFileFullPath = None
                                                    
                        if env != 'not-required':
                            env = None
                            # Examples below the various ways to define env in playbooks 
                            # env = DOMAIN=QA/Samples/demoEnv1
                            #     = None (None type)
                            #     = ''   (None type)
                            #            (None type)
                            #     = not-required
                    
                    # User might not have included some module params: env, loadBalanceGroup, verifyPatterns, etc.
                    # Have to include it for generateReport to state the env used.
                    # Have to manually include artifactsFolder for user's scripts to consume the path
                    taskProperties.update({'env': env,
                                           'parallelUsage': isEnvParallelUsed,
                                           'envFile': self.envFileFullPath,
                                           'loadBalanceGroup': loadBalanceGroup,
                                           'artifactsFolder': self.artifactsFolder,
                                           'verifyFailurePatterns': verifyFailurePatterns,
                                           'playbookVars': playbookVars})
                    taskResultsFolder = f'{self.timestampFolder}/STAGE={stage}_TASK={taskName}_ENV={envNameForResultPath}'   
                    makeFolder(taskResultsFolder, stdout=False)
                    self.keystackLogger.debug(f'Stage={stage}  Task properties={taskName} => {json.dumps(taskProperties, indent=4)}')
                    
                    self.taskSummaryDataFile = f'{taskResultsFolder}/taskSummary.json'
                    self.taskSummaryData = {'user': self.user,
                                            'playbook': self.playbook,
                                            'stage': stage,
                                            'task': taskName,
                                            'env': env,
                                            'loadBalanceGroup': loadBalanceGroup,
                                            'envPath': self.envFileFullPath,
                                            'isEnvParallelUsed': isEnvParallelUsed,
                                            'playlistExclusions': taskProperties.get('playlistExclusions', []),
                                            'envParams': {},
                                            'status': 'Did-Not-Start',
                                            'result': None,
                                            'exceptionErrors': [],
                                            'pretestErrors': [],
                                            'taskResultsFolder': taskResultsFolder,
                                            'abortTaskOnFailure': self.abortTaskOnFailure,
                                            'showResultDataForNumberOfDays': 10,
                                            'currentlyRunning': None,
                                            'stopped': '',
                                            'testDuration': '',
                                            'totalPassed': 0,
                                            'totalFailed': 0,
                                            'totalFailures': 0,
                                            'pausedOnFailure': '',
                                            'totalTestAborted': 0,
                                            'totalSkipped': 0}

                    writeToJson(self.taskSummaryDataFile, data=self.taskSummaryData, mode='w')
                    chownChmodFolder(self.timestampFolder, GlobalVars.user, GlobalVars.userGroup, stdout=False)

                    if taskProperties.get('playlist', []):
                        taskPlaylist = taskProperties['playlist']
                    else:
                        taskPlaylist = []
                                       
                    if self.playbookTasks['stages'][stage].get('runTasksConcurrently', False):
                        if runTasksConcurrently and doOnceFlagForParallelLocks:                   
                            self.lock = threading.Lock()
                            self.mainLogFileLock = threading.Lock()
                            doOnceFlagForParallelLocks = False
                    
                    # Run each Playbook task in its own instance 
                    self.mainObj = RunTaskAssistant(keystackLogger=self.keystackLogger, playbookObj=self, playbook=self.playbook, task=taskName,        
                                                    envFile=self.envFileFullPath, stage=stage, taskEnvMgmtFile=envMgmtDataFile,
                                                    taskPlaylist=taskPlaylist, playbookGlobalSettings=self.playbookGlobalSettings,
                                                    stageProperties=stageProperties, taskProperties=taskProperties,
                                                    emailResults=self.emailResults, redisEnvMgmt=self.redisEnvMgmt,
                                                    debugMode=self.debug, taskResultsFolder=taskResultsFolder,
                                                    timestampRootLevelFolder=self.timestampFolder, sessionId=self.sessionId,
                                                    pauseOnFailure=self.pauseOnFailure, holdEnvsIfFailed=self.holdEnvsIfFailed,
                                                    user=self.user, isFromKeystackUI=self.isFromKeystackUI,
                                                    awsS3Upload=self.awsS3Upload, statusFileLock=self.lock,
                                                    mainLogFileLock=self.mainLogFileLock, jira=self.jira, execRestApiObj=self.execRestApiObj)
                                
                    if runTasksConcurrently:
                        threadObj = threading.Thread(target=self.mainObj.run, name=f'{stage}-{taskName}-{env}')
                        threadObj.start()
                        #print(f'\nkeystack.py runPlaybook(): runTasksConcurrently starting: {threadObj.name}')
                        threadList.append(threadObj)
                        # Must add a delay here in case env load balance group is configured.
                        # If no delay is added, the LBG don't have enough time to set the env as reserved. So now
                        # multiple tasks are contending for the same env vs getting the next available env.
                        sleep(1)
                    else:
                        self.lock = False
                        if self.mainObj.hasPlaylist:
                            if self.abortStageOnFailure and didTaskFail:
                                continue
                            
                            self.mainObj.run(skipTask=didTaskFail)

                            for taskItem in self.overallSummaryData['stages'][stage]['tasks']:
                                for task, properties in taskItem.items():
                                    if task == taskName:
                                        if properties['result'] != 'Passed':
                                            if self.abortStageOnFailure:
                                                didTaskFail = True
                        
                    # Delay each test in case the tests are using the same env and if they finish very fast.
                    # Not enough time to holdEnvsIfFailed.
                    time.sleep(.5)
                                                    
            if runTasksConcurrently:
                while True:
                    breakoutCounter = 0

                    for eachJoinThread in threadList:
                        print(f'\nkeystack.py runPlaybook(): thread completed: {eachJoinThread.name}')
                        eachJoinThread.join()
                    
                        if eachJoinThread.is_alive():
                            print(f'\n{eachJoinThread.name} is still alive\n')
                        else:
                            print(f'{eachJoinThread.name} alive == {eachJoinThread.is_alive}\n')
                            breakoutCounter += 1
        
                    if breakoutCounter == len(threadList):
                        print('\nAll threads are done\n')
                        break
                    else:
                        continue
                   
        except Exception as errMsg:
            msg = f'Playbook runTasks exception: {traceback.format_exc(None, errMsg)}'
            self.exceptionErrors.append(msg)
            #print(f'\n{msg}')
            self.updateOverallSummaryDataOnRedis()
            raise
    
    def readReconfigData(self):
        # Read and concatinate all reconfig data files users included by using -testConfigs
        # Write data to testSessionReconfigs.yml
        
        if self.testConfigs:
            for reconfigFile in self.testConfigs:
                regexMatch = re.search(f'{GlobalVars.testConfigsFolder}.+({reconfigFile})', reconfigFile)
                if regexMatch:
                    reconfigPath = regexMatch.group(1)
                else:
                    reconfigPath = reconfigFile
                
                if reconfigPath.endswith('.yml') is False:
                    reconfigPath = f'{reconfigPath}.yml'
                
                # /opt/KeystackTests/Reconfigs/<reconfig file>.yml       
                self.reconfigReferenceFile = f'{GlobalVars.testConfigsFolder}/{reconfigPath}'

                if os.path.exists(self.reconfigReferenceFile) is False:
                    self.abortTest(f'No such reconfig file: {self.reconfigReferenceFile}')

                data = readYaml(self.reconfigReferenceFile)
                self.reconfigData.update(data)
                self.keystackLogger.debug(f'Reconfigs: {self.reconfigReferenceFile}') 
                testSessionReconfigsFile = f'{self.timestampFolder}/testSessionReconfigs.yml'
                writeToYamlFile(self.reconfigData, yamlFile=testSessionReconfigsFile)
             
            pprint(self.reconfigData)  
           
    def updateStageResult(self, stage, taskResult): 
        """ 
        This function is called at the end of the RunTask class.
        Update the stage result used by executeStages()
        """                   
        if self.overallSummaryData['stages'][stage]['result'] is None:
            self.overallSummaryData['stages'][stage]['result'] = taskResult
        else:
            if self.overallSummaryData['stages'][stage]['result'] == 'Passed' and taskResult in ['Failed', 'Aborted']:
                self.overallSummaryData['stages'][stage]['result'] = taskResult

            if self.overallSummaryData['stages'][stage]['result'] == 'Passed' and taskResult == 'Passed':
                # Don't do anything.  Leave the stage passed
                pass
                                        
            if self.overallSummaryData['stages'][stage]['result'] == 'Failed' and taskResult in ['Failed', 'Aborted']:
                self.overallSummaryData['stages'][stage]['result'] = taskResult

            if self.overallSummaryData['stages'][stage]['result'] in ['Failed', 'Aborted'] and taskResult == 'Passed':
                # Leave the stage failed/aborted
                pass

    def ciTestResultPath(self):
        """ 
        TODO:
            - Create a new folder: CI_TestResultPaths
            - Create a file for each test session. Use sessionId as filename
            - Do cleanups after # days
        """
        # 12-01-2023-14:35:30:410843_hgee
        timestamp = self.timestampFolderName.split('_')[0]
        
        data = {self.sessionId: {'timestamp': timestamp,
                                 'result': self.overallSummaryData['result'],
                                 'resultPath': self.timestampFolder}}
        
        if self.continuousIntegration:
            if os.path.exists(GlobalVars.ciTestResultLocationFile) is False:
                writeToJson(jsonFile=GlobalVars.ciTestResultLocationFile, data=data, mode='w')
                chownChmodFolder(topLevelFolder=GlobalVars.ciTestResultLocationFile,
                                 user=GlobalVars.user, userGroup=GlobalVars.userGroup)
            else:
                existingData = readJson(GlobalVars.ciTestResultLocationFile)
                existingData.update(data)
                writeToJson(jsonFile=GlobalVars.ciTestResultLocationFile, data=existingData, mode='w')
                         
    def getLoginCredentials(self):
        """ 
        Get the login details from file .loginCredentials.yml
        Verify all credential values
        """
        isAnyServiceEnabled = False
        for platform in [self.jira, self.awsS3Upload]:
            if platform:
                isAnyServiceEnabled = True
                
        if isAnyServiceEnabled is False:
            return

        if 'loginCredentialKey' not in self.playbookGlobalSettings:
            raise Exception(f'You did not set which loginCredentialKey to use in playbook.globalSettings.')

        self.credentialYmlFile = GlobalVars.loginCredentials

        if os.path.exists(self.credentialYmlFile) is False:
            errorMsg = f'Login credentials file not found: {self.credentialYmlFile}.'
            self.keystackLogger.error(errorMsg)
            raise Exception(errorMsg)
        
        loginCredentialObj = readYaml(self.credentialYmlFile)
        self.loginCredentialKey = self.playbookGlobalSettings['loginCredentialKey']
        if self.loginCredentialKey not in loginCredentialObj:
            raise Exception(f'Playbook globalSettings:loginCredentialKey "{self.loginCredentialKey}" does not exists in the loginCredentials.yml file')
            
        self.loginCredentials = loginCredentialObj[self.loginCredentialKey]
        
        # Validate the credentials
        self.awsAccessKey = convertNoneStringToNoneType(self.loginCredentials.get('awsAccessKey', None))

        if self.awsAccessKey is None:
            self.awsAccessKey = convertNoneStringToNoneType(os.environ.get('AWS_ACCESS_KEY', None))

        self.awsSecretKey = convertNoneStringToNoneType(self.loginCredentials.get('awsSecretKey', None))
        if self.awsSecretKey is None:
            self.awsSecretKey = convertNoneStringToNoneType(os.environ.get('AWS_ACCESS_KEY', None))
                            
        self.awsS3BucketName = convertNoneStringToNoneType(self.loginCredentials.get('awsS3BucketName', None))    
        if self.awsS3BucketName is None:
            self.awsS3BucketName = convertNoneStringToNoneType(os.environ.get('AWS_S3_BUCKET_NAME', None))

        self.awsRegion = convertNoneStringToNoneType(self.loginCredentials.get('awsRegion', None))
        if self.awsRegion is None:
            self.awsRegion = convertNoneStringToNoneType(os.environ.get('AWS_REGION', None))
                    
        for eachAwsCredential in ['awsAccessKey', 'awsSecretKey', 'awsS3BucketName', 'awsRegion']:
            if getattr(self, eachAwsCredential) is None:
                raise Exception(f'keystack.py getLoginCredentials(): {eachAwsCredential} in .loginCredentials.yml is set to None.') 
        
    def getRestApiMods(self):
        """
        Allow users to create a dynamic Playbook from blank or 
        modify the Playbook, the Playbook task playlist and
        the Playbook task Env.
        
        Overwrite the self.playbookTasks with rest api mods (playbookConfigs).
        The rest api include the param -isFromKeystackUI as a flag.
           
        feature: KeystackSystemEnv | testcase | env | playbook 
        """
        # <sessionId>_configurations.json
        for modFile in glob(f'{self.restApiModsFolder}/*'):
            if '~' in modFile:
                os.remove(modFile)
                continue

            # The rest api mod file timestamp folder: 11-14-2022-09:44:08:336539_dynamicPlaybook
            # must be the same as -resultFolder. playbookView/runPlaybook created a timestamp folder
            # for both to match
            timestampResultFolder = modFile.split('/')[-1]
            timestampFolderName = self.timestampFolder.split('/')[-1] # Incoming timestamp folder name

            if timestampFolderName == timestampResultFolder:
                modsObj = readJson(modFile)
                # {"KeystackSystemEnv": {}, "testcase": [], "env": {}, "playbook": {}, "createDynamicPlaybook": False}
                self.restApiMods.update(modsObj)
                os.remove(modFile)
       
                if self.restApiMods['createDynamicPlaybook'] is False:
                    # Playbook: Update with the playbook
                    if self.restApiMods['playbook']:
                        self.playbookTasks = updateDict(self.playbookTasks, self.restApiMods['playbook'])
                        writeToYamlFile(self.playbookTasks, f'{self.sessionDataFolder}/playbook_{self.playbookName}.yml')
                        self.keystackLogger.debug(f'createDynamicPlaybook=False: File:{self.sessionDataFolder}/playbook_{self.playbookName}.yml. PlaybookTasks: {self.playbookTasks}')
                else:
                    # Create a dynamic playbook from scratch
                    self.playbookTasks = self.restApiMods['playbook']
                    writeToYamlFile(self.playbookTasks, f'{self.sessionDataFolder}/playbook_dynamically-created.yml')
                    self.keystackLogger.debug(f'createDynamicPlaybook=True: File:{self.sessionDataFolder}/playbook_dynamically-created.yml: PlaybookTasks:{self.playbookTasks}')

                # Testcases: Will be updated in readYmlTestcaseFile() using testcaseDict 
                # Env: Will be updated in Main() class
