import os, sys

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import HtmlStatusCodes

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets


class Vars:
    """ 
    For logging the correct topics.
    To avoid human typo error, always use a variable instead of typing the word.
    """
    webpage = 'accountMgmt'
    

class GetApiKeyFromRestApi(APIView):
    login = openapi.Parameter(name='login', description="Login name",
                              required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    password = openapi.Parameter(name='password', description="Password",
                              required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)      
    @swagger_auto_schema(tags=['/api/v1/accountMgmt/apiKey'], operation_description="Get user API-Key with login credentials",
                         manual_parameters=[login, password])
    #@verifyUserRole(webPage=Vars.webpage, action='getApiKey', exclude=['engineer'])
    def post(self, request):
        """
        Description:
           Get user API-Key
        
        POST /api/v1/system/accountMgmt/apiKey?login=<login>&password=<password>
        
        Replace <login> and <password>
        
        Parameter:
            login: The login name
            password: The login password
        
        Examples:
            curl -X POST 'http://192.168.28.10:28028/api/v1/system/accountMgmt/apiKey?login=admin&password=admin'
            
            curl -d "login=admin&password=admin" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.10:28028/api/v1/system/accountMgmt/apiKey
            
            curl -d '{"login": "admin", "password": "admin"}' -H "Content-Type: application/json" -X POST http://192.168.28.10:28028/api/v1/system/accountMgmt/apiKey
                      
        Return:
            testcase details
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        login = None
        password = None
        apiKey = None
        errorMsg = None
        status = 'success'
        statusCode =  HtmlStatusCodes.success

        # /api/v1/accountMgmt?login=admin&password=admin
        if request.GET:
            try:
                login = request.GET.get('login')
                password = request.GET.get('password')
                
            except Exception as error:
                errorMsg = f'Expecting parameter login and password, but got: {request.GET}'
                return Response(data={'status': 'failed', 'error': errorMsg}, status=HtmlStatusCodes.error)
            
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                login = request.data['login']
                password = request.data['password']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters login and password, but got: {request.data}'
                status = 'failed'
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'login': login, 'password': password}
            restApi = '/api/v1/system/accountMgmt/apiKey'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetApiKeyFromRestApi')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                apiKey = response.json()['apiKey']
                
        else:
            for param in [('login', login), ('password', password)]:
                if param[1] is None:
                    return Response(data={'status': 'failed', 'errorMsg': f'The param {param[0]} is incorrect. Please correct the parameter'},
                                    status=HtmlStatusCodes.error)
            
            try:
                userDetails = AccountMgr().getUserDetails(key='loginName', value=login)

                if password == userDetails['password']:
                    apiKey = userDetails['apiKey']
                else:
                    errorMsg = f'Login name and password failed: {login} / {password}'
                    status = 'failed'
                    statusCode = HtmlStatusCodes.forbidden
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error

        return Response(data={'status': status, 'apiKey': apiKey, 'errorMsg': errorMsg}, status=statusCode)

