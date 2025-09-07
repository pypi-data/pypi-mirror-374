import sys, os, traceback, datetime, yaml, re, json, time, traceback
import types
import subprocess
import operator
from copy import deepcopy
from pathlib import Path
from glob import glob
import runpy
from os import fdopen
from pydantic import Field, dataclasses, BaseModel
from typing import Optional
from pprint import pprint

from globalVars import GlobalVars
from commonLib import informAwsS3ServiceForUploads, KeystackException
from keystackUtilities import execSubprocess2, mkdir2, readFile, readYaml, readJson, writeToJson, getDictIndexList, getDictIndexFromList
from keystackUtilities import execSubprocessInShellMode, execSubprocess, getTimestamp, chownChmodFolder
from Services import Serviceware
from .EnvAssistants import EnvAssistant
from .TestReportAssistants import TestReportAssistant
from .TestcaseAssistants import TestcaseAssistant
from RedisMgr import RedisMgr
import EnvMgmt

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    
    
@dataclasses.dataclass
class RunTaskAssistant():
    """
    Keystack class that runs a Playbook Task
    
    Parameters
        isFromKeystackUI <bool>:            If True, the job came from the UI (docker). Used internally to know which
                                            Python path to use: docker python path or local linux host python path.
        playbookObj <obj>:                  The Playbook object to pass data from Main to Playbook level.
        playbook <str>:                     The full path to the playbook to play: /opt/KeystackTests/Playbooks/Samples/pythonSample.yml
        stage <str>:                        The stage the task is in.
        task <str>:                         Mandatory: The task to run for this test. 
        envFile <ymal file>:                Optional: None | A full path test env .yml file that contains test env 
                                            IP addresses, login credentials, environment config settings.      
                                            credentials, etc, without the path.
        taskEnvMgmtFile <str>:              The task's envMgmt file in /timstampResultFolder/.Data/EnvtMgmt.
                                            Use this file to track task result and holdEnvsIfFailed for ReleaseEnv to 
                                            utilize.
        taskPlaylist <folderPaths|yamlFiles>:  Mandatory: One or more folders containing testcase yaml files. Could also include
                                            individual yaml files. If it's a folder, all subfolders yaml files are
                                            executed also.
        playbookGlobalSettings:             The Playbook's global setting parameters.
        taskProperties <dict>:              From playbook. Each task properties/values.
        stageProperties <dict>:             From Playbook. Each stage properties/values.
        emailResults <bool>:                Optional: Send email results at the end of the test.
        debugMode <bool>:                   Optional: True = State 'Dev-Mode' in email result subject line and state debugMode 
                                            on the test timestamp folder.
        overallSummaryData <dict>:          The initial overall summary data that goes at the top-level timestamp folder.
        pauseOnFailure <bool>:              Pause the test on failure for debugging.
        holdEnvsIfFailed <bool>:            Don't release the env setups if the test failed for debugging.
        sessionId <int>:                    Optional: For referencing the test in KeystackUI and results folder
        taskResultsFolder <str>:            Results/Logs for the task.
        timestampRootLevelFolder <str>:     Ex: /KeystackTests/Results/Playbook_L3Testing/04-20-2022-12:29:57:258836_hgee
        user <str>:                         Optional: The logged in user.
        awsS3 <bool>:                       Upload results to AWS S3 Data-Lake
        statusFileLock <threadLock>:        File lock for overallSummary.json file
        mainLogFileLock <threadLock>:       File lock for the main debug log file and metadata.json
        execRestApiObj <None|Obj>:          Used for sending REST APIs. For EnvMgmt / holdEnvsIfFailed
    """

    keystackLogger:           object
    playbookObj:              Optional[object] = None
    playbook:                 Optional[str] = None
    stage:                    Optional[str] = None
    task:                     Optional[str] = None
    envFile:                  Optional[str] = None
    taskEnvMgmtFile:          Optional[str] = None
    taskPlaylist:             list = Field(default_factory=list)
    playbookGlobalSettings:   dict = Field(default_factory=dict)
    overallSummaryData:       Optional[str] = None
    sessionId:                Optional[str] = None
    taskProperties:           dict = Field(default_factory=dict)
    stageProperties:          dict = Field(default_factory=dict)
    emailResults:             bool = Field(default=False)
    debugMode:                bool = Field(default=False)
    taskResultsFolder:        Optional[str] = None
    timestampRootLevelFolder: Optional[str] = None
    pauseOnFailure:           bool = Field(default=False)
    holdEnvsIfFailed:         bool = Field(default=False) 
    user:                     Optional[str] = None
    awsS3Upload:              bool = Field(default=False)
    isFromKeystackUI:         bool = Field(default=False)
    statusFileLock:           Optional[object] = None
    mainLogFileLock:          Optional[object] = None
    jira:                     bool = Field(default=False)
    execRestApiObj:           Optional[object] = None
    keystackRootPath:         str = Field(default=GlobalVars.keystackRootPath)
    keystackTestRootPath:     str = Field(default=GlobalVars.keystackTestRootPath)
    keystackSystemPath:       str = Field(default=GlobalVars.keystackSystemPath)
    taskProperties:           dict = Field(default_factory=dict)
    stageProperties:          dict = Field(default_factory=dict)
    testAbortions:            int = Field(default=0)
    testStartTime:            object = datetime.datetime.now()
    testStopTime:             Optional[object] = None
    # envPortGroups: listf of portGroups to reserve / release
    envPortGroups:            list = Field(default_factory=list)
    testcaseResults:          Optional[str] = None
    portGroupsData:           dict = Field(default_factory=dict)
    portsData:                dict = Field(default_factory=dict)
    devicesData:              dict = Field(default_factory=dict)
    
    # envMgmt-{self.timestampFolderName}-STAGE={stage}_TASK={taskName}_ENV=DOMAIN=Communal-envName
    redisEnvMgmt:             Optional[str] = None
    
    # The module results folder:
    # /Results/DOMAIN="Communal"/04-20-2022-12:34:22:409096_<sessionId>/STAGE=Test_MODULE=PythonScripts_ENV=None
    taskResultsFolder: Optional[str] = None
    hasPlaylist:       bool = Field(default=False)
    
    def __post_init__(self):
        try:
            self.envAssist = EnvAssistant(self)
            self.testcaseAssist = TestcaseAssistant(self)
            self.testReportAssist = TestReportAssistant(self)
    
            # Just the name without the playbook group
            self.playbookName: str = self.playbook.split('/')[-1].split('.')[0]
            self.debug = self.debugMode

            # envFile could be "not-required" is used in playbook tasks to exclude the defined Env if 
            # the env or loadBalanceGroup is set at globalSettings or stage
            # self.envFile: /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/demoEnv1.yml
            if self.envFile and self.envFile != 'not-required':
                # self.env: DOMAIN=Communal/Samples/demoEnv1
                self.env = self.envFile.split('/Envs/')[-1].split('.')[0]
            if self.envFile is None:
                self.env = None
            if self.envFile == 'not-required':
                self.env = 'not-required'

            self.testResultPlaybookPath = f'{GlobalVars.keystackTestRootPath}/Results/DOMAIN={self.playbookObj.domain}/PLAYBOOK={self.playbookObj.playbookGroup}'
            
            # # The module results folder:
            # # /Results/Playbook_L3Testing/04-20-2022-12:34:22:409096_<sessionId>/STAGE=Test_MODULE=PythonScripts_ENV=None
            self.taskSummaryFile = f'{self.taskResultsFolder}/taskSummary.json'
            self.awsS3UploadResults = self.awsS3Upload

            self.playbookObj.airMosaicCellList = [] ;# From airMosaic.py. Get the tested cells used and show in the report
            self.taskProperties.update({'dataConfigs': {}})
            
            # # For storing keystack_detailLogs: /KeystackTests/Results/Playbook_L3Testing/04-20-2022-12:29:57:258836_<sessionId>
            self.resultsTimestampFolder = self.timestampRootLevelFolder
            self.timestampFolderName = self.timestampRootLevelFolder.split('/')[-1]
            
            # # A main debug log file used to show which test got executed, errors/abortions and end results
            self.debugLogFile   = f'{self.resultsTimestampFolder}/detailLogs' 
            self.testReportFile = f"{self.resultsTimestampFolder}/testReport" ;# overall test report
            self.taskTestReportFile = f'{self.taskResultsFolder}/taskTestReport'
            
            # If you get error importing boto3: cannot import name 'DEFAULT_CIPERS from urllib3,
            # do pip install 'urllib3<2' --force-reinstall
            if self.awsS3Upload:
                self.awsS3ServiceObj = Serviceware.KeystackServices(typeOfService='keystackAwsS3', isFromKeystackUI=self.isFromKeystackUI)
                self.s3StagingFolder = Serviceware.vars.awsS3StagingFolder
                if self.awsS3ServiceObj.isServiceRunning('keystackAwsS3', showStdout=True) is False:
                    self.keystackLogger.debug('keystackAwsS3 service is not running.  Enabling the service...')

                    # Turn on Keystack AWS service
                    # f'{currentDir}/Services/keystackAwsS3.py'
                    if self.isFromKeystackUI:
                        pythonPath = keystackSettings.get('dockerPythonPath', None)
                        cmd = f'{pythonPath} {Serviceware.vars.keystackAwsS3Service} -isFromKeystackUI > /dev/null 2>&1 &'
                    else:
                        pythonPath = keystackSettings.get('pythonPath', None)
                        cmd = f'{pythonPath} {Serviceware.vars.keystackAwsS3Service} > /dev/null 2>&1 &'
 
                    self.awsS3ServiceObj.writeToServiceLogFile(msgType='info', msg=f'keystack: start keystackAwsS3 service: {cmd} ...',
                                                               playbookName=self.playbookObj.playbookName, sessionId=self.playbookObj.sessionId)
                    
                    try:
                        result = subprocess.call(cmd, shell=True)
                    except Exception as errMsg:
                        msg = f'Serviceware failed to start keystackAwsS3: {errMsg}'
                        self.keystackLogger.error(msg)
                        self.awsS3ServiceObj.writeToServiceLogFile(msgType='error', msg=f'keystack: start keystackAwsS3 service: {msg}',
                                                                   playbookName=self.playbookObj.playbookName, sessionId=self.playbookObj.sessionId)  
                        raise Exception(msg)
                    
                    if self.awsS3ServiceObj.isServiceRunning('keystackAwsS3') is False:
                        msg = f'Serviceware failed to start keystackAwsS3'
                        self.keystackLogger.error(msg)
                        self.awsS3ServiceObj.writeToServiceLogFile(msgType='failed', msg=msg,
                                                                   playbookName=self.playbookObj.playbookName, sessionId=self.playbookObj.sessionId)  
                        raise Exception(msg)
             
            # Initital envParams containing all module properties.
            # Testcases will be updated in getAllTestcaseFiles()
            self.envParams = {'playbook': self.playbook, 'tasks': self.playbookObj.playbookTasks['stages']}

            if self.playbookName != 'Dynamically-Created':
                if 'playbook' in self.playbookObj.restApiMods.keys() and self.playbookObj.restApiMods['playbook']:
                    self.envParams['playbook'] = f'{self.playbook} - modified'
                
            # Env system settings have been read in runPlaybook
            for envParam,value in keystackSettings.items():
                # if envParam.startswith('keystack_'):
                #     envParam = envParam.replace('keystack_', '')
                if value in ['True', 'true', 'yes', 'Yes']:
                    value = True
                if value in ['False', 'false', 'no', 'No']:
                    value = False
                if value in [None, 'None', 'null']:
                    value = None
                    
                self.envParams.update({envParam: value})

            # Update/overwrite envParams with Playbook global settings
            # This means that any params in the keystackSystemSettings.env could go in playbooks.
            self.envParams.update(self.playbookGlobalSettings)

            # These playbook params are common in globalSettings, stage and modules.
            for commonParam in ['abortTaskOnFailure', 'playbookVars', 'verifyFailurePatterns', 'env', 'loadBalanceGroup']:
                # OVERWRITE globalSettings at stage level
                    
                if commonParam in self.stageProperties['stage'][self.stage]:
                    self.envParams[commonParam] = self.stageProperties['stage'][self.stage][commonParam]
                    
                # OVERWRITE stage properties at module level
                if commonParam in self.taskProperties:
                    self.envParams[commonParam] = self.taskProperties[commonParam]
                else:
                    self.taskProperties.update({commonParam: {}})
                    
            # Env files could contain two type of resources:
            # 1> Env IP, login credentials, license server, etc.
            #    These env resources are stored in self.taskProperties['envParams']
            # 2> It could also contain testcase "configs". Users put them in env files so the configs could apply to all testcases.
            #    To overwrite them, put specific configs in the testcase yml file's configs key.
            #    In the env file, use the key "configs" and these testcase configs are stored in self.taskProperties['configs'].
            #    When reading testcase yml files, Keystack looks for "configs". If exists, overwrite self.taskProperties['configs'] 
            
            # Use the stated env file in the playbook if no rest api env was not provided for this test module
            # Overwrite env's variables
            if self.envFile and self.envFile != 'not-required':
                testEnvParams = readYaml(yamlFile=self.envFile, threadLock=self.statusFileLock)
                if testEnvParams is None:
                    raise Exception(f'keystack.py: Syntax error in the env file: {self.envFile}')
            
                self.taskProperties.update({'envParams': testEnvParams})
                  
                # Move the key "dataConfigs" to top level so testcaseDict could overwrite it if users defined 
                # the "dataConfigs" key in the testcase yml files.
                # And finally in the run() function, 'dataConfigs' in the testcase 'DataConfigs' folder
                # has highest overwrite precedence.

                # if 'configs' in testEnvParams:
                #     self.taskProperties.update({'configParams': testEnvParams['configParams']})

                if 'dataConfigs' in testEnvParams:
                    self.taskProperties.update({'dataConfigs': testEnvParams['dataConfigs']})
                                
            # Use Env settings provied by rest api CLI
            # "env": [
            #     {
            #         "stage": "Test",
            #         "module": "CustomPythonScripts",
            #         "envConfigs": {
            #             "login": false
            #         }
            #     }
            # ]
            # User is using REST API to modify the playbook
            if 'env' in self.playbookObj.restApiMods and \
                self.playbookObj.restApiMods['env'] != 'not-required' and \
                len(self.playbookObj.restApiMods['env']) > 0:   
                    for eachEnvMod in self.playbookObj.restApiMods['env']:
                        if eachEnvMod['stage'] == self.stage:
                            if eachEnvMod['task'] == self.task:
                                self.taskProperties['envParams'].update(eachEnvMod['params'])
                                if self.envFile:
                                    self.taskProperties.update({'env': f'{self.envFile} - modified'})
                
            # This is not-in-used. It is under work-in-progress.  Possibly remove it. 
            # Execute Play Actions first
            if self.taskProperties.get('playActions', []):
                for playAction in self.taskProperties.get('playActions', []):
                    self.runPlayAction(playAction)
            
            # Execute playlist        
            if self.taskProperties.get('playlist', []):
                self.hasPlaylist = True
                # try:
                #     # Some modules like AirMosaic don't have a config file folder
                #     self.configFileFolder = self.envParams.get('configFileFolder', None)
                # except:
                #     pass
                self.configFileFolder = self.envParams.get('configFileFolder', None)
                self.testcaseDict = dict()    
                self.testcaseAssist.getAllTestcaseFiles(self.taskProperties.get('playlistExclusions', []))
                    
                # if 'kafkaClusterIp' in self.envParams and self.envParams['kafkaClusterIp'] != "None":
                #     self.connectToKafka(self.envParams['kafkaClusterIp'])
                
                # if self.envParams.get('removeResultsFolder', GlobalVars.removeResultFoldersAfterDays) != 'never':
                #     # self.testResultPlaybookPath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=<playbook>
                #     removePastFoldersBasedOnFolderTimestamp(self.testResultPlaybookPath,
                #                                             removeDaysOlderThan=self.envParams.get('removeResultsFolder',
                #                                                                                    GlobalVars.removeResultFoldersAfterDays))
                    
            self.keystackLogger.debug(f'TaskProperties: {json.dumps(self.taskProperties, indent=4)}')

        except:
            raise
                  
    def writeToTestcaseLogFile(self, msg, includeTimestamp=True, stdout=True): 
        """ 
        Throughout testing, testcase logs are collected in Redis with this function.
        At the end of the test, transferTestcaseLogsRedisToFolder() is called to dump all 
        the testcase logs into a log file.
        """
        if includeTimestamp:
            timestamp = getTimestamp()
            enhancedMsg = f'{timestamp}: {msg}'
        else:
            enhancedMsg = msg
        
        if stdout:    
            print(f'{enhancedMsg}')
        
        try:
            RedisMgr.redis.appendStringValue(self.testcaseRedisKeyName, f'\n{enhancedMsg}')
        except:
            # There might've been an error and self.testcaseRedisKeyName doesn't exist. Don't blow up!
            pass
        
    def transferTestcaseLogsRedisToFolder(self, deleteRedisTestcaseKey=True):
        try:
            if self.testcaseDebugLogFile:
                testcaseLogs = RedisMgr.redis.getCachedKeyData(keyName=self.testcaseRedisKeyName, isJson=False)
                with open(self.testcaseDebugLogFile, 'w') as logFile:
                    logFile.write(testcaseLogs)
            
            if deleteRedisTestcaseKey:                    
                RedisMgr.redis.deleteKey(self.testcaseRedisKeyName)
        except:
            pass
                                                       
    def writeToMainLogFile(self, msg, writeType='a', includeTimestamp=True, printToStdout=True):
        """
        Main log file to show test checkpoints prior to running testcases and after running testcases
        """
        # TODO: Need to remove writing to detailed.log
        return
    
        if self.mainLogFileLock:
            self.mainLogFileLock.acquire()
            
        if includeTimestamp:
            timestamp = getTimestamp()
            enhancedMsg = f'{timestamp}: {msg}'
        else:
            enhancedMsg = msg

        if printToStdout:
            print(f'{enhancedMsg}\n')
            
        with open(self.debugLogFile, writeType) as logFile:
            logFile.write(f'{enhancedMsg}\n\n')
        
        if self.mainLogFileLock:    
            self.mainLogFileLock.release()

    def logInfo(self, msg, includeTimestamp=True):
        """ 
        Log a testcase info to the test case test.log debug file.
        """
        self.writeToTestcaseLogFile(f'[INFO]: {msg}', includeTimestamp=includeTimestamp)
        
    def logWarning(self, msg, includeTimestamp=True):
        """ 
        Log debug messages to show if something had occured.
        All warnings will be appended to the overallSummary.json file for quick view.
        """
        self.writeToTestcaseLogFile(f'[WARNING]: {msg}', includeTimestamp=includeTimestamp)
        self.playbookObj.overallSummaryData['warnings'].append({'testcase': self.testcaseResultsFolder, 'message': msg})
        self.testcaseData['warnings'].append(msg)
        self.playbookObj.updateOverallSummaryDataOnRedis()
           
    def logFailed(self, msg, includeTimestamp=True):
        """ 
        Log a testcase failure to the test case's test.log debug file.
        This function keep tracks of failures for the final test report.
        """
        self.writeToTestcaseLogFile(f'[FAILED]: {msg}', includeTimestamp=includeTimestamp)
        self.transferTestcaseLogsRedisToFolder(deleteRedisTestcaseKey=False)
                
        self.testcaseResult = 'Failed'
        self.taskSummaryData['totalFailures'] += 1
        self.testcaseData['totalFailures'] += 1
        self.playbookObj.overallSummaryData['totalFailures'] += 1
        self.testcaseData['failures'].append(msg)
    
        if self.pauseOnFailure:
            self.playbookObj.overallSummaryData['pausedOnFailureCounter'] += 1
            self.playbookObj.updateOverallSummaryDataOnRedis()
            
            self.taskSummaryData['pausedOnFailure'] = f'{self.taskResultsFolder}/pausedOnFailure'
            self.taskSummaryData['status'] = 'paused-on-failure'
            self.testcaseData['pausedOnFailure'] = True
            self.testcaseData['status'] = 'paused-on-failure'
            writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', retry=5)
            self.pauseTestOnFailure()
            
            # At this point, pause-on-error is  released
            self.testcaseData['pausedOnFailure'] = ''
            self.taskSummaryData['pausedOnFailure'] = ''
            self.testcaseData['status'] = 'Running'
            self.taskSummaryData['status'] = 'Running'
            writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', retry=5)

    def logDebug(self, msg, includeTimestamp=True):
        """ 
        Log a testcase debug message to the test case test.log debug file.
        """
        self.writeToTestcaseLogFile(f'[DEBUG]: {msg}', includeTimestamp=includeTimestamp)
        
    def logError(self, msg, includeTimestamp=True):
        """ 
        Log a testcase error message to the test case test.log debug file
        and abort the testcase.
        """
        # Must explicitly wrap exception errors in a string or else 
        # you a json dump error when writing to json data files
        traceErrorMsg = ''
        for line in str(msg).split('\n'):
            traceErrorMsg += f'{line}'
            
        self.writeToTestcaseLogFile(f'[ERROR]: {msg}', includeTimestamp=includeTimestamp)
        self.playbookObj.overallSummaryData['exceptionErrors'].append({'testcase': self.testcaseResultsFolder, 
                                                                       'message': traceErrorMsg,
                                                                       'status': 'Error'})
        self.testcaseData['exceptionErrors'].append(traceErrorMsg)
        self.playbookObj.updateOverallSummaryDataOnRedis()
        
        # Raise an exception to abort the task. Not aborting the test.
        raise Exception(traceErrorMsg)

    def updateTaskStatusData(self, status):
        """
        Update the run time overallSummary.json file.
        """
        self.taskSummaryData['status'] = status
        # Use mode='w' to always overwrite the old data with updated data
        writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', 
                    threadLock=self.statusFileLock, retry=3)
                     
    def pauseTestOnFailure(self):
        """ 
        Pause the test when a failure is encountered.
        Remove the pauseOnFailure file in the result timestamp folder when done 
        debugging to resume testing
        """
        pauseOnFailureFilePath = f'{self.taskResultsFolder}/pausedOnFailure'
        with open(pauseOnFailureFilePath, 'w') as fileObj:
            fileObj.write('')
 
        chownChmodFolder(pauseOnFailureFilePath, self.user, GlobalVars.userGroup, permission=770)      
        
        print(f'\npaused-on-failure! Go debug the issue. When done, remove the file: {pauseOnFailureFilePath}\n')
        self.keystackLogger.debug(f'\npaused-on-failure! Go debug the issue. When done, remove the file: {pauseOnFailureFilePath}\n')
        
        # Wait until user removes the pause-on-failure
        while True:
            if os.path.exists(pauseOnFailureFilePath):
                time.sleep(1)
                continue
            else:
                self.playbookObj.overallSummaryData['pausedOnFailureCounter'] -= 1
                self.playbookObj.updateOverallSummaryDataOnRedis()
                break
        
    def createJiraIssues(self):      
        if self.jira is False or self.overallResult == 'Passed':
            return

        self.jiraLogFileLock.acquire()
        issueList = []
        predefinedJiraIssueWithTestcases = False
          
        for testcase, properties in self.jiraFailures.items():
            # jiraTestcaseIssueKey are predefined opened jira issues that is used for logging bugs and set to active/opened
            if 'jiraTestcaseIssueKey' in self.testcaseDict[testcase] and self.testcaseDict[testcase]['jiraTestcaseIssueKey']:
                predefinedJiraIssueWithTestcases = True
                testcaseIssue = {'description': properties['bodyMessage']}
            else:
                testcaseIssue = {
                        'project': {'key': self.playbookObj.loginCredentials['jiraProject']}, 
                        'summary': properties['failed'],
                        'description': properties['bodyMessage'],
                        'issuetype': {'name': 'Bug'},
                        'assignee': {'name': self.playbookObj.loginCredentials['jiraAssignee']},
                        'priority': {'name': self.playbookObj.loginCredentials['jiraPriority']}               
                    }
                                
            issueList.append(testcaseIssue)
        
        self.keystackLogger.debug(f'IssueList: {issueList}')   
         
        try:
            from Services.JiraLib import Jira

            jiraObj = Jira(logFile=Serviceware.vars.jiraServiceLogFile, 
                           loginCredentialKey=self.playbookObj.loginCredentialKey)                    
            jiraObj.connect()
            
            if predefinedJiraIssueWithTestcases:
                predefinedIssueKey = self.testcaseDict[testcase]['jiraTestcaseIssueKey']
                self.writeToTestcaseLogFile(f'Jira: Using predefined issue key: {predefinedIssueKey}')
                
                for issue in issueList:
                    jiraObj.updateIssue(issueKey=predefinedIssueKey, 
                                        description=issue['description'], 
                                        setStatus=self.playbookObj.loginCredentials['jiraSetActiveStatus'])
                    
            if predefinedJiraIssueWithTestcases is False:
                if 'jiraAppendFailureToOpenedIssue' in self.playbookObj.loginCredentials:
                    # True | False
                    appendFailureToOpenedIssue = self.playbookObj.loginCredentials['jiraAppendFailureToOpenedIssue']
                
                self.writeToTestcaseLogFile(f'Jira: Creating issue: {issueList}')
                jiraObj.createIssueList(issueList=issueList, addCommentToExistingIssue=appendFailureToOpenedIssue)
                        
        except Exception as errMsg:
            self.writeToTestcaseLogFile(f'keystack.py: createJiraIssue: Exception: {traceback.format_exc(None, errMsg)}')
        
        self.jiraLogFileLock.release()
    
    def writeMetaDataToTopLevelResultsFolder(self):
        metadataFile = f'{self.resultsTimestampFolder}/metadata.json'
        metadata = readJson(metadataFile, threadLock=self.statusFileLock)
        metadata.update(self.stageReport)
        writeToJson(metadataFile, metadata, threadLock=self.statusFileLock)

    def logTaskExceptionError(self, errorMsg: str) -> None: 
        #print(f'\nlogTaskExceptionError(): {errorMsg}')        
        self.taskSummaryData['exceptionErrors'].append(errorMsg)
        writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', threadLock=self.statusFileLock)
        self.keystackLogger.debug(errorMsg)
                            
    def runStandAloneApp(self, typeOfApp='python', scriptFullPath=None, cliCommand=None):
        """
        Run plain Python scripts, shell scripts and any cli command
        Whow output in real time
        
        envAutoSetupAndTeardown: False | 'AutoSetup' | 'AutoTeardown'
        
        Requirements:
            - The testcase yaml files must set one of the followings
                  standalonePythonScripts: 
                  shellScripts:
                  cliCommands: 
        
            - In the playbook, use verifyFailurePatterns to look for failures:
                verifyFailurePatterns: ['Failed', 'SyntaxError']
             
        https://earthly.dev/blog/python-subprocess/
        """
        if typeOfApp == 'python':
            # sys.executable -> /usr/local/python3.10.0/bin/python3.10
            command = f'{sys.executable} {scriptFullPath}'
                
        if typeOfApp == 'shell':
            command = f'sh {scriptFullPath}'
        
        if typeOfApp == 'cli':
            command = cliCommand
         
        # testcase yml file might include scriptCmdlineArgs which are python script cmdline args
        if self.testcaseScriptArgv:
            command += f' {self.testcaseScriptArgv}'
        
        self.writeToTestcaseLogFile(f'[COMMAND]: {command}')
        # Add default failure serches
        self.verifyFailurePatterns = self.taskProperties.get('verifyFailurePatterns', None)
        errorPatterns = ['command not found', 
                         'Traceback', 
                         'SyntaxError:', 
                         "Can't find __main__",
                         '\[Errno [0-9]+\]', 
                         '/bin/sh:.*not found']
            
        self.keystackLogger.debug(f'typeOfApp:{typeOfApp} scriptFullPath:{scriptFullPath} cliCommand={cliCommand}')      

        try:
            writeToTaskSummaryFile = False
            entercounteredErrorPattern = False
            
            self.logInfo(f'\nrunStandAloneApp: typeOfApp: {typeOfApp} cliCommand: {command}')  
            # Note, bufsize=1 won't work without text=True or universal_newlines=True.        
            with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True) as output:
                # Flush stdout         
                with fdopen(sys.stdout.fileno(), 'wb', closefd=False) as stdout:                
                    for line in output.stdout: 
                        print(line.strip())
                        self.writeToTestcaseLogFile(line.strip(), includeTimestamp=False, stdout=False)
 
                        for errorPattern in errorPatterns:
                            # The standalone script has error. Cannot use try/except to catch standalone script error
                            match = re.search(f'.*{errorPattern}', line.strip(), re.I)
                            if match:
                                entercounteredErrorPattern = True
                                writeToTaskSummaryFile = True
                                self.testcaseResult = 'Failed'
                                self.taskSummaryData['totalTestAborted'] += 1
                                self.taskSummaryData['result'] = 'Aborted'
                                self.taskSummaryData['status'] = 'Incomplete'
                                
                                standaloneScriptError = f'Script-Error: Command:{command}  Error:{line}'
                                self.taskSummaryData['exceptionErrors'].append(standaloneScriptError)
                                self.testcaseData['exceptionErrors'].append(standaloneScriptError)
                                
                                if self.verifyFailurePatterns is []:
                                    self.writeToTestcaseLogFile(standaloneScriptError)
                    
                        if entercounteredErrorPattern is False:                                                      
                            for eachFailurePattern in self.verifyFailurePatterns: 
                                if bool(re.search(eachFailurePattern, line.strip())):
                                    self.writeToTestcaseLogFile(f'[FAILED]: [Verify-Failure-Pattern]: task:{self.task} env:{self.env}: FailedPattern={eachFailurePattern} -> {line}')
                                    self.transferTestcaseLogsRedisToFolder(deleteRedisTestcaseKey=False)
                                    
                                    self.testcaseResult = 'Failed'
                                    self.playbookObj.overallSummaryData['totalFailures'] += 1
                                    self.taskSummaryData['totalFailures'] += 1
                                    self.testcaseData['totalFailures'] += 1
                                    self.testcaseData['failures'].append(line)
                                    writeToTaskSummaryFile = True

                                    if self.pauseOnFailure:
                                        self.playbookObj.overallSummaryData['pausedOnFailureCounter'] += 1
                                        self.playbookObj.updateOverallSummaryDataOnRedis()
                                        
                                        self.taskSummaryData['pausedOnFailure'] = f'{self.taskResultsFolder}/pausedOnFailure'
                                        self.taskSummaryData['status'] = 'paused-on-failure'
                                        self.testcaseData['pausedOnFailure'] = True
                                        self.testcaseData['status'] = 'paused-on-failure'
                                        writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', retry=5)
                                        self.pauseTestOnFailure()
                                        
                                        # At this point, pause-on-error is released
                                        self.testcaseData['pausedOnFailure'] = ''
                                        self.taskSummaryData['pausedOnFailure'] = ''
                                        self.testcaseData['status'] = 'Running'
                                        self.taskSummaryData['status'] = 'Running'
                        
            if self.testcaseResult != 'Failed':
                self.testcaseResult = 'Passed'
      
            if writeToTaskSummaryFile:                              
                writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', retry=5)
      
        except Exception as errMsg:
            self.logTaskExceptionError(f'runStandAloneApp script error: {traceback.format_exc(None, errMsg)}')
            raise Exception(errMsg)
            
    def convertDictObjToClassObj(self, dictObj):
        """ 
        Convert a dict object into a class object for passing in module properties
        into scripts to consume
        """
        return types.SimpleNamespace(**dictObj)

    def taskDependencies(self, eachTestcase):
        # Verify test case dependecies
        self.dependencySkipTestcase = False

        # taskProperties: {'enable': True, 'env': 'None', 'playlist': ['/Modules/CustomPythonScripts/Bringups']}
        if 'dependencies' in self.taskProperties:                     
            for isCurrentTestcase in self.taskProperties['dependencies'].keys():
                if isCurrentTestcase in eachTestcase:
                    if 'enable' in self.taskProperties['dependencies'][isCurrentTestcase] and \
                        self.taskProperties['dependencies'][isCurrentTestcase]['enable'] is False:
                            continue
                    
                    self.testcaseData.update(self.taskProperties['dependencies'][isCurrentTestcase])
                    dependOnCases = self.taskProperties['dependencies'][isCurrentTestcase]['dependOnCases']
                    
                    # dependencies:
                    #     /Testcases/Demo/L2L3/isis.yml:
                    #     enable: True
                    #         dependOnCases:
                    #             - /Playlist/Testcases/L2L3/bgp.yml
                    for eachDependentCase in dependOnCases:
                        regexMatch = re.search(f'({GlobalVars.keystackTestRootPath})?(.+)', eachDependentCase)
                        if regexMatch:
                            if regexMatch.group(2).startswith('/'):
                                eachDependentCase = f'{GlobalVars.keystackTestRootPath}{regexMatch.group(2)}'
                            else:
                                eachDependentCase = f'{GlobalVars.keystackTestRootPath}/{regexMatch.group(2)}'
                        
                        if os.path.exists(eachDependentCase) is False:
                            raise KeystackException(f'No such path found in dependency list: {eachDependentCase}')
                        
                        dependentTestcaseResultFiles = glob(f'{self.playbookObj.resultsMetaFolder}{eachDependentCase}*')

                        for resultFile in dependentTestcaseResultFiles:
                            # resultFile: testcaseResultsData-10-18-2024-11:43:34:154948_882_debug-/opt/KeystackTests/Playlist/Demo/L2L3_Testcases/bgp.yml_1_1

                            # NOTE:
                            #    The dependent testcase could have been iterated in a loop
                            #    So any of the dependent testcase failed result will skip the current testcase 
                            currentDependencyData = readJson(resultFile)
                                
                            # The dependent testcase had ran and finished already
                            result = currentDependencyData['result']
                            self.writeToTestcaseLogFile(f'[DEPENDENCY]: {eachDependentCase}:  Result={result}') 
                            if result != 'Passed':
                                # Update the current running testcase. Pop it and insert updated data.
                                self.testcaseData.update({'result': 'Skipped', 
                                                          'status': 'Skipped', 
                                                          'skipped': True,
                                                        })
                                
                                match = re.search('(/Modules.+|Testcases.+)', eachDependentCase)
                                if match:
                                    theModule = match.group(1)
                                else:
                                    theModule = eachDependentCase
                                    
                                msg = f"Dependent case failed: {theModule}"
                                self.testcaseData['failures'].append(msg)
                                writeToJson(self.testcaseResultsMetaFile, self.testcaseData)                                    
                                self.writeToTestcaseLogFile(f'[SKIPPING TESTCASE]: Dependency failed: {eachDependentCase}')
                                self.dependencySkipTestcase = True

                                # NOTE: taskSummaryData['totalSkipped'] is calculated in TestReportAssistant
                                                        
    def initializeTaskSummaryData(self):
        """ 
        Update the current task in test data.
        Check if the current task has any exception error.
        Abort the current task if exception error exists.
        """ 
        # The self.taskResultsFolder could be updated in the envLoadBalance() function with updated ENV=<env>
        self.taskSummaryData.update({'status': 'Running',
                                     'result': 'Not-Ready',
                                     'cases': dict(),
                                     'env': self.env,
                                     'envPath': self.envFile,
                                     'sessionId': self.sessionId,
                                     'testcaseSortedOrderList': self.testcaseSortedOrderList,
                                     'totalLoopIterations': self.totalIterations,
                                     'outerLoop': self.totalOuterLoopIterations,
                                     'topLevelResultFolder': self.resultsTimestampFolder,
                                     'taskResultsFolder': self.taskResultsFolder,
                                     'currentlyRunning': None,
                                     'progress': f'0/{self.totalIterations}',
                                     'totalCases': len(self.testcaseSortedOrderList),
                                     'pausedOnFailure': False,
                                     'started': self.testStartTime.strftime('%m-%d-%Y %H:%M:%S:%f'),
                                     'abortTaskOnFailure': self.envParams['abortTaskOnFailure'], 
                                     }) 
        
        writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', threadLock=self.statusFileLock)
    
    def verifyForExceptionError(self):
        if len(self.taskSummaryData['exceptionErrors']) > 0:
            self.testStopTime = datetime.datetime.now()
            self.testDeltaTime = str((self.testStopTime - self.testStartTime))
            self.taskSummaryData['stopped'] = self.testStopTime.strftime('%m-%d-%Y %H:%M:%S:%f')
            self.taskSummaryData['testDuration'] = self.testDeltaTime
            self.taskSummaryData['status'] = 'Aborted'
            self.taskSummaryData['result'] = 'None'
            self.taskSummaryData['totalTestAborted'] += 1
            self.taskSummaryData['currentlyRunning'] = None
            writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', threadLock=self.statusFileLock)

            self.playbookObj.overallSummaryData['totalTestAborted'] += 1               
            self.playbookObj.overallSummaryData['currentlyRunning'] = None
            self.playbookObj.overallSummaryData['status'] = 'Aborted'
            self.playbookObj.overallSummaryData['result'] = 'None' 
            self.playbookObj.updateOverallSummaryDataOnRedis()
            self.testReportAssist.generateTaskTestReport(modulePretestAborted=True)
            return True
                      
    def run(self, skipTask=False):
        """
        Run a task (Keystack Module)
        Execute each testcase based on the collected yaml testcase files
        
        skipTask <bool>
             - skipTask is set to True if abortTaskOnFailure is True
             - And the previous task within the same stage failed
        """
        self.keystackLogger.debug(f'TaskName: {self.task}   skipTask={skipTask}')

        try:
            if skipTask:
                return
            
            if 'waitTimeBetweenTests' in self.taskProperties:
                self.waitTimeBetweenTests = self.taskProperties['waitTimeBetweenTests']
            else:
                self.waitTimeBetweenTests = 0
            
            if 'outerLoop' in self.taskProperties:
                self.totalOuterLoopIterations = int(self.taskProperties['outerLoop'])
                if self.totalOuterLoopIterations == 0:
                    self.totalOuterLoopIterations = 1
            else:
                self.totalOuterLoopIterations = 1
            
            self.totalIterations = 0
            for outerLoop in range(1, self.totalOuterLoopIterations+1):
                for eachTestcase, cmdLindArgs in self.testcaseSortedOrderList:
                    testcaseInnerLoopCount = self.testcaseAssist.getLoopTestcaseCount(eachTestcase)
                    self.totalIterations += testcaseInnerLoopCount
                
            doOneTimeOnly = 0
            self.testcaseDebugLogFile = None
            self.emailAttachmentList = []
            self.taskSummaryData = readJson(self.taskSummaryFile)
            self.initializeTaskSummaryData()
         
            # if skipTask is False:
            # Declaring this variable = None before envHandler autoSetup calling runStandaloneApp
            self.testcaseScriptArgv = None
            self.envAssist.envHandler()
            
            if self.verifyForExceptionError():
                # There is are errors. Exit the task.
                return
            
        except (KeystackException, Exception) as errMsg:
            self.logTaskExceptionError(str(errMsg))
        
        # Verify all exceptionErrors.  Don't go beyond this point if there is any exception error
            
        # For Keystack sessionMgmt
        testcaseCounter = 0
        
        # Not-Ready | Passed | Failed
        self.overallResult = 'Not-Ready'
        
        # For test with loops
        self.excludePassedResults = False
        
        # To avoid redoing the same thing in a for loop such as creating resources to consume in scripts
        self.doOnceOnly = True
        
        # For KPI analyzing
        self.operators = {'>': operator.gt, '<': operator.lt, '<=': operator.le, '>=': operator.ge, '=': operator.eq}

        # This will allow scripts to import keystackEnv in order for scripts to use test parameters from env, testcases, playbook
        sys.path.append(GlobalVars.appsFolder)

        for outerLoop in range(1, self.totalOuterLoopIterations+1):
            self.outerLoop = outerLoop
            
            # ['/opt/KeystackTests/Modules/Demo/Samples/Bringups/bringupDut1.yml', '/opt/KeystackTests/Modules/Demo/Samples/Bringups/bringupDut2.yml']
            for eachTestcase, cmdLineArgs in self.testcaseSortedOrderList:        
                self.keystackLogger.debug(f'Running testcase: {eachTestcase}')
                self.testcaseFileName = eachTestcase.split('/')[-1] 
                self.testcaseYmlFilename = eachTestcase.split('/')[-1].split('.')[0]               
                self.abortTestCaseErrors = []
                self.testcasePythonScripts = []
                self.testcaseStandalonePythonScripts = []
                self.testcaseShellScripts = []
                self.testcaseRunCliCommands = []
                self.testcaseAppLibraryPathsToImport = []
                self.loopTestcase = self.testcaseAssist.getLoopTestcaseCount(eachTestcase)
                self.testcaseScriptArgv = cmdLineArgs
                self.testcaseResultsMetaFile = None
                self.isPythonScriptImportingKeystackEnv = False
                
                # eachTestcase could be a testcase.yml file or .py script or .sh|.bash shell script
                if eachTestcase.endswith('.yml'):
                    self.testcaseAppLibraryPathsToImport = self.testcaseAssist.getTestcaseAppLibraryPath(eachTestcase)
                    if self.playbookObj.reconfigData and eachTestcase in self.playbookObj.reconfigData.keys():
                        for argLine in self.playbookObj.reconfigData[eachTestcase]['scriptCmdlineArgs']:
                            self.testcaseScriptArgv += f' {argLine}'
                    else:
                        for argLine in self.testcaseDict[eachTestcase].get('scriptCmdlineArgs', []):
                            self.testcaseScriptArgv += f' {argLine}' 
                    
                    # The Keystack cmdline -appArgs overwrites testcase yml file scriptCmdlineArgs.
                    if self.playbookObj.appArgs:
                        self.testcaseScriptArgv = self.playbookObj.appArgs

                    # Keystack integrated Python scripts
                    if self.testcaseDict[eachTestcase].get('pythonScripts', []):
                        self.testcasePythonScripts = self.testcaseAssist.getTestcaseScript(typeOfScript='pythonScripts', testcase=eachTestcase)
                    # Standalone Python scripts
                    if self.testcaseDict[eachTestcase].get('standalonePythonScripts', []):
                        self.testcaseStandalonePythonScripts = self.testcaseAssist.getTestcaseScript(typeOfScript='standalonePythonScripts',
                                                                                                     testcase=eachTestcase)
                    
                    # Shell/Bash scripts                        
                    if self.testcaseDict[eachTestcase].get('shellScripts', []):
                        self.testcaseShellScripts = self.testcaseAssist.getTestcaseScript(typeOfScript='shellScripts', testcase=eachTestcase)
                        
                    if self.testcaseDict[eachTestcase].get('cliCommands', []):
                        self.testcaseRunCliCommands = self.testcaseDict[eachTestcase]['cliCommands']

                else:
                    # Getting in here means the playbook stage/task isn't running a testcase YAML file
                    # Python scripts integrating with keystackEnv is supported here
                    # Otherwise, if python scripts don't import keystackEnv, verifyFailurePatterns is still supported
                    self.testcaseScriptArgv = cmdLineArgs

                    if eachTestcase.endswith('.py'):
                        scriptContents = readFile(eachTestcase)
                        if bool(re.search('.*keystackEnv', scriptContents)):
                            # Standalone python script is importing keystackEnv
                            self.testcasePythonScripts = [eachTestcase]
                            self.isPythonScriptImportingKeystackEnv = True
                        else:
                            # Standalone pythong script is not importing keystackEnv
                            # Using verifyFailurePattern to determine passed/failed result
                            self.testcaseStandalonePythonScripts = [eachTestcase]
                        
                    if eachTestcase.endswith('.sh') or eachTestcase.endswith('.bash'):                       
                        self.testcaseShellScripts = [eachTestcase]
                                                    
                if self.testcasePythonScripts is not [] \
                   and self.testcaseStandalonePythonScripts is [] \
                   and self.testcaseShellScripts is [] \
                   and self.testcaseRunCliCommands is []:
                        self.abortTestCaseErrors.append(f'Testcase did not state what to run: {eachTestcase}\nTestcase param values:\n{self.testcaseDict[eachTestcase]}') 
                                
                self.eachTestcase = eachTestcase
                self.innerLoopCounter = 1

                while True:
                    if self.innerLoopCounter > self.loopTestcase:
                        break
                    
                    try:
                        # Result: Passed, Failed, Incomplete
                        # Status: Did-Not-Start, Started, Running, Aborted, Terminated
                        # Each testcase summary report
                        self.testcaseData = {'testcase': eachTestcase,
                                             'timeStart': None,
                                             'timeStop': None,
                                             'testDuration': None,
                                             'status': 'Did-Not-Start',
                                             'outerLoop': f'{self.outerLoop}/{self.totalOuterLoopIterations}',
                                             'innerLoop': f'{self.innerLoopCounter}/{self.loopTestcase}',
                                             'currentInnerOuterLoop': f'{self.outerLoop}/{self.innerLoopCounter}',
                                             'testConfiguredDuration': None,
                                             'task': self.task,
                                             'testSessionId': None,
                                             'testSessionIndex': None,
                                             'pythonScripts': self.testcasePythonScripts,
                                             'standaloneScripts': self.testcaseStandalonePythonScripts,
                                             'shellScripts': self.testcaseShellScripts,
                                             'result': 'Not-Ready',
                                             'scriptCmdlineArgs': [],
                                             'totalFailures': 0,
                                             'KPIs': dict(),
                                             'testcaseResultsFolder': None,
                                             'testAborted': 'No',
                                             'pausedOnFailure': '',
                                             'exceptionErrors': [],
                                             'warnings': [],
                                             'failures': [],
                                             'passed': [],
                                             'skipped': skipTask}

                        self.taskSummaryData['currentlyRunning'] = eachTestcase
                        self.testcaseStart = datetime.datetime.now() # for test time delta
                        self.testcaseData['timeStart'] = self.testcaseStart.strftime('%m-%d-%Y %H:%M:%S:%f')
                        self.testcaseResult = 'Not-Ready'
                        
                        # 'tasks' field contains a list. In order to update the current task, must get the index,
                        # make the updates and insert it back to the same index position in the list.
                        # Note: The task properties were initialized in the playbook class in:
                        #       executeStages().runTaskHelper()
                        # dictIndexList: [{0: {'result': None, 'env': None, 'currentlyRunning': None}}]
                        # [{1: {'result': None, 'env': 'DOMAIN=Communal/Samples/demoEnv1', 'progress': '', 'currentlyRunning': None}}]
                        dictIndexList = getDictIndexList(self.playbookObj.overallSummaryData['stages'][self.stage]['tasks'], self.task)
                        index = getDictIndexFromList(dictIndexList, key='env', value=self.taskProperties['env'])
                        currentRunningTask = {self.task: {'result': self.taskSummaryData['result'], 
                                                          'env': self.taskProperties['env'], 
                                                          'progress': self.taskSummaryData['progress'],
                                                          'currentlyRunning': eachTestcase}}

                        if self.taskProperties['env'] not in ['not-required', None] and index is None:
                            # The stated env to use in playbook no longer exists. It has been removed.
                            self.logTaskExceptionError(f'RunTask.py:run() The env "{self.taskProperties["env"]}" stated in playbook in stage:{self.stage} task:{self.task} does not exists')
                            return
                        
                        self.playbookObj.overallSummaryData['stages'][self.stage]['tasks'].pop(index)
                        self.playbookObj.overallSummaryData['stages'][self.stage]['tasks'].insert(index, currentRunningTask)
                        self.playbookObj.updateOverallSummaryDataOnRedis(threadLock=self.statusFileLock)
     
                        if self.task not in ['AirMosaic']:
                            # AirMosaic result folder has additional cell vendor folder. Created in airMosaic.py.
                            # taskResultsFolder: /Results/Playbook_L3Testing/04-20-2022-12:34:22:409096_<sessionId>/STAGE=Test_TASK=PythonScripts_ENV=None
                            self.testcaseResultsFolder = f'{self.taskResultsFolder}/{self.testcaseYmlFilename}_{str(self.outerLoop)}x_{str(self.innerLoopCounter)}x'
                            self.testcaseData['testcaseResultsFolder'] = self.testcaseResultsFolder
                            self.testcaseDebugLogFile  = f'{self.testcaseResultsFolder}/test.log' 
                            self.testSummaryFile       = f'{self.testcaseResultsFolder}/testSummary.json'
                            execSubprocess(['mkdir', '-p', self.testcaseResultsFolder], stdout=False)
                            chownChmodFolder(self.resultsTimestampFolder, self.playbookObj.user, GlobalVars.userGroup, stdout=False)
                            chownChmodFolder(self.testcaseResultsFolder, self.playbookObj.user, GlobalVars.userGroup, stdout=False)
                            
                            if RedisMgr.redis:
                                # Write test logs to redis. Then transfer the logs to the testcase folder at the end of the test case
                                if self.env:
                                    setEnv = self.env.replace("/", "-")
                                else:
                                    setEnv = 'None'
                                self.testcaseRedisKeyName = f'testcase-{self.timestampFolderName}-STAGE={self.stage}_TASK={self.task}_ENV={setEnv}_TESTCASE={self.testcaseYmlFilename}_{str(self.outerLoop)}x_{str(self.innerLoopCounter)}x'
                                RedisMgr.redis.appendStringValue(keyName=self.testcaseRedisKeyName, stringValue="")
    
                            # Create testcaseResultsMetaFolder: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/10-18-2024-11:30:16:976622_5924_debug/.Data/ResultsMeta/opt/KeystackTests/Playlist/Demo/L2L3_Testcases
                            # Consumed by generateTaskTestReport()
                            testcaseResultsMetaFolder = '/'.join(f'{self.playbookObj.resultsMetaFolder}{eachTestcase}'.split('/')[:-1])
                            self.testcaseResultsMetaFolder = '/'.join(f'{eachTestcase}'.split('/')[:-1])                          
                            loopStrFormat = self.testcaseData["currentInnerOuterLoop"].replace('/', '_')
                            self.testcaseResultsMetaFile = f'{testcaseResultsMetaFolder}/{self.testcaseFileName}_{loopStrFormat}'

                            execSubprocessInShellMode(f'touch {self.testcaseResultsMetaFile}', showStdout=False)
                            chownChmodFolder(self.playbookObj.resultsMetaFolder, user=self.playbookObj.user,
                                             userGroup=GlobalVars.userGroup, stdout=False)
                            execSubprocess(['chmod', '-R', '774', self.resultsTimestampFolder], stdout=False)
                            
                            if skipTask is False:
                                self.writeToTestcaseLogFile(f'[STARTING CASE]: {eachTestcase}...Iterating: {self.outerLoop}:{self.innerLoopCounter}/{self.loopTestcase}x')

                        # skipTask is set to True if abortTaskOnFailure is caught
                        # The previous task within the same stage failed
                        if skipTask:
                            self.writeToTestcaseLogFile(f'[SKIPPING CASE]: {eachTestcase}...Iterating: {self.outerLoop}:{self.innerLoopCounter}/{self.loopTestcase}x')
                            self.overallResult = 'Skipped'
                            self.testcaseResult == 'Skipped'
                            self.playbookObj.overallSummaryData['totalSkipped'] += 1
                            self.testcaseData.update({'result': 'Skipped', 'status': 'Skipped'})
                            self.taskSummaryData.update({'status': 'Skipped', 'started': '', 'stopped': '', 'result': None})
                            self.taskSummaryData['totalSkipped'] += 1
                            writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', threadLock=self.statusFileLock, retry=5)
                            writeToJson(self.testSummaryFile, self.testcaseData, mode='w', threadLock=self.statusFileLock, retry=5)
                            writeToJson(self.testcaseResultsMetaFile, self.testcaseData)
                            return
                        
                        if self.doOnceOnly:        
                            # TEST CASE CONFIGS
                            self.testcaseParams = {}
                            self.testcaseParams['dataConfigs'] = {}
                            self.testcaseParams['exportedConfigsFile'] = None
                            self.dataConfigs = {}

                            # 1of4: Keystack reads Env keyword "dataConfigs" and store them in taskProperties['envParams']['dataConfigs'] first.
                            # Then below this, testcase yml files overwrite them if keyword 'dataConfigs' exists.
                            if self.taskProperties.get('envParams', None):
                                # Need to read the env file dataConfigs again because LoadCore del agents['agent']
                                if 'dataConfigs' in self.taskProperties['envParams']:
                                    envFileContents = readYaml(self.envFile)
                                    self.taskProperties['envParams'].update({'dataConfigs': envFileContents['dataConfigs']})
                                    
                                    # Decided not to do over-writes
                                    #self.testcaseParams['dataConfigs'].update(self.taskProperties['envParams']['dataConfigs'])
                                
                            # 2of4: For modules such as LoadCore: Each testcase must make a new copy of the key 'dataConfigs' 
                            # because LoadCore MW.reassignPorts() does a del agents['agent'] in the key 'configParam'                       
                            # If testcase yml file has 'dataConfigs', overwrite the dataConfigs from Env file
                            if eachTestcase.endswith('.yml'):
                                freshCopy = deepcopy(self.testcaseDict[eachTestcase])
                                for key,value in freshCopy.items():
                                    if key == 'dataConfigs':
                                        continue
                                    
                                    self.testcaseParams.update({key: value})

                                if 'dataConfigs' in self.testcaseDict[eachTestcase]:
                                    self.testcaseParams['dataConfigs'].update(self.testcaseDict[eachTestcase]['dataConfigs'])
                                    
                                # 3of4: Ultimately, dataConfigs are overwritten by DataConfigs file if the testcase includes it.
                                #       Location: /Modules/<name>/DataConfigs or state the full-path 
                                #       Used for: Passing in dictionary params/values into scripts / data-model file
                                self.dataConfigsFile = self.testcaseDict[eachTestcase].get("dataConfigsFile", None)
                                self.testcaseParams.update({"dataConfigsFile": self.dataConfigsFile})
                                if self.dataConfigsFile not in ['', 'None', 'none', None, 'null']:
                                    regexMatch = re.search('.*Modules/(.+DataConfigs/.+)', self.dataConfigsFile)
                                    if regexMatch:
                                        dataConfigFilesFullPath = f'{GlobalVars.keystackTestRootPath}/Modules/{regexMatch.group(1)}'  
                                        if os.path.exists(dataConfigFilesFullPath) is False:
                                            raise Exception(f'keystack: The dataConfigsFile does not exists: {dataConfigFilesFullPath}')    
                                    else:
                                        if os.path.exists(self.dataConfigsFile) is False:
                                            raise Exception(f'dataConfigsFile in testcase yml file does not exists: {self.dataConfigsFile}')
                                        else:
                                            dataConfigFilesFullPath = self.dataConfigsFile
                                            
                                    if '.json' in dataConfigFilesFullPath:
                                        self.dataConfigs = readJson(dataConfigFilesFullPath)
                                        self.testcaseParams['dataConfigs'].update(self.dataConfigs)
                                        
                                    if '.yml' in dataConfigFilesFullPath:
                                        self.dataConfigs = readYaml(dataConfigFilesFullPath)
                                        self.testcaseParams['dataConfigs'].update(self.dataConfigs)
                                else:
                                     self.testcaseParams['dataConfigs'] = {}
                                                                            
                                # Location: /Modules/<name>/ExportedConfigs  <- Must have a folder called ExportedConfigs                 
                                exportedConfigsFile = self.testcaseDict[eachTestcase].get("exportedConfigsFile", None)
                                if exportedConfigsFile not in ['', 'None', 'none', None, 'null']:
                                    regexMatch = re.search('.*Modules/(.+ExportedConfigs/.+)', exportedConfigsFile)
                                    if regexMatch:
                                        # self.exportedConfigsFolder = /opt/KeystackTests/Modules/<module>/ExportedConfigs
                                        self.exportedConfigsFullPath = f'{GlobalVars.keystackTestRootPath}/Modules/{regexMatch.group(1)}'
                                        if os.path.exists(self.exportedConfigsFullPath) is False:
                                            self.writeToTestcaseLogFile(f'Keystack: The exported config file does not exists: {self.exportedConfigsFullPath}')
                                            raise KeystackException(f'Keystack: The exported config file does not exists: {self.exportedConfigsFullPath}')
                                        else:
                                            self.testcaseParams['exportedConfigsFile'] = self.exportedConfigsFullPath
                                    else:
                                        self.exportedConfigsFullPath = exportedConfigsFile
                                        self.testcaseParams['exportedConfigsFile'] = exportedConfigsFile
                                        if os.path.exists(exportedConfigsFile) is False:
                                            raise Exception(f'exportedConfigsFile in testcase yml file does not exists: {exportedConfigsFile}')
                                else:
                                     self.testcaseParams['exportedConfigsFile'] = None

                            # If user includes -testConfigs, read the reconfig data files and overwrite the param values         
                            if eachTestcase in self.playbookObj.reconfigData.keys():
                                for reconfigParams in ['scriptCmdlineArgs', 'dataConfigs', 'dataConfigsFile', 'exportedConfigsFile']:
                                    if reconfigParams in self.playbookObj.reconfigData[eachTestcase].keys() or self.isPythonScriptImportingKeystackEnv:
                                        self.testcaseParams.update({reconfigParams: self.playbookObj.reconfigData[eachTestcase][reconfigParams]})
                                      
                        self.taskDependencies(eachTestcase)    
                        writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', threadLock=self.statusFileLock, retry=5)

                        # The current testcase depends on a testcase that failed. Skip this testcase
                        if self.dependencySkipTestcase:
                            break

                        testcaseCounter += 1
                        self.taskSummaryData['progress'] = f'{testcaseCounter}/{self.totalIterations}'   
                        
                        # Skip this testcase if there is any exception errors
                        if self.abortTestCaseErrors:
                            raise KeystackException(self.abortTestCaseErrors)

                        # Additional library modules to import that supports the test case
                        for appLibraryPath in self.testcaseAppLibraryPathsToImport:
                            sys.path.append(appLibraryPath)
                                
                        self.testcaseData['status'] = 'Running'
                        self.updateTaskStatusData(status="Running")

                        # Shell scripts with no keystackEnv resources 
                        if self.testcaseShellScripts:
                            for eachShellScript in self.testcaseShellScripts:
                                self.runStandAloneApp(typeOfApp='shell', scriptFullPath=eachShellScript)
                                
                        # Python scripts with no keystackEnv resources 
                        if self.testcaseStandalonePythonScripts:
                            for eachPythonStandAloneScript in self.testcaseStandalonePythonScripts:
                                self.runStandAloneApp(typeOfApp='python', scriptFullPath=eachPythonStandAloneScript)
                        
                        # Run any server app on CLI
                        if self.testcaseRunCliCommands:
                            for eachCliCommand in self.testcaseRunCliCommands:
                                self.runStandAloneApp(typeOfApp='cli', cliCommand=eachCliCommand)
                      
                        # For integrated python scripts with keystackEnv resources                               
                        if self.testcasePythonScripts:
                            if 'keystackEnv' in sys.modules:
                                del sys.modules['keystackEnv']
                            
                            sys.path.append(f'{GlobalVars.keystackSystemPath}/Apps')
                            # Pass the test object into the script for consumption
                            __import__('keystackEnv').keystack = self

                            # Don't keep setting resource parameters inside this while loop and 
                            # these resources applieds to all same task scripts/testcases
                            if self.doOnceOnly:
                                self.doOnceOnly = False
                                # Convert dict object to class object for Python scripts to consume data resources
                                # keystack.taskParams.envParams.<key>
                                # keystack.testcase.<key>
                                #self.taskParams = json.loads(json.dumps(self.taskProperties), object_hook=self.convertDictObjToClassObj)
                                #self.testcase = json.loads(json.dumps(self.testcaseParams), object_hook=self.convertDictObjToClassObj)
                                
                                # Note: self.portGroupsData, self.portsData and self.devicesData are included. Done in EnvAssistants
                            
                            for eachTestcasePythonScript in self.testcasePythonScripts:
                                self.writeToTestcaseLogFile(f'[SCRIPT]: {eachTestcasePythonScript}')
                                try:
                                    runpy.run_path(path_name=eachTestcasePythonScript, run_name='__main__')
                                except Exception as errMsg:
                                    self.writeToTestcaseLogFile(traceback.format_exc(None, errMsg))
                                    raise Exception(f'Script=Error: {traceback.format_exc(None, errMsg)}')
                                                                
                        # Getting means the testcase is done successfully

                        if self.taskSummaryData['totalTestAborted'] == 0 and len(self.taskSummaryData['exceptionErrors']) == 0:
                            self.taskSummaryData['status'] = 'Completed'
                            self.testcaseData['status'] = 'Completed'
                        else:
                            self.taskSummaryData['status'] = 'Incomplete'
                            self.testcaseData['status'] = 'Incompleted'
                            self.taskSummaryData['testAborted'] = 'Yes'
                            self.testcaseData['testAborted'] = 'Yes'
                            self.testcaseData['result'] = 'Aborted'
                            
                        # Note: self.testcaseResult is set in self.logFailed() called inside scripts
                        if self.testcaseResult == 'Failed':
                            self.taskSummaryData['totalFailed'] += 1
                            self.playbookObj.overallSummaryData['totalFailed'] += 1
                            self.testcaseData['result'] = 'Failed'
                            self.taskSummaryData['result'] = 'Failed'
                            # Overwrite the overallResult to Failed if there is a failure
                            self.overallResult = 'Failed'                        

                        if self.testcaseResult not in ['Failed', None] and \
                            self.taskSummaryData['status'] != 'Incomplete' and \
                                self.taskSummaryData['totalTestAborted'] == 0 and \
                                len(self.taskSummaryData['exceptionErrors']) == 0:
                            self.testcaseResult = 'Passed'
                            self.testcaseData['result'] = 'Passed'
                            self.taskSummaryData['result'] = 'Passed'
                            self.taskSummaryData['totalPassed'] += 1
                            self.playbookObj.overallSummaryData['totalPassed'] += 1

                        self.testcaseStop = datetime.datetime.now()
                        self.testcaseData['timeStop'] = self.testcaseStop.strftime('%m-%d-%Y %H:%M:%S:%f')
                        self.testcaseData['testDuration'] = str((self.testcaseStop - self.testcaseStart))
                        writeToJson(self.testSummaryFile, self.testcaseData, mode='w', threadLock=self.statusFileLock, retry=5)
                        
                        if self.waitTimeBetweenTests > 0:
                            time.sleep(int(self.waitTimeBetweenTests))

                        self.writeToTestcaseLogFile(f'[CASE COMPLETED]: STAGE:{self.stage} TASK:{self.task} {eachTestcase} {self.outerLoop}/{self.totalOuterLoopIterations}x {self.innerLoopCounter}/{self.loopTestcase}x [CASE RESULT]: {self.testcaseResult}')
                        
                    except (AssertionError, KeystackException, Exception) as errMsg:
                        if self.testcaseData['status'] == 'Did-Not-Start':
                            self.writeToTestcaseLogFile(f'[TEST CASE DID NOT RUN]: STAGE:{self.stage} TASK:{self.task} CASE:{eachTestcase} {self.outerLoop}/{self.totalOuterLoopIterations}x {self.innerLoopCounter}/{self.loopTestcase}x')

                        trace = ''
                        if sys.exc_info()[0] == KeystackException:
                            trace = str(errMsg)
                        else:
                            # -8 for two levels up
                            for eachTrace in traceback.format_exc().splitlines():
                                trace += f'{eachTrace}\n'
                            if trace == '': trace = None

                        self.testcaseStop = datetime.datetime.now()
                        self.testcaseResult = 'Aborted'
                        self.testcaseData['timeStop'] = self.testcaseStop.strftime('%m-%d-%Y %H:%M:%S:%f')
                        self.testcaseData['result'] = 'Aborted'
                        self.testcaseData['testAborted'] = 'Yes'
                        self.testcaseData['status'] = 'Aborted'
                        self.testcaseData['exceptionErrors'].append(trace)
                        writeToJson(self.testSummaryFile, self.testcaseData, mode='w', threadLock=self.statusFileLock, retry=5)
                 
                        self.taskSummaryData['status'] = 'Aborted'
                        self.taskSummaryData['result'] = 'Incomplete'
                        self.taskSummaryData['totalTestAborted'] += 1
                        self.taskSummaryData['currentlyRunning'] = None
                        self.taskSummaryData['exceptionErrors'].append(trace)    
                        writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', threadLock=self.statusFileLock)
                        
                        try:
                            self.writeToTestcaseLogFile(trace)
                        except:
                            # It is ok to fail to write to the testcase log file because
                            # it might not exists yet.
                            pass
                        
                        self.playbookObj.overallSummaryData['totalTestAborted'] += 1
                        self.playbookObj.overallSummaryData['exceptionErrors'].append(f'TestAborted: Stage={self.stage} TASK={self.task} Testcase={self.testcaseYmlFilename} Exception: {errMsg}')             
                   
                        if self.envParams.get('abortTaskOnFailure', False):
                            # Abort the test and don't run anymore testcases so user could debug the state of the test
                            self.writeToTestcaseLogFile('[ABORT-ON-FAILURE] abortTaskOnFailure is set to True. Aborting task.')
   
                        if self.testcaseResultsMetaFile:
                            writeToJson(self.testcaseResultsMetaFile, self.testcaseData, mode='w', threadLock=self.statusFileLock) 
                        
                            
                    finally:
                        if self.testcaseResultsMetaFile:
                            writeToJson(self.testcaseResultsMetaFile, self.testcaseData, mode='w', threadLock=self.statusFileLock)
                            
                        self.transferTestcaseLogsRedisToFolder()
                        self.keystackLogger.debug(f'Stage:{self.stage} Task:{self.task} Testcase result: {self.testcaseResult} -> {eachTestcase}')
                        
                        # Clean up sys path
                        try:
                            for appLibraryPath in self.testcaseAppLibraryPathsToImport:
                                index = sys.path.index(appLibraryPath)
                                del sys.path[index]
                                
                            if 'keystackEnv' in sys.modules:
                                del sys.modules['keystackEnv']    
                        except:
                            # It's ok to fail here
                            pass
                        
                        chownChmodFolder(topLevelFolder=self.resultsTimestampFolder, user=self.user, userGroup=GlobalVars.userGroup)

                        if self.awsS3UploadResults:
                            uploadToS3 = True
                            
                            # For loop tests, don't upload all the passed logs and artifacts to save space.
                            if self.totalOuterLoopIterations > 1 or self.loopTestcase > 1:
                                if self.testcaseData['result'] == 'Passed' and self.stage not in [self.playbookObj.stageSetup, self.playbookObj.stageTeardown]:
                                    uploadToS3 = False
                                    
                                    if self.playbookObj.includeLoopTestPassedResults:
                                        # Allow users to overwrite the default
                                        uploadToS3 = True

                            if uploadToS3:
                                # /opt/KeystackSystem/ServicesStagingArea/AwsS3Uploads/07-04-2022-18:55:00:743939
                                # self.testcaseResultsFolder = /path/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/04-10-2023-08:40:11:952322_<sessionId>/STAGE=Test_MODULE=CustomPythonScripts_ENV=pythonSample/bgp_0001x_0001x
                                # self.timestampFolderName = 04-13-2023-13:36:52:855428_hgee9
                                
                                informAwsS3ServiceForUploads(playbookName=self.playbookObj.playbookAndNamespace, sessionId=self.sessionId,
                                                             resultsTimestampFolder=self.resultsTimestampFolder,
                                                             listOfFilesToUpload=[self.testcaseResultsFolder],
                                                             loginCredentialPath=self.playbookObj.credentialYmlFile,
                                                             loginCredentialKey=self.playbookObj.loginCredentialKey,
                                                             logFile=self.testcaseDebugLogFile)
                        
                        if self.testcaseData['result'] == 'Passed' and self.stage not in [self.playbookObj.stageSetup, self.playbookObj.stageTeardown] and \
                            self.playbookObj.includeLoopTestPassedResults is False:
                            if self.totalOuterLoopIterations > 1 or self.loopTestcase > 1:
                                execSubprocessInShellMode(f'rm -rf {self.testcaseResultsFolder}', showStdout=False)
                                self.excludePassedResults = True

                        if self.testcaseData['result'] in ['Failed', 'Aborted']:
                            if self.playbookObj.abortTestOnFailure:
                                self.playbookObj.exitTest = True
                                self.logDebug('-abortTestOnFailure was enabled. Aborting test.')
                                
                                self.taskSummaryData['status'] = 'Aborted'
                                self.testcaseData['status'] = 'Aborted'
                                self.testcaseData['testAborted'] = 'Yes'
                                self.playbookObj.overallSummaryData['testAborted'] = True
                                self.playbookObj.overallSummaryData['status'] = 'Aborted'
                            
                            if self.playbookObj.abortStageOnFailure:
                                self.logDebug('-abortStageOnFailure=True. Aborting test.')
                                self.playbookObj.overallSummaryData['testAborted'] = True
                                self.playbookObj.overallSummaryData['stageFailAborted'] = True
                            
                            self.playbookObj.updateOverallSummaryDataOnRedis()
                            if self.testcaseResultsMetaFile:
                                writeToJson(self.testcaseResultsMetaFile, self.testcaseData, mode='w', threadLock=self.statusFileLock) 
                                
                            if self.playbookObj.abortTestOnFailure or self.playbookObj.abortStageOnFailure:
                                break


                        if self.taskSummaryData['status'] == 'Aborted' or self.envParams['abortTaskOnFailure']:
                            # Break ouf of the innerLoop while loop
                            self.logDebug('-abortTaskOnFailure==True or status==Aborted. Aborting test.')
                            break
                        else:
                            self.innerLoopCounter += 1
                            
                # Inner while loop        
                if self.taskSummaryData['status'] == 'Aborted' or self.envParams['abortTaskOnFailure']:
                    # Break out of the testcase for loop
                    break
                
                if self.playbookObj.exitTest:
                    break
            
            # Outer loop testcases                        
            if self.taskSummaryData['status'] == 'Aborted' or self.envParams['abortTaskOnFailure']:
                # Break out of the outerLoop iteration for loop
                break
        
            if self.playbookObj.exitTest:
                break
         
        # ---- At this point, task is done ----

        # Test is over.  Close it up.       
        self.testStopTime = datetime.datetime.now()
        self.testDeltaTime = str((self.testStopTime - self.testStartTime))
                               
        # Upload the task folder files to AWS-S3:
        if self.awsS3UploadResults:
            informAwsS3ServiceForUploads(playbookName=self.playbookObj.playbookAndNamespace, sessionId=self.sessionId,
                                         resultsTimestampFolder=self.resultsTimestampFolder,
                                         listOfFilesToUpload=[f'{self.taskResultsFolder}/taskTestReport',
                                                              f'{self.taskResultsFolder}/taskSummary.json'],
                                         loginCredentialPath=self.playbookObj.credentialYmlFile,
                                         loginCredentialKey=self.playbookObj.loginCredentialKey)
        
        # NOTE: Complete results and status are calculated in generateTaskTestReport() at the bottom                          
        if self.taskSummaryData['totalTestAborted'] == 0 and self.taskSummaryData['totalSkipped'] == 0:
            self.taskSummaryData['status'] = 'Completed'
            
            if self.overallResult != 'Failed':
                if self.testcaseResult not in ['Skipped', 'Aborted', 'Not-Ready', 'Failed']:
                    self.overallResult = 'Passed'
            
            self.taskSummaryData['result'] = self.overallResult
        
        if self.taskSummaryData['totalTestAborted'] > 0:
            self.taskSummaryData['status'] = 'Aborted'
            
        elif self.taskSummaryData['totalSkipped'] > 0:
            self.taskSummaryData['status'] = 'Incomplete'
            
        if len(self.taskSummaryData['exceptionErrors']) > 0 or self.taskSummaryData['status'] in ['Aborted', 'Incomplete']:
            self.taskSummaryData['result'] = 'Incompete'
        
        self.taskSummaryData['currentlyRunning'] = None
        self.taskSummaryData['stopped'] = self.testStopTime.strftime('%m-%d-%Y %H:%M:%S:%f')
        self.taskSummaryData['testDuration'] = self.testDeltaTime
        writeToJson(self.taskSummaryFile, self.taskSummaryData, mode='w', threadLock=self.statusFileLock)

        # METADATA: for KeystackUI
        # self.playbookObj.overallSummaryData['stages'][self.stage]['tasks'][self.task].update({
        #     'result': self.taskSummaryData['result'], 'env': self.taskProperties['env'], 'currentlyRunning': None})
        dictIndexList = getDictIndexList(self.playbookObj.overallSummaryData['stages'][self.stage]['tasks'], self.task)
        index = getDictIndexFromList(dictIndexList, key='env', value=self.taskProperties['env'])
        runningTask = {self.task: {'result': self.taskSummaryData['result'], 
                                   'env': self.taskProperties['env']}}
        self.playbookObj.updateStageResult(self.stage, self.overallResult)           
        self.playbookObj.overallSummaryData['stages'][self.stage]['tasks'].pop(index)
        self.playbookObj.overallSummaryData['stages'][self.stage]['tasks'].insert(index, runningTask)
        self.playbookObj.updateOverallSummaryDataOnRedis(threadLock=self.statusFileLock)

        # Release the env if task passed.
        if self.env and self.env != 'not-required':
            if self.taskProperties.get('parallelUsage', False) == True:
                # The env is parallelUsed. So just release the env.
                # releaseEnv calls /api/v1/env/removeFromActiveUsersListUI'
                self.keystackLogger.debug(f'The env:{self.taskProperties["env"]} is parallel mode.  Releasing env.')
                self.envAssist.releaseEnv(env=self.taskProperties['env']) 
                self.envAssist.releasePortGroup()
                
            if self.taskProperties.get('parallelUsage', False) is False:
                if self.execRestApiObj:
                    """ 
                    {'env': 'DOMAIN=Communal/Samples/demoEnv1',
                     'envIsReleased': False,
                     'holdEnvsIfFailed': True,
                     'result': 'Failed',
                     'sessionId': '12-14-2023-10:40:17:025196_8471',
                     'stage': 'Test',
                     'task': 'Layer3',
                     'user': 'user-1'
                    }
                    """
                    if '-' in self.taskProperties['env']:
                        env = self.taskProperties['env'].replace('-', '/')
                    else:
                        env = self.taskProperties['env']
                    
                    if self.taskSummaryData['result'] == 'Passed':
                        self.keystackLogger.debug(f'Task passed. Releasing Env: {self.taskProperties["env"]}')
                        self.envAssist.releaseEnv(env=env)
                        self.envAssist.releasePortGroup()
                    else:
                        if self.holdEnvsIfFailed is False:
                            self.keystackLogger.debug(f'holdEnvsIfFailed=False. Calling releaseEnv()  env={self.taskProperties["env"]}')
                            self.envAssist.releaseEnv(env=env)
                            self.envAssist.releasePortGroup()
        
        self.playbookObj.updateOverallSummaryDataFile() 
        self.testReportAssist.generateTaskTestReport()                        
        self.createJiraIssues()
        index = sys.path.index(f'{GlobalVars.appsFolder}')
        del sys.path[index]
        
        # Add delay to update env DB especially for -holdEnvsIffailed
        time.sleep(.5)
        return None