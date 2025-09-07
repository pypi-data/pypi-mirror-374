import os, sys
from glob import glob

# /Keystack/KeystackUI/restApi
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir.replace('/KeystackUI/restApi', ''))

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyApiKey
from topbar.docs.restApi.accountMgr import AccountMgr
from keystackUtilities import readFile

from sidebar.sessionMgmt.views import SessionMgmt
from django.conf import settings

from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets


class GlobalVars:
    """ 
    For logging the correct topics.
    To avoid human typo error, always use a variable instead of typing the word.
    """
    webpage = 'session'
       
 
class Report(APIView):
    sessionPath  = openapi.Parameter(name='sessionPath',
                                     description="The session test result path",
                                     required=True in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 

    @swagger_auto_schema(tags=['/api/v1/test/report'], operation_description="Get a test report",
                         manual_parameters=[sessionPath],)    
    @verifyApiKey
    def get(self, request):
        """
        Description: 
            Get a test report summary

        GET /api/v1/test/report
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/test/report
            
        Return:
            A test report
        """
        statusCode = 200
        status = 'success'
        envs = []
        error = None
        user = AccountMgr().getRequestSessionUser(request)
        
        if request.GET:
            try:
                sessionPath = request.GET.get('sessionPath', None)
            except Exception as errMsg:
                print('\nreport: request.GET error:', errMsg)
        
        if request.data:
            # <QueryDict: {'playbook': ['coolPlaybook'], 'sessionId': ['awesomeTest'], 'awsS3': ['true']}
            try:
                sessionPath = request.data.get('sessionPath', None)
            except Exception as errMsg:
                print('\nreport: request.data error:', errMsg)
                                                
        report = readFile(f'{sessionPath}/testReport')
        
        return Response(data={'report': report, 'status': status, 'errorMsg': error}, status=statusCode)

 