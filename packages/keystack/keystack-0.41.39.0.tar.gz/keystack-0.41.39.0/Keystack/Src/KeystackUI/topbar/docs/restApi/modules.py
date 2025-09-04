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
    webpage = 'modules'
    
class GetModules(APIView):
    #@verifyUserRole(webPage=Vars.webpage, action='GetModules', exclude=['engineer'])
    def post(self, request):
        """
        Get sidebar modules one at a time.
        The template base.html JS function getSidebarModules() will increment counter.
        If counter == len(moduleList). set noMoreModule=True, then the function 
        will stop requesting for modules.
        """
        # body = json.loads(request.body.decode('UTF-8'))
        #counter = body['counter']
        # user = request.session['user']
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        counter = request.data.get('counter', None)
        noMoreModule  = True 
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        html = '' 
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"counter": counter}
            restApi = '/api/v1/modules'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetModules')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                html = response.json()['modulesHtml']
                noMoreModule = response.json()['noMoreModule']
        
        else:
            try:
                moduleList = glob(f'{GlobalVars.modules}/*')  
                if counter == len(moduleList):
                    noMoreModule = True
                else:
                    noMoreModule = False
        
                for index, eachModule in enumerate(moduleList):
                    if index != counter:
                        continue
                    
                    moduleName = eachModule.split('/')[-1]

                    html += '<p class="mt-2 mb-2">'
                    html += f'<a class="textBlack fontSize12px" href="/getModuleFolderFiles/{moduleName}" data-value="{moduleName}">'
                    html += f'<i class="fa-regular fa-folder pl-2 pr-2"></i>{moduleName}'
                    html += '</a>'           
                    html += '</p>'
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                
        return Response(data={'modulesHtml': html, 'noMoreModule':noMoreModule, 'status': status, 'errorMsg': errorMsg},
                        status=statusCode)


class GetModuleDetails(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetModuleDetails', exclude=['engineeer'])
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
        
        module = request.data.get('module', None)
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
                path = f'{GlobalVars.keystackTestRootPath}/Modules/{module}'

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
            params = {"module": module}
            restApi = '/api/v1/modules/details'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetModuleDetails') 
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                var.html = response.json()['moduleDetails'] 
                          
        else:
            loop(init=True)
                        
            # Close all the nested menu opened tags    
            for x in range(0, var.counter):
                var.html += '</ul></li>'
                        
            var.html += '</ul>'
        
        return Response(data={'moduleDetails': var.html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
 

