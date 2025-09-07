""" 
Run AWS S3 upload in background.

Usage:
   1> python3 keystackAwsS3.py > /dev/null &
   2> Run at startup: Add in crontab: @reboot <user> python /Keystack/Services/keystackAwsS3.py
   3> Subprocess #1
   
   To enable debug mode:
       - In folder /opt/KeystackSystem/ServicesStagingArea
       - touch file: debuggingAwsS3
       - Remove file when done
"""

import sys, re, os, traceback, threading, time, subprocess
from glob import glob
from shutil import rmtree

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(currentDir.replace('/Services', ''))

from keystackUtilities import mkdir2, updateLogFolder, execSubprocessInShellMode, readJson, readYaml
from Serviceware import KeystackServices, vars
    
fileLock = threading.Lock()
      
if len(sys.argv) > 1:
    isFromKeystackUI = True
else:
    isFromKeystackUI = False

def getLoginCredentials(credentialYmlFile, loginCredentialKey):
    if os.path.exists(credentialYmlFile) == False:
        raise Exception(f'Login credentials file not found: {credentialYmlFile}.')
    
    loginCredentialObj = readYaml(credentialYmlFile)
    loginCredentials = loginCredentialObj[loginCredentialKey]      
    return loginCredentials


class ProgressPercentage(object):
    """ 
    For AWS S3 callback when uploading files
    
    s3.upload_file(
        'FILE_NAME', 'BUCKET_NAME', 'OBJECT_NAME',
        Callback=ProgressPercentage('FILE_NAME')
    )
    """  
    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename, self._seen_so_far, self._size,
                    percentage))
            
            # Too chatty, but leave behind for debugging purpose
            # writeToServiceLogFile("\nawsS3Upload Progress:  %s -> %s / %s  (%.2f%%)\n" % (
            #         self._filename, self._seen_so_far, self._size,
            #         percentage))
            
            sys.stdout.flush()
    

class AwsS3Upload():
    def __init__(self, uploadFile=None, playbookName=None, sessionId=None, logFile=None, accessKey=None, 
                 secretKey=None, region=None, bucketName=None, *args, **kwargs):

        self.playbookName = playbookName
        self.sessionId = sessionId
        self.awsS3Service = awsS3ServiceObj
        self.uploadFile = uploadFile
        self.logFile = logFile
        self.accessKey = accessKey
        self.secretKey = secretKey
        self.region = region
        self.bucketName = bucketName

        if isDebugEnabled:
            awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'accessKey={accessKey}  secretKey={secretKey}', logFile=logFile, fileLock=fileLock)
            
        # AccessKey/SecretKey: Could be static in a secret file or exported in memory or in a SSM case, it doesn't require it.
        #                      The ssm method is by best effort since it doesn't require passing in an accessKey.
        if accessKey in [None, 'None', 'none']:
            self.accessKey = os.getenv("AWS_ACCESS_KEY_ID", None)
            
        if secretKey in [None, 'None', 'none']:  
            self.secretKey = os.getenv("AWS_SECRET_ACCESS_KEY", None)
            
        if region in [None, 'None', 'none']:  
            self.region = os.getenv("AWS_DEFAULT_REGION", None)
        
        if isDebugEnabled:
            awsS3ServiceObj.writeToServiceLogFile(msgType='debug',
                                                  msg=f'AWS_ACCESS_KEY_ID={self.accessKey}  AWS_SECRET_ACCESS_KEY={self.secretKey} AWS_DEFAULT_REGION={self.region}', 
                                                  playbookName=self.playbookName, sessionId=self.sessionId, logFile=logFile, fileLock=fileLock)
                
        if os.path.exists(vars.keystackServiceLogsFolder) == False:
            try:
                mkdir2(vars.keystackServiceLogsFolder)
            except Exception as errMsg:
                self.awsS3Service.writeToServiceLogFile(msgType='error', msg=f'AwsS3Upload init: \n{traceback.format_exc(None, errMsg)}', 
                                                        playbookName=self.playbookName, sessionId=self.sessionId, fileLock=fileLock)
                return False
                   
    def connect(self, accessKey=None, secretKey=None, region=None, bucketName=None):
        """ 
        Each upload requires a new connection because AWS is not thread safe.
        """
        try:
            if isDebugEnabled:
                self.awsS3Service.writeToServiceLogFile(msgType='debug',
                                                           msg='Conecting to S3 service ...', 
                                                           logFile=self.logFile, fileLock=fileLock, showOutput=True)
            
            session = boto3.Session(aws_access_key_id=accessKey, aws_secret_access_key=secretKey, region_name=region)
            # s3 | ssm
            self.s3 = session.client('s3')
            
            if isDebugEnabled:
                self.awsS3Service.writeToServiceLogFile(msgType='debug',
                                                           msg='Successfully conected to S3 service ...', 
                                                           logFile=self.logFile, fileLock=fileLock, showOutput=True)
                
        except (ClientError, Exception) as errMsg:
            if isDebugEnabled:
                self.awsS3Service.writeToServiceLogFile(msgType='debug',
                                                           msg='Failed to connect to S3 service ...', 
                                                           logFile=self.logFile, fileLock=fileLock, showOutput=True)
            return False

    def pushToS3(self, sourceFile, bucketName):
        """ 
        Configure S3 bucket to grant public access to files.
        In S3 Permissions, add:
        
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicRead",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetObject",
                        "s3:GetObjectVersion"
                    ],
                    "Resource": "arn:aws:s3:::<Bucket Name>/*"
                }
            ]
        }
        """
        # sourceFile: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-22-2024-02:29:43:159370_6033/STAGE=Teardown_TASK=teardown_ENV=DOMAIN=Communal-demo1/taskSummary.json
        match = re.search('(DOMAIN=.+/PLAYBOOK=.*)', sourceFile)
        if match is None:
            self.awsS3Service.writeToServiceLogFile(msgType='error', msg=f'pushToS3: sourceFile did not find PLAYBOOK.* pattern: {sourceFile}',
                                                    playbookName=self.playbookName, sessionId=self.sessionId, logFile=self.logFile, fileLock=fileLock)
            return False
        
        destFile = match.group(1)
        exitCounter = 3
        counter = 1
        while True:
            try:
                with open(sourceFile, 'rb') as fileObj:
                    # Use put_object so there is json response with results
                    # result = self.s3.put_object(Bucket=os.environ['keystack_awsS3BucketName'],
                    #                             Key=destFile, Body=fileObj)
                    result = self.s3.put_object(Bucket=bucketName, Key=destFile, Body=fileObj) 
                                   
                if counter <= exitCounter and result['ResponseMetadata']['HTTPStatusCode'] != 200:
                    counter += 1
                    if self.awsS3Service.debugEnabled():
                        self.awsS3Service.writeToServiceLogFile(msgType='failed', msg=f'pushToS3: S3 upload failed on {counter}/{exitCounter}x: {sourceFile}: Retrying ...', logFile=self.logFile, playbookName=self.playbookName, sessionId=self.sessionId, fileLock=fileLock)
                        
                    time.sleep(1)
                    continue
                
                if counter <= exitCounter and result['ResponseMetadata']['HTTPStatusCode'] == 200:
                    #if debug:
                    #    self.awsS3Service.writeToServiceLogFile(msgType='debug', msg=f'http status code = 200: {result["ResponseMetadata"]}', 
                    #                                            playbookName=self.playbookName, sessionId=self.sessionId, fileLock=fileLock) 
                    return True
                
                if counter == exitCounter and result['ResponseMetadata']['HTTPStatusCode'] != 200:
                    self.awsS3Service.writeToServiceLogFile(msgType='failed', msg=f'pushToS3: S3 upload failed after {counter}/{exitCounter} retries: {sourceFile}',
                                                            playbookName=self.playbookName, sessionId=self.sessionId,logFile=self.logFile, fileLock=fileLock)
                    return False
                
                #url = self.getFileObjectUrl(destFile, bucketName)
                
            except (ClientError, Exception) as errorMsg:
                uploadSuccess = False
                self.awsS3Service.writeToServiceLogFile(msgType='error', msg=f'\npushToS3 exception: {traceback.format_exc(None, errorMsg)}', 
                                                        playbookName=self.playbookName, sessionId=self.sessionId, logFile=self.logFile, fileLock=fileLock)
                # Stop trying. Let the while loop retry.
                self.awsS3Service.writeToServiceLogFile(msgType='error', msg=f'pushToS3: AWS S3 LOGIN CONNECTION FAILED: {traceback.format_exc(None, errorMsg)}', 
                                                        playbookName=self.playbookName, sessionId=self.sessionId, fileLock=fileLock, logFile=self.logFile)
                self.awsS3Service.writeToServiceLogFile(msgType='error', msg=f'pushToS3: AWS S3 LOGIN CONNECTION FAILED: {traceback.format_exc(None, errorMsg)}', 
                                                        playbookName=self.playbookName, sessionId=self.sessionId, 
                                                        fileLock=fileLock, logFile=awsS3ServiceObj.serviceLogFile)
                pid = os.getpid()
                execSubprocessInShellMode(f'sudo kill {pid}')
                sys.exit(1)


    def getFileObjectUrl(self, destFile, bucketName):
        """ 
        Each test session has its own logFile
        """
        # URL: https://hubertgee-bucket.s3.amazonaws.com/PLAYBOOK%3DL3Testing/05-07-2022-09%3A03%3A47%3A047488_s3Url/STAGE%3DTest_MODULE%3DCustomPythonScripts_ENV%3DL3Testing/isis/test_summary.json?AWSAccessKeyId=AKIxxxdddd&Signature=HA5hWE5CqnISd%2FE%3D&Expires=1651943032
        url = self.s3.generate_presigned_url(ClientMethod="get_object", ExpiresIn=0,
                                             Params={"Bucket": bucketName, "Key": destFile})
        
        # Remove the AWSAccessKeyId, Signature and Expires from the URI
        url = url.split('?')[0]
        return url        

    def upload(self):
        """
        Note: 
            # S3 is not thread safe. Must open a connection for each upload.
            # Each call to upload() will make a new connection.
             
        uploadFilePath = /full/path/<file to upload>
        destFilename   = The file name in the bucket
        bucektName     = The AWS S3 bucket name: bucket-name
        accessKey      = 'AKIARN4JPYEIUONIXXXX'
        secretKey      = 'ACvmw9EugnETo9KuY4TMobRJTV0RK7Bc/bXXXXXX'
        region         = 'us-west-1'
        
        Note: Boto3 check these env variables for credentials:
                AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN
                
        AWS accessKey/secretKey usage best practice: 
            If you want to interoperate with multiple AWS SDKs (e.g Java, Javascript, Ruby, PHP, .NET, AWS CLI, Go, C++), 
            use the shared credentials file (~/.aws/credentials). By using the shared credentials file, you can use a single 
            file for credentials that will work in all AWS SDKs
        """
        removeFolder = True
        removeFile = True
        isDebugEnabled = self.awsS3Service.debugEnabled()
        currentResult = True

        if self.connect(self.accessKey, self.secretKey, self.region, self.bucketName) == False:
            awsS3ServiceObj.writeToServiceLogFile(msgType='info', msg=f'keystackAwsS3 Failed to connect to AWS. Resolve login issue. New test will attempt to restart this service automatically.', playbookName=self.playbookName, sessionId=self.sessionId, logFile=self.logFile, fileLock=fileLock)
            return False
        
        if os.path.isdir(self.uploadFile):
            if isDebugEnabled:
                self.awsS3Service.writeToServiceLogFile(msgType='debug', msg=f'Uploading folder to S3 bucket {self.bucketName}: {self.uploadFile}',
                                                        playbookName=self.playbookName, sessionId=self.sessionId, logFile=self.logFile, fileLock=fileLock)
               
            for root,dirs,files in os.walk(self.uploadFile):
                if files:
                    for eachUploadFile in files:                         
                        result = self.pushToS3(f'{root}/{eachUploadFile}', self.bucketName)
                        if result == False:
                            currentResult = False
                                                            
        if os.path.isfile(self.uploadFile):
            if isDebugEnabled:
                self.awsS3Service.writeToServiceLogFile(msgType='debug', msg=f'Uploading file to S3 bucket {self.bucketName}: {self.uploadFile}',
                                                        playbookName=self.playbookName, sessionId=self.sessionId, logFile=self.logFile, fileLock=fileLock)
                
            currentResult = self.pushToS3(self.uploadFile, self.bucketName)

        return currentResult
    

class MainThread(threading.Thread):
    """ 
    Intercept thread start so we could get return values
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # child class's variable, not available in parent.
        self._return = None 
 
    def run(self):
        """
        The original run method does not return value after self._target is run.
        This child class adds a return value.
        """
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
 
    def join(self, *args, **kwargs):
        """
        Join normally like the parent class, but added a return value which
        the parent class join method does not have. 
        """
        super().join(*args, **kwargs)
        return self._return
  
  
class Danger:
    # Track failures and delay continuous loop
    failedCount = 0
    
          
# If Docker: The container will automatically launch the keystackAwsS3.py script to run in the background 
#            with the parameter isFromKeystackUI
awsS3ServiceObj = KeystackServices(typeOfService='keystackAwsS3', isFromKeystackUI=isFromKeystackUI)

while True:
    if Danger.failedCount == 5:
        awsS3JsonFilesRemainders = len(glob(f'{awsS3ServiceObj.stagingFolder}/*'))
        if awsS3JsonFilesRemainders > 0:
            awsS3ServiceObj.writeToServiceLogFile(msgType='error', msg=f'{awsS3JsonFilesRemainders} remaining files cannot get uploaded to S3',
                                                  logFile=awsS3ServiceObj.serviceLogFile, fileLock=fileLock)
            # Don't keep looping and build up a large log file.
            # Perform once a hour.  Otherwise, kill the service process id and let it restart automatically or restart the service manually.
            time.sleep(18000)
        else:
            Danger.failedCount = 0
                        
    threadList = []
    playbookName = None
    goToWork = 0
    isDebugEnabled = awsS3ServiceObj.debugEnabled()
    
    # Gather all files and folders in the staging folder.
    # Each test has its own timestamp folder    
    # Ex: f'{Serviceware.vars.awsS3StagingFolder}/{playbookName}-{sessionId}-{getTimestamp()}.json'
    # Old format: /opt/KeystackSystem/ServicesStagingArea/AwsS3Uploads/PLAYBOOK=Samples-pythonSample_04-13-2023-14:29:34:960688.json
    # New format: /opt/KeystackSystem/ServicesStagingArea/AwsS3Uploads/PLAYBOOK=DOMAIN=Communal-Samples-advance_04-21-2024-16:25:07:101675.json
    for keystackMessageToUpload in glob(f'{vars.awsS3StagingFolder}/*json'):       
        jsonFilename = keystackMessageToUpload.split('/')[-1]

        try:
            # keystackMessageToUpload: Contains login details created by keystack.py  
            keystackTestResultPathContent = readJson(keystackMessageToUpload)
            
            loginCredentialPath = keystackTestResultPathContent['loginCredentialPath']
            loginCredentialKey = keystackTestResultPathContent['loginCredentialKey']
            loginCredentials = getLoginCredentials(loginCredentialPath, loginCredentialKey)
            # "playbookName": "DOMAIN=Communal-Samples-advance"
            playbookName = keystackTestResultPathContent['playbookName']

            # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-21-2024-16:24:51:867576_awesomeTest
            resultFolderPath = keystackTestResultPathContent['resultsTimestampFolder']
            resultsTimestampFolder = resultFolderPath.split('/')[-1]
            sessionId = resultsTimestampFolder.split('_')[-1]

            # Verify if the results still exists.  If the results don't not exists anymore, remove the aws s3 uploads from the staging area.
            if os.path.exists(resultFolderPath) == False:
                os.remove(keystackMessageToUpload)
                if isDebugEnabled:
                    awsS3ServiceObj.writeToServiceLogFile(msgType='debug',
                                                          msg=f'The results no longer exists. Removing the AWS S3 upload in the staging area: {keystackMessageToUpload}',
                                                          playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
                continue

            # Each job has its own aws-<sessionId> log file
            # Ex: '{Serviceware.vars.keystackServiceLogsFolder}/awsS3-{playbookName}-{sessionId}.json'
            # PLAYBOOK=DOMAIN=Communal-Samples-advance_04-21-2024-16:25:07:101675.json
            logFile = f'{vars.keystackServiceLogsFolder}/PLAYBOOK={playbookName}_{resultsTimestampFolder}.json'
            
            if isDebugEnabled:
                awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'logFile: {logFile}', logFile=logFile,
                                                      playbookName=playbookName, sessionId=sessionId, fileLock=fileLock)
                awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'aws login credential key {loginCredentialKey}',
                                                      playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
                
            if isDebugEnabled:
                awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'keystackMessage: {keystackMessageToUpload}', 
                                                      playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
        
            if os.path.exists(keystackMessageToUpload) == False:
                # Safety check: file doesn't exists
                if isDebugEnabled:
                    awsS3ServiceObj.writeToServiceLogFile(msgType='error', msg=f'File not found, but found in glob: {keystackMessageToUpload}', 
                                                          playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
                continue
            
        except Exception as errMsg:
            awsS3ServiceObj.writeToServiceLogFile(msgType='error', msg=f'aws login credentials: {traceback.format_exc(None,errMsg)}',
                                                  playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
            awsS3ServiceObj.writeToServiceLogFile(msgType='error', msg=f'aws login credentials: {traceback.format_exc(None,errMsg)}',
                                                  playbookName=playbookName, sessionId=sessionId, logFile=awsS3ServiceObj.serviceLogFile, fileLock=fileLock)
            sys.exit(1)
        
        # This is the actual result path in /KeystackTests/Results: 
        # /PLAYBOOK=pythonSample/07-04-2022-18:48:54:244690_4876
        if isDebugEnabled:
            awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'Files in staging area for S3 upload:', 
                                                  playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
            for eachFileWaiting in keystackTestResultPathContent['artifactsPath']:
                awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'\t- Waiting to upload: {eachFileWaiting}', 
                                                      playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
        
        # Upload the actual result timestamp folders
        for eachFileOrFolderToUpload in keystackTestResultPathContent['artifactsPath']:   
            # S3 is not thread safe. Must open a connection for each upload.
            # Each call to upload() will make a new connection
            # These AWS login credentials already been verified by keystack.py getLoginCredentials()
            # artifactsPath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-21-2024-16:24:51:867576_awesomeTest/testReport
            newThreadObj = AwsS3Upload(eachFileOrFolderToUpload, playbookName, sessionId, logFile,
                                       loginCredentials['awsAccessKey'], 
                                       loginCredentials['awsSecretKey'], 
                                       loginCredentials['awsRegion'], 
                                       loginCredentials['awsS3BucketName'])

            threadObj = MainThread(target=newThreadObj.upload, name=f'PATH={keystackMessageToUpload}_PLAYBOOK={playbookName}_{resultsTimestampFolder}')       
            threadList.append(threadObj)

            if goToWork == 0:
                goToWork = 1
                        
    if goToWork:
        for eachThread in threadList:
            if isDebugEnabled:
                # PATH=/opt/KeystackSystem/ServicesStagingArea/AwsS3Uploads/PLAYBOOK=Samples-pythonSample_04-13-2023-14:45:37:817768.json_PLAYBOOK=Samples-pythonSample_04-13-2023-14:45:33:977187_hgee13
                regexpMatch = re.search(f'PATH=.+json_PLAYBOOK=DOMAIN=(.+)_([0-9]+-[0-9]+-[0-9]+-[0-9]+:[0-9]+:[0-9]+:[0-9]+.+)', eachThread.name)
                if regexpMatch:
                    playbookName = regexpMatch.group(1)
                    timestamp    = regexpMatch.group(2)
                    logFile = f'{vars.keystackServiceLogsFolder}/PLAYBOOK={playbookName}_{timestamp}.json'
                    awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'Starting thread: {eachThread.name}', 
                                                        playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
            eachThread.start()
        
        # Wait for all threads to complete.
        for eachThread in threadList:
            if isDebugEnabled:
                regexpMatch = re.search(f'PATH=.+json_PLAYBOOK=DOMAIN=(.+)_([0-9]+-[0-9]+-[0-9]+-[0-9]+:[0-9]+:[0-9]+:[0-9]+.+)', eachThread.name)
                playbookName = regexpMatch.group(1)
                timestamp    = regexpMatch.group(2)
                logFile = f'{vars.keystackServiceLogsFolder}/PLAYBOOK={playbookName}_{timestamp}.json'
                awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'thread join(): {eachThread.name}', 
                                                      playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock) 
                
            eachThread.join()
                
        while True:
            alive = False
            
            for eachThread in threadList:
                regexpMatch = re.search(f'PATH=(.+json)_PLAYBOOK=DOMAIN=(.+)_([0-9]+-[0-9]+-[0-9]+-[0-9]+:[0-9]+:[0-9]+:[0-9]+.+)', eachThread.name)
                messagePath  = regexpMatch.group(1)
                playbookName = regexpMatch.group(2)
                timestamp    = regexpMatch.group(3)
                sessionId    = timestamp.split('_')[-1]
                logFile = f'{vars.keystackServiceLogsFolder}/PLAYBOOK={playbookName}_{timestamp}.json'

                if eachThread.is_alive():
                    alive = True
                else:
                    if isDebugEnabled:
                        awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'Thread is done: {messagePath}', 
                                                              playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
                
                    # Removed the json message after the upload is done
                    if os.path.exists(messagePath):
                        if isDebugEnabled:
                            awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=f'Removing json msg file: {messagePath}', 
                                                                  playbookName=playbookName, sessionId=sessionId, logFile=logFile, fileLock=fileLock)
                            
                        result = eachThread.join()
                        if result:  
                            os.remove(messagePath)
                        else:
                             Danger.failedCount += 1 
                    
            if alive:
                time.sleep(1)
                continue
                
            if alive == False:
                if isDebugEnabled:
                    awsS3ServiceObj.writeToServiceLogFile(msgType='info', msg=f'All threads are done', logFile=logFile, fileLock=fileLock)
                break

    # Pause to avoid cpu spike
    time.sleep(1)
