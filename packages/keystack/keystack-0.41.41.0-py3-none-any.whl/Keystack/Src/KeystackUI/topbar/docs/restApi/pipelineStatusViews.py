import os, sys, traceback
from glob import glob

from keystackUtilities import readYaml, readFile
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from topbar.settings.accountMgmt.views import AccountMgmt
from topbar.docs.restApi.pipelineViews import getTableData
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes

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
    webpage = 'pipelines'
       
       
class GetPipelineStatus(APIView):
    group     = openapi.Parameter(name='group', description="The name of the result group",
                                 required=False, default="Default", in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 
    playbook  = openapi.Parameter(name='playbook', description="Name of the Playbook",
                                 required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    pipelineId = openapi.Parameter(name='pipelineId', description="The pipeline timestamp ID to query", 
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(tags=['/api/v1/pipeline/status'], manual_parameters=[group, playbook, pipelineId], 
                         operation_description="Get pipeline status")
    @verifyUserRole()   
    def get(self, request):
        """
        Description:
            Get status of a pipeline
        
        GET /api/v1/pipeline/status
        
        Parameter:
            group:     The result group name
            playbook:  The playbook name
            pipelineId: The test timestamp session ID (folder)
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET 'http://192.168.28.7:8000/api/v1/pipeline/status?playbook=pythonSample&pipelineId=10-25-2022-16:33:54:783552_6639'
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "playbook=pythonSample&sessionId=09-29-2022-15:19:13:190045_awesomeTest" -H "Content-Type: application/x-www-form-urlencoded" -X GET http://192.168.28.7:8000/api/v1/pipeline/status 
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"playbook": "pythonSample", "pipelineId": "09-29-2022-15:19:13:190045_awesomeTest"}' -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/pipeline/status
                        
        Return:
            Session overall summary
        """
        sessionOverallSummary = {}
        errorMsg = None
        details = None
        sessionId = None
        sessionStatus = None
        playbook = None
        pipelineId = None
        user = AccountMgmt().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        # http://ip:port/staus?playbook=<playbook_name>&sessionId=<test_sessionId>
        if request.GET:
            try:
                group = request.GET.get('group', "Default")
                playbook = request.GET.get('playbook')
                pipelineId = request.GET.get('pipelineId')
            except Exception as errMsg:
                errorMsg = f'Expecting parameters: playbook & pipelineId, but got: {request.GET}'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getSession', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
            
        # JSON format
        if request.data:
            # <QueryDict: {'sessionId': <session_name>}
            try:
                group = request.data.get('group', 'Default')
                playbook = request.data['playbook']
                pipelineId = request.data['pipelineId']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters: playbook name & pipelineId, but got: {request.data}'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getPipelineStatus', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"group": group, "playbook": playbook, 'pipelineId': pipelineId}
            restApi = '/api/v1/pipeline/status'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetPipelineStatus')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error 
            else:
                playbook = response.json()['playbook'] 
                pipelineId = response.json()['sessionId'] 
                sessionStatus = response.json()['sessionStatus'] 
                details = response.json()['details']        
        else:            
            try:
                sessionStatusList = []
                sessions = f'{GlobalVars.keystackTestRootPath}/Results/DOMAIN={group}/PLAYBOOK={playbook}/{pipelineId}'
                sessionList = glob(sessions)

                for eachTestResult in sessionList:
                    overallSummary = f'{eachTestResult}/overallSummary.json'
                    sessionDetails = readYaml(overallSummary)
                    testResultTopLevelFolder = eachTestResult.split('/')[-1]
                    pipelineId = testResultTopLevelFolder
                    sessionStatus = sessionDetails['status']
                    details = sessionDetails
                        
            except Exception as errMsg:
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getPipelineStatus', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
        
        if details is not None:  
            return Response(data={'playbook': playbook, 'sessionId': pipelineId, 'sessionStatus': sessionStatus, 
                                  'details': details, 'status': 'success', 'error': None}, status=HtmlStatusCodes.success)
        else:
            return Response(data={'playbook': playbook, 'sessionId': pipelineId, 'sessionStatus': sessionStatus, 
                                  'details': details, 'status': 'failed', 'errorMsg': 'Failed to get session details. Check if the followings are correct: group,  playbook and pipelineId'}, status=HtmlStatusCodes.error)


class Pipelines(APIView):
    swagger_schema = None
    
    @verifyUserRole()
    def get(self, request):
        """
        Description: 
            Get CI/CT/CD pipelines. 
            For controller-to-controller usage

        GET /api/v1/pipelines
        
        Requirements:
           group <str>: The session group name. Default=Default
           view <str>:  current|archive. Default=current
           
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/pipelines
            
        Return:
            Sessions
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        sessions = None
        user = AccountMgmt().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        
        if request.GET:
            try:
                #group = request.GET.get('group', 'Default')
                view = request.GET.get('view', 'current')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getPipelines', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        if request.data:
            # <QueryDict: {'playbook': ['coolPlaybook'], 'sessionId': ['awesomeTest'], 'awsS3': ['true']}
            try:
                view = request.data.get('view', 'current')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getPipelines', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"view": view}
            restApi = '/api/v1/pipelines'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='Pipelines')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error 
            else:
                sessions = response.json()['sessions']  
                     
        else:        
            try:
                #sessions = SessionMgmt().getTableData(view, group)
                sessions = getTableData(view, group)
                
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                statusCode = HtmlStatusCodes.error
                                         
        return Response(data={'sessions':sessions, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
     
class Report(APIView):
    pipelinePath  = openapi.Parameter(name='pipelinePath',
                                      description="The pipeline result path",
                                      required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 

    @swagger_auto_schema(tags=['/api/v1/pipeline/report'], operation_description="Get a pipeline report",
                         manual_parameters=[pipelinePath],)    
    @verifyUserRole()
    def get(self, request):
        """
        Description: 
            Get a pipeline report summary

        GET /api/v1/pipeline/report
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/pipeline/report
            
        Return:
            A test report
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        user = AccountMgmt().getRequestSessionUser(request)

        if request.GET:
            try:
                pipelinePath = request.GET.get('pipelinePath', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getPipelineReport', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 
        
        if request.data:
            # <QueryDict: {'playbook': ['coolPlaybook'], 'sessionId': ['awesomeTest'], 'awsS3': ['true']}
            try:
                pipelinePath = request.data.get('pipelinePath', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getPipelineReport', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                                                             
        report = readFile(f'{pipelinePath}/testReport')
                
        return Response(data={'report': report, 'status': status, 'errorMsg': error}, status=statusCode)
