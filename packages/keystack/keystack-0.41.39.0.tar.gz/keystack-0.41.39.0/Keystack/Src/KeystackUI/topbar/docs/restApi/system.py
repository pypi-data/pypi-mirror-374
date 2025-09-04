import os, sys, json, traceback
from glob import glob
from re import search
from datetime import datetime
import tarfile

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from domainMgr import DomainMgr
from EnvMgmt import ManageEnv
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import HtmlStatusCodes
from sidebar.sessionMgmt.views import SessionMgmt
from keystackUtilities import readYaml, writeToYamlFile, readFile, writeToFile, removeFile, removeFolder, execSubprocessInShellMode, chownChmodFolder, getTimestamp
from commonLib import showVersion, syncTestResultsWithRedis
from globalVars import GlobalVars, HtmlStatusCodes
from db import DB
from RedisMgr import RedisMgr

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


class Vars:
    webpage = 'system'
       
       
currentDir = os.path.abspath(os.path.dirname(__file__))

class GetSystemSettings(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='view', adminOnly=True)
    def post(self, request):
        remoteControllerIp = request.data.get('remoteController', None)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)  
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        settingsData = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/getSystemSettings'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetSystemSettings')
            settingsData = response.json()['settings']
        else:        
            try:
                settingsData = readFile(GlobalVars.keystackSystemSettingsFile)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
        
        return Response({'settings': settingsData, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class ModifySystemSettings(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='modify', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)  
        user = AccountMgr().getRequestSessionUser(request)
        textarea = request.data.get('textarea', None)
        
        # import json
        # body = json.loads(request.body.decode('UTF-8'))
        # textarea = body['textarea']
        #user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'textarea': textarea}
            restApi = '/api/v1/system/modifySystemSettings'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='ModifySystemSettings')
        else:        
            try:
                writeToFile(GlobalVars.keystackSystemSettingsFile, textarea, mode='w')

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='modify', msgType='Success',
                                        msg='', forDetailLogs='')              
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='modify', msgType='Error',
                                        msg=f'Settings: {errMsg}', 
                                        forDetailLogs=traceback.format_exc(None, errMsg))  
        
        return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
     
class GetSystemPaths(APIView):
    @swagger_auto_schema(tags=['/api/v1/system/paths'], operation_description="Get paths from /etc/keystack",
                         manual_parameters=[],)
    def get(self, request):
        """
        Description: 
            Return a list of all the system paths from /etc/keystack.yml
        
        No parameters required

        GET /api/v1/system/paths
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/system/paths
            
        Return:
            A list of environments
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)  
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        systemPaths = ''
        
        # TODO: Need to set controller in central location in order to use rest apis

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/paths'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetSystemPaths')
            systemPaths = response.json()['systemPaths']    
        else:        
            try:
                if os.path.exists('/etc/keystack.yml'):
                    systemPaths = readYaml('/etc/keystack.yml')
                else:
                    systemPaths = None
                    errorMsg = 'Not found: /etc/keystack.yml'
                    status = 'failed'
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getSystemPaths', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
        
        return Response(data={'systemPaths':systemPaths, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class GetServerTime(APIView):
    def post(self, request):
        """ 
                timedatectl:
                
                    Local time: Tue 2023-03-21 13:44:35 PDT
                Universal time: Tue 2023-03-21 20:44:35 UTC
                        RTC time: Tue 2023-03-21 20:44:35
                        Time zone: America/Los_Angeles (PDT, -0700)
        System clock synchronized: yes
                    NTP service: active
                RTC in local TZ: no

        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)  
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        serverTime = ''
    
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/serverTime'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetServerTime')
            serverTime = response.json()['serverTime']
        else:
            try:
                # Use zdump /etc/localtime to get the local time. This will work for both
                # Linux mode and docker mode.  Docker will use UTC. Linux mode will use the local host time. 
                
                # (True, '/etc/localtime  Fri Mar 24 12:01:21 2023 PDT')

                localHostTime = execSubprocessInShellMode('zdump /etc/localtime', showStdout=False)[1]
                match = search('/etc/localtime +([a-zA-Z]+) +([a-zA-Z]+) +([0-9]+) +([0-9]+:[0-9]+:.*) +([^ ]+) (.*)', localHostTime)
                serverTime = f'{match.group(1)} {match.group(2)} {match.group(3)} {match.group(5)} {match.group(4)} {match.group(6)}'
                
                # UTC: serverTime: (True, 'Thu Mar 16 01:39:55 UTC 2023')
                # serverTimeLinux = keystackUtilities.execSubprocessInShellMode('date', showStdout=True)[1]
                # match = search('([a-zA-Z]+) +([a-zA-Z]+) +([0-9]+) +([0-9]+:[0-9]+:.*) +([^ ]+) (.*)', serverTimeLinux)
                # serverTime = f'{match.group(1)} {match.group(2)} {match.group(3)} {match.group(6)} {match.group(4)} {match.group(5)}'
                
                # timedatectl: (This doesn't work in docker ubuntu)
                # Local time: Tue 2023-03-21 13:47:04 PDT
                #serverTimeLinux = keystackUtilities.execSubprocessInShellMode('timedatectl', showStdout=False)[1]
                #regexp = search('.*Local time:\s+([a-zA-Z]+.*)\n', serverTimeLinux)
                #serverTime = regexp.group(1)
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
            
        return Response({'status':status, 'errorMsg': errorMsg, 'serverTime': serverTime}, status=statusCode)
    
class Ping(APIView):
    swagger_schema = None
    
    def post(self, request):
        """
        Description: 
            Internal use only.  Check if KeystackUI is alive.
            If it gets here, then return a 200 status code for success
        
        No parameters required

        POST /api/system/ping
        
        Example:
            curl -X POST http://192.168.28.7:8000/api/system/ping
            wget --no-check-certificate "https://192.168.28.10/api/system/ping"
            
        Return:
            A list of environments
        """
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        from commonLib import logDebugMsg
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class GetInstantMessages(APIView):
    def post(self, request):
        """
        Get today's instant messages from systemLogging.py.SystemLogAssistant()
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)  
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        webPage = request.data.get('webPage', None)
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'webPage': webPage}
            restApi = '/api/v1/system/getInstantMessages'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetInstantMessages')
            html = response.json()['instantMessages']
                
        else:        
            try:
                # The template informs which message topic to get messages from
                html = SystemLogsAssistant().getInstantMessages(webPage)
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=request.session['user'], webPage=webPage,
                                        action='GetInstantMessages', msgType='Error', 
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'instantMessages': html}, content_type='application/json', status=statusCode)


class VerifyVersion(APIView):
    def get(self, request):
        """
        Verify the Keystack framework version and the Keystack UI version
        
        Keystack could be installed as a local host pip install to use the CLI.
        Subsequently, there could be a docker container installation.
        These two could have a version mismatch.
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)  
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        keystackVersion = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/verifyVersion'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='VerifyVersion')
        else:
            try:
                keystackVersion, dockerContainerVersion = showVersion(stdout=False)
                    
                # if dockerContainerVersion:
                #     print(f'\nkeystack container version=={dockerContainerVersion}\n')
            
                #keystackVersion = f'Keystack version: {keystackVersion}<br>Docker container version: {dockerContainerVersion}'
                keystackVersion = f'Keystack version: {keystackVersion}<br>'
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=request.session['user'], webPage=Vars.webpage,
                                          action='VerifyVersion', msgType='Error', 
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'keystackVersion': keystackVersion, 'status': status, 'errorMsg': errorMsg}, content_type='application/json', status=statusCode)
    
    
class GetUserAllowedDomainsAndRoles(APIView):
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)  
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/getUserAllowedDomainsAndRoles'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetUserAllowedDomainsAndRoles')
        else:        
            try:
                # [('Communal', 'admin'), ('KeystackQA', 'admin')]
                userAllowedDomainsAndUserRole = DomainMgr().getUserAllowedDomainsAndRoles(user)

                userAllowedDomainList = ''
                for userAllowedDomain, userRole in userAllowedDomainsAndUserRole:
                    userAllowedDomainList += '<tr>'
                    userAllowedDomainList += f'<td class="textAlignCenter">{userAllowedDomain}</td>'
                    userAllowedDomainList += f'<td class="textAlignCenter">{userRole}</td>'
                    userAllowedDomainList += '</tr>'
                 
                userAllowedDomainList += '<tr></tr>'   
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                userAllowedDomainList = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetUserAllowedDomainsAndRoles', msgType='Error',
                                        msg=errMsg, 
                                        forDetailLogs=traceback.format_exc(None, errMsg))  
        
        return Response({'userAllowedDomainList': userAllowedDomainList, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
    
class SystemBackup(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='SystemBackup', exclude=['engineer'])     
    def post(self, request):    
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        backupFilename = request.data.get('backupFilename', None)
        if backupFilename is not None:
            backupFilename = backupFilename.replace(' ', '-')
            
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"backupFilename": backupFilename}
            restApi = '/api/v1/system/systemBackup'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SystemBackup')
        else:
            from bson.json_util import dumps

            dt = datetime.now()
            timestamp = f'{dt.month}-{dt.day}-{dt.year}_{dt.hour}_{dt.minute}'
            machine_id = execSubprocessInShellMode(command="cat /etc/machine-id")[1].strip()

            if backupFilename is None:
                backupFilename = timestamp
            else:
                backupFilename = f'{timestamp}-{backupFilename}'

            fullPathFolder = f'{GlobalVars.systemBackupPath}/{backupFilename}'
            
            # keystackDB-2-28-2025_15_21.gz
            # keystackSystem-2-28-2025_15_21.gz
            machineIdFile = f'{fullPathFolder}/machine_id.yaml'
            mongoDB = f'{fullPathFolder}/mongoDB.gz'
            keystackSystemFiles = f'{fullPathFolder}/keystackSystem.gz'
            keystackTestsFiles = f'{fullPathFolder}/keystackTests.gz'
            completeBackupTarFile = f'{fullPathFolder}.gz'
            
            SystemBackup.createFolderBackup(GlobalVars.systemBackupPath)
            chownChmodFolder(GlobalVars.systemBackupPath, user=GlobalVars.user, userGroup=GlobalVars.userGroup)
            SystemBackup.createFolderBackup(fullPathFolder)
            chownChmodFolder(fullPathFolder, user=GlobalVars.user, userGroup=GlobalVars.userGroup)

            writeToYamlFile(contents={'uuid': machine_id}, yamlFile=machineIdFile)
                            
            # KeystackSystem: Copy and tar everything in /opt/KeystackSystem except for: Apps, SystemBackup, MongoDB
            excludeDirs = ['Apps', 'SystemBackup', 'MongoDB']
            with tarfile.open(keystackSystemFiles, "w:gz") as keystackSystemTar:
                for file in os.listdir(GlobalVars.keystackSystemPath):
                    if 'MongoDB' in file: continue
                    if 'Apps' in file: continue
                    if 'SystemBackup' in file: continue
                     
                    addFile = f'{GlobalVars.keystackSystemPath}/{file}'   

                    # When decompressed, will create files and folder:
                    #    appStoreLocations.yml  customizeTestReport.yml  keystackSystem.gz  keystackSystemSettings.yml  
                    #    Logs  RestApiMods  ResultDataHistory  ServicesStagingArea
                    if os.path.isdir(addFile):
                        # addFile = The full path to the file to be added in the tar 
                        # file = just the file name
                        keystackSystemTar.add(addFile, arcname=file)
                        
                    if os.path.isfile(addFile):
                        keystackSystemTar.add(addFile, arcname=file)

            # KeystackTests
            '''
            with tarfile.open(keystackTestsFiles, "w:gz") as keystackTestsTar:
                for file in os.listdir(GlobalVars.keystackTestRootPath):
                    addFile = f'{GlobalVars.keystackTestRootPath}/{file}'   

                    # When decompressed, will create files and folder:
                    #    appStoreLocations.yml  customizeTestReport.yml  keystackSystem.gz  keystackSystemSettings.yml  
                    #    Logs  RestApiMods  ResultDataHistory  ServicesStagingArea
                    if os.path.isdir(addFile):
                        # addFile = The full path to the file to be added in the tar 
                        # file = just the file name
                        keystackTestsTar.add(addFile, arcname=file)
                        
                    if os.path.isfile(addFile):
                        keystackTestsTar.add(addFile, arcname=file)
            '''
                                    
            # MongoDB collections
            with tarfile.open(mongoDB, "w:gz") as tar:
                for collectionName in DB.name.getAllCollections():
                    addFile = f'{fullPathFolder}/{collectionName}.json'
                    
                    with open(addFile, 'w') as file:
                        cursor = DB.name.getDocuments(collectionName, fields={})
                        # using bson dumps to convert json to bson
                        json.dump(json.loads(dumps(cursor)), file)
                        
                    relativePath = os.path.relpath(addFile, fullPathFolder)
                    tar.add(addFile, arcname=collectionName)
                    removeFile(f'{fullPathFolder}/{collectionName}.json')
            
            # Tar the main folder containing all backups
            with tarfile.open(completeBackupTarFile, "w:gz") as completeTar:
                completeTar.add(machineIdFile)
                
                for file in os.listdir(fullPathFolder):
                    addFile = f'{fullPathFolder}/{file}' 
                    completeTar.add(addFile, arcname=file)
        
            # Remove the untarted folder
            removeFolder(fullPathFolder)
    
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)  
    
    @staticmethod
    def createFolderBackup(fullPathFolder):
        if not os.path.exists(fullPathFolder):
            os.makedirs(fullPathFolder)

    @staticmethod
    def makeTarFile(outputFilename, sourceDir):
        ''' 
        Open: w | w: | w:gz | w:bz2 | w:xz
        Create tarfile: x | x: | x:bz2 | x:xz | 
        '''
        relativePath = os.path.relpath(outputFilename, sourceDir)
        
        with tarfile.open(outputFilename, "w:gz") as tar:
            for filename in sourceDir:
                tar.add(filename, argname=relativePath)
    
    @staticmethod
    def extractTarFile(tarGzFile, extractPath):
        with tarfile.open(tarGzFile, 'r:gz') as tar:
            tar.extractall(extractPath)
  

class SystemRestore(APIView):
    """
    Restore a system backup file
    """
    @verifyUserRole(webPage=Vars.webpage, action='SystemRestore', exclude=['engineer']) 
    def post(self, request):    
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        backupFilename = request.data.get('backupFilename', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"backupFilename": backupFilename}
            restApi = '/api/v1/system/systemRestore'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SystemRestore')
        else:
            sourceFileFullPath = f'{GlobalVars.systemBackupPath}/{backupFilename}'
            #  /opt/KeystackSystem/SystemBackups/restoreBackupTemp/<timestamp>
            systemBackupTempPath = f'{GlobalVars.systemBackupTempPath}/{getTimestamp()}'
        
            if os.path.exists(sourceFileFullPath) is False:
                return Response(data={'status': 'failed', 'errorMsg': f'Backup file not in expected location: {sourceFileFullPath}'}, status=statusCode) 

            # extract: /opt/KeystackSystem/SystemBackups/2-28-2025_16_40.gz -> /opt/KeystackSystem/SystemBackups/restoreBackupTemp/04-03-2025-15:02:18:204991 
            SystemRestore.extract(sourceFileFullPath, systemBackupTempPath)
            SystemRestore.restore(systemBackupTempPath, user)
            removeFolder(systemBackupTempPath)
            
            if RedisMgr.redis:
                DomainMgr().dumpDomainDataToRedis()
                DomainMgr().createDefaultDomain()
                syncTestResultsWithRedis()
                ManageEnv().syncTestcaseEnvMgmt()
                AccountMgr().syncAccountsWithRedis()
     
        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SystemRestore', msgType='Info',
                                  msg=f'System backup restored: {backupFilename}')
                        
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)  
    
    @staticmethod
    def extract(sourceFileFullPath, systemBackupTempPath):
        ''' 
        Open for reading: r | r:* | r: | r:gz | r:bz2 | r:xz
        '''
        if os.path.exists(sourceFileFullPath):
            with tarfile.open(sourceFileFullPath, "r") as tf:
                tf.extractall(path=systemBackupTempPath)

    @staticmethod
    def convert_json_to_bson(json_data):
        """
        This function is not in used currently
        
        Converts JSON data to BSON format.

        Args:
            json_data (str or dict): JSON data as a string or a Python dictionary.

        Returns:
            bytes: BSON representation of the JSON data.
        """
        from bson import BSON
        from bson.json_util import dumps, loads
        
        if isinstance(json_data, str):
            # Parse JSON string to a Python dictionary
            data_dict = loads(json_data)
        elif isinstance(json_data, dict):
            data_dict = json_data
        else:
            raise TypeError("Input must be a JSON string or a dictionary.")

        # Convert the Python dictionary to BSON
        bson_data = BSON.encode(data_dict)
        return bson_data

    
    @staticmethod
    def restore(systemBackupTempPath, user):
        """ 
        systemBackupTempPath:  /opt/KeystackSystem/SystemBackups/restoreBackupTemp/<timestamp>
        
        MongoDB:
           accountMgmt  envLoadBalanceGroups  keystackMisc  logs       scheduler
           domains      envMgmt               labInventory  portGroup  utilization
        
        KeystackSystem:
           appStoreLocations.yml    keystackSystemSettings.yml  RestApiMods        ServicesStagingArea
           customizeTestReport.yml  Logs                        ResultDataHistory
        
        2-28-2025_16_8-hgee-backup.gz  keystackSystem.gz  mongoDB.gz
        """  
        from bson import json_util
                
        mongoDBTarFile = f'{systemBackupTempPath}/mongoDB.gz'
        keystackSystemTarFile = f'{systemBackupTempPath}/keystackSystem.gz'
        keystackTestsTarFiles = f'{systemBackupTempPath}/keystackTests.gz'
        mongoDBTempPath = f'{systemBackupTempPath}/{getTimestamp()}'
        
        os.makedirs(mongoDBTempPath)
        SystemRestore.extract(mongoDBTarFile, mongoDBTempPath)
        SystemRestore.extract(keystackSystemTarFile, GlobalVars.keystackSystemPath)
        #SystemRestore.extract(keystackTestsTarFiles, GlobalVars.keystackTestRootPath)
        
        localHostMachineId = execSubprocessInShellMode(command="cat /etc/machine-id")[1].strip()
        machineIdFile = f'{systemBackupTempPath}/machine_id.yaml'
        systemBackFromMachineId = readYaml(machineIdFile)
        
        isMachineIdTheSame = True
        if localHostMachineId != systemBackFromMachineId['uuid']:
            isMachineIdTheSame = False
        
        # if isMachineIdTheSame == False:
        #     SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SystemRestore', msgType='Failed',
        #                               msg=f'The saved system backup file is from a different machine')
            
        # with open(labInventoryJson,'rb') as f:
        #     json_data = bson.decode_all(f.read())
        
        for bsonFileFullPath in glob(f'{mongoDBTempPath}/*'):
            with open(bsonFileFullPath,'rb') as f:
                content = f.read()
                json_data = json_util.loads(content)
            
            collectionName = bsonFileFullPath.split('/')[-1]
            
            if DB.name.isCollectionExists(collection=collectionName):
                DB.name.deleteCollection(collectionName=collectionName)
                
            DB.name.insertMany(collectionName=collectionName, data=json_data)
            
        #bson_data = SystemRestore.convert_json_to_bson(json_data)
        # bson_data = json.loads(json_data)
        # bson_data = json_util.loads(json_data)
        #pprint(bson_data)
    

class GetBackupFilesTable(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetBackupFilesTable', exclude=['engineer']) 
    def post(self, request):    
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = None
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/getBackupFilesTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetBackupFilesTable')
        else:
            restoreBackupTempFolderName = GlobalVars.systemBackupTempPath.split('/')[-1]
            
            for file in os.listdir(GlobalVars.systemBackupPath):
                if restoreBackupTempFolderName in file:
                    continue
                
                # /api/v1/system/downloadBackupFile
                html += f'<tr>'
                html += f'<td><input type="checkbox" name="backupFileCheckbox" backupFilename="{file}" /></td>'
                html += f'<td class="textAlignLeft">{file}</td>'
                html += f'<td><button type="submit" class="btn btn-outline-primary" name="backupFilename" value="{file}"><i class="fas fa-cloud-arrow-down"></i></button></td>'
                html += f'<td><a class="restoreSystemBackup" systemBackupFile={file} data-bs-toggle="modal" data-bs-target="#restoreSystemBackupModal" href="#">Restore</a></td>'
                html += f'</tr>'                                
            
        return Response(data={'backupFilesHtml': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)  
    

class DownloadBackupFile(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DownloadBackupFile', exclude=['engineer']) 
    def post(self, request):    
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        backupFilename = request.POST.get('backupFilename')
        
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"backupFilename": backupFilename}
            restApi = '/api/v1/system/downloadBackupFile'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DownloadBackupFile')
        else:
            import mimetypes
            import zipfile
            from shutil import make_archive
            from django.http import JsonResponse, FileResponse, HttpResponse
            
            try:
                fullPath = f'{GlobalVars.systemBackupPath}/{backupFilename}'
                fileType, encoding = mimetypes.guess_type(fullPath)
                if fileType is None:
                    fileType = 'application/octet-stream'

                response = HttpResponse(open(fullPath, 'rb'))
                response['Content-Type'] = fileType
                response['Content-Length'] = str(os.stat(fullPath).st_size)
                if encoding is not None:
                    response['Content-Encoding'] = encoding
                    
                response['Content-Disposition'] = f'attachment; filename={backupFilename}'

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DownloadTestResults', msgType='Info',
                                          msg=f'Downloaded system backup file: {fullPath}')
                return response
            
            except Exception as errMsg:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DownloadTestResults', msgType='Error', 
                                        msg="Failed to download system backup file:\n{traceback.format_exc(None, errMsg)}", 
                                        forDetailLogs=traceback.format_exc(None, errMsg))

                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode) 
            

class UploadBackupFile(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='UploadBackupFile', exclude=['engineer'])
    def post(self, request):
        """
        Upload a backup file
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # <input id="uploadSystemBackupFileInput" name="uploadSystemBackupFile" type="file" accept=".gz" /><br><br>
        # 'uploadSystemBackupFile' is obtain from tne input name. Not from JS post
        uploadBackupFile = request.FILES.get('uploadSystemBackupFile', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"uploadBackupFile": uploadBackupFile}
            restApi = '/api/v1/system/uploadBackupFile'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='UploadBackupFile')
        else:        
            try:
                if not os.path.exists(GlobalVars.systemBackupPath):
                    os.makedirs(GlobalVars.systemBackupPath)

                # Store the imported file from memory into a temp folder
                from django.core.files.storage import FileSystemStorage
                
                FileSystemStorage(location=GlobalVars.systemBackupPath).save(uploadBackupFile.name, uploadBackupFile)
                
                if uploadBackupFile.split('.')[-1] != 'gz':
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UploadBackupFile', msgType='Error',
                                              msg=f'Upload backup file must have extension .gz',
                                              forDetailLogs='')
                    
                    return Response(data={'status': 'failed', f'Upload backup file must have extension .gz': errorMsg},
                                    status=statusCode)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UploadBackupFile', msgType='Info',
                                          msg=f'Successfully Uploaded backup file: {uploadBackupFile}',
                                          forDetailLogs='')
                    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UploadBackupFile', msgType='Error',
                                          msg=f'Upload system backup file failed:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg))
                 
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class DeleteBackupFiles(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteBackupFiles', exclude=['engineer'])
    def post(self, request):
        """
        Upload a backup file
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        backupFiles = request.data.get('backupFiles', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"backupFiles": backupFiles}
            restApi = '/api/v1/system/deleteBackupFiles'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteBackupFiles')
        else:        
            try:
                for backupFile in backupFiles:
                    backupFileFullPath = f'{GlobalVars.systemBackupPath}/{backupFile}'
                    if os.path.exists(backupFileFullPath):
                        removeFile(backupFileFullPath)
                    
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteBackupFiles', msgType='Success',
                                          msg=f'{backupFiles}',
                                          forDetailLogs='')
                    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                print(errorMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteBackupFiles', msgType='Error',
                                          msg=f'{backupFiles}<br>{errorMsg}<br>{traceback.format_exc(None, errMsg)}',
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
                            
class WebsocketDemo(View):
    def get(self, request):
        return render(request, 'realtimeLogs.html') 