import os, sys, subprocess, json, re, traceback
from glob import glob
from time import sleep
from pathlib import Path

# /Keystack/KeystackUI/sidebar/sessionMgmt
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir.replace('/KeystackUI/restApi', ''))

from commonLib import validatePlaylistExclusions
from keystackUtilities import readYaml, readFile
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes

from django.views import View
from django.http import JsonResponse
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
    webpage = 'testcase'
       

class GetTestcaseDetails(APIView):
    testcasePath = openapi.Parameter(name='testcasePath', description="The testcase path beginning with /Modules",
                                     required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    
    @swagger_auto_schema(tags=['/api/v1/testcase/details'], operation_description="Get a testcase details from a playbook playlist",
                         manual_parameters=[testcasePath])
    def get(self, request):
        """
        Description:
           Get testcase details
        
        GET /api/v1/testcase/details?testcasePath=<testcasePath>
        
        Replace <testcasePath>
        
        Parameter:
            testcasePath: The testcase path beginning with /Modules/<moduleName>/
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET 'http://192.168.28.7:8000/api/v1/testcase/details?testcasePath=/Modules/LoadCore/Testcases/fullcoreBase.yml'
            
            curl -d "testcasePath=/Modules/LoadCore/Testcases/fullcoreBase.yml" -H "Content-Type: application/x-www-form-urlencoded" -X GET http://192.168.28.7:8000/api/v1/testcase/details
            
            curl -d '{"testcasePath": "/Modules/LoadCore/Testcases/fullcoreBase.yml"}' -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/testcase/details
                        
        Return:
            testcase details
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        testcaseData = {}
        testcasePath = None # User input
        errorMsg = None
        status = 'success'

        # /api/v1/playbook/testcase?testcasePath=/Modules/LoadCore/Testcases/fullcoreBase.yml
        if request.GET:
            try:
                testcasePath= request.GET.get('testcasePath')
            except Exception as error:
                errorMsg = f'Expecting parameter testcasePath, but got: {request.GET}'
                statusCode = HtmlStatusCodes.error
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                testcasePath = request.data['testcasePath']
            except Exception as errMsg:
                errorMsg = f'Expecting parameter testcasePath, but got: {request.data}'
                statusCode = HtmlStatusCodes.error
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'testcasePath':testcasePath}
            restApi = '/api/v1/results/nestedFolderFiles'
            response, errorMsg , status = executeRestApiOnRemoteController('gett', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestcaseDetails')
            if errorMsg:
                return Response({'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
            else:
                testcasePath = response.json()['testcase']
                testcaseData = response.json()['data']
  
        else: 
            if testcasePath is None:
                return Response(data={'errorMsg': f'Must include the parameter testcasePath', 'status': 'failed'}, status=HtmlStatusCodes.error)
                    
            if '.yml' not in testcasePath:
                testcasePath = f'{testcasePath}.yml'
            
            testcasePath = testcasePath.split(f'{GlobalVars.keystackTestRootPath}')[-1]  
        
            testcaseFullPath = f'{GlobalVars.keystackTestRootPath}/{testcasePath}'
            if os.path.exists(testcaseFullPath) == False:
                errorMsg = f'Testcase path not found: {testcaseFullPath}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=HtmlStatusCodes.error)

            try:
                testcaseData = readYaml(testcaseFullPath)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error

        return Response(data={'testcase': testcasePath, 'data': testcaseData, 
                              'status': status, 'errorMsg': errorMsg}, status=statusCode)
 

class GetTestcasesInternal(APIView):
    swagger_schema = None

    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            Get a list of testcase yml files from the selected playbook
            for modifying testcase params
        
        POST /api/vi/testcase/get
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:28028/api/v1/testcase/get
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:28028/api/v1/testcase/get
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:28028/api/v1/testcase/get
            
            session = requests.Session()
            response = session.request('post', 'http://192.168.28.7:28028/api/v1/testcase/get')
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        playbookName = request.data.get('playbook', None)
        
        class InternalVar:
            testcasesHtml = ''
                           
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'playbook': playbookName}
            restApi = '/api/v1/testcase/get'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetTestcasesInternal')  
            if errorMsg:
                status = 'failed'
                return Response({'testcases':InternalVar.testcasesHtml, 'status': 'failed', 'errorMsg': errorMsg}, 
                                 status=HtmlStatusCodes.error)
            else:
                InternalVar.testcasesHtml = response.json()['testcases']
            
        else:
            try:
                # playbookName includes the subfolder without the forward slash
                playbookFullPath = f'{GlobalVars.playbooks}/{playbookName}.yml'
                
                if os.path.exists(playbookFullPath) is False:
                    return Response({'testcases': '', 'status': 'failed',
                                     'errorMsg': f'No such playbook: {playbookFullPath}'
                                     }, status=HtmlStatusCodes.error)

                playbookData = readYaml(playbookFullPath)
                
                for stage in playbookData['stages'].keys():
                    for module in playbookData['stages'][stage]['tasks']:
                        # {'/Modules/Demo': {'enable': True, 'env': 'bypass', 'playlist': ['/Modules/Demo/Samples/Bringups']}}
                        for moduleName, moduleProperties in module.items():

                            InternalVar.testcasesHtml += f'&ensp;<strong>Stage:&ensp;{stage} &emsp; Module:&ensp;{moduleName}</strong><br>'
                            
                            modulePlaylist = moduleProperties.get('playlist', [])
                            playlistExclusions = moduleProperties.get('playlistExclusions', [])
                            
                            # excludeTestcases: Full path testcase yaml files
                            problems, excludeTestcases = validatePlaylistExclusions(playlistExclusions)
                            InternalVar.testcasesHtml += '<ul class="listNoBullets">'
                                                                                      
                            # modulePlaylist are <testcase>.yml files
                            for testcasePath in modulePlaylist:
                                # testcasePath: /Modules/Demo/Samples/Testcases/Bringups
                                #               /opt/KeystackTests/Modules/Demo/Samples/Testcases/runPytest.yml
                                
                                regexMatch = re.search('.*(Modules|Testcases/.*)', testcasePath)
                                if regexMatch:
                                    testcaseFullPath = f'{GlobalVars.keystackTestRootPath}/{regexMatch.group(1)}'
                                else:
                                    print(f'GetTestcasesInternal() error: Playbook playlist must be in {GlobalVars.keystackTestRootPath}/Modules or {GlobalVars.keystackTestRootPath}/Testcases. Not: {testcaseFullPath}')
                                    continue
                                
                                if Path(testcaseFullPath).is_dir():
                                    # Run all file in folders and subfolders
                                    
                                    for root, dirs, files in os.walk(testcaseFullPath):
                                        # root ex: starting_path/subFolder/subFolder
                                        if files:
                                            # Store files in numerical/alphabetic order
                                            for eachFile in sorted(files):
                                                if bool(re.search('.*(yml|yaml)$', eachFile)) is False:
                                                    continue
                                                
                                                if root[-1] == '/':
                                                    eachFile = f'{root}{eachFile}'
                                                else:
                                                    eachFile = f'{root}/{eachFile}'
                                                    
                                                # Testcases/Nokia/nokia.yml
                                                currentFilename = eachFile.split('/')[-1]
                                            
                                                if eachFile in excludeTestcases:
                                                    continue
                                                
                                                if bool(re.search('.*(#|~|backup|readme|__init__|pyc)', currentFilename, re.I)):
                                                    continue

                                                InternalVar.testcasesHtml += f'<li>&ensp;&ensp;<a href="#" data-bs-toggle="modal" data-bs-target="#showTestcasesForModifyingModal" onclick=getTestcaseContents("{eachFile}")>{eachFile}</a>&ensp;&ensp;</li>'                   
                                else:
                                    if bool(re.search('.*(yml|yaml)$', testcaseFullPath)) is False:
                                        continue
                                    
                                    if testcasePath in excludeTestcases:
                                        continue

                                    InternalVar.testcasesHtml += f'<li>&ensp;&ensp;<a href="#" data-bs-toggle="modal" data-bs-target="#showTestcasesForModifyingModal" testcaseFullPath={testcaseFullPath} onclick=getTestcaseContents("{testcaseFullPath}")>{testcaseFullPath}</a>&ensp;&ensp;</li>'
                            
                            InternalVar.testcasesHtml += '</ul><br>'
                                                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestcasesInternal', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'testcases':InternalVar.testcasesHtml, 'errorMsg': errorMsg, 'status': 'success'}, status=statusCode)



        
'''    
class GetContents(APIView):
    swagger_schema = None

    @verifyUserRole()
    def post(self, request, data=None):
        """
        Description:
            Internal usage only
            Get testcase contents for modifying configs
        
        POST /api/vi/testcase/contents
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:28028/api/v1/testcase/contents
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:28028/api/v1/testcase/contents
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:28028/api/v1/testcase/contents
            
            session = requests.Session()
            response = session.request('post', 'http://192.168.28.7:28028/api/v1/testcase/contents')
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        remoteController = request.data.get('remoteController', None)
        mainControllerIp, remoteControllerIp, ipPort = getMainAndRemoteControllerIp(request, remoteController)
          
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/testcase/contents'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, ipPort, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetContents')  
            if errorMsg:
                status = 'failed'
                return Response({'testcase': '', 'status': 'failed', 'errorMsg': errorMsg}, 
                                 status=HtmlStatusCodes.error)
            else:
                testcaseData = response.json()['testcaseContents']
            
        else:
            try:
                testcaseFullPath = request.data.get('testcaseFullPath', None)
                
                if os.path.exists(testcaseFullPath) is False:
                    return Response({'testcases': '', 'status': 'failed',
                                     'errorMsg': f'No testcase yml file: {testcaseFullPath}'
                                     }, status=HtmlStatusCodes.error)

                testcaseData = readFile(testcaseFullPath)
                                                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetContents', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'testcaseContents': testcaseData,
                              'errorMsg': errorMsg, 'status': 'success'}, status=statusCode)
'''    