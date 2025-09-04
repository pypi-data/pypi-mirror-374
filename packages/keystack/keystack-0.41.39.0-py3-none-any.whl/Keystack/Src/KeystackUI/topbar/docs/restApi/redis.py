import traceback

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse, FileResponse, HttpResponse, HttpResponseRedirect

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole, authenticateLogin
from topbar.docs.restApi.accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from RedisMgr import RedisMgr
from globalVars import GlobalVars, HtmlStatusCodes


class Vars:
    webpage = 'redis'
    
    
class UpdateOverallSummaryData(APIView):
    def post(self,request):
        """
        Update Redis.
        Mainly used when a user runs CLI commands on the Linux host.
        The data needs to be transferred to the KeystackUI redis DB
        """
        keyName = request.data.get('keyName', None)
        data    = request.data.get('data', None)
        
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'keyName': keyName, 'data': data}
            restApi = '/api/v1/redis/updateOverallSummaryData'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='UpdateOverallSummaryData')   
        else:        
            try:
                if RedisMgr.redis:
                    RedisMgr.redis.write(keyName=keyName, data=data)
                                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdateOverallSummaryData', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status':status, 'errorMsg': errorMsg}, status=statusCode)
    


class UpdateEnvMgmt(APIView):
    def post(self,request):
        """
        Update docker Redis envMgmt .
        Mainly used when a user runs CLI commands on the Linux host.
        The data needs to be transferred to the KeystackUI redis DB
        """
        keyName = request.data.get('keyName', None)
        data    = request.data.get('data', None)
        
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'keyName': keyName, 'data': data}
            restApi = '/api/v1/redis/updateEnvMgmt'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='UpdateEnvMgmt')   
        else:        
            try:
                if RedisMgr.redis:
                    RedisMgr.redis.write(keyName=keyName, data=data)
                                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdateEnvMgmt', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status':status, 'errorMsg': errorMsg}, status=statusCode)
    

class ReadEnvMgmt(APIView):    
    def post(self,request):
        """
        Readdocker Redis envMgmt .
        Mainly used when a user runs CLI commands on the Linux host.
        The envMgmt data was transferred to the KeystackUI redis DB.
        This function reads the data from redis DB.
        """
        keyName = request.data.get('keyName', None)
        
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'keyName': keyName}
            restApi = '/api/v1/redis/readEnvMgmt'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='ReadEnvMgmt') 
            data = response.json()['data'] 
             
        else:        
            try:
                if RedisMgr.redis:
                    data = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReadEnvMgmt', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'data': data, 'status':status, 'errorMsg': errorMsg}, status=statusCode)
    