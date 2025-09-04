import os, sys, json, traceback, subprocess
from re import search
from glob import glob

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

import db
from execRestApi import ExecRestApi
from systemLogging import SystemLogsAssistant
from accountMgr import AccountMgr
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from keystackUtilities import convertStrToBoolean, mkdir2, readYaml, writeToYamlFile, chownChmodFolder, removeFile
from globalVars import GlobalVars, HtmlStatusCodes

class Vars:
    webpage = 'controllers'


def getMainAndRemoteControllerIp(request):
    """ 
    Get the mainControllerIp and the remoteControllerIp
    
    returning format: ip:portIp
    """
    remoteControllerIp = request.data.get('remoteController', None)
    
    if 'mainControllerIp' in request.session:
        # IP:PortIp
        mainControllerIp = request.session['mainControllerIp']
    else:
        mainControllerIp = remoteControllerIp
    
    # if remoteControllerIp is None:
    #     remoteControllerIp = mainControllerIp
            
    return mainControllerIp, remoteControllerIp
            
def executeRestApiOnRemoteController(sendHttp='post', remoteControllerIp=None, restApi=None, params={}, user=None,
                                     webPage=None, action=None, timeout=10, maxRetries=5,
                                     showApiOnly=True, silentMode=True, ignoreError=False, stream=False):
    """ 
    Internal helper function for all Rest API calls to a remote controller.
    The local controller checks if mainControllerIp and remoteControllerIp are same.
    Only if they're different, the respective local controller will call this function to send a REST API
    to the remote controllerIp, get the response and return the response to the originator.
    
    1> LocalController -> response = remoteController <-> nginx <-> gunicorn <-> Django
    2> Get returned json values from response and update the localController's browser
    
    Reads the controller registry file to get the access-key
    """
    response = None
    errorMsg = None
    status = 'success'
   
    # Coming in here means to view a remote controller
    # Get the Access-Key from the remote_<controller_ip>.yml file
    # /opt/KeystackSystem/.Controllers/remote_192.168.28.17:28028.yml
    remoteControllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'
    remoteControllerRegistryFile = f'{remoteControllerRegistryPath}/remote_{remoteControllerIp}.yml'
    
    if ':' in remoteControllerIp:
        ipPort = remoteControllerIp.split(':')[-1]
        remoteControllerIp = remoteControllerIp.split(':')[0]
    else:
        ipPort = None
        
    if os.path.exists(remoteControllerRegistryFile):
        # {'accessKey': 'X1jEtPdUiA4jdOWCH1aoog', 'controller': '192.168.28.7', 'https': False, 'ipPort': 8000}
        try:
            data = readYaml(remoteControllerRegistryFile)
        except Exception as errMsg:
            status = 'failed'
            errorMsg = f'readYaml:remoteControllerRegistryFile<br><br>{traceback.format_exc(None, errMsg)}'
            return response, errorMsg, status
            
        # curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"view": "current", "group": "Default"}' -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/pipeline/getSessions  
        #print(f'---- executeRestApiOnRemoteController: remote:{remoteControllerIp} ipPort={ipPort} https={data["https"]}  restApi={restApi}  params={params}') 
                    
        restObj = ExecRestApi(ip=remoteControllerIp, port=ipPort, https=data['https'],
                              headers={"Content-Type": "application/json", "Access-Key": data['accessKey']})
        
        if sendHttp == 'post':
            response = restObj.post(restApi, params=params, headers=None, silentMode=silentMode, showApiOnly=showApiOnly,
                                    ignoreError=ignoreError, timeout=timeout, maxRetries=maxRetries, user=user, webPage=webPage, action=action)
        if sendHttp == 'get':
            response = restObj.get(restApi, params=params, stream=stream, showApiOnly=showApiOnly, silentMode=silentMode,
                                   ignoreError=ignoreError, timeout=timeout, maxRetries=maxRetries, user=user, webPage=webPage, action=action)
        if sendHttp == 'delete':
            response = restObj.delete(restApi, params=params, headers=None, maxRetries=maxRetries, user=user, webPage=webPage, action=action)
              
        del restObj 
        
        if response and str(response.status_code).startswith('2') == False:
            #  {"sessions": {}, "status": "failed", "errorMsg": "GET Exception error 2/2 retries: HTTPSConnectionPool(host='192.168.28.17', port=88028): Max retries exceeded with url: /api/v1/sessions?view=current&group=Default (Caused by SSLError(SSLError(1, '[SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:997)')))"}
            try:
                error = json.loads(response.content.decode('utf-8'))
                errorMsg = error['errorMsg']
            except Exception as errMsg:
                status = 'failed'
                errorMsg = traceback.format_exc(None, errMsg)
                print(f'\nexecuteRestApiOnRemoteController: json.loads failed on response.content')
            
            if settings.KEYSTACK_SESSIONS_CONNECTIVITY == True:
                settings.KEYSTACK_SESSIONS_CONNECTIVITY = False
                SystemLogsAssistant().log(user=user, webPage=webPage, action=action, msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
    else:
        status = 'failed'
        errorMsg = f'executeRestApiOnRemoteController: No remote controller found: {remoteControllerRegistryFile}'
        SystemLogsAssistant().log(user=user, webPage=webPage, action=action, msgType='Error', msg=errorMsg, 
                                  forDetailLogs= f'remoteControllerIp:{remoteControllerIp} restApi:{restApi} action:{action}')

    return response, errorMsg, status
               
                        
class AddController(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='addController', adminOnly=True) 
    def post(self, request):
        """ 
        Add a controller.
        This will generate an access-key for user to register
        on the controller to be added so the remote controller
        could authenticate valid users by the access-key.
        
        Each added remote controller has its own file:
            /path/keystackSystem/.Controllers/remote_<controllerIP>.yml
            
        Step to add a remote controller:
           - On the main controller, add "remote controller"
             (This will generate an Access-Key)
           - Go on the remote controller, add "Access Key" with the above main controller IP
        """
        body = json.loads(request.body.decode('UTF-8'))
        controllerName = body['controllerName']
        controllerIp = body['controllerIp']
        ipPort = str(body['ipPort'])
        https = convertStrToBoolean(body['https'])
        verifyConnectivity = convertStrToBoolean(body['verifyConnectivity'])
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None

        if https and ipPort == '':
            # Default https port to 443
            ipPort = str(443)
            registryFilename = f'remote_{controllerIp}:443.yml'

        # Command to verify connectivity
        command = f'nc -vz {controllerIp}'                   
        if ipPort != '':
            registryFilename = f'remote_{controllerIp}:{ipPort}.yml'
            command += f' {str(ipPort)}'
        else:
            registryFilename = f'remote_{controllerIp}.yml'
            
        import secrets
        accessKey = secrets.token_urlsafe(16)
            
        try:
            controllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'
            controllerRegistryFile = f'{controllerRegistryPath}/{registryFilename}'
            
            newControllerRegistry = {'controllerName': controllerName, 
                                     'controller':controllerIp, 
                                     'ipPort':int(ipPort),
                                     'https':https, 
                                     'accessKey':accessKey}
            
            if bool(search('^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', controllerIp)) == False:
                return Response({'status':'failed', 'errorMsg':f'The controller IP is incorrect: {controllerIp}'}, status=HtmlStatusCodes.success)
            
            if os.path.exists(controllerRegistryPath) == False:
                mkdir2(controllerRegistryPath, stdout=False)
            
            if os.path.exists(controllerRegistryFile):
                return Response({'status':'failed', 'errorMsg':f'The controller already exists: {controllerIp}'}, status=HtmlStatusCodes.success)
            
            if verifyConnectivity:
                verifiedController = False
                
                # nc -vz 192.168.28.17 88028
                # Ncat: Version 7.70 ( https://nmap.org/ncat )
                # Ncat: Connected to 192.168.28.17:88028
                run = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                processError, process = run.communicate()

                for line in process.decode('utf-8').split('\n'):
                    if line:
                        # CentOS/Rocky success response: Connected to 192.168.28.17:88028
                        # Ubuntu success response: Connection to 192.168.28.7 8000 port [tcp/*] succeeded!
                        if bool(search(f'.*Connected to {controllerIp}|.*succeeded', line)):
                            verifiedController = True
                            
                if verifiedController == False:
                    error = f'Controller is unreachable: {controllerIp} {ipPort}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddController', msgType='Failed',
                                              msg=error, forDetailLogs='')
                    return Response(data={'status':'failed', 'errorMsg':error}, status=HtmlStatusCodes.error)

            writeToYamlFile(newControllerRegistry, controllerRegistryFile, mode='w')
            chownChmodFolder(controllerRegistryPath, GlobalVars.user, GlobalVars.userGroup, permission=770, stdout=False)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddController', msgType='Info',
                                      msg=f'Linked controller: {controllerIp}', forDetailLogs='')
                
        except Exception as errMsg:
            error = str(errMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddController', msgType='Error',
                                      msg=error, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'accessKey': accessKey, 'status': status, 'errorMsg': error}, status=statusCode)


class DeleteControllers(APIView):    
    @verifyUserRole(webPage=Vars.webpage, action='removeController', adminOnly=True)
    def post(self, request):
        body = json.loads(request.body.decode('UTF-8'))
        controllers = body['controllers']
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
    
        try:
            controllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'
            controllerList = []
            for controller in controllers:
                controllerRegistryFile = f'{controllerRegistryPath}/remote_{controller}.yml'
                # removeFile will verify if file exists
                removeFile(controllerRegistryFile)
                controllerList.append(controller)
                
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveControllers', msgType='Info',
                                      msg=f'{controllerList}', forDetailLogs='') 
               
        except Exception as errMsg:
            error = str(errMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, 
                                      action='RemoveControllers', msgType='Error', msg=errMsg,
                                      forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status': status, 'errorMsg': error}, status=statusCode)
            
                    
class GetControllers(APIView):
    """ 
    The Controller Mgmt webpage.  Not the same as GetControllerList() for dropdown selection
    """
    @verifyUserRole(webPage=Vars.webpage, action='GetControllers')
    def post(self,request):
        user = request.session['user']
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        tableData = ''
        
        try:
            controllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'

            for controller in glob(f'{controllerRegistryPath}/remote_*.yml'):
                data = readYaml(controller)
                ipPortSet = data.get('ipPort', None)
                
                if ipPortSet:
                    controllerIp = f'{data["controller"]}:{ipPortSet}'
                else:
                    controllerIp = data['controller']

                tableData += '<tr>'
                tableData += f'<td><input type="checkbox" name="controllerCheckboxes" controller="{controllerIp}"/></td>'
                tableData += f'<td style="text-align:center">{data["controllerName"].capitalize()}</td>'
                tableData += f'<td style="text-align:center">{data["https"]}</td>'
                tableData += f'<td style="text-align:center">{data["controller"]}</td>'
                tableData += f'<td style="text-align:center">{data["ipPort"]}</td>'
                if request.session['userRole'] == 'admin':
                    tableData += f'<td style="text-align:center">{data["accessKey"]}</td>'
                else:
                    tableData += f'<td style="text-align:center">User is unauthorized to view</td>'
                tableData += '</tr>'
                                
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            errorMsg = str(errMsg)
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetControllers', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
         
        return Response(data={'tableData': tableData, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class GetControllerList(APIView):
    #@verifyUserRole(webPage=Vars.webpage, action='getControllerList')
    def post(self, request):
        """ 
        Get controller dropdown menu for sidebar
        
        This function is called in base.js by getControllerList():
        
            const data = await commons.postData("/api/v1/system/controller/getControllerList",  
                                                {remoteController: sessionStorage.getItem("remoteController")})
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        controllerRegistryPath = GlobalVars.controllerRegistryPath
        user = AccountMgr().getRequestSessionUser(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success

        #print('\n---- GetControllerList REMOTE_ADDR:', request.META) 
                       
        # 192.168.28.17:443 192.168.28.7:8000
        # 192.168.28.7:8000 192.168.28.7:8000
        if remoteControllerIp != mainControllerIp:
            backgroundColor = 'red'
            controllerName = 'Remote'
            controllerTitle = remoteControllerIp
        else:
            backgroundColor = 'blue'
            controllerName = 'Main'
            controllerTitle = mainControllerIp

        html = '<div class="dropdown me-3">'
        
        #print(f'\n---- GetControllerList: mainControllerIp:{mainControllerIp}  remoteControllerIp:{remoteControllerIp}  controllerName:{controllerName}  controllerTitle:{controllerTitle} ---')
                          
        try:
            html += f'        <button type="button" class="btn btn-primary dropdown-toggle mainFontSize" style="background-color:{backgroundColor}" data-bs-toggle="dropdown" aria-expanded="false" data-bs-offset="10,20">{controllerTitle}: {controllerName}</button>'
                                    
            html += '    <ul class="dropdown-menu">'
            
            # Always include the main controller to go back into
            html += f'        <li><a style="padding-left:5px" class="dropdown-item" href="#" onclick="connectToController(this)" connectToController="{mainControllerIp}">{mainControllerIp} - Main</a></li><br>'  
                                                        
            # A list of remote controller
            for controller in glob(f'{controllerRegistryPath}/remote_*.yml'):
                # {'name': 'sanity', 'accessKey': 'll-x_8RIv0Uh-dhuA7r3YA', 'controller': '192.168.28.17', 'https': True, 'ipPort': 443}
                data = readYaml(controller)
                controllerIp = data['controller']
                controllerName = data['controllerName'].capitalize()
                ipPort = data['ipPort']
                
                # Set the current controller
                controllerName = controllerName.capitalize()
                
                # Add the port to the ip address
                if ipPort != '':
                    controllerIp += f':{ipPort}'

                html += f'        <li><a style="padding-left:5px" class="dropdown-item" href="#" onclick="connectToController(this)" connectToController="{controllerIp}">{controllerIp} - {controllerName}</a></li><br>'             
                
            html += '    </ul>'
                        
        except Exception as errMsg:
            errorMsg = str(f'getControllerList: {errMsg}')
            print(errorMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetControllerList', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        html += '</div><br>'

        return Response(data={'status':status, 'errorMsg':errorMsg,
                              'controllers': html},
                              status=statusCode) 


class RegisterRemoteAccessKey(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RegisterRemoteAccessKey', adminOnly=True)
    def post(self, request):
        """ 
        Register a remote controller access key
        for ReST API executions.
        """
        body = json.loads(request.body.decode('UTF-8')) 
        user = request.session['user']
        
        # CurrentController is for dropdown menu title display               
        controllerIp = body['controllerIp']
        controllerName = body['controllerName']
        accessKey = body['accessKey']
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        
        try:
            # Validate the IP address format first
            if bool(search('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', controllerIp)) == False:
                statusCode = HtmlStatusCodes.error
                errorMsg = f'The controller IP address format is incorrect: {controllerIp}'
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RegisterRemoteAccessKey', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
                        
            controllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'
            controllerAccessKeyFile = f'{controllerRegistryPath}/accessKeys.yml'
            
            if os.path.exists(controllerRegistryPath) is False:
                mkdir2(controllerRegistryPath, stdout=False)
            
            # Verify if controller exists first
            if os.path.exists(controllerAccessKeyFile):
                 data1 = readYaml(controllerAccessKeyFile)
                 if data1:
                    for accessKeyLookup,controller in data1.items():
                        if controller == controllerIp:
                            errorMsg = f'The controller IP already exists: {controllerIp}'
                            status = 'failed'
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RegisterRemoteAccessKey', msgType='Error',
                                                      msg=errorMsg, forDetailLogs='')
                            return Response({'status':status, 'errorMsg':errorMsg}, status=HtmlStatusCodes.success)
            
            if os.path.exists(controllerAccessKeyFile) == False:
                data = {accessKey: {'controllerName': controllerName, 'controllerIp': controllerIp}}
                writeToYamlFile(data, controllerAccessKeyFile, mode='w')
            else:
                data = readYaml(controllerAccessKeyFile)
                if data:
                    data.update({str(accessKey): {'controllerName': controllerName, 
                                                  'controllerIp': controllerIp}})
                    writeToYamlFile(data, controllerAccessKeyFile, mode='w')
                else:
                    data = {accessKey: {'controllerName': controllerName, 
                                        'controllerIp': controllerIp}}
                    writeToYamlFile(data, controllerAccessKeyFile, mode='w')
                
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            errorMsg = str(errMsg)
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RegisterRemoteAccessKey', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                   
        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
        
        
class RemoveAccessKeys(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemoveAccessKeys', adminOnly=True)
    def post(self, request):
        """ 
        Remove remote controller access keys
        """
        body = json.loads(request.body.decode('UTF-8')) 
        user = request.session['user']
        accessKeys = body['accessKeys']
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        
        try:                        
            controllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'
            controllerAccessKeyFile = f'{controllerRegistryPath}/accessKeys.yml'
            
            if os.path.exists(controllerAccessKeyFile):
                accessKeyData = readYaml(controllerAccessKeyFile)
                for accessKey in accessKeys:
                    if accessKey in list(accessKeyData.keys()):
                        del accessKeyData[accessKey]
                        writeToYamlFile(accessKeyData, controllerAccessKeyFile, mode='w')
                        
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveAccessKeys', msgType='Info',
                                          msg="", forDetailLogs='')
            else:
                statusCode = HtmlStatusCodes.error
                error = 'No access-key database located'
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveAccessKeys', msgType='Error',
                                          msg=error, forDetailLogs='')
                                
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            error = str(errMsg)
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveAccessKeys', msgType='Error',
                                      msg=error, forDetailLogs=traceback.format_exc(None, error))
                   
        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class GetAccessKeys(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetAccessKeys', adminOnly=True)
    def post(self, request):
        """ 
        Get remote controller access-keys 
        """
        user = request.session['user']
        status = 'success'
        error = None
        statusCode = HtmlStatusCodes.success
        tableData = ''
        controllerRegistryPath = f'{GlobalVars.controllerRegistryPath}'
        accessKeyFile = f'{controllerRegistryPath}/accessKeys.yml'
        
        try:
            if os.path.exists(accessKeyFile):
                accessKeysData = readYaml(accessKeyFile)
                if accessKeysData:            
                    for accessKey, properties in accessKeysData.items():                              
                        tableData += '<tr>'
                        tableData += f'<td><input type="checkbox" name="accessKeyCheckboxes" accessKey="{accessKey}"/></td>'
                        tableData += f'<td style="text-align:center">{properties["controllerName"].capitalize()}</td>'
                        tableData += f'<td style="text-align:center">{properties["controllerIp"]}</td>'
                        tableData += f'<td style="text-align:center">{accessKey}</td>'
                        tableData += '</tr>'
                        
        except Exception as errMsg:
            status = 'failed'
            error = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAccessKeys', msgType='Error',
                                      msg=error, forDetailLogs=traceback.format_exc(None, error))
                        
        return Response(data={'status':status, 'errorMsg':error, 'tableData':tableData}, status=statusCode)
        
                        
class GenerateAccessKey(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GenerateAccessKey', adminOnly=True)
    def get(self, request):
        """
        Description: 
            Generate a unique access key for a remote controller linkage 
            For controller-to-controller usage
        """
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        sessions = None
        accessKey = None
        
        try:
            import secrets
            accessKey = secrets.token_urlsafe(16)
        except Exception as errMsg:
            status = 'failed'
            error = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GenerateAccessKey', msgType='Error',
                                      msg=error, forDetailLogs=traceback.format_exc(None, error))
                             
        return Response({'accessKey':accessKey, 'status':status, 'errorMsg':error}, status=statusCode)

