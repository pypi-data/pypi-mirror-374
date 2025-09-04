import os, json, traceback
from re import search
from shutil import rmtree, copytree
from pathlib import Path
from glob import glob, iglob
import itertools
from datetime import datetime 

from django.views import View
from django.http import JsonResponse, FileResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from domainMgr import DomainMgr
from globalVars import GlobalVars, HtmlStatusCodes
from baseLibs import removeEmptyTestResultFolders
from keystackUtilities import makeFolder, mkdir2, rmtree, readJson, readYaml, readFile, writeToJson, execSubprocessInShellMode
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from RedisMgr import RedisMgr
from commonLib import getHttpIpAndPort, syncTestResultsWithRedis
from execRestApi import ExecRestApi
from RedisMgr import RedisMgr

class Vars:
    webpage = 'testResults'
        
         
def deleteTestResultFolders(deleteTestResults, user, isDomain=False):
    """ 
    Helper function
    """            
    try:
        deletedResultList = []
        for resultFolder in deleteTestResults:
            # resultFolder: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/10-26-2022-14:42:25:471305_809           
            rmtree(resultFolder)
            deletedResultList.append(resultFolder)
            if isDomain is False:
                removeEmptyTestResultFolders(user, resultFolder)
                    
        HtmlStatusCodes.success
        if deletedResultList:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestResults',
                                      msgType='Info', msg=f'Deleted results: {deletedResultList}')
        
        statusCode = HtmlStatusCodes.success 
        
    except Exception as errMsg:
        statusCode = HtmlStatusCodes.error
        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestResults', 
                                  msgType='Error', msg=errMsg, 
                                  forDetailLogs=f'DeleteTestResults: {traceback.format_exc(None, errMsg)}')
        
    return statusCode   
    
    
class SidebarTestResults(APIView):
    def post(self, request):
        """
        For sidebar test resuls and archive results
        
        whichResults <str>: activeResults|archiveResults
        
        {% for group, playbookList in allPlaybookTestResultFoldersForSidebar.activeResults.items %}
            <span class="pb-2 pt-2 marginLeft10 textBlack fontSize12px">Group: {{group}}</span>

            {% for playbookPath in playbookList %}
                <!-- Notes: url testResults takes you to testResults.views -->
                <a class="collapse-item pt-2 pl-3 fontSize12px" href="{% url "testResults" %}?resultFolderPath={{playbookPath}}&typeOfResult=activeTestResults"><i class="fa-regular fa-folder pr-3 pt-1"></i>{% getPlaybookName playbookPath %}</a><br>
            {% endfor %}
            <br><br>
        {% endfor %}
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        
        # activeResults | archiveResults
        #whichResult = request.data.get('whichResultType', None)
        htmlTestResults = ''
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/results/sidebarMenu'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SidebarTestResults')

            htmlTestResults = response.json()['testResults']
            
        else:        
            try:
                testResults = dict()
                testResults['activeResults'] = dict()
                testResults['archiveResults'] = dict()
                
                for domain in  DomainMgr().getUserAllowedDomains(user):
                    testResults['activeResults'][domain] = []
                    testResults['archiveResults'][domain] = []
                    for playbookPath in glob(f"{GlobalVars.resultsFolder}/DOMAIN={domain}/*"):
                        # playbookpath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance
                        testResults['activeResults'][domain].append(playbookPath)
                        
                    if os.path.exists(GlobalVars.archiveResultsFolder):
                        for playbookPath in glob(f"{GlobalVars.archiveResultsFolder}/DOMAIN={domain}/*"):
                            testResults['archiveResults'][domain].append(playbookPath)    

                # Add a line spacing                
                htmlTestResults += '<div class="pt-3"></div>'
                
                htmlTestResults += '<div class="dropdown pb-2">'
                # Change data-toggle to data-bs-toggle to lower the dropdown menu
                htmlTestResults += '<a class="dropdown-toggle pl-2 textBlack" id="resultArchiveSelection" data-bs-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>Results Archive</a>'

                # dropdownSizeMedium dropdownFontSize
                htmlTestResults += '<ul class="dropdown-menu" id="selectResultArchiveDomain">'
                for domain, playbookList in testResults['archiveResults'].items():
                    if len(playbookList) == 0:
                        continue

                    htmlTestResults += f'<li class="dropdown-item"><strong>Domain: {domain}</strong></li>'
                    
                    for playbookPath in playbookList:
                        # playbookPath -> /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample
                        totalResults = execSubprocessInShellMode(f'ls {playbookPath} -1 | wc -l', showStdout=False)[1].replace('\n', '')
                        playbookName = playbookPath.split('/')[-1].split('=')[-1].replace('-', '/')
                        
                        htmlTestResults += f' <li class="dropdown-item"><a class="collapse-item fontSize12px" href="/testResults?resultFolderPath={playbookPath}&typeOfResult=archiveResults">{totalResults} {playbookName}</a></li>'
                        
                    htmlTestResults += '<div class="pb-1"></div>'
                htmlTestResults += '</ul></div>'
 
                # Add a line spacing
                htmlTestResults += '<div class="pt-3"></div>'
                 
                # Add active results below the Results Archive               
                for domain, playbookList in testResults['activeResults'].items():
                    if len(playbookList) == 0:
                        continue

                    htmlTestResults += f'<p class="pl-2 pb-0 marginLeft10 textBlack fontSize12px"><strong>Domain: {domain}</strong></p>'
                    htmlTestResults += '<p>'
                    
                    for playbookPath in playbookList:
                        # playbookPath -> /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample
                        totalResults = execSubprocessInShellMode(f'ls {playbookPath} -1 | wc -l', showStdout=False)[1].replace('\n', '')
                        playbookName = playbookPath.split('/')[-1].split('=')[-1].replace('-', '/')
                        htmlTestResults += f'<a class="collapse-item fontSize12px" href="/testResults?resultFolderPath={playbookPath}&typeOfResult=activeResults">{totalResults} {playbookName}</a>'
                        
                    htmlTestResults += '</p>'
                        
            except Exception as errMsg:
                erroMsg = str(errMsg)
                status = 'failed'
                htmlTestResults = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestResults', msgType='Error', msg=errMsg,
                                        forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
        
        return Response(data={'status':status, 'errorMsg':errorMsg, 'testResults':htmlTestResults}, status=statusCode)


class SidebarTestResults_backup(APIView):
    def post(self, request):
        """
        For sidebar test resuls and archive results
        
        whichResults <str>: activeResults|archiveResults
        
        {% for group, playbookList in allPlaybookTestResultFoldersForSidebar.activeResults.items %}
            <span class="pb-2 pt-2 marginLeft10 textBlack fontSize12px">Group: {{group}}</span>

            {% for playbookPath in playbookList %}
                <!-- Notes: url testResults takes you to testResults.views -->
                <a class="collapse-item pt-2 pl-3 fontSize12px" href="{% url "testResults" %}?resultFolderPath={{playbookPath}}&typeOfResult=activeTestResults"><i class="fa-regular fa-folder pr-3 pt-1"></i>{% getPlaybookName playbookPath %}</a><br>
            {% endfor %}
            <br><br>
        {% endfor %}
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        
        # activeResults | archiveResults
        whichResult = request.data.get('whichResultType', None)
        htmlTestResults = ''
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'whichResultType': whichResult}
            restApi = '/api/v1/results/sidebarMenu'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SidebarTestResults')

            htmlTestResults = response.json()['testResults']
            
        else:        
            try:
                testResults = dict()
                testResults['activeResults'] = dict()
                testResults['archiveResults'] = dict()
                
                for domain in  DomainMgr().getUserAllowedDomains(user):
                    testResults['activeResults'][domain] = []
                    testResults['archiveResults'][domain] = []
                    for playbookPath in glob(f"{GlobalVars.resultsFolder}/DOMAIN={domain}/*"):
                        # playbookpath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance
                        testResults['activeResults'][domain].append(playbookPath)
                        
                    if os.path.exists(GlobalVars.archiveResultsFolder):
                        for playbookPath in glob(f"{GlobalVars.archiveResultsFolder}/DOMAIN={domain}/*"):
                            testResults['archiveResults'][domain].append(playbookPath)    
                
                htmlTestResults += '<div class="pt-3"></div>'
                
                for domain, playbookList in testResults[whichResult].items():
                    if len(playbookList) == 0:
                        totalDomainResults = 0
                    else:
                        totalDomainResults = ''
                        
                    htmlTestResults += f'<p class="pl-2 pb-0 marginLeft10 textBlack fontSize12px">{totalDomainResults}&emsp;Domain: {domain}</p>'
                    htmlTestResults += '<p>'
                    
                    for playbookPath in playbookList:
                        # playbookPath -> /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample
                        totalResults = execSubprocessInShellMode(f'ls {playbookPath} -1 | wc -l', showStdout=False)[1].replace('\n', '')
                        playbookName = playbookPath.split('/')[-1].split('=')[-1].replace('-', '/')
                        htmlTestResults += f'<a class="collapse-item fontSize12px" href="/testResults?resultFolderPath={playbookPath}&typeOfResult={whichResult}">{totalResults} <i class="fa-regular fa-folder pr-3"></i>{playbookName}</a>'
                        
                    htmlTestResults += '</p>'
                        
            except Exception as errMsg:
                erroMsg = str(errMsg)
                status = 'failed'
                htmlTestResults = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestResults', msgType='Error', msg=errMsg,
                                        forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
        
        return Response(data={'status':status, 'errorMsg':errorMsg, 'testResults':htmlTestResults}, status=statusCode)
    
    
class GetNestedFolderFiles(APIView):
    def post(self, request):
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        nestedFolderPath = request.data.get('nestedFolderPath', None)
        insertToDivId = request.data.get('insertToDivId', None)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        html = ''
        caretName = None
        nestedFolderUniqueCounter = 200000
        
        import random
        randomNumber = str(random.sample(range(100,10000), 1)[0])
        caretName = f"caret{randomNumber}"
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'nestedFolderPath': nestedFolderPath, 'insertToDivId': insertToDivId}
            restApi = '/api/v1/results/nestedFolderFiles'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetNestedFolderFiles')
            html = response.json()['folderFiles']
            caretName = response.json()['caretName']
  
        else:                    
            for eachFile in glob(f'{nestedFolderPath}/*'):
                if os.path.isfile(eachFile):
                    filename = eachFile .split('/')[-1]
                    # Open the modifyFileModal and get the file contents                  
                    html += f'<li><a class="nav-link" href="#" onclick="getFileContents(this)" filePath="{eachFile}"  data-bs-toggle="modal" data-bs-target="#openFileModal"><i class="fa-regular fa-file pr-2"></i> {filename} </a></li>'
                
                if os.path.isdir(eachFile):
                    filename = eachFile.split('/')[-1]
                    nestedFolderDivId = f'insertNestedFolderFiles_{str(nestedFolderUniqueCounter)}'

                    html += f'<li><span class="{caretName}"><a class="nav-link" href="#" onclick="getNestedFolderFiles(this)" insertToDivId="#{nestedFolderDivId}" nestedFolderPath="{eachFile}"><i class="fa-regular fa-folder pr-2"></i> {filename}</a></span>'
                                    
                    html += f'<ul class="nested" id="{nestedFolderDivId}"></ul>'
                    html += '</li>'
                    nestedFolderUniqueCounter += 1

        return JsonResponse(data={'folderFiles':html, 'caretName': caretName, 'newVarName': f'newVar_{randomNumber}',
                            'status':status, 'errorMsg':errorMsg}, status=statusCode)
        

class GetTestResultPages(APIView):
    def post(self, request):
        """
        When users go to a test results page, show page number buttons.
        The buttons will contain the amount of pages to show.
        
        The return html code goes in conjunction with getTestResultTreeView.css.
        
        Requirements:
            - CSS: <link href={% static "commons/css/testResultsTreeView.css" %} rel="stylesheet" type="text/css">
            - html template needs to call addListeners() and getFileContents()
        """        
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # 192.168.28.17:443
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        
        # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample
        # /opt/KeystackTests/ResultsArchive/DOMAIN=Communcal/PLAYBOOK=pythonSample
        resultFolderPath = request.data.get('resultFolderPath', None)
        
        # ['0:2'] <-- In a list
        pageIndexRangeOriginal = request.data.get('pageIndexRange')
        pageIndexRange = pageIndexRangeOriginal[0]
        
        # The page number to get
        getPageNumber = request.data.get('getPageNumber')
        getResultsPerPage = request.data.get('getResultsPerPage', 25)
        pageIndex = request.data.get('pageIndex', None)
        pageIndex = int(pageIndex)
        indexStart = int(pageIndexRange.split(':')[0])
        indexEnd = int(pageIndexRange.split(':')[1])
        testResultTimestampFolders = []
        startingRange = pageIndexRange.split(":")[0]
        pages = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'resultFolderPath': resultFolderPath, 
                      'pageIndexRange': pageIndexRangeOriginal,
                      'getPageNumber': getPageNumber,
                      'getResultsPerPage': getResultsPerPage,
                      'pageIndex': pageIndex}
            
            restApi = '/api/v1/results/pages'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestResultPages')
        
            return JsonResponse(data={'pages': response.json()['pages'], 'status':status, 'errorMsg':errorMsg}, status=statusCode)
            
        else:            
            try:
                testResultTimestampFolders = glob(f'{resultFolderPath}/*')
            except:
                errorMsg = f'The result folder path is removed: {resultFolderPath}'

            # Get test results in a reversed list
            datetimeList = []
            for eachTimestampFolder in testResultTimestampFolders:
                datetimeList.append(eachTimestampFolder)
                
            # Got a sorted list
            datetimeList = list(reversed(sorted(datetimeList, key=lambda fileName: datetime.strptime(fileName.split('/')[-1].split('_')[0], "%m-%d-%Y-%H:%M:%S:%f"))))
            totalResults = len(testResultTimestampFolders)
            if totalResults <= getResultsPerPage:
                lastPage = True
            else:
                lastPage = False

            if indexEnd >= len(datetimeList):
                lastIndex = len(datetimeList)
            else:
                lastIndex = indexEnd
                                
            # Get round rounter
            #resultsPerPage =  round(totalResults / getResultsPerPage)
            # Get remainders using %.  Remainders go on the last page.
            #remainders = totalResults % getResultsPerPage        

            ''' 
            getTestResultsPages: totalResults: 5
            resultsPerPage: 2
            remainders: 1
            --- Page:1  0:2
            --- Page:2  2:4
            --- Page:3  4:6
            {1: (0, 2), 2: (2, 4), 3: (4, -1)}
            '''
            # Create the page buttons
            pages = dict()
            
            if pageIndex == int(pageIndexRange.split(":")[0]):
                resultsPerPageDropdown = f'<label for="resultsPerPage">Results Per Page: </label> <select id="resultsPerPage" onchange="setResultsPerPage(this)">'
                for option in [10, 25, 50, 100]:                    
                    if int(option) == int(getResultsPerPage):
                        resultsPerPageDropdown += f'<option value="{option}" selected="selected">{option}</option>'
                    else:
                        resultsPerPageDropdown += f'<option value="{option}">{option}</option>'
        
                resultsPerPageDropdown += f'</select>'

                pageButtons = f'{resultsPerPageDropdown} &emsp; Current Page: {getPageNumber} &emsp; Pages: &ensp;'
            else:
                pageButtons = ''
                
            if pageIndex == int(pageIndexRange.split(":")[0]):
                for index,startingIndex in enumerate(range(0, totalResults, getResultsPerPage)):
                    pageNumber = index+1
                    endingIndex = startingIndex + getResultsPerPage

                    if pageNumber > 1 and endingIndex == totalResults:
                        # Don't create a 2nd page button if there's only 1 page of results to show
                        pages[pageNumber] = (startingIndex, totalResults)
                        pageButtons += f'<button type="button" class="btn btn-outline-primary" onclick="getTestResultPages(this)" getPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{totalResults}">{pageNumber}</button>&ensp;'
                    else:
                        # if endingIndex != totalResults:
                        pages[pageNumber] = (startingIndex, endingIndex)
                        pageButtons += f'<button type="button" class="btn btn-outline-primary" onclick="getTestResultPages(this)" getPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</button>&ensp;' 

                    
            class getPagesVars:
                counter = 0
                jsonCounter = 0
                htmlPageButtons = f'{pageButtons}<br><br>'
                
                if pageIndex == int(pageIndexRange.split(":")[0]):
                    html = f'{pageButtons}<br><br> <ul id="testResultFileTree">'
                else:
                    html = f'<ul id="testResultFileTree">'
                            
            """
            https://www.w3schools.com/howto/howto_js_treeview.asp
            
            <ul id="myUL">
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
            """

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
                    path = eachResultFolderFullPath
                
                if init == False:
                    folderName = path.split('/')[-1]
                    getPagesVars.html += f'<li style="margin-left:17px"><span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{folderName}</span>'  
                    
                getPagesVars.html += '<ul class="nested">'
                getPagesVars.counter += 1
                            
                for eachFile in glob(f'{path}/*'):
                    if os.path.isfile(eachFile):
                        filename = eachFile .split('/')[-1]
                        # Open the modifyFileModal and get the file contents 
                        if '.pdf' in eachFile:
                            # User clicks on pdf file, getTestResultFileContents uses Django's FileResponse to read the PDF file and display it in a new tab
                            getPagesVars.html += f'<li><a class="nav-link" href="/testResults/getTestResultFileContents?testResultFile={eachFile}" target="_blank"><i class="fa-regular fa-file pr-2"></i>{filename}</a></li>'
                        else:                 
                            getPagesVars.html += f'<li><a class="nav-link" href="#" onclick="getFileContents(this)" filePath="{eachFile}" data-bs-toggle="modal" data-bs-target="#openFileModal"><i class="fa-regular fa-file pr-2"></i> {filename} </a></li>'
                
                # Use iglob to get both regular folders, files and files beginnging with a dot
                for eachFolder in itertools.chain(iglob(f'{path}/**'), iglob(f'{path}/.**')):  
                    if os.path.isdir(eachFolder):
                        loop(eachFolder, init=False)
                        getPagesVars.html += '</li></ul>'
                        getPagesVars.counter -= 1
                                  
            for index in range(indexStart, lastIndex):
                try:
                    eachResultFolderFullPath = datetimeList[index]
                except Exception as errMsg:
                    break
             
                # eachResultFolderFullPath: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/12-20-2022-18:00:49:300483_2054
                timestampResultFolder = eachResultFolderFullPath.split('/')[-1]
                started = ''
                stopped = ''
                testResult = ''
                testStatus = ''
                totalTestAborted = 0
                totalCases = ''
                totalFailed = 0
                user = ''
                getPagesVars.counter = 0
                
                try:
                    if os.path.exists(f'{eachResultFolderFullPath}/overallSummary.json'):
                        statusJsonFile = readJson(f'{eachResultFolderFullPath}/overallSummary.json')
                        getPagesVars.jsonCounter += 1
                        started = statusJsonFile.get('started', None)
                        stopped = statusJsonFile.get('stopped', None)
                        testResult = statusJsonFile.get('result', None)
                        testStatus = statusJsonFile.get('status', None)
                        totalTestAborted = statusJsonFile.get('totalTestAborted', None)
                        totalCases = statusJsonFile.get('totalCases', None)
                        totalFailed = statusJsonFile.get('totalFailed', None)
                        user = statusJsonFile.get('user', None)

                    # Starting <li>:  Top-level timestamp result folders
                    # When user clicks on the download button, the <form action="{% url 'downloadResults' %}" method="post"> will be directed.
                    # Using name="downloadTestResults" value="{eachResultFolderFullPath}" to get the value
                    getPagesVars.html += f'\n\t\t\t<li><input type="checkbox" name="testResultCheckbox" value="{eachResultFolderFullPath}" />&emsp;<button type=submit class="btn btn-sm btn-outline-primary p-0 px-2" style="height:20px" id="getSelectedTestResult" name="downloadTestResults" value={eachResultFolderFullPath}><i class="fas fa-cloud-arrow-down"></i></button><span class="caret2">&ensp;<a class="nav-link" style="display:inline-block" href="#"><i class="fa-regular fa-folder pr-2"></i>{timestampResultFolder}&emsp;User:{user}&emsp;Result:{testResult}&emsp;Status:{testStatus}&emsp;TotalCases:{totalCases}&emsp;TotalFailed:{totalFailed}&emsp;TotalAborted:{totalTestAborted}</a></span>'
                                                        
                    loop(eachResultFolderFullPath, init=True)
                    
                    for x in range(0, getPagesVars.counter):
                        getPagesVars.html += '</ul></li>'
                        
                    getPagesVars.html += '</li>'
                    
                except Exception as errMsg:
                    errorMsg = traceback.format_exc(None, errorMsg)
                    status = 'failed'
                    pages = ''
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestResultPages', msgType='Error',
                                              msg=errorMsg, forDetailLogs=errorMsg)
                        
            getPagesVars.html += '</ul>'
             
            return JsonResponse(data={'pages':getPagesVars.html, 'lastPage': lastPage,
                                      'status':status, 'errorMsg':errorMsg}, status=statusCode)
        

class DeleteResults(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteTestResults', exclude=['engineer'])
    def post(self,request):
        """
        Delete test results
        
        Delete is called by KeystackUI
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        testStillRunningMessages = []
        
        deleteTestResults = request.data.get('deleteTestResults')
        # True | None
        forceDeleteTestResults = request.data.get('forceDeleteTestResults', False)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"deleteTestResults": deleteTestResults, "forceDeleteTestResults": forceDeleteTestResults}
            restApi = '/api/v1/results/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteResults')  
        else:
            try:
                keystackHttpIpAddress, keystackIpPort = getHttpIpAndPort()
                execRestApiObj = ExecRestApi(ip=keystackHttpIpAddress, port=keystackIpPort)
                testStillRunningMessages = []
                      
                # {'deleteTestResults': ['/opt/KeystackTests/Results/DOMAIN=QA/PLAYBOOK=pythonSample/10-15-2022-17:42:49:516252_qa']}
                for testResultPath in deleteTestResults:
                    timestampFolderName = testResultPath.split('/')[-1]
                    overallSummaryJsonFile = f'{testResultPath}/overallSummary.json'
                    
                    try:
                        if os.path.exists(overallSummaryJsonFile):
                            overallSummaryData = readJson(overallSummaryJsonFile)                                                
                            if overallSummaryData['status'] != 'Running':
                                deleteTestResultFolders([testResultPath], user)
                                deleteTestResultFromRedis = True
                                
                            elif overallSummaryData['status'] == 'Running':
                                api = '/api/v1/pipelines/terminateProcessId'
                                params = {'sessionId': overallSummaryData['sessionId'], 
                                          'processId': overallSummaryData['processId'], 
                                          'statusJsonFile': f"{overallSummaryData['topLevelResultFolder']}/overallSummary.json"}
                                execRestApiObj.post(restApi=api, params=params, timeout=20)
                                
                                if forceDeleteTestResults is False:
                                    testStillRunningMessages.append(f'Test still running. Not deleting: {testResultPath.split("/")[-1]}')
                                    deleteTestResultFromRedis = False
                                    
                                elif overallSummaryData['status'] == 'Running' and forceDeleteTestResults:
                                    deleteTestResultFolders([testResultPath], user)
                                    deleteTestResultFromRedis = True

                            if deleteTestResultFromRedis:
                                if RedisMgr.redis:
                                    regexMatch = search('.*DOMAIN=(.+?)/.*', testResultPath)
                                    if regexMatch:
                                        timestampFolder = testResultPath.split('/')[-1]
                                        redisOverallSummaryData = f'overallSummary-domain={regexMatch.group(1)}-{timestampFolder}'
                                        RedisMgr.redis.deleteKey(keyName=redisOverallSummaryData)
                                     
                                    RedisMgr.redis.deleteMatchingPatternKeys(pattern=f'envMgmt-{timestampFolderName}*') 
                                    # RedisMgr.redis.deleteMatchingPatternKeys(pattern=f'testcaseResultsData-{timestampFolderName}*')  
                            
                    except Exception as errMsg:
                        del execRestApiObj
                        errorMsg = str(errMsg)
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestResults', 
                                                  msgType='Error', msg=errMsg, 
                                                  forDetailLogs=f'DeleteTestResults: {traceback.format_exc(None, errMsg)}')
                        return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)
                                
                if len(testStillRunningMessages) > 0:
                    status = 'failed'
                    errorMsg = testStillRunningMessages
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestResults', 
                                              msgType='Failed', msg=errorMsg, 
                                              forDetailLogs='')
                    
                del execRestApiObj
                
            except Exception as errMsg: 
                erroMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestResults', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)
                                    
class DeleteAllInDomain(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteAllInDomain', exclude=['engineer'])
    def post(self, request):
        """
        Delete all test results in DOMAIN=<domain>
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
                        
        # /opt/KeystackTests/Results/DOMAIN=Communal
        domain = request.data.get('domain', None)
        # activeResults | archiveResults
        testResultActiveOrArchive = request.data.get('testResultActiveOrArchive', 'activeResults')
        
        # True | False
        forceDeleteTestResults = request.data.get('forceDeleteTestResults', False)
        
        if testResultActiveOrArchive == 'activeResults':
            resultPath = 'Results'
        if testResultActiveOrArchive == 'archiveResults':
            resultPath = 'ResultsArchive'
            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, 'testResultActiveOrArchive': testResultActiveOrArchive, 
                      "forceDeleteTestResults": forceDeleteTestResults}
            restApi = '/api/v1/results/deleteAllInDomain'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeleteAllInDomain')       
        else:
            try:
                keystackHttpIpAddress, keystackIpPort = getHttpIpAndPort()
                execRestApiObj = ExecRestApi(ip=keystackHttpIpAddress, port=keystackIpPort)
                testStillRunningMessages = []
                 
                for playbook in glob(f'{GlobalVars.keystackTestRootPath}/{resultPath}/DOMAIN={domain}/PLAYBOOK*'):
                    # Must verify if the pipeline is still running first
                    for testResultPath in glob(f'{playbook}/*'):
                        overallSummaryJsonFile = f'{testResultPath}/overallSummary.json'
                        timestampFolderName = testResultPath.split('/')[-1]
                        
                        try:
                            if os.path.exists(overallSummaryJsonFile):
                                overallSummaryData = readJson(overallSummaryJsonFile)                                           
                                if overallSummaryData['status'] != 'Running':
                                    deleteTestResultFolders([testResultPath], user)
                                    deleteTestResultFromRedis = True
                                    
                                elif overallSummaryData['status'] == 'Running':
                                    api = '/api/v1/pipelines/terminateProcessId'
                                    params = {'sessionId': overallSummaryData['sessionId'], 
                                            'processId': overallSummaryData['processId'], 
                                            'statusJsonFile': f"{overallSummaryData['topLevelResultFolder']}/overallSummary.json"}
                                    response = execRestApiObj.post(restApi=api, params=params, timeout=20)
                                    
                                    if forceDeleteTestResults is False:
                                        testStillRunningMessages.append(f'Test still running. Not deleting: {testResultPath.split("/")[-1]}')
                                        deleteTestResultFromRedis = False
                                        
                                    elif overallSummaryData['status'] == 'Running' and forceDeleteTestResults:
                                        deleteTestResultFolders([testResultPath], user)
                                        deleteTestResultFromRedis = True

                                if deleteTestResultFromRedis:
                                    if RedisMgr.redis:
                                        regexMatch = search('.*DOMAIN=(.+?)/.*', testResultPath)
                                        if regexMatch:
                                            timestampFolder = testResultPath.split('/')[-1]
                                            redisOverallSummaryData = f'overallSummary-domain={regexMatch.group(1)}-{timestampFolder}'
                                            RedisMgr.redis.deleteKey(keyName=redisOverallSummaryData)
                                            
                                        RedisMgr.redis.deleteMatchingPatternKeys(pattern=f'envMgmt-{timestampFolderName}*') 
                                        # RedisMgr.redis.deleteMatchingPatternKeys(pattern=f'testcaseResultsData-{timestampFolderName}*')  
                            
                        except Exception as errMsg:
                            errorMsg = str(errMsg)
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllInDomain', 
                                                      msgType='Error', msg=errMsg, 
                                                      forDetailLogs=f'DeleteAllInDomain: {traceback.format_exc(None, errMsg)}')
                            return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)
                                
            except Exception as errMsg:
                erroMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllInDomain', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)
                    
        del execRestApiObj
                            
        if len(testStillRunningMessages) > 0:
            status = 'failed'
            errorMsg = testStillRunningMessages
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllInDomain', 
                                      msgType='Failed', msg=testStillRunningMessages, 
                                      forDetailLogs='')
                                
        return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeleteAllInPlaybook(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteAllInPlaybook', exclude=['engineer'])
    def post(self, request):
        """
        Delete all test results in GROUP=<groupName>/PLAYBOOK=<playbookName>
        """
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
                
        # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=KeystackQA-playbook1
        path = request.data.get('path', None)
        # True | False
        forceDeleteTestResults = request.data.get('forceDeleteTestResults', False)
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"path": path, "forceDeleteTestResults": forceDeleteTestResults}
            restApi = '/api/v1/results/deleteAllInPlaybook'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeleteAllResultsInPlaybook') 
        else:
            try:
                keystackHttpIpAddress, keystackIpPort = getHttpIpAndPort()
                execRestApiObj = ExecRestApi(ip=keystackHttpIpAddress, port=keystackIpPort)
                testStillRunningMessages = []
                      
                # path: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=KeystackQA-playbook1
                for testResultPath in glob(f'{path}/*'):
                    overallSummaryJsonFile = f'{testResultPath}/overallSummary.json'
                    timestampFolderName = testResultPath.split('/')[-1]
                    
                    try:
                        if os.path.exists(overallSummaryJsonFile):
                            overallSummaryData = readJson(overallSummaryJsonFile)                                                
                            if overallSummaryData['status'] != 'Running':
                                deleteTestResultFolders([testResultPath], user)
                                deleteTestResultFromRedis = True
                                
                            elif overallSummaryData['status'] == 'Running':
                                api = '/api/v1/pipelines/terminateProcessId'
                                params = {'sessionId': overallSummaryData['sessionId'], 
                                        'processId': overallSummaryData['processId'], 
                                        'statusJsonFile': f"{overallSummaryData['topLevelResultFolder']}/overallSummary.json"}
                                response = execRestApiObj.post(restApi=api, params=params, timeout=20)
                                
                                if forceDeleteTestResults is False:
                                    testStillRunningMessages.append(f'Test still running. Not deleting: {testResultPath.split("/")[-1]}')
                                    deleteTestResultFromRedis = False
                                    
                                elif overallSummaryData['status'] == 'Running' and forceDeleteTestResults:
                                    deleteTestResultFolders([testResultPath], user)
                                    deleteTestResultFromRedis = True

                            if deleteTestResultFromRedis:
                                if RedisMgr.redis:
                                    regexMatch = search('.*DOMAIN=(.+?)/.*', testResultPath)
                                    if regexMatch:
                                        timestampFolder = testResultPath.split('/')[-1]
                                        redisOverallSummaryData = f'overallSummary-domain={regexMatch.group(1)}-{timestampFolder}'
                                        RedisMgr.redis.deleteKey(keyName=redisOverallSummaryData)
                                    
                                    RedisMgr.redis.deleteMatchingPatternKeys(pattern=f'envMgmt-{timestampFolderName}*') 
                                    # RedisMgr.redis.deleteMatchingPatternKeys(pattern=f'testcaseResultsData-{timestampFolderName}*')
                        
                    except Exception as errMsg:
                        errorMsg = str(errMsg)
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllResultsInPlaybook', 
                                                msgType='Error', msg=errMsg, 
                                                forDetailLogs=f'DeleteAllResultsInPlaybook: {traceback.format_exc(None, errMsg)}')         
                        return JsonResponse(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)
                    
            except Exception as errMsg:
                statusCode = HtmlStatusCodes.error
                erroMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllResultsInPlaybook', msgType='Error',
                                          msg=errorMsg, forDetailLogs=errorMsg)
                return JsonResponse(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)
            
        del execRestApiObj
        
        if len(testStillRunningMessages) > 0:
            status = 'failed'
            errorMsg = testStillRunningMessages
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllResultsInPlaybook', 
                                      msgType='Failed', msg=testStillRunningMessages, 
                                      forDetailLogs='')
                     
        return JsonResponse(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
    
class DownloadResults(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DownloadTestResults')
    def post(self,request):
        """
        Download test results
        
        Download is called by <form action={% url "downloadResults" %}? method="POST">. 
        Get the getSelectedTestResult value from the <button name= value=>
        """
        user = AccountMgr().getRequestSessionUser(request)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None 
        tempFolder = None
        
        # <form action="{% url 'downloadResults' %}" method="post"> style
        # Using <button type="submit" name="downloadTestResults" value="{eachResultFolderFullPath}"> to get the value
        downloadTestResults = request.POST.get('downloadTestResults')
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
           
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"downloadTestResults": downloadTestResults}
            restApi = '/api/v1/results/downloadResults'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DownloadResults')   
            return response
        else:
            try:    
                # JS style
                response = self.downloadTestResultFolder(downloadTestResults, user)          
                return response
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'success'
                statusCode = HtmlStatusCodes.success
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DownloadResults', msgType='Error', 
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        #return Response({'status':status, 'errorMsg': errorMsg}, status=statusCode, content_type='application/json')
    
    def downloadTestResultFolder(self, downloadTestResults, user):
        """ 
        Download files to the client is done inside <form action="{% url 'testResults' %}" method="post"></form>
        It is a direct response back to the client.
        """
        import mimetypes
        import zipfile
        from shutil import make_archive
        
        tempFolderIsCreated = False
        currentDir = os.path.abspath(os.path.dirname(__file__))
        # /opt/Keystack/Src/KeystackUI/topbar/docs/restApi/testResults_tempFolderToStoreZipFiles
        tempFolderToStoreZipFiles = f'{currentDir}/testResults_tempFolderToStoreZipFiles'

        # Create a temp folder first
        if os.path.exists(tempFolderToStoreZipFiles) == False:
            try:
                path = Path(tempFolderToStoreZipFiles)
                originalMask = os.umask(000)
                path.mkdir(mode=0o770, parents=True, exist_ok=True)
                os.umask(originalMask)
                tempFolderIsCreated = True
            except Exception as errMsg:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DownloadTestResults', msgType='Error', 
                                          msg="Internal failure: Create temp folder for storing zip file. Check detail logs.", 
                                          forDetailLogs=f'downloadTestResultsFolder(): {traceback.format_exc(None, errMsg)}')
                tempFolderIsCreated = False
        else:
            tempFolderIsCreated = True
            
        if tempFolderIsCreated:     
            try:
                filename = downloadTestResults.split('/')[-1]
                pathToResultFolder = downloadTestResults.replace(filename, '')  # For FileResponse()
                destZipFilename = f'{tempFolderToStoreZipFiles}/{filename}'     # No .zip extension
                zipFileFullPath = f'{destZipFilename}.zip'                      # /full_path/file.zip for os.remove()
                zipFilename = f'{filename}.zip'                                 # zip file name for download filename
                make_archive(destZipFilename, 'zip', downloadTestResults)
                fileType, encoding = mimetypes.guess_type(zipFilename)
                
                if fileType is None:
                    fileType = 'application/octet-stream'

                #response = FileResponse(open(zipFileFullPath, 'rb'))
                response = HttpResponse(open(zipFileFullPath, 'rb'))
                response['Content-Type'] = fileType
                response['Content-Length'] = str(os.stat(zipFileFullPath).st_size)
                if encoding is not None:
                    response['Content-Encoding'] = encoding
                response['Content-Disposition'] = f'attachment; filename={zipFilename}'
                
                if os.path.exists(tempFolderToStoreZipFiles):
                    rmtree(tempFolderToStoreZipFiles)      
                                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DownloadTestResults', msgType='Info',
                                          msg=f'Downloaded results: {zipFilename}')
                return response
            
            except Exception as errMsg:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DownloadTestResults', msgType='Error', 
                                msg="Failed to create downloadable zip file. Check detail logs.", 
                                forDetailLogs=traceback.format_exc(None, errMsg))
                statusCode = HtmlStatusCodes.error

        else:
            statusCode = HtmlStatusCodes.success
                    
           
class ArchiveResults(APIView):
    def post(self,request):
        """ 
        Archive results
        """
        user = AccountMgr().getRequestSessionUser(request)
        # resultsPathList: ['/opt/KeystackTests/Results/DOMAIN=QA/PLAYBOOK=pythonSample/10-14-2022-13:05:25:612106']
        resultsPathList = request.data.get('results', [])
        playbookFolderName = None
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        activeResultsPath = f"{GlobalVars.keystackTestRootPath}/Results"
        archiveResultsPath = f"{GlobalVars.keystackTestRootPath}/ResultsArchive"
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"results": resultsPathList}
            restApi = '/api/v1/results/archive'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='ArchiveResults')
        else:           
            if os.path.exists(archiveResultsPath) == False:
                makeFolder(targetPath=archiveResultsPath, permission=0o770, stdout=False)
                execSubprocessInShellMode(f'chown -R {GlobalVars.user}:{GlobalVars.userGroup} {archiveResultsPath}', showStdout=False)
                               
            for resultsPath in resultsPathList:
                # ['/opt/KeystackTests/Results/DOMAIN=QA/PLAYBOOK=pythonSample/10-14-2022-13:05:25:612106_hgee_debugMode']
                try:
                    match = search('.*/DOMAIN=(.+?)/(PLAYBOOK=.+)/(.+)', resultsPath)
                    if match:
                        domain = match.group(1)
                        playbook = match.group(2)
                        timestampResults = match.group(3)
                        destination = f'{archiveResultsPath}/DOMAIN={domain}/{playbook}/{timestampResults}'
                        
                        if RedisMgr.redis:
                            redisOverallSummary = f'overallSummary-domain={domain}-{timestampResults}'
                            RedisMgr.redis.deleteKey(keyName=redisOverallSummary)
                        
                        if os.path.exists(destination) == False:
                            mkdir2(destination, stdout=False)
                        
                        copytree(resultsPath, destination, dirs_exist_ok=True)
                        # Remove the results from the active test results
                        rmtree(resultsPath)
                        removeEmptyTestResultFolders(user, resultsPath)
                        execSubprocessInShellMode(f'chown -R {GlobalVars.user}:{GlobalVars.userGroup} {destination}', showStdout=False)

                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ArchiveResults', 
                                                msgType='Info', msg=f'results:{resultsPath}')
                    
                except Exception as errMsg:
                    status = 'failed'
                    errorMsg = str(errMsg)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ArchiveResults', msgType='Error',
                                              msg=f'results:{resultsPath}: {traceback.format_exc(None, errMsg)}')
                
        return Response(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)
