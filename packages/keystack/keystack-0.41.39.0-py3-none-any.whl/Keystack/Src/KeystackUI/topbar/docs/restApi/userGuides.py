import os, traceback
from pprint import pprint

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes
from keystackUtilities import readFile

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework import viewsets

class Vars:
    webpage = 'userGuides'
    
    
class UserGuidesMenu(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetUserGuidesMenu')
    def post(self, request):
        """
        Description:
           Sidebar menu
        
        POST /api/v1/userGuides/getMenu
        """    
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/userGuides/getMenu'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='UserGuidesMenu')    
        else:
            try:
                # /opt/Keystack/Src/KeystackUI/topbar/docs/restApi
                currentDir = os.path.abspath(os.path.dirname(__file__))
                docsRootDirectory = currentDir.replace('/Src/KeystackUI/topbar/docs/restApi', '')
                excludeDocs = ['Installation', 'Remote Controller', 'App Store']
                menuDict = {}
                
                docsLevelPriorityFiles = ['Keystack Overview',
                                          'Features',
                                          'Installation',
                                          'User And Domain Mgmt',
                                          'Test Parameters',
                                          'CLI',
                                          'Scripts',
                                          'Login Credentials',
                                          'Pytest Sample',
                                          'Remote Controller',
                                          'App Store']
                
                def helper(root, files, priorityFiles, excludeFiles):
                    for docsLevelFile in priorityFiles:
                        if docsLevelFile[0] in ['.', '#']:
                            continue
                        
                        if docsLevelFile[-1] in ['~']:
                            continue
                                                    
                        if docsLevelFile in files:
                            docName = docsLevelFile.split('/')[-1]
                            if docName not in excludeFiles:
                                index = files.index(docsLevelFile)
                                files.pop(index)
                                menuDict[root]['docs'].append(f'{root}/{docsLevelFile}')

                    # Get the remaining docs level files and put at the end of the list
                    for docsLevelFile in files:
                        if docsLevelFile[0] in ['.', '#']:
                            continue
                        
                        if docsLevelFile[-1] in ['~']:
                            continue
                        
                        docName = docsLevelFile.split('/')[-1]
                        if docName not in excludeFiles:
                            menuDict[root]['docs'].append(f'{root}/{docsLevelFile}')
                        
                for root, dirs, files in os.walk(f'{docsRootDirectory}/Docs'):
                    ''' 
                    root: /opt/Keystack/Docs
                    root: /opt/Keystack/Docs/Playbook
                    root: /opt/Keystack/Docs/Env
                    root: /opt/Keystack/Docs/Test Cases
                    '''
                    menuDict[root] = {'docs': []}
                    
                    if root == f'{docsRootDirectory}/Docs':
                        helper(root, files, docsLevelPriorityFiles, excludeDocs)

                    if root == f'{docsRootDirectory}/Docs/Env':
                        helper(root, files, ['Env Overview'], [])

                    if root == f'{docsRootDirectory}/Docs/Test Cases':
                        helper(root, files, ['Testcases Overview'], [])
                        
                    if root == f'{docsRootDirectory}/Docs/Playbook':
                        helper(root, files, ['Playbook Overview'], [])
            
                html += '<div class="sidenav">'
                                
                for index, (docFilePath, docs) in enumerate(menuDict.items()):
                    subject = docFilePath.split('/')[-1]
                    #html += f'<button class="dropdown-btn">{subject}<i class="fa fa-caret-down"></i></button>'
                    html += f'<button class="dropdown-btn">{subject}</button>'
                    html += '<div class="dropdown-container">'
                    
                    for docFullPath in menuDict[docFilePath]['docs']:
                        docName = docFullPath.split('/')[-1]
                        html += f'<a class="lineHeight1-2" userGuide="{docFullPath}" href="#" onclick="getUserGuide(this)"><span class="textWhite">{docName}</span></a>'
                        
                    html += '</div>'
                    
                html += '</div>'
                
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='UserGuidesMenu', 
                                        msgType='Error', msg=errorMsg)

        return Response(data={'userGuidesMenu': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class UserGuide(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetUserGuide')
    def post(self, request):
        """
        Description:
           Show a user guide
        
        POST /api/v1/userGuides/getUserGuide
        """    
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        userGuide= request.data.get('userGuide', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        userGuideContents = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/userGuides/getUserGuide'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='UserGuide')    
        else:
            try:
                if os.path.exists(userGuide):
                    userGuideContents = readFile(userGuide)
                
            except Exception as errMsg:
                errorMsg= traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='UserGuide', 
                                        msgType='Error', msg=errorMsg)

        return Response(data={'userGuideContents': f'{userGuideContents}', 'status': status, 'errorMsg': errorMsg}, status=statusCode)