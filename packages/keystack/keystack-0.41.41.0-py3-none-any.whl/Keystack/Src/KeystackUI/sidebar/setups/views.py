import os, sys
from re import search
from django.shortcuts import render
from django.views import View

from baseLibs import getSetups
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from domainMgr import DomainMgr
from accountMgr import AccountMgr
from globalVars import HtmlStatusCodes, GlobalVars


class Setups(View):
    @authenticateLogin
    def get(self, request):
        user = request.session['user']
        module = request.GET.get('module')
        status = HtmlStatusCodes.success        
        # envGroupPath: Envs/DOMAIN=Communal/Samples
        envGroupPath = request.GET.get('group')

        # topbarDisplay: DOMAIN=Communal/KeystackQA/nestedDir
        topbarDisplay = request.GET.get('group').replace('Envs/', '')
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        topbarDisplayDomain = None
        topbarDisplayGroup = None
        
        # group: Playbooks/DOMAIN=Communal/Samples
        regexMatch = search('.*Envs/DOMAIN=(.+?)/(.*)', envGroupPath)
        if regexMatch:
            domain = f'DOMAIN={regexMatch.group(1)}'
            envGroup = f'Group={regexMatch.group(2)}'
        else:
            regexMatch = search('.*Envs/DOMAIN=(.+)', envGroupPath)
            if regexMatch:
                domain = f'DOMAIN={regexMatch.group(1)}'
                #envGroup = f'Resource-Group=None'
                envGroup = f'Group=None'
    
        topbarDisplayDomain = domain
        topbarDisplayGroup = envGroup
        domainName = domain.split('=')[1]
        
        if domainName:
            # AccountMgmt.verifyLogin.getUserRole() uses this
            request.session['domain'] = domainName
            domainUserRole = DomainMgr().getUserRoleForDomain(user, domainName) 
        else:
            domainUserRole = None
        
        return render(request, 'envs.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'domain': domainName,
                       'envGroupPath': envGroupPath,
                       'topbarDisplayDomain': topbarDisplayDomain,
                       'topbarDisplayGroup': topbarDisplayGroup,
                       'topbarTitlePage': f'Env Mgmt',
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                      }, status=status)
 

class EnvLoadBalancer(View):
    """ 
    Load balance group main page
    """
    @authenticateLogin
    def get(self, request):
        user = request.session['user']
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        status = HtmlStatusCodes.success

        # SessionMgmt view is the default login page.
        # domain will be None
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
            domainUserRole = DomainMgr().getUserRoleForDomain(user, domain) 
        else:
            domainUserRole = None
            
        return render(request, 'envLoadBalancerMgmt.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': f'Env Load Balance Group Mgmt',
                       'domain': domain,
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                      }, status=status)
        
        
'''         
class Vars:
    webpage = 'envs'
    envMgmtDB = 'envMgmt'
    envLoadBalanceDB = 'envLoadBalanceGroups'
    keystackIpPort = os.environ.get('keystack_keystackIpPort', GlobalVars.keystackIpPort)
    # http://0.0.0.0
    keystackHttpUrl = os.environ.get('keystack_httpIpAddress', GlobalVars.keystackHttpUrl)
    # http://0.0.0.0:8000
    keystackHttpBase = f'{keystackHttpUrl}:{keystackIpPort}'
    keystackUIIpAddress = keystackHttpUrl.split('//')[-1]

   
def getTableData(envGroup, user) -> str:
    """ 
    Get setup yml files from /$keystackTestRootPath/Setup folder.
    
    Setup groups are subfolder names
    """
    tableData: str = ''
    envPath = GlobalVars.envPath
    envMgmtPath = GlobalVars.envMgmtPath
    
    for rootPath,dirs,files in os.walk(envPath): 
        #  root=/opt/KeystackTests/Envs files=['pythonSample.yml', 'loadcoreSample.yml']          
        if bool(search(f'^{GlobalVars.keystackTestRootPath}/{envGroup}$', rootPath)) and files:
            # Just file names. Not path included.
            for envYmlFile in files:
                if envYmlFile.endswith('.yml'):
                    envYmlFileFullPath = f'{rootPath}/{envYmlFile}'
                    
                    try:
                        envData = readYaml(envYmlFileFullPath)
                    except Exception as errMsg:
                        # TODO: If there is an invisible tab in the yml file, no env will be shown
                        #       Must show the error to the user
                        print(f'setup: getTableData error: Problem found in yml file. Most likely tabs were used instead of spaces: {envYmlFileFullPath}: {errMsg}')
                        continue 

                    if envData is None:
                        continue
                    
                    if type(envData) != dict:
                        print(f'setup getTableData error: Yaml file contents is string type. Expecting dict type. Check the yaml file: {envYmlFileFullPath}')
                        continue
            
                    isParallelUsage = envData.get('parallelUsage', False) # Default to No if not exists
                    if isParallelUsage:
                        isParallelUsage = 'Yes'
                    if isParallelUsage == False:
                        isParallelUsage = 'No'
                
                    # Samples/loadcoreSample 
                    regexMatch = search(f'{GlobalVars.keystackTestRootPath}/Envs/(.+)\.y.+', envYmlFileFullPath)
                    if regexMatch:
                        envName = regexMatch.group(1)

                    envMgmtObj = ManageEnv(envName)
                    if envMgmtObj.isEnvExists() == False:
                        envMgmtObj.addEnv()

                    isAvailable = envMgmtObj.isEnvAvailable()
                    if isAvailable: isAvailable = 'Yes'
                    if isAvailable == False: isAvailable = 'No'
                    totalWaiting = len(envMgmtObj.getWaitList())
                    activeUsers = envMgmtObj.getActiveUsers()
                    totalActiveUsers = len(activeUsers)
                    
                    loadBalanceGroups = envMgmtObj.getLoadBalanceGroups()
                    if loadBalanceGroups:
                        lbgDropdown = '<div class="dropdown">'
                        lbgDropdown += '<a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>View</a>'
                        lbgDropdown += '  <ul class="dropdown-menu dropdownSizeSmall">'
                        for lbg in loadBalanceGroups:
                            lbgDropdown += f'<li class="dropdown-item">{lbg}</li>'
                        lbgDropdown += '</ul></div>' 
                    else:
                        lbgDropdown = 'None'
                        
                    tableData += '<tr>'
                    tableData += f'<td><input type="checkbox" name="envCheckboxes" value="{envYmlFileFullPath}"/></td>'
                    tableData += f'<td><button class="btn btn-sm btn-outline-primary" value="{envYmlFileFullPath}" onclick="getFileContents(this)" data-bs-toggle="modal" data-bs-target="#viewEditEnvModal">View / Edit</button></td>'
                    
                    tableData += f'<td style="text-align:left">{envName}</td>'
                    tableData += f'<td style="text-align:center">{lbgDropdown}</td>'
                    tableData += f'<td style="text-align:center">{isParallelUsage}</td>'
                    tableData += f'<td style="text-align:center">{isAvailable}</td>'

                    # data-toggle="modal" data-target="#modalId"
                    tableData += f'<td style="text-align:center"><a href="#" onclick="activeUsersList(this)" env={envName} data-bs-toggle="modal" data-bs-target="#activeUsersModal">ActiveUsers:{totalActiveUsers}&emsp;&ensp;Waiting:{totalWaiting}</a></td>'
                    
                    # The reserve button has no stage and module
                    tableData += f'<td><button onclick="reserveEnv(this)" env={envName} class="btn btn-sm btn-outline-primary">Reserve</button></td>'
                      
                    if isParallelUsage == 'No' and totalActiveUsers > 0: 
                        tableData += f'<td style="text-align:center"><button class="btn btn-sm btn-outline-primary" env={envName} onclick="releaseEnv(this)" >Release</button></td>'
                    else:
                        tableData += '<td></td>'
                        
                    tableData += f'<td><button onclick="resetEnv(this)" env={envName} class="btn btn-sm btn-outline-primary">Reset</button></td>'
                                                
                    tableData += '</tr>'
      
    return tableData


class GetSetupTableData(View):
    @authenticateLogin
    def post(self, request):
        """ 
        Get all env updates for an env group
        """
        tableData = "" 
        status = 'success' 
        statusCode = HtmlStatusCodes.success 
        errorMsg = None     
        body = json.loads(request.body.decode('UTF-8'))
        user = request.session['user']
        # Example: Envs | Envs/Samples
        envGroupToView = body['envGroup']
        
        # Self cleanup on activeUsers
        # Users might have included -holdEnvsIfFailed and deleted the pipeline or test result
        # The env still has the active user. We need to automatically release the active-user from the env.
        #    1> Get all envs for the envGroupToView
        #    2> Get active users for all envs in this env group
        #    3> Check if test results exists.  If not, the user deleted the pipeline test results before
        #       releasing the env.

        envMgmtObj = ManageEnv(envGroupToView)                
        envGroupPath = f'{GlobalVars.keystackTestRootPath}/{envGroupToView}'

        for env in glob(f'{envGroupPath}/*'):
            if bool(search('.+\.(yml|ymal)$', env)) == False:
                continue 

            envGroup = ''
            envName = env.split('/')[-1].split('.')[0]
            regexMatch = search('^Envs/(.+)', envGroupToView)
            if regexMatch:
                 envGroup = regexMatch.group(1)

            envMgmtObj.setenv = f'{envGroup}/{envName}'
            activeUsers = envMgmtObj.getActiveUsers()
            if activeUsers:
                # Get test result path and check for path exists

                # [{'sessionId': '05-17-2023-15:49:07:297406_5432', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=Samples-pythonSample/05-17-2023-15:49:07:297406_5432/overallSummary.json', 'user': 'hgee', 'stage': 'Test', 'module': 'CustomPythonScripts2'}]
                for activeUser in activeUsers:
                    overallSummaryFile = activeUser['overallSummaryFile']
                    if overallSummaryFile:
                        testResultPath = overallSummaryFile.split('/overallSummary.json')[0]
                        if os.path.exists(testResultPath) == False:
                            # Release the env from activeUsers
                            session = {'sessionId':activeUser['sessionId'], 'stage':activeUser['stage'],
                                       'module':activeUser['module'], 'user':activeUser['user']} 
                            envMgmtObj.removeFromActiveUsersList([session])
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AutoRemoveActiveUser', 
                                                    msgType='Info', msg=f'The env {envGroup}/{envName} has active user, but the pipeline and test results are deleted. Releasing active user on this env.',
                                                    forDetailLogs='')
        
        try:
            tableData = getTableData(envGroupToView, user)

        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvTableData', 
                                      msgType='Error', msg=errMsg,
                                      forDetailLogs=traceback.format_exc(None, errMsg))
                        
        return JsonResponse({'tableData': tableData, 'status': status, 'errorMsg': errorMsg}, status=statusCode)    
'''
                        

# Leaving this code here for reference
'''
class EnvGroups(View):
    """
    Get Env groups for sidebar Env dropdown menu
    """
    @authenticateLogin
    def get(self, request):
        """
        Get Env groups for sidebar Env menu
        """
        user = request.session['user']
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        htmlEnvGroups = ''
            
        try:
            # Env groups
            envPath = f'{GlobalVars.keystackTestRootPath}/Envs'
            envGroups = []
            for root,dirs,files in os.walk(envPath):
                envGroup = root.split(GlobalVars.keystackTestRootPath)[1]
                envGroups.append(envGroup[1:])

            htmlEnvGroups += '<a href="/setups/envLoadBalancer" class="collapse-item pl-0 pt-3 pb-3 textBlack fontSize12px">Load Balance Group Mgmt</a>'

            htmlEnvGroups += '<p class="pl-2 pt-2 textBlack fontSize12px">Select Env Group:</p><br>'
            for group in envGroups:
                htmlEnvGroups += f'<a class="collapse-item pl-3 fontSize12px" href="/setups?group={group}"><i class="fa-regular fa-folder pr-3"></i>{group}</a>'
                   
        except Exception as errMsg:
            errorMsg = str(errMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvGroups', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            
            
        return JsonResponse({'envGroups':htmlEnvGroups, 'status':status, 'error':errorMsg}, status=statusCode)   


class EnvGroupsTableForDelete(View):
    """
    Get Env groups for delete env group table selection
    """
    @authenticateLogin
    def get(self, request):
        """
        Create a table for selecting Env groups to delete
        """
        user = request.session['user']
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        html = ''
            
        try:
            # Env groups
            execRestApiObj = ExecRestApi(ip=Vars.keystackUIIpAddress, port=Vars.keystackIpPort, https=False)
            response = execRestApiObj.get(restApi='/api/v1/env/groups', params={'webhook':True}, silentMode=False) 

            if response.status_code == 200:
                html +=   '<center><table class="tableFixHead2 table-bordered" style="width:90%">'    
                html +=        '<thead>'
                html +=            '<tr>'
                html +=                 '<th><input type="checkbox" name="deleteAllEnvGroups" onclick="disableEnvGroupCheckboxes(this)" \></th>'
                html +=                 '<th>EnvGroup</th>'
                html +=            '</tr>'
                html +=         '</thead>'
                html +=         '<tbody>'
                
                for envGroup in response.json()['envGroups']:
                    envGroupName = envGroup.split('/Envs/')[-1]
                    html += '<tr>'
                    html += f'<td><input type="checkbox" name="deleteEnvGroups" value="{GlobalVars.keystackTestRootPath}/{envGroup}"></td>'
                    html += f'<td class="textAlignLeft">{envGroupName}</td>'
                    html += '</tr>'
                    
                html +=  '</tbody>'    
                html +=  '</table></center>'
            else:
                raise Exception(response.json()['errorMsg'])
            
        except Exception as errMsg:
            errorMsg = str(errMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvGroups', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            
            
        return JsonResponse({'envGroupsHtml':html, 'status':status, 'error':errorMsg}, status=statusCode)   
            
            
class ViewEditEnv(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='view/edit')
    def post(self, request):
        """
        Show the env yml file contents and allow editing
        """
        body = json.loads(request.body.decode('UTF-8'))
        envFile = body['envFile']
        user = request.session['user']
        envContents = dict()        
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if os.path.exists(envFile) == False:
            errorMsg = f'Env yml file not found: {envFile}'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ViewEditEnv', msgType='Error',
                                      msg=errorMsg, forDetailLogs='')  
            statusCode = HtmlStatusCodes.error
            status = 'failed'
        else:    
            envContents = readYaml(envFile)
            
        return JsonResponse({'envContents': envContents, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
  
   
class CreateEnv(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='Create', exclude='engineer')
    def post(self, request):
        """
        Create a new Env file
        """
        body = json.loads(request.body.decode('UTF-8'))
        envNamespace = body['newEnv']
        envGroup = body['envGroup']
        textArea = body['textArea']
        user = request.session['user']  
        envPath = GlobalVars.envPath
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if '-' in envNamespace:
            env = envNamespace.replace('-', '/')
        else:
            env = envNamespace
        
        try:
            if '.yml' not in env:
                env = f'{env}.yml'
            
            if envGroup:
                if envGroup[0] == '/':
                    envGroup = f'/{envGroup[1:]}'

                envFullPath = f'{envPath}/{envGroup}'
                mkdir2(envFullPath)
                fullPathFile = f'{envFullPath}/{env}' 
                chownChmodFolder(envFullPath, GlobalVars.user, GlobalVars.userGroup)
                chownChmodFolder(fullPathFile, GlobalVars.user, GlobalVars.userGroup)
                           
            else:
                envGroup = None
                playbookGroup = None
                fullPathFile = f'{envPath}/{env}'

            if os.path.exists(fullPathFile):
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                errorMsg = f'Env already exists: Group:{envGroup} Env:{env}'
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', 
                                            msgType='Failed', msg=errorMsg, forDetailLogs='')
                return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
            writeToFile(fullPathFile, textArea, mode='w')
                        
            try:
                # Verify for yaml syntax error
                readYaml(fullPathFile)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', 
                                          msgType='Info',
                                          msg=f'Env:{env} Group:{envGroup}', forDetailLogs='') 
                            
            except Exception as errMsg:
                errorMsg = "Error: Yml syntax error."
                status = "failed"
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', 
                                          msgType='Error',
                                          msg=errorMsg, forDetailLogs='') 

        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            status = "failed"
            errorMsg = str(errMsg)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', msgType='Error',
                                      msg=errMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)


class GetWaitList(View):
    @authenticateLogin
    def post(self, request):
        """ 
        "waitList": [{"module": "LoadCore",
                      "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                      "user": "rocky"
                     },
                     {"module": "LoadCore",
                      "sessionId": "11-01-2022-04:23:05:749724_rocky_1test",
                      "user": "rocky"}]
        """
        body = json.loads(request.body.decode('UTF-8'))
        envNamespace = body['env']
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        user = request.session['user']
        
        if '-' in envNamespace:
            env = envNamespace.replace('-', '/')
        else:
            env = envNamespace

        try:
            envMgmtObj = ManageEnv(env)

            # waitList: [{'module': 'LoadCore', 'sessionId': '11-01-2022-04:21:00:339301_rocky_200Loops', 'user': 'rocky'}, {'module': 'LoadCore', 'sessionId': '11-01-2022-04:23:05:749724_rocky_1test', 'user': 'rocky'}]
            waitList = envMgmtObj.getWaitList()

            html = '<table id="envWaitListTable" class="mt-2 table table-sm table-bordered table-fixed tableFixHead tableMessages">' 
            html += '<thead>'
            html += '<tr>'
            html += '<th scope="col">Remove</th>'
            html += '<th scope="col" style="text-align:left">User</th>'
            html += '<th scope="col" style="text-align:left">SessionId</th>'
            html += '<th scope="col" style="text-align:left">Stage</th>'
            html += '<th scope="col" style="text-align:left">Task / Module</th>'
            html += '</tr>'
            html += '</thead>'
            html += '<tbody>'
            
            for eachWait in waitList:
                user =      eachWait['user']
                sessionId = eachWait['sessionId']
                stage =     eachWait['stage']
                module =    eachWait['module']
            
                html += '<tr>'
                html += f'<td><input type="checkbox" name="envWaitListCheckboxes" env="{env}" user="{user}" sessionId="{sessionId}" stage="{stage}" module="{module}"/></td>'
                html += f'<td style="text-align:left">{user}</td>'
                html += f'<td style="text-align:left">{sessionId}</td>'
                html += f'<td style="text-align:left">{stage}</td>'
                html += f'<td style="text-align:left">{module}</td>'
                html += f'</tr>'
                
            html += '</tbody>'       
            html += '</table>'
            
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvWaitList',
                                      msgType='Error', msg=errorMsg,
                                      forDetailLogs=f'GetEnvWaitList: {traceback.format_exc(None, errMsg)}') 
            
        return JsonResponse({'tableData': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
          

class RemoveFromWaitList(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='view/edit')
    def post(self, request):
        """ 
        "waitList": [{"module": "LoadCore",
                      "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                      "stage": "LoadCoreTest",
                      "user": "rocky"
                     },
                     {"module": "LoadCore",
                      "sessionId": "11-01-2022-04:23:05:749724_rocky_1test",
                      "stage": "Test",
                      "user": "bullwinkle"}]
        """
        body = json.loads(request.body.decode('UTF-8'))
        removeList = body['removeList']
        envNamespace = body['env']
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        user = request.session['user']
        
        if '-' in envNamespace:
            env = envNamespace.replace('-', '/')
        else:
            env = envNamespace

        try:            
            envMgmtObj = ManageEnv(env)
 
            for waiting in removeList:
                # {'env': 'loadcoreSample', 'sessionId': '11-06-2022-07:11:12:859325', 'stage': None, 'module': None}
                envMgmtObj.removeFromWaitList(sessionId=waiting['sessionId'], user=waiting['user'], 
                                              stage=waiting['stage'], module=waiting['module'])
                                                                                   
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveEnvFromWaitList', msgType='Info',
                                      msg=f'SessionId:{waiting["sessionId"]} User:{waiting["user"]} Stage:{waiting["stage"]}  Module:{waiting["module"]}', forDetailLogs=f'')
                
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveEnvFromWaitList', msgType='Error',
                                      msg=errorMsg, forDetailLogs=f'RemoveFromWaitList: {traceback.format_exc(None, errMsg)}')
            
        return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
        

class GetActiveUsersList(View):
    @authenticateLogin
    def post(self, request):
        """ 
        "waitList": [{"module": "LoadCore",
                      "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                      "user": "rocky"
                     },
                     {"module": "LoadCore",
                      "sessionId": "11-01-2022-04:23:05:749724_rocky_1test",
                      "user": "rocky"}]
        """
        body = json.loads(request.body.decode('UTF-8'))
        envNamespace = body['env']
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        user = request.session['user']
        
        if '-' in envNamespace:
            env = envNamespace.replace('-', '/')
        else:
            env = envNamespace
            
        try:
            envMgmtObj = ManageEnv(env)
            envMgmtObj.setenv = env
                          
            html = '<table id="envActiveUsersTable" class="mt-2 table table-sm table-bordered table-fixed tableFixHead tableMessages">' 
            html += '<thead>'
            html += '<tr>'
            html += '<th scope="col" style="text-align:left">Release</th>'
            html += '<th scope="col" style="text-align:left">User</th>'
            html += '<th scope="col" style="text-align:left">SessionId</th>'
            html += '<th scope="col" style="text-align:left">Stage</th>'
            html += '<th scope="col" style="text-align:left">Task / Module</th>'
            html += '</tr>'
            html += '</thead>'
            html += '<tbody>'
                        
            # "inUsedBy": {'available': False, 'activeUsers': {'sessionId': '11-04-2022-10:26:25:988063', 'user': 'Hubert Gee', 'stage': None, 'module': None}, 'waitList': [{'sessionId': '11-05-2022-09:37:23:403861', 'user': 'Hubert Gee', 'stage': None, 'module': None}, {'sessionId': '11-05-2022-10:13:25:068764', 'user': 'Hubert Gee', 'stage': None, 'module': None}, {'sessionId': '11-05-2022-10:25:48:431241', 'user': 'Hubert Gee', 'stage': None, 'module': None}], 'isAvailable': False}

            for inUsedBy in envMgmtObj.getActiveUsers():
                user = inUsedBy.get('user')
                sessionId = inUsedBy.get('sessionId')
                overallSummaryFile= inUsedBy.get('overallSummaryFile')
                stage = inUsedBy.get('stage', None)
                module = inUsedBy.get('module', None)
  
                html += '<tr>'
                html += f'<td><input type="checkbox" name="envActiveUsersCheckboxes" env="{env}" sessionId="{sessionId}" overallSummaryFile="{overallSummaryFile}" stage="{stage}" module="{module}" /></td>'
                html += f'<td style="text-align:left">{user}</td>'
                html += f'<td style="text-align:left">{sessionId}</td>'
                html += f'<td style="text-align:left">{stage}</td>'
                html += f'<td style="text-align:left">{module}</td>'
                html += f'</tr>'

            html += '</tbody>'
            html += '</table>' 
                        
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvActiveUsers', msgType='Error',
                                      msg=errorMsg, forDetailLogs=f'GetEnvActiveUsers: {traceback.format_exc(None, errMsg)}')
            
        return JsonResponse({'tableData': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
 

class RemoveFromActiveUsersList(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='removeEnvFromActiveUsers')
    def post(self, request):
        """ 
        Remove users or sessionId from using the env
        """
        body = json.loads(request.body.decode('UTF-8'))
        removeList = body['removeList']
        envNamespace = body['env']
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        user = request.session['user']
        
        if '-' in envNamespace:
            env = envNamespace.replace('-', '/')
        else:
            env = envNamespace

        try:
            envMgmtObj = ManageEnv(env)
            excludeRemovingActiveUsers = []

            if '/' in env:
                env = env.replace('/', '-')

            # Check if the env session is currently runing. Can't just release the env when it's testing.
            # But allow to release the env if it's manually reserved   
            # removeList: 
            #     [{'env': 'pythonSample', 'sessionId': '04-25-2023-18:13:51:640030', 'overallSummaryFile': 'None', 'stage': 'None', 'module': 'None'}]        
            for index,activeUser in enumerate(removeList): 
                # overallSummaryFile exists only if it is a test. It doesn't exists for 
                # manual users reserving the env. 
                overallSummaryFile = activeUser['overallSummaryFile']                      
                if activeUser['overallSummaryFile']:
                    if os.path.exists(overallSummaryFile):
                        overallSummaryData = readJson(overallSummaryFile)
                        resultPath = '/'.join(overallSummaryFile.split('/')[:-1])
                        envMgmtFile = f'/{resultPath}/.Data/EnvMgmt/STAGE={activeUser["stage"]}_MODULE={activeUser["module"]}_ENV={env}.json'
                        
                        if overallSummaryData['status'] == 'Running':
                            excludeRemovingActiveUsers.append(index)
                            status = 'failed'
                            errorMsg = f'Cannot remove an active session from a actively running session: {activeUser["sessionId"]}'
                            statusCode = HtmlStatusCodes.error
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveActiveUserFromEnv', 
                                                        msgType='Failed', msg=errorMsg, forDetailLogs='')
                            JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                            
                        elif overallSummaryData['holdEnvsIfFailed']:
                            envMgmtData = readJson(envMgmtFile)
                            if envMgmtData['result'] == 'Failed' and envMgmtData['envIsReleased'] == False:
                                excludeRemovingActiveUsers.append(index)
                                status = 'failed'
                                errorMsg = f'The Env:{env} is on hold for test failure debugging. It must be released in the pipeline page on sessionId: {activeUser["sessionId"]}'
                                statusCode = HtmlStatusCodes.error
                                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveActiveUserFromEnv', msgType='Failed', msg=errorMsg, forDetailLogs='')
                                JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                                
            if len(excludeRemovingActiveUsers) > 0:
                for index in excludeRemovingActiveUsers:
                    removeList.pop(index)
                        
            envMgmtObj.removeFromActiveUsersList(removeList)
            
            for env in removeList:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUsersFromEnvActiveList', 
                                          msgType='Info',
                                          msg=f'SessionId:{env["sessionId"]} stage:{env["stage"]} module:{env["module"]}', forDetailLogs='')
                
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveActiveUsersFromEnv', msgType='Error',
                                      msg=errorMsg, forDetailLogs=f'RemoveUsersFromEnvActiveList: {traceback.format_exc(None, errMsg)}')
            
        return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
        

class ReserveEnv(View):
    @authenticateLogin
    @verifyUserRole(webPage=Vars.webpage, action='reserve')
    def post(self, request):
        """ 
        Go on the env wait-list.
        The reserve button has no stage and module
        """
        body = json.loads(request.body.decode('UTF-8'))
        envNamespace = body['env']
        sessionId = getTimestamp()
        user = request.session['user']
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None

        if '-' in envNamespace:
            env = envNamespace.replace('-', '/')
        else:
            env = envNamespace

        try:
            envMgmtObj = ManageEnv(env)
            if envMgmtObj.isUserInActiveUsersList(user):
                status = 'failed'
                errorMsg = f'The user is already actively using the env: {user}'
                statusCode = HtmlStatusCodes.notAllowed
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Failed',
                                          msg=errorMsg, forDetailLogs='')
                return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
            if envMgmtObj.isUserInWaitList(user):
                status = 'failed'
                errorMsg = f'the user is already in the wait list: {user}'
                statusCode = HtmlStatusCodes.notAllowed
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Failed',
                                          msg=errorMsg, forDetailLogs='')
                return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                            
            result = envMgmtObj.reserveEnv(sessionId=sessionId, user=user)
            if result[0] == 'success':
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Info',
                                          msg=result[1], forDetailLogs='')
                                
            else:
                status = 'failed'
                errorMsg = result[1]
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Failed',
                                          msg=errorMsg, forDetailLogs='')
                                      
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.notAllowed
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Error',
                                      msg=errorMsg, forDetailLogs=f'ReserveEnv: {traceback.format_exc(None, errMsg)}')
            
        return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ReleaseEnv(View):
    @authenticateLogin
    def post(self, request):
        """ 
        Release button to release the current occupying session/user from the env in InUsedBy.
        """
        body = json.loads(request.body.decode('UTF-8'))
        env = body['env']
        if '/' in env:
            envNamespace = env.replace('/', '-')
        else:
            envNamespace = env
                
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        user = request.session['user']
        
        try:
            envMgmtObj = ManageEnv()
            # [{'sessionId': '11-08-2022-15:10:36:026486_1231', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample/11-08-2022-15:10:36:026486_1231/overallSummary.json', 'user': 'hgee', 'stage': 'Test', 'module': 'CustomPythonScripts'}]
            envMgmtObj.setenv = env
            details = envMgmtObj.getEnvDetails()
            
            if len(details['activeUsers']) > 0:
                # topActiveUser: {'sessionId': '11-16-2022-14:05:18:399384_hubogee', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample/11-16-2022-14:05:18:399384_hubogee/overallSummary.json', 'user': 'hgee', 'stage': 'DynamicVariableSample', 'module': 'CustomPythonScripts'}
                
                topActiveUser = details['activeUsers'][0]
                # Check if the env session is currently runing. Can't just release the env when it's testing.
                # But allow to release the env if it's manually reserved 
                # If overallSummaryFile exists, this means the session is an automated test. Not manual user.           
                if topActiveUser['overallSummaryFile']:
                    overallSummaryFile = topActiveUser['overallSummaryFile']
                    if os.path.exists(overallSummaryFile):
                        overallSummaryData = readJson(overallSummaryFile)
                        resultPath = '/'.join(overallSummaryFile.split('/')[:-1])
                        envMgmtFile = f'/{resultPath}/.Data/EnvMgmt/STAGE={topActiveUser["stage"]}_MODULE={topActiveUser["module"]}_ENV={envNamespace}.json'
                        
                        if overallSummaryData['status'] == 'Running':
                            status = 'failed'
                            errorMsg = f'The Env:{env} is still being used by a running session: {topActiveUser["sessionId"]}'
                            statusCode = HtmlStatusCodes.error
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', msgType='Error',
                                                    msg=errorMsg, forDetailLogs='')
                            return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                        else:
                            # Completed or Aborted
                            if overallSummaryData['holdEnvsIfFailed']:
                                envMgmtData = readJson(envMgmtFile)
                                if envMgmtData['result'] == 'Failed' and envMgmtData['envIsReleased'] == False:
                                    status = 'failed'
                                    errorMsg = f'The Env:{env} is on hold for test failure debugging. It must be released in the pipeline page on sessionId: {topActiveUser["sessionId"]}'
                                    statusCode = HtmlStatusCodes.error
                                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', msgType='Error', msg=errorMsg, forDetailLogs='')
                                    return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                        
                envMgmtObj.releaseEnv()
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', msgType='Info',
                                        msg=f'Env:{env}', forDetailLogs='') 

        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', msgType='Error',
                                      msg=errorMsg, forDetailLogs=f'ReleaseEnv: {traceback.format_exc(None, errMsg)}')
            
        return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)

   
class ReleaseEnvOnFailure(View):
    """ 
    sessionMgmt release-env button for each stage/module/env failure.
    If test failed, envs are on hold for debugging. A Release Envs button is created and blinking.
    """
    @authenticateLogin
    def post(self,request):
        body = json.loads(request.body.decode('UTF-8'))
        sessionId = body['sessionId']
        sessionUser = body['user']
        stage = body['stage']
        module = body['module']
        env = body['env']
        resultTimestampPath = body['resultTimestampPath']

        if '/' in env:
            env = env.replace('/', '-')
            
        envMgmtDataFile = f'{resultTimestampPath}/.Data/EnvMgmt/STAGE={stage}_MODULE={module}_ENV={env}.json'
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        error = None
        status = 'success'

        if '-' in env:
            env = env.replace('-', '/')
        
        try:
            envMgmtData = readJson(envMgmtDataFile)
            envMgmtObj = ManageEnv(env)
            session = {'sessionId':sessionId, 'stage':stage, 'module':module, 'user':sessionUser}
            envMgmtObj.removeFromActiveUsersList([session])
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnvOnFailed', msgType='Info',
                                      msg=f'{session}', forDetailLogs='')

            envMgmtData['envIsReleased'] = True
            writeToJson(envMgmtDataFile, envMgmtData)
                
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            error = errMsg
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnvOnFailed', msgType='Error',
                                      msg=errMsg, forDetailLogs=f'error: {traceback.format_exc(None, errMsg)}')
          
        return JsonResponse({'status': status, 'error': error}, status=statusCode)


class ResetEnv(View):
    """ 
    If the DB is unrepairable, reset it as last resort. 
    """
    @authenticateLogin
    def post(self, request):
        body = json.loads(request.body.decode('UTF-8'))
        env = body['env']
        user = request.session['user']
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        try:
            envMgmtObj = ManageEnv(env)
            envMgmtObj.resetEnv()
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetEnv', msgType='Info',
                                      msg=f'Env: {env}', forDetailLogs='')
                        
        except Exception as errMsg:
            status = 'failed'
            errorMsg = errMsg
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetEnv', msgType='Error',
                                      msg=errorMsg, forDetailLogs=f'ResetEnv: {traceback.format_exc(None, errMsg)}')
            
        return JsonResponse({'status': status, 'errorMsg': errorMsg}, status=statusCode)
'''
#---- Load Balance Mgmt below ----#

#import asyncio
#import httpx
#from django.http.response import HttpResponse
#from asgiref.sync import async_to_sync, sync_to_async

