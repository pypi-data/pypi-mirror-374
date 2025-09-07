import os, re, traceback
from pydantic import Field, dataclasses

from globalVars import GlobalVars
from commonLib import KeystackException
from keystackUtilities import readYaml, readJson, writeToJson
from RedisMgr import RedisMgr

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)

@dataclasses.dataclass
class TestReportAssistant:
    runTaskObj: object
    
    def generateTaskTestReport(self, modulePretestAborted=False, cells=None):
        """
        Generate a "module" test report.
        An overall test report is combined in the Playbook class.executeTest()    
    
        Parameters
           cells <str>: For AirMosaic only
        """
        if self.runTaskObj.debug:
            subjectHeader = 'Debug-Mode: '
        else:
            subjectHeader = ''

        totalSkippedTestcases = 0
        bodyMessage = ''
        self.runTaskObj.jiraFailures = {}
        
        # {keystackSystemPath}/customizeTestReport.yml
        if os.path.exists(GlobalVars.customizeTestReportFile):
            customizeTestReportFile = readYaml(GlobalVars.customizeTestReportFile)
            
        if customizeTestReportFile.get('emailPutFailureDescriptionsAfterResultSummary', None) in ['True', 'true', 'yes']:
            putFailureDescAtEnd = True
        else:
            putFailureDescAtEnd = False
            
        if customizeTestReportFile.get('reportPutFailureDetailsAfterResultSummary', None) in ['True', 'true', 'yes']:
            putFailureDescAtEnd = True
        else:
            putFailureDescAtEnd = False
        
        if modulePretestAborted is False:  
            try:
                totalOuterLoopIterations = int(self.runTaskObj.taskProperties.get('outerLoop', 1))
                index = 0
                
                # For better visibility using string formatting
                longestStringLength = 0
                for tc, cmdLineArgs in self.runTaskObj.testcaseSortedOrderList:
                    # tc: /opt/KeystackTests/Playlist/Demo/Bringups/bringupDut1.yml
                    regexMatch = re.search('(.*(Testcases|Modules)/[^ ]+)/.+', tc)
                    if regexMatch:
                        #shortenPath = tc.split(self.runTaskObj.modulePath)[-1]
                        shortenPath = regexMatch.group(1)
                        if len(shortenPath) > longestStringLength:
                            longestStringLength = len(shortenPath)
                
                # Test Summary
                # Note about totalFailed vs totalFailures:
                #     totalFailed   = testcase failures.
                #     totalFailures = The amount of failures within a testcases.  Uses KPI-Failed
                # /opt/KeystackTests/Results/GROUP=Default/PLAYBOOK=loadcoreSample/11-01-2022-07:27:02:355686_5423/STAGE=LoadCoreTest_MODULE=LoadCore_ENV=loadcoreSample
                
                # /opt/KeystackTests/Results/GROUP=Default/PLAYBOOK=pythonSample/12-03-2022-08:25:28:290086_2733/.Data/ResultsMeta/opt/KeystackTests/Modules/CustomPythonScripts/Samples/Teardowns/teardownDut.yml_1_1
                                
                for outerLoop in range(1, totalOuterLoopIterations+1):
                    for eachTestcase, cmdLineArgs in self.runTaskObj.testcaseSortedOrderList:
                        testcaseName = eachTestcase.split('/')[-1].split('.')[0] 
                        testcaseFileName = eachTestcase.split('/')[-1]
                        testcaseShortenPath = eachTestcase.split(GlobalVars.keystackTestRootPath)[-1]
                        
                        loopTestcaseTotal= self.runTaskObj.testcaseAssist.getLoopTestcaseCount(eachTestcase)
                        for innerLoop in range(1, loopTestcaseTotal+1):
                            testcaseResultsMetaFolder = '/'.join(f'{self.runTaskObj.playbookObj.resultsMetaFolder}{eachTestcase}'.split('/')[:-1])
                            
                            # Consumed by generateTaskTestReport()
                            # testcaseResultsData-10-18-2024-11:43:34:154948_882_debug-/opt/KeystackTests/Playlist/Demo/L2L3_Testcases/bgp.yml_1_1
                            testcaseResultsMetaFile = f'{testcaseResultsMetaFolder}/{testcaseFileName}_{outerLoop}_{innerLoop}'

                            if os.path.exists(testcaseResultsMetaFile):
                                fileSize = os.path.getsize(testcaseResultsMetaFile)
                                if fileSize == 0:
                                    # Most likely a testcase did not run because dependent cases failed
                                    testcase = None
                                else:
                                    testcase = readJson(testcaseResultsMetaFile)
                            else:
                                # Getting here means abortTaskOnFailure=True
                                testcase = None
                                    
                            index += 1
                            count = f'{str(index)}:'
                            
                            try:
                                self.runTaskObj.playbookObj.overallSummaryData['totalKpiPassed'] += len(testcase["passed"])
                                self.runTaskObj.playbookObj.overallSummaryData['totalKpiFailed'] += testcase["totalFailures"]
                            except:
                                # If the testcase is skipped, there is no testcaseIndex.
                                pass
                            
                            if testcase is None:
                                # Getting here means abortTaskOnFailure = True
                                # Remaining tests were skipped
                                self.runTaskObj.taskSummaryData['totalSkipped'] += 1
                                self.runTaskObj.playbookObj.overallSummaryData['totalSkipped'] += 1
                                self.runTaskObj.playbookObj.totalSkipped += 1
                                
                                if customizeTestReportFile.get('reportsummary', None)  not in [None, 'None', '']:
                                    summary = customizeTestReportFile['reportSummary']
                                    
                                    for replace in [{'{{enumerateTestcase}}': str(index)},
                                                    {'{{testcase}}': f'{testcaseShortenPath:{longestStringLength}s}'},
                                                    {'{{result}}': f"{'Skipped':8s}"}, 
                                                    {'{{aborted}}': "No"},
                                                    {'{{kpiPassed}}': ""}, 
                                                    {'{{kpiFailed}}': ""},
                                                    {'{{outerLoopCounter}}': ""}, 
                                                    {'{{innerLoopCounter}}': ""}
                                                    ]:
                                        
                                        summary = summary.replace(list(replace.keys())[0], list(replace.values())[0])
                                        
                                    bodyMessage += f'\t{summary}\n'
                                else:
                                    # Default format: print(f'{var:12s}')
                                    # test might've aborted. testcase == None
                                    if testcase:
                                        bodyMessage += f"\t{count:5s} {'Skipped':8s} {testcaseShortenPath:{longestStringLength}s} {testcase['outerLoop']} {testcase['innerLoop']}: [{testcase['testDuration']}]\n"
                                    else:
                                        bodyMessage += f"\t{count:5s} {'Skipped':8s} {testcaseShortenPath:{longestStringLength}s}\n"
                                                            
                                continue
                            
                            if customizeTestReportFile.get('reportSummary', None) not in [None, 'None', '']:
                                summary = customizeTestReportFile['reportSummary']
                                
                                for replace in [{'{{enumerateTestcase}}': str(index)},
                                                {'{{testcase}}': f'{testcaseShortenPath:{longestStringLength}s}'},
                                                {'{{result}}': f'{testcase["result"]:8s}'}, 
                                                {'{{aborted}}': str(testcase["testAborted"])},
                                                {'{{kpiPassed}}': f'{str(len(testcase["passed"])):2s}'}, 
                                                {'{{kpiFailed}}': f'{str(testcase["totalFailures"]):2s}'},
                                                {'{{outerLoopCounter}}': f'{str(testcase["outerLoop"]):4s}'}, 
                                                {'{{innerLoopCounter}}': f'{str(testcase["innerLoop"]):6s}'}]:
                                    
                                    summary = summary.replace(list(replace.keys())[0], list(replace.values())[0])
                                bodyMessage += f'\t{summary}\n'
                            else:
                                # Default format
                                bodyMessage += f"\t{count:5s} {testcase['result']:10s} {testcaseShortenPath:{longestStringLength}s} {testcase['outerLoop']} {testcase['innerLoop']}: [{testcase['testDuration']}]\n"
                                    
                            # {{testcase}}  {{result}}  {{kpiPassed}}  {{kpiFailed}}  {{aborted}}  {{outerLoopCounter}}  {{innerLoopCounter}}
                            # {{startTime}}  {{stopTime}}  {{duration}}
                            if testcase['result'] == 'Skipped':
                                self.runTaskObj.taskSummaryData['totalSkipped'] += 1
                                self.runTaskObj.playbookObj.overallSummaryData['totalSkipped'] += 1
                                totalSkippedTestcases += 1
                                description = f"{'Skipped:':8s} Stage:{self.runTaskObj.stage}  Task:{self.runTaskObj.task:10s}  Env:{self.runTaskObj.taskProperties['env']}\n\t {testcaseShortenPath:{longestStringLength}s} {testcase['outerLoop']} {testcase['innerLoop']}: [{testcase['testDuration']}]\n"
                                
                                for msg in testcase['failures']:
                                    if putFailureDescAtEnd:
                                        description += f"\t {msg}\n\n"
                                        self.runTaskObj.playbookObj.putFailureDetailsAfterResults.append({testcaseShortenPath: description})
                                    else:
                                        bodyMessage += f"\t   - {msg}\n\n"
                                continue
                                
                            if testcase['testAborted'] == "Yes":
                                description = f"{'Aborted:':8s} Stage:{self.runTaskObj.stage}  Task:{self.runTaskObj.task:10s}  Env:{self.runTaskObj.taskProperties['env']}\n\t {testcaseShortenPath:{longestStringLength}s} {testcase['outerLoop']} {testcase['innerLoop']}   \n"
                                
                                if putFailureDescAtEnd:
                                    for failureMsg in testcase['failures']:
                                        description += f"\t   - {failureMsg}\n"

                                    self.runTaskObj.playbookObj.putFailureDetailsAfterResults.append({testcaseShortenPath: description})
                                else:
                                    for failureMsg in testcase['failures']:
                                        if 'abortTaskOnFailure is set to True. Aborting Test.' in failureMsg:
                                            failureMsg = 'abortTaskOnFailure=True. Aborting Test.\n'
                                        
                                        if failureMsg:    
                                            bodyMessage += f"\t   * {failureMsg}\n"

                                continue
                            
                            if testcase['status'] != 'Completed':
                                bodyMessage += f"{count:5s} Stage:{self.runTaskObj.stage}  Task:{self.runTaskObj.task:10s}  Env:{self.runTaskObj.taskProperties['env']}\n\t {testcase['status']:10s} {testcaseShortenPath:{longestStringLength}s} {testcase['outerLoop']} {testcase['innerLoop']}\n"
                                continue
                            
                            if len(testcase['warnings']) > 0:
                                description = f"{'Warning:':8s} Stage:{self.runTaskObj.stage}  Task:{self.runTaskObj.task:10s}  Env:{self.runTaskObj.taskProperties['env']}\n\t {testcaseShortenPath:{longestStringLength}s} {testcase['outerLoop']} {testcase['innerLoop']}: [{testcase['testDuration']}]\n"
                                
                                for warning in testcase['warnings']:
                                    if putFailureDescAtEnd:
                                        description += f"\t   - Warning: {warning}\n"
                                    else:
                                        bodyMessage += f"\t   - Warning: {warning}\n\n"
                                
                                if putFailureDescAtEnd:
                                    self.runTaskObj.playbookObj.putFailureDetailsAfterResults.append({testcaseShortenPath: description})
                                                                                              
                            if testcase['result'] in ['Failed']:
                                self.runTaskObj.jiraFailures[eachTestcase] = {}
                                jiraBodyHeader =  f'Playbook: {self.runTaskObj.playbookName}\n'
                                jiraBodyHeader += f'Stage: {self.runTaskObj.stage}\n'
                                jiraBodyHeader += f'Module: {self.runTaskObj.task}\n'
                                jiraBodyHeader += f'Env used: {self.runTaskObj.env}\n'
                                result = f'{testcase["result"]}:'

                                description = f"{result:8s} Stage:{self.runTaskObj.stage}  Task:{self.runTaskObj.task}  Env:{self.runTaskObj.taskProperties['env']}\n\t {testcaseShortenPath:{longestStringLength}s} {testcase['outerLoop']} {testcase['innerLoop']}: [{testcase['testDuration']}]\n"

                                if self.runTaskObj.task == 'LoadCore':
                                    for failure in testcase['failures']:
                                        # For LoadCore, data structure: 
                                        #    failures:
                                        #        - ApplicationTrafficGeneral:
                                        #            Bits received/s: Result=failed  ExpectedValue=400000000-500000000  MaxValue=325926120.0
                                        for csvResultFile,values in failure.items():
                                            for kpi,value in values.items():
                                                self.runTaskObj.jiraFailures[eachTestcase].update({'failed': f'{self.runTaskObj.task}:{testcaseName} Env:{self.runTaskObj.env} KPI:{kpi} -> {value}'})
                                                
                                                if putFailureDescAtEnd:
                                                    description += f"\t   - KPI:{kpi} -> {value}\n"
                                                else:
                                                    bodyMessage += f"\t   - KPI:{kpi} -> {value}\n"

                                    # Show the passed KPIs also for better understanding of the test failures
                                    if putFailureDescAtEnd:
                                        description += f"\n\t   Passed KPIs:\n"
                                    else:
                                        bodyMessage += f"\n\t   Passed KPIs:\n"
                                        
                                    for passed in testcase['passed']:
                                        for csvResultFile,values in passed.items():
                                            for kpi,value in values.items():
                                                if putFailureDescAtEnd:
                                                    description += f"\t\t- KPI:{kpi} -> {value}\n"
                                                else:
                                                    bodyMessage += f"\t\t- KPI:{kpi} -> {value}\n"
                                                    
                                    if putFailureDescAtEnd:
                                        self.runTaskObj.playbookObj.putFailureDetailsAfterResults.append({testcaseShortenPath: description})
                                    
                                elif self.runTaskObj.task == 'AirMosaic':
                                    for failure in testcase['failures']:
                                        # For AirMosaic, data structure: 
                                        #    failures:
                                        #        - Registration Request: Result=failed ExpectedValue==1  ReceivedMaxValue=3
                                        #        - Registration Complete: Result=failed ExpectedValue==1  ReceivedMaxValue=0
                                        for kpi,value in failure.items():
                                            self.runTaskObj.jiraFailures[eachTestcase].update({'failed': f'{self.runTaskObj.task}:{testcaseName} Env:{self.runTaskObj.env} KPI:{kpi} -> {value}'})
                                            
                                            if putFailureDescAtEnd:
                                                description += f"\t   - KPI:{kpi} -> {value}\n"
                                            else:
                                                bodyMessage += f"\t   - KPI:{kpi} -> {value}\n"
                                        
                                    # Show the passed KPIs also for better understanding of the test failures
                                    if putFailureDescAtEnd:
                                        description += f"\n\t     Passed KPIs:\n"
                                    else:
                                        bodyMessage += f"\n\t     Passed KPIs:\n"
                                        
                                    for passed in testcase['passed']:
                                        for kpi,value in passed.items():
                                            if putFailureDescAtEnd:
                                                description += f"\t\t- KPI:{kpi} -> {value}\n"
                                            else:
                                                bodyMessage += f"\t\t- KPI:{kpi} -> {value}\n"
                                    
                                    if putFailureDescAtEnd:        
                                        self.runTaskObj.playbookObj.putFailureDetailsAfterResults.append({testcaseShortenPath: description})
                                    
                                else:
                                    for failure in testcase['failures']:
                                        self.runTaskObj.jiraFailures[eachTestcase].update({'failed': f"{self.runTaskObj.task}:{testcaseName} Env:{self.runTaskObj.env}: {failure.replace('Failed: ', '')}"})
                                        
                                        if putFailureDescAtEnd:
                                            description += f"\t   - {failure.strip()}\n"
                                        else:
                                            bodyMessage += f"\t   - {failure.strip()}\n\n"
                                    
                                    if putFailureDescAtEnd:
                                        self.runTaskObj.playbookObj.putFailureDetailsAfterResults.append({testcaseShortenPath: description})
                                
                                if putFailureDescAtEnd:
                                    self.runTaskObj.jiraFailures[eachTestcase].update({'bodyMessage': f'{jiraBodyHeader}\n\n{description}'})
                                else:
                                    self.runTaskObj.jiraFailures[eachTestcase].update({'bodyMessage': f'{jiraBodyHeader}\n\n{bodyMessage}'})
                                        
            except KeystackException as errMsg:
                bodyMessage = f'\tNo summary data. Test did not run successfully: {errMsg}'
        
        if modulePretestAborted:
            bodyMessage = ''
            for errorMsg in self.runTaskObj.taskSummaryData['exceptionErrors']:
                bodyMessage += f'\t- {errorMsg}\n'
                
        stageHeadings = ''
        includeStageHeadings = True
        
        if 'reportIncludeStageHeadings' in keystackSettings:
            if keystackSettings['reportIncludeStageHeadings'] in [False, 'False', 'false', 'no', 'No']:
                includeStageHeadings = False
        
        if includeStageHeadings:    
            stageHeadings += f'\nSTAGE:  {self.runTaskObj.stage}\n'
            
            if self.runTaskObj.taskSummaryData['totalSkipped'] > 0:
                taskResult = "Incomplete"
            else:
                taskResult = self.runTaskObj.taskSummaryData['result']
    
            taskStartTime        = self.runTaskObj.taskSummaryData['started']
            taskStopTime         = self.runTaskObj.taskSummaryData['stopped']
            taskDuration         = self.runTaskObj.taskSummaryData['testDuration']
            taskTotalPassed      = self.runTaskObj.taskSummaryData['totalPassed']
            taskTotalFailed      = self.runTaskObj.taskSummaryData['totalFailed'] ;# Overall test failures
            taskTotalFailures    = self.runTaskObj.taskSummaryData['totalFailures'] ;# Total module failures
            taskTotalSkipped     = self.runTaskObj.taskSummaryData['totalSkipped']
            taskTotalTestAborted = self.runTaskObj.taskSummaryData['totalTestAborted']

            # Script errors
            if self.runTaskObj.taskSummaryData['exceptionErrors']:
                taskExceptionError = len(self.runTaskObj.taskSummaryData["exceptionErrors"])
                bodyMessage += '\n\tErrors:\n'
                for eachError in self.runTaskObj.taskSummaryData["exceptionErrors"]:
                    # eachError: ['    exec(code, run_globals)\n  File "/opt/KeystackTests/Modules/Demo/Samples/Scripts/bgp.py", line 13, in <module>\n    print(f\'\\n---- bgp moduleProperties testcaseConfigParams:\', keystackObj.testcaseConfigParamsObj.pythonScripts)\nAttributeError: \'types.SimpleNamespace\' object has no attribute \'pythonScripts\'\n\n']
                    bodyMessage += f'\n\t\t{eachError.strip()}\n'

                bodyMessage += '\n'
            else:
                taskExceptionError = 0

            if self.runTaskObj.task== 'AirMosaic':
                # AirMosaic
                try:
                    stageHeadings += f"\tTASK:   {self.runTaskObj.task}\n"
                    stageHeadings += f"\tCells: {self.runTaskObj.airMosaicCellList}\n"
                    stageHeadings += f"\t{subjectHeader}Result:{taskResult} Testcases={len(self.runTaskObj.testcaseSortedOrderList)}  TotalPassed={taskTotalPassed}  TotalFailed:{taskTotalFailed}  KPI-Failed={taskTotalFailures}  Skipped:{taskTotalSkipped}  TestcaseAborted={taskTotalTestAborted}\n\n"
                except Exception as errMsg:
                    stageHeaderMessage = f"\t{self.runTaskObj.task} Task Report Error: {errMsg}\n\n"
                    
            elif self.runTaskObj.task== 'LoadCore':
                try:
                    stageHeadings += f"TASK:   {self.runTaskObj.task}\n\t{subjectHeader}\nENV:    {self.runTaskObj.taskSummaryData['env']}\n\tResult:{taskResult}   Testcases={len(self.runTaskObj.testcaseSortedOrderList)}  TotalPassed={taskTotalPassed}  TotalFailed={taskTotalFailed}  KPI-Failed={taskTotalFailures}  Skipped:{taskTotalSkipped}  TestcaseAborted={taskTotalTestAborted}   Errors={taskExceptionError}\n\n"
                except Exception as errMsg:
                    stageHeadings += f"MODULE: {self.runTaskObj.task}\n\t{subjectHeader}Error: {errMsg}\n\n"
            else:
                try:
                    stageHeadings += f"TASK:   {self.runTaskObj.task}\nENV:    {self.runTaskObj.taskSummaryData['env']}\n\t{subjectHeader}Result:{taskResult}   Testcases={len(self.runTaskObj.testcaseSortedOrderList)}  TotalPassed={taskTotalPassed}  TotalFailed={taskTotalFailed}  Skipped:{taskTotalSkipped}  TestcaseAborted={taskTotalTestAborted}  Errors={taskExceptionError}\n\n"
                except Exception as errMsg:
                    stageHeaderMessage += f"MODULE: {self.runTaskObj.task}\n\t{subjectHeader}Error: {errMsg}\n\n"

            if taskResult in ['Failed', 'Incomplete']:
                stageHeadings += f"\tabortTaskOnFailure: {self.runTaskObj.envParams['abortTaskOnFailure']}\n"
                stageHeadings += f"\tabortStageOnFailure: {self.runTaskObj.envParams['abortStageOnFailure']}\n"
                stageHeadings += f"\tabortTestOnFailure: {self.runTaskObj.playbookObj.abortTestOnFailure}\n"
                         
            stageHeadings += f"\tTest start time: {taskStartTime}\n"
            stageHeadings += f"\tTest stop time:  {taskStopTime}\n"
            stageHeadings += f"\tTest duration    {taskDuration}\n\n"
            
            playlistExclusions = self.runTaskObj.taskProperties.get('playlistExclusions', [])
            if playlistExclusions:
                stageHeadings += f"\tPlaylist Exclusions:\n"
                
                for excludedTestcase in playlistExclusions:
                    stageHeadings += f"\t   - {excludedTestcase}\n"
            
                stageHeadings += '\n'
            
        # Keep track of passed/failed module test for top-level Playbook reporting
        self.runTaskObj.playbookObj.overallResultList.append(self.runTaskObj.taskSummaryData['result'])
        overallResultList = [eachResult for eachResult in self.runTaskObj.playbookObj.overallResultList if eachResult != 'Passed']
        
        if self.runTaskObj.playbookObj.overallSummaryData['totalTestAborted'] > 0 or \
            self.runTaskObj.playbookObj.overallSummaryData['totalSkipped'] > 0:
            self.runTaskObj.playbookObj.result = 'Incomplete'
        else:
            if len(overallResultList) > 0:
                self.runTaskObj.playbookObj.result = 'Failed'
            else:
                self.runTaskObj.playbookObj.result = 'Passed'
                
        self.runTaskObj.playbookObj.overallSummaryData['result'] = self.runTaskObj.playbookObj.result
        if self.runTaskObj.playbookObj.result == 'Incomplete':
            self.runTaskObj.playbookObj.overallSummaryData['result'] = 'Incomplete'
            
        self.runTaskObj.playbookObj.updateOverallSummaryFileAndRedis() 

        if self.runTaskObj.taskSummaryData['totalSkipped'] > 0:
            self.runTaskObj.taskSummaryData['status'] = 'Incomplete'
            self.runTaskObj.taskSummaryData['result'] == 'Incomplete'
            
        writeToJson(self.runTaskObj.taskSummaryFile, self.runTaskObj.taskSummaryData, mode='w', threadLock=self.runTaskObj.statusFileLock)
                                                
        # Append the current testing task results to the overall test report
        self.runTaskObj.playbookObj.overallTestReport += f'{stageHeadings}'
        self.runTaskObj.playbookObj.overallTestReport += f'{bodyMessage}'
        self.runTaskObj.playbookObj.abortTaskOnFailure = self.runTaskObj.envParams['abortTaskOnFailure']
        self.runTaskObj.playbookObj.abortStageOnFailure = self.runTaskObj.envParams['abortStageOnFailure']  
        self.runTaskObj.playbookObj.testResultFolder = self.runTaskObj.taskResultsFolder
        self.runTaskObj.playbookObj.taskExceptionError = self.runTaskObj.taskSummaryData['exceptionErrors']

        try:
            if putFailureDescAtEnd:
                combineFailureDescriptions = ''
                for eachFailure in self.runTaskObj.playbookObj.putFailureDetailsAfterResults:
                    for testcase, failureDesc in eachFailure.items():
                        combineFailureDescriptions += f'{failureDesc}\n'
                    
                with open(self.runTaskObj.taskTestReportFile, 'w') as testReportFileObj: 
                    if combineFailureDescriptions:
                        msg = f'{stageHeadings}{bodyMessage}\n\nFailure Summary:\n{combineFailureDescriptions}\n'
                    else:
                        msg = f'{stageHeadings}{bodyMessage}'
 
                    testReportFileObj.write(msg)

            else:
                with open(self.runTaskObj.taskTestReportFile, 'w') as testReportFileObj: 
                    testReportFileObj.write(f'{stageHeadings}{bodyMessage}') 
       
        except Exception as errMsg:
            print(f'\ngenerateTaskTestReport error: {traceback.format_exc(None, errMsg)}')

        print(f'\nTask:{self.runTaskObj.task} results are in: {self.runTaskObj.resultsTimestampFolder}\n')
        
        