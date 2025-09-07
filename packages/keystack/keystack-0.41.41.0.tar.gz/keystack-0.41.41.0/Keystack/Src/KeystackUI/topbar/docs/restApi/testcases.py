import os, traceback
from glob import glob

from rest_framework.views import APIView
from rest_framework.response import Response

from systemLogging import SystemLogsAssistant
from accountMgr import AccountMgr
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes
from db import DB


class Vars:
    webpage = 'testcases'
    

class GetTestcaseGroupFolders(APIView):
    def post(self, request):
        """ 
        Sidebar Testcases menu
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        html = ''
        doOnce = True
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/testcases'
            
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetTestcaseGroupFolders')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                html = response.json()['testcasesHtml']
                
        else:        
            try:
                testcaseDetails = '<a href="/testcases/show" class="collapse-item pl-0 pt-3 pb-3 textBlack fontSize12px"><strong>Testcase Details</strong></a>'
                
                for testcaseGroup in glob(f'{GlobalVars.testcasesFolder}/*') :
                    if os.path.isfile(testcaseGroup):
                        if doOnce:
                            doOnce = False
                            testcaseGroupName = testcaseGroup.split(f'{GlobalVars.testcasesFolder}/')[-1]
                            html += '<p class="mt-2 mb-2">'
                            html += f'<a class="textBlack fontSize12px" href="/getTestcaseFiles" data-value="">'
                            html += f'<i class="fa-regular fa-folder pl-2 pr-2"></i>'
                            html += '</a>'           
                            html += '</p>'   

                    if os.path.isdir(testcaseGroup):
                        testcaseGroupName = testcaseGroup.split(f'{GlobalVars.testcasesFolder}/')[-1]
                        html += '<p class="mt-2 mb-2">'
                        html += f'<a class="textBlack fontSize12px" href="/getTestcaseFiles/{testcaseGroupName}" data-value="{testcaseGroupName}">'
                        html += f'<i class="fa-regular fa-folder pl-2 pr-2"></i>{testcaseGroupName}'
                        html += '</a>'           
                        html += '</p>'
                        
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                html = ''
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetTestcaseGroupFolders', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 
                
            
        return Response(data={'testcasesHtml': html, 'status': status, 'errorMsg': errorMsg},
                        status=HtmlStatusCodes.success)
        

class GetTestcaseDetails(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetTestcaseDetails', exclude=['engineeer'])
    def post(self, request):
        """ 
        Get testcase tree folder/files
        
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
                    var.html += f'<li><a class="nav-link" href="#" onclick="getFileContents(this)" filePath="{eachFile}"  data-bs-toggle="modal" data-bs-target="#modifyFileModal"><i class="fa-regular fa-file pr-2"></i>{eachFile}</a></li>'
            
            if testcase:
                # If testcase group is '', just show files in the folder /opt/KeystackTests/Testcases
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
 
