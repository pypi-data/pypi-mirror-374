import os, sys, traceback, httpx
from re import search
from glob import glob
from shutil import rmtree

from systemLogging import SystemLogsAssistant
from execRestApi import ExecRestApi
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from keystackUtilities import readFile, readYaml, convertStrToBoolean, execSubprocess, execSubprocessInShellMode, chownChmodFolder
from globalVars import HtmlStatusCodes, GlobalVars
from commonLib import getLoginCredentials

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
    webpage = 'apps'
    metadataFilename = 'readme'    

     
class GetApps(APIView):
    # @swagger_auto_schema(tags=['/api/v1/apps'], operation_description="Get a list of installed Apps",
    #                      manual_parameters=[])
    def post(self, request):
        """
        Description: 
            Return a list of all the installed apps
        
        No parameters required

        POST /api/v1/apps
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/apps
            
        Return:
            A list of installed apps
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        apps = []
        html = '<ul style="list-style-type:none";>'
        totalApps = 0

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/apps'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetInstalledApps')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                html = response.json()['apps']
  
        else:        
            try:
                appsPath = GlobalVars.appsFolder
                for index,app in enumerate(glob(f'{appsPath}/*')):
                    if os.path.isdir(app):
                        appName = app.split('/')[-1]
                        if appName in ["__pycache__"] or '_backup' in appName:
                            continue
                        
                        try:
                            currentVersion = ''
                            
                            # An app might not be from Github. It could be built-in
                            appRemoteUrl = None
                            
                            # Get the version from the readme file
                            output = execSubprocess(['grep', 'version:', f'{GlobalVars.appsFolder}/{appName}/readme'], stdout=False)
                            if output[0]:
                                currentVersion = output[1].replace('\n', '').replace('version:', '')
                             
                            # Get the app's github url for git pull   
                            #output2 = execSubprocess(['git', 'remote', 'get-url', 'origin'], cwd=f'{GlobalVars.appsFolder}/{appName}', stdout=True)
                            output2 = execSubprocess(['git', 'pull'], cwd=f'{GlobalVars.appsFolder}/{appName}', stdout=True)
                            if output2[0]:
                                appRemoteUrl = output2[1]
                        except:
                            pass
                        
                        apps.append(appName)
                        totalApps += 1
                        html += f'<li><input type="checkbox" name="appsCheckbox" value="{appName}" appName={appName} remoteUrl={appRemoteUrl} />&emsp;<a href="#" class="mainTextColor" app="{appName}" isAppInstalled="true" onclick="getAppDescription(this)">{appName}: {currentVersion}</a></li>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getInstalledApps', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
        
        html += '</ul>'
        return Response(data={'apps': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class RemoveApps(APIView):
    # apps = openapi.Parameter(name='apps', description="The name of the apps to remove in a list",
    #                     required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
        
    # @swagger_auto_schema(tags=['/api/v1/apps/remove'], operation_description="Remove installed Apps",
    #                      manual_parameters=[apps])
    @verifyUserRole(webPage=Vars.webpage, action='InstallApps', exclude=['engineer'])
    def post(self, request):
        """
        Description: 
            Remove a list of all the installed apps
        
        No parameters required

        POST /api/v1/apps/remove
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/apps/remove
            
        Return:
            None
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        apps = []

        if request.GET:
            # Rest APIs with inline params come in here
            try:
                selectedApps = request.GET.get('apps')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveApps', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                selectedApps = request.data['apps']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveApps', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"apps": selectedApps}
            restApi = '/api/v1/apps/remove'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='RemoveApps')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        
        else:
            try:    
                appsPath = GlobalVars.appsFolder
                for appName in selectedApps:
                    appPath = f'{appsPath}/{appName}'
                    if os.path.isdir(appPath) and appName not in ['AppRegistration']:
                        apps.append(appName)
                        rmtree(f'{GlobalVars.appsFolder}/{appName}')
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removeApps', msgType='Info',
                                          msg=apps, forDetailLogs='')                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removeApps', msgType='Error',
                                        msg=errorMsg, forDetailLogs='')
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
        
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetAppDescription(APIView):
    swagger_schema = None
    
    def post(self, request):
        """
        Description: 
            Installed App description
        
        app <str>: App name
        isInstalledApp <bool>: Is the app installed or online

        POST /api/v1/app/description
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/app/description
            
        Return:
            None
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        apps = []
        appDescr = ''
                     
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                app = request.GET.get('app')
                isAppInstalled = convertStrToBoolean(request.GET.get('isAppInstalled'))
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='appDescription', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                app = request.data.get('app', None)
                isAppInstalled = convertStrToBoolean(request.data['isAppInstalled'])
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='appDescription', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"app": app, 'isAppInstalled': isAppInstalled}
            restApi = '/api/v1/apps/description'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetAppDescription')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                appDescr = response.json()['description']
        
        else:
            try:                      
                appsPath = GlobalVars.appsFolder
                appMetadataFile = f'{appsPath}/{app}/{Vars.metadataFilename}'

                appDescr = '<p style="line-height:1;" class="marginLeft20px">'
                appDescr += f'appName: {app}<br><br>'
                            
                if os.path.exists(appMetadataFile) == False:
                    appDescr += 'No description found for this app'
                else:     
                    try:
                        appDescr += readFile(appMetadataFile) 
                            
                    except Exception as errMsg:
                        errorMsg = str(errMsg)
                        status = 'failed'
                        statusCode = HtmlStatusCodes.error
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='appDescription', msgType='Error',
                                                  msg=errorMsg, forDetailLogs='')
                
                appDescr +='</p>'
                    
            except Exception as errMsg:
                errorMsg = str (errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='appDescription', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
        
        return Response(data={'description': appDescr, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
     
class GetAvailableApps(APIView):
    # @swagger_auto_schema(tags=['/api/v1/apps/getAvailableApps'], operation_description="Get all available online apps",
    #                      manual_parameters=[])
    def post(self, request):
        """
        Description: 
            Return a list of available apps to install
        
        No parameters required

        GET /api/v1/apps/availableApps
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/getAvailableApps
            
        Return:
            A list of available apps
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        latestVersion = ''
        port = None
        restApiPath = None
        https = True
        appStoreUrls = []
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/apps/getAvailableApps'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetAvailableApps')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                apps = response.json()['availableApps']
                
        else:        
            try:
                # /opt//KeystackSystem/.loginCredentials should have a 'keystack' key
                # for universal usage
                credentials = getLoginCredentials(loginCredentialKey='keystack')
                if credentials:
                    githubAuthorizationToken = credentials.get('githubAccessToken', '')
                    if githubAuthorizationToken is None:
                        githubAuthorizationToken = ''
                else:
                    githubAuthorizationToken = ''

                if os.path.exists(GlobalVars.appStoreLocationsFile):
                    appStoreLocation = readYaml(GlobalVars.appStoreLocationsFile)                             
                    # https://api.github.com/repos/OpenIxia

                    # By default, github only allows 100 rest api hits.  
                    # To increase it to 5000 hits, include 'Authorization': '<github user token> in the headers
                    # 'Authorization': githubAuthorizationToken

                    apps = '<ul style="list-style-type:none";>'

                    for app in appStoreLocation:
                        # app: {'app': {'apiUrl': 'https://api.github.com/repos/OpenIxia/keystack-LoadCore', 'cloneUrl': 'https://github.com/OpenIxia/keystack-LoadCore.git'}}

                        eachAppStore = app['app']['apiUrl']
                        cloneUrl = app['app']['cloneUrl']
                                                
                        # https://api.github.com/repos/OpenIxia (OpenIxia)
                        orgs = eachAppStore.split('.com')[-1]
                    
                        # For dns using ip address
                        regexMatch2 = search('(http|https)://([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)(:[0-9]+)?(.+)', eachAppStore)
                        
                        if '.com' in eachAppStore:
                            regexMatch = search('(http|https)://(.+\.com)(/.+)', eachAppStore)
                            if regexMatch:
                                #dns = 'api.github.com'
                                if regexMatch.group(1) == 'http':
                                    https = False
                                    
                                dns = regexMatch.group(2)
                                # /repos/OpenIxia
                                restApiPath = regexMatch.group(3)
                                
                        elif regexMatch2:
                            if regexMatch2.group(3):
                                if regexMatch2.group(1) == 'http':
                                    https = False

                                # has ip port number
                                dns  = regexMatch2.group(2)
                                port = regexMatch2.group(3)
                                restApiPath = regexMatch2.group(4)
                            else:
                                if regexMatch2.group(1) == 'http':
                                    https = False
                                    
                                dns = regexMatch2.group(2)
                                restApiPath = regexMatch2.group(4)
                        else:
                            continue
                         
                        #  dns: api.github.com
                        restObj = ExecRestApi(ip=dns, port=port, 
                                              headers={'Accept':'application/vnd.github+json', 
                                                       'Accept': 'application/vnd.github.v3.raw',
                                                       'X-GitHub-Api-Version': '2022-11-28',
                                                       'Authorization': githubAuthorizationToken
                                                      },
                                              https=https)

                        # Ex: orgs = OpenIxia
                        #response = restObj.get(restApi=f'/orgs/{orgs}/repos?per_page=100')
                        response = restObj.get(restApi=orgs)
                        if response.status_code == 403:
                            raise Exception(f"Getting apps from github has reached its limit. Must wait 1 hour. If you don't want to wait for Github clearance, edit .loginCredentials.yml file, under keystack, add a valid github access token for githubAccessToken")
                        
                        repoName = response.json()['full_name']
                                                
                        releases = restObj.get(restApi=f'{restApiPath}/releases', silentMode=True,
                                               user=user, webPage=Vars.webpage, action='getAvailableApps')
                                                              
                        if response.status_code == 200:
                            # The lastest release is set as the first in the list
                            latestVersion = releases.json()[0]['tag_name']
                    
                        apps += f'<li>&ensp;&ensp;<input type="checkbox" name="appStoreAppsCheckbox" cloneUrl="{cloneUrl}" />&emsp;<a href="#" class="mainTextColor" app="{eachAppStore}" onclick="getAppStoreAppDescription(this)">{repoName} {latestVersion}</a></li>'
                        
                    apps += '<ul>'
                                            
            except Exception as errMsg:
                errorMsg = str(traceback.format_exc(None, errMsg))
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getAvailableApps', msgType='Error',
                                        msg=errorMsg, forDetailLogs='')
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)

        return Response(data={'availableApps': apps, 'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    

class GetAppStoreAppDescription(APIView):
    appName = openapi.Parameter(name='appBane', description="The name of the apps for the description",
                                required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
        
    @swagger_auto_schema(tags=['/api/v1/apps/getAppStoreAppDescription'], operation_description="Get the online app description",
                         manual_parameters=[appName])
    def post(self, request):
        """
        Description: 
            Get available App store app descriptions
        
        Parameter:
            appName <str>: The name of the app

        POST /api/v1/apps/getAppStoreAppDescription
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/getAppStoreAppDescription
            
        Return:
            A list of available apps
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        appDescription = '<span>No description provided</span>'

        if request.GET:
            # Rest APIs with inline params come in here
            try:
                # https://api.github.com/repos/OpenIxia/keystack-LoadCore
                app = request.GET.get('app')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getAppStoreAppDescription', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                app = request.data['app']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getAppStoreAppDescription', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"app": app}
            restApi = '/api/v1/apps/getAppStoreAppDescription'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetAppStoreAppDescription')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                appDescription = response.json()['appDescription'] 
                
        else:         
            try:    
                appNamme = ''
                tagVersion = ''
                
                # app: https://api.github.com/repos/OpenIxia/keystack-LoadCore
                appName = app.split('/repos/')[-1]
                dns = app.split('/repos')[0].split('//')[-1]
                restApi = app.split('.com')[-1]
                
                credentials = getLoginCredentials(loginCredentialKey='keystack')
                if credentials:
                    if 'githubAccessToken' in credentials:
                        githubAuthorizationToken = credentials['githubAccessToken'] 
                    else:
                        githubAuthorizationToken = None
                else:
                    githubAuthorizationToken = None
                
                # By default, github only allows 100 rest api hits.  
                # To increase it to 5000 hits, include 'Authorization': '<github user token> in the headers
                # 'Authorization': githubAuthorizationToken
                restObj = ExecRestApi(ip=dns, port=None, 
                                      headers={'Accept':'application/vnd.github+json', 
                                               'Accept': 'application/vnd.github.v3.raw',
                                               'X-GitHub-Api-Version': '2022-11-28'}, 
                                      https=True)

                # The latest tag release is in index 0:
                # [{'url': 'https://api.github.com/repos/OpenIxia/keystack-LoadCore/releases/107147874', 'assets_url': 'https://api.github.com/repos/OpenIxia/keystack-LoadCore/releases/107147874/assets', 'upload_url': 'https://uploads.github.com/repos/OpenIxia/keystack-LoadCore/releases/107147874/assets{?name,label}', 'html_url': 'https://github.com/OpenIxia/keystack-LoadCore/releases/tag/1.0.0', 'id': 107147874, 'author': {'login': 'hubogee', 'id': 4120328, 'node_id': 'MDQ6VXNlcjQxMjAzMjg=', 'avatar_url': 'https://avatars.githubusercontent.com/u/4120328?v=4', 'gravatar_id': '', 'url': 'https://api.github.com/users/hubogee', 'html_url': 'https://github.com/hubogee', 'followers_url': 'https://api.github.com/users/hubogee/followers', 'following_url': 'https://api.github.com/users/hubogee/following{/other_user}', 'gists_url': 'https://api.github.com/users/hubogee/gists{/gist_id}', 'starred_url': 'https://api.github.com/users/hubogee/starred{/owner}{/repo}', 'subscriptions_url': 'https://api.github.com/users/hubogee/subscriptions', 'organizations_url': 'https://api.github.com/users/hubogee/orgs', 'repos_url': 'https://api.github.com/users/hubogee/repos', 'events_url': 'https://api.github.com/users/hubogee/events{/privacy}', 'received_events_url': 'https://api.github.com/users/hubogee/received_events', 'type': 'User', 'site_admin': False}, 'node_id': 'RE_kwDOJrR6984GYvJi', 'tag_name': '1.0.0', 'target_commitish': 'main', 'name': 'Initial app release', 'draft': False, 'prerelease': False, 'created_at': '2023-06-04T16:06:01Z', 'published_at': '2023-06-04T16:09:15Z', 'assets': [], 'tarball_url': 'https://api.github.com/repos/OpenIxia/keystack-LoadCore/tarball/1.0.0', 'zipball_url': 'https://api.github.com/repos/OpenIxia/keystack-LoadCore/zipball/1.0.0', 'body': ''}]
                response = restObj.get(restApi=f'{restApi}/releases', silentMode=True,
                                       user=user, webPage=Vars.webpage, action='GetAppStoreAppDescription')
                
                if response.status_code == 200:
                    # The lastest release is set as the first in the list
                    tagVersion = response.json()[0]['tag_name']
                else:
                    pass
                        
                response = restObj.get(restApi=f'{restApi}/contents/readme', silentMode=True,
                                    user=user, webPage=Vars.webpage, action='getAvailableApps')
                if response.status_code == 200:
                    appDescription = f'<pre class="mainTextColor">avaialable app: {appName} {tagVersion}<br><br>{response.text}</pre>'
                else:
                    pass
                                                            
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getAppStoreAppDescription', msgType='Error',
                                        msg=errorMsg, forDetailLogs='')
        
        return Response(data={'appDescription': appDescription, 'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    

class UpdateApps(APIView):
    swagger_schema = None
    
    @verifyUserRole(webPage=Vars.webpage, action='UpdateApps', exclude=['engineer'])
    def post(self, request):
        """
        Description: 
            Update one or more installed apps
            Remove the current app first
        
        selectedApps: A list of full path apps

        POST /api/v1/apps/update
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/apps/update
            
        Return:
            None
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # Set to True to show command on the screen
        debug = False
        
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                selectedApps = request.GET.get('selectedApps', None)
            except Exception as errMsg:
                error = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdateApps', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                #selectedApps: [['keystack-IxLoad', 'https://github.com/OpenIxia/keystack-IxLoad.git']
                selectedApps = request.data.get('selectedApps', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdateApps', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"selectedApps": selectedApps}
            restApi = '/api/v1/apps/update'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='UpdateApps')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        
        else:            
            appsPath = GlobalVars.appsFolder
            failedToInstallApps = []
            successfullyUpdatedApps = []

            # selectedApps: [['keystack-IxLoad', 'https://github.com/OpenIxia/keystack-IxLoad.git']
            for appName, cloneUrl in selectedApps:
                # /opt/KeystackSystem/Apps/keystack-IxLoad
                appPath = f'{appsPath}/{appName}'

                # The app might not be from github.  Can't update using git.
                if cloneUrl and os.path.isdir(appPath):
                    # Use git describe --tags to check if the app was installed from github.
                    # If yes, then remove the current app and do a git clone to get the latest version.
                    
                    # Get the latest tag version from github repo using git fetch
                    execSubprocess(['git', 'fetch', '--tags'], cwd=appPath, stdout=debug)
                    output = execSubprocess(['git', 'describe', '--tags'], cwd=appPath, stdout=debug)
                    if output[0]:
                        currentVersion = output[1].replace('\n', '')

                        try:
                            execSubprocess(['sudo', 'mv', appPath, f'{appPath}_backupOriginal'], stdout=debug)

                            # execSubprocess(['git', 'clone', f'https://github.com/OpenIxia/keystack-{appName}.git', appName],
                            #                 cwd=f'{GlobalVars.keystackSystemPath}/Apps', stdout=debug)
                            execSubprocess(['git', 'clone', cloneUrl, appName],
                                            cwd=f'{GlobalVars.keystackSystemPath}/Apps', stdout=debug)
                            chownChmodFolder(appPath, GlobalVars.user, GlobalVars.userGroup, permission=770, stdout=debug)

                            if os.path.exists(appPath):
                                execSubprocess(['sudo', 'rm', '-rf', f'{appPath}_backupOriginal'], stdout=debug)
                                successfullyUpdatedApps.append(appName)
                            else:
                                execSubprocess(['sudo', 'mv', f'{appPath}_backupOriginal', appPath], stdout=debug)
                                failedToInstallApps.append(appName)

                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='updateApps', msgType='Success',
                                                      msg=f'git pull: {cloneUrl}', forDetailLogs='') 
                        except Exception as errMsg:
                            errorMsg = str(errMsg)
                            statusCode = HtmlStatusCodes.error
                            status = 'failed'
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='updateApps', msgType='Error',
                                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))   
                            return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
                    else:
                        failedToInstallApps.append(appName)
                        statusCode = HtmlStatusCodes.error
                        status = 'failed'
                        errorMsg = f'Getting the latest app version from github using "git fetch --tags" failed to retrieve the app tag info for the app. Maybe something wrong going out to github at the moment: {appName}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='updateApps', msgType='Error',
                                                  msg=errorMsg, forDetailLogs='')
  
                        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='updateApps', msgType='Info',
                                              msg=f'The app {appName} is not in Github. Could not update the app', forDetailLogs='') 
                                                      
            if len(successfullyUpdatedApps)  > 0:       
                # Getting out to there means apps were updated successfully               
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='updateApps', msgType='Info',
                                          msg=successfullyUpdatedApps, forDetailLogs='') 
                        
            if len(failedToInstallApps) > 0:
                statusCode = HtmlStatusCodes.error
                status = 'failed'
                errorMsg = f'Failed to update apps from the App store: "{failedToInstallApps}"'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='updateApps', msgType='Failed',
                                          msg=errorMsg, forDetailLogs='')

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class InstallApps(APIView):
    swagger_schema = None
    
    @verifyUserRole(webPage=Vars.webpage, action='InstallApps', exclude=['engineer'])
    def post(self, request):
        """
        Description: 
            Install app from App store if the app is not currently installed
        
        selectedApps: A list of apps to install

        POST /api/v1/apps/install
        
        Example:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST http://192.168.28.7:8000/api/v1/apps/install
            
        Return:
            None
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        apps = []
                
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                selectedApps = request.GET.get('selectedApps', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='InstallApps', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                selectedApps = request.data.get('selectedApps', None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='InstallApps', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"selectedApps": selectedApps}
            restApi = '/api/v1/apps/install'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeleteResults')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        
        else:             
            appsPath = GlobalVars.appsFolder
            appAlreadyExists = []
            successfullyInstalled = []

            # selectedApps: cloneUrl: https://github.com/OpenIxia/keystack-IxNetworkDataModel.git
            for cloneUrl in selectedApps:
                # /opt/KeystackSystem/Apps/LoadCore
                appName = cloneUrl.split('/')[-1].split('.git')[0]
                appPath = f'{appsPath}/{appName}'
                                
                if os.path.exists(appPath):
                    appAlreadyExists.append(appName)
                else:
                    try:
                        #gitClone = f'git clone https://github.com/openixia/{app} {appPath}'
                        gitClone = f'git clone {cloneUrl} {appPath}'
                        # (True, '')

                        output = execSubprocessInShellMode(gitClone, cwd=GlobalVars.appsFolder, showStdout=True)
                        execSubprocessInShellMode(f'git config --global --add safe.directory {appsPath}/{appName}',
                                                  cwd=f'{appsPath}/{appName}', showStdout=True)

                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='installApps', msgType='Info',
                                                  msg=gitClone, forDetailLogs='') 
                                                
                    except Exception as errMsg:
                        errorMsg = str(errMsg)
                        status = 'failed'
                        statusCode = HtmlStatusCodes.error
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='installApps', msgType='Error',
                                                  msg=errorMsg, forDetailLogs='')
                        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
                    
                    # Verify the installation
                    if os.path.exists(appPath):  
                        successfullyInstalled.append(appName)
                        chownChmodFolder(appPath, GlobalVars.user, GlobalVars.userGroup, permission=770, stdout=False)
            
            if len(successfullyInstalled) > 0:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='installApps', msgType='Info',
                                          msg=f'Successfully installed apps: {successfullyInstalled}', forDetailLogs='') 
                    
            if len(successfullyInstalled) == 0:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='installApps', msgType='Failed',
                                          msg=f'No apps were installed', forDetailLogs='')
                
            if len(appAlreadyExists) > 0:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='installApps', msgType='Warning',
                                          msg=f'These apps already exists. Use update apps instead if you want to reinstall or update the apps: {appAlreadyExists}', forDetailLogs='')
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    