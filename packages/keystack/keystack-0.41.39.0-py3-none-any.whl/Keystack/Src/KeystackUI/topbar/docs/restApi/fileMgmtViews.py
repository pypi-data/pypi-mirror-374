import os, sys, subprocess, json, traceback
from re import search
from glob import glob
from time import sleep

from commonLib import createTestResultTimestampFolder, validatePlaybook
from keystackUtilities import convertStringToDict, getDeepDictKeys, readJson, readYaml, writeToJson, convertStrToBoolean, mkdir2, writeToFile
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from accountMgr import AccountMgr
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from globalVars import GlobalVars, HtmlStatusCodes
from db import DB

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
    webpage = 'fileMgmt'
    

class GetFileContents(APIView):
    swagger_schema = None

    def post(self, request, data=None):
        """
        Description:
           Internal helper function to get file contents.
        
        POST /api/v1/fileMgmt/getFileContents?filePath=<filePath>
        
        Parameter:
            filePath: The full path of the file to get the contents
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/fileMgmt/getFileContents=<filePath>
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "filePath=<full path>" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/fileMgmt/getFileContents
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"filePath": "fullPathFile"}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/fileMgmt/getFileContents
                        
        Return:
            None
        """     
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        fileContents = ''
        
        if request.GET:
            try:
                filePath = request.GET.get('filePath')
            except Exception as error:
                error = f'Expecting parameters filePath but got: {request.GET}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=HtmlStatusCodes.error)
        
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                # ['/opt/KeystackTests/Playbooks/qa/qa1.yml']
                filePath  = request.data['filePath']
            except Exception as errMsg:
                error = f'Expecting parameters filePath, but got: {request.data}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=HtmlStatusCodes.error)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"filePath": filePath}
            restApi = '/api/v1/fileMgmt/getFileContents'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetFileContents')
            if errorMsg:
                statusCode = HtmlStatusCodes.error
                status = 'failed'
            else:   
                fileContents = response.json()['fileContents']
                filePath = response.json()['fullPath']
        else: 
            try:   
                filename = filePath.split('/')[-1]

                for ignore in ['zip', 'pdf', 'bzip', 'bzip2']:
                    if ignore in filename:
                        return Response(data={'status': 'failed', 'errorMsg': f'Cannot open file type {ignore}: {filename}'}, status=HtmlStatusCodes.error)

                if os.path.exists(filePath):
                    # fileId = open(filePath)
                    # fileContents = fileId.read()
                    # fileId.close()
                    with open(filePath) as fileObj:
                        fileContents = fileObj.read()
                        
                contentType = 'application/json'
        
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='GetFileContents', 
                                          msgType='Error', msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'fullPath': filePath, 'fileContents': fileContents, 
                              'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class ModifyFile(APIView):
    swagger_schema = None

    @verifyUserRole(webPage=Vars.webpage, action='ModifyFile', exclude=['engineer'])
    def post(self, request, data=None):
        """
        Description:
           Internal helper function to modify a file.
        
        POST /api/v1/fileMgmt/modifyFile?filePath=<filePath>&textarea=<text>
        
        Parameter:
            filePath: The full path of the file to get the contents
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/fileMgmt/modifyFile=<filePath>&textarea=<text>
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "filePath=<full path>&textarea=<text>" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/fileMgmt/modifyFile
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"filePath": "fullPathFile" "textarea": text}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/fileMgmt/modifyFile
                        
        Return:
            None
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        htmlPlaybookGroups = ''
        
        if request.GET:
            try:
                filePath = request.GET.get('filePath')
                textarea = request.GET.get('textarea')
            except Exception as error:
                error = f'Expecting parameters filePath and textarea but got: {request.GET}'
                return Response(data={'errorMsg': error, 'status': 'failed'}, status=HtmlStatusCodes.error)
        
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                # ['/opt/KeystackTests/Playbooks/qa/qa1.yml']
                filePath  = request.data['filePath']
                textarea  = request.data['textarea']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters filePath and textarea, but got: {request.data}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=HtmlStatusCodes.error)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"filePath": filePath, 'textarea': textarea}
            restApi = '/api/v1/fileMgmt/modifyFile'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='ModifyFile')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error 
                   
        else:
            try:
                with open(filePath, 'w') as fileObj:
                    fileObj.write(textarea)
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='ModifyFile', msgType='Error', msg=errorMsg)

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
