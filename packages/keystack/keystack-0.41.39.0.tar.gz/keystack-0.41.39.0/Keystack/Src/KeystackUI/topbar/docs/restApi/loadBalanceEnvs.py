import os, sys, traceback
from glob import glob
from re import search
from shutil import rmtree

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from domainMgr import DomainMgr
import EnvMgmt
from globalVars import HtmlStatusCodes
from keystackUtilities import readJson, writeToJson, readYaml, execSubprocessInShellMode, mkdir2, chownChmodFolder, writeToFile, getTimestamp
from EnvMgmt import ManageEnv
from db import DB
from globalVars import GlobalVars
from commonLib import getHttpIpAndPort
from sidebar.sessionMgmt.views import SessionMgmt

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
#---- Load Balance Group Mgmt

class Vars:
    """ 
    For logging the correct topics.
    To avoid human typo error, always use a variable instead of typing the word.
    """
    webpage = 'envs'
    envMgmtDB = 'envMgmt'
    envLoadBalanceDB = 'envLoadBalanceGroups'
    keystackUIIpAddress, keystackIpPort = getHttpIpAndPort() 
    
      
class CreateNewLoadBalanceGroup(APIView):
    loadBalanceGroup    = openapi.Parameter(name='loadBalanceGroup', description="Create a new load-balance group",
                                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)      
    @swagger_auto_schema(tags=['/api/v1/env/loadBalanceGroup/create'], operation_description="The load-balance group",
                         manual_parameters=[loadBalanceGroup])
    @verifyUserRole(webPage=Vars.webpage, action='CreateNewLoadBalanceGroupRest', exclude=['engineer'])
    def post(self, request):
        """ 
        Create a new load balance group

        Description: 
            Create a new load balance group

        POST /api/v1/env/loadBalanceGroup/create
        
        Parameters:
            loadBalanceGroup: <str>: Name of the load balance group to create
        
        Usage:
            envObj = EnvMgmt.ManageEnv(env=self.taskProperties['env'])
            envObj.createNewLoadBalanceGroup([{'user':self.user, 'sessionId':self.timestampFolderName, 
                                               'stage':self.stage, 'task':self.task}])                         
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/create
            
        Return:
            status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # http://ip:port/api/v1/env/loadBalanceGroup?loadBalanceGroup=name
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                loadBalanceGroup = request.GET.get('loadBalanceGroup')
                user = request.GET.get('user', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateNewLoadBalanceGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                loadBalanceGroup = request.data['loadBalanceGroup']
                user = request.data.get('user', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateNewLoadBalanceGroupRest', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        if user is None:
            user = AccountMgr().getRequestSessionUser(request)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup, 'user': user}
            restApi = '/api/v1/env/loadBalanceGroup/create'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='CreateNewLoadBalanceGroup')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        else:                                   
            try:
                # envs: ['Samples/pythonSample', qa, ...]
                # Used envMgmt to set availability
                isLoadBalanceGroupExists = DB.name.isDocumentExists(collectionName=Vars.envLoadBalanceDB,
                                                                    keyValue={'name':loadBalanceGroup},
                                                                    regex=False)
                if isLoadBalanceGroupExists:
                    errorMsg = f'Env load balancer already exists: {loadBalanceGroup}'
                    statusCode = HtmlStatusCodes.error
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateNewLoadBalanceGroup', msgType='Failed',
                                            msg=errorMsg, forDetailLogs='')
                else:    
                    response = DB.name.insertOne(collectionName=Vars.envLoadBalanceDB, data={'name':loadBalanceGroup, 'envs': {}})
                    if response.acknowledged:        
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateNewLoadBalanceGroup', msgType='Info',
                                                msg=f'Create new load balance group: {loadBalanceGroup}', forDetailLogs='')
                    
                    isLoadBalancerExists = DB.name.isDocumentExists(collectionName=Vars.envLoadBalanceDB, keyValue={'name':loadBalanceGroup}, regex=False)
                    if isLoadBalancerExists == False:
                        errorMsg = f'Created env load balancer, but verification failed: {loadBalanceGroup}'
                        statusCode = HtmlStatusCodes.error
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateNewLoadBalanceGroup', msgType='Failed',
                                                msg=errorMsg, forDetailLogs='')
                                            
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateNewLoadBalanceGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
    
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

    
class DeleteLoadBalanceGroup(APIView):
    loadBalanceGroup    = openapi.Parameter(name='loadBalanceGroup', description="Delete a load balance group",
                                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)      
    @swagger_auto_schema(tags=['/api/v1/env/loadBalanceGroup/delete'], operation_description="The load balance group",
                         manual_parameters=[loadBalanceGroup])
    @verifyUserRole(webPage=Vars.webpage, action='DeleteLoadBalanceGroup', exclude=['engineer'])
    def post(self, request):
        """ 
        Delete load balance group

        Description: 
            Delete load balance group

        POST /api/v1/env/loadBalanceGroup/delete
        
        Parameters:
            loadBalanceGroup: <str>: Name of the load balance group to delete
        
        Usage:
            envObj = EnvMgmt.ManageEnv(env=self.taskProperties['env'])
            envObj.createNewLoadBalanceGroup([{'user':self.user, 'sessionId':self.timestampFolderName, 
                                               'stage':self.stage, 'task':self.task}])                         
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/delete
            
        Return:
            status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # http://ip:port/api/v1/env/loadBalanceGroup?loadBalanceGroup=name
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                loadBalanceGroup = request.GET.get('loadBalanceGroup')
                user = request.GET.get('user', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteLoadBalanceGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
             
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                loadBalanceGroup = request.data.get('loadBalanceGroup', None)
                user = request.data.get('user', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteLoadBalanceGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        if user is None:
            user = AccountMgr().getRequestSessionUser(request)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup, 'user': user}
            restApi = '/api/v1/env/loadBalanceGroup/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeleteLoadBalanceGroup')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        else:                                   
            try:
                # Remove the load balance group from all envs in this LB group
                envData = DB.name.getDocuments(collectionName=Vars.envLoadBalanceDB, fields={'name':loadBalanceGroup}, includeFields={'envs':1, '_id':0})

                for env in envData[0]['envs']:
                    DB.name.updateDocument(collectionName=Vars.envMgmtDB, queryFields={'env':env}, 
                                            updateFields={'loadBalanceGroups':loadBalanceGroup},
                                            removeFromList=True)
                    
                DB.name.deleteOneDocument(collectionName=Vars.envLoadBalanceDB, fields={'name': loadBalanceGroup})
                        
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteLoadBalanceGroup', msgType='Info',
                                          msg=f'Load balance group: {loadBalanceGroup}', forDetailLogs='')
                                            
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteLoadBalanceGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
    
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class AddEnvsToLoadBalancGroup(APIView):
    loadBalanceGroup         = openapi.Parameter(name='loadBalanceGroup', description="The load balance group",
                                                 required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    individualEnvsFullPaths  = openapi.Parameter(name='individualEnvsFullPaths', description="A list of full path envs",
                                                 required=False, in_=openapi.IN_QUERY, 
                                                 type=openapi.TYPE_ARRAY, 
                                                 items=openapi.Items(type=openapi.TYPE_STRING))  
    envGroupsFullPaths       = openapi.Parameter(name='envGroupsFullPaths', description="A list of env group folders",
                                                 required=False, in_=openapi.IN_QUERY, 
                                                 type=openapi.TYPE_ARRAY, 
                                                 items=openapi.Items(type=openapi.TYPE_STRING))        
    @swagger_auto_schema(tags=['/api/v1/env/loadBalanceGroup/addEnvs'], operation_description="The load balance group",
                         manual_parameters=[loadBalanceGroup, individualEnvsFullPaths, envGroupsFullPaths])
    @verifyUserRole(webPage=Vars.webpage, action='AddEnvsToLoadBalancGroupRest', exclude=['engineer'])
    def post(self, request):
        """ 
        Select and add Envs to a load balance group

        Description: 
            Add Envs to a load balance group

        POST /api/v1/env/loadBalanceGroup/addEnvs
        
        Parameters:
            loadBalanceGroup: <str>: Name of the load balance group to delete
            individualEnvsFullPaths: <list>: A list of full path envs files
            envGroupsFullPaths: <list>: A list of env group folders                        
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/addEnvs
            
        Return:
            status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        # http://ip:port/api/v1/env/loadBalanceGroup/addEnvs?loadBalanceGroup=name
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                # loadBalanceGroup:loadBalanceGroup, envGroups:envGroupArray, individualEnvs:individualEnvsArray
                loadBalanceGroup        = request.GET.get('loadBalanceGroup', None)
                individualEnvsFullPaths = request.GET.get('individualEnvsFullPaths', None)
                envGroupsFullPaths      = request.GET.get('envGroupsFullPaths', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvsToLoadBalancGroupRest', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                loadBalanceGroup        = request.data.get('loadBalanceGroup', None)
                individualEnvsFullPaths = request.data.get('individualEnvsFullPaths', None)
                envGroupsFullPaths      = request.data.get('envGroupsFullPaths', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvsToLoadBalancGroupRest', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup, 
                      'individualEnvsFullPaths': individualEnvsFullPaths,
                      'envGroupsFullPaths': envGroupsFullPaths}
            restApi = '/api/v1/env/loadBalanceGroup/addEnvs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='AddEnvsToLoadBalancGroup')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                
        else:           
            combinedEnvList = individualEnvsFullPaths + envGroupsFullPaths
            envList = []
            envDeniedList = [] 
            errorMsg = ''

            for eachEnv in envGroupsFullPaths:
                if os.path.isdir(eachEnv):
                    for env in glob(f'{eachEnv}/*'):
                        if bool(search('.+\.(yml|yaml)$', env)) == False:
                            continue
                        
                        individualEnvsFullPaths.append(env)
    
            # ['/opt/KeystackTests/Envs/qa/hgee.yml', '/opt/KeystackTests/Envs/qa/loadcoreSample.yml', 
            # '/opt/KeystackTests/Envs/qa/pythonSample.yml']
            for eachEnv in individualEnvsFullPaths:
                # eachEnv: /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/demoEnv2.yml
                envName = eachEnv.split(f'{GlobalVars.envPath}/')[-1].split('.')[0]
                envList.append(envName)
                envContents = readYaml(eachEnv)
                envData = DB.name.getOneDocument(collectionName=Vars.envMgmtDB, fields={'env':envName})

                if envData is None:
                    # Getting in here means the env was manually created. The env is not in the DB.
                    # Add the env to the DB here.
                    envMgmtObj = EnvMgmt.ManageEnv(envName)
                    if envMgmtObj.isEnvExists() == False:
                        envMgmtObj.addEnv()
                    
                    envData = DB.name.getOneDocument(collectionName=Vars.envMgmtDB, fields={'env':envName})
                    if envData is None:  
                        status = 'failed'
                        statusCode = HtmlStatusCodes.error
                        errorMsg = f'Failed to retrieve env {envName} data from DB. Try refreshing the loadbalance page.'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvsToLoadBalanceGroup', msgType='Failed',
                                                  msg=errorMsg, forDetailLogs='')
                        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
            
                if loadBalanceGroup in envData['loadBalanceGroups']:
                    # The env is already in the load balance group!
                    index = envList.index(envName)
                    envList.pop(index)
                    envDeniedList.append(envName)
                    errorMsg += f'Env:{envName} already in LBG:{loadBalanceGroup}<br>'
                else:        
                    DB.name.updateDocument(collectionName='envMgmt', queryFields={'env':envName}, 
                                           updateFields={'loadBalanceGroups':loadBalanceGroup},
                                           appendToList=True)

            if envDeniedList:
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvsToLoadBalanceGroup', msgType='Error',
                                        msg=errorMsg, forDetailLogs='')

            # Add to envLoadBalanceGroups DB   
            try: 
                # envList: envList: ['qa/loadcoreSample', 'qa/pythonSample', 'pythonSample', 'loadcoreSample']
                envLoadBalanceDetailKeys = {}
                for eachEnv in envList:
                    # Mongodb way to add key/value pair to the existing key envs
                    # NOTE: Added envs to the load balance group as an Object in case in the future there is
                    #       a need to display some details 
                    envData = DB.name.getOneDocument(collectionName=Vars.envLoadBalanceDB, fields={'name':loadBalanceGroup})
                    
                    if eachEnv not in envData['envs'].keys():
                        envLoadBalanceDetailKeys.update({f'envs.{eachEnv}': {'placeholder':None}})

                # Add all the envs to the load balancer group
                if envLoadBalanceDetailKeys:
                    DB.name.updateDocument(collectionName=Vars.envLoadBalanceDB, queryFields={'name':loadBalanceGroup}, 
                                           updateFields=envLoadBalanceDetailKeys)            
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvsToLoadBalanceGroup', msgType='Info',
                                              msg=f'LBG:{loadBalanceGroup} &ensp;Added envs: {envList}', forDetailLogs='')
                                                                                
            except Exception as errMsg:
                if errorMsg == '':
                    errorMsg = str(errMsg)
                else:
                    errMsg2 = str(errMsg)
                    errorMsg += f'{errorMsg}<br>{errMsg2}<br>'
                    
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvsToLoadBalanceGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)    
    
 
class GetLoadBalanceGroups(APIView):
    """_
    Internal usage only
    """
    swagger_schema = None
    def post(self, request):
        """ 
        Get all of the load balance groups

        Description: 
            Get all of the load balance groups

        POST /api/v1/env/loadBalanceGroup/get
        
        Parameters:
            None                      
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/get
            
        Return:
            status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        loadBalanceGroups = '<ul>'
        totalLoadBalanceGroups = 0            
                            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/loadBalanceGroup/get'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetLoadBalanceGroups')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                loadBalanceGroups = response.json()['loadBalanceGroups']
                totalLoadBalanceGroups = response.json()['totalLoadBalanceGroups']
                
        else:        
            try:                
                # {'name': 'Qa', 'envs': []}
                loadBalancers = DB.name.getDocuments(collectionName=Vars.envLoadBalanceDB, fields={}, includeFields={'_id':0}, sortBy=[('name', 1)])
                
                for index, eachLoadBalancer in enumerate(loadBalancers):
                    # {'_id': ObjectId('645d60a27c534d5996dc8d0b'), 'name': 'Qa'}
                    loadBalancerName = eachLoadBalancer['name']
                    totalLoadBalanceGroups += 1
                    if index == 0:
                        loadBalanceGroups += f'<li><input type="radio" name="loadBalancerGroupRadio" value="{loadBalancerName}" onclick="updateLoadBalanceGroup()" checked=checked/>&emsp; {loadBalancerName} </li>'
                    else:
                        loadBalanceGroups += f'<li><input type="radio" name="loadBalancerGroupRadio" value="{loadBalancerName}" onclick="updateLoadBalanceGroup()" />&emsp; {loadBalancerName} </li>'
                                                                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvLoadBalanceGroups', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                        
        loadBalanceGroups += '</ul>'
        
        return Response(data={'loadBalanceGroups':loadBalanceGroups, 
                              'totalLoadBalanceGroups':totalLoadBalanceGroups,
                              'status': status, 'errorMsg': errorMsg}, 
                        status=statusCode) 
    
    
class GetAllEnvs(APIView):
    """_
    Internal usage only
    """
    swagger_schema = None
    def post(self, request):
        """ 
        Get all available envs including subfolder env groups

        Description: 
            Get all envs

        POST /api/v1/env/loadBalanceGroup/getAllEnvs
        
        Parameters:
            user: <str>: The Keystack session user                     
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/getAllEnvs

        Requirements:
            The return html code goes in conjunction with testResultTreeView.css.
            - The template must import CSS: <link href={% static "commons/css/testResultsTreeView.css" %} rel="stylesheet" type="text/css">
            - Calling GetAllEnvs in JS must call await addListeners("caret2") and must have the function available
        
        https://www.w3schools.com/howto/howto_js_treeview.asp
        
        <ul id="testResultFileTree">
            <li><span class="caret2">Beverages</span>
                <ul class="nested">
                    <li>Water</li>
                    <li>Coffee</li>
                    <li><span class="caret2">Tea</span>
                        <ul class="nested">
                            <li>Black Tea</li>
                            <li>White Tea</li>
                            <li><span class="caret2">Green Tea</span>
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
                    
        Return:
            envs, status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
  
        class InternalVar:
            envsHtml = ''
    
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/loadBalanceGroup/getAllEnvs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetAllEnvs')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                InternalVar.envsHtml = response.json()['envs']

        else:
            userAllowedDomains = DomainMgr().getUserAllowedDomains(user) 

            def loop(path, envFiles):
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
                    for eachFile in envFiles:
                        envFileFullPath = f'{path}/{eachFile}'
                        # Show just the name of the env without the group name because user expanded the group folder already.
                        envName = eachFile.split('.')[0]

                        if bool(search(f'{GlobalVars.keystackTestRootPath}/Envs/(DOMAIN=(.+?)/.+)\.(yml|yaml)$', envFileFullPath)) is False:
                            continue
                        
                        regexpMatch = search(f'{GlobalVars.keystackTestRootPath}/Envs/(DOMAIN=(.+?)/.+)\.(yml|yaml)$', envFileFullPath)
                        if regexpMatch.group(2) not in userAllowedDomains:
                            continue
                        
                        envPlusGroupName = regexpMatch.group(1)
                        # Check if env parallelUsage=True|False.
                        # If parallelUsage = False:
                        #    check env in DB if it belongs to a load balance group. 
                        #    Don't show the option if the env already belongs to a load balance group.
                        #envContents = readYaml(envFileFullPath)

                        #if type(envContents) != dict:
                        #    #raise Exception(f'Env yml file has syntax error. It is not a dict type. env file: {envFileFullPath}')
                        #    print(f'getAllEnvs loop: Env yml file has syntax error. It is not a dict type. env file: {envFileFullPath}')
                        envData = DB.name.getOneDocument(collectionName=Vars.envMgmtDB, fields={'env':envPlusGroupName})
                        if envData:
                            loadBalanceGroup = envData.get('loadBalanceGroup', None)
                        else:
                            loadBalanceGroup = None
                        
                        if loadBalanceGroup:
                            html += f'<li><input type="checkbox" disabled/>&emsp; {envName}</li>'
                        else:
                            html += f'<li><input type="checkbox" name="envCheckboxLBG" envPath="{path}" value="{envFileFullPath}" />&emsp; {envName}</li>'
                                    
                except Exception as errMsg:
                    errorMsg = str(errMsg)
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAllEnvs', msgType='Error',
                                              msg=errorMsg, forDetailLogs=traceback.format_exc(None, errorMsg))  

                html += '</ul>'
                return html
                            
            try:    
                for root,dir,files in os.walk(GlobalVars.envPath):
                    # root: /opt/KeystackTests/Envs/DOMAIN=newDomain1/KeystackQA
                    if 'DOMAIN=' not in root:
                        continue
                    
                    # /opt/KeystackTests/Envs/DOMAIN=Communal
                    # Files in the Domain Communal
                    regexMatch = search(f'.*DOMAIN=(.+?)/.+', root)
                    if regexMatch:
                        if regexMatch.group(1) not in userAllowedDomains:
                            continue
                    else:
                        # SubGroups inside a domain folder
                        regexMatch = search(f'.*DOMAIN=(.+)(/.+)?', root)
                        if regexMatch:
                            if regexMatch.group(1) not in userAllowedDomains:
                                continue
                                                       
                    # Some folders might not have any env files.  Check for file count.
                    totalFilesInFolder = execSubprocessInShellMode(f'find {root} -maxdepth 1 -type f | wc -l', showStdout=False)[-1]
                    if int(totalFilesInFolder) == 0:
                        continue
                    
                    shortenPath = root.split(f'{GlobalVars.envPath}/')[-1]
                    html = loop(path=root, envFiles=files)
            
                    topFolder = '<ul id="testResultFileTree">'
                    
                    # # Add checkbox for for individual selections
                    topFolder += f'\n\t\t\t<li><input type="checkbox" name="envGroupCheckbox" value={root} onclick="disableEnvCheckboxes(this)" />&emsp;<span class="caret2">&ensp;{shortenPath}</span>'
                    
                    InternalVar.envsHtml += f'{topFolder}{html}</li></ul>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAllEnvs', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))        

        return Response(data={'envs': InternalVar.envsHtml, 'status': status, 'errorMsg': errorMsg}, status=statusCode) 
 

class GetLoadBalanceGroupEnvs(APIView):
    """_
    Internal usage only
    """
    swagger_schema = None
    def post(self, request):
        """ 
        Description: 
            Get the configured load balance group envs

        POST /api/v1/env/loadBalanceGroup/getEnvs
        
        Parameters:
            loadBalanceGroup: <str>: The load balance group
            user: <str>: The Keystack session user                     
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/getEnvs
                    
        Return:
            envs, status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        loadBalanceGroup = request.data.get('loadBalanceGroup', None)
        envs = []
       
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup}
            restApi = '/api/v1/env/loadBalanceGroup/getEnvs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetLoadBalanceGroupEnvs')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                envs = response.json()['loadBalanceGroupEnvs']
        else:  
            try:
                loadBalanceGroupEnvs = DB.name.getOneDocument(collectionName=Vars.envLoadBalanceDB, fields={'name':loadBalanceGroup})
                if loadBalanceGroupEnvs is None:
                    raise Exception(f'No such load balance group: {loadBalanceGroup}.  Most likely a typo in the playbook.')
                    
                for eachEnv, values in loadBalanceGroupEnvs['envs'].items():
                    if os.path.exists(f'{GlobalVars.keystackTestRootPath}/Envs/{eachEnv}.yml') is False:
                        print(f'GetLoadBalanceGroupEnvs() Env not exists in /Envs. Removing env:{eachEnv} from LBG:{loadBalanceGroup}')
                        result = DB.name.updateDocument(collectionName=Vars.envLoadBalanceDB,
                                                        queryFields={'name': loadBalanceGroup},
                                                        updateFields={f'envs.{eachEnv}': ""}, removeKey=True)
                        
                        print(f'GetLoadBalanceGroupEnvs() Removing non-existing env from envMgmt DB: {eachEnv}')
                        result = DB.name.deleteOneDocument(collectionName='envMgmt', fields={'env': eachEnv})
                          
                    else:
                        envs.append(eachEnv)
         
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getLoadBalanceGroupEnvs', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'loadBalanceGroupEnvs':envs, 'status': status, 'errorMsg': errorMsg}, status=statusCode) 
       

class GetLoadBalanceGroupEnvsUI(APIView):
    """_
    Internal usage only
    """
    swagger_schema = None

    def post(self, request):
        """ 
        Get the load balance group envs

        Description: 
            Get the load balance group envs

        POST /api/v1/env/loadBalanceGroup/getEnvs
        
        Parameters:
            loadBalanceGroup: <str>: The load balance group
            user: <str>: The Keystack session user                     
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/getEnvs
                    
        Return:
            envs, status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        loadBalanceGroup = request.data.get('loadBalanceGroup', None)
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup}
            restApi = '/api/v1/env/loadBalanceGroup/getEnvsUI'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetLoadBalanceGroupEnvsUI')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                html = response.json()['loadBalanceGroupEnvs']
        else:  
            try:
                # GetLoadBalanceGroupEnvsUI: loadBalanceGroupEnvs: {'_id': ObjectId('650873f63fe3e3e2bd8abe21'), 'name': 'regression', 'envs': {'Samples/airMosaicSample': {'placeholder': None}, 'Samples/bobafett': {'placeholder': None}, 'Samples/bringup': {'placeholder': None}, 'Samples/global': {'placeholder': None}, 'Samples/hubert': {'placeholder': None}, 'Samples/loadcoreSample': {'placeholder': None}, 'Samples/pythonSample': {'placeholder': None}, 'Samples/stage': {'placeholder': None}, 'Samples/teardown': {'placeholder': None}, 'Samples/test': {'placeholder': None}, 'qa/hgee': {'placeholder': None}, 'qa/loadcoreSample': {'placeholder': None}, 'qa/pythonSample': {'placeholder': None}, 'qa/server10': {'placeholder': None}}}

                loadBalanceGroupEnvs = DB.name.getOneDocument(collectionName=Vars.envLoadBalanceDB, fields={'name': loadBalanceGroup})
                
                if loadBalanceGroupEnvs:
                    # loadBalanceGroupEnvs = {'_id': ObjectId('64626dad290aa13111466ed3'), 'name': 'qa', 'envs': {}}
                                    
                    html =    '<center><table class="tableFixHeadLB" style="width:90%">'    
                    html +=        '<thead>'
                    html +=            '<tr>'
                    html +=                 '<th></th>'
                    html +=                 '<th>Env</th>'
                    html +=                 '<th>In-Used-By Pipeline Id</th>'
                    html +=                 '<th>User</th>'
                    html +=            '</tr>'
                    html +=         '</thead>'
                    html +=         '<tbody>'
                    
                    # eachEnv: qa/pythonSample           
                    for eachEnv, values in loadBalanceGroupEnvs['envs'].items():                        
                        html += f'<tr>'
                        
                        # GET just the activeUsers. activeUsers returns a list
                        envDetails = DB.name.getDocuments(collectionName=Vars.envMgmtDB, fields={'env':eachEnv}, 
                                                          includeFields={'_id':0, 'activeUsers':1})

                        try:
                            envDetails[0]
                        except IndexError:
                            # TODO: This env was not created by the UI. Therefore, it is missing keywords/values:
                            #       env, available, loadBalanceGroups, activeUsers, waitList
                            #       Must create the Keywords/values
                            #       Somehow the env keys/values are added when manually creating an env!  Figure this out!
  
                            #params = {"newEnv": eachEnv, "envGroup":envGroup, "textArea":textArea}
                            restApi = '/api/v1/env/create'
                            continue
                            
                        inUsedBySessionIdList = ''
                        inUsedByUserList = ''
                        
                        for sessionDetails in envDetails[0]["activeUsers"]:
                            # sessionDetails: {'sessionId': '05-18-2023-15:48:13:349241_9557', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=Samples-pythonSample/05-18-2023-15:48:13:349241_9557/overallSummary.json', 'user': 'hgee', 'stage': 'Test', 'task': 'CustomPythonScripts'}
                            inUsedBySessionIdList += f'{sessionDetails["sessionId"]}<br>'
                            inUsedByUserList += f'{sessionDetails["user"]}<br>'
                        
                        # inUsedBy: Is set when the env is reserved
                        #if values['inUsedBy']:
                        # Can't select this env for delete if the env is being used
                        if envDetails[0]['activeUsers']:
                            html += f'<td><input type="checkbox" name="removeEnvFromLB" value="{eachEnv}" disabled></td>'
                        else:     
                            html +=  f'<td><input type="checkbox" name="removeEnvFromLB" value="{eachEnv}"></td>'
                            
                        html +=     f'<td>{eachEnv}</td>'
                        html +=     f'<td>{inUsedBySessionIdList}</td>'
                        html +=     f'<td>{inUsedByUserList}</td>'
                        html += f'</tr>'
                        
                    html +=  '</tbody>'    
                    html +=  '</table></center>'
                                            
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getLoadBalanceGroupEnvs', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'loadBalanceGroupEnvs':html, 'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    

class RemoveAllEnvsFromLoadBalanceGroup(APIView):
    loadBalanceGroup       = openapi.Parameter(name='loadBalanceGroup', description="The load balance group",
                                               required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)        
    @swagger_auto_schema(tags=['/api/v1/env/loadBalanceGroup/removeAllEnvs'], operation_description="The load balance group",
                         manual_parameters=[loadBalanceGroup])
    @verifyUserRole(webPage=Vars.webpage, action='RemoveAllEnvsFromLoadBalanceGroupRest', exclude=['engineer'])
    def post(self, request):
        """ 
        Remove all envs from the load balance group

        Description: 
            Remove all envs from the load balance group

        POST /api/v1/env/loadBalanceGroup/removeAllEnvs
        
        Parameters:
            loadBalanceGroup: <str>: The load balance group
            user: <str>: The Keystack session user                     
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/removeAllEnvs
                    
        Return:
            envs, status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
           
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                loadBalanceGroup = request.GET.get('loadBalanceGroup')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveAllEnvsFromLBGRest', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
        # JSON format
        if request.data:
            try:
                loadBalanceGroup = request.data['loadBalanceGroup']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveAllEnvsFromLBGRest', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup}
            restApi = '/api/v1/env/loadBalanceGroup/removeAllEnvs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='RemoveAllEnvsFromLoadBalanceGroup')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error

        else:
            try:              
                # 1: Get all the envs from the load balance group in order to know which envs to reset in the envMgmt DB
                envData = DB.name.getDocuments(collectionName=Vars.envLoadBalanceDB, fields={'name':loadBalanceGroup}, 
                                            includeFields={'envs':1, '_id':0})

                for env in envData[0]['envs'].keys():
                    DB.name.updateDocument(collectionName=Vars.envMgmtDB, queryFields={'env':env}, 
                                           updateFields={'loadBalanceGroups':loadBalanceGroup},
                                           removeFromList=True)

                # Do this last
                DB.name.updateDocument(collectionName=Vars.envLoadBalanceDB, queryFields={'name':loadBalanceGroup}, 
                                       updateFields={'envs': {}})
                                            
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removeAllEnvsFromLBG', msgType='Info',
                                        msg=f'Load balance group:{loadBalanceGroup}', forDetailLogs='')
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removeAllEnvsFromLBG', msgType='Error',
                                          msg=f'Load balance group:{loadBalanceGroup}<br>error:{errorMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))
                             
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    

class RemoveSelectedEnvsRest(APIView):
    loadBalanceGroup       = openapi.Parameter(name='loadBalanceGroup', description="The load balance group",
                                               required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 
    removeSelectedEnvs     = openapi.Parameter(name='removeSelectedEnvs', 
                                               description="A list of env names. Ex: rack1 or if env is in a group folder, qa/rack1",
                                               required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)        
    @swagger_auto_schema(tags=['/api/v1/env/loadBalanceGroup/removeEnvs'], operation_description="The load balance group",
                         manual_parameters=[loadBalanceGroup, removeSelectedEnvs])
    @verifyUserRole(webPage=Vars.webpage, action='RemoveSelectedEnvsRest', exclude=['engineer'])
    def post(self, request):
        """ 
        Remove selected envs from the load balance group

        Description: 
            Remove selected envs from the load balance group

        POST /api/v1/env/loadBalanceGroup/removeEnvs
        
        Parameters:
            loadBalanceGroup: <str>: The load balance group
            user: <str>: The Keystack session user                     
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/removeEnvs
                    
        Return:
            envs, status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
           
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                loadBalanceGroup = request.GET.get('loadBalanceGroup', None)
                removeSelectedEnvs = request.GET.get('removeSelectedEnvs', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveSelectedEnvsRest', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            try:
                loadBalanceGroup = request.data.get('loadBalanceGroup', None)
                removeSelectedEnvs = request.data.get('removeSelectedEnvs', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveSelectedEnvsRest', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup, 'removeSelectedEnvs': removeSelectedEnvs}
            restApi = '/api/v1/env/loadBalanceGroup/removeEnvs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='RemoveSelectedEnvsRest')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error

        else:        
            try:
                for env in removeSelectedEnvs:
                    # Remove the env from the load balance group
                    DB.name.updateDocument(collectionName=Vars.envMgmtDB, 
                                           queryFields={'env':env}, 
                                           updateFields={'loadBalanceGroups':loadBalanceGroup},
                                           removeFromList=True)

                    # Do this last: Update the load balance group DB 
                    DB.name.updateDocument(collectionName=Vars.envLoadBalanceDB, 
                                           queryFields={'name':loadBalanceGroup}, 
                                           updateFields={f'envs.{env}': ""}, removeKey=True)
                                            
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveSelectedEnvsFromLB', msgType='Info',
                                          msg=f'Load balance group:{loadBalanceGroup}  envs:{removeSelectedEnvs}', forDetailLogs='')
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removeAllEnvsFromLBG', msgType='Error',
                                          msg=f'LBG:{loadBalanceGroup}<br>error:{errorMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))
                             
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
            
 
class ResetLoadBalanceGroupRest(APIView):
    """_
    Internal usage only
    """
    swagger_schema = None
    @verifyUserRole(webPage=Vars.webpage, action='ResetLoadBalanceGroupRest', exclude=['engineer'])
    def post(self, request):
        """ 
        Wipe out the load balance group.  Remove all envs. Reset the internal DB.

        Description: 
            Wipe out the load balance group.  Remove all envs. Reset the internal DB.

        POST /api/v1/env/loadBalanceGroup/reset
        
        Parameters:
            loadBalanceGroup: <str>: The load balance group
            user: <str>: The Keystack session user                     
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/loadBalanceGroup/reset
                    
        Return:
            envs, status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        loadBalanceGroup = request.data.get('loadBalanceGroup', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'loadBalanceGroup': loadBalanceGroup}
            restApi = '/api/v1/env/loadBalanceGroup/reset'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='ResetLoadBalanceGroup')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                Response(data={'testResults':htmlTestResults, 'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
            else:
                htmlTestResults = response.json()['testResults']
        else:   
            try:
                DB.name.updateDocument(collectionName='envMgmt', queryFields={}, 
                                    updateFields={'loadBalanceGroups':loadBalanceGroup},
                                    removeFromList=True, multi=True)
                
                DB.name.updateDocument(collectionName=Vars.envLoadBalanceDB, queryFields={'name':loadBalanceGroup}, 
                                    updateFields={'envs': {}}) 
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetLoadBalanceGroup', msgType='Info',
                                        msg=f'Cleared Load-Balance Group={loadBalanceGroup}', forDetailLogs='')                                         
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetLoadBalanceGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    
    