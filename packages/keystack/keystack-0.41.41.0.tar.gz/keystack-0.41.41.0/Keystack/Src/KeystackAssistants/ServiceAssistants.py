import os
import datetime
from glob import glob
import time
import csv
import random
from pathlib import Path
from pydantic import Field, dataclasses
from globalVars import GlobalVars
from keystackUtilities import writeToJson, readYaml, getTimestamp, writeToFileNoFileChecking, mkdir2, chownChmodFolder, execSubprocessInShellMode
from Services import Serviceware


@dataclasses.dataclass
class AwsAssistant:
    keystackObj: object
    
    def waitForS3UploadToComplete(self):
        """
        For docker only.
        
        Once the test is done, Keystack container might exit immediately 
        while the S3 transfer was still transferring in the background.
        Need to verify the staging folder until the test results timestamp folder is 
        removed by the keystackAwsS3 background process. Otherwise, S3 will have missing files and folders.
        """
        # AWS S3 login credentials could be failing. Don't keep logging.
        # User must restore login issue and restart the keystackAwsS3 services manually.
        if self.keystackObj.awsS3ServiceObj.isServiceRunning('keystackAwsS3') is False:
            return
        
        self.keystackObj.keystackLogger.debug()
        filesToUpload = glob(f'{Serviceware.vars.awsS3StagingFolder}/*')
        self.keystackObj.awsS3ServiceObj.writeToServiceLogFile(msgType='info', msg=f'waitForS3UploadToComplete: {filesToUpload}',
                                                   playbookName=self.keystackObj.playbookName, sessionId=self.keystackObj.sessionId)
                        
        selfExitCounter = 1800
        counter = 0
        while True:
            currentAwsS3UploadFolder = glob(f'{Serviceware.vars.awsS3StagingFolder}/*')
            
            # S3 copy is not done as long as files exist in the staging folder  
            if counter < selfExitCounter and len(currentAwsS3UploadFolder) == 0:
                self.keystackObj.awsS3ServiceObj.writeToServiceLogFile(msgType='info', msg=f'waitForS3UploadToComplete: Done',
                                                           playbookName=self.keystackObj.playbookName, sessionId=self.keystackObj.sessionId)
                return 
            
            if counter < selfExitCounter and len(currentAwsS3UploadFolder) > 0:
                counter += 1
                time.sleep(1)
            
            if counter == selfExitCounter and len(currentAwsS3UploadFolder) > 0:
                # TODO: Write problem to /KeystackTests/KeystackSystem/Logs/awsS3ServiceLogs
                self.keystackObj.awsS3ServiceObj.writeToServiceLogFile(msgType='info', msg=f'waitForS3UploadToComplete error: It has been {counter}/{selfExitCounter} seconds and S3 transfer is still not done: {Serviceware.vars.awsS3StagingFolder}', playbookName=self.keystackObj.playbookName, sessionId=self.keystackObj.sessionId)
                break
            
     