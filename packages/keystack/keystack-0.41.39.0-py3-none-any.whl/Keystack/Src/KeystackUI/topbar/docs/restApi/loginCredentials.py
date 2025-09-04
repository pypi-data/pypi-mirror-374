import json, traceback

from rest_framework.views import APIView
from rest_framework.response import Response

from keystackUtilities import readFile, writeToFile
from globalVars import GlobalVars, HtmlStatusCodes
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import  verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp

class Vars:
    webpage = 'loginCredentials'
    

class LoginCredentials(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='view', adminOnly=True)
    def get(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        loginCredentialsData = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/loginCredentials'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='LoginCredentials')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                loginCredentialsData = response.json()['settings']

        else:         
            try:
                loginCredentialsFile = f'{GlobalVars.keystackSystemPath}/.loginCredentials.yml'
                loginCredentialsData = readFile(loginCredentialsFile)
                            
            except Exception as errMsg:
                statusCode = HtmlStatusCodes.error
                errorMsg = str(errMsg)
                status = 'failed'
        
        return Response(data={'settings': loginCredentialsData, 
                              'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    @verifyUserRole(webPage=Vars.webpage, action='modify', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        textarea = request.data.get('textarea', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'textarea': textarea}
            restApi = '/api/v1/system/loginCredentials'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='LoginCredentials')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error

        else:  
            try:
                loginCredentialsFile = f'{GlobalVars.keystackSystemPath}/.loginCredentials.yml'
                writeToFile(loginCredentialsFile, textarea, mode='w', printToStdout=False)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='modify', msgType='Success',
                                          msg='', forDetailLogs='')              
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='modify', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))  
        
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
