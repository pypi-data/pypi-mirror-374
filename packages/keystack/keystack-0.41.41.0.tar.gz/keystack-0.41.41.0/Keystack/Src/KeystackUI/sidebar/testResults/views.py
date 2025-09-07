import os, sys, json, re, traceback
from datetime import datetime
from shutil import rmtree
from glob import glob
from pathlib import Path

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from baseLibs import removeEmptyTestResultFolders
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole

from db import DB
from keystackUtilities import readJson, readYaml, execSubprocessInShellMode 
from domainMgr import DomainMgr
from accountMgr import AccountMgr           
from globalVars import GlobalVars, HtmlStatusCodes
    
class Vars:
    webpage = 'results'
 
                
class TestResults(View):
    @authenticateLogin        
    def get(self, request):
        """
        This view is called by base.html, sidebar. 
        User selects Test Results | Result Archives. 
        Then selects the group/playbook result to view.
        
        This view passed a variable to the testResults.hmtl template:
            'currentResultsFolderPath': resultFolderPath
            
        JS in base.html will automatically call GetTestResultPages and insert the pages
        """
        user = request.session['user']
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        
        # User selects a playbook in test results: /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample
        resultFolderPath = request.GET.get('resultFolderPath')
        
        # activeResults | archiveResults
        typeOfResult = request.GET.get('typeOfResult')
        
        if typeOfResult == 'activeResults':
            title = 'Test Results'
        else:
            title = 'Test Results Archive'
            
        status = HtmlStatusCodes.success
        
        match = re.search('.*DOMAIN=([^ /]+)?/.+', resultFolderPath)
        if match:
            domain = match.group(1)
        else:
            domain = 'Unknown'

        # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample
        #/opt/KeystackTests/ResultsArchive/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample
        match = re.search('.*PLAYBOOK=(.+)', resultFolderPath)
        if match:
            playbook = match.group(1)
        else:
            playbook = 'Unknown'

        #domain = request.GET.get('domain')
        userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
        
        if domain is None:
            if len(userAllowedDomains) > 0:
                if GlobalVars.defaultDomain in userAllowedDomains:
                    domain = GlobalVars.defaultDomain
                else:
                    domain = userAllowedDomains[0]
 
        if domain:
            # AccountMgmt.verifyLogin.getUserRole() uses this
            request.session['domain'] = domain
            domainUserRole = DomainMgr().getUserRoleForDomain(user, domain) 
        else:
            domainUserRole = None
        
        # removeResultsAfterDays = os.environ.get('keystack_removeResultsFolder', GlobalVars.removeResultFoldersAfterDays)
        keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
        removeResultsAfterDays = keystackSettings.get('removeResultsFolder', GlobalVars.removeResultFoldersAfterDays)
        
        # The template shows all the test result folders using testResultFolders
        return render(request, 'testResults.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': title,
                       'domain': domain,
                       'playbook': playbook,
                       'removeResultsAfterDays': removeResultsAfterDays,
                       'resultFolderPath': resultFolderPath,
                       'testResultActiveOrArchive': typeOfResult,
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                      }, status=status)
    
    
            
class GetTestResultPages(View):
    @authenticateLogin
    def post(self, request):
        """
        When users go to a test results page, show page number buttons.
        The buttons will contain the amount of pages to show.
        
        The return html code goes in conjunction with getTestResultTreeView.css.
        
        Requirements:
            - CSS: <link href={% static "commons/css/testResultsTreeView.css" %} rel="stylesheet" type="text/css">
            - html template needs to call addListeners() and getFileContents()
        """
        body = json.loads(request.body.decode('UTF-8'))
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample
        # /opt/KeystackTests/ResultsArchive/DOMAIN=ho/PLAYBOOK=pythonSample
        resultFolderPath = body['resultFolderPath']
        
        # Default to first page: ['0:2']
        pageIndexRange = body['pageIndexRange'][0]
        
        # The page number to get
        getPageNumber = body['getPageNumber']

        getResultsPerPage = body.get('resultsPerPage', 25)
        
        # ADDED
        pageIndex = body['pageIndex']
        pageIndex = int(pageIndex)
        
        indexStart = int(pageIndexRange.split(':')[0])
        indexEnd = int(pageIndexRange.split(':')[1])
        testResultTimestampFolders = []
        startingRange = pageIndexRange.split(":")[0]
             
        try:
            testResultTimestampFolders = glob(f'{resultFolderPath}/*')
        except:
            errorMsg = f'The result folder path is removed: {resultFolderPath}'
            status = HtmlStatusCodes.error

        # Get test results in a reversed list
        datetimeList = []
        for eachTimestampFolder in testResultTimestampFolders:
            datetimeList.append(eachTimestampFolder)
            
        # Got a sorted list
        datetimeList = list(reversed(sorted(datetimeList, key=lambda fileName: datetime.strptime(fileName.split('/')[-1].split('_')[0], "%m-%d-%Y-%H:%M:%S:%f"))))

        totalResults = len(testResultTimestampFolders)
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
                #selectOption = f'<option value="{option}" abc>{option}</option>'
                
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
                    #pages[pageNumber] = (startingIndex, -1)
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
        
        for index in range(indexStart, indexEnd):
            if pageIndex != index:
                continue
            
            # The last page could have less than the calculated pages.
            # Just break out of the loop if there is no more results left to get.
            try:
                eachResultFolderFullPath = datetimeList[index]
            except:
                break
                     
            # eachResultFolderFullPath: /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample/12-20-2022-18:00:49:300483_2054
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
                                 
            if os.path.exists(f'{eachResultFolderFullPath}/overallSummary.json'):
                statusJsonFile = readJson(f'{eachResultFolderFullPath}/overallSummary.json')
                getPagesVars.jsonCounter += 1
                
                started = statusJsonFile['started']
                stopped = statusJsonFile['stopped']
                testResult = statusJsonFile['result']
                testStatus = statusJsonFile['status']
                totalTestAborted = statusJsonFile['totalTestAborted']
                totalCases = statusJsonFile['totalCases']
                totalFailed = statusJsonFile['totalFailed']
                user = statusJsonFile['user']

            # Starting <li>:  Top-level timestamp result folders

            # When user clicks on the download button, the <form action="{% url 'testResults' %}" method="post"> will be directed.
            # Using name="downloadTestResults" to get the value
            getPagesVars.html += f'\n\t\t\t<li><input type="checkbox" name="testResultCheckbox" value="{eachResultFolderFullPath}" />&emsp;<button type=submit class="btn btn-sm btn-outline-primary p-0 px-2" style="height:20px" id="getSelectedTestResult" name="downloadTestResults" value={eachResultFolderFullPath}><i class="fas fa-cloud-arrow-down"></i></button><span class="caret2">&ensp;<a class="nav-link" style="display:inline-block" href="#"><i class="fa-regular fa-folder pr-2"></i>{timestampResultFolder}&emsp;User:{user}&emsp;Result:{testResult}&emsp;Status:{testStatus}&emsp;TotalCases:{totalCases}&emsp;TotalFailed:{totalFailed}&emsp;TotalAborted:{totalTestAborted}</a></span>'
                            
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
                
                for eachFolder in glob(f'{path}/*'):        
                    if os.path.isdir(eachFolder):
                        loop(eachFolder, init=False)
                        getPagesVars.html += '</li></ul>'
                        getPagesVars.counter -= 1
                
            loop(eachResultFolderFullPath, init=True)
            
            for x in range(0, getPagesVars.counter):
               getPagesVars.html += '</ul></li>'
                
            getPagesVars.html += '</li>'
                       
        getPagesVars.html += '</ul>'
            
        return JsonResponse({'pages':getPagesVars.html, 'status':status, 'errorMsg':errorMsg}, status=statusCode)

    
class DeleteAllInGroup(View):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteTestResults', exclue=['engineer'])
    @authenticateLogin
    def post(self, request):
        """
        Delete all test results in GROUP=<groupName>
        
        TODO: Don't delete active test
        """
        body = json.loads(request.body.decode('UTF-8'))
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        # /opt/KeystackTests/Results/DOMAIN=Default
        group = body['group']
        
        try:
            cmd = f'rm -rf {GlobalVars.keystackTestRootPath}/Results/DOMAIN={group}'
            execSubprocessInShellMode(cmd)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllInGroup', msgType='Info',
                                      msg=cmd, forDetailLogs='')
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            erroMsg = str(errMsg)
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllInGroup', msgType='Error',
                                      msg=cmd, forDetailLogs=errorMsg)
             
        return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeleteAllInPlaybook(View):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteTestResults', exclude=['engineer'])
    @authenticateLogin
    def post(self, request):
        """
        Delete all test results in GROUP=<groupName>/PLAYBOOK=<playbookName>
        
        TODO: Don't delete active test
        """
        body = json.loads(request.body.decode('UTF-8'))
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        # /opt/KeystackTests/Results/DOMAIN=Default
        path = body['path']
        
        try:
            cmd = f'rm -rf {path}'
            execSubprocessInShellMode(cmd)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllResultsInPlaybook', msgType='Info',
                                      msg=cmd, forDetailLogs='')
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            erroMsg = str(errMsg)
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteAllResultsInPlaybook', msgType='Error',
                                      msg=cmd, forDetailLogs=errorMsg)
             
        return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
    
            
    '''        
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='Delete/Download')
    def post(self, request):
        """
        Delete and download test results
        
        Delete is called by Javascript fetch.
        Download is called by <form action={% url "testResults" %}? method="POST">. 
        Get the getSelectedTestResult value from the <button name= value=>
        """
        try:    
            # <form action="{% url 'testResults' %}" method="post"> style
            downloadTestResults = request.POST.get('downloadTestResults')
            
            # JS style
            #body = json.loads(request.body.decode('UTF-8'))
            #downloadTestResults = body['downloadTestResults']
            if downloadTestResults:
                return self.downloadTestResultFolder(downloadTestResults, request.session['user'])
        except:
            downloadTestResults = False

        try:
            deleteTestResults = json.loads(request.body.decode('UTF-8'))   
        except:
            deleteTestResults = False

        if deleteTestResults:
            # {'deleteTestResults': ['/opt/KeystackTests/Results/DOMAIN=QA/PLAYBOOK=pythonSample/10-15-2022-17:42:49:516252_qa']}
            statusCode = self.deleteTestResultFolders(deleteTestResults, request.session['user'])
            
            if statusCode == HtmlStatusCodes.error:
                status = 'failed'
            else:
                status = 'success'
                    
        return JsonResponse({'status':status}, status=statusCode, content_type='application/json')

    def deleteTestResultFolders(self, deleteTestResults, user):            
        try:
            deletedResultList = []
            for resultFolder in deleteTestResults['deleteTestResults']:
                # resultFolder: /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample/10-26-2022-14:42:25:471305_809                
                rmtree(resultFolder)
                deletedResultList.append(resultFolder)
                removeEmptyTestResultFolders(user, resultFolder)

            HtmlStatusCodes.success
            if deletedResultList:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestResults',
                                          msgType='Info', msg=f'Deleted results: {deletedResultList}')
            
            statusCode = HtmlStatusCodes.success 
            
        except Exception as errMsg:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteTestResults', 
                                      msgType='Error', msg=errMsg, 
                                      forDetailLogs=f'DeleteTestResults: {traceback.format_exc(None, errMsg)}')
            statusCode = HtmlStatusCodes.error
    
        return statusCode

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
        # /opt/Keystack/KeystackUI/sidebar/testResults/tempFolderToStoreZipFiles
        tempFolderToStoreZipFiles = f'{currentDir}/tempFolderToStoreZipFiles'

        # Create a temp folder first
        if os.path.exists(tempFolderToStoreZipFiles) == False:
            try:
                path = Path(tempFolderToStoreZipFiles)
                originalMask = os.umask(000)
                path.mkdir(mode=0o770, parents=True, exist_ok=True)
                os.umask(originalMask)
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

                response = FileResponse(open(zipFileFullPath, 'rb'))
                response['Content-Type'] = fileType
                response['Content-Length'] = str(os.stat(zipFileFullPath).st_size)
                if encoding is not None:
                    response['Content-Encoding'] = encoding
                    
                response['Content-Disposition'] = f'attachment; filename={zipFilename}'
                
                #os.remove(zipFileFullPath)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DownloadTestResults', msgType='Info',
                                          msg=f'Downloaded results: {zipFilename}')
                return response
            
            except Exception as errMsg:
                SystemLogsAssistant().log(user=user, webPage='results', action='DownloadTestResults', msgType='Error', 
                                msg="Failed to create downloadable zip file. Check detail logs.", 
                                forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
                statusCode = HtmlStatusCodes.error
        else:
            statusCode = HtmlStatusCodes.error
    '''
    

'''        
class SidebarTestResults(View):
    @authenticateLogin
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
        user = request.session['user']
        body = json.loads(request.body.decode('UTF-8'))
        whichResult = body['whichResultType']
        htmlTestResults = ''
        
        try:
            testResults = dict()
            testResults['activeResults'] = dict()
            testResults['archiveResults'] = dict()
            status = 'success'
            errorMsg = None
            statusCode = HtmlStatusCodes.success
            
            for groupPath in glob(f"{GlobalVars.resultsFolder}/DOMAIN*"):
                group = groupPath.split('/')[-1].split('=')[-1]
                testResults['activeResults'][group] = []
                
                for playbookPath in glob(f'{groupPath}/PLAYBOOK*'):
                    testResults['activeResults'][group].append(playbookPath)
                    
            if os.path.exists(GlobalVars.archiveResultsFolder):
                for groupPath in glob(f"{GlobalVars.archiveResultsFolder}/DOMAIN*"):
                    group = groupPath.split('/')[-1].split('=')[-1]
                    testResults['archiveResults'][group] = []
                    for playbookPath in glob(f'{groupPath}/PLAYBOOK*'):
                        testResults['archiveResults'][group].append(playbookPath)    
            
            htmlTestResults += '<center><p class="pt-3 pb-2 textBlack fontSize12px">Select a Playbook</p></center>'
            
            for group,playbookList in testResults[whichResult].items():
                htmlTestResults += f'<p class="pl-2 pb-0 marginLeft10 textBlack fontSize12px">Test Group: {group}</p>'
                
                htmlTestResults += '<p>'
                
                for playbookPath in playbookList:
                    playbookName = playbookPath.split('/')[-1].split('=')[-1].replace('-', '/')
                    htmlTestResults += f'<a class="collapse-item fontSize12px" href="/testResults?resultFolderPath={playbookPath}&typeOfResult={whichResult}"><i class="fa-regular fa-folder pr-3"></i>{playbookName}</a>'
                    
                htmlTestResults += '</p>'
                    
        except Exception as errMsg:
            erroMsg = str(errMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestResults', msgType='Error', msg=errMsg,
                                      forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
        
        return JsonResponse({'status':status, 'errorMsg':errorMsg, 'testResults':htmlTestResults}, status=statusCode)
'''
  
'''           
class GetTestResultFileContents(View):
    @authenticateLogin
    def get(self, request):
        """
        Selected to open a PDF file. Open PDF in a new tab. 
        The PDF link is created in the TestResult() class treewalk() function.
        """
        filePath = request.GET.get('testResultFile')
        from django.http import FileResponse
        
        user = request.session['user']
        
        if 'pdf' in filePath:
            return FileResponse(open(filePath, 'rb'), content_type='application/pdf')
        else:
            return FileResponse(open(filePath, 'rb'), content_type='text/plain')
    
    @authenticateLogin    
    def post(self, request):
        """
        Get file contents.
        This post is called by testResult.hmtl template in the readTestResultFile() <scripts>.
        
        The <a href="#" data=value="$file">

        Expect: <file path> and <file name> separated by dash
                Ex: /Keystack/Modules/LoadCore/GlobalVariables&globalVariables.yml
        """
        body = json.loads(request.body.decode('UTF-8'))
        filePath = body['testResultFile']
        fileExtension = filePath.split('/')[-1].split('.')[-1]
        user = request.session['user']
        status = HtmlStatusCodes.success
        
        try:
            if fileExtension == 'zip':
                fileContents = ''
            
            elif fileExtension == 'pdf':
                from django.http import FileResponse
                return FileResponse(open(filePath, 'rb'), content_type='application/pdf', status=HtmlStatusCodes.success)
        
            else:
                with open(filePath) as fileObj:
                    contents = fileObj.read()
                    
                # Use <pre> to render the file format
                fileContents = f'<pre>{contents}</pre>'
            
        except Exception as errMsg:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestResultsContents', msgType='Error',
                            msg=f'Failed to open file contents for viewing: {filePath}', forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
            status = HtmlStatusCodes.error

        data = {'fileContents': fileContents}
        return JsonResponse(data, content_type='application/json', status=status)    


class GetNestedFolderFiles(View):
    @authenticateLogin
    def post(self, request):
        body = json.loads(request.body.decode('UTF-8'))
        user = request.session['user']
        nestedFolderPath = body['nestedFolderPath']
        insertToDivId = body['insertToDivId']
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        html = ''
        nestedFolderUniqueCounter = 200000
        
        import random
        randomNumber = str(random.sample(range(100,10000), 1)[0])
        caretName = f"caret{randomNumber}"
                                
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
                   
        #print(f'\n--- GetNestedFolderFiles: nestedFolderPath:{nestedFolderPath}  insertToDivId={insertToDivId}')
        return JsonResponse({'folderFiles':html, 'caretName': caretName, 'newVarName': f'newVar_{randomNumber}',
                             'status':status, 'errorMsg':errorMsg}, status=statusCode)
'''
 
