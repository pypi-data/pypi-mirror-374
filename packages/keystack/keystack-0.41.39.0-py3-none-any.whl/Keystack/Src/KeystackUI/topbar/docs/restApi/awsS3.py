import os, sys, json, traceback, subprocess
from glob import glob

from rest_framework.views import APIView
from rest_framework.response import Response

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
#from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from Services import Serviceware

from keystackUtilities import readYaml, readJson, execSubprocessInShellMode
from globalVars import GlobalVars, HtmlStatusCodes
  
class Vars:
    webpage = 'debug'
    

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)

class GetAwsS3Uploads(APIView):
    def post(self, request):
        """ 
        Get all the current AWS S3 uploads in the staging area 
        """
        try:
            body = json.loads(request.body.decode('UTF-8'))
            s3StagingFolder = Serviceware.vars.awsS3StagingFolder
            statusCode = HtmlStatusCodes.success
            status = 'success'
            errorMsg = None
            counter = 0
            html = ''
            headers = 'The files shown in this page are waiting to be uploaded to AWS S3. If these files are not getting uploaded, this means there is a problem connecting to AWS S3.  Verify the AWS S3 connection details.'
            # Default to first page: ['0:2']
            pageIndexRange = body['pageIndexRange'][0]
            
            # The page number to get
            getPageNumber = body['getPageNumber']
            getResultsPerPage = body.get('resultsPerPage', 100)
            
            indexStart    = int(pageIndexRange.split(':')[0])
            indexEnd      = int(pageIndexRange.split(':')[1])
            startingRange = pageIndexRange.split(":")[0]
                        
            # pageIndexRange:0:100  startingRange:0  pageNumber:1  startIndex:0  resultsPerPage:100 
            #print(f'\n--- GetAwsS3Uploads: pageIndexRange:{pageIndexRange}  startingRange:{startingRange}  pageNumber:{getPageNumber} startIndex:{indexStart}  resultsPerPage:{getResultsPerPage} ----')
                            
            try:
                s3UploadJsonFiles = glob(f'{s3StagingFolder}/*.json')
            except:
                errorMsg = f'The awsS3 stage folder is not found: {s3StagingFolder}'
                statusCode = HtmlStatusCodes.error
                return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)

            totalResults = len(s3UploadJsonFiles)
            
            ''' 
            getTestResultsPages: totalResults: 5
            resultsPerPage: 2
            remainders: 1
            --- Page:1  0:2
            --- Page:2  2:4
            --- Page:3  4:6
            {1: (0, 2), 2: (2, 4), 3: (4, -1)}
            '''
            # Create the page buttons
            pages = dict()
            
            # pageIndexRange:0:100  startingRange:0  pageNumber:1  startIndex:0  resultsPerPage:100 
            if indexStart == int(pageIndexRange.split(":")[0]):
                filesPerPageDropdown = f'<label for="resultsPerPage">Files Per Page: </label> <select id="resultsPerPage" onchange="setFilesPerPage(this)">'
                #for option in [10, 25, 50, 100]:
                for option in [100, 200, 300, 500]:                     
                    if int(option) == int(getResultsPerPage):
                        filesPerPageDropdown += f'<option value="{option}" selected="selected">{option}</option>'
                    else:
                        filesPerPageDropdown += f'<option value="{option}">{option}</option>'
        
                filesPerPageDropdown += f'</select>'

                pageButtons = f'{filesPerPageDropdown} &emsp; Current Page: {getPageNumber} &emsp; Pages: &ensp;'
            else:
                pageButtons = ''
               
            if indexStart == int(pageIndexRange.split(":")[0]):
                for index,startingIndex in enumerate(range(0, totalResults, getResultsPerPage)):
                    pageNumber = index+1
                    endingIndex = startingIndex + getResultsPerPage

                    if pageNumber > 1 and endingIndex == totalResults:
                        # Don't create a 2nd page button if there's only 1 page of results to show
                        #pages[pageNumber] = (startingIndex, -1)
                        pages[pageNumber] = (startingIndex, totalResults)
                        pageButtons += f'<button type="button" class="btn btn-outline-primary" onclick="getAwsS3Uploads(this)" getPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{totalResults}">{pageNumber}</button>&ensp;'
                    else:

                        pages[pageNumber] = (startingIndex, endingIndex)
                        pageButtons += f'<button type="button" class="btn btn-outline-primary" onclick="getAwsS3Uploads(this)" getPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</button>&ensp;'
            
            for index in range(indexStart, indexEnd):
                try:
                    eachS3UploadFileFullPath = s3UploadJsonFiles[index]
                    shortenPath = eachS3UploadFileFullPath.split('ServicesStagingArea')[-1]
                except:
                    break
                
                # When user clicks on the download button, the <form action="{% url 'testResults' %}" method="post"> will be directed.
                # Using name="downloadTestResults" to get the value
                html += f'\n\t\t\t<input type="checkbox" name="awsS3UploadsCheckbox" value="{eachS3UploadFileFullPath}" />&ensp;<a class="nav-link" style="display:inline-block" href="#" filePath="{eachS3UploadFileFullPath}" onclick="getFileContents(this)" data-bs-toggle="modal" data-bs-target="#openFileModal"><i class="fa-regular fa-file pr-2"></i>{shortenPath}</a></span><br>'
            
        except Exception as errMsg:
            errorMsg = str(errMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error

        concatHtml = f'{headers}<br><br>{pageButtons}<br>{html}'   
        return Response({'pages':concatHtml, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class DeleteAwsS3Uploads(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='awsS3', exclude=['engineer'])
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        deleteMethod = None
        
        try:
            # options: deleteAll | selectedFiles
            body = json.loads(request.body.decode('UTF-8'))
            selectedFiles = body['selectedFiles']
            deleteAll     = body['deleteAll']

            if selectedFiles:
                deleteMethod = 'DeleteSelected'
                for eachFile in selectedFiles:
                    execSubprocessInShellMode(f'sudo rm {eachFile}', showStdout=False)

            if deleteAll:
                deleteMethod = 'DeleteAllAwsS3Uploads'
                for eachFile in glob(f'{Serviceware.vars.awsS3StagingFolder}/*.json'):
                    execSubprocessInShellMode(f'sudo rm {eachFile}', showStdout=False)

            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action=deleteMethod, msgType='Info',
                                      msg='', forDetailLogs='')
            
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action=deleteMethod, msgType='Error',
                                      msg=errorMsg, forDetailLogs='')
        
        return Response({'status':status, 'error':errorMsg}, status=statusCode)
    

class StopAwsS3Service(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='awsS3', exclude=['engineer'])
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        try:
            # f'{keystackSystemPath}/ServicesStagingArea/AwsS3Uploads'
            self.s3StagingFolder = Serviceware.vars.awsS3StagingFolder
            self.awsS3ServiceObj = Serviceware.KeystackServices(typeOfService='keystackAwsS3', isFromKeystackUI=True)
            self.awsS3ServiceObj.stopService('keystackAwsS3')
            
            if self.awsS3ServiceObj.isServiceRunning('keystackAwsS3'):
                msg = f'Serviceware failed to stop keystackAwsS3 service'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='StopAwsS3Service', msgType='Error',
                                        msg=msg, forDetailLogs='')
                                
                raise Exception(msg)
            else:
                msg = f'Successfully stopped keystackAwsS3 service'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='StopAwsS3Service', msgType='Info',
                                            msg=msg, forDetailLogs='')

        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='StopAwsS3Service', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'status':status, 'error':errorMsg}, status=statusCode)
    
    
class RestartAwsS3Service(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='awsS3', exclude=['engineer'])
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        try:
            # f'{keystackSystemPath}/ServicesStagingArea/AwsS3Uploads'
            self.s3StagingFolder = Serviceware.vars.awsS3StagingFolder
            self.awsS3ServiceObj = Serviceware.KeystackServices(typeOfService='keystackAwsS3', isFromKeystackUI=True)
            
            if self.awsS3ServiceObj.isServiceRunning('keystackAwsS3'):
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RestartAwsS3Service', msgType='Info',
                                          msg='keystackAwsS3 service is currently running. Stopping service ...', forDetailLogs='')
                self.awsS3ServiceObj.stopService('keystackAwsS3')

            # This could only be done in the UI. So no need to also use keystack_pythonPath
            pythonPath = keystackSettings.get('dockerPythonPath')
            cmd = f'{pythonPath} {Serviceware.vars.keystackAwsS3Service} -isFromKeystackUI > /dev/null 2>&1 &'

            try:
                execSubprocessInShellMode(cmd)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RestartAwsS3Service', msgType='Info',
                                          msg=cmd, forDetailLogs='')
                                
            except Exception as errMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
                msg = f'Failed to start keystackAwsS3 serivce: {errMsg}'
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RestartAwsS3Service', msgType='Error',
                                          msg=msg, forDetailLogs=traceback.format_exc(None, errMsg))

                raise Exception(msg)
            
            if self.awsS3ServiceObj.isServiceRunning('keystackAwsS3') == False:
                msg = f'Serviceware failed to start keystackAwsS3'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RestartAwsS3Service', msgType='Error',
                                          msg=msg, forDetailLogs='')
                                 
                raise Exception(msg)
            else:
                msg = f'keystackAwsS3 service is running'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RestartAwsS3Service', msgType='Info',
                                          msg=msg, forDetailLogs='')    
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RetartAwsS3Service', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'status':status, 'error':errorMsg}, status=statusCode)
    
    
class IsAwsS3ServiceRunning(APIView):
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        try:
            self.awsS3ServiceObj = Serviceware.KeystackServices(typeOfService='keystackAwsS3', isFromKeystackUI=True)
            
            if self.awsS3ServiceObj.isServiceRunning('keystackAwsS3'):
                isAwsS3ServiceRunning = True
            else:
                isAwsS3ServiceRunning = False
                
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsAwsS3ServiceRunning', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'isAwsS3ServiceRunning':isAwsS3ServiceRunning, 'status':status, 'error':errorMsg}, status=statusCode)


class GetAwsS3Logs(APIView):
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        awsS3Logs = None
        
        try:
            if os.path.exists(GlobalVars.keystackAwsS3Logs):
                logs = readJson(GlobalVars.keystackAwsS3Logs)
            else:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAwsS3Logs', msgType='Info',
                                          msg=f'There is no AWS S3 log file recently', forDetailLogs='')
                
                return Response({'awsS3Logs':awsS3Logs, 'status':status, 'error':errorMsg}, status=statusCode)
            
            html = '<div class="row tableStyle">'
            html +=    '<table id="awsS3LogsTable" class="tableFixHead2">'   
            html +=        '<thead>'
            html +=            '<tr>'
            html +=                 '<th>Date/Time</th>'
            html +=                 '<th>Msg Type</th>'
            html +=                 '<th>Message</th>'
            html +=            ' </tr>'
            html +=         '</thead>'
            html +=         '<tbody>'

            for message in logs['messages']:
                html += f'<tr>'
                html +=     f'<td>{message["timestamp"]}</td>'
                html +=     f'<td>{message["msgType"]}</td>'
                html +=     f'<td>{message["msg"]}</td>'
                html += f'</tr>'
            
            html +=          '</tbody>'    
            html +=     '</table>'
            html += '</div>'
 
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsAwsS3ServiceRunning', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'awsS3Logs':html, 'status':status, 'error':errorMsg}, status=statusCode)


class ClearAwsS3Logs(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='deleteDomains', exclude=['engineer']) 
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        try:
            if os.path.exists(GlobalVars.keystackAwsS3Logs):
                os.remove(GlobalVars.keystackAwsS3Logs)
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ClearAwsS3Logs', msgType='Info',
                                      msg=f'Cleared AWS S3 logs: {GlobalVars.keystackAwsS3Logs}', 
                                      forDetailLogs='')
            else:
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ClearAwsS3Logs', msgType='Info',
                                          msg=f'No AWS S3 logs to clear', forDetailLogs='')
                                 
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ClearAwsS3Logs', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'awsS3Logs':html, 'status':status, 'error':errorMsg}, status=statusCode)
 

class EnableAwsS3DebugLogs(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='deleteDomains', exclude=['engineer']) 
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        try:
            execSubprocessInShellMode(f'touch {GlobalVars.awsS3DebugFile}')
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='EnableAwsS3DebugLogs', msgType='Info',
                                      msg='Enabled', forDetailLogs='')
             
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='EnableAwsS3DebugLogs', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'status':status, 'error':errorMsg}, status=statusCode)
    

class DisableAwsS3DebugLogs(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='deleteDomains', exclude=['engineer']) 
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        try:
            os.remove(GlobalVars.awsS3DebugFile)
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveAwsS3DebugLogs', msgType='Info',
                                      msg='Disabled', forDetailLogs='')
             
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveAwsS3DebugLogs', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'status':status, 'error':errorMsg}, status=statusCode)
    
    
class IsAwsS3DebugEnabled(APIView):
    def post(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        isAwsS3DebugEnabled = False
        
        try:
            if os.path.exists(GlobalVars.awsS3DebugFile):
                isAwsS3DebugEnabled = True
             
        except Exception as errMsg:
            status = 'failed'
            errorMsg = str(errMsg)
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsAwsS3DebugEnabled', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response({'isAwsS3DebugEnabled':isAwsS3DebugEnabled, 'status':status, 'error':errorMsg}, status=statusCode)
    
 
class GetPipelineAwsS3LogFiles(APIView):
    def post(self, request):
        """ 
        Running a playbook generates its own aws s3 logs.
        These logs shows detailed aws s3 connections, starting threads, completed threads, etc.
        
        Ex: PLAYBOOK=Samples-pythonSample_05-05-2023-09:39:40:605539_<sessionId>.json
        """
        user = request.session['user']
        logsFolder = GlobalVars.keystackServiceLogPath
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        counter = 0
        dropdownFileMenu = ''
        
        try:    
            pipelineAwsS3Logs = glob(f'{logsFolder}/PLAYBOOK=*.json')
            totalFiles = len(pipelineAwsS3Logs)
            
            dropdownFileMenu = '<div class="dropdown"><a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>Select a log to view</a>'
            dropdownFileMenu += '<ul class="dropdown-menu dropdownSize dropdownFontSize">'
                    
            for eachTestLog in pipelineAwsS3Logs:
                logFileName = eachTestLog.split('/')[-1]
                dropdownFileMenu += f'<li class="dropdown-item" logFile="{eachTestLog}" onclick="showPipelineAwsS3Logs(this)">{logFileName}</li>'
              
            dropdownFileMenu += '</ul></div>'
            
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelineAwsS3LogFiles', msgType='Info',
                                      msg=f'{totalFiles} pipeline aws S3 logs', forDetailLogs='')
                                      
        except Exception as errMsg:
            errorMsg = str(errMsg)
            status = 'failed'
            statusCode = HtmlStatusCodes.error
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPipelineAwsS3LogFiles', msgType='Error',
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'dropdownFileMenu':dropdownFileMenu, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
       
    