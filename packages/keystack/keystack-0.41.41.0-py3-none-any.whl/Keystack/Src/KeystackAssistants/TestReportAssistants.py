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

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)

@dataclasses.dataclass
class TestReportAssistant:
    keystackObj: object
    
    def createTestReport(self):
        """ 
        Note:
            Most of these properties were created in the Main() class in the generateReport() 
            function using the self.keystackObj.playbookObj, which in this Playbook class.
        """
        # overallSummary: {'group': 'Default', 'processId': 1725064, 'keystackVersion': '0.10.0', 'user': 'hgee', 'playbook': '/opt/KeystackTests/Playbooks/Samples/pythonSample.yml', 'loginCredentialKey': None, 'trackResults': False, 'abortTestOnFailure': False, 'includeLoopTestPassedResults': False, 'testAborted': False, 'stageFailAborted': False, 'status': 'Completed', 'result': None, 'exceptionErrors': [], 'warnings': [], 'sessionId': 4231, 'topLevelResultFolder': '/opt/KeystackTests/Results/GROUP=Default/PLAYBOOK=Samples-pythonSample/06-29-2023-17:34:42:321074_4231', 'started': '2023-06-29 17:34:42.313590', 'stopped': '', 'testDuration': '', 'totalCases': 0, 'totalFailures': 0, 'totalPassed': 0, 'totalFailed': 0, 'totalSkipped': 0, 'totalTestAborted': 0, 'totalKpiPassed': 0, 'totalKpiFailed': 0, 'pausedOnError': None, 'holdEnvsIfFailed': False, 'stages': {'Test': {'result': None, 'tasks': []}}, 'runList': [], 'notes': []}            

        try:
            self.keystackObj.keystackLogger.debug()
            if os.path.exists(GlobalVars.customizeTestReportFile):
                customizeTestReportFile = readYaml(GlobalVars.customizeTestReportFile)
                
            self.keystackObj.stopTime = datetime.datetime.now()
            self.keystackObj.stopTime.strftime('%m-%d-%Y %H:%M:%S')
            self.keystackObj.duration = str((self.keystackObj.stopTime - self.keystackObj.startTime))

            if customizeTestReportFile.get('reportSubject', None) not in ['None', None, '']:
                reportSubject = customizeTestReportFile['reportSubject']
            else:
                # Default report subject
                reportSubject = f"Keystack Report: PipelineId:{self.keystackObj.sessionId}   Result:{self.keystackObj.result}\n"
                reportSubject += f"{' ':17s}TotalCases:{self.keystackObj.totalCases}  TotalPassed:{self.keystackObj.overallSummaryData['totalPassed']}  TotalFailed:{self.keystackObj.overallSummaryData['totalFailed']}\n"
                reportSubject += f"{' ':17s}SkippedTestcases:{self.keystackObj.overallSummaryData['totalSkipped']}  AbortedTestcases:{self.keystackObj.overallSummaryData['totalTestAborted']} AbortedStages:{len(self.keystackObj.abortedStages)}"
                    
            # Allow users to customize the email subject line with these replacement values
            for replace in [{'{{datetime}}':         getTimestamp(includeMillisecond=False)},
                            {'{{totalPassed}}':      str(self.keystackObj.overallSummaryData['totalPassed'])},
                            {'{{totalFailed}}':      str(self.keystackObj.overallSummaryData['totalFailed'])},
                            {'{{totalTestAborted}}': str(self.keystackObj.overallSummaryData['totalTestAborted'])},
                            {'{{totalTestcases}}':   str(self.keystackObj.totalCases)},
                            {'{{totalSkipped}}':     str(self.keystackObj.overallSummaryData['totalSkipped'])},
                            {'{{result}}':           str(self.keystackObj.result)},
                            {'{{pipelineId}}':       str(self.keystackObj.sessionId)}]:
                
                reportSubject = reportSubject.replace(list(replace.keys())[0], list(replace.values())[0])    
                
            self.keystackObj.subjectLine = reportSubject
            useDefaultReportHeadings = True
            reportHeadingAdditions = ''
            
            if self.keystackObj.abortStageOnFailure:
                if self.keystackObj.abortedStages:
                    abortedStageMsg = f'Aborted Stages: ' 
                    for stage in self.keystackObj.abortedStages:
                        abortedStageMsg += f'{stage} '
                else:
                    abortedStageMsg = '' 
                                    
            if self.keystackObj.skippedStages:
                skippedStages = f'Skipped Stages: ' 
                for stage in self.keystackObj.skippedStages:
                    skippedStages += f'{stage} '
                                        
            # Additional report header tags from playbooks
            if self.keystackObj.playbookGlobalSettings.get('reportHeadingAdditions', None) not in [None, 'None', '']:
                for pairValue in self.keystackObj.playbookGlobalSettings['reportHeadingAdditions']:
                    for key,value in pairValue.items():
                        reportHeadingAdditions += f'{key}: {value}\n'

            if customizeTestReportFile.get('reportHeadings', None) not in [None, 'None', '']:
                useDefaultReportHeadings = False
                self.keystackObj.overallTestReportHeadings  = customizeTestReportFile['reportHeadings']
                
                for replace in [{'{{totalTestcases}}':   str(self.keystackObj.totalCases)},
                                {'{{totalPassed}}':      str(self.keystackObj.overallSummaryData['totalPassed'])}, 
                                {'{{totalFailed}}':      str(self.keystackObj.overallSummaryData['totalFailed'])},
                                {'{{totalSkipped}}':     str(self.keystackObj.overallSummaryData['totalSkipped'])}, 
                                {'{{totalTestAborted}}': str(self.keystackObj.overallSummaryData['totalTestAborted'])},
                                {'{{startTime}}':        str(self.keystackObj.startTime)},
                                {'{{stopTime}}':         str(self.keystackObj.stopTime)},
                                {'{{duration}}':         str(self.keystackObj.duration)},
                                {'{{playbook}}':         self.keystackObj.playbookName},
                                {'{{testResultPath}}':   self.keystackObj.timestampFolder},
                                {'{{reportHeadingAdditions}}': reportHeadingAdditions},
                                {'{{pipelineId}}':             str(self.keystackObj.sessionId)}
                                ]:
                    
                    self.keystackObj.overallTestReportHeadings = self.keystackObj.overallTestReportHeadings.replace(list(replace.keys())[0], list(replace.values())[0])
            
            if useDefaultReportHeadings:
                # Default report header
                self.keystackObj.overallTestReportHeadings =  f"Playbook Executed: {self.keystackObj.playbookName}\n"
                self.keystackObj.overallTestReportHeadings += f'Test Result Path: {self.keystackObj.timestampFolder}\n'
                self.keystackObj.overallTestReportHeadings += f'Start Time: {self.keystackObj.startTime}\n'
                self.keystackObj.overallTestReportHeadings += f'Stop Time: {self.keystackObj.stopTime}\n'
                self.keystackObj.overallTestReportHeadings += f'Duration: {self.keystackObj.duration}\n'
            
            if self.keystackObj.putFailureDetailsAfterResults:
                combineFailureDetails = ''
                for eachFailure in self.keystackObj.putFailureDetailsAfterResults:
                    for testcase, failureDesc in eachFailure.items():
                        combineFailureDetails += f'{failureDesc}\n'

                self.keystackObj.reportBody =  f'{self.keystackObj.subjectLine}\n\n'
                if self.keystackObj.abortStageOnFailure:
                    self.keystackObj.reportBody += f'{" ":17s}{abortedStageMsg}\n'
                    
                if self.keystackObj.skippedStages:
                    self.keystackObj.reportBody += f'{" ":17s}{skippedStages}\n' 
                                        
                self.keystackObj.reportBody += f'{self.keystackObj.overallTestReportHeadings}\n'     
                self.keystackObj.reportBody += f'{self.keystackObj.overallTestReport}\n\n'
                self.keystackObj.reportBody += f'Failure Details:\n\n{combineFailureDetails}\n'
            else:
                self.keystackObj.reportBody =  f'{self.keystackObj.subjectLine}\n'
                if self.keystackObj.abortStageOnFailure:
                    self.keystackObj.reportBody += f'{" ":17s}{abortedStageMsg}\n'

                if self.keystackObj.skippedStages:
                    self.keystackObj.reportBody += f'{" ":17s}{skippedStages}\n'

                self.keystackObj.reportBody += f'\n{self.keystackObj.overallTestReportHeadings}\n' 
                self.keystackObj.reportBody += f'{self.keystackObj.overallTestReport}'        
            writeToFileNoFileChecking(f'{self.keystackObj.timestampFolder}/testReport', self.keystackObj.reportBody, mode='w')

            print(f'\n{self.keystackObj.reportBody}')

            self.keystackObj.overallSummaryData.update({'stopped': str(self.keystackObj.stopTime), 
                                                        'testDuration': self.keystackObj.duration,
                                                        'totalCases': self.keystackObj.totalCases,
                                                        'result': self.keystackObj.result, 
                                                        'status': self.keystackObj.overallSummaryData['status']})  
            
            writeToJson(self.keystackObj.overallSummaryDataFile, data=self.keystackObj.overallSummaryData, mode='w', retry=3)
        except Exception as errMsg:
            raise Exception(f'CreateTestReport: None. Test did not run successfully.\nError: {errMsg}')
        

    def recordResults(self):
        """ 
        Track results for graphing
        """
        if self.keystackObj.trackResults is False or self.debug:
            return

        resultDataHistoryPath = f'{GlobalVars.resultHistoryPath}/{self.playbookName}'
        lockFile = f'{resultDataHistoryPath}/lock'
        
        if Path(resultDataHistoryPath).exists() is False:
            mkdir2(resultDataHistoryPath, stdout=False)
            chownChmodFolder(resultDataHistoryPath, self.user, GlobalVars.userGroup, stdout=False)
        
        daysToKeepData = keystackSettings.get('trackResultsForHowManyDays', 14)
        now = datetime.datetime.now()
        nowStringFormat = now.strftime('%m-%d-%Y %H:%M:%S')
        format = '%m-%d-%Y %H:%M:%S'
        resultData = dict()
        
        columnHeaders = ['dateTime', 'totalTestcases', 'result', 'totalPassed', 'totalFailed',
                         'totalAborted', 'totalSkipped', 'totalKpiPassed', 'totalKpiFailed']

        resultData = {'dateTime':       nowStringFormat, 
                      'totalTestcases': str(self.totalCases),
                      'result':         self.result, 
                      'totalPassed':    str(self.overallSummaryData['totalPassed']), 
                      'totalFailed':    str(self.overallSummaryData['totalFailed']),
                      'totalAborted':   str(self.overallSummaryData['totalTestAborted']),
                      'totalSkipped':   str(self.overallSummaryData['totalSkipped']),
                      'totalKpiPassed': str(self.overallSummaryData['totalKpiPassed']),
                      'totalKpiFailed': str(self.overallSummaryData['totalKpiFailed']),
                      }
                    
        selfRemovingLockCounter = 1
        breakLockCount = 10
        while True:
            try:
                if Path(lockFile).exists() and selfRemovingLockCounter <= breakLockCount:
                    print(f'recordResults: Track file is locked. Wait {selfRemovingLockCounter}/{breakLockCount} secs')
                    time.sleep(1)
                    selfRemovingLockCounter += 1
                    
                if Path(lockFile).exists() is False and selfRemovingLockCounter <= breakLockCount:
                    execSubprocessInShellMode(f'touch {lockFile}', showStdout=False)
                    execSubprocessInShellMode(f'chown {GlobalVars.user}:{GlobalVars.userGroup} {lockFile}', showStdout=False)
                    execSubprocessInShellMode(f'chmod 770 {lockFile}', showStdout=False)
                    selfRemovingLockCounter = 1
                    break

                if Path(lockFile).exists() and selfRemovingLockCounter == breakLockCount:
                    # Just take over and remove the lock when done
                    print(f'recordResults: {selfRemovingLockCounter}/{breakLockCount}: Taking over the lock for playbook: {self.playbookName}')
                    selfRemovingLockCounter = 1
                    break  
                
            except:
                # In case there is an I/O error clash between multiple instances 
                # trying to read/write to the same csv file
                time.sleep(1)
                continue        

        # Each playbook folder should only have one .csv file
        currentCsvFile = glob(f'{resultDataHistoryPath}/*.csv')
        
        if not currentCsvFile:
            # Initiate a new CSV file
            currentCsvFile = f'{resultDataHistoryPath}/{self.keystackObj.playbookName}.csv'
            
            # Create the header column names
            with open(currentCsvFile, 'w') as dataFileObj:
                writer = csv.DictWriter(dataFileObj, fieldnames=columnHeaders)
                writer.writeheader()  

        if type(currentCsvFile) is list:
            currentCsvFile = currentCsvFile[0] 
                    
        # Append the new result to the current csv file
        with open(currentCsvFile, 'a') as fileObj:
            writer = csv.DictWriter(fileObj, fieldnames=columnHeaders)
            writer.writerow(resultData)

        with open(currentCsvFile, 'r') as fileObj:    
            reader = csv.reader(fileObj)
            keepRowsList = []
            removeRowList = []
            
            for rowNumber, row in enumerate(reader, start=0):
                if rowNumber == 0: 
                    continue
    
                datetimeObj = datetime.datetime.strptime(row[0], format)
                deltaObj = now.date() - datetimeObj.date()
                days = deltaObj.days
                if days <= int(daysToKeepData):
                    # Keep the rows that are within the specified days to keep
                    keepRowsList.append(row)
                else:
                    removeRowList.append(row)
                    
        if len(removeRowList) > 0:
            # The next CSV file
            randomNumber = random.sample(range(1,1000), 1)[0]
            self.updateCsvDataFile = f'{resultDataHistoryPath}/{self.keystackObj.playbookName}_{randomNumber}.csv'

            with open(self.updateCsvDataFile, 'w') as fileObj:
                writer = csv.writer(fileObj)
                writer.writerow(columnHeaders)
                writer.writerows(keepRowsList)
            
            os.remove(currentCsvFile)
        else:
           self.updateCsvDataFile = currentCsvFile
        
        execSubprocessInShellMode(f'chown :Keystack {self.updateCsvDataFile}', showStdout=False)
        
        try:     
            os.remove(lockFile)
        except:
            # It is ok to error out because the while loop will remove the lock file
            # after the default timer
            pass
        
        # Clean up: Get a list of known Playbooks and remove all non-existing playbooks from
        # the /opt/KeystackSystems/resultDataHistory folder
        