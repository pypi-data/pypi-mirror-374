""" 
Keystack services and variables
"""
import os, sys, time, re, subprocess, traceback
from glob import glob
from shutil import rmtree

currentDir = os.path.abspath(os.path.dirname(__file__))
keystackRootPath = currentDir.replace('/Services', '')
sys.path.insert(0, keystackRootPath)

from keystackUtilities import readYaml, readJson, readYaml, writeToJson, getTimestamp, execSubprocessInShellMode
from globalVars import GlobalVars

# Get the KeystackTests location. os.path.exists already checked in keystack.py Playbook()
keystackObj = readYaml('/etc/keystack.yml')

# Ex: /opt/KeystackSystem
keystackSystemPath = keystackObj['keystackSystemPath']
keystackSettings = readYaml(f'{keystackSystemPath}/keystackSystemSettings.yml')

    
class vars:    
    keystackTestsBaseDir = keystackObj["keystackTestRootPath"]
    keystackServiceLogsFolder = f'{keystackObj["keystackSystemPath"]}/Logs'
    pythonPath = None
    
    # On-Demand debugging: touch this file to enter debug mode. 
    # This will enable log verbosity and show more print statements.
    awsS3EnableDebugModeFile = f'{keystackObj["keystackSystemPath"]}/ServicesStagingArea/debuggingAwsS3'        
    keystackAwsS3Service =     f'{keystackRootPath}/Services/keystackAwsS3.py'
    awsS3ServiceLogFile  =     f'{keystackServiceLogsFolder}/keystackAwsS3.json'
    awsS3StagingFolder =       f'{keystackSystemPath}/ServicesStagingArea/AwsS3Uploads'
    awsS3ServiceLockFileName = 'awsS3Service.lock'
    keystackS3LockFileName   = 'keystackS3Write.lock'

    keystackJiraService = f'{keystackRootPath}/Services/keystackJira.py'
    jiraServiceLogFile  = f'{keystackServiceLogsFolder}/jira.json'
    jiraStagingFolder =   f'{keystackSystemPath}/ServicesStagingArea/Jira'
    jiraServiceLockFile = f'{jiraStagingFolder}/jiraService.lock'
    keystackTestJiraWriteLockFile = f'{jiraStagingFolder}/keystackTestJiraWrite.lock'
    
    keystackSchedulerService = f'{keystackRootPath}/Services/keystackScheduler.py'
    schedulerServiceLogFile  = f'{keystackServiceLogsFolder}/scheduler.json'
    
    keystackWatchdogService = f'{keystackRootPath}/Services/keystackWatchdog.py'
    keystackSyncTestResultsService = f'{keystackRootPath}/Services/keystackSyncTestResults.py'
    
    keystackDeleteLogsService = f'{keystackRootPath}/Services/keystackDeleteLogs.py'
    logsServiceLogFile  = f'{keystackServiceLogsFolder}/keystackUILogs.json'
    

class KeystackServices:
    def __init__(self, typeOfService=None, isFromKeystackUI=False):
        """ 
        typeOfService: options: keystackAwsS3 | keystackJira | keysatckLogs | keystackScheduler | keystackWatchdog
        
        Two ways of using this class:
        
            1> Each service .py module such as keystacAwsS3.py will set typeOfService accordingly to the type of service.
               Ex: serviceObj = Serviceware.KeystackServices(typeOfService='keystackAwsS3', isFromKeystackUI=True)
                                                                       
                   serviceObj = Serviceware.vars.awsS3StagingFolder
                   if serviceObj.isServiceRunning('keystackAwsS3', showStdout=True) is False:
                       # Do domething
                       
                   serviceObj.writeToServiceLogFile(msgType='info', msg=f'keystack: start keystackAwsS3 service: {cmd} ...',
                                                              playbookName=self.playbookObj.playbookName, sessionId=self.playbookObj.sessionId)
                   
                   serviceObj.restartService('keystackAwsS3')
                                                                                         
            2> CLI: keystack -restarttServices | -stopServices | -restartAwsS3
               Ex: Serviceware.KeystackServices().restartAwsS3()
        """
        self._service = typeOfService

        if typeOfService:
            self.setService(typeOfService)

        self.isFromKeystackUI = isFromKeystackUI
        
        if isFromKeystackUI:
            vars.pythonPath = keystackSettings['dockerPythonPath']
        else:
            vars.pythonPath = keystackSettings['pythonPath']
                
    def setService(self, service):       
        if service == 'keystackAwsS3':
            self.serviceLogFile = vars.awsS3ServiceLogFile
            self.stagingFolder  = vars.awsS3StagingFolder
            
        if service == 'keystackJira':
            self.lockFolderFile = vars.jiraServiceLockFile
            self.serviceLogFile = vars.jiraServiceLogFile
            self.folderLock     = vars.keystackTestJiraWriteLockFile
            self.stagingFolder  = vars.jiraStagingFolder

        if service == 'keystackScheduler':
            self.serviceLogFile = vars.schedulerServiceLogFile
         
        if service == 'keystackWatchdog':
            self.serviceLogFile = None

        if service == 'keystackSyncTestResults':
            self.serviceLogFile = None
                            
        if service == 'keystackDeleteLogs':
            self.serviceLogFile = vars.logsServiceLogFile
                                   
    @property   
    def service(self):
        return self._service
    
    @service.setter
    def service(self, whichService):
        self._service = whichService
        self.setService(whichService)
                   
    def writeToServiceLogFile(self, msgType, msg, playbookName=None, sessionId=None, 
                              logFile=None, fileLock=None, showOutput=False):
        """ 
        - awsS3 is called in keystack
        - logs is called in Django settings
        """
        if logFile is None:
            # Default to awsS3ServiceLogs file
            logFile = self.serviceLogFile
        
        if logFile is None:
            return
            
        if fileLock:
            fileLock.acquire()
            
        timestamp = getTimestamp()

        if showOutput:
            print(f'\n{msgType}: {msg}')
            
        if showOutput == False and msgType == 'debug':
            print(f'\n{msgType}: {msg}')
        
        if os.path.exists(logFile) == False:
            data = {'messages': []}
            writeToJson(logFile, data=data, mode='w')        
            execSubprocessInShellMode(f'chown :Keystack {logFile}', showStdout=showOutput) 
            execSubprocessInShellMode(f'chmod 770 {logFile}', showStdout=showOutput) 

        data = readJson(logFile)
        msg = {'timestamp': timestamp, 'playbook':playbookName, 'sessionId':sessionId, 'msgType': msgType, 'msg': msg}

        if playbookName is None:
            del msg['playbook']
            
        if sessionId is None:
            del msg['sessionId']
                    
        data['messages'].append(msg)
        writeToJson(logFile, data, mode='w')

        if fileLock:
            fileLock.release()

    def debugEnabled(self):
        if os.path.exists(vars.awsS3EnableDebugModeFile):
            return True
        else:
            return False
        
    def isFolderLocked(self, whichLock, fileLock, timeout=60):
        """ 
        Look for keystack test write lock.  Keystack will do the same for the service file lock.
        
        Defaulting timeout = 60 because copying the result data to the service staging folder 
        should not take more than 60 seconds.
        
        whichLock:
            Ex: /path/KeystackSystem/ServicesStagingArea/AwsS3Uploads/PLAYBOOK=<playbook>/<timestampFolder>_<sessionId>/awsS3Service.lock
            
            If from Keystack framework, then monitor the vars.awsS3ServiceLockFile
            If from keystackS3Service, then monitor the vars.keystackS3WriteLockFile
        """
        lockFileName = whichLock.split('/')[-1]
        timestampFolderPath = '/'.join(whichLock.split('/')[:-1])
        regexMatch = re.search('.*PLAYBOOK=([^ ]+)/.+_([^ ]+)/', whichLock)
        if regexMatch:
            playbookName = regexMatch.group(1)
            sessionId = regexMatch.group(2)
        else:
            playbookName = None
            sessionId = None
            
        counter = 0
        while True:
            # Verify if there are any folders. If not, remove the lock.
            currentGlobList = glob(f'{timestampFolderPath}/*')
            isLockFileExists = False
            if os.path.exists(whichLock):
                isLockFileExists = True
                # Remove the .lock file from the in-memory timestamp folder.
                # The .lock file is still there.  Not a real lock removal.
                index = currentGlobList.index(whichLock)
                currentGlobList.pop(index)
            
            if self.debugEnabled() and counter == 0:
                #Diplay message one time only
                message = f'isFolderLocked: Current files in staging folder:\n'
                if len(currentGlobList) > 0:    
                    #self.writeToServiceLogFile(msgType='info', msg=f'isFolderLocked: Current files in staging folder:'
                    #                           playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                    for eachFile in currentGlobList:
                        message += f'\t- {eachFile}\n'
                       
                    self.writeToServiceLogFile(msgType='info', msg=message, playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                
            if len(currentGlobList) == 0 and isLockFileExists:
                # There is no file/folders in the timestamp folder. Forcefully remove the .lock.
                try:
                    os.remove(whichLock)
                except Exception as errMsg:
                    self.writeToServiceLogFile(msgType='error', msg=f'isFolderLocked: {traceback.format_exc(None, errMsg)}', 
                                               playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                    
                return
            
            if os.path.exists(whichLock) == False and counter < timeout:
                if self.debugEnabled():
                    self.writeToServiceLogFile(msgType='debug', msg=f'isFoldereLocked: {timestampFolderPath}: No', 
                                               playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                break
            
            if os.path.exists(whichLock) and len(currentGlobList) > 0 and counter < timeout:
                if self.debugEnabled() and counter == 0:
                    self.writeToServiceLogFile(msgType='debug', msg=f'isFoldereLocked: {timestampFolderPath}: Yes', 
                                               playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                
                counter += 1
                time.sleep(1)
                continue
            
            if os.path.exists(whichLock) and counter == timeout:
                if self.debugEnabled():
                    self.writeToServiceLogFile(msgType='debug', msg=f'isFolderLocked: It has been {timeout} seconds. Forcefully unlocking folder: {timestampFolderPath}',
                                               playbookName=playbookName, sessionId=sessionId, fileLock=fileLock, showOutput=False)
                try:
                    os.remove(whichLock)
                except Exception as errMsg:
                    self.writeToServiceLogFile(msgType='error', msg=f'isFolderLocked: {traceback.format_exc(None, errMsg)}', 
                                               playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                                    
                return

    def lockFolder(self, whichLock, fileLock):
        """ 
        fileLock: thread lock
        """
        whichLockName = whichLock.split('/')[-1]
        regexMatch = re.search('.*PLAYBOOK=([^ ]+)/.+_([^ ]+)/', whichLock)
        if regexMatch:
            playbookName = regexMatch.group(1)
            sessionId = regexMatch.group(2)
        else:
            playbookName = None
            sessionId = None
            
        if self.debugEnabled():
            self.writeToServiceLogFile(mstType='debug', msg=f'lockFolder: {whichLock}', 
                                       playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
        
        if os.path.exists(whichLock):
            return
        else:
            timestampFolderPath = '/'.join(whichLock.split('/')[:-1])
            if os.path.exists(timestampFolderPath) == False:
                execSubprocessInShellMode(f'mkdir -p {timestampFolderPath}', showStdout=False)
                           
        with open(whichLock, 'w') as fileObj:
            fileObj.write('')
        
        execSubprocessInShellMode(f'chmod 777 {whichLock}')   

    def unlockFolder(self, whichLock, fileLock):
        whichLockName = whichLock.split('/')[-1]
        regexMatch = re.search('.*PLAYBOOK=([^ ]+)/.+_([^ ]+)/', whichLock)
        if regexMatch:
            playbookName = regexMatch.group(1)
            sessionId = regexMatch.group(2)
        else:
            playbookName = None
            sessionId = None
            
        if os.path.exists(whichLock):
            if self.debugEnabled():
                self.writeToServiceLogFile(msgType='debug', msg=f'UnlockFolder: {whichLock}', 
                                           playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                
            try:
                os.remove(whichLock)
            except Exception as errMsg:
                self.writeToServiceLogFile(msgType='error', msg=f'unlockFolder: {traceback.format_exc(None, errMsg)}', 
                                           playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)   
                    
    def isServiceRunning(self, service, showStdout=False):
        """
        service: keystackAwsS3, keystackJira, keystackDeleteLogs, keystackScheduler, keystackWatchdog
        """
        if showStdout:
            print(f'Verifying for keystack service: {service} ...')
            
        result, process = execSubprocessInShellMode(f'ps -ef | grep {service}', showStdout=showStdout)

        if process:
            match = re.search(f'.*{keystackRootPath}/Services/{service}.py.*', process)
        
            if match:
                if showStdout:
                    print(f'KeystackServices:isServiceRunning: {service} is running')
                return True
            else:
                if showStdout:
                    print(f'KeystackServices:isServiceRunning: {service} is not running')
                return False

        return False
    
    def startService(self, service):
        """
        if self.isFromKeystackUI:
            pythonPath = keystackSettings.get('dockerPythonPath', None)
            cmd = f'{pythonPath} {Serviceware.vars.keystackAwsS3Service} -isFromKeystackUI > /dev/null 2>&1 &'
        else:
            pythonPath = keystackSettings.get('pythonPath', None)
            cmd = f'{pythonPath} {Serviceware.vars.keystackAwsS3Service} > /dev/null 2>&1 &'
                        
        Parameters
           service: <str>: logs|awsS3|jira
        """
        self.setService(service)

        if service == 'keystackDeleteLogs':
            serviceScript = vars.keystackDeleteLogsService
            
        if service == 'keystackAwsS3':
            serviceScript = vars.keystackAwsS3Service

        if service == 'keystackScheduler':
            serviceScript = vars.keystackSchedulerService

        if service == 'keystackWatchdog':
            serviceScript = vars.keystackWatchdogService

        if service == 'keystackSyncTestResults':
            serviceScript = vars.keystackSyncTestResultsService
                                                
        if self.isFromKeystackUI:
            cmd = f'{vars.pythonPath} {serviceScript} -isFromKeystackUI > /dev/null 2>&1 &'
        else:
            cmd = f'{vars.pythonPath} {serviceScript} > /dev/null 2>&1 &'            

        self.writeToServiceLogFile(msgType='info', msg=f'startService: {service}: {cmd} ...')
        
        try:
            print(f'KeystackServices:startService: {serviceScript} ...')
            result = subprocess.call(cmd, shell=True)
        except Exception as errMsg:
            msg = f'Serviceware failed to start {service}: {errMsg}'
            print(f'KeystackServices:startService: {serviceScript} error: {errMsg} ...')
            self.writeToServiceLogFile(msgType='error', msg=f'startService: {msg}')  
            raise Exception(msg)
    
        self.isServiceRunning(service)

    def stopService(self, service, showStdout=False):
        """ 
        Parameters
            service: <str>: keystackDeleteLogs|keystackAwsS3
        """ 
        buffer = execSubprocessInShellMode(f'ps -aux | grep {service}', showStdout=showStdout)
        for line in buffer[1].split('\n'):
            match = re.search(f'[^ ]+ *([0-9]+).*{service}.py', line)
            if match:
                self.setService(service)
                self.writeToServiceLogFile(msgType='info', msg=f'stopService: Kill {service} service PID: {match.group(1)}')
                print(f'KeystackServices:stopService: {service} ...')
                execSubprocessInShellMode(f'sudo kill -9 {match.group(1)}', showStdout=showStdout)
                                
    def stopServices(self):
        """ 
        A function to stop all services
        """
        self.stopAwsS3Service()
        
    def restartServices(self):
        """ 
        A function to restart multiple services
        """
        self.restartAwsS3()
     
    def restartService(self, service):
        print(f'\nKeystackServices:restartService: {service} ...')
        self.stopService(service)
        self.startService(service)
                       
    def restartAwsS3(self):
        self.setService('awsS3')
        if self.isServiceRunning('keystackAwsS3'):
            self.stopAwsS3Service()
            
        self.startAwsS3Service()
        self.isServiceRunning('keystackAwsS3')
        
    def startAwsS3Service(self):
        self.startService('keystackAwsS3')
        
    def stopAwsS3Service(self):
        self.setService('keystackAwsS3')
        self.stopService('keystackAwsS3')

    def restartLogsService(self):
        self.setService('keystackDeleteLogs')
        self.stopLogsService()
        self.startLogsService()
        
    def startLogsService(self):
        self.startService('keystackDeleteLogs')
        
    def stopLogsService(self):
        self.setService('keystackDeleteLogs')
        self.stopService('keystackDeleteLogs')
                    
                                            
if __name__ == "__main__":
    obj = KeystackServices()
    obj.stopServices()
    obj.startAwsS3Service()
    
    
