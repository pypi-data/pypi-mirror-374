import json, os, sys, traceback
      
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from domainMgr import DomainMgr
from accountMgr import AccountMgr
from globalVars import GlobalVars, HtmlStatusCodes

class Vars:
    webpage = 'pipelines'

 
class SessionMgmt(View):
    @authenticateLogin
    def get(self, request):
        """
        Get all the top-level folders for each module for users to dig into.
        When a user clicks on a module folder, the content page has a dropdown menu
        to select subfolders and files to view or modify.
        """
        user = request.session['user']
        
        # SessionMgmt view is the default login page.
        # domain will be None
        domain = request.GET.get('domain')
        userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        
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
                  
        # current|archive
        view = request.GET.get('view', 'current') 

        # getPlaybookNames() -> For selecting a playbook to play
        #  [('pythonSample.yml', '/opt/KeystackTests/Playbooks/pythonSample.yml'), ('loadcoreSample.yml', '/opt/KeystackTests/Playbooks/loadcoreSample.yml'), ('airMosaic.yml', '/opt/KeystackTests/Playbooks/airMosaic.yml'), ('loadcore_5Loops.yml', '/opt/KeystackTests/Playbooks/loadcore_5Loops.yml'), ('playbookTemplate.yml', '/opt/KeystackTests/Playbooks/playbookTemplate.yml'), ('/qa/qa1.yml', '/opt/KeystackTests/Playbooks/qa/qa1.yml)'), ('/qa/dev/dev1.yml', '/opt/KeystackTests/Playbooks/qa/dev/dev1.yml)')]

        # Shows sessionMgmt.html, which uses JS to automatically call getSessions(). 
        # This function passes in the domain to show. Uses the following to set
        # the domain for JS getSession() to get.
        # <div id='getSessionGroupToShow' domain={{showDomainSessions}}> view={{showGroupView}}</div> 
        # It calls the class GetSessions with the selected domain
        
        # mainControllerIp: Informs base.html the main controller IP
        #                   Every view page must include this.
        # 
        return render(request, 'sessionMgmt.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'showDomainView': view,
                       'topbarTitlePage': 'Pipelines',
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domain': domain,
                       'domainUserRole': domainUserRole,
                       'wsPipelineRoom': 'wsPipelineRoom',
                      }, status=HtmlStatusCodes.success)   


class SessionDetails(View):
    @authenticateLogin
    def get(self, request):
        """
        Get all the top-level folders for each module for users to dig into.
        When a user clicks on a module folder, the content page has a dropdown menu
        to select subfolders and files to view or modify.
        """
        user = request.session['user']
        #request.session['domain'] = GlobalVars.defaultDomain
        # domain = GlobalVars.defaultDomain
        # userRole = DomainMgr().getUserRoleForDomain(user, domain)
        
        domain = request.GET.get('domain')
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
            userRole = DomainMgr().getUserRoleForDomain(user, domain) 
        else:
            userRole = None
            
        testResultsPath = request.GET.get('testResultsPath')

        return render(request, 'sessionDetails.html',
                      {'testResultsPath': testResultsPath,
                       'topbarTitlePage': f'Session Details',
                       'domain': domain,
                       'userLevel': userRole,
                       'user': request.session['user']
                      }, status=HtmlStatusCodes.success)
    
    '''    
    @authenticateLogin
    def post(self, request):
        """ 
        Get the session details
        
        The folder toggler works in conjuntion with an addListener in getTestcaseData() 
        and keystackDetailedLogs CSS
        """
        try:
            body = json.loads(request.body.decode('UTF-8'))
            testResultsPath = body['testResultsPath']
            status = keystackUtilities.readJson(f'{testResultsPath}/moduleSummary.json')
            
            # Verify if the overall test is terminated
            overallSummaryFile = f'{testResultsPath.split("STAGE")[0]}/overallSummary.json'
            overallStatus = keystackUtilities.readJson(overallSummaryFile)
            
            user = request.session['user']
            playbookFullPath = status['playbook']
            match = search(f'{GlobalVars.keystackTestRootPath}/Playbooks/([^ ]+)\.', playbookFullPath)
            if match:
                playbook = match.group(1)
            else:
                playbook = 'Unknown'
                
            # STAGE=Tests_MODULE=CustomPythonScripts_ENV=loadcoreSample
            match = search('(STAGE=.*)_MODULE.*', testResultsPath)
            if match:
                stage = match.group(1).replace('=', ': ')
                
            match = search('STAGE=.*_(MODULE=.*)_ENV', testResultsPath)
            if match:
                module = match.group(1).replace('=', ': ')

            match = search('STAGE=.*_MODULE=.*_(ENV.*)', testResultsPath)
            if match:
                env = match.group(1).replace('=', ': ')
            
            statusCode = HtmlStatusCodes.success

        except Exception as errMsg:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Get', msgType='Error',
                                        msg=f'sessionDetails(): {errMsg}',
                                        forDetailLogs=f'sessionDetails() -> {traceback.format_exc(None, errMsg)}')
            statusCode = HtmlStatusCodes.error

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
                               
        #sessionData = f'<div class="row col-xl-8">{stage}&emsp;&emsp;{module}&emsp;&emsp;{env}</div><br>'
        stageModuleEnv = f'{stage}&ensp;&emsp;{module}&ensp;&emsp;{env}'
        sessionData = '<div class="row">'
        sessionData += createCard(testTime)
        
        if status['status'] not in ['Completed', 'Terminated', 'Aborted']:
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
        # Testcases begin here
        
        class getPagesVars:
            counter = 0
            
        timestampResultFolder = testResultsPath.split('/')[-1]
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
                path = testResultsPath
                getPagesVars.html += f'<li style="margin-left:17px"> <span class="caret2"><i class="fa-regular fa-folder pr-2"></i>{stage}&emsp;&ensp; {module}&emsp;&ensp; {env}</span>'
                
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
                    # The the testcase results first so results could be shown next to the testcase folder
                    for eachFile in glob(f'{eachFolder}/*'):
                        if 'testSummary.json' in eachFile:
                            testcaseSummary = keystackUtilities.readJson(eachFile)
                            status = testcaseSummary['status']
                            result = testcaseSummary['result']
                    
                    if index == 1:
                        isTestcaseFolder = True
                    else:
                        isTestcaseFolder = False
                                
                    loop(eachFolder, init=False, status=status, result=result, isTestcaseFolder=isTestcaseFolder)
                    getPagesVars.html += '</li></ul>'
                    getPagesVars.counter -= 1
            
        loop(testResultsPath, init=True)
        
        for x in range(0, getPagesVars.counter):
            getPagesVars.html += '</ul></li>'
            
        getPagesVars.html += '</ul>'        

        return JsonResponse({'sessionData': sessionData, 'testcaseData': getPagesVars.html,
                             'stageModuleEnv':stageModuleEnv}, status=statusCode) 
    '''

'''     
class GetSessions(View):    
    @authenticateLogin
    def post(self, request):
        user = request.session['user']
        body = json.loads(request.body.decode('UTF-8'))
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success 
        # view: current | archive
        view = body['view']
        group = body['group']
        tableData = ''
        # The current controller. Default to the main controller if None 
        controller = body.get('controller', request.session['mainControllerIp'])
        
        if ":" in controller:
            controllerIp = controller.split(":")[0]
            # ipPort is str type
            ipPort = controller.split(":")[-1]
        else:
            controllerIp = controller 
            ipPort = '' 
         
        try:
            overallDetailsHtml = ''
            
            # 28.7 = iNP29xnXdlnsfOyausD_EQ
            # 28.17 = da3XzmXRitPueJr4uPgBog
            if controller != request.session['mainControllerIp']:
                # Coming in here means to view a remote controller
                # Get the Access-Key from the remote_<controller_ip>.yml file
                controllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'
                controllerRegistryFile = f'{controllerRegistryPath}/remote_{controllerIp}.yml'
            
                if os.path.exists(controllerRegistryFile):
                    data = keystackUtilities.readYaml(controllerRegistryFile)                    
                    restObj = ExecRestApi(ip=controllerIp, port=ipPort, https=data['https'],
                                          headers={"Content-Type": "application/json", "Access-Key": data['accessKey']})

                    params = {"view":view, "group":group}
                    response = restObj.get('/api/v1/sessions', params=params)
                    del restObj 
                    
                    if str(response.status_code).startswith('2') == False:
                        #  {"sessions": {}, "status": "failed", "errorMsg": "GET Exception error 2/2 retries: HTTPSConnectionPool(host='192.168.28.17', port=8028): Max retries exceeded with url: /api/v1/sessions?view=current&group=Default (Caused by SSLError(SSLError(1, '[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:997)')))"}
                        error = json.loads(response.content.decode('utf-8'))
                        errorMsg = error['errorMsg']
                        
                        if settings.KEYSTACK_SESSIONS_CONNECTIVITY == True:
                            settings.KEYSTACK_SESSIONS_CONNECTIVITY = False
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetSessions', msgType='Error',
                                                    msg=errorMsg, forDetailLogs='')

                        return JsonResponse({'status': 'failed', 'errorMsg': errorMsg, 'tableData': ''}, status=406)
                                    
                    tableData = response.json()['sessions']
            else:
                tableData, overallDetails = SessionMgmt().getTableData(view, group)
                settings.KEYSTACK_SESSIONS_CONNECTIVITY = True
                
     
                # overallDetails is from getTableData()
                overallDetailsHtml += '<center>'
                overallDetailsHtml += f'Total-Pipelines: {overallDetails["sessions"]}&emsp;&emsp;&emsp; Running: {overallDetails["running"]}&emsp;&emsp;&emsp;'
                overallDetailsHtml += f'Completed: {overallDetails["completed"]}&emsp;&emsp;&emsp; Aborted: {overallDetails["aborted"]}&emsp;&emsp;&emsp;'
                overallDetailsHtml += f'Terminated: {overallDetails["terminated"]}&emsp;&emsp;&emsp; Paused-On-Failure: {overallDetails["pausedOnFailure"]}&emsp;&emsp;&emsp;'
                overallDetailsHtml += f'Passed: {overallDetails["passed"]}&emsp;&emsp;&emsp; Failed: {overallDetails["failed"]}'
                overallDetailsHtml += '</center>'
                
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetSessions', msgType='Error', msg=errMsg,
                                      forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
            statusCode = HtmlStatusCodes.error
            
        return JsonResponse({'status':status, 'errorMsg':errorMsg, 'tableData':tableData, 'overallDetails':overallDetailsHtml}, status=statusCode)


class GetTestReport(View):
    @authenticateLogin
    def post(self,request):
        body = json.loads(request.body.decode('UTF-8'))
        testReportPath = body['testReportPath']
        user = request.session['user']
        
        try:
            testReport = keystackUtilities.readFile(testReportPath)
            statusCode = HtmlStatusCodes.success
        except Exception as errMsg:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestReport', msgType='Error',
                                      msg=errMsg, forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
            testReport = f'Error: {errMsg}'
            statusCode = HtmlStatusCodes.error
            
        return JsonResponse({'testReportInsert': testReport}, status=statusCode, safe=False)
    
    
class GetTestLogs(View):
    @authenticateLogin
    def post(self,request):
        body = json.loads(request.body.decode('UTF-8'))
        testResultPath = body['testResultPath']
        user = request.session['user']
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        
        try:
            testLogs = getArtifacts(testResultPath)
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestLogs', msgType='Error',
                                      msg=errMsg, forDetailLogs=f'{traceback.format_exc(None, errMsg)}')
            testlogs = f"Error: {errMsg}"

        return JsonResponse({'status':status, 'errorMsg':errorMsg, 'testLogsHtml': testLogs, 
                             'test': testResultPath.split('/')[-1]}, status=statusCode, safe=False)


class GetJobSchedulerCount(View):
    @authenticateLogin
    def get(self, request):
        """
        Get the total amount of scheduled jobs
        """
        totalCronJobs = len(JobScheduler().getCurrentCronjobList())
        statusCode = HtmlStatusCodes.success
        return JsonResponse({'totalScheduledJobs': totalCronJobs}, status=statusCode)


class GetCronScheduler(View):
    @authenticateLogin
    def get(self, request):
        """
        Dropdowns for minute, hour, day, month, dayOfWeek
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        
        minute = f'<label for="minute">Minute:&emsp; </label>'
        minute += '<select id="minute">'
        minute += f'<option value="*" selected="selected">*</option>'
        for option in range(0, 61):            
            minute += f'<option value="{option}">{option}</option>'
        minute += f'</select> &emsp;&emsp;'
        
        hour = f'<label for="hour">Hour:&emsp; </label>'
        hour += '<select id="hour">'
        hour += f'<option value="*" selected="selected">*</option>'
        for option in range(0, 24):            
            hour += f'<option value="{option}">{option}</option>'
        hour += f'</select> &emsp;&emsp;'

        dayOfMonth = f'<label for="dayOfMonth">Day Of Month:&emsp; </label>'
        dayOfMonth += '<select id="dayOfMonth">'
        dayOfMonth += f'<option value="*" selected="selected">*</option>'
        for option in range(1, 32):            
            dayOfMonth += f'<option value="{option}">{option}</option>'
        dayOfMonth += f'</select> &emsp;&emsp;'

        month = f'<label for="month">Month:&emsp; </label>'
        month += '<select id="month">'
        month += f'<option value="*" selected="selected">*</option>'
        for option in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:            
            month += f'<option value="{option}">{option}</option>'
        month += f'</select> &emsp;&emsp;'

        dayOfWeek = f'<label for="dayOfWeek">Day Of Week:&emsp; </label>'
        dayOfWeek += '<select id="dayOfWeek">'
        dayOfWeek += f'<option value="*" selected="selected">*</option>'
        for option in ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']:            
            dayOfWeek += f'<option value="{option}">{option}</option>'
        dayOfWeek += f'</select>'
                                                
        return JsonResponse({'minute':minute, 'hour':hour, 'dayOfMonth':dayOfMonth, 'month':month, 'dayOfWeek':dayOfWeek}, status=statusCode)

                   
class JobScheduler(View):       
    def getCurrentCronjobs(self):
        """ 
        Get the as-is /etc/crontab file
        """
        cronJobs = ''
        if os.path.exists('/etc/crontab'):
            with open('/etc/crontab', 'r') as cronObj:
                currentCron = cronObj.readlines()
        
            for line in currentCron:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('#'):
                    continue
                
                if 'playbook' not in line:
                    continue
                
                cronJobs += f'{line}\n'

        return cronJobs        
    
    def getCurrentCronjobList(self):
        """ 
        Create a crontab list
        """
        cronjobs = self.getCurrentCronjobs()

        from re import search
        
        cronlist = []
        for job in cronjobs.split('\n'):
            if job == '':
                continue 
            
            if bool(search('.*SHELL', job)) or bool(search('.*PATH', job)):
                continue

            cronlist.append(job)
 
        return cronlist
     
    def isCronExists(self, playbook, min, hour, day, month, dayOfWeek):
        currentCronList = self.getCurrentCronjobList()
        if len(currentCronList)  == 0:
            return False
        
        for eachCron in self.getCurrentCronjobList():
            match = search(' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*playbook=([^ &]+).*-H', eachCron)
            if match:
                cronMin       = match.group(1)
                cronHour      = match.group(2)
                cronDay       = match.group(3)
                cronMonth     = match.group(4)
                cronDayOfWeek = match.group(5)
                cronPlaybook  = match.group(6)
                
                cronList = [cronPlaybook, cronMin, cronHour, cronDay, cronMonth, cronDayOfWeek]
                newList  = [playbook, min, hour, day, month, dayOfWeek]
                if set(cronList) == set(newList):
                    # Found existing cron
                    return True
     
        return False
                   
    @authenticateLogin
    def get(self, request):        
        """ 
        Create job scheduler data table. Called by template.
        """
        #html = '<table class="table table-sm table-bordered table-fixed tableFixHead">'
        html = '<table class="tableMessages table-bordered">'
        html += '<thead>'
        html += '<tr>'
        html += '<th>Delete</th>'
        html += '<th>Playbook</th>'
        html += '<th>Scheduled To Run</th>'
        html += '</tr>'
        html += '</thead>'

        try:
            user = request.session['user']
            cronjobs = JobScheduler().getCurrentCronjobList()

            # 25 12 24 3 * root curl -d "playbook=goody&user=Hubert Gee" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://172.16.1.16:8000/api/playbook
            # <a href="#" testLogResultPath="{moduleTestResultsPath}" onclick="openTestLogsModal(this)" data-bs-toggle="modal" data-bs-target="#testLogsModalDiv">View Logs</a>
            for eachCron in cronjobs:
                # Handle the \t: '17 *\t* * *\troot    cd / && run-parts --report /etc/cron.hourly
                eachCron = eachCron.replace('\t', ' ')
                
                # [{playbook, month, day, hour, min}]
                # 00 14 31 3 * root curl -d "playbook=sanity&user=Hubert Gee"

                # 42 11 6 10 * keystack curl -d "playbook=/opt/KeystackTests/Playbooks/pythonSample.yml&awsS3=False&jira=False&pauseOnError=False&debug=False" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/run
                #
                match = search(' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*playbook=([^ &]+).*-H', eachCron)
                if match:
                    min       = match.group(1)
                    hour      = match.group(2)
                    day       = match.group(3)
                    month     = match.group(4)
                    dayOfWeek = match.group(5)
                    playbook  = match.group(6)

                    html += '<tr>'
                    html += f'<td class="textAlignCenter"><input type="checkbox" name="jobSchedulerMgmt" playbook={playbook} dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                    html += f'<td>{playbook}</td>'
                    html += f'<td>Minute:{min}&emsp; Hour:{hour}&emsp; DayOfMonth:{day}&emsp; Month:{month}&emsp; DayOfWeek:{dayOfWeek}</td>'
                    html += '</tr>'
                else:
                    match     = search(' *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+).*', eachCron)
                    min       = match.group(1)
                    hour      = match.group(2)
                    day       = match.group(3)
                    month     = match.group(4)
                    dayOfWeek = match.group(5)
                    html += '<tr>'
                    html += f'<td class="textAlignCenter"><input type="checkbox" name="jobSchedulerMgmt" playbook="" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                    html += f'<td></td>'
                    html += f'<td>Minute:{min}&emsp; Hour:{hour}&emsp; DayOfMonth:{day}&emsp; Month:{month}&emsp; DayOfWeek:{dayOfWeek}</td>'
                    html += '</tr>'
                                        
            html += '</table>'    
            statusCode = HtmlStatusCodes.success
            
        except Exception as errMsg:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetScheduledJobs', msgType='Error',
                                      msg=errMsg, forDetailLogs=f'GetScheduledJob: {traceback.format_exc(None, errMsg)}')
            statusCode = HtmlStatusCodes.error
            
        return JsonResponse({'jobSchedules': html}, status=statusCode)
        
    def removeCronJobs(self, listOfJobsToRemove, user):
        """
        Crontab example: 
            25 12 24 3 * root curl -d "playbook=goody&user=Hubert Gee" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://172.16.1.16:8000/api/playbook
         
        listOfJobsToRemove: <list of dicts>:  
              [{'playbook': '/opt/KeystackTests/Playbooks/pythonSample.yml', 'month': '10', 'day': '6', 'hour': '11', 'minute': '42'}, {}, ...]
        """
        cronJobs = self.getCurrentCronjobList()
        if not cronJobs:
            return
        
        def deleteCron(min, hour, day, month, dayOfWeek, playbook):
            cronJobs = self.getCurrentCronjobList()
            
            for index,eachCron in enumerate(cronJobs):
                if playbook and bool(search(f'{min} *{hour} *{day} *{month} *{dayOfWeek}.*playbook={playbook}.*', eachCron)):
                    cronJobs.pop(index)
                    break            
                                    
        for removeJob in listOfJobsToRemove:
            # {'playbook': 'pythonSample', 'month': '*', 'day': '*', 'hour': '*', 'minute': '*', 'dayOfWeek': '*'}
            playbook =  removeJob['playbook']
            min =       removeJob["minute"]
            hour =      removeJob["hour"]
            day =       removeJob["day"]
            month =     removeJob["month"]
            dayOfWeek = removeJob["dayOfWeek"]
            
            for cronProperty in [{'min':min}, {'hour':hour}, {'day':day}, {'month':month}, {'dayOfWeek':dayOfWeek}]:
                for key,value in cronProperty.items():
                    if value == "*":
                        # The template already added slashes.  runPlaybook does not add slashes.
                        if key == 'min': min = '\\*'
                        if key == 'hour': hour = '\\*'
                        if key == 'day': day = '\\*'
                        if key == 'month': month = '\\*'
                        if key == 'dayOfWeek': dayOfWeek = '\\*'

            for index,eachCron in enumerate(cronJobs):
                # each cron: * * * * * keystack curl -d "sessionId=&playbook=pythonSample&awsS3=False&jira=False&pauseOnError=False&debug=False&group=Default&scheduledJob="minute=* hour=* dayOfMonth=* month=* dayOfWeek=*"&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/run
                
                # eachCron: 18 19 24 3 * root curl -d "playbook=playbookName&user=user" 
                if bool(search(f'{min}\s+{hour}\s+{day}\s+{month}\s+{dayOfWeek}.*playbook={playbook}&.*', eachCron)):
                    cronJobs.pop(index)
                    break
                    
        if cronJobs:
            updatedCronJobs = ''
            for cron in cronJobs:
                # The crontab file may contain some unknown Linux OS cron jobs. Exclude them.
                if 'playbook' in cron:
                    updatedCronJobs += f'{cron}\n'
        
            try:
                keystackUtilities.execSubprocessInShellMode(f"sudo echo '{updatedCronJobs}' | sudo tee /etc/crontab", showStdout=False)
                    
            except Exception as errMsg:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removeScheduledJob', msgType='Error',
                                          msg=cronJobs.replace('\\'), forDetailLogs=f'removeScheduledJob: {traceback.format_exc(None, errMsg)}')
        else:
            try:
                keystackUtilities.execSubprocessInShellMode('sudo echo "" | sudo tee /etc/crontab', showStdout=False)

            except Exception as errMsg:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removeScheduledJob', msgType='Error',
                                          msg=cronJobs.replace('\\'), forDetailLogs=f'clearAllScheduledJob: {traceback.format_exc(None, errMsg)}')

    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='DeleteScheduledJob', exclude="engineer")      
    def delete(self, request):
        """ 
        Delete a scheduled job.  Called from template.
        """
        body = json.loads(request.body.decode('UTF-8'))
        removeScheduledJobs = body['removeScheduledJobs']
        user = request.session['user']
        
        try:
            #  [{playbook, month, day, hour, min}, {}, ...]
            removeJobList = []
            
            for cron in removeScheduledJobs:
                # eachJob: {'playbook': 'goody', 'month': '3', 'day': '26', 'hour': '17', 'minute': '29'}
                #removeJobList.append({'playbook':cron['playbook'], 'month':cron['month]'], 'day':cron['day'], 'hour':cron['hour'], 'min':cron['minute']})
                
                # {'playbook': 'pythonSample', 'month': '*', 'day': '*', 'hour': '*', 'minute': '*', 'dayOfWeek': '*'}
                removeJobList.append(cron)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveScheduledJobs', msgType='Info',
                                          msg=cron, forDetailLogs='')
                    
            JobScheduler().removeCronJobs(listOfJobsToRemove=removeJobList, user=user)
            statusCode = HtmlStatusCodes.success
            
        except Exception as errMsg:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveScheduledJobs', msgType='Error',
                                      msg=f'RemoveScheduledJobs: {errMsg}', 
                                      forDetailLogs=f'RemoveScheduledJobs: {traceback.format_exc(None, errMsg)}')            
            statusCode = HtmlStatusCodes.error
            
        return JsonResponse({}, status=statusCode)
                                       
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='JobScheduler')
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
        try:
            # body: {'minute': '*', 'hour': '*', 'dayOfMonth': '*', 'month': '*', 'dayOfWeek': '*', 'removeJobAfterRunning': False, 'controller': '192.168.28.7:8000', 'playbook': '/opt/KeystackTests/Playbooks/pythonSample.yml', 'debug': False, 'emailResults': False, 'awsS3': False, 'jira': False, 'pauseOnError': False, 'holdEnvsIfFailed': False, 'abortTestOnFailure': False, 'includeLoopTestPassedResults': False, 'sessionId': '', 'group': 'Default'}
            body = json.loads(request.body.decode('UTF-8'))
            user = request.session['user']
            localHostIp = os.environ.get('keystack_localHostIp', 'localhost')
            keystackIpPort = os.environ.get('keystack_keystackIpPort', '8028')
            cronjobUser = 'keystack'
            statusCode = HtmlStatusCodes.success
            status = 'success'
            error = None

            # 2022-03-23T02:00:00-07:00
            minute = body['minute']
            hour = body['hour']
            dayOfMonth = body['dayOfMonth']
            month = body['month']
            dayOfWeek = body['dayOfWeek']
            removeJobAfterRunning = body['removeJobAfterRunning']
            
            if 'group' in body:
                group = body['group']
            else:
                group = 'Default'
             
            sessionId = body['sessionId']   
            playbook = body['playbook']
            debugMode = body['debug']
            awsS3 = body['awsS3']
            jira = body['jira']
            emailResults = body['emailResults']
            pauseOnError = body['pauseOnError']
            holdEnvsIfFailed = body['holdEnvsIfFailed']
            abortTestOnFailure = body['abortTestOnFailure']
            includeLoopTestPassedResults = body['includeLoopTestPassedResults']
            
            schedule = f'playbook={playbook} minute={minute} hour={hour} day={dayOfMonth} month={month} dayOfWeek={dayOfWeek}'
            
            if self.isCronExists(playbook, minute, hour, dayOfMonth, month, dayOfWeek):
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='JobScheduler', msgType='Info', msg='Cron already exists: {schedule}')
                return JsonResponse({'status':'failed', 'error':'Failed: Already exists'}, status=statusCode)
            
            # REST API: Run playbook function is in Playbook apiView.py
            # For job scheduling, include the param -webhook to bypass verifying api-key
            #newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} keystack curl -d "sessionId={sessionId}&playbook={playbook}&awsS3={awsS3}&jira={jira}&pauseOnError={pauseOnError}&debug={debugMode}&group={group}&holdEnvsIfFailed={holdEnvsIfFailed}&abortTestOnFailure={abortTestOnFailure}&includeLoopTestPassedResults={includeLoopTestPassedResults}&scheduledJob=\'{schedule}\'&removeJobAfterRunning={removeJobAfterRunning}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/playbook/run'
            
            newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} {cronjobUser} curl -d "sessionId={sessionId}&playbook={playbook}&awsS3={awsS3}&jira={jira}&pauseOnError={pauseOnError}&debug={debugMode}&group={group}&holdEnvsIfFailed={holdEnvsIfFailed}&abortTestOnFailure={abortTestOnFailure}&includeLoopTestPassedResults={includeLoopTestPassedResults}&scheduledJob=\'{schedule}\'&removeJobAfterRunning={removeJobAfterRunning}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/playbook/run'
            
            cronJobs = self.getCurrentCronjobs()
            cronJobs += f'{newJob}\n'
            
            # Leaving behind for debugging purpose
            #cronJobs = f"""
            #{newJob}
            #* * * * * root date > /proc/1/fd/1 2>/proc/1/fd/2
            #* * * * * root echo "Hello World! 8" >/proc/1/fd/1 2>/proc/1/fd/2
            #"""

            keystackUtilities.execSubprocessInShellMode(f"sudo echo '{cronJobs}' | sudo tee /etc/crontab", showStdout=False)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ScheduledJob', msgType='Info', msg=newJob.replace('&webhook=true', ''))            
            
        except Exception as errMsg:
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ScheduledJob', msgType='Error',
                                      msg=errMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return JsonResponse({'status':status, 'error':error}, status=statusCode)
  

class TerminateProcessId(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='Terminate')
    def post(self,request):
        """ 
        body: {'sessionId': 'awesomeTest2', 'playbook': '/opt/KeystackTests/Playbooks/pythonSample.yml', 'module': 'CustomPythonScripts2', 'processId': '36895', 'statusJsonFile': '/opt/KeystackTests/Results/PLAYBOOK=pythonSample/09-30-2022-15:31:36:496194_awesomeTest2/overallSummary.json'}
        """
        body = json.loads(request.body.decode('UTF-8'))
        sessionId = body['sessionId']
        processId = body['processId']
        playbook = body['playbook']
        module = body['module']
        statusJsonFile = body['statusJsonFile']
        timestampResultPath = '/'.join(statusJsonFile.split('/')[:-1])
        envMgmtPath = f'/{timestampResultPath}/.Data/EnvMgmt'
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        # processIdLink: <a href="#" style="text-decoration:none" sessionId=hgee2 playbook=/opt/KeystackTests/Playbooks/pythonSample.yml module=CustomPythonScripts processId= statusJsonFile=/opt/KeystackTests/Results/PLAYBOOK=pythonSample/09-27-2022-08:04:59:982339_hgee2/STAGE=Test_MODULE=CustomPythonScripts_ENV=loadcoreSample/moduleSummary.json onclick="terminateProcessId(this)">Terminate</a>

        if statusJsonFile == 'None':
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Terminate', msgType='Failed', 
                                      msg=f'No overallSummaryData.json result file for test: sessionId:{sessionId} playbook:{playbook} module:{module}')
            return JsonResponse({'status': 'failed', 'errorMsg': 'No overallSummaryData.json file found'}, status=HtmlStatusCodes.error)
          
        try:
            from datetime import datetime
            
            # Terminate the running the process
            if os.environ['keystack_platform'] == 'linux':
                result, process = keystackUtilities.execSubprocessInShellMode(f'sudo kill -9 {processId}')
                
            if os.environ['keystack_platform'] == 'docker':
                result, process = keystackUtilities.execSubprocessInShellMode(f'kill -9 {processId}')
                
            # Verify the termination
            result, process = keystackUtilities.execSubprocessInShellMode(f'ps -ef | grep keystack | grep {module} | grep {sessionId}')

            # Update the test's overallSummary.json
            testStopTime = datetime.now()
            testStatusFile = keystackUtilities.readJson(statusJsonFile)
            testStatusFile['status'] = 'Terminated'
            testStatusFile['result'] = 'Incomplete'
            testStatusFile['stopped'] = testStopTime.strftime('%m-%d-%Y %H:%M:%S:%f')
            testStatusFile['currentlyRunning'] = ''

            # Don't remove the test session from the active user list.  
            # The user might have terminated the session for debugging. Just remove from the wait-list.
            if testStatusFile['holdEnvsIfFailed']:
                for envMgmtDataFile in glob(f'{envMgmtPath}/*.json'):
                    envMgmtData = keystackUtilities.readJson(envMgmtDataFile)
                    env = envMgmtData['env']
                    envSessionId = envMgmtData['sessionId']
                    envUser = envMgmtData['user']
                    envStage = envMgmtData['stage']
                    envModule = envMgmtData['module']
                    envMgmtObj = EnvMgmt.ManageEnv()
                    envList = []
                    
                    # {'user': 'hgee', 'sessionId': '11-07-2022-12:37:30:802368_2280_debugMode', 'stage': 'Test', 'module': 'CustomPythonScripts', 'env': 'qa-rack1'}
                    envMgmtObj.setenv = env
                    envMgmtObj.removeFromWaitList(envSessionId, user=envUser, stage=envStage, module=envModule)
                    envList.append(env)
            else:
                # Remove env from activeUserList
                for envMgmtDataFile in glob(f'{envMgmtPath}/*.json'):
                    envMgmtData = keystackUtilities.readJson(envMgmtDataFile)
                    env = envMgmtData['env']
                    envSessionId = envMgmtData['sessionId']
                    envUser = envMgmtData['user']
                    envStage = envMgmtData['stage']
                    envModule = envMgmtData['module']
                    envMgmtObj = EnvMgmt.ManageEnv()
                    envList = []
                    
                    # {'user': 'hgee', 'sessionId': '11-07-2022-12:37:30:802368_2280_debugMode', 'stage': 'Test', 'module': 'CustomPythonScripts', 'env': 'qa-rack1'}
                    envMgmtObj.setenv = env
                    envMgmtObj.removeFromActiveUsersList([{'user':envUser, 'sessionId':envSessionId, 'stage':envStage, 'module':envModule}])
                   
                    envMgmtData['envIsReleased'] = True
                    keystackUtilities.writeToJson(jsonFile=envMgmtDataFile, data=envMgmtData)

            # Update overallSummary status with Terminated    
            keystackUtilities.writeToJson(jsonFile=statusJsonFile, data=testStatusFile)

            # "waitList": [{"module": "LoadCore", "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
            #               "stage": "LoadCoreTest", "user": "rocky"}
            for waitingSession in envMgmtObj.getWaitList():
                # Remove sessionId in waitlist
                if waitingSession['sessionId'] == envSessionId:
                    envMgmtObj.removeFromWaitList(sessionId=envSessionId, user=waitingSession['user'], 
                                                    stage=waitingSession['stage'], module=waitingSession['module'])
                    
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Terminate', 
                                      msgType='Info', msg=f'sessionId:{sessionId} playbook:{playbook} module:{module}')
            
        except Exception as errMsg:
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Terminate', msgType='Error',
                                      msg=f'sessionId:{sessionId} playbook:{playbook} module:{module}',
                                      forDetailLogs=traceback.format_exc(None, errMsg))
            
            statusCode = HtmlStatusCodes.error
            status = 'failed'
            errorMsg = str(errMsg)

        return JsonResponse({'status':status, 'errorMsg':errorMsg}, status=statusCode)
        
       
class ArchiveResults(View):
    @authenticateLogin
    def post(self,request):
        """ 
        Archive results
        """
        body = json.loads(request.body.decode('UTF-8'))
        user = request.session['user']

        # /opt/KeystackTests/Results/PLAYBOOK=pythonSample/09-27-2022-08:17:44:760556_hgee2
        # resultsPathList: ['/opt/KeystackTests/Results/DOMAIN=QA/PLAYBOOK=pythonSample/10-14-2022-13:05:25:612106_hgee_debugMode']
        resultsPathList = body['results']
        playbookFolderName = None
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        activeResultsPath = f"{GlobalVars.keystackTestRootPath}/Results"
        archiveResultsPath = f"{GlobalVars.keystackTestRootPath}/ResultsArchive"
        
        if os.path.exists(archiveResultsPath) == False:
            keystackUtilities.makeFolder(targetPath=archiveResultsPath, permission=0o770, stdout=False)
            keystackUtilities.execSubprocessInShellMode(f'chown -R {GlobalVars.user}:{GlobalVars.userGroup} {archiveResultsPath}')
                                
        for resultsPath in resultsPathList:
            # ['/opt/KeystackTests/Results/DOMAIN=QA/PLAYBOOK=pythonSample/10-14-2022-13:05:25:612106_hgee_debugMode']
            try:
                match = search('.*/(GROUP=.+)/(PLAYBOOK=.+)/(.+)', resultsPath)
                if match:
                    group = match.group(1)
                    playbook = match.group(2)
                    timestampResults = match.group(3)
                    destination = f'{archiveResultsPath}/{group}/{playbook}/{timestampResults}'
                    
                    if os.path.exists(destination) == False:
                        keystackUtilities.mkdir2(destination)
                        
                    print(f'\nArchiveResults: resultsPath={resultsPath} -> dest={destination}\n')   
                    
                    copytree(resultsPath, destination, dirs_exist_ok=True)
                    # Remove the results from the active test results
                    rmtree(resultsPath)
                    removeEmptyTestResultFolders(user, resultsPath)
                    keystackUtilities.execSubprocessInShellMode(f'chown -R {GlobalVars.user}:{GlobalVars.userGroup} {destination}')

                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ArchiveResults', 
                                              msgType='Info', msg=f'results:{resultsPath}')
                
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ArchiveResults', msgType='Error',
                                        msg=f'results:{resultsPath}: {traceback.format_exc(None, errMsg)}')
                
        return JsonResponse({'status':status, 'error':errorMsg}, status=statusCode)


class ResumePausedOnError(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='Resume-PausedOnError')
    def post(self,request):
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        user = request.session['user']
        
        try:
            body = json.loads(request.body.decode('UTF-8'))
            pausedOnErrorFile = body['pausedOnErrorFile']
            os.remove(pausedOnErrorFile)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResumePausedOnError', msgType='Info',
                                      msg=pausedOnErrorFile, forDetailLogs='')
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            status = 'failed'
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResumePausedOnError', msgType='Error',
                                      msg=error, forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
            
        return JsonResponse({'error': error, 'status': status}, status=statusCode)


class ShowGroups(View):
    @authenticateLogin
    def get(self,request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        error = None
        groupsRadioButtons = ''
        
        try:
            testGroupsFile = GlobalVars.testGroupsFile
            if os.path.exists(testGroupsFile):
                groupsData = keystackUtilities.readYaml(testGroupsFile)
                
                for group in groupsData.keys():
                    groupsRadioButtons += '<div class="pl-2 form-check form-check-inline" style="inline:block; color:black">'
                    if group == "Default":
                        groupsRadioButtons += f'<input class="form-check-input" type="radio" checked="checked" id="{group}" name="group" value="{group}">'
                    else:
                        groupsRadioButtons += f'<input class="form-check-input" type="radio" id="{group}" name="group" value="{group}">'                    
                    groupsRadioButtons += f'<label for="{group}" class="form-check-label">{group}</label>'
                    groupsRadioButtons += '</div>'

        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetGroups', msgType='Error',
                                      msg=errMsg, forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
          
        return JsonResponse({'groups': groupsRadioButtons, 'error': error}, status=statusCode)


class GetSessionGroups(View):
    @authenticateLogin
    def post(self,request):
        """
        For Pipelines dropdown:
            <GROUPNAME>: <total>
        """
        statusCode = HtmlStatusCodes.success
        error = None
        user = request.session['user']
        
        try:
            sessionGroups = getDomainSessions(user)
            body = json.loads(request.body.decode('UTF-8'))
            controller = body['controller']
            html = ''

            for groupName in sessionGroups:
                totalPlaybookSessions = 0
                for playbook in glob(f'{GlobalVars.keystackTestRootPath}/Results/DOMAIN={groupName}/PLAYBOOK=*'):
                    for timestampResult in glob(f'{playbook}/*'):
                        if os.path.exists(f'{timestampResult}/overallSummary.json'):
                            totalPlaybookSessions += 1
                    
                html += f'<a class="collapse-item pl-3 textBlack" href="/sessionMgmt?group={groupName}"><i class="fa-regular fa-folder pr-3"></i>{groupName}: {totalPlaybookSessions}</a>'
                    					
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetSessionGroups', msgType='Error',
                                      msg=errMsg,
                                      forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
        
        return JsonResponse({'sessionGroups':html, 'error': error}, status=statusCode)
    

class GetPipelinesDropdown(View):
    @authenticateLogin
    def get(self,request):
        """ 
        Dropdown menu for user to select a pipeline to run
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        user = request.session['user']
        
        try:
            pipelines = '<ul class="dropdown-menu dropdownSizeSmall dropdownFontSize">'
                    
            for eachPipeline in getPipelines():
                pipeline = eachPipeline.replace(f'{GlobalVars.pipelineFolder}/', '').split('.')[0]
                pipelines += f'<li class="dropdown-item" pipeline="{eachPipeline}" onclick="playPipeline(this)">{pipeline}</li>'
              
            pipelines += '</ul>'
                        
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            status = 'failed'
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelines', msgType='Error',
                                      msg=errMsg,
                                      forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
        
        return JsonResponse({'pipelines': pipelines, 'status':status, 'error': error}, status=statusCode)

    
class GetPipelinesForJobScheduler(View):
    @authenticateLogin
    def get(self,request):
        """ 
        Dropdown menu for job scheduler
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        user = request.session['user']
        
        try:            
            pipelineForJobScheduler = f'<label for="pipelineForJobScheduler">Select a Pipeline:&emsp; </label>'
            pipelineForJobScheduler += '<select id="pipelineForJobScheduler">'
            pipelineForJobScheduler += f'<option value="None" selected="selected">None</option>'

            for eachPipeline in getPipelines():
                pipelineName = eachPipeline.split('/')[-1].split('.')[0]
                pipelineForJobScheduler += f'<option value="{eachPipeline}">{pipelineName}</option>'
                
            pipelineForJobScheduler += f'</select> &emsp;&emsp;'
                                
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            status = 'failed'
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelinesForSchedluer', msgType='Error',
                                      msg=errMsg,
                                      forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
        
        return JsonResponse({'pipelines': pipelineForJobScheduler, 'status':status, 'error': error}, status=statusCode)
    
        
class SavePipeline(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='SavePipeline', exclude='engineer')
    def post(self,request):
        """ 
        Create a new pipeline
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        user = request.session['user']
        
        try:
            body = json.loads(request.body.decode('UTF-8'))
            pipelineFilename = f'{GlobalVars.pipelineFolder}/{body["pipelineName"]}.yml'
            pipelineName = body.get('pipelineName', None)
            playbook     = body.get('playbook', None)
            
            if playbook == '':
                statusCode = HtmlStatusCodes.error
                status = 'failed'
                error = 'You must select a playbook'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Failed',
                                          msg=error, forDetailLogs='')
                return JsonResponse({'status':status, 'error': error}, status=statusCode)
            
            for eachPipelineName in getPipelines():
                if bool(match(pipelineName, eachPipelineName)):
                    status = 'failed'
                    statusCode = HtmlStatusCodes.error
                    error = f'Pipeline name already exists: {pipelineName}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Error',
                                              msg=error, forDetailLogs='')
            
            if error is None:                    
                if os.path.exists(GlobalVars.pipelineFolder) == False:
                    keystackUtilities.mkdir2(GlobalVars.pipelineFolder, stdout=False)
                
                keystackUtilities.writeToYamlFile(body, pipelineFilename, mode='w')
                keystackUtilities.chownChmodFolder(GlobalVars.pipelineFolder,
                                                   user=GlobalVars.user, userGroup=GlobalVars.userGroup, permission=770)
            
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Info',
                                          msg=f'{body}', forDetailLogs='')
                        
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            status = 'failed'
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SavePipeline', msgType='Error',
                                      msg=errMsg, forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
        
        return JsonResponse({'status':status, 'error': error}, status=statusCode)


class GetPipelineTableData(View):
    @authenticateLogin
    def get(self, request):
        """ 
        Get detailed Pipeline data table 
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        user = request.session['user']
        
        #html = '<table class="table table-sm table-bordered table-fixed tableFixHead">'
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
                pipelineParams = keystackUtilities.readYaml(eachPipeline)
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
            error = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelineTableData', msgType='Error',
                                      msg=error, forDetailLogs='')
                        
        html += '</table>'
                          
        return JsonResponse({'pipelineTableData':html, 'status':status, 'error': error}, status=statusCode)
       

class DeletePipelines(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='DeletePipelines', exclude='engineer')
    def post(self, request):
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        user = request.session['user']
        body = json.loads(request.body.decode('UTF-8'))
        pipelines = body['pipelines']
        
        try:
            for eachPipeline in pipelines:
                os.remove(eachPipeline)
                pipelineName = eachPipeline.split('/')[-1].split('.')[0]
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipeline', msgType='Info',
                                          msg=f'Pipeline name: {pipelineName}', forDetailLogs='')
                
        except Exception as errMsg:
            status = 'failed'
            statusCoe = HtmlStatusCodes.error
            error = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePipeline', msgType='Error',
                                      msg=pipelineName, forDetailLogs=error)
       
        return JsonResponse({'status':status, 'error': error}, status=statusCode)                          
 
    
class GetServerTime(View):
    @authenticateLogin
    def get(self, request):
        """ 
                timedatectl:
                
                    Local time: Tue 2023-03-21 13:44:35 PDT
                Universal time: Tue 2023-03-21 20:44:35 UTC
                        RTC time: Tue 2023-03-21 20:44:35
                        Time zone: America/Los_Angeles (PDT, -0700)
        System clock synchronized: yes
                    NTP service: active
                RTC in local TZ: no

        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        serverTime = ''

        try:
            # Use zdump /etc/localtime to get the local time. This will work for both
            # Linux mode and docker mode.  Docker will use UTC. Linux mode will use the local host time. 
            
            # (True, '/etc/localtime  Fri Mar 24 12:01:21 2023 PDT')
            localHostTime = keystackUtilities.execSubprocessInShellMode('zdump /etc/localtime', showStdout=False)[1]
            match = search('/etc/localtime +([a-zA-Z]+) +([a-zA-Z]+) +([0-9]+) +([0-9]+:[0-9]+:.*) +([^ ]+) (.*)', localHostTime)
            serverTime = f'{match.group(1)} {match.group(2)} {match.group(3)} {match.group(5)} {match.group(4)} {match.group(6)}'
            
            # UTC: serverTime: (True, 'Thu Mar 16 01:39:55 UTC 2023')
            # serverTimeLinux = keystackUtilities.execSubprocessInShellMode('date', showStdout=True)[1]
            # match = search('([a-zA-Z]+) +([a-zA-Z]+) +([0-9]+) +([0-9]+:[0-9]+:.*) +([^ ]+) (.*)', serverTimeLinux)
            # serverTime = f'{match.group(1)} {match.group(2)} {match.group(3)} {match.group(6)} {match.group(4)} {match.group(5)}'
            
            # timedatectl: (This doesn't work in docker ubuntu)
            # Local time: Tue 2023-03-21 13:47:04 PDT
            #serverTimeLinux = keystackUtilities.execSubprocessInShellMode('timedatectl', showStdout=False)[1]
            #regexp = search('.*Local time:\s+([a-zA-Z]+.*)\n', serverTimeLinux)
            #serverTime = regexp.group(1)
            
        except Exception as errMsg:
            error = str(errMsg)
            status = 'failed'
            statusCoe = HtmlStatusCodes.error 
            
        return JsonResponse({'status':status, 'error': error, 'serverTime': serverTime}, status=statusCode)
'''    
            
