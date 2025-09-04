import os, json, traceback
from glob import glob
from time import sleep
from datetime import datetime
from re import search, match, I
from pathlib import Path
from pprint import pprint 
from shutil import rmtree
from copy import deepcopy  
               
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole, authenticateLogin
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from domainMgr import DomainMgr
from execRestApi import ExecRestApi
from globalVars import GlobalVars, HtmlStatusCodes
from EnvMgmt import ManageEnv
from PortGroupMgmt import ManagePortGroup
from baseLibs import removeEmptyTestResultFolders
from keystackUtilities import readJson, readYaml, readFile, writeToJson, writeToYamlFile, mkdir2, chownChmodFolder, execSubprocessInShellMode, removeTree, getTimestamp
from commonLib import validatePlaylistExclusions, logDebugMsg, logSession
from RedisMgr import RedisMgr
from scheduler import JobSchedulerAssistant, getSchedulingOptions
from db import DB

class Vars:
    """ 
    For logging the correct log topic.
    To avoid human typo error and be consistant
    """
    webpage = 'pipelines'
    commonPipelineStatus = ['Completed', 'Incomplete', 'Aborted', 'Skipped', 'StageFailAborted', 'Did-Not-Start', 'Terminated']
    

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    
def getPipelines():
    return glob(f'{GlobalVars.pipelineFolder}/*.yml')
   
def pipelineTable(tableBody, usersList, resultsList):
    # userFilterDropdown(usersList)
    table = f"""
       <div class="row tableStyle">  
            <table id="sessionsTable" class="tableFixHead2">   
                <thead>
                    <tr style="border-bottom: 1pt solid white;" id="pipelineDetails">
                        <th colspan="12" class="backgroundColorBlack mainTextColor" id="overallDetails"></th>
                    </tr>
                    
                    <tr>
                        <th><input type="checkbox" id="selectAllPipelineCheckbox" name="selectAllPipelines"></th>
                        <th class="textAlignCenter" style="z-index:8">Users</th>
                        <th class="textAlignCenterr">Pipeline ID</th>
                        <th class="textAlignLeft">Playbooks</th>
                        <th class="textAlignLeft">Stages</th>
                        <th class="textAlignLeft">Tasks / Logs</th>
                        <th class="textAlignLeft">Envs / Testbeds</th>
                        <th class="textAlignLeft">Running</th>
                        <th style="z-index:9">{statusFilterDropdown()}</th>
                        <th class="width150px textAlignCenter" style="z-index:9">{resultFilterDropdown(resultsList)}</th>
                    </tr>
                </thead>

                <tbody id="tableData">{tableBody}</tbody>
            </table>
        </div>
    """

    return table
                            
def statusFilterDropdown():
    pipelineStatus = ['All', 'Running', 'Completed', 'Incomplete', 'Aborted', 'Terminated', 'StageFailAborted', 'Did-Not-Start']

    dropdown = '<div class="btn-group dropleft">'
    dropdown += "<a class='dropdown-toggle deviceTypeHoverColor mainTextColor' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Status&ensp;&ensp;</a>"
      
    dropdown += f'<ul id="selectStatusFilter" class="dropdown-menu" aria-labelledby="">'
    
    for status in pipelineStatus:
        if status == 'All':
            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" id="selectedAllStatusFilter" name="selectedAllStatusFilter">&ensp;&ensp;All</li>'
        else:
            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox"  name="selectedStatusFilter" status="{status}">&ensp;&ensp;{status}</li>'
    
    dropdown += '<br>'
    dropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectStatusFilterButton" type="submit" class="btn btn-sm btn-outline-primary">Go</button></li>'
    dropdown += '</ul></div>'
    
    return dropdown

def resultFilterDropdown(resultsList):
    dropdown = '<div class="btn-group dropleft">'
    dropdown += "<a class='dropdown-toggle deviceTypeHoverColor mainTextColor' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Results&ensp;&ensp;</a>"
    
    dropdown += f'<ul id="selectResultFilter" class="dropdown-menu" aria-labelledby="">'
    
    for result in resultsList:
        if result == 'All':
            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" id="selectedAllResultFilter" name="selectedAllResultFilter">&ensp;&ensp;All</li>'
        else:
            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox"  name="selectedResultFilter" result="{result}">&ensp;&ensp;{result}</li>'
    
    dropdown += '<br>'
    dropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectResultFilterButton" type="submit" class="btn btn-sm btn-outline-primary">Go</button></li>'
    dropdown += '</ul></div>'
    
    return dropdown

def userFilterDropdown(usersList):
    """ 
    This user filter is not in use. 
    Leaving it here in case it is needed in the future
    """
    dropdown = '<div class="dropdown">'
    dropdown += "<a class='dropdown-toggle deviceTypeHoverColor mainTextColor' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Users&ensp;&ensp;</a>"
        
    dropdown += f'<ul id="selectUserFilter" class="dropdown-menu" aria-labelledby="">'
    
    for user in usersList:
        if user == 'All':
            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" id="selectedAllUserFilter" name="selectedAllUserFilter">&ensp;&ensp;All</li>'
        else:
            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox"  name="selectedUserFilter" user="{user}">&ensp;&ensp;{user}</li>'
    
    dropdown += '<br>'
    dropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectUserFilterButton" type="submit" class="btn btn-sm btn-outline-primary">Go</button></li>'
    dropdown += '</ul></div>'
    
    return dropdown
                    
def getOverallDetails(testResults):
    datetimeSortedList = []
    overallDetails = dict()
    overallDetails['sessions'] = 0
    overallDetails['running'] = 0
    overallDetails['completed'] = 0
    overallDetails['incomplete'] = 0
    overallDetails['pausedOnFailure'] = 0
    overallDetails['failed'] = 0
    overallDetails['passed'] = 0
    overallDetails['aborted'] = 0
    overallDetails['terminated'] = 0

    if RedisMgr.redis:
        #  ['overallSummary-domain=Communal-11-21-2024-08:39:45:255459_1749', 'overallSummary-domain=Communal-11-21-2024-16:40:34:537279_2142', 'overallSummary-domain=Communal-11-21-2024-16:42:47:715347_4335']
        datetimeSortedList = testResults 
    
    if RedisMgr.redis is None:                    
        for playbookResults in testResults:
            # playbookResults: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-11-2024-18:11:42:558897_7141
            if 'PLAYBOOK=' not in playbookResults:
                continue
        
            # ['/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/05-09-2023-18:19:06:538380', 
            #  '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/05-09-2023-18:20:01:607913']
            testResultTimestampFolders = glob(f'{playbookResults}/*')
            # Ascending order
            datetimeSortedList = list(sorted(testResultTimestampFolders, 
                                      key=lambda fileName: datetime.strptime(fileName.split('/')[-1].split('_')[0], "%m-%d-%Y-%H:%M:%S:%f")))
     
    for index, timestampResultsFullPath in enumerate(datetimeSortedList):
        if RedisMgr.redis is None:
            timestampResultFolder = timestampResultsFullPath.split('/')[-1]
            overallSummaryFile = f'{timestampResultsFullPath}/overallSummary.json'
            resultsMeta = f'{timestampResultsFullPath}/.Data/ResultsMeta'
            if os.path.exists(overallSummaryFile) == False:
                continue
            
            try:
                overallSummaryData = readJson(overallSummaryFile)
            except Exception as errMsg:
                # overallSummaryData file is malformed
                overallSummaryDataError = f'Get pipline TableData Error on overallSummaryFile: {overallSummaryFile}\nError: {traceback.format_exc(None, errMsg)}'
                print(f'GetPipelineData overallSummaryData error: {overallSummaryDataError}')
                continue
        else:                
            # timestampResultsFullPath: overallSummary-domain=Communal-04-12-2024-10:25:25:841330_3380
            timestampResultFolder = '-'.join(timestampResultsFullPath.split('-')[2:])
                            
            # Verify if the actual test result folder exists in the Linux OS filesystem. If not, remove it from Redis.
            regexMatch = search('.*-domain=(.+)-[0-9]+-[0-9]+-[0-9]+-[0-9]+:.+', timestampResultsFullPath)
            if regexMatch:
                actualTimestampTestResultFolder = f'{GlobalVars.resultsFolder}/DOMAIN={regexMatch.group(1)}'
                output = execSubprocessInShellMode(f'find {actualTimestampTestResultFolder} -name "{timestampResultFolder}"')[1]
                if output == '':
                    RedisMgr.redis.deleteKey(keyName=timestampResultsFullPath)
                    continue
                
            overallSummaryData = RedisMgr.redis.getCachedKeyData(keyName=timestampResultsFullPath)

            # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-11-2024-20:05:02:357476_9145/.Data/ResultsMeta/opt/KeystackTests/Playlist/Demo/Teardowns/teardownDut.yml_1_1
            try:
                resultsMeta = f'{overallSummaryData["topLevelResultFolder"]}.Data/ResultsMeta'
            except:
                continue
            
            overallSummaryFile = f'{overallSummaryData["topLevelResultFolder"]}/overallSummary.json'
        
        if len(overallSummaryData["pretestErrors"]) > 0:
            continue
                
        try:
            resultsPath = overallSummaryData.get('topLevelResultFolder', None)
        except:
            # Skip this erroroneous result
            continue
        
        overallCurrentStatus = overallSummaryData['status']                                  
        overallDetails['sessions'] += 1

        overallDetails['aborted'] += overallSummaryData['totalTestAborted']
      
        if overallCurrentStatus == 'Completed':
           overallDetails['completed'] += 1

        if overallCurrentStatus == 'Incomplete':
           overallDetails['incomplete'] += 1
           
        if overallCurrentStatus == 'Terminated':
            overallDetails['terminated'] += 1
            
        if overallCurrentStatus == 'Running':
            overallDetails['running'] += 1
        
        if 'result' in overallSummaryData:
            if overallSummaryData['result'] == 'Failed':
                overallDetails['failed'] += 1
            
            if overallSummaryData['result'] == 'Passed':
                overallDetails['passed'] += 1

        overallDetails['pausedOnFailure'] = overallSummaryData['pausedOnFailureCounter']
        
        for taskTestResultsPath in glob(f'{resultsPath}/STAGE=*'):
            taskSummaryFile = f'{taskTestResultsPath}/taskSummary.json'
            if os.path.exists(taskSummaryFile) is False:
                continue
                                   
    return overallDetails


def getTableData(view, domain, user, testResults, indexStart, indexEnd, userFilters='All', statusFilters='All', resultFilters='All'):
    """ 
    Get pipeline test sessions for a domain
    
    Parameters
        testResults: ['overallSummary-domain=Communal-10-18-2024-19:24:09:377777_5369_debug', 
                      'overallSummary-domain=Communal-10-19-2024-03:19:17:121446_5833]
        view: <str>: current | archive
    """
    tableData = ''
    completeTable = ''
    usersList = ['All']
    resultsList = ['All']
    
    if view == 'current':
        resultsPath = GlobalVars.resultsFolder
    else:
        resultsPath = GlobalVars.archiveResultsFolder
    
    index = 0
    datetimeSortedList   = []
    overallDetails = getOverallDetails(testResults)
 
    try:
        if RedisMgr.redis:
            datetimeSortedList = testResults
                
        for playbookResults in testResults:
            if RedisMgr.redis is None:
                # playbookResults: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-11-2024-18:11:42:558897_7141
                if 'PLAYBOOK=' not in playbookResults:
                    continue
            
                # ['/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/05-09-2023-18:19:06:538380_hgee', 
                #  '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/05-09-2023-18:20:01:607913_hgee2']
                testResultTimestampFolders = glob(f'{playbookResults}/*')
                datetimeSortedList = list(sorted(testResultTimestampFolders, 
                                          key=lambda fileName: datetime.strptime(fileName.split('/')[-1].split('_')[0], "%m-%d-%Y-%H:%M:%S:%f")))

        # Reverse the list to show pipelines in descending order
        for index, timestampResultsFullPath in enumerate(reversed(datetimeSortedList[indexStart:indexEnd])):
            if RedisMgr.redis is None:
                timestampResultFolder = timestampResultsFullPath.split('/')[-1]
                overallSummaryFile = f'{timestampResultsFullPath}/overallSummary.json'
                resultsMeta = f'{timestampResultsFullPath}/.Data/ResultsMeta'
                if os.path.exists(overallSummaryFile) == False:
                    continue
                
                try:
                    overallSummaryData = readJson(overallSummaryFile)
                except Exception as errMsg:
                    # overallSummaryData file is malformed
                    overallSummaryDataError = f'Get pipline TableData Error on overallSummaryFile: {overallSummaryFile}\nError: {traceback.format_exc(None, errMsg)}'
                    continue
            else:
                # timestampResultsFullPath: overallSummary-domain=Communal-04-12-2024-10:25:25:841330_3380
                timestampResultFolder = '-'.join(timestampResultsFullPath.split('-')[2:])
                   
                # Commenting this out because it might induce delays searching the filesystem             
                # Verify if the actual test result folder exists in the Linux OS filesystem. If not, remove it from Redis.
                regexMatch = search('.*-domain=(.+)-[0-9]+-[0-9]+-[0-9]+-[0-9]+:.+', timestampResultsFullPath)
                if regexMatch:
                    actualTimestampTestResultFolder = f'{GlobalVars.resultsFolder}/DOMAIN={regexMatch.group(1)}'
                    output = execSubprocessInShellMode(f'find {actualTimestampTestResultFolder} -name "{timestampResultFolder}"')[1]
                    if output == '':
                        RedisMgr.redis.deleteKey(keyName=timestampResultsFullPath)
                        continue
                 
                overallSummaryData = RedisMgr.redis.getCachedKeyData(keyName=timestampResultsFullPath)
                # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-11-2024-20:05:02:357476_9145/.Data/ResultsMeta/opt/KeystackTests/Playlist/Demo/Teardowns/teardownDut.yml_1_1
                try:
                    resultsMeta = f'{overallSummaryData["topLevelResultFolder"]}.Data/ResultsMeta'
                except:
                    continue
                
                overallSummaryFile = f'{overallSummaryData["topLevelResultFolder"]}/overallSummary.json'

            index += 1
            processId = overallSummaryData.get('processId', None)
            overallCurrentStatus = overallSummaryData['status']
            pipelineTimestampFolderFullPath = overallSummaryData['topLevelResultFolder']
            timestampFolderName = pipelineTimestampFolderFullPath.split('/')[-1]
            testReportSummaryFile = f'{pipelineTimestampFolderFullPath}/testReport'

            # If status has stopped, create a link to view the overall test report summary
            if overallCurrentStatus in Vars.commonPipelineStatus:
                timestampResultFolderLink = f'<a href="#" onclick="getFileContents(this)" filePath="{testReportSummaryFile}">{timestampResultFolder}</a>'
            else:
                timestampResultFolderLink = timestampResultFolder
                            
            if userFilters != 'All' and overallSummaryData['user'] not in userFilters:
                continue
                        
            if statusFilters != 'All' and overallCurrentStatus not in statusFilters:
                continue

            if resultFilters != 'All' and overallSummaryData['result'] not in resultFilters:
                continue
                                      
            # /opt/KeystackTests/Playbooks/DOMAIN=Communal/qa/pythonSample.yml
            playbookPath = overallSummaryData['playbook']

            matchRegex = search(f'{GlobalVars.playbooks}/(DOMAIN={domain}/.+)\.y.+', playbookPath)
            if matchRegex:
                # DOMAIN=Communal/Samples/advance -> Samples/advance
                playbookNamespacePath = matchRegex.group(1)
            else:
                playbookNamespacePath = 'Unknown'

            if '/' in playbookNamespacePath:
                playbookNameOnly = playbookNamespacePath.split('/')[-1]
            else:
                playbookNameOnly = playbookNamespacePath
                
            try:
                resultsPath = overallSummaryData.get('topLevelResultFolder', None)
            except:
                # Skip this erroroneous result
                continue
            
            timestampFolder = resultsPath.split('/')[-1]
            sessionId = overallSummaryData['sessionId']
            user = overallSummaryData['user']
            holdEnvsIfFailed = overallSummaryData.get('holdEnvsIfFailed', False)
            setHoldEnvsIfFailed = False
            envIcon = ''
            testAborted = False

            if user not in usersList:
                usersList.append(user)
            
            if overallSummaryData['result'] not in resultsList:
                resultsList.append(overallSummaryData['result'])
                                        
            # The Stage/task order in which the playbook was creeated and executed.
            # This runList will compare with ranList.
            # This is to show what is about to run and what already ran by comparing 
            # to the ranList created inside the for loop for taskProperties below.
            # runList: [{'stage': 'Bringup', 'task': 'bringup', 'env': 'DOMAIN=Communal/Samples/demoEnv'},
            #           {'stage': 'Test', 'task': 'layer3', 'env': 'DOMAIN=Communal/Samples/demoEnv1'}]
            runList = overallSummaryData.get('runList', [])
            
            # Start a new table row for each test
            tableData          += '<tr class="bottomBorder">'
            tdProcessIdLink    = f'<input class="width50px textAlignLeft wordWrap" type="checkbox" name="deleteSessionId" testResultsPath={resultsPath} />'
            tdStage            = '<td class="width200px textAlignLeft wordWrap">'
            tdTask             = '<td class="width200px textAlignLeft wordWrap">'
            tdEnv              = '<td class="width200px textAlignLeft wordWrap">'
            tdCurrentlyRunning = '<td class="width100px textAlignLeft wordWrap">'
            tdStatus           = '<td class="width200px textAlignCenter wordWrap">'
            tdResult           = '<td class="width120px textAlignCenter wordWrap">'
            
            # Get exception errors if any exists
            pretestErrors = ''            
            if len(overallSummaryData["pretestErrors"]) > 0:
                if len(overallSummaryData["pretestErrors"]) == 1:
                    for line in overallSummaryData["pretestErrors"][0].split('\n'):
                        line = line.replace('"', '&quot;')
                        pretestErrors += f"{line}<br>"          
                else:
                    for line in overallSummaryData["pretestErrors"]:
                        pretestErrors += f"{line}<br>"  
                    
                # Getting in here means there are Task pretest errors in the overSummaryData which means not all task
                # has this pretest failures.  Pretest errors could come from any stage/task/env.    
                testAborted = True                                                    
                currentStatus = 'Aborted'   
                tdProcessIdLink = f'<input type="checkbox" name="deleteSessionId" testResultsPath={resultsPath} />'
                tdStage    += ''
                tdTask     += ''
                tdEnv      += ''
                tdCurrentlyRunning  += ''
                tdStatus   += f'<a href="#" exceptionError="{pretestErrors}" testLogResultPath="{resultsPath}" onclick="openTestLogsModal(this)" data-bs-toggle="modal" data-bs-target="#testLogsModalDiv" class="blink">Pretest-Error </a>'
                tdResult   += ''

                tableData += f'<td>{tdProcessIdLink}</td>'
                tableData += f'<td class="col-1 textAlignCenter wordWrap">{user}</td>'
                tableData += f'<td class="col-2 textAlignLeft wordWrap">{timestampResultFolder}</td>'
                tableData += f'<td class="col-2 textAlignLeft wordWrap" title={playbookNamespacePath}><a href="#" data-bs-toggle="modal" data-bs-target="#showPlaybookModal" id="playbookPath" onclick="showPlaybook(this)" playbookPath="{playbookPath}">{playbookNameOnly}</a></td>'
                tableData += f'{tdStage}</td>'
                tableData += f'{tdTask}</td>'
                tableData += f'{tdEnv}</td>'
                tableData += f'{tdCurrentlyRunning}</td>'
                tableData += f'{tdStatus}</td>'
                tableData += f'{tdResult}</td>'
                tableData += '</tr>'
                                
            if len(overallSummaryData["pretestErrors"]) == 0:
                ranList = []
                # Don't keep showing stage for all the tasks. Just show stage name one time.
                stageTrackingForDisplay = ['']
                resultPathStageList = []
                for task in runList:
                    resultPathStageList += glob(f'{resultsPath}/STAGE={task["stage"]}_TASK={task["task"]}_ENV=*')
                
                for taskTestResultsPath in resultPathStageList:
                    taskSummaryFile = f'{taskTestResultsPath}/taskSummary.json'
                    testReportPath = f'{taskTestResultsPath}/taskTestReport'
                    if os.path.exists(testReportPath) is False:
                        testReportPath = ''
                        
                    if os.path.exists(taskSummaryFile) is False:
                        continue

                    # taskTestResultsPath:/opt/KeystackTests/Results/PLAYBOOK=pythonSample/07-08-2022-16:10:03:744673_qt8/STAGE=Test_TASK=CustomPythonScripts_ENV=qa-pythonSample
                    match = search('STAGE=(.+)_TASK=(.+)_ENV=(.+)', taskTestResultsPath)
                    if match is None:
                        continue

                    currentStage = match.group(1)
                    currentTask = match.group(2)
                    currentEnv = match.group(3)
                    if currentEnv in ['None', 'none', '']:
                        currentEnv = None
   
                    try:
                        # Test might have started, but it aborted before the testcase began running
                        try:
                            taskSummaryData = readJson(taskSummaryFile)
                        except Exception as errMsg:
                            errorMsg = traceback.format_exc(None, errMsg)
                            logDebugMsg(f'taskSummaryData exception: {errorMsg}')
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelineData', msgType='Error',
                                                      msg=f'Test aborted. tasksummary file is malformed: {taskSummaryFile}<br><br>', 
                                                      forDetailLogs=errorMsg)

                            exceptionMsg = f'Opening json taskSummaryFile error: {taskSummaryFile}: {errorMsg}' 
                            addExceptionList = f'{pretestErrors}<br><br>{exceptionMsg}'                   
                            currentStatus = 'Aborted'   
                            tdProcessIdLink = f'<input type="checkbox" name="deleteSessionId" testResultsPath={resultsPath} />'
                            tdStage    += ''
                            tdTask     += ''
                            tdEnv      += ''
                            tdProgress += ''
                            tdStatus   += f'<a href="#" exceptionError="{addExceptionList}" testLogResultPath="{resultsPath}" onclick="openTestLogsModal(this)" data-bs-toggle="modal" data-bs-target="#testLogsModalDiv">Aborted</a>'                       
                            tdResult   += ''
                            continue

                        # Get all the task exception errors here so below areas could use it
                        taskExceptionErrors = ''
                        if len(taskSummaryData["exceptionErrors"]) > 0:
                            for line in taskSummaryData["exceptionErrors"][0].split('\n'):
                                line = line.replace('"', '&quot;')
                                taskExceptionErrors += f"{line}<br>"
                                
                        # addedExceptionErrors: Test Errors:<br><br><br>Task Errors:<br>  File &quot;/opt/KeystackTests/tasks/Demo/Samples/Scripts/bgp.py&quot;, line 10, in <task><br>    keystackObj.logwarning('Warning message')<br>AttributeError: 'Main' object has no attribute 'logwarning'<br><br><br><br>
                        addedExceptionErrors = f'{pretestErrors}<br>Task Errors:<br>{taskExceptionErrors}<br>'
                                            
                        stage = currentStage
                        envFullPath = taskSummaryData['envPath']
                        testcaseSortedOrderList = taskSummaryData.get('testcaseSortedOrderList', None)
                        
                        ranList.append({'stage': currentStage, 'task':currentTask, 'env': taskSummaryData['env']})
                        isEnvParallelUsed = taskSummaryData.get('isEnvParallelUsed', False)
                        
                        envIcon = ''
                        progress = taskSummaryData.get('progress', '')
                        stopped = ':'.join(taskSummaryData['stopped'].split(':')[:-1])
                        currentlyRunning = ''
                        result = taskSummaryData['result']
                        resultReport = taskSummaryData['result']
                        processIdLink = ''
                        testToolSessionIdUrl = None
                        deleteButton = ''
                        viewLogs = ''
                        processIdLink = ''
                        holdEnvOnFailure = 'No'
                        currentStatus = None

                        # env => DOMAIN=Communal/Samples/demoEnv1
                        env = taskSummaryData.get('env', 'Not-Needed')
                        envWithDomain = env
                        if env not in [None, 'Not-Needed']:
                            # env => Samples/demoEnv1
                            regexMatch = search(f'(DOMAIN={domain}/)?(.+)', env)
                            if regexMatch:
                                env = regexMatch.group(2)
                            if env == 'not-required':
                                env = ''
 
                        if taskSummaryData['loadBalanceGroup']:
                            if taskSummaryData["env"] is None:
                                lbgEnv = "No env in LBG"
                            else:
                                lbgEnv = taskSummaryData["env"]
                                # env => Samples/demoEnv1
                                regexMatch = search(f'DOMAIN={domain}/(.+)', lbgEnv)
                                if regexMatch:
                                    lbgEnv = regexMatch.group(1)

                            # qa DOMAIN=Communal/Samples/demoEnv1
                            env = f'{taskSummaryData["loadBalanceGroup"]}: {lbgEnv}'
                        else:
                            if env is None:
                                env = ''

                        if '/' in env:
                            envNameOnly = env.split('/')[-1]
                        else:
                            envNameOnly = env
                        
                        # Don't include the env icons if the task doesn't use an env    
                        if env and "Not-Needed" not in env:
                            if isEnvParallelUsed:
                                envIcon += f'<i class="fa-regular fa-circle-pause" title="parallelUsage=True" style="transform:rotate(90deg);"></i>&ensp;'
                                #envIcon += f'<i class="fa-solid fa-equals"></i>&ensp;'
                            else:
                                #envIcon += f'<i class="fa-solid fa-circle-minus" style="transform:rotate(90deg);"></i>&ensp;'
                                envIcon += f'<i class="fa-regular fa-circle-dot" title="parallelUsage=False"></i>&ensp;'
                            
                            if taskSummaryData['loadBalanceGroup']:
                                envIcon += f'<i class="fa-solid fa-circle-half-stroke" title="LoadBalance=True"></i>'
                            else:
                                envIcon += f'<i class="fa-regular fa-circle" title="LoadBalance=False"></i>'

                        if taskSummaryData.get('currentlyRunning', None):
                            # /opt/KeystackTests/Modules/CustomPythonScripts/Samples/BridgeEnvParams/dynamicVariableSample.yml
                            currentlyRunning = taskSummaryData['currentlyRunning'].split('/')[-1].split('.')[0]
                            
                        # Overall Status: Started | Did-Not-Start | Rebooting Agents | Loading Config File | TestConfiguring Config | Running 
                        #         Collecting Artifacts | Deleting Test Session
                        #         Completed | Incomplete | Aborted | Terminated
 
                        if overallCurrentStatus not in ['Completed', 'Incomplete', 'Aborted', 'Skipped', 'StageFailAborted', 'Terminated']:
                            currentlyRunningTestcase = taskSummaryData['currentlyRunning']
                            if currentlyRunningTestcase:
                                # currentlyRunningTestcase could be None. There could be a ymal file error.
                                # /opt/KeystackTests/Modules/CustomPythonScripts/Samples/Testcases/bgp.yml
                                
                                tcFile = f'{resultsMeta}{currentlyRunningTestcase}'
                                
                                for testcaseIterationFile in glob(f'{tcFile}/*'):
                                    testcaseIteration = readJson(tcFile)
                                    if testcaseIteration['status'] == 'Running':
                                        totalRunning += 1
                                        testToolSesisonIdUrl = testcaseIteration['testSessionId']
                                                                        
                            # Terminate is displayed because the is still running
                            processIdLink = f'<a href="#" style="text-decoration:none" sessionId={overallSummaryData["sessionId"]} processId={processId} statusJsonFile={overallSummaryFile} onclick="terminateProcessId(this)">Terminate</a>'
                            
                        if overallCurrentStatus in Vars.commonPipelineStatus:       
                            if result in ['Failed', 'Error']:
                                resultColor = 'red'
                                setHoldEnvsIfFailed = True
                            else:
                                resultColor = 'blue'
                            
                            resultReport = f'<a href="#" style="color:{resultColor}" testReportPath={testReportPath} onclick="openTestResultModal(this)" data-bs-toggle="modal" data-bs-target="#testReportModalDiv">{result}</a>'                                
                        
                            # Delete is displayed because the test has stopped
                            processIdLink = f'<input type="checkbox" name="deleteSessionId" testResultsPath={resultsPath} />'
                                                
                        if overallCurrentStatus in ['Pretest-Error', 'Aborted', 'StageFailAborted'] and result in ['Incomplete', 'Error']:
                            if os.path.exists(testReportPath):
                                with open(testReportPath, 'w') as fileObj:
                                    fileObj.write(str(json.dumps(taskSummaryData, indent=4)))
                            
                            setHoldEnvsIfFailed = True
                        
                        # Progress
                        progress = f'<a href="#" resultsPath="{resultsPath}" testcasesSortedOrderList="{testcaseSortedOrderList}" onclick="showTestcasesInProgress(this)">{progress}</a>'
                            
                        if overallCurrentStatus == 'Terminated':
                            currentStatus = 'Terminated'
                        else:    
                            if testToolSessionIdUrl:
                                if taskSummaryData["status"] not in Vars.commonPipelineStatus:
                                    if overallCurrentStatus != 'Terminated':
                                        currentStatus = f'<a class="blink" href={testToolSessionIdUrl} target="_blank" style="text-decoration:none;">{taskSummaryData["status"]}</a>'
                                    if overallCurrentStatus == 'Terminated' and taskSummaryData["status"] == 'Running':
                                        currentStatus = 'Aborted'      
                                else:
                                    if pretestErrors != '' or taskExceptionErrors != '':
                                        currentStatus = f'<a href="#" exceptionError="{addedExceptionErrors}" testLogResultPath="{resultsPath}" onclick="openTestLogsModal(this)" data-bs-toggle="modal" data-bs-target="#testLogsModalDiv">{taskSummaryData["status"]}</a>'
                                    else: 
                                        currentStatus = f'<a href={testToolSessionIdUrl} target="_blank">{taskSummaryData["status"]}</a>'
                                    setHoldEnvsIfFailed = True
                            else:                   
                                if taskSummaryData["status"] not in Vars.commonPipelineStatus:
                                    # status = Running | Started
                                    if overallCurrentStatus != 'Terminated':
                                        if testAborted:
                                            currentStatus = f'<span class="blink">-{taskSummaryData["status"]}</span>'
                                        else:
                                            currentStatus = f'<span class="blink">{taskSummaryData["status"]}</span>'
                                            
                                    if overallCurrentStatus == 'Terminated' and taskSummaryData["status"] == 'Running':
                                        currentStatus = 'Aborted'
                                else:
                                    if pretestErrors != '' or taskExceptionErrors != '':
                                        currentStatus = f'<a href="#" exceptionError="{addedExceptionErrors}" testLogResultPath="{resultsPath}" onclick="openTestLogsModal(this)" data-bs-toggle="modal" data-bs-target="#testLogsModalDiv">{taskSummaryData["status"]}</a>'
                                    else:   
                                        currentStatus = f'{taskSummaryData["status"]}'
                                    
                                    setHoldEnvsIfFailed = True

                            # If paused-on-error, overwrite above status
                            if taskSummaryData["status"] == 'paused-on-failure':
                                currentStatus = f'<a href="#" class="blink" pausedOnFailureFile="{taskTestResultsPath}/pausedOnFailure" onclick="resumePausedOnFailure(this)"> PausedOnFailure</a>'

                        # If the test is terminated, taskSummary.json status won't be set to Terminated.
                        # Use overallSummary data and get the taskSummary['currentlyRunning'] to set the testcase status to terminated 
                        if overallCurrentStatus == 'Terminated':
                            if currentlyRunning or taskSummaryData['status'] == 'Waiting-For-Env':
                                currentStatus = f'<span style="color:red">Terminated</span>'

                    except Exception as errMsg:
                        print('\nGetSession Exception:', traceback.format_exc(None, errMsg))
                        #logDebugMsg(f'\nGetSession Exception: {traceback.format_exc(None, errMsg)}')
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelineData', msgType='Error',
                                                    msg=f'getTableData(): {errMsg}', 
                                                    forDetailLogs=traceback.format_exc(None, errMsg))

                    tdProcessIdLink = processIdLink
                    if stageTrackingForDisplay[-1] != currentStage:
                        # <i class="fa-solid fa-circle-check"></i> | <i class="fa-solid fa-circle-xmark"></i> 
                        # <i class="fa-regular fa-circle">  | <i class="fa-solid fa-person-running"></i>
                        # <i class="fa-solid fa-dash"></i>  |  <i class="fas fa-circle-exclamation"></i>
                        # <i class="fa-solid fa-circle-notch"></i>
                        if stage in overallSummaryData['stages']:
                            if overallSummaryData['stages'][stage]['result'] in ['Failed', 'Incomplete', 'Aborted']:
                                #tdStage += '<strong><i class="fa-solid fa-circle-xmark textRed" title="Failed, Incomplete, Aborted"></i></strong>&emsp;'
                                tdStage += '<strong><i class="textRed" title="Failed, Incomplete, Aborted"></i></strong>'
                            elif overallSummaryData['stages'][stage]['result'] == 'Passed':
                                #tdStage += '<i class="fa-solid fa-circle-check mainTextColor" title="Passed"></i>&emsp;' 
                                tdStage += '<i class="mainTextColor" title="Passed"></i>'
                            elif overallSummaryData['stages'][stage]['result'] == '':
                                # Running
                                #tdStage += '<i class="fa-solid fa-person-running"></i>'
                                tdStage += '<i class="sessionSpinningProgress"></i>'
                            else:
                                # Aborted
                                #tdStage += '<i class="fa-solid fa-circle-notch" title="Not-Started, skipped or aborted"></i></i>&emsp;'
                                tdStage += '<i title="Not-Started, skipped or aborted"></i></i>'
                                
                            tdStage  += f'{stage}<br>'
                    else:
                        # Don't show the stage name again
                        tdStage  += '<br>'
                    
                    stageTrackingForDisplay.append(currentStage)
                    tdTask += f'<a style="text-decoration:none" href="/sessionMgmt/sessionDetails?testResultsPath={taskSummaryData["taskResultsFolder"]}">{currentTask}</a><br>'
                                                                       
                    if currentStatus in ['Incomplete', 'Completed'] and 'Failed' in resultReport and holdEnvsIfFailed:
                        envMgmtDataFile = f'{resultsPath}/.Data/EnvMgmt/STAGE={currentStage}_TASK={currentTask}_ENV={currentEnv}.json'
                        
                        if RedisMgr.redis:
                            keyName = f'envMgmt-{timestampFolderName}-STAGE={currentStage}_TASK={currentTask}_ENV={currentEnv}'
                            envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                        else:
                            envMgmtData = readJson(envMgmtDataFile)
                        
                        # envMgmtData:  {'user': 'hgee', 'sessionId': '05-25-2023-15:43:49:755851_2058', 'stage': 'Test', 'task': 'Demo2', 'env': 'Samples/hubert', 'envIsReleased': True, 'holdEnvsIfFailed': True, 'result': 'Failed'}
                        if isEnvParallelUsed == False and envMgmtData and envMgmtData['envIsReleased'] == False:                        
                            # These envs failed and need to be released                        
                            # [{'user': 'hgee', 'sessionId': '11-15-2022-12:01:30:521184_hubogee', 'stage': 'Bringup', 'task': 'CustomPythonScripts', 'env': 'None'}, {'user': 'hgee', 'sessionId': '11-15-2022-12:01:30:521184_hubogee', 'stage': 'Test', 'task': 'CustomPythonScripts', 'env': 'pythonSample'},]
                            
                            # setups.views.ReleaseEnvsOnFailure() will clear out the Envs by pressing the releaseEnv button
                            tdEnv += f'{envIcon} <a href="#" class="blink textBlue" user="{user}" sessionId="{timestampResultFolder}" stage="{currentStage}" task="{currentTask}" env="{taskSummaryData["env"]}" resultTimestampPath="{resultsPath}" onclick="releaseEnvOnFailure(this)">Release-Env: </a><span title="{envWithDomain}">{envNameOnly}</span><br>'
                        else:
                            # Passed | Aborted | Waiting
                            tdEnv += f'<a href="#" data-bs-toggle="modal" data-bs-target="#showEnvModal" onclick="showEnv(this)" title={envWithDomain}  envPath="{envFullPath}">{envIcon} {envNameOnly}</a><br>'
                    else:
                        tdEnv += f'<a href="#" data-bs-toggle="modal" data-bs-target="#showEnvModal" onclick="showEnv(this)" title={envWithDomain} envPath="{envFullPath}">{envIcon} {envNameOnly}<br></a>'
                        
                    tdCurrentlyRunning += f'<a class="textBlue" href="#" title={taskSummaryData["currentlyRunning"]}>{currentlyRunning}</a><br>'
                    tdStatus   += f'{currentStatus}&nbsp; {progress}<br>'
                    tdResult   += f'{resultReport}<br>'                     
                    
                # print('\n--- runList:', runList)
                # print('\n---- ranList:', ranList)
                remainingList = [currentRuns for currentRuns in runList if currentRuns not in ranList]
                for x in remainingList:
                    # Show what is about to run:  DOMAIN=Communal/Samples/demoEnv1
                    if x['env'] is None:
                        remainingTaskEnv = ''
                        envIcon = ''
                    else:
                        # DOMAIN=Communal/Samples/demoEnv3 -> Samples/demoEnv3
                        remainingTaskEnv = x['env']
                        #remainingTaskEnv = '/'.join(remainingTaskEnv.split('/')[1:])
                        if remainingTaskEnv != "not-required":
                            remainingTaskEnv = remainingTaskEnv.split('/')[-1]
                        else:
                            #remainingTaskEnv = 'Not-required'
                            emainingTaskEnv = ''
                    
                    tdStage  += f'<i title="Aborted, Skipped or Did-Not-Start"></i></i>{x["stage"]}<br>'
                    tdTask += f'{x["task"]}<br>'
                    envFullPath = f'{GlobalVars.envPath}/{x["env"]}.yml'
                    tdEnv    += f'<a href="#" data-bs-toggle="modal" data-bs-target="#showEnvModal" onclick="showEnv(this)" title={x["env"]} envPath="{envFullPath}">{envIcon} {remainingTaskEnv}</a><br>'
                        
                    if 'Aborted' not in tdStatus:
                        tdStatus += 'Not-Started<br>'

                # Create the pipeline        
                # processIdLink replaces Delete when it's active
                tableData += f'<td>{tdProcessIdLink}</td>'
                tableData += f'<td class="width200px textAlignCenter wordWrap" >{user}</td>'
                tableData += f'<td class="width300px textAlignLeft wordWrap">{timestampResultFolderLink}</td>'
                tableData += f'<td class="width200px textAlignLeft wordWrap" title={playbookNamespacePath}><a href="#" data-bs-toggle="modal" data-bs-target="#showPlaybookModal" id="playbookPath" onclick="showPlaybook(this)" playbookPath="{playbookPath}">{playbookNameOnly}</a></td>'
                tableData += f'{tdStage}</td>'
                tableData += f'{tdTask}</td>'
                tableData += f'{tdEnv}</td>'
                tableData += f'{tdCurrentlyRunning}</td>'
                tableData += f'{tdStatus}</td>'
                tableData += f'{tdResult}</td>'
                tableData += '</tr>'
                
        # Add extra row to support the tableFixHead2 body with height:0 to 
        # show a presentab
        # le table. Otherwise, if there are a few rows, the row 
        # height will be large to fill the table size
        tableData += f'<tr></tr>'
            
        completeTable = pipelineTable(tableBody=tableData, usersList=usersList, resultsList=resultsList)
  
    except Exception as errMsg:
        completeTable = ''
        print(f'\nPipeline getTableData Error: {traceback.format_exc(None, errMsg)}')
        logDebugMsg(f'\npipeline getTableData Exception: {traceback.format_exc(None, errMsg)}')
                       
    return completeTable, overallDetails


class GetSessions(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetSessions', allowUserRoles=['all'])
    def post(self, request):
        """ 
        Step to add a remote controller:
           - On the main controller, add "remote controller"
             (This will generate an Access-Key)
           - Go on the remote controller, add "Access Key" with the above main controller IP
        """ 
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)    
        user = AccountMgr().getRequestSessionUser(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        tableData = '' 
        # view: current | archive
        view = request.data.get('view', None)
        domain = request.data.get('domain', None)

        # 'All' or a list of: ['Running', 'Completed', 'Incomplete', 'Skipped', 'Aborted', 'Terminated', 'StageFailAborted', 'Did-Not-Start']
        userFilterCheckboxes = request.data.get('userFilterCheckboxes', 'All')
        statusFilterCheckboxes = request.data.get('statusFilterCheckboxes', 'All')
        resultFilterCheckboxes = request.data.get('resultFilterCheckboxes', 'All')

        # Pagination
        getCurrentPageNumber  = request.data.get('getCurrentPageNumber', None)
        devicesPerPage        = request.data.get('devicesPerPage', None)
                
        # ['0:2'] <-- In a list
        # pageIndexRange: The document range to get from the collective pool of document data
        pageIndexRangeOriginal = request.data.get('pageIndexRange', None)
        
        # 0:2
        if pageIndexRangeOriginal:
            pageIndexRange = pageIndexRangeOriginal[0]
            indexStart     = int(pageIndexRange.split(':')[0])
            indexEnd       = int(pageIndexRange.split(':')[1])
            startingRange  = pageIndexRange.split(":")[0]
                    
        # remoteController:192.168.28.17  mainControllerIp:192.168.28.7
        #print(f'\n---- pipelineViews: remoteController:{remoteControllerIp}  mainControllerIp:{mainControllerIp}')
                 
        try:
            overallDetailsHtml = ''

            if remoteControllerIp and remoteControllerIp != mainControllerIp:
                params = {"view":view, "domain":domain}
                restApi = '/api/v1/pipeline/getPipelines'
                response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                               user, webPage=Vars.webpage, action='GetPipelines')
                if errorMsg:
                    return Response({'isUserAllowedInDomain': False, 'status': 'failed', 'errorMsg': errorMsg, 
                                     'tableData': '', 'overallDetailsHtml':''},
                                    status=statusCode)
                else:
                    tableData = response.json()['tableData']
                    overallDetailsHtml = response.json()['overallDetails']
                
            else:
                if view == 'current':
                    resultsPath = GlobalVars.resultsFolder
                else:
                    resultsPath = GlobalVars.archiveResultsFolder
        
                if RedisMgr.redis:
                    # ['domain=Communal-overallSummary-04-11-2024-18:11:09:802448_3627', 'domain=Communal-overallSummary-04-11-2024-18:11:42:558897_7141']
                    testResults = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'overallSummary-domain={domain}*', sort=True)
                else:
                    testResults = glob(f'{resultsPath}/DOMAIN={domain}/*')
                                
                totalPipelines = len(testResults)
                pageNumber = 0
                            
                pagination = """<nav aria-label="">
                                    <ul class="pagination pagination-sm">
                                        <li class="page-item">
                                            <a class="page-link" id="previousPage" href="#" aria-label="Previous">
                                                <span aria-hidden="true">&laquo;</span>
                                            </a>
                                        </li>"""

                pageNumberMapping = {}
                # devicesPerPage:5  getPageNumber:1  pageIndexRange:0:5  indexStart:0  indexEnd:5  startingRange:0
                for index, startingIndex in enumerate(range(0, totalPipelines, devicesPerPage)):
                    # Creating page buttons with specific range of devices to show
                    pageNumber = index+1
                    endingIndex = startingIndex + devicesPerPage
                    pageNumberMapping[pageNumber] = (startingIndex, endingIndex)

                    if pageNumber > 1 and endingIndex == totalPipelines:
                        # Don't create a 2nd page button if there's only 1 page of results to show
                        pagination += f'<li class="page-item"><a class="page-link" href="#" onclick="getSessions(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{totalPipelines}">{pageNumber}</a></li>'
                    else:
                        # Note: if endingIndex != data.count():
                        # getPageNumber: Is to show the current page number
                        if int(pageNumber) == int(getCurrentPageNumber):
                            pagination += f'<li class="page-item active"><a class="page-link" href="#" onclick="getSessions(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</a></li>'
                        else:
                            pagination += f'<li class="page-item"><a class="page-link" href="#" onclick="getSessions(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</a></li>'
                        
                pagination += """<li class="page-item">
                                    <a class="page-link" id="nextPage" href="#" aria-label="Next">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                    </li></ul></nav>"""

                if pageNumberMapping == {}:
                    indexStart = 0
                    indexEnd = 0
                else:
                    currentPageStartAndEndIndexes = pageNumberMapping[int(getCurrentPageNumber)]
                    indexStart = currentPageStartAndEndIndexes[0]
                    indexEnd = currentPageStartAndEndIndexes[1]
                    
                tableData, overallDetails = getTableData(view, domain, user, testResults, 
                                                         indexStart, indexEnd, userFilterCheckboxes,
                                                         statusFilterCheckboxes, resultFilterCheckboxes)

                # Mainly used for controller-to-controller pulling sessions from a remote controller.
                # True = Sessions is working.  False = Not working. 
                # Session failures could be because the remote controller is unreachable.
                # Set to False and SystemLogging log only once instead of continuously logging which 
                # overwhelms the database.
                # Once connectivity is back, pipelineViews.py:GetSessions() will set to True.                
                settings.KEYSTACK_SESSIONS_CONNECTIVITY = True
                
                # overallDetails is from getTableData()
                overallDetailsHtml += '<center>'
                
                overallDetailsHtml += f'Total-Pipelines: {totalPipelines}&emsp;&emsp;&emsp;'
                if overallDetails["running"] > 0:
                    overallDetailsHtml += f'<span class="blink1-5s">Running: {overallDetails["running"]}</span>&emsp;&emsp;&emsp;'
                else:
                     overallDetailsHtml += f'Running: {overallDetails["running"]}&emsp;&emsp;&emsp;'
                     
                overallDetailsHtml += f'Completed: {overallDetails["completed"]}&emsp;&emsp;&emsp;'
                overallDetailsHtml += f'Incomplete: {overallDetails["incomplete"]}&emsp;&emsp;&emsp;'
                overallDetailsHtml += f'Aborted: {overallDetails["aborted"]}&emsp;&emsp;&emsp;'
                overallDetailsHtml += f'Terminated: {overallDetails["terminated"]}&emsp;&emsp;&emsp;'
                
                if overallDetails["pausedOnFailure"] > 0:
                    overallDetailsHtml += f'<span class="blink1-5s">Paused-On-Failure: {overallDetails["pausedOnFailure"]}</span>&emsp;&emsp;&emsp;'
                else:
                    overallDetailsHtml += f'Paused-On-Failure: {overallDetails["pausedOnFailure"]}&emsp;&emsp;&emsp;'
                    
                overallDetailsHtml += f'Passed: {overallDetails["passed"]}&emsp;&emsp;&emsp;'
                overallDetailsHtml += f'Failed: {overallDetails["failed"]}'
                overallDetailsHtml += '</center>'
                
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            overallDetailsHtml = ''
            tableData = ''
            #print(f'\n--- GetSessions error:', traceback.format_exc(None, errMsg))
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelines', msgType='Error', msg=errorMsg,
                                      forDetailLogs=f'{traceback.format_exc(None, errMsg)}')

        return Response(data={'status':status,
                              'errorMsg':errorMsg, 
                              'tableData': tableData,
                              'overallDetails': overallDetailsHtml,
                              'pagination': pagination,
                              'totalPages': pageNumber,
                              'getCurrentPageNumber': getCurrentPageNumber}, 
                        status=statusCode)


class GetSessionDetails(APIView):        
    @verifyUserRole(webPage=Vars.webpage, action='GetSessionDetails')
    def post(self, request):
        """ 
        Get the session details
        
        The folder toggler works in conjuntion with an addListener in getTestcaseData() 
        and keystackDetailedLogs CSS
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        
        # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/08-23-2023-20:04:09:337297_9269/STAGE=Test_TASK=Demo_ENV=Samples-pythonSample
        testResultsPath = request.data.get('testResultsPath', None)

        class getPagesVars:
            counter = 0
            html = ''
         
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"testResultsPath": testResultsPath}
            restApi = '/api/v1/pipeline/getSessionDetails'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetSessionDetails')
            if errorMsg:
                sessionData = None
                stageTaskEnv = None 
            else:    
                sessionData = response.json()['sessionData']
                stageTaskEnv = response.json()['stageTaskEnv']
                getPagesVars.html = response.json()['testcaseData']                          
        else:   
            try:      
                taskSummaryFile = f'{testResultsPath}/taskSummary.json'
                if os.path.exists(taskSummaryFile) is False:
                    raise Exception(f'TaskSummaryFile does not exists: {taskSummaryFile}')
            
                status = readJson(taskSummaryFile)
                # Verify if the overall test is terminated
                overallSummaryFile = f'{testResultsPath.split("STAGE")[0]}/overallSummary.json'
                overallStatus = readJson(overallSummaryFile)
                
                playbookFullPath = status['playbook']
                testcaseSortedOrderList = status.get('testcaseSortedOrderList', [])
                match = search(f'{GlobalVars.keystackTestRootPath}/Playbooks/([^ ]+)\.', playbookFullPath)
                if match:
                    playbook = match.group(1)
                else:
                    playbook = 'Unknown'

                # STAGE=Tests_TASK=CustomPythonScripts_ENV=loadcoreSample
                match = search('(STAGE=.*)_TASK.*', testResultsPath)
                if match:
                    stage = match.group(1).replace('=', ': ')
                    
                match = search('STAGE=.*_(TASK=.*)_ENV', testResultsPath)
                if match:
                    task= match.group(1).replace('=', ': ')

                match = search('STAGE=.*_TASK=.*_(ENV.*)', testResultsPath)
                if match:
                    env = match.group(1).replace('=', ': ')
                
                statusCode = HtmlStatusCodes.success

            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                #print('\n--- getSessionDetails error:', traceback.format_exc(None, errMsg))
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetSessionDetails', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

            testTime = f"Playbook: {playbook}<br>Started: {status['started']}<br>Stopped: {status['stopped']}<br>"
            
            try:
                testTime += f"Duration: {status['testDuration']}<br>"
            except:
                # test time may not be ready yet
                pass
            
            def createCard(inserts, col="col-xl-4"):
                data = f"""<div class="{col} col-md-6 mb-4">
                                <div class="card border-left-primary h-100 py-0">
                                    <div class="card-body">
                                        <div class=f"row no-gutters align-items-center">
                                            {inserts}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        """  
                return data

            stageTaskEnv = f'{stage}&ensp;&emsp;{task}&ensp;&emsp;{env}'
            sessionData = '<div class="row">'
            sessionData += createCard(testTime)
            
            #if status['status'] not in ['Completed', 'Terminated', 'Aborted']:
            if status['status'] not in Vars.commonPipelineStatus:
                if overallStatus['status'] == 'Terminated':
                    status2 = f'<span style="color:blue">Terminated</span>'
                else:
                    status2 = f'<span class="blink"><span style="color:blue">{status["status"]}</span></span>'
                
                sessionData += createCard(f"""<div style="font-size:20px; padding-left:0px">Status: {status2}</span></div><br>
                                        Total Testcases: {status['totalCases']}&emsp;&emsp; 
                                        Total Passed: {status['totalPassed']}&emsp;&emsp;
                                        Total Failed: {status['totalFailed']}&emsp;&emsp;<br>
                                        Progress: {status['progress']}
                                        """)
            else:
                # #10b332 = Green
                sessionData += createCard(f"""<div style="font-size:20px; padding-left:0px">Status: <span style="color:blue">{status['status']}</div><br>
                                        Total Testcases: {status['totalCases']}&emsp;&emsp; 
                                        Total Passed: {status['totalPassed']}&emsp;&emsp;
                                        Total Failed: {status['totalFailed']}&emsp;&emsp;<br>
                                        Progress: {status['progress']}
                                        """)

            if status['result'] in ['Failed', 'Incomplete']:
                status2 = f'<span style="color:red">{status["result"]}</span>'
            elif status['result'] == 'Passed':
                status2 = f'<span style="color:#10b332">{status["result"]}</span>'
            else:
                # Not-Ready
                status2 = f'<span style="color:blue">{status["result"]}</span>'
                    
            sessionData += createCard(f"""<div style="font-size:20px; padding-left:0px">Result: {status2}</div><br>
                                        Test Cases Aborted: {status['totalTestAborted']}&emsp;&emsp;
                                        Test Cases Skipped: {status['totalSkipped']}&emsp;&emsp;
                                        """)
            sessionData += "</div>"

            """
            The folder toggler works in conjuntion with an addListener in getTestcaseData() 
            
            <nav class="keystackDetailedLogs card py-0 mb-0">
                <ul class="nav flex-column" id="nav_accordion">
                    <li class="nav-item has-submenu">
                        <a class="nav-link" href="#"> resultFolder </a>
                        <ul class="submenu collapse">
                            <li><a class="nav-link" href="#"> File 1 </a></li>
                            <li><a class="nav-link" href="#"> File 2 </a></li>
                            <li><a class="nav-link" href="#"> File 3 </a> </li>
                        </ul>
                    </li>
                </ul>
            </nav>
            """
    
            if status['currentlyRunning']:
                sessionData += '<div class="row">'
                sessionData += createCard(f"Currently Running: {status['currentlyRunning']}", col="col-xl-12")       
                sessionData += "</div>"     

            if status.get('playlistExclusions', []):
                sessionData += 'Playlist Exclusions:<br>'
                for eachExclusion in status['playlistExclusions']:
                    sessionData += f'&emsp;&emsp;- {eachExclusion}<br>'
                    
                sessionData += '<br>'

            getPagesVars.html = f'<ul id="testResultFileTree">'

            def loop(path, init=False, status=None, result=None, isTestcaseFolder=False):
                """ 
                Create nested menu tree.  var.counter keeps track
                of the amount of nested menus so it knows the 
                amount of </li></ul> to close at the end.
                
                <li><span class="caret">Green Tea</span>
                    <ul class="nested">
                        <li>Sencha</li>
                        <li>Gyokuro</li>
                        <li>Matcha</li>
                        <li>Pi Lo Chun</li>
                """
                if result in ['Failed', 'Aborted']:
                    result = f'<span class="textRed">{result}</span>'
                
                if init == True:
                    # testResultsPath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/08-23-2023-20:04:09:337297_9269/STAGE=Test_TASK=Demo_ENV=Samples-pythonSample
                    path = testResultsPath
                    getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{stage}&emsp;&ensp; {task}&emsp;&ensp; {env}</span>'
                    
                if init == False:
                    # FOLDER
                    folderName = path.split('/')[-1]
                    if isTestcaseFolder:
                        getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{folderName} &emsp;Status:{status} &emsp;Result:{result}</span>'
                    else:
                        getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{folderName}</span>'  
                        
                getPagesVars.html += '<ul class="nested">'
                getPagesVars.counter += 1
                            
                # FILE
                for eachFile in glob(f'{path}/*'):
                    if os.path.isfile(eachFile): 
                        filename = eachFile .split('/')[-1]
                
                        # JS format:
                        #    <object data="data/test.pdf" type="application/pdf" width="300" height="200">
                        #    <a href="data/test.pdf">test.pdf</a>
                        #    </object>
                        # 
                        # html
                        # <iframe src="http://docs.google.com/gview?
                        #     url=http://infolab.stanford.edu/pub/papers/google.pdf&embedded=true"
                        #     style="width:600px; height:500px;" frameborder="0">
                        # </iframe>
                        if '.pdf' in eachFile:
                            # ${{window.location.host}}
                            # User clicks on pdf file, getTestResultFileContents uses Django's FileResponse to read the PDF file
                            getPagesVars.html += f'<i class="fa-regular fa-file pr-2"></i><a href="/testResults/getTestResultFileContents?testResultFile={eachFile}" target="_blank">{filename}</a>'
                        else:
                            # getFileContents() is a JS function in sessionMgmt.html. It shows the file contents in a new web browser tab.
                            getPagesVars.html += f'<li><a href="#" onclick="getFileContents(this)" filePath="{eachFile}"><i class="fa-regular fa-file pr-2"></i>{filename}</a></li>'
                                                                
                # FOLDER
                for index,eachFolder in enumerate(glob(f'{path}/*')):
                    if os.path.isdir(eachFolder):
                        # Get the testcase results first so results could be shown next to the testcase folder
                        isTestcaseFolder = False
                        for eachFile in glob(f'{eachFolder}/*'):
                            if 'testSummary.json' in eachFile:
                                # Getting in here means the folder is a testcase folder because 
                                # only testcase folder has testSummary.json file
                                testcaseSummary = readJson(eachFile)
                                status = testcaseSummary['status']
                                result = testcaseSummary['result']
                                isTestcaseFolder = True
       
                        loop(eachFolder, init=False, status=status, result=result, isTestcaseFolder=isTestcaseFolder)
                        getPagesVars.html += '</li></ul>'
                        getPagesVars.counter -= 1
             
            loop(testResultsPath, init=True)
            
            for x in range(0, getPagesVars.counter):
                getPagesVars.html += '</ul></li>'
                
            getPagesVars.html += '</ul>'        

        return Response(data={'sessionData': sessionData, 'testcaseData': getPagesVars.html,
                              'stageTaskEnv': stageTaskEnv, 'errorMsg':errorMsg}, status=statusCode) 
        
        
        
class GetSessionDetails_new(APIView):        
    @verifyUserRole(webPage=Vars.webpage, action='GetSessionDetails')
    #@authenticateLogin
    def post(self, request):
        """ 
        Get the session details
        
        The folder toggler works in conjuntion with an addListener in getTestcaseData() 
        and keystackDetailedLogs CSS
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        
        # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/08-23-2023-20:04:09:337297_9269/STAGE=Test_TASK=Demo_ENV=Samples-pythonSample
        testResultsPath = request.data.get('testResultsPath', None)

        class getPagesVars:
            counter = 0
            html = ''
         
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"testResultsPath": testResultsPath}
            restApi = '/api/v1/pipeline/getSessionDetails'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetSessionDetails')
            if errorMsg:
                sessionData = None
                stageTaskEnv = None 
            else:    
                sessionData = response.json()['sessionData']
                stageTaskEnv = response.json()['stageTaskEnv']
                getPagesVars.html = response.json()['testcaseData']                          
        else:   
            try:
                if RedisMgr.redis:
                    keyName = f'envMgmt-{timestampFolderName}-STAGE={currentStage}_TASK={currentTask}_ENV={currentEnv}'
                    envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                            
                taskSummaryFile = f'{testResultsPath}/taskSummary.json'
                if os.path.exists(taskSummaryFile) is False:
                    raise Exception(f'TaskSummaryFile does not exists: {taskSummaryFile}')
            
                status = readJson(taskSummaryFile)
                # Verify if the overall test is terminated
                overallSummaryFile = f'{testResultsPath.split("STAGE")[0]}/overallSummary.json'
                overallStatus = readJson(overallSummaryFile)
                
                playbookFullPath = status['playbook']
                testcaseSortedOrderList = status.get('testcaseSortedOrderList', [])
                match = search(f'{GlobalVars.keystackTestRootPath}/Playbooks/([^ ]+)\.', playbookFullPath)
                if match:
                    playbook = match.group(1)
                else:
                    playbook = 'Unknown'

                # STAGE=Tests_TASK=CustomPythonScripts_ENV=loadcoreSample
                match = search('(STAGE=.*)_TASK.*', testResultsPath)
                if match:
                    stage = match.group(1).replace('=', ': ')
                    
                match = search('STAGE=.*_(TASK=.*)_ENV', testResultsPath)
                if match:
                    task= match.group(1).replace('=', ': ')

                match = search('STAGE=.*_TASK=.*_(ENV.*)', testResultsPath)
                if match:
                    env = match.group(1).replace('=', ': ')
                
                statusCode = HtmlStatusCodes.success

            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                #print('\n--- getSessionDetails error:', traceback.format_exc(None, errMsg))
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetSessionDetails', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

            testTime = f"Playbook: {playbook}<br>Started: {status['started']}<br>Stopped: {status['stopped']}<br>"
            
            try:
                testTime += f"Duration: {status['testDuration']}<br>"
            except:
                # test time may not be ready yet
                pass
            
            def createCard(inserts, col="col-xl-4"):
                data = f"""<div class="{col} col-md-6 mb-4">
                                <div class="card border-left-primary h-100 py-0">
                                    <div class="card-body">
                                        <div class=f"row no-gutters align-items-center">
                                            {inserts}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        """  
                return data

            stageTaskEnv = f'{stage}&ensp;&emsp;{task}&ensp;&emsp;{env}'
            sessionData = '<div class="row">'
            sessionData += createCard(testTime)
            
            #if status['status'] not in ['Completed', 'Terminated', 'Aborted']:
            if status['status'] not in Vars.commonPipelineStatus:
                if overallStatus['status'] == 'Terminated':
                    status2 = f'<span style="color:blue">Terminated</span>'
                else:
                    status2 = f'<span class="blink"><span style="color:blue">{status["status"]}</span></span>'
                
                sessionData += createCard(f"""<div style="font-size:20px; padding-left:0px">Status: {status2}</span></div><br>
                                        Total Testcases: {status['totalCases']}&emsp;&emsp; 
                                        Total Passed: {status['totalPassed']}&emsp;&emsp;
                                        Total Failed: {status['totalFailed']}&emsp;&emsp;<br>
                                        Progress: {status['progress']}
                                        """)
            else:
                # #10b332 = Green
                sessionData += createCard(f"""<div style="font-size:20px; padding-left:0px">Status: <span style="color:blue">{status['status']}</div><br>
                                        Total Testcases: {status['totalCases']}&emsp;&emsp; 
                                        Total Passed: {status['totalPassed']}&emsp;&emsp;
                                        Total Failed: {status['totalFailed']}&emsp;&emsp;<br>
                                        Progress: {status['progress']}
                                        """)

            if status['result'] in ['Failed', 'Incomplete']:
                status2 = f'<span style="color:red">{status["result"]}</span>'
            elif status['result'] == 'Passed':
                status2 = f'<span style="color:#10b332">{status["result"]}</span>'
            else:
                # Not-Ready
                status2 = f'<span style="color:blue">{status["result"]}</span>'
                    
            sessionData += createCard(f"""<div style="font-size:20px; padding-left:0px">Result: {status2}</div><br>
                                        Test Cases Aborted: {status['totalTestAborted']}&emsp;&emsp;
                                        Test Cases Skipped: {status['totalSkipped']}&emsp;&emsp;
                                        """)
            sessionData += "</div>"

            """
            The folder toggler works in conjuntion with an addListener in getTestcaseData() 
            
            <nav class="keystackDetailedLogs card py-0 mb-0">
                <ul class="nav flex-column" id="nav_accordion">
                    <li class="nav-item has-submenu">
                        <a class="nav-link" href="#"> resultFolder </a>
                        <ul class="submenu collapse">
                            <li><a class="nav-link" href="#"> File 1 </a></li>
                            <li><a class="nav-link" href="#"> File 2 </a></li>
                            <li><a class="nav-link" href="#"> File 3 </a> </li>
                        </ul>
                    </li>
                </ul>
            </nav>
            """
    
            if status['currentlyRunning']:
                sessionData += '<div class="row">'
                sessionData += createCard(f"Currently Running: {status['currentlyRunning']}", col="col-xl-12")       
                sessionData += "</div>"     

            if status.get('playlistExclusions', []):
                sessionData += 'Playlist Exclusions:<br>'
                for eachExclusion in status['playlistExclusions']:
                    sessionData += f'&emsp;&emsp;- {eachExclusion}<br>'
                    
                sessionData += '<br>'

            getPagesVars.html = f'<ul id="testResultFileTree">'

            def loop(path, init=False, status=None, result=None, isTestcaseFolder=False):
                """ 
                Create nested menu tree.  var.counter keeps track
                of the amount of nested menus so it knows the 
                amount of </li></ul> to close at the end.
                
                <li><span class="caret">Green Tea</span>
                    <ul class="nested">
                        <li>Sencha</li>
                        <li>Gyokuro</li>
                        <li>Matcha</li>
                        <li>Pi Lo Chun</li>
                """
                if result in ['Failed', 'Aborted']:
                    result = f'<span class="textRed">{result}</span>'
                
                if init == True:
                    # testResultsPath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/08-23-2023-20:04:09:337297_9269/STAGE=Test_TASK=Demo_ENV=Samples-pythonSample
                    path = testResultsPath
                    getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{stage}&emsp;&ensp; {task}&emsp;&ensp; {env}</span>'
                    
                if init == False:
                    # FOLDER
                    folderName = path.split('/')[-1]
                    if isTestcaseFolder:
                        getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{folderName} &emsp;Status:{status} &emsp;Result:{result}</span>'
                    else:
                        getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{folderName}</span>'  
                        
                getPagesVars.html += '<ul class="nested">'
                getPagesVars.counter += 1
                            
                # FILE
                for eachFile in glob(f'{path}/*'):
                    if os.path.isfile(eachFile): 
                        filename = eachFile .split('/')[-1]
                
                        # JS format:
                        #    <object data="data/test.pdf" type="application/pdf" width="300" height="200">
                        #    <a href="data/test.pdf">test.pdf</a>
                        #    </object>
                        # 
                        # html
                        # <iframe src="http://docs.google.com/gview?
                        #     url=http://infolab.stanford.edu/pub/papers/google.pdf&embedded=true"
                        #     style="width:600px; height:500px;" frameborder="0">
                        # </iframe>
                        if '.pdf' in eachFile:
                            # ${{window.location.host}}
                            # User clicks on pdf file, getTestResultFileContents uses Django's FileResponse to read the PDF file
                            getPagesVars.html += f'<i class="fa-regular fa-file pr-2"></i><a href="/testResults/getTestResultFileContents?testResultFile={eachFile}" target="_blank">{filename}</a>'
                        else:
                            # getFileContents() is a JS function in sessionMgmt.html. It shows the file contents in a new web browser tab.
                            getPagesVars.html += f'<li><a href="#" onclick="getFileContents(this)" filePath="{eachFile}"><i class="fa-regular fa-file pr-2"></i>{filename}</a></li>'
                                                                
                # FOLDER
                for index,eachFolder in enumerate(glob(f'{path}/*')):
                    if os.path.isdir(eachFolder):
                        # Get the testcase results first so results could be shown next to the testcase folder
                        isTestcaseFolder = False
                        for eachFile in glob(f'{eachFolder}/*'):
                            if 'testSummary.json' in eachFile:
                                # Getting in here means the folder is a testcase folder because 
                                # only testcase folder has testSummary.json file
                                testcaseSummary = readJson(eachFile)
                                status = testcaseSummary['status']
                                result = testcaseSummary['result']
                                isTestcaseFolder = True
       
                        loop(eachFolder, init=False, status=status, result=result, isTestcaseFolder=isTestcaseFolder)
                        getPagesVars.html += '</li></ul>'
                        getPagesVars.counter -= 1
             
            loop(testResultsPath, init=True)
            
            for x in range(0, getPagesVars.counter):
                getPagesVars.html += '</ul></li>'
                
            getPagesVars.html += '</ul>'        

        return Response(data={'sessionData': sessionData, 'testcaseData': getPagesVars.html,
                              'stageTaskEnv': stageTaskEnv, 'errorMsg':errorMsg}, status=statusCode) 
        
        
def getPipelines():
    return glob(f'{GlobalVars.pipelineFolder}/*.yml')

def getArtifacts(topLevelFolderFullPath):
    """
    Get result logs
    
    https://www.w3schools.com/howto/howto_js_treeview.asp

    <ul id="testResultFileTree">
        <li><span class="caret">Beverages</span>
            <ul class="nested">
                <li>Water</li>
                <li>Coffee</li>
                <li><span class="caret">Tea</span>
                    <ul class="nested">
                        <li>Black Tea</li>
                        <li>White Tea</li>
                        <li><span class="caret">Green Tea</span>
                            <ul class="nested">
                                <li>Sencha</li>
                                <li>Gyokuro</li>
                                <li>Matcha</li>
                                <li>Pi Lo Chun</li>
                            </ul>
                        </li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>
    
    Requirements:
        - CSS: <link href={% static "commons/css/testResultsTreeView.css" %} rel="stylesheet" type="text/css">
        - html template needs to call addListeners() and getFileContents()
    """
    class getPagesVars:
        counter = 0
        
    timestampResultFolder = topLevelFolderFullPath.split('/')[-1]
    getPagesVars.html = f'<ul id="testResultFileTree">'

    def loop(path, init=False):
        """ 
        Create nested menu tree.  var.counter keeps track
        of the amount of nested menus so it knows the 
        amount of </li></ul> to close at the end.
        
        <li><span class="caret">Green Tea</span>
            <ul class="nested">
                <li>Sencha</li>
                <li>Gyokuro</li>
                <li>Matcha</li>
                <li>Pi Lo Chun</li>
        """
        if init == True:
            path = topLevelFolderFullPath
            getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{timestampResultFolder}</span>' 
        
        if init == False:
            # FOLDER
            folderName = path.split('/')[-1]
            getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{folderName}</span>'  
                
        getPagesVars.html += '<ul class="nested">'
        getPagesVars.counter += 1
                    
        # FILE
        for eachFile in glob(f'{path}/*'):
            if os.path.isfile(eachFile): 
                filename = eachFile .split('/')[-1]

                # Open the modifyFileModal and get the file contents                  
                #getPagesVars.html += f'<li><a class="nav-link" href="#" onclick="getFileContents(this)" filePath="{eachFile}"  data-bs-toggle="modal" data-bs-target="#openFileModal"><i class="fa-regular fa-file pr-2"></i> {filename} </a></li>'
        
                # JS format:
                #    <object data="data/test.pdf" type="application/pdf" width="300" height="200">
                #    <a href="data/test.pdf">test.pdf</a>
                #    </object>
                # 
                # html
                # <iframe src="http://docs.google.com/gview?
                #     url=http://infolab.stanford.edu/pub/papers/google.pdf&embedded=true"
                #     style="width:600px; height:500px;" frameborder="0">
                # </iframe>
                if '.pdf' in eachFile:
                    # ${{window.location.host}}
                    # User clicks on pdf file, getTestResultFileContents uses Django's FileResponse to read the PDF file
                    getPagesVars.html += f'<i class="fa-regular fa-file pr-2"></i><a href="/testResults/getTestResultFileContents?testResultFile={eachFile}" target="_blank">{filename}</a>'
                else:
                    # getFileContents() is a JS function in sessionMgmt.html. It shows the file contents in a new web browser tab.
                    getPagesVars.html += f'<li><a href="#" onclick="getFileContents(this)" filePath="{eachFile}"><i class="fa-regular fa-file pr-2"></i>{filename}</a></li>'
                                                        
        # FOLDER
        for eachFolder in glob(f'{path}/*'):        
            if os.path.isdir(eachFolder):
                loop(eachFolder, init=False)
                getPagesVars.html += '</li></ul>'
                getPagesVars.counter -= 1
        
    loop(topLevelFolderFullPath, init=True)
    
    for x in range(0, getPagesVars.counter):
        getPagesVars.html += '</ul></li>'
        
    getPagesVars.html += '</ul>'

    return getPagesVars.html

    
class GetPipelines(APIView):
    @swagger_auto_schema(tags=['/api/v1/pipelinesUI'], manual_parameters=[], 
                         operation_description="Get list of pipeline names")

    @verifyUserRole(webPage=Vars.webpage, action='GetPipelines')
    def get(self, request, data=None):
        """
        Description:
            Get a list of saved pipelines names to play
        
        GET /api/vi/pipelinesUI
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/pipelinesUI
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X GET http://192.168.28.7:8000/api/v1/pipelinesUI/ 
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/pipelinesUI
            
            session = requests.Session()
            response = session.request('get', 'http://localhost:8000/api/v1/pipelinesUI')
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        pipelines = []
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelinesUI'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPipelines')  
            pipelines = response.json()['pipelines']
            
        else:                           
            pipelineFile = f'{GlobalVars.pipelineFolder}'
            for eachPipeline in glob(f'{GlobalVars.pipelineFolder}/*.yml'):
                eachPipeline = eachPipeline.split('/')[-1].split('.')[0]
                pipelines.append(eachPipeline)
                
        return Response(data={'pipelines':pipelines, 'errorMsg': errorMsg, 'status': 'success'}, status=statusCode)


class DeletePipelineSessions(APIView):
    pipelines = openapi.Parameter(name='pipelines', description="Delete pipeline sessions",
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_ARRAY, 
                                  items=openapi.Items(type=openapi.TYPE_STRING)) 

    domain = openapi.Parameter(name='pipelines', description="Domain is used only if pipelines is 'all'",
                               required=False, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)   
        
    @swagger_auto_schema(tags=['/api/v1/pipeline/deletePipelineSessions'], manual_parameters=[pipelines], 
                         operation_description="Delete pipeline sessions")
    
    @verifyUserRole(webPage=Vars.webpage, action='DeletePipelineSessions', exclude=['engineer'])
    @authenticateLogin
    def post(self, request, data=None):
        """
        Description:
            Delete pipeline test sessions from web UI checkboxes
            
        Parameters:
            pipelines: <list>: Full path to top-level test session result folder
                       [{'testResultPath': <full path}]
        
        POST /api/v1/pipeline/delete
        ---
        Examples:
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipeline/deletePipelineSessions?pipelines=pipelines
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -d "pipelines=session1" -d "pipelines=session2"  -X POST http://192.168.28.7:8000/api/v1/pipeline/deletePipelineSessions
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -d '{"pipelines": ["session1", "session2"]}'  -X POST http://192.168.28.7:8000/api/v1/pipeline/deletePipelineSessions
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipeline/deletePipelineSessions')
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        sessionId = None
        
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                # pipelines: 'all' | list of timestamped folders
                pipelines = request.GET.get('pipelines', [])
                
                # domain: Only used if pipelines = 'all'
                domain = request.GET.get('domain', None)
            except Exception as error:
                error = f'Expecting key pipelines, but got: {request.GET}'
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                # pipelines: 'all' | list of timestamped folders
                pipelines = request.data.get('pipelines', [])
                
                # domain: Only used if pipelines = 'all'
                domain = request.data.get('domain', None)
            except Exception as errMsg:
                errorMsg = f'Expecting key pipelines, but got: {request.data}'
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"pipelines": pipelines, "domain": domain}
            restApi = '/api/v1/pipelines/deletePipelineSessions'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeletePipelineSessions')
        else:
            try:
                # If "Delte results" checkbox is unchecked: 
                #    {'sessions': [{'sessionId': 'hgee3', 'testResultsPath': None}]}
                # If "Delte results" checkbox is checked:
                #    {'sessions': [{'sessionId': 'hgee3', 'testResultsPath': None}, {'sessionId': 'hgee3', 'testResultsPath': '/opt/KeystackTests/Results/PLAYBOOK=pythonSample/09-24-2022-15:55:58:091405_hgee3'}]}
                # [{'sessionId': 'hgee3', 'testResultsPath': None}, {'sessionId': 'hgee3', 'testResultsPath': None}]
                additionalMessage = ''
                isEnvsOnHold = False

                if pipelines == 'all':
                    pipelines = []
                    plabyookPaths = f'{GlobalVars.resultsFolder}/DOMAIN={domain}/PLAYBOOK=*'
                    for playbookPath in glob(f'{GlobalVars.resultsFolder}/DOMAIN={domain}/PLAYBOOK=*'):
                        for timestampFolderFullPath in glob(f'{playbookPath}/*'):
                            pipelines.append({'testResultsPath': timestampFolderFullPath})
                    
                for eachSession in pipelines:
                    # eachSession {'testResultsPath': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/11-16-2022-15:25:11:957919_hubogee'}
                    
                    # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/10-26-2022-14:54:49:859583_1600
                    testResultsPath     = eachSession['testResultsPath']
                    timestampFolderName = testResultsPath.split('/')[-1]
                    overallSummaryFile  = f'{testResultsPath}/overallSummary.json'
                    testSessionLog      = f'{testResultsPath}/testSession.log' 
                    envMgmtPath         = f'{testResultsPath}/.Data/EnvMgmt'
                    envList             = [] 
                    isEnvsOnHold        = False
                    
                    if RedisMgr.redis:
                        redisOverallSummary = f'overallSummary-domain={domain}-{timestampFolderName}'
                        redisEnvMgmt = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'envMgmt-{timestampFolderName}*')
                        overallSummaryData = RedisMgr.redis.getCachedKeyData(keyName=redisOverallSummary)
                        pipelineCurrentStatus = overallSummaryData['status']
                        processId = overallSummaryData['processId']
                        sessionId = overallSummaryData['sessionId']
                        
                        if pipelineCurrentStatus == 'Running':
                            # Terminate the running the process
                            if keystackSettings['platform'] == 'linux':
                                result, process = execSubprocessInShellMode(f'sudo kill -9 {processId}', showStdout=False)
                                
                            if keystackSettings['platform'] == 'docker':
                                result, process = execSubprocessInShellMode(f'kill -9 {processId}', showStdout=False)

                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipelineSessions', msgType='Warning', msg=f'Terminated running pipeline: {sessionId}')
                                                            
                        # Don't delete the pipeline if the env is on hold for debugging
                        for envTask in redisEnvMgmt:
                            envTaskData = RedisMgr.redis.getCachedKeyData(keyName=envTask)
                            if envTaskData == {}:
                                continue
                            
                            if envTaskData['holdEnvsIfFailed'] and envTaskData['envIsReleased'] is False:
                                if overallSummaryData['status'] not in ['Aborted', 'Terminated']:
                                    isEnvsOnHold = True
                                    continue

                            envMgmtObj = ManageEnv()                                        
                            envMgmtObj.setenv = envTaskData['env']
                            session = {'user': envTaskData['user'], 'sessionId': envTaskData['sessionId'], 'stage': envTaskData['stage'], 'task': envTaskData['task']}
                            envMgmtObj.removeFromActiveUsersList([session])
                            envMgmtObj.removeFromWaitList(envTaskData['sessionId'], envTaskData['user'], envTaskData['stage'], envTaskData['task'])
                            envList.append(envTaskData['env'])
                            
                            if len(envTaskData['portGroups']) > 0:
                                for portGroup in envTaskData['portGroups']:
                                    ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromActiveUsersList(envTaskData['sessionId'], testSessionLog)
                                    ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromWaitList(envTaskData['sessionId'], testSessionLog)
                            
                            RedisMgr.redis.deleteMatchingPatternKeys(pattern=f'envMgmt-{timestampFolderName}*')
                                
                        if isEnvsOnHold is False:
                            RedisMgr.redis.deleteKey(keyName=redisOverallSummary)
                    else:
                        if os.path.exists(overallSummaryFile):
                            overallSummaryData = readJson(overallSummaryFile)                           
                            pipelineCurrentStatus = overallSummaryData['status']
                            processId = overallSummaryData['processId']
                            sessionId = overallSummaryData['sessionId']
                            
                            if pipelineCurrentStatus == 'Running':
                                # Terminate the running the process
                                if keystackSettings['platform'] == 'linux':
                                    result, process = execSubprocessInShellMode(f'sudo kill -9 {processId}', showStdout=False)
                                    
                                if keystackSettings['platform'] == 'docker':
                                    result, process = execSubprocessInShellMode(f'kill -9 {processId}', showStdout=False)

                                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipelines', msgType='Warning', msg=f'Terminated running pipeline: {sessionId}')
                                                        
                            for envMgmtFile in glob(f'{envMgmtPath}/*.json'):
                                envMgmtData = readJson(envMgmtFile)
                                if envMgmtData == {}:
                                    continue

                                if envTaskData['holdEnvsIfFailed'] and envTaskData['envIsReleased'] is False:
                                    if overallSummaryData['status'] not in ['Aborted', 'Terminated']:
                                        isEnvsOnHold = True
                                        continue
                                
                                envMgmtObj = ManageEnv()                                        
                                envMgmtObj.setenv = envMgmtData['env']
                                session = {'user': envMgmtData['user'], 'sessionId': envMgmtData['sessionId'], 'stage': envMgmtData['stage'], 'task': envMgmtData['task']}
                                envMgmtObj.removeFromActiveUsersList([session])
                                envMgmtObj.removeFromWaitList(envMgmtData['sessionId'], envMgmtData['user'], envMgmtData['stage'], envMgmtData['task'])
                                envList.append(envMgmtData['env'])
                                
                                if len(envMgmtData['portGroups']) > 0:
                                    for portGroup in envMgmtData['portGroups']:
                                        ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromActiveUsersList(envMgmtData['sessionId'], testSessionLog)
                                        ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromWaitList(envMgmtData['sessionId'], testSessionLog)
                                        
                    if isEnvsOnHold is False and os.path.exists(testResultsPath):
                        execSubprocessInShellMode(f'sudo rm -rf {testResultsPath}')        
                                
                    additionalMessage = f'Released Envs: {envList}'
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipelines', msgType='Info', msg=f'Deleted pipelines {pipelines}.<br>{additionalMessage}')
                                                  
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                print('DeletePipeline error:', traceback.format_exc(None, errMsg))
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipelines', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeletePipelines(APIView):
    """ 
    Delete a saved webhook pipeline
    
    Parameters:
        pipelines: <list> 
    """
    @verifyUserRole(webPage=Vars.webpage, action='DeletePipelines', exclude=['engineer'])
    def post(self, request):
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        if request.GET:
            # Rest APIs with inline params come in here
            try:
                pipelines = request.GET.get('pipelines')
            except Exception as error:
                errorMsg = f'Expecting key pipelines, but got: {request.GET}'
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                pipelines = request.data['pipelines']
            except Exception as errMsg:
                errorMsg = f'Expecting key pipelines, but got: {request.data}'
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
 
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"pipelines": pipelines}
            restApi = '/api/v1/pipelines/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeletePipelines')
        else:                
            try:
                # eachPipeline: qa-test | /opt/KeystackTests/Pipelines/qa-test.yml
                for eachPipeline in pipelines:
                    if GlobalVars.pipelineFolder not in eachPipeline:
                        eachPipeline = f'{GlobalVars.pipelineFolder}/{eachPipeline}'
                        if '.ym' not in eachPipeline:
                            eachPipeline = f'{eachPipeline}.yml'
                            
                    if os.path.exists(eachPipeline):
                        os.remove(eachPipeline)
                        pipelineName = eachPipeline.split('/')[-1].split('.')[0]
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipelines', msgType='Info',
                                                msg=f'Pipeline name: {pipelineName}', forDetailLogs='')
                    
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipelines', msgType='Error',
                                          msg=f'Pipeline:{pipelineName}: {errorMsg}', forDetailLogs=traceback.format_exc(None, errMsg))
       
        return Response(data={'status':status, 'errorMsg': errorMsg}, status=statusCode)  
    

class GetPipelinesDropdown(APIView):
    swagger_schema = None

    def post(self,request):
        """ 
        Dropdown menu for user to select a pipeline to run
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        pipelines = []
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/dropdown'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPipelinesDropdown')
            pipelines = response.json()['pipelines']
                  
        else:           
            try:
                pipelines = '<ul class="dropdown-menu dropdownSizeSmall dropdownFontSize">'
                        
                for eachPipeline in getPipelines():
                    pipeline = eachPipeline.replace(f'{GlobalVars.pipelineFolder}/', '').split('.')[0]
                    pipelines += f'<li class="dropdown-item" pipeline="{eachPipeline}" onclick="playPipeline(this)">{pipeline}</li>'
                
                pipelines += '</ul>'
                            
            except Exception as errMsg:
                pipelines = []
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelines', msgType='Error',
                                          msg=errMsg,
                                          forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
        
        return Response({'pipelines': pipelines, 'status':status, 'errorMsg': errorMsg}, status=statusCode)
    

class SavePipeline(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='SavePipeline', exclude=['engineer'])
    @authenticateLogin
    def post(self,request):
        """ 
        Create a new pipeline
        
        Parameters: 
        Playbook
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # request.data: 
        #     {'pipelineName': 'abc', 'remoteController': '192.168.28.10:28028', 'playbook': 'Samples/pythonSample', 'debug': True, 'emailResults': False, 'awsS3': False, 'jira': False, 'pauseOnFailure': False, 'holdEnvsIfFailed': False, 'abortTestOnFailure': False, 'includeLoopTestPassedResults': False, 'sessionId': 'hgee2', 'domain': 'Communal', 'testConfigs': 'demoChanges'}
        pipeline = request.data.get('pipeline', None)
        playbook = request.data.get('playbook', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"pipeline": pipeline, "playbook": playbook}
            restApi = '/api/v1/pipelines/save'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SavePipeline')  
        else:                    
            try:
                pipelineFilename = f'{GlobalVars.pipelineFolder}/{pipeline}.yml'
            
                if playbook == '':
                    status = 'failed'
                    errorMsg = 'You must select a playbook'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
                    return Response({'status':status, 'errorMsg': errorMsg}, status=statusCode)
                
                # /opt/KeystackTests/Pipelines/DOMAIN=Communal/Samples-Simple1.yml qa-test
                for eachPipelineName in getPipelines():
                    currentPipeline = eachPipelineName.split('/')[-1]
                    if pipeline in currentPipeline:
                        status = 'failed'
                        errorMsg = f'Pipeline name already exists: {pipeline}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Error',
                                                  msg=errorMsg, forDetailLogs='')
                        return Response({'status':status, 'errorMsg': errorMsg}, status=statusCode)
                                 
                if os.path.exists(GlobalVars.pipelineFolder) == False:
                    mkdir2(GlobalVars.pipelineFolder, stdout=False)
                
                writeToYamlFile(request.data, pipelineFilename, mode='w')
                chownChmodFolder(GlobalVars.pipelineFolder,
                                 user=GlobalVars.user, userGroup=GlobalVars.userGroup, permission=770, stdout=False)
            
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Info',
                                          msg=f'playbook={playbook}  pipelineName={pipeline}', forDetailLogs='')
                            
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'status':status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetPipelineTableData(APIView):
    def post(self, request):
        """ 
        Get detailed Pipeline data table 
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"remoteController": remoteControllerIp}
            restApi = '/api/v1/pipelines/tableData'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetPipelineTableData')

            html = response.json()['pipelineTableData']
                  
        else:
            html = '<table class="tableMessages table-bordered">'
            html += '<thead>'
            html += '<tr>'
            html += '<th>Delete</th>'
            html += '<th>Existing Pipelines</th>'
            html += '<th>Parameters</th>'
            html += '</tr>'
            html += '</thead>'

            try:
                for eachPipeline in glob(f'{GlobalVars.pipelineFolder}/*.yml'):
                    pipelineParams = readYaml(eachPipeline)
                    pipelineName = eachPipeline.split('/')[-1].split('.')[0]
                    paramsInStrFormat = ''
                    for key,value in pipelineParams.items():
                        paramsInStrFormat += f'{key}:{value}&emsp;'

                    html += '<tr>'
                    html += f'<td><center><input type="checkbox" name="deletePipeline" pipelineFullPath={eachPipeline} /></center></td>'
                    html += f'<td>{pipelineName}</td>'
                    html += f'<td class="marginLeft0">{paramsInStrFormat}</td>'
                    html += '</tr>'
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelineTableData', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
                        
            html += '</table>'
                          
        return Response({'pipelineTableData':html, 'status':status, 'errorMsg': errorMsg}, status=statusCode)
    
            
class GetTestReport(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetTestReport')
    def post(self,request):
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                testReportPath = request.GET.get('testReportPath')
            except Exception as error:
                errorMsg = f'Expecting key testReportPath, but got: {request.GET}'
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                testReportPath = request.data['testReportPath']
            except Exception as errMsg:
                error = f'Expecting key testReportPath, but got: {request.data}'
                return Response(data={'status': 'failed', 'errorMsg': error}, status=statusCode)
 
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"testReportPath": testReportPath}
            restApi = '/api/v1/pipelines/getTestReport'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestReport')
            if errorMsg:
                status = 'failed'
                testReport = ''
            else:
                testReport = response.json()['testReportInsert']
                       
        else:                    
            try:
                testReport = readFile(testReportPath)
                statusCode = HtmlStatusCodes.success
            except Exception as errMsg:
                errorMsg = str(errMsg)
                testReport = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestReport', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                testReport = f'Error: {errMsg}'

        return Response(data={'testReportInsert':testReport, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
    
class GetTestLogs(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetTestLogs')
    def post(self,request):
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        testLogs = ''
        testResultsPath = ''
        
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                testResultPath = request.GET.get('testResultPath')
            except Exception as error:
                error = f'Expecting key testResultPath, but got: {request.GET}'
                return Response(data={'status': 'failed', 'errorMsg': error}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                testResultPath = request.data['testResultPath']
            except Exception as errMsg:
                error = f'Expecting key testResultPath, but got: {request.data}'
                return Response(data={'status': 'failed', 'errorMsg': error}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"testResultPath": testResultPath}
            restApi = '/api/v1/pipelines/getTestLogs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestLogs')

            testLogs = response.json()['testLogsHtml']
            testResultPath = response.json()['test'].split('/')[-1]
     
        else:         
            try:
                testLogs = getArtifacts(testResultPath)
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                testResultsPath = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestLogs', msgType='Error',
                                          msg=errMsg, forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
                testlogs = f"Error: {errMsg}"

        return Response(data={'status':status, 'errorMsg':errorMsg, 'testLogsHtml': testLogs, 
                              'test': testResultPath.split('/')[-1]}, status=statusCode)
        
# ---- Job Scheduler ----
 
class AddJobSchedule(APIView):                                           
    @verifyUserRole(webPage=Vars.webpage, action='AddJobSchedule', exclude=['engineer'])
    def post(self, request):
        """ 
        Schedule a cron job
        
            # Example of job definition:
            # .---------------- minute (0 - 59)
            # |  .------------- hour (0 - 23)
            # |  |  .---------- day of month (1 - 31)
            # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
            # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
            # |  |  |  |  |
            # *  *  *  *  * user-name command to be executed
        """
        # body: {'minute': '*', 'hour': '*', 'dayOfMonth': '*', 'month': '*', 'dayOfWeek': '*', 'removeJobAfterRunning': False, 'controller': '192.168.28.7:8000', 'playbook': '/opt/KeystackTests/Playbooks/pythonSample.yml', 'debug': False, 'emailResults': False, 'awsS3': False, 'jira': False, 'pauseOnFailure': False, 'holdEnvsIfFailed': False, 'abortTestOnFailure': False, 'includeLoopTestPassedResults': False, 'sessionId': '', 'domain': 'Communal'}
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        keystackUser = GlobalVars.user
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        minute                       = request.data.get('minute', None)
        hour                         = request.data.get('hour', None)
        dayOfMonth                   = request.data.get('dayOfMonth', None)
        month                        = request.data.get('month', None)
        dayOfWeek                    = request.data.get('dayOfWeek', None)

        reservationUser              = request.data.get('reservationUser', user)
        reservationNotes             = request.data.get('reservationNotes', '')          
        removeJobAfterRunning        = request.data.get('removeJobAfterRunning', None)
        domain                       = request.data.get('domain', None)
        sessionId                    = request.data.get('sessionId', None)
        
        # playbook: DOMAIN=Communal/Samples/advance
        playbook                     = request.data.get('playbook', None)
        debugMode                    = request.data.get('debug', None)
        awsS3                        = request.data.get('awsS3', None)
        jira                         = request.data.get('jira', None)
        emailResults                 = request.data.get('emailResults', None)
        pauseOnFailure               = request.data.get('pauseOnFailure', None)
        holdEnvsIfFailed             = request.data.get('holdEnvsIfFailed', None)
        abortTestOnFailure           = request.data.get('abortTestOnFailure', None)
        includeLoopTestPassedResults = request.data.get('includeLoopTestPassedResults', [])
        
        # ['demo2.yml', 'demo1.yml', 'qa/sample2.yml']
        testConfigs                    = request.data.get('testConfigs', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            #params = {"minute": minute, "hour": hour, "dayOfMonth": dayOfMonth, "month": month, "dayOfWeek": dayOfWeek, "reservationUser": reservationUser, "removeJobAfterRunning": removeJobAfterRunning, "domain": domain, "sessionId": sessionId, "playbook": playbook, "debugMode": debugMode, "awsS3": awsS3, "jira": jira, #"emailResults": emailResults, "pauseOnFailure": pauseOnFailure, "holdEnvsIfFailed": holdEnvsIfFailed, "abortTestOnFailure": abortTestOnFailure, #"includeLoopTestPassedResults": includeLoopTestPassedResults, }
            
            restApi = '/api/v1/pipelines/jobScheduler/add'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, request.data, 
                                                                           user, webPage=Vars.webpage, action='AddScheduledJob')
        else:
            try:
                localHostIp = keystackSettings.get('localHostIp', 'localhost')
                keystackIpPort = keystackSettings.get('keystackIpPort', '28028')
                schedule = f'playbook={playbook} minute={minute} hour={hour} day={dayOfMonth} month={month} dayOfWeek={dayOfWeek}' 
                  
                if JobSchedulerAssistant().isCronExists(playbook, minute, hour, dayOfMonth, month, dayOfWeek):
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddJobSchedule', 
                                              msgType='Failed', msg=f'Cron job already exists: {schedule}')
                    return Response({'status':'failed', 'errorMsg': 'Cron Job already exists'}, status=statusCode)
                
                # REST API: Run playbook function is in Playbook apiView.py
                # For job scheduling, include the param -webhook to bypass verifying api-key
                
                # crontab command-line
                # newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} {keystackUser} '
                # newJob += f'curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}'
                # newJob += f'&sessionId={sessionId}&playbook={playbook}&awsS3={awsS3}&jira={jira}&pauseOnFailure={pauseOnFailure}&debug='
                # newJob += f'{debugMode}&domain={domain}&testConfigs={testConfigs}&holdEnvsIfFailed={holdEnvsIfFailed}&abortTestOnFailure={abortTestOnFailure}'
                # newJob += f'&includeLoopTestPassedResults={includeLoopTestPassedResults}&scheduledJob={schedule}'
                # newJob += f'&removeJobAfterRunning={removeJobAfterRunning}&webhook=true"'
                # newJob += f' -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/playbook/runPlaybook'

                newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} {keystackUser} '
                newJob += f'curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}'
                newJob += f'&sessionId={sessionId}&playbook={playbook}&awsS3={awsS3}&jira={jira}&pauseOnFailure={pauseOnFailure}&debug='
                newJob += f'{debugMode}&domain={domain}&holdEnvsIfFailed={holdEnvsIfFailed}&abortTestOnFailure={abortTestOnFailure}'
                newJob += f'&includeLoopTestPassedResults={includeLoopTestPassedResults}&scheduledJob={schedule}'
                
                if len(testConfigs) > 0:
                    testConfigStrList = ''
                    for index, testConfig in enumerate(testConfigs):
                        testConfigStrList += f'{testConfig}'
                        if testConfig != testConfigs[-1]:
                            testConfigStrList += ','
                        
                    newJob += f'&testConfigs={testConfigStrList}'
                     
                newJob += f'&removeJobAfterRunning={removeJobAfterRunning}&webhook=true"'
                newJob += f' -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/playbook/runPlaybook'
                                          
                # if RedisMgr.redis:
                #     keyName = f'scheduler-add-{playbook}'                    
                #     RedisMgr.redis.write(keyName=keyName, data=newJob)
                
                data = {'cron': newJob, 'notes': reservationNotes}
                
                # Add job to mongoDB scheduler: env|playbook
                JobSchedulerAssistant().addToScheduler(DB.name, 'playbook', data)
                
                # Add job to /etc/crontab
                JobSchedulerAssistant().createCronJob(newJob)
                                          
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddJobSchedule', msgType='Info', msg=newJob.replace('&webhook=true', ''))            
            
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddJobSchedule', msgType='Error',
                                          msg=errMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeleteScheduledJob(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteScheduledJob', exclude=["engineer"])    
    def post(self, request):
        """ 
        Delete a scheduled job.  Called from template.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        removeScheduledJobs = request.data.get('removeScheduledJobs', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"removeScheduledJobs": removeScheduledJobs}
            restApi = '/api/v1/pipelines/jobScheduler/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteScheduledJob')
        else:        
            try:
                #  [{playbook, month, day, hour, min}, {}, ...]
                removeJobList = []
                
                for cron in removeScheduledJobs:
                    # cron: {'jobSearchPattern': 'playbook=DOMAIN=Communal/Samples/advance', 'month': '\\*', 
                    # 'dayOfMonth': '\\*', 'hour': '11', 'minute': '\\*', 'dayOfWeek': '\\*'}
                    playbook = cron['jobSearchPattern'].split('playbook=')[-1]
                    removeJobList.append(cron)
                    
                    # if RedisMgr.redis:
                    #     keyName = f'scheduler-remove-{playbook}'  
                    #     data = RedisMgr.redis.getCachedKeyData(keyName=keyName) 

                    #     for index, eachCron in enumerate(data):
                    #         if eachCron == cron:  
                    #             data.pop(index)          
                    #             RedisMgr.redis.updateKey(keyName=keyName, data=data)
                    #             break
                    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledJob', msgType='Info',
                                              msg=cron, forDetailLogs='')
                
                # This removes from crontab and mongodb        
                JobSchedulerAssistant().removeCronJobs(removeJobList, dbObj=DB.name, queryName='playbook')
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledJob', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ScheduledJobs(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeletePipelines')
    def post(self, request):        
        """         
        Create a data table of scheduled jobs. Called by html template.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        html = ''
        areThereJobs = False
            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/jobScheduler/scheduledJobs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ScheduledJobs')
            html = response.json()['jobSchedules']
                        
        else:
            html = '<table class="tableMessages table-bordered" width="500">'
            html += '<thead>'
            html += '<tr>'
            html += '<th>Delete</th>'
            html += '<th class="maxWidth25px">User</th>'
            html += '<th>Playbooks</th>'
            html += '<th class="maxWidth50px">Remove After Execution</th>'
            html += '<th>Scheduled Tasks</th>'
            html += '<th class="col-4">Tasks</th>'
            html += "<th>Notes</th>"
            html += '</tr>'
            html += '</thead>'
            
            try:
                cronjobs = JobSchedulerAssistant().getCurrentCronJobs('playbook=')
                # ['* * * * * hgee /usr/local/python3.10.0/bin/python3.10 /opt/Keystack/Src/crontabTest.py', '* */2 * * * hgee /usr/local/python3.10.0/bin/python3.10 /opt/Keystack/Src/crontabTest2.py']
                
                # 25 12 24 3 * root curl -d "playbook=goody&user=Hubert Gee" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://172.16.1.16:8000/api/playbook
                # <a href="#" testLogResultPath="{taskTestResultsPath}" onclick="openTestLogsModal(this)" data-bs-toggle="modal" data-bs-target="#testLogsModalDiv">View Logs</a>
                for eachCron in cronjobs:
                    # Handle the \t: '17 *\t* * *\troot    cd / && run-parts --report /etc/cron.hourly
                    eachCron = eachCron.replace('\t', ' ')
                    if eachCron == '':
                        continue
                        
                    scheduledJobSimplified = eachCron.replace('&webhook=true', '')
                    scheduledJobSimplified = scheduledJobSimplified.replace('-H "Content-Type: application/x-www-form-urlencoded', '')
                    areThereJobs = True
                    
                    # 42 11 6 10 * keystack curl -d "playbook=/opt/KeystackTests/Playbooks/pythonSample.yml&awsS3=False&jira=False&pauseOnFailure=False&debug=False" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/run

                    # 13 17 * * * keystack curl -d "mainController=192.168.28.10:28028&remoteController=192.168.28.10:28028&reservationUser=Hubert Gee&sessionId=&playbook=DOMAIN=Communal/Samples/advance&awsS3=False&jira=False&pauseOnFailure=False&debug=None&domain=Communal&testConfigs=&holdEnvsIfFailed=False&abortTestOnFailure=False&includeLoopTestPassedResults=False&scheduledJob=playbook=DOMAIN=Communal/Samples/advance minute=13 hour=17 day=* month=* dayOfWeek=*&removeJobAfterRunning=False&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.10:28028/api/v1/playbook/runPlaybook

                    match = search(' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*reservationUser=([a-zA-Z ]+)&(sessionId.*playbook=([^ &]+).*includeLoopTestPassedResults=(True|False)).*removeJobAfterRunning=(True|False)&webhook=true.*POST.*', eachCron)
                    if match:
                        min                  = match.group(1)
                        hour                 = match.group(2)
                        day                  = match.group(3)
                        month                = match.group(4)
                        dayOfWeek            = match.group(5)
                        reservationUser      = match.group(6)
                        parameters           = match.group(7)
                        playbook             = match.group(8)
                        removeAfterExecution = match.group(10)
 
                        if removeAfterExecution == 'True':
                            remove = 'Yes'
                        else:
                            remove = 'No'

                        reservationNotes = ''
                        cronJobReservationNotesData = JobSchedulerAssistant().getDetailsFromMongoDB(dbObj=DB.name, queryName='playbook')
                        countX = deepcopy(cronJobReservationNotesData)
                        count = len(list(countX))
                        if count > 0:
                            for cronInMongoDB in cronJobReservationNotesData[0]['cronJobs']:
                                if cronInMongoDB['cron'].strip() == eachCron.strip():
                                    reservationNotes = cronInMongoDB['notes']
                                                                
                        html += '<tr>'
                        
                        html += f'<td class="width50px textAlignCenter"><input type="checkbox" name="jobSchedulerMgmt" jobSearchPattern="playbook={playbook}" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        
                        html += f'<td class="maxWidth50px wordWrap textAlignCenter">{reservationUser}</td>'
                        html += f'<td class="maxWidth100px wordWrap textAlignCenter">{playbook}</td>'
                        html += f'<td class="maxWidth50px textAlignCenter">{remove}</td>'
                                                
                        # Scheduled job
                        html += f'<td width="20%" class="wordWrap textAlignLeft">Hour:{hour}&emsp; Minute:{min}&emsp; DayOfMonth:{day}&emsp; Month:{month}&emsp; DayOfWeek:{dayOfWeek}</td>'

                        # Parameters
                        parametersForDisplay = ''
                        for params in parameters.split('&'):
                            param = params.split('=')[0]
                            if param in ['domain', 'playbook']:
                                continue
                            
                            parametersForDisplay += f'{params}<br>'
                            
                        html += f'<td class="maxWidth200px wordWrap textAlignLeft">{parametersForDisplay}</td>'
                        html += f'<td class="textAlignCenter">{reservationNotes}</td>'
                        html += '</tr>'
                        
                    else:
                        match     = search(' *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+).*', eachCron)
                        min       = match.group(1)
                        hour      = match.group(2)
                        day       = match.group(3)
                        month     = match.group(4)
                        dayOfWeek = match.group(5)
                        html += '<tr>'
                        
                        html += f'<td class="class="width50px textAlignCenter"><input type="checkbox" name="jobSchedulerMgmt" jobSearchPattern="playbook={playbook}" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += '</tr>'
                                            
                html += '</table>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                #print('\n--- error:', traceback.format_exc(None, errMsg))
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetScheduledJobs', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        # This is to tell javascript if there are any scheduled job.
        # If there is no job, then hide the remove and close modal buttons
            
        return Response(data={'jobSchedules': html, "areThereJobs": areThereJobs, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
    
class GetCronScheduler(APIView):
    #@verifyUserRole(webPage=Vars.webpage, action='GetCronScheduler', exclude=['engineer'])
    def post(self, request):
        """
        Dropdowns for minute, hour, day, month, dayOfWeek
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        minute = ''
        hour = ''
        dayOfMonth = ''
        month = ''
        dayOfWeek = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/jobScheduler/getCronScheduler'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetCronScheduler')

            minute     = response.json()['minute']
            hour       = response.json()['hour']
            dayOfMonth = response.json()['dayOfMonth']
            month      = response.json()['month']
            dayOfWeek  = response.json()['dayOfWeek']
                   
        else: 
            hour, minute, month, dayOfMonth, dayOfWeek = getSchedulingOptions(typeOfScheduler='schedulePlaybook')
            schedulerDateTimePicker = f'{hour} {minute} {month} {dayOfMonth} {dayOfWeek}'  
                                                
        return Response(data={'schedulerDateTimePicker': schedulerDateTimePicker,
                              'status':status, 'errorMsg':errorMsg}, status=statusCode)


class GetJobSchedulerCount(APIView):
    def post(self, request):
        """
        Get the total amount of scheduled jobs
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        totalCronJobs = 0

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/jobScheduler/getJobSchedulerCount'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetJobSchedulerCount')

            totalCronJobs = response.json()['totalScheduledJobs']
                   
        else:         
            try:
                totalCronJobs = len(JobSchedulerAssistant().getCurrentCronJobs())
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                totalCronJobs = 0
            
        return Response(data={'totalScheduledJobs': totalCronJobs, 'status':status, 'errorMsg':errorMsg}, status=statusCode)

 
class TerminateProcessId(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='Terminate')
    def post(self,request):
        """ 
        For KeystackUI only.  Terminating from the CLI does not call here.
        
        Terminate a pipeline session will also release all reserved envs and envs waiting-in-queue
        
        body: {'sessionId': 'awesomeTest2', 'playbook': '/opt/KeystackTests/Playbooks/DOMAIN=Communal/pythonSample.yml', 'task': 'CustomPythonScripts2', 'processId': '36895', 'statusJsonFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/09-30-2022-15:31:36:496194_awesomeTest2/overallSummary.json'}
        """        
        sessionId      = request.data.get('sessionId', None)
        processId      = request.data.get('processId', None)
        # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-13-2024-20:30:50:202799_1889/overallSummary.json
        overallSummaryFile = request.data.get('statusJsonFile', None)
        timestampResultPath = '/'.join(overallSummaryFile.split('/')[:-1])
        timestampFolderName = timestampResultPath.split('/')[-1]
        testSessionLog = f'{timestampResultPath}/{GlobalVars.sessionLogFilename}'
        
        # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/10-20-2024-02:46:13:545172_7910/.Data/EnvMgmt
        envMgmtPath = f'{timestampResultPath}/.Data/EnvMgmt'
        pipelineId = timestampResultPath.split('/')[-1]
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"sessionId": sessionId, 
                      "processId": processId,
                      "statusJsonFile": overallSummaryFile}
            restApi = '/api/v1/pipelines/terminateProcessId'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='TerminateProcessId')    
        else:          
            # processIdLink: <a href="#" style="text-decoration:none" sessionId=hgee2 playbook=/opt/KeystackTests/Playbooks/pythonSample.yml task=CustomPythonScripts processId= statusJsonFile=/opt/KeystackTests/Results/PLAYBOOK=pythonSample/09-27-2022-08:04:59:982339_hgee2/STAGE=Test_TASK=CustomPythonScripts_ENV=loadcoreSample/taskSummary.json onclick="terminateProcessId(this)">Terminate</a>
            if overallSummaryFile == 'None':
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Terminate', msgType='Failed', 
                                          msg=f'No overallSummaryData.json result file for test: sessionId:{sessionId}')
                return Response(data={'status': 'failed', 'errorMsg': 'No overallSummaryData.json file found'}, status=HtmlStatusCodes.error)
            
            try:
                from datetime import datetime
                
                # Terminate the running the process
                if keystackSettings['platform'] == 'linux':
                    logSession(testSessionLog, f'[INFO]: terminateProcessId: On Linux host: kill -9 {processId}')
                    result, process = execSubprocessInShellMode(f'sudo kill -9 {processId}', showStdout=False)
                    
                if keystackSettings['platform'] == 'docker':
                    logSession(testSessionLog, f'[INFO]: terminateProcessId: On docker: kill -9 {processId}')
                    result, process = execSubprocessInShellMode(f'kill -9 {processId}', showStdout=False)
                
                # In case the test ran the playbook first time. Need to set the Playbook folder permissions 
                chownChmodFolder(topLevelFolder=GlobalVars.resultsFolder, user=GlobalVars.user, userGroup=GlobalVars.userGroup)
                   
                # Verify the termination
                result, process = execSubprocessInShellMode(f'ps -ef | grep keystack | grep {processId}', showStdout=False)
           
                isProcessIdExists = False
                for outputLine in process.split('\n'):
                    if bool(search(f'.*{processId}.+', outputLine)):
                        isProcessIdExists = True
                
                if isProcessIdExists:
                    errorMsg = f'Entered kill {processId}, but the process ID is still alive!'
                    logSession(testSessionLog, f'[FAILED]: terminateProcessId: Process ID is still alive after kill -9')
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Terminate', msgType='Failed', msg=errorMsg)
                    
                # Update the test's overallSummary.json
                testStopTime = datetime.now()
                overallSummaryData = readJson(overallSummaryFile)
                overallSummaryData['status'] = 'Terminated'
                overallSummaryData['result'] = 'Incomplete'
                overallSummaryData['stopped'] = testStopTime.strftime('%m-%d-%Y %H:%M:%S:%f')
                overallSummaryData['currentlyRunning'] = ''
                overallSummaryData['pausedOnFailureCounter'] = 0
                domain = overallSummaryData['domain']
                # Update overallSummary status with Terminated    
                writeToJson(jsonFile=overallSummaryFile, data=overallSummaryData)

                if RedisMgr.redis:
                    regexMatch = search(f'.*DOMAIN=(.+?)/.*', overallSummaryFile)
                    if regexMatch:
                        timestampFolder = overallSummaryFile.split('/')[-2]
                        domain = regexMatch.group(1)
                        redisKey = f'overallSummary-domain={domain}-{timestampFolder}'
                        redisOverallSummaryData = RedisMgr.redis.getCachedKeyData(keyName=redisKey)
                        redisOverallSummaryData.update({'status': 'Terminated',
                                                        'result': 'Incomplete',
                                                        'stopped': testStopTime.strftime('%m-%d-%Y %H:%M:%S:%f'),
                                                        'currentlyRunning': '',
                                                        'pausedOnFailureCounter': 0})
                        
                        RedisMgr.redis.write(keyName=redisKey, data=redisOverallSummaryData)
                        redisOverallSummary = RedisMgr.redis.getCachedKeyData(keyName=redisKey)
                            
                # Don't remove the test session from the active user list.  
                # The user might have terminated the session for debugging. Just remove from the wait-list.
                
                # envMgmtPath = /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/12-08-2023-17:12:09:714378_5169/.Data/EnvMgmt STAGE=Bringup_TASK=bringup_ENV=Samples-demoEnv1.json

                envMgmtObj = ManageEnv()
                envTracker = []
          
                if RedisMgr.redis:
                    envMgmtDataInRedis = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'envMgmt-{timestampFolderName}-*')
                    for envMgmtRedisData in envMgmtDataInRedis:
                        envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=envMgmtRedisData)
                        envSessionId = envMgmtData['sessionId']
                        env = envMgmtData['env']
                        testResultRootPath = envMgmtData['testResultRootPath'] 
                        testSessionLog = f'{testResultRootPath}/testSession.log'                     
                        envMgmtObj.setenv = env

                        if envMgmtData['envIsReleased'] is False:
                            envMgmtData['envIsReleased'] = True
                            RedisMgr.redis.updateKey(keyName=envMgmtRedisData, data= envMgmtData)

                        if env not in envTracker:
                            # For each Env, remove all sessionID from activeUser and waitList
                            logSession(testSessionLog, f'[INFO]: terminateProcessId: Calling EnvMgmt.removeAllSessionIdFromWaitList: env={env} sessionID={envSessionId}')
                            envMgmtObj.removeAllSessionIdFromWaitList(envSessionId, testSessionLog)
                            
                            logSession(testSessionLog, f'[INFO]: pipelineViews.terminateProcessId: Calling EnvMgmt.removeAllSessionIdFromActiveUsersList: env={env} sessionID={envSessionId}')
                            envMgmtObj.removeAllSessionIdFromActiveUsersList(envSessionId, testSessionLog)
                            envTracker.append(env)

                        if len(envMgmtData['portGroups']) > 0:
                            for portGroup in envMgmtData['portGroups']:                        
                                ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromActiveUsersList(envSessionId, testSessionLog)
                                ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromWaitList(envSessionId, testSessionLog)
                            
                            ManagePortGroup().selfUpdateActiveUsersAndWaitList()
                else:                   
                    for envMgmtDataFile in glob(f'{envMgmtPath}/*.json'):                     
                        envMgmtData = readJson(envMgmtDataFile)
                        envSessionId = envMgmtData['sessionId']
                        env = envMgmtData['env']
                        testResultRootPath = envMgmtData['testResultRootPath'] 
                        testSessionLog = f'{testResultRootPath}/testSession.log'                     
                        envMgmtObj.setenv = env

                        if envMgmtData['envIsReleased'] is False:
                            envMgmtData['envIsReleased'] = True
                            writeToJson(envMgmtDataFile, envMgmtData)
                            
                        if env not in envTracker:
                            # For each Env, remove all sessionID from activeUser and waitList
                            logSession(testSessionLog, f'[INFO]: terminateProcessId: Calling EnvMgmt.removeAllSessionIdFromWaitList: env={env} sessionID={envSessionId}')
                            envMgmtObj.removeAllSessionIdFromWaitList(envSessionId, testSessionLog)
                            
                            logSession(testSessionLog, f'[INFO]: pipelineViews.terminateProcessId: Calling EnvMgmt.removeAllSessionIdFromActiveUsersList: env={env} sessionID={envSessionId}')
                            envMgmtObj.removeAllSessionIdFromActiveUsersList(envSessionId, testSessionLog)
                            envTracker.append(env)

                        if len(envMgmtData['portGroups']) > 0:
                            for portGroup in envMgmtData['portGroups']:                   
                                ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromActiveUsersList(envSessionId, testSessionLog)
                                ManagePortGroup(domain=domain, portGroup=portGroup).removeAllSessionIdFromWaitList(envSessionId, testSessionLog)
                                                                                         
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Terminate', 
                                          msgType='Info', msg=f'sessionId:{sessionId}')             
            except Exception as errMsg:                
                status = 'failed'
                errorMsg = str(errMsg)
                logSession(testSessionLog, f'[ERROR]: {traceback.format_exc(None, errMsg)}')
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Terminate', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class ResumePausedOnFailure(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='ResumedPausedOnFailure')
    def post(self,request):
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        pausedOnFailureFile = request.data.get('pausedOnFailureFile', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'pausedOnFailureFile': pausedOnFailureFile}
            restApi = '/api/v1/pipelines/resumePausedOnFailure'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='ResumePausedOnFailure')     
        else:        
            try:
                os.remove(pausedOnFailureFile)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResumePausedOnFailure', msgType='Info',
                                          msg=pausedOnFailureFile, forDetailLogs='')
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResumePausedOnFailure', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'errorMsg': errorMsg, 'status': status}, status=statusCode)
  
    
class GetSessionDomains(APIView):
    def post(self,request):
        """
        Called by base.html. Pipelines sidebar menu.
        
        For Pipelines dropdown:
            <GROUPNAME>: <total>
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/getSessionDomains'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetSessionDomains')
            html = response.json()['sessionDomains']       
        else:        
            try:
                #from commonLib import syncTestResultsWithRedis
                #syncTestResultsWithRedis()
                
                userAllowedDomains = DomainMgr().getUserAllowedDomains(user)

                defaultDomainPath = f'{GlobalVars.resultsFolder}/DOMAIN={GlobalVars.defaultDomain}'
                if os.path.exists(defaultDomainPath) is False:
                    mkdir2(defaultDomainPath)
                    chownChmodFolder(defaultDomainPath, user=GlobalVars.user, userGroup=GlobalVars.userGroup)
                    
                for domain in userAllowedDomains:
                    totalPlaybookSessions = 0
                    domainPath = f'{GlobalVars.resultsFolder}/DOMAIN={domain}'
                    if os.path.exists(domainPath):    
                        totalFilesInDomainPath = execSubprocessInShellMode('ls -1 | wc -l', cwd=domainPath)[1]
                        if int(totalFilesInDomainPath) == 0 and GlobalVars.defaultDomain not in domainPath:
                            removeTree(domainPath)
                            
                            if RedisMgr.redis:
                                pattern= f'overallSummary-domain={domain}*'
                                RedisMgr.redis.deleteMatchingPatternKeys(pattern=pattern)
                                
                            continue
                    
                    for playbook in glob(f'{GlobalVars.keystackTestRootPath}/Results/DOMAIN={domain}/PLAYBOOK=*'):
                        totalFilesInPlaybookPath = execSubprocessInShellMode('ls -1 | wc -l', cwd=playbook)[1]
                        if int(totalFilesInPlaybookPath) == 0:
                            removeTree(playbook)
                            continue
                            
                        for timestampResult in glob(f'{playbook}/*'):
                            # timestampResult: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/07-01-2024-04:43:25:269836_9289
                            if os.path.exists(f'{timestampResult}/overallSummary.json'):
                                totalPlaybookSessions += 1
                            else:
                                removeTree(playbook)
                                if RedisMgr.redis:
                                    timestampId = timestampResult.split('/')[-1]
                                    pattern= f'overallSummary-domain={domain}-{timestampId}'
                                    RedisMgr.redis.deleteKey(keyName=pattern)
                                
                    html += f'<a class="collapse-item pl-3 textBlack" href="/sessionMgmt?domain={domain}">{totalPlaybookSessions} <i class="fa-regular fa-folder pr-3"></i>{domain}</a>'
                
                if os.path.exists(f'{GlobalVars.keystackTestRootPath}/Results/DOMAIN=None'):
                    removeTree(f'{GlobalVars.keystackTestRootPath}/Results/DOMAIN=None')
                                                    
            except Exception as errMsg:
                html = ''
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetSessionDomains', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'sessionDomains':html, 'status':status, 'errorMsg': errorMsg}, status=statusCode)


class GetTestcasesInProgress(APIView):
    swagger_schema = None

    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            
            User clicked on the progress link.
            Show a list of task testcases in progress
        
        POST /api/vi/pipelines/getTestcasesInProgress
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipelines/getTestcasesInProgress
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/pipelines/getTestcasesInProgress
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/pipelines/getTestcaseParamsInternal
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipelines/getTestcasesInProgress')
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        testcasesHtml = '<ul class="listNoBullets">'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        testcaseSortedOrderList = request.data.get('testcaseSortedOrderList', [])
        resultsPath = request.data.get('resultsPath', None)
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'testcaseSortedOrderList': testcaseSortedOrderList, 'resultsPath': resultsPath}
            restApi = '/api/v1/pipelines/getTestcasesInProgress'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestcasesInProgress')  
            testcasesHtml = response.json()['testcases']
            
        else:              
            if os.path.exists(resultsPath):
                resultsMetaDataPath = f'{resultsPath}/.Data/ResultsMeta'
                        
                for index, (testcase, cmdLindArgs) in enumerate(eval(testcaseSortedOrderList)):
                    testcaseMetaDataPath = f'{resultsMetaDataPath}{testcase}'
                    
                    for testcaseIteration in glob(f'{testcaseMetaDataPath}*'):
                        testcaseIterationOnly = testcaseIteration.split('/')[-1]
                        
                        if RedisMgr.redis:
                            testcaseResultsMeta = f'testcaseResultsData-{self.playbookObj.timestampFolderName}-{testcaseIteration}'
                            testcaseMetaData= RedisMgr.redis.getCachedKeyData(keyName=testcaseResultsMeta)
                        else:
                            testcaseMetaData = readYaml(testcaseIteration)
                            
                        testcaseResult = testcaseMetaData.get('result', 'Not-Ready')
                        status = testcaseMetaData.get('status', 'Unknown')
                        
                        if testcaseResult in ['Failed', 'Aborted']:
                            coloredResult = f'<span style="color:red"><strong>{testcaseResult}</strong></span>'
                        else:
                            coloredResult = f'<span style="color:green">{testcaseResult}</span>'
                          
                        testcasesHtml += f'<li><a href="#" testcasePath="{testcase}" onclick="showTestcase(this)">{index+1}: {testcase}</a></li>'
                        testcasesHtml += f'<li>&emsp;&ensp;Status:{status} &ensp;Result:{coloredResult}: &ensp;{testcaseIterationOnly}</li>'
                        
                    testcasesHtml += '<br>'
                
        testcasesHtml += '</ul>'
        
        return Response(data={'testcases':testcasesHtml, 'errorMsg': errorMsg, 'status': status}, status=statusCode)


class GetTestConfigsDropdownForPipeline(APIView):
    swagger_schema = None

    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            TestConfig selection for "pipeline test parameters"
        
        POST /api/vi/pipelines/testConfigs/getTestConfigsDropdownForPipeline
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline')
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        class InternalVar:
            html = ''
  
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestConfigsDropdownForPipeline')  
            InternalVar.html = response.json()['testConfigs']
            
        else:             
            def loop(path, testConfigFiles):
                """ 
                Create nested menu tree.  var.counter keeps track
                of the amount of nested menus so it knows the 
                amount of </li></ul> to close at the end.
                
                <li><span class="caret">Green Tea</span>
                    <ul class="nested">
                        <li>Sencha</li>
                        <li>Gyokuro</li>
                        <li>Matcha</li>
                        <li>Pi Lo Chun</li>
                """
        
                html = '<ul class="nested">'
                
                try:          
                    # eachFile: totalFilesInFolder
                    for eachFile in testConfigFiles:
                        if eachFile.endswith('~'):
                            continue
                        
                        testConfigFileFullPath = f'{path}/{eachFile}'
                        testConfigGroupPath = testConfigFileFullPath.split(f'{GlobalVars.testConfigsFolder}/')[-1]
                        # Show just the name of the env without the group name because user expanded the group folder already.
                        testConfigName = eachFile.split('.')[0]
                        html += f'<li><input type="checkbox" name="individualTestConfigCheckbox" value="{testConfigGroupPath}" />&emsp;{testConfigName}</li>'
                                    
                except Exception as errMsg:
                    errorMsg = str(errMsg)
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAllTestConfigs', msgType='Error',
                                              msg=errorMsg, forDetailLogs=traceback.format_exc(None, errorMsg))  

                html += '</ul>'
                return html
            
            try:    
                for root, dir, files in os.walk(GlobalVars.testConfigsFolder):
                    # root: /opt/KeystackTests/TestConfigs          
                    # files: ['demoChanges.yml', 'demo2.yml', 'demo1.yml']    
                                       
                    # Some folders might not have any env files.  Check for file count.
                    totalFilesInFolder = execSubprocessInShellMode(f'find {root} -maxdepth 1 -type f | wc -l', showStdout=False)[-1]
                    if int(totalFilesInFolder) == 0:
                        continue
                    
                    # /opt/KeystackTests/TestConfigs
                    #shortenPath = root.split(f'{GlobalVars.testConfigsFolder}/')[-1]
                    html = loop(path=root, testConfigFiles=files)
            
                    topFolder = '<ul id="testResultFileTree">'
                    
                    # # Add checkbox for for group selections
                    # topFolder += f'\n\t\t\t<li><input type="checkbox" name="groupTestConfigCheckbox" value={shortenPath} />&emsp;<span class="caret2">&ensp;{shortenPath}</span>'
                    topFolder += f'<li><span class="caret2 textBlue">{root}</span>'                    
                    InternalVar.html += f'{topFolder}{html}</li></ul>'
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAllEnvs', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))        
       
        return Response(data={'testConfigs': InternalVar.html, 'errorMsg': errorMsg, 'status': status}, status=statusCode)
   
   
class GetTestConfigsDropdownForPipeline_backup(APIView):
    swagger_schema = None

    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            TestConfig selection for "pipeline test parameters"
        
        POST /api/vi/pipelines/testConfigs/getTestConfigsDropdownForPipeline
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline')
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        
        testConfigsHtml = '<label for="testConfigs">Select a testConfig file:</label>&emsp;'
        testConfigsHtml += '<select id="testConfigs">'
        testConfigsHtml += '<option value="" selected="selected">Select</option>'
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestConfigsDropdownForPipeline')  
            testConfigsHtml = response.json()['testConfigs']
            
        else:             
            for testConfigFile in glob(f'{GlobalVars.testConfigsFolder}/*.yml'):
                testConfigFileName = testConfigFile.split('/')[-1].split('.')[0]
                testConfigsHtml += f'<option value="{testConfigFileName}">{testConfigFileName}</option>'
               
        testConfigsHtml += '</select>'
        
        return Response(data={'testConfigs':testConfigsHtml, 'errorMsg': errorMsg, 'status': status}, status=statusCode)
   
 
class GetTestConfigsList(APIView):
    swagger_schema = None

    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            Get testConfig selection for "modifying testcase" configurations
        
        POST /api/vi/pipelines/testConfigs/getTestConfigsList
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsList
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsList
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getTestConfigsList
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipelines/testConfigs/getTestConfigsList')
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        
        testConfigsHtml = '<select id="testConfigsList" onchange="getTestConfigContents(value)">'
        testConfigsHtml += '<option value="" selected="selected">Select TestConfig File</option>'
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/testConfigs/getTestConfigsList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestConfigsList')  
            testConfigsHtml = response.json()['testConfigsList']
            
        else:      
            for testConfigFile in glob(f'{GlobalVars.testConfigsFolder}/*.yml'):
                testConfigFileName = testConfigFile.split('/')[-1].split('.')[0]
                testConfigsHtml += f'<option value="{testConfigFile}">{testConfigFileName}</option>'
                
        testConfigsHtml += '</select>'
        
        return Response(data={'testConfigsList': testConfigsHtml, 'errorMsg': errorMsg, 'status': status}, status=statusCode)

    
class DeleteTestConfigs(APIView):
    swagger_schema = None

    @verifyUserRole(webPage=Vars.webpage, action='DeleteTestConfigs', exclude=['engineer'])
    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            TestConfig selection for "pipeline test parameters"
        
        POST /api/vi/pipelines/testConfigs/delete
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/delete
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/delete
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/delete
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipelines/testConfigs/delete)
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        testConfigsFullPath = request.data.get('testConfigFullPath', None)
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'testConfigFullPath': testConfigsFullPath}
            restApi = '/api/v1/pipelines/testConfigs/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeleteTestConfigs')  
        else:
            try:
                if os.path.exists(testConfigsFullPath):
                    os.remove(testConfigsFullPath)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestConfigs', msgType='Success',
                                              msg=f'Deleted testConfigs: {testConfigsFullPath}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestConfigs', msgType='Info',
                                              msg=f'No testConfig file: {testConfigsFullPath}', forDetailLogs='')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestConfigs', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                                
        return Response(data={'errorMsg': errorMsg, 'status': status}, status=statusCode)
    

class GetTestConfigParams(APIView):
    swagger_schema = None

    @verifyUserRole(webPage=Vars.webpage, action='GetTestConfigParams', exclude=['engineer'])
    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            Get all the testConfig params to help user create a new testConfig file
        
        POST /api/vi/pipelines/testConfigs/getParams
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getParams
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getParams
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/getParams
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipelines/testConfigs/getParams)
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        testConfigParams = ''
               
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/pipelines/testConfigs/getParams'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestConfigParams')  
        else:
            try:
                currentDir = os.path.abspath(os.path.dirname(__file__))
                testConfigsTemplateYmlFile = f'{currentDir}/testConfigsTemplate.yml'
                testConfigContents = readFile(testConfigsTemplateYmlFile)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestConfigParams', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                                
        return Response(data={'testConfigParams': testConfigContents, 'errorMsg': errorMsg, 'status': status}, status=statusCode)


class SaveNewTestConfigsToFile(APIView):
    swagger_schema = None

    @verifyUserRole(webPage=Vars.webpage, action='SaveNewTestConfigsToFile', exclude=['engineer'])
    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            Save new testConfigs to a file
        
        POST /api/vi/pipelines/testConfigs/saveNewTestConfigsToFile
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/saveNewTestConfigsToFile
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/saveNewTestConfigsToFile
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/pipelines/testConfigs/saveNewTestConfigsToFile
            
            session = requests.Session()
            response = session.request('post', 'http://localhost:8000/api/v1/pipelines/testConfigs/saveNewTestConfigsToFile)
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        testConfigsFilename = request.data.get('testConfigName', None)
        textArea = request.data.get('textarea', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'testConfigName': testConfigsFilename, 'textarea': textArea}
            restApi = '/api/v1/pipelines/testConfigs/saveNewTestConfigsToFile'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='SaveNewTestConfigsToFile')  
        else:
            try:
                testConfigFileFullPath = f'{GlobalVars.testConfigsFolder}/{testConfigsFilename}.yml'
                if os.path.exists(testConfigFileFullPath):
                    raise Exception(f'There is already a testConfig with same filename already: {testConfigsFilename}')
                
                with open(testConfigFileFullPath, 'w') as fileObj:
                    fileObj.write(textArea)
                 
                chownChmodFolder(GlobalVars.testConfigsFolder,
                                 user=GlobalVars.user, userGroup=GlobalVars.userGroup, permission=770, stdout=False)
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SaveNewTestConfigsToFile', msgType='Success',
                                          msg=testConfigFileFullPath, forDetailLogs='')
                                   
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SaveNewTestConfigsToFile', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                                
        return Response(data={'errorMsg': errorMsg, 'status': status}, status=statusCode)
 