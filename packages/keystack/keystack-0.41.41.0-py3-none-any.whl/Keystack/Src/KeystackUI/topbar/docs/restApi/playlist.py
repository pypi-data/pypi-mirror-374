import json, os, sys, traceback
from glob import glob

from rest_framework.views import APIView
from rest_framework.response import Response

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes

class Vars:
    webpage = 'playlist'
    
    
class GetPlaylist(APIView):
    # This is NOT in use.  It is here as a conceptual idea
    
    @verifyUserRole(webPage=Vars.webpage, action='GetPlaylist', exclude=['engineer'])
    def post(self, request):
        """
        Get sidebar playlist one at a time.
        The template base.html JS function getSidebarPlaylist() will increment counter.
        If counter == len(playList). set noMorePlaylist=True, then the function 
        will stop requesting for playlist.
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        counter = request.data.get('counter', None)
        noMorePlaylist  = True 
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        html = '' 
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"counter": counter}
            restApi = '/api/v1/playlist'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPlaylist')
            html = response.json()['playlist']
            noMorePlaylist = response.json()['noMorePlaylist']
        
        else:
            playList = glob(f'{GlobalVars.testcasesFolder}/*') 
            if counter == len(playList):
                noMorePlaylist = True
            else:
                noMorePlaylist = False
       
            for index, eachPlaylist in enumerate(playList):
                if index != counter:
                    continue
                
                playlistName = eachPlaylist.split('/')[-1]

                html += '<p class="mt-2 mb-2">'
                html += f'<a class="textBlack fontSize12px" href="/getPlaylistFolderFiles/{playlistName}" data-value="{playlistName}">'
                html += f'<i class="fa-regular fa-folder pl-2 pr-2"></i>{playlistName}'
                html += '</a>'           
                html += '</p>'
            
        return Response(data={'playlist': html, 'noMorePlaylist': noMorePlaylist, 
                              'status': status, 'errorMsg': errorMsg},
                        status=statusCode)


class GetPlaylistDetails(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetPlaylistDetails', exclude=['engineeer'])
    def post(self, request):
        """ 
        root: /opt/KeystackTests/Modules/CustomPythonScripts
            dir: ['Samples']
                files: []

        root: /opt/KeystackTests/Modules/CustomPythonScripts/Samples
            dir: ['Bringups', 'Teardowns', 'Scripts', 'Testcases', 'BridgeEnvParams']
                files: []

        root: /opt/KeystackTests/Modules/CustomPythonScripts/Samples/Bringups
            dir: []
                files: ['bringupDut1.yml', 'bringupDut2.yml']
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        
        playlist = request.data.get('playlist', None)
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        
        """
        <ul id="myUL">
            <li><span class="caret">Beverages</span>
                <ul class="nested">
                    <li>Water</li>
                    <li>Coffee</li>
                    <li><span class="caret">Tea</span>
                        <ul class="nested">
                            <li>Black Tea</li>
                            <li>White Tea</li>
                            <li><span class="caret">Green Tea</span>
                                <ul class="nested">
                                    <li>Sencha</li>
                                    <li>Gyokuro</li>
                                    <li>Matcha</li>
                                    <li>Pi Lo Chun</li>
                                </ul>
                            </li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ul>
        """
        class var:
            counter = 0
            html = '<ul id="menuTree">'
        
        def loop(path=None, init=False):
            """ 
            Create nested menu tree.  var.counter keeps track
            of the amount of nested menus so it knows the 
            amount of </li></ul> to close at the end.
            
            <li><span class="caret">Green Tea</span>
                <ul class="nested">
                    <li>Sencha</li>
                    <li>Gyokuro</li>
                    <li>Matcha</li>
                    <li>Pi Lo Chun</li>
            """
            if init:
                path = f'{GlobalVars.testcasesFolder}/{playlist}'

            var.html += f'<li><span class="caret"><i class="fa-regular fa-folder pr-2"></i>{path}</span>'
            var.html += '<ul class="nested">'
            var.counter += 1 
            
            for eachFile in glob(f'{path}/*'):
                if os.path.isfile(eachFile):
                    # Open the modifyFileModal and get the file contents                  
                    var.html += f'<li><a class="nav-link" href="#" onclick="getFileContents(this)" filePath="{eachFile}"  data-bs-toggle="modal" data-bs-target="#modifyFileModal"><i class="fa-regular fa-file pr-2"></i> {eachFile} </a></li>'
            
            for eachFolder in glob(f'{path}/*'):          
                if os.path.isdir(eachFolder):
                    loop(eachFolder)
                    var.html += '</li></ul>'


        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"playlist": playlist}
            restApi = '/api/v1/playlists/details'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPlaylistDetails') 
            var.html = response.json()['playlistDetails'] 
                          
        else:
            loop(init=True)
                        
            # Close all the nested menu opened tags    
            for x in range(0, var.counter):
                var.html += '</ul></li>'
                        
            var.html += '</ul>'
        
        return Response(data={'playlistDetails': var.html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
 

class GetTestcaseDetails(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetTestcaseDetails', exclude=['engineeer'])
    def post(self, request):
        """ 
        root: /opt/KeystackTests/Modules/CustomPythonScripts
            dir: ['Samples']
                files: []

        root: /opt/KeystackTests/Modules/CustomPythonScripts/Samples
            dir: ['Bringups', 'Teardowns', 'Scripts', 'Testcases', 'BridgeEnvParams']
                files: []

        root: /opt/KeystackTests/Modules/CustomPythonScripts/Samples/Bringups
            dir: []
                files: ['bringupDut1.yml', 'bringupDut2.yml']
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        
        testcase = request.data.get('testcase', None)
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        
        """
        <ul id="myUL">
            <li><span class="caret">Beverages</span>
                <ul class="nested">
                    <li>Water</li>
                    <li>Coffee</li>
                    <li><span class="caret">Tea</span>
                        <ul class="nested">
                            <li>Black Tea</li>
                            <li>White Tea</li>
                            <li><span class="caret">Green Tea</span>
                                <ul class="nested">
                                    <li>Sencha</li>
                                    <li>Gyokuro</li>
                                    <li>Matcha</li>
                                    <li>Pi Lo Chun</li>
                                </ul>
                            </li>
                        </ul>
                    </li>
                </ul>
            </li>
        </ul>
        """
        class var:
            counter = 0
            html = '<ul id="menuTree">'
        
        def loop(path=None, init=False):
            """ 
            Create nested menu tree.  var.counter keeps track
            of the amount of nested menus so it knows the 
            amount of </li></ul> to close at the end.
            
            <li><span class="caret">Green Tea</span>
                <ul class="nested">
                    <li>Sencha</li>
                    <li>Gyokuro</li>
                    <li>Matcha</li>
                    <li>Pi Lo Chun</li>
            """
            if init:
                path = f'{GlobalVars.testcasesFolder}/{testcase}'

            var.html += f'<li><span class="caret"><i class="fa-regular fa-folder pr-2"></i>{path}</span>'
            var.html += '<ul class="nested">'
            var.counter += 1 
            
            for eachFile in glob(f'{path}/*'):
                if os.path.isfile(eachFile):
                    # Open the modifyFileModal and get the file contents                  
                    var.html += f'<li><a class="nav-link" href="#" onclick="getFileContents(this)" filePath="{eachFile}"  data-bs-toggle="modal" data-bs-target="#modifyFileModal"><i class="fa-regular fa-file pr-2"></i> {eachFile} </a></li>'
            
            for eachFolder in glob(f'{path}/*'):          
                if os.path.isdir(eachFolder):
                    loop(eachFolder)
                    var.html += '</li></ul>'


        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"testcase": testcase}
            restApi = '/api/v1/testcases/details'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetTestcaseDetails') 
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                var.html = response.json()['testcaseDetails'] 
                          
        else:
            loop(init=True)
                        
            # Close all the nested menu opened tags    
            for x in range(0, var.counter):
                var.html += '</ul></li>'
                        
            var.html += '</ul>'
        
        return Response(data={'testcaseDetails': var.html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)