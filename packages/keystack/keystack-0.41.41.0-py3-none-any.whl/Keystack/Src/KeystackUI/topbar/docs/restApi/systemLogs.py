import json
import os
from pprint import pprint

from rest_framework.views import APIView
from rest_framework.response import Response

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes
from db import DB


class Vars:
    webpage = 'debug'
    
    
class GetLogMessageTopics(APIView):
    def post(self, request):
        """ 
        System logs: Get a dropdown menu of log topics to view 
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        logTopicDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/getLogMessageTopics'
            
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetLogMessageTopics')
            html = response.json()['logTopicDropdown']
        else:        
            try:
                logTitlesObj = DB.name.getDocuments(collectionName='logs', fields={})
                    
                from functools import reduce
                
                logTitlesList = list(reduce( lambda all_keys, rec_keys: all_keys | set(rec_keys), map(lambda d: d.keys(), logTitlesObj), set() ))
                logTitlesList.remove('_id')

                logTopicDropdown = '<div class="dropdown">'
                logTopicDropdown += "<a class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Select Log Topic</a>"
                logTopicDropdown += '<ul id="selectLogTopic" class="dropdown-menu dropdownSizeSmall" aria-labelledby="">'
                
                for logTopic in sorted(logTitlesList):                    
                    logTopicDropdown += f'<li class="mainFontSize textBlack paddingLeft20px">{logTopic}</li>'
                
                logTopicDropdown += '</ul></div>'
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                logTopicDropdown = ''
            
        return Response({'logTopicDropdown': logTopicDropdown}, status=statusCode)
    
    
class GetLogMessages(APIView):
    def post(self, request):
        """ 
        System logs: User selects the log webPage 
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        webPage = request.data.get('webPage', None)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'webPage': webPage}
            restApi = '/api/v1/system/getLogMessages'
            
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetLogMessages')
            if errorMsg:
                status = 'failed'
            else:
                html = response.json()['logs']
        else:        
            try:
                html = SystemLogsAssistant().getLogMessages(webPage=webPage)
                statusCode = HtmlStatusCodes.success
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
            
        return Response({'logs': html}, status=statusCode)
    

class DeleteLogs(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='deleteLogs', exclude=['engineer'])
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        logPage = request.data.get('webPage', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'webPage': logPage}
            restApi = '/api/v1/system/deleteLogs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteLogs')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        else:        
            try:
                SystemLogsAssistant().delete(logPage)
                
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
        
        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    