import os, sys, traceback
from glob import glob
from re import search
from shutil import rmtree
from time import sleep
from re import search
from copy import deepcopy
from pprint import pprint

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole, getUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
import EnvMgmt
from globalVars import HtmlStatusCodes, GlobalVars
from commonLib import logDebugMsg, getHttpIpAndPort
from keystackUtilities import readJson, writeToJson, readFile, readYaml, writeToYamlFile, execSubprocessInShellMode, mkdir2, chownChmodFolder, writeToFile, removeFile, getTimestamp, convertStrToBoolean
from PortGroupMgmt import ManagePortGroup
from domainMgr import DomainMgr
from db import DB
from scheduler import JobSchedulerAssistant, getSchedulingOptions
from RedisMgr import RedisMgr

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    

class Vars:
    """ 
    For logging the correct topics.
    To avoid human typo error, always use a variable instead of typing the word.
    """
    webpage = 'envs'
    envMgmtDB = 'envMgmt'
    envLoadBalanceDB = 'envLoadBalanceGroups'


def getEnvGroupsHelper():
    """ 
    This function is used by multiple functions:
    getEnvGroups and EnvGroupsTableForDelete
    """
    envGroups = []

    for root,dirs,files in os.walk(GlobalVars.envPath):
        # /opt/KeystackTests/Envs/LoadCore
        regexMatch = search(f'.+(/Envs.+)$', root)
        if regexMatch:
            # /opt/KeystackTests/Envs
            # /opt/KeystackTests/Envs/qa
            envGroups.append(regexMatch.group(1))
    
    return envGroups
     
                         
def getTableData(request, domain, envGroup, user, indexStart, indexEnd) -> str:
    """ 
    Get env yml files from /$keystackTestRootPath/Envs folder.
    
    Env groups are subfolder names: Envs/DOMAIN=Communal/KeystackQA
    """
    tableData: str = ''
    envMgmtPath = GlobalVars.envMgmtPath

    try:
        # Get all the Envs from /opt/KeystackTests/Envs/$envGroup path
        # Calling EnvMgmt.isEnvParallelUsage() calls getEnvDetails() which will add the env
        # to MongoDB if the env does not exists
        
        domainUserRole = DomainMgr().getUserRoleForDomain(user, domain)
        envMgmtObj = EnvMgmt.ManageEnv() 
        
        for rootPath, dirs, files in os.walk(GlobalVars.envPath): 
            #  root=/opt/KeystackTests/Envs files=['pythonSample.yml', 'loadcoreSample.yml']          
            if bool(search(f'^{GlobalVars.keystackTestRootPath}/{envGroup}$', rootPath)) and files:
                # Just file names. Not path included.
                for index, envYmlFile in enumerate(files[indexStart:indexEnd]):
                    if bool(search('.+\.(yml|ymal)$', envYmlFile)):
                        envYmlFileFullPath = f'{rootPath}/{envYmlFile}'
                        regexMatch = search('.*DOMAIN=(.+?)/(.+)\.(yml|yaml)?', envYmlFileFullPath)
                        if regexMatch:
                            domain = regexMatch.group(1)
                            env = regexMatch.group(2)
                        else:
                            domain = None
                        
                        # DOMAIN=Communal/Samples/demoEnv
                        envWithDomain = f'DOMAIN={domain}/{env}'
                        
                        # DOMAIN=Communal/<group>/<env>.yml 
                        envMgmtObj.setenv = f'{envWithDomain}.yml'

                        envYmalHasError = False
                        try:
                            envData = readYaml(envYmlFileFullPath)
                        except Exception as errMsg:
                            # If there is an invisible tab in the yml file, show the error to the user using title
                            envData = {}
                            errorMsg = str(errMsg).replace('<', '').replace('>', '').replace('"', '')
                            envYmalHasError = f'Error found in Env Yaml file. {envYmlFileFullPath}: {errorMsg}'

                        if envData is None:
                            envData = {}
                
                        location = envData.get('location', 'Not-Specified')
                        if location == 'none':
                            location = 'Not-Specified'
                            
                        isParallelUsage = envMgmtObj.isEnvParallelUsage()
                        if isParallelUsage:
                            shareable = 'Yes'
                        else:
                            shareable = 'No'

                        if domainUserRole != 'engineer':
                            sharedDropdown = '<div class="dropdown">'
                            sharedDropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{shareable}</a>"        
                            sharedDropdown += f'<ul  id="isEnvSharedDropdownId" class="dropdown-menu shareableDropdown" aria-labelledby="">'
                            if isParallelUsage:
                                sharedDropdown += f'<li class="dropdown-item" env="{envWithDomain}" shareable="No">No</li>'
                            else: 
                                sharedDropdown += f'<li class="dropdown-item" env="{envWithDomain}" shareable="Yes">Yes</li>'
                            sharedDropdown += '</ul></div>' 
                        else:
                            sharedDropdown = shareable
                                                          
                        portGroups = envData.get('portGroups', None)
                        concatPortGroupDropdown = ''
                                                      
                        if portGroups and domain is not None:
                            for portGroup in portGroups:
                                ports = ManagePortGroup(domain=domain, portGroup=portGroup).getPortGroupPorts()

                                if len(ports) > 0:
                                    concatPortGroupDropdown = f'Port-Group: {portGroup}'
                                    
                                    # ports': {'device_1': {'domain': 'Communal', 'ports': ['1/1', '1/2']}}
                                    for deviceName, value in ports.items():
                                        deviceDomain = value['domain']
                                        devicePorts = value['ports']
                                        
                                        portGroupDropdown = '<div class="dropdown">'
                                        portGroupDropdown += f"<a class='dropdown-toggle textBlack marginLeft20px' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Device: {deviceName}</a>"    
                                        
                                        portGroupDropdown += '<ul class="dropdown-menu dropdownSizeMedium" id="envPortGroupDropdownId" aria-labelledby="portsDropdown">'                                 
                                        portGroupDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><br>Domain: {deviceDomain}&emsp;&emsp;Device: {deviceName}:</li>'
                                        
                                        for index, eachDevicePort in enumerate(devicePorts):
                                            portGroupDropdown += f'<li class="mainFontSize textBlack paddingLeft40px">{index+1}: Port: {eachDevicePort}</li>' 
                                                    
                                        portGroupDropdown += '</ul></div>'
                                        concatPortGroupDropdown += portGroupDropdown   
               
                        # envYmlFileFullPath: /opt/KeystackTests/Envs/DOMAIN=Communal/KeystackQA/env1.yml
                        # envName: DOMAIN=Communal/KeystackQA/env1
                        envName = envYmlFileFullPath.split(f'{GlobalVars.envPath}/')[1].split('.')[0]
                        
                        envDisplayName = envYmlFileFullPath.split('/')[-1].split('.')[0]
                        onSchedulerCronJobs = len(JobSchedulerAssistant().getCurrentCronJobs(searchPattern=f'env={envYmlFileFullPath}'))
                        
                        envMgmtObj = EnvMgmt.ManageEnv(envName)
                        isAvailable = envMgmtObj.isEnvAvailable()
                        if isAvailable:
                            isAvailable = 'Yes'
                            
                        if isAvailable == False:
                            isAvailable = 'No'
                            
                        totalWaiting = len(envMgmtObj.getWaitList())
                        activeUsers = envMgmtObj.getActiveUsers()
                        totalActiveUsers = len(activeUsers)
                        
                        loadBalanceGroups = envMgmtObj.getLoadBalanceGroups()
                        if loadBalanceGroups:
                            lbgDropdown = '<div class="dropdown">'
                            lbgDropdown += '<a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>View</a>'
                            lbgDropdown += '  <ul class="dropdown-menu dropdownSizeSmall">'
                            for lbg in loadBalanceGroups:
                                lbgDropdown += f'<li class="dropdown-item">{lbg}</li>'
                                
                            lbgDropdown += '</ul></div>' 
                        else:
                            lbgDropdown = 'None'
                            
                        tableData += '<tr>'
                        if domainUserRole == 'engineer':
                            tableData += f'<td><input type="checkbox" name="envCheckboxes" value="{envYmlFileFullPath}" envName="{envName}" parallelUsage="{isParallelUsage}" disabled/></td>'
                        else:
                            tableData += f'<td><input type="checkbox" name="envCheckboxes" value="{envYmlFileFullPath}" envName="{envName}" parallelUsage="{isParallelUsage}" /></td>'
                            
                        tableData += f'<td><button class="textAlignCenter btn btn-sm btn-outline-primary" value="{envYmlFileFullPath}" onclick="getFileContents(this)" data-bs-toggle="modal" data-bs-target="#viewEditEnvModal">View / Edit</button></td>'
                        
                        if envYmalHasError is not False:
                            tableData += f'<td class="textAlignCenter"> <span class="textRed" title="{envYmalHasError}"> {envDisplayName} </span> </td>'
                        else:
                            tableData += f'<td class="textAlignCenter">{envDisplayName}</td>'
                        
                        tableData += f'<td class="textAlignLeft">{concatPortGroupDropdown}</td>'    
                        tableData += f'<td class="textAlignCenter">{location}</td>'
                        tableData += f'<td class="textAlignCenter">{lbgDropdown}</td>'
                        tableData += f'<td class="textAlignCenter">{sharedDropdown}</td>'
                        tableData += f'<td class="textAlignCenter">{isAvailable}</td>'

                        if isParallelUsage is False:
                            tableData += f'<td class="textAlignCenter"><a href="#" onclick="activeUsersList(this)" env={envName} data-bs-toggle="modal" data-bs-target="#activeUsersModal">Active: {totalActiveUsers}&emsp;&ensp;Waiting: {totalWaiting}</a></td>'
                            
                        # Get total cron jobs for this Env
                        if isParallelUsage is False:
                            tableData += f'<td class="textAlignCenter"><a href="#" data-bs-toggle="modal" data-bs-target="#createEnvSchedulerModal" env={envYmlFileFullPath} onclick="getEnvCronScheduler(this)">{onSchedulerCronJobs}</a></td>'
                        else:
                            tableData += '<td></td>'
                                                   
                        # The reserve button has no stage and task
                        if isParallelUsage is False:
                            tableData += f'<td class="textAlignCenter"><button onclick="reserveEnv(this)" env={envName} class="btn btn-sm btn-outline-primary">Reserve Now</button></td>'
                        else:
                            tableData += '<td></td>'
                        
                        if isParallelUsage is False:    
                            tableData += f'<td class="textAlignCenter"><button class="btn btn-sm btn-outline-primary" env={envName} onclick="releaseEnv(this)" >Release</button></td>'
                        else:
                            tableData += '<td></td>'
                     
                        # if getUserRole(request) == 'admin':
                        #     tableData += f'<td class="textAlignCenter"><button onclick="resetEnv(this)" env={envName} class="btn btn-sm btn-outline-primary">Reset</button></td>'
                        # else:
                        if isParallelUsage is False:
                            if getUserRole(request) == 'admin':
                                tableData += f'<td class="textAlignCenter"><button onclick="resetEnv(this)" env={envName} class="btn btn-sm btn-outline-primary">Reset</button></td>'
                            else:
                                tableData += f'<td class="textAlignCenter"><button onclick="resetEnv(this)" env={envName} class="btn btn-sm btn-outline-primary" disabled>Reset</button></td>'
                        else:
                            tableData += '<td></td>'
                                               
                        # tableData += f'<td class="textAlignCenter"><button env={envName} class="btn btn-sm btn-outline-primary envAutoSetup">Define</button></td>'

                        # tableData += f'<td class="textAlignCenter"><button data-bs-toggle="modal" data-bs-target="#autoTeardownModal" env={envName} class="btn btn-sm btn-outline-primary">Define</button></td>'
                                                                           
                        tableData += '</tr>'
        
        if tableData != '':
            # Add extra row to support the tableFixHead2 body with height:0 to 
            # show a presentable table. Otherwise, if there are a few rows, the row 
            # height will be large to fill the table size
            tableData += '<tr></tr>'
                            
    except Exception as errMsg:
        tableData += '<tr></tr>'
        print('\nenvViews getTableData error:', traceback.format_exc(None, errMsg))
        pass
        
    return tableData


class GetEnvTableData(APIView):
    swagger_schema = None

    def post(self, request):
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        errorMsg = None
        statusCode= HtmlStatusCodes.success
        status = 'success'
        tableData = ''

        getCurrentPageNumber  = request.data.get('getCurrentPageNumber', None)
        devicesPerPage        = request.data.get('devicesPerPage', None)
                
        # ['0:2'] <-- In a list
        # pageIndexRange: The document range to get from the collective pool of document data
        pageIndexRangeOriginal = request.data.get('pageIndexRange', None)
        
        # 0:2
        if pageIndexRangeOriginal:
            pageIndexRange = pageIndexRangeOriginal[0]
            indexStart     = int(pageIndexRange.split(':')[0])
            indexEnd       = int(pageIndexRange.split(':')[1])
            startingRange  = pageIndexRange.split(":")[0]
        
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                envGroupToView = request.GET.get('envGroup')
                domain = request.GET.get('domain')               
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getEnvDataTable', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
        # JSON format
        if request.data:
            # <QueryDict: {'env': 'loadcoreSample', 'sessionId': '02-04-2023-08:53:15:021768_7277', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json', 'user': 'hgee', 'stage': 'Teardown', 'task': 'CustomPythonScripts', 'trackUtilization': False, 'webhook': True}
            try:
                envGroupToView = request.data['envGroup']
                domain = request.data['domain']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getEnvDataTable', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"envGroup": envGroupToView, 'domain':domain}
            restApi = '/api/v1/env/getEnvTableData'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetEnvTableData')
            tableData = response.json()['tableData']
            pagination = response.json()['pagination']
            pageNumber = response.json()['totalPages'] 
              
        else:                  
            try:            
                # Self cleanup on activeUsers
                # Users might have included -holdEnvsIfFailed and deleted the pipeline or test result
                # The env still has the active user. We need to automatically release the active-user from the env.
                #    1> Get all envs for the envGroupToView
                #    2> Get active users for all envs in this env group
                #    3> Check if test results exists.  If not, the user deleted the pipeline test results before
                #       releasing the env.

                # envGroupToView: Envs/DOMAIN=Communal/Samples
                envMgmtObj = EnvMgmt.ManageEnv(envGroupToView.replace('Envs/', '')) 
                # envGroupPath: /opt/KeystackTests/Envs/DOMAIN=Communal/Samples               
                envGroupPath = f'{GlobalVars.keystackTestRootPath}/{envGroupToView}'
                devices = glob(f'{envGroupPath}/*')
                totalDevices = len(devices)
                pageNumber = 0

                pagination = """<nav aria-label="">
                                    <ul class="pagination pagination-sm">
                                        <li class="page-item">
                                            <a class="page-link" id="previousPage" href="#" aria-label="Previous">
                                                <span aria-hidden="true">&laquo;</span>
                                            </a>
                                        </li>"""

                pageNumberMapping = {}
                # devicesPerPage:5  getPageNumber:1  pageIndexRange:0:5  indexStart:0  indexEnd:5  startingRange:0
                for index, startingIndex in enumerate(range(0, totalDevices, devicesPerPage)):
                    # Creating page buttons with specific range of devices to show
                    pageNumber = index+1
                    endingIndex = startingIndex + devicesPerPage
                    pageNumberMapping[pageNumber] = (startingIndex, endingIndex)

                    if pageNumber > 1 and endingIndex == totalDevices:
                        # Don't create a 2nd page button if there's only 1 page of results to show
                        pagination += f'<li class="page-item"><a class="page-link" href="#" onclick="getSetupTableData(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{totalDevices}">{pageNumber}</a></li>'
                    else:
                        # Note: if endingIndex != data.count():
                        # getPageNumber: Is to show the current page number
                        if int(pageNumber) == int(getCurrentPageNumber):
                            pagination += f'<li class="page-item active"><a class="page-link" href="#" onclick="getSetupTableData(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</a></li>'
                        else:
                            pagination += f'<li class="page-item"><a class="page-link" href="#" onclick="getSetupTableData(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</a></li>'
                        
                pagination += """<li class="page-item">
                                    <a class="page-link" id="nextPage" href="#" aria-label="Next">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                    </li></ul></nav>"""

                if pageNumberMapping == {}:
                    indexStart = 0
                    indexEnd = 0
                else:
                    currentPageStartAndEndIndexes = pageNumberMapping[int(getCurrentPageNumber)]
                    indexStart = currentPageStartAndEndIndexes[0]
                    indexEnd = currentPageStartAndEndIndexes[1]

                for index, env in enumerate(devices[indexStart:indexEnd]):
                    # env: /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bringup.yml
                    if bool(search('.+\.(yml|ymal)$', env)) == False:
                        continue 

                   # Creating page buttons with specific range of devices to show
                    pageNumber = index+1
                    endingIndex = startingIndex + devicesPerPage

                    envGroup = ''
                    envName = env.split('/')[-1].split('.')[0]
                    regexMatch = search('^Envs/(.+)', envGroupToView)
                    if regexMatch:
                        envGroup = regexMatch.group(1)

                    envMgmtObj.setenv = f'{envGroup}/{envName}'
                    activeUsers = envMgmtObj.getActiveUsers()
                    if activeUsers:
                        # Get test result path and check for path exists

                        # [{'sessionId': '05-17-2023-15:49:07:297406_5432', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/05-17-2023-15:49:07:297406_5432/overallSummary.json', 'user': 'hgee', 'stage': 'Test', task: 'CustomPythonScripts2'}]
                        for activeUser in activeUsers:
                            overallSummaryFile = activeUser['overallSummaryFile']
                            if overallSummaryFile:
                                testResultPath = overallSummaryFile.split('/overallSummary.json')[0]
                                if os.path.exists(testResultPath) == False:
                                    # Release the env from activeUsers
                                    session = {'sessionId':activeUser['sessionId'], 'stage':activeUser['stage'],
                                               'task':activeUser['task'], 'user':activeUser['user']}
                                     
                                    envMgmtObj.removeFromActiveUsersList([session])
                                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AutoRemoveActiveUser', 
                                                              msgType='Success', msg=f'The env {envGroup}/{envName} has active user, but the pipeline and test results are deleted. Releasing active user on this env.',
                                                              forDetailLogs='')
 
                tableData = getTableData(request, domain, envGroupToView, user, indexStart, indexEnd)
 
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                tableData = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvTableData', 
                                        msgType='Error', msg=errorMsg,
                                        forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'tableData': tableData, 
                              'pagination': pagination,
                              'totalPages': pageNumber,
                              'getCurrentPageNumber': getCurrentPageNumber,
                              'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class CreateEnv(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='Create', exclude=['engineer'])
    def post(self, request):
        """
        Create a new Env file
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        envPath = GlobalVars.envPath
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if request.GET:
            # Rest APIs with inline params come in here
            try:
                envNamespace = request.GET.get('newEnv')
                envGroup     = request.GET.get('envGroup') 
                textArea     = request.GET.get('textArea')
                domain       = request.GET.get('domain')             
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='createEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
        # JSON format
        if request.data:
            # <QueryDict: {'env': 'loadcoreSample', 'sessionId': '02-04-2023-08:53:15:021768_7277', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json', 'user': 'hgee', 'stage': 'Teardown', 'task': 'CustomPythonScripts', 'trackUtilization': False, 'webhook': True}
            try:
                envNamespace = request.data['newEnv']
                envGroup     = request.data['envGroup']
                textArea     = request.data['textArea']
                domain       = request.data['domain']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='createEnv', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"newEnv":envNamespace, "envGroup":envGroup, "textArea":textArea}
            restApi = '/api/v1/env/create'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='Create')  
        else:        
            if '-' in envNamespace:
                env = envNamespace.replace('-', '/')  
            else:
                env = envNamespace

            try:
                if '.yml' not in env:
                    env = f'{env}.yml'
                
                if envGroup not in ['None', '']:
                    if envGroup[0] == '/':
                        envGroup = f'/{domain}{envGroup}'
                    else:
                        envGroup = f'/{domain}/{envGroup}'
                        
                    envFullPath = f'{envPath}/{envGroup}'
                    mkdir2(envFullPath)
                    fullPathFile = f'{envFullPath}/{env}' 
                    chownChmodFolder(envFullPath, GlobalVars.user, GlobalVars.userGroup, stdout=False)
                    chownChmodFolder(fullPathFile, GlobalVars.user, GlobalVars.userGroup, stdout=False)

                else:
                    envGroup = None
                    playbookGroup = None
                    fullPathFile = f'{envPath}/{domain}/{env}'

                if os.path.exists(fullPathFile):
                    status = 'failed'
                    statusCode = HtmlStatusCodes.error
                    errorMsg = f'Env already exists: Group:{envGroup} Env:{env}'
                    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', 
                                              msgType='Failed', msg=errorMsg, forDetailLogs='')
                    return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)

                if textArea == '':
                    writeToFile(fullPathFile, '', mode='w', printToStdout=False)
                else:    
                    writeToFile(fullPathFile, textArea, mode='w', printToStdout=False)
                            
                try:
                    # Verify for yaml syntax error
                    readYaml(fullPathFile)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', 
                                            msgType='Success',
                                            msg=f'Env:{env} Group:{envGroup}', forDetailLogs='') 
         
                except Exception as errMsg:
                    errorMsg = "Error: The env Yaml file has syntax error."
                    status = "failed"
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', 
                                              msgType='Error',
                                              msg=errorMsg, forDetailLogs='') 

            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateEnv', msgType='Error',
                                          msg=errMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

     
class DeleteEnvs(APIView):
    # envs = openapi.Parameter(name='envs', description="A list of envs to delete",
    #                                       required=False, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)           
    # @swagger_auto_schema(tags=['/api/v1/env/delete'], operation_description="Delete Envs",
    #                      manual_parameters=[envs])
    @verifyUserRole(webPage=Vars.webpage, action='DeleteEnv', exclude=['engineer'])
    def post(self, request):
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        error = None
        statusCode= HtmlStatusCodes.success
        status = 'success'

        if request.GET:
            # Rest APIs with inline params come in here
            try:
                deleteEnvs = request.GET.get('envs')                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
        # JSON format
        if request.data:
            # <QueryDict: {'env': 'loadcoreSample', 'sessionId': '02-04-2023-08:53:15:021768_7277', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json', 'user': 'hgee', 'stage': 'Teardown', 'task': 'CustomPythonScripts', 'trackUtilization': False, 'webhook': True}
            try:
                deleteEnvs = request.data['envs']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"envs": deleteEnvs}
            restApi = '/api/v1/env/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteEnvs')
        else:              
            try:  
                # deleteEnvs: ['/opt/KeystackTests/Envs/DOMAIN=Communal/rack1.yml', 
                #              '/opt/KeystackTests/Envs/DOMAIN=Communal/rack3.yml']          
                for env in deleteEnvs:
                    # envName: DOMAIN=Communal/Samples/stage
                    envName = env.split(f'{GlobalVars.envPath}/')[-1].split('.')[0]
                    os.remove(env)
                    
                    # Get the env load balance group name
                    envData = DB.name.getOneDocument(collectionName=Vars.envMgmtDB, fields={'env':envName})
                    
                    # Remove the env from the load balancer
                    if envData['loadBalanceGroups']:
                        DB.name.updateDocument(collectionName=Vars.envLoadBalanceDB, queryFields={'name':envData['loadBalanceGroups']}, 
                                               updateFields={'envs': envName}, removeFromList=True)
                        
                    DB.name.deleteOneDocument(collectionName=Vars.envMgmtDB, fields={'env': envName})
                    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnv', 
                                              msgType='Success', msg=f'Deleted Env: {env}')
                    
            except Exception as errMsg:
                error = f'Error: {errMsg}'
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnv', 
                                          msgType='Error', msg=error,
                                          forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'status': status, 'errorMsg': error}, status=statusCode)
 

class ViewEditEnv(APIView):
    swagger_schema = None
    @verifyUserRole(webPage=Vars.webpage, action='view/edit', exclude=["engineer"])
    def post(self, request):
        """
        Show the env yml file contents and allow editing
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        envFile = request.data.get('envFile', None)
        envContents = dict()        
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"envFile": envFile}
            restApi = '/api/v1/env/viewEditEnv'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ViewEditEnv')
            envContents = response.json()['envContents']  
             
        else:
            if os.path.exists(envFile) == False:
                errorMsg = f'Env yml file not found: {envFile}'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ViewEditEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
                status = 'failed'
            else:    
                envContents = readYaml(envFile)
            
        return Response(data={'envContents': envContents, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
           
class GetEnvs(APIView):
    @swagger_auto_schema(tags=['/api/v1/env/list'], operation_description="Get a list of Envs",
                         manual_parameters=[])
    def get(self, request):
        """
        Description: 
            Return a list of all the Envs in full path files
        
        No parameters required

        GET /api/v1/envs/list
        
        Example:
            curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X GET http://192.168.28.10:8000/api/v1/env/list
            
        Return:
            A list of environments
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        envs = []
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/list'
            # stream=False, showApiOnly=False, silentMode=False, 
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetEnvs', stream=False) 
            envs = response.json()['envs']
              
        else:        
            try:
                envPath = GlobalVars.envPath
                for root,dirs,files in os.walk(envPath):
                    # /opt/KeystackTests/Envs/LoadCore
                    envGroup = root.split(envPath)[1]

                    if files:
                        for eachFile in files:
                            if eachFile.endswith('.yml'):
                                envs.append(f'{root}/{eachFile}')
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                envs = []
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getEnvs', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
        
        return Response(data={'envs': envs, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class EnvGroups(APIView):
    """
    Internal usage only: Get Env domain groups for sidebar Env dropdown menu
    
    /api/v1/env/envGroups
    """
    def post(self, request):
        """
        Get Env groups for sidebar Env menu
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        htmlEnvGroups = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/envGroups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='EnvGroups')
            htmlEnvGroups = response.json()['envGroups']               
        else:          
            try:
                envGroups = []
                trackDomainMenu = []
                htmlEnvGroups = ''
                userAllowedDomains = DomainMgr().getUserAllowedDomains(user)

                htmlEnvGroups += '<a href="/setups/envLoadBalancer" class="collapse-item pl-0 pt-3 pb-3 textBlack fontSize12px"><strong>Env Load-Balance Mgmt</strong></a>'
                
                for root,dirs,files in os.walk(GlobalVars.envPath):
                    currentDomain = root.split(f'{GlobalVars.envPath}/')[-1].split('/')[0].split('=')[-1]
                    # Envs/DOMAIN=Sanity/qa/dev
                    envGroup = root.split(f'{GlobalVars.keystackTestRootPath}/')[-1]
                    envGroupName = '/'.join(envGroup.split('/')[2:])
                    totalEnvs = len([envFile for envFile in files if '~' not in envFile and 'backup' not in envFile])
                    
                    if currentDomain in userAllowedDomains:
                        if currentDomain not in trackDomainMenu:
                            trackDomainMenu.append(currentDomain)
                            htmlEnvGroups += f'<p class="pl-2 pt-2 textBlack fontSize12px"><strong>Domain:&ensp;{currentDomain}</strong></p><br>'
                        
                        htmlEnvGroups += f'<a class="collapse-item pl-3 fontSize12px" href="/setups?group={envGroup}">{totalEnvs} <i class="fa-regular fa-folder pr-3"></i>{envGroupName}</a>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                htmlEnvGroups = ''
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            
        
        return Response(data={'envGroups':htmlEnvGroups, 'status':status, 'error':errorMsg}, status=statusCode)   
    
    
class GetEnvGroups(APIView):
    @swagger_auto_schema(tags=['/api/v1/env/groups'], operation_description="Get a list of Env Groups",
                         manual_parameters=[])
    def get(self, request):
        """
        Description: 
            Return a list of all the env groups
        
        No parameters required

        GET /api/v1/env/groups
        
        Example:
            curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X GET http://192.168.28.10:8000/api/v1/env/groups
            
        Return:
            A list of environments
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        envGroups = []
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/groups'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetEnvGroups')
            envGroups = response.json()['envGroups']
                       
        else:
            try:
                envGroups = getEnvGroupsHelper()
        
            except Exception as errMsg:
                errorMsg = str(errMsg)
                envGroups = []
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getEnvGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
        
        return Response(data={'envGroups': envGroups, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetEnvGroupsDropdownForUserGroupMgmt(APIView):
    def post(self, request):
        """
        Description: 
            Return a list of all the Envs in full path files
        
        No parameters required

        POST /api/v1/env/getEnvGroupsDropdownForUserGroupMgmt
        
        Example:
            curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X GET http://192.168.28.10:8000/api/v1/env/getEnvGroupsDropdownForUserGroupMgmt
            
        Return:
            html dropdown list of envs
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        envsDropdown = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/getEnvGroupsDropdownForUserGroupMgmt'
            # stream=False, showApiOnly=False, silentMode=False, 
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='getEnvGroupsDropdownForUserGroupMgmt', 
                                                                  stream=False)  
            envsDropdown = response.json()['envsDropdown']
              
        else:        
            try:
                for root, dirs, files in os.walk(GlobalVars.envPath):
                    # /opt/KeystackTests/Envs/LoadCore
                    envGroup = root.split(GlobalVars.envPath)[1]
                    if envGroup.startswith('/'):
                        envGroup = envGroup[1:]
                    envsDropdown += f'<li class="dropdown-item pl-2 textBlack">{envGroup}</li>'
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                envsDropdown = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getEnvGroupsDropdownForUserGroupMgmt', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response(data={'envsDropdown': envsDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class EnvGroupsTableForDelete(APIView):
    swagger_schema = None
    """
    Internal usage only: Get Env groups for delete env group table selection
    """
    def post(self, request):
        """
        Create a table for selecting Env groups to delete
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/envGroupsTableForDelete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='EnvGroupsTableForDelete')
            html = response.json()['envGroupsHtml'] 
                   
        else:  
            try:
                html +=   '<center><table class="tableFixHead2 table-bordered" style="width:90%">'    
                html +=        '<thead>'
                html +=            '<tr>'
                html +=                 '<th><input type="checkbox" name="deleteAllEnvGroups" onclick="disableEnvGroupCheckboxes(this)" \></th>'
                html +=                 '<th>EnvGroup</th>'
                html +=            '</tr>'
                html +=         '</thead>'
                html +=         '<tbody>'
                
                for envGroup in getEnvGroupsHelper():
                    envGroupName = envGroup.split('/Envs/')[-1]
                    html += '<tr>'
                    html += f'<td><input type="checkbox" name="deleteEnvGroups" value="{GlobalVars.keystackTestRootPath}/{envGroup}"></td>'
                    html += f'<td class="textAlignLeft">{envGroupName}</td>'
                    html += '</tr>'
                    
                html +=  '</tbody>'    
                html +=  '</table></center>'
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                html = ''
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='EnvGroupsTableForDelete', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            
            
        return Response(data={'envGroupsHtml':html, 'status':status, 'error':errorMsg}, status=statusCode)   
    

class GetActiveUsersList(APIView):
    swagger_schema = None
    def post(self, request):
        """ 
        "waitList": [{"task": "LoadCore",
                      "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                      "user": "rocky"
                     },
                     {"task": "LoadCore",
                      "sessionId": "11-01-2022-04:23:05:749724_rocky_1test",
                      "user": "rocky"}]
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        envNamespace = request.data.get('env', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"env": envNamespace}
            restApi = '/api/v1/env/getActiveUsersList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetActiveUsersList')
            html = response.json()['tableData'] 
                      
        else:
            if '-' in envNamespace:
                env = envNamespace.replace('-', '/')
            else:
                env = envNamespace
                
            try:
                envMgmtObj = EnvMgmt.ManageEnv(env)
                envMgmtObj.setenv = env
                            
                html = '<table id="envActiveUsersTable" class="mt-2 table table-sm table-bordered table-fixed tableFixHead tableMessages">' 
                html += '<thead>'
                html += '<tr>'
                html += '<th scope="col" class="textAlignCenter">Release</th>'
                html += '<th scope="col" class="textAlignCenter">User</th>'
                html += '<th scope="col" class="textAlignCenter">SessionId</th>'
                html += '<th scope="col" class="textAlignCenter">Stage</th>'
                html += '<th scope="col" class="textAlignCenter">Task-In-Use</th>'
                html += '</tr>'
                html += '</thead>'
                html += '<tbody>'
                            
                # "inUsedBy": {'available': False, 'activeUsers': {'sessionId': '11-04-2022-10:26:25:988063', 'user': 'Hubert Gee', 'stage': None, 'task': None}, 'waitList': [{'sessionId': '11-05-2022-09:37:23:403861', 'user': 'Hubert Gee', 'stage': None, 'task': None}, {'sessionId': '11-05-2022-10:13:25:068764', 'user': 'Hubert Gee', 'stage': None, 'task': None}, {'sessionId': '11-05-2022-10:25:48:431241', 'user': 'Hubert Gee', 'stage': None, 'task': None}], 'isAvailable': False}

                # {'sessionId': '09-12-2024-15:08:12:023213', 'overallSummaryFile': None, 'user': 'Hubert Gee', 'stage': None, 'task': None}
                for inUsedBy in envMgmtObj.getActiveUsers():
                    sessionId = inUsedBy.get('sessionId')
                    overallSummaryFile= inUsedBy.get('overallSummaryFile')
                    stage = inUsedBy.get('stage', None)
                    task = inUsedBy.get('task', None)
                    user = inUsedBy.get('user', 'Unknown')
                    if overallSummaryFile and os.path.exists(overallSummaryFile):
                        data = readYaml(overallSummaryFile)
                        user = data['user']
                    
                    html += '<tr>'
                    html += f'<td class="textAlignCenter"><input type="checkbox" name="envActiveUsersCheckboxes" env="{env}" sessionId="{sessionId}" user="{user}" overallSummaryFile="{overallSummaryFile}" stage="{stage}" task="{task}" /></td>'
                    html += f'<td class="textAlignCenter">{user}</td>'
                    html += f'<td class="textAlignCenter">{sessionId}</td>'
                    html += f'<td class="textAlignCenter">{stage}</td>'
                    html += f'<td class="textAlignCenter">{task}</td>'
                    html += f'</tr>'

                html += '</tbody>'
                html += '</table>' 
                            
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvActiveUsers', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'tableData': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
 
class GetWaitList(APIView):
    swagger_schema = None
    def post(self, request):
        """ 
        "waitList": [{"task": "LoadCore",
                      "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                      "user": "rocky"
                     },
                     {"task": "LoadCore",
                      "sessionId": "11-01-2022-04:23:05:749724_rocky_1test",
                      "user": "rocky"}]
        """
        user = AccountMgr().getRequestSessionUser(request)
        envNamespace = request.data.get('env', None)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"env": envNamespace}
            restApi = '/api/v1/env/envWaitList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetWaitList')
            html = response.json()['tableData'] 
                   
        else:
            if '-' in envNamespace:
                env = envNamespace.replace('-', '/')
            else:
                env = envNamespace

            try:
                envMgmtObj = EnvMgmt.ManageEnv(env)

                # waitList: [{'task': 'LoadCore', 'sessionId': '11-01-2022-04:21:00:339301_rocky_200Loops', 'user': 'rocky'}, {'task': 'LoadCore', 'sessionId': '11-01-2022-04:23:05:749724_rocky_1test', 'user': 'rocky'}]
                waitList = envMgmtObj.getWaitList()

                html = '<table id="envWaitListTable" class="mt-2 table table-sm table-bordered table-fixed tableFixHead tableMessages">' 
                html += '<thead>'
                html += '<tr>'
                html += '<th scope="col">Remove</th>'
                html += '<th scope="col" class="textAlignCenter">User</th>'
                html += '<th scope="col" class="textAlignCenter">SessionId</th>'
                html += '<th scope="col" class="textAlignCenter">Stage</th>'
                html += '<th scope="col" class="textAlignCenter">Task-In-Waiting</th>'
                html += '</tr>'
                html += '</thead>'
                html += '<tbody>'
                
                # {'sessionId': '09-12-2024-15:20:01:972920', 'overallSummaryFile': None, 'user': 'CLI: hgee', 'stage': None, 'task': None}
                for eachWait in waitList:
                    sessionId = eachWait['sessionId']
                    stage     = eachWait['stage']
                    task      = eachWait['task']
                    user      = eachWait.get('user', 'Unknown')
                    overallSummaryFile = eachWait['overallSummaryFile']
                    
                    if overallSummaryFile and os.path.exists(overallSummaryFile):
                        data = readYaml(overallSummaryFile)
                        user = data['user'] 
                                   
                    html += '<tr>'
                    html += f'<td class="textAlignCenter"><input type="checkbox" name="envWaitListCheckboxes" env="{env}" user="{user}" sessionId="{sessionId}" stage="{stage}" task="{task}"/></td>'
                    html += f'<td class="textAlignCenter">{user}</td>'
                    html += f'<td class="textAlignCenter">{sessionId}</td>'
                    html += f'<td class="textAlignCenter">{stage}</td>'
                    html += f'<td class="textAlignCenter">{task}</td>'
                    html += f'</tr>'
                    
                html += '</tbody>'       
                html += '</table>'
                
            except Exception as errMsg:
                status = 'failed'
                errorMsg = errMsg
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvWaitList',
                                          msgType='Error', msg=errorMsg,
                                          forDetailLogs=f'GetEnvWaitList: {traceback.format_exc(None, errMsg)}') 
            
        return Response(data={'tableData': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
                    
class IsEnvAvailableRest(APIView):
    env = openapi.Parameter(name='env', description="The name of the envGroup/env",
                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)        
    @swagger_auto_schema(tags=['/api/v1/env/isEnvAvailable'], operation_description="Verify if the env is available",
                         manual_parameters=[env])
    def post(self, request):
        """
        Description: 
            Verify if the env is available

        POST /api/v1/envs/isEnvAvailable
        
        Example:
            curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X POST http://192.168.28.10:8000/api/v1/env/isEnvAvailable?env=<env name>
            
        Return:
            A list of environments
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        isAvailable = False
        env = None
        
        # http://ip:port/api/v1/env/activeUsers&env=env
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                env = request.GET.get('env')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsEnvAvailableRest', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'env': 'loadcoreSample', 'sessionId': '02-04-2023-08:53:15:021768_7277', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json', 'user': 'hgee', 'stage': 'Teardown', 'task': 'CustomPythonScripts', 'trackUtilization': False, 'webhook': True}
            try:
                env = request.data['env']
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsEnvAvailableRest', msgType='Error',
                                          msg=errorMsg, forDetailLogs=errorMsg)
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"env": env}
            restApi = '/api/v1/env/isEnvAvailable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='IsEnvAvailableRest')
            isAvailable = response.json()['isAvailable']       
        else:
            if env is None:
                return Response(data={'status': 'failed', 'errorMsg': 'You must provide an env name'}, 
                                status=HtmlStatusCodes.error)
                             
            try:
                # env: Samples/pythonSample 
                envObj = EnvMgmt.ManageEnv(env=env)                 
                isAvailable = envObj.isEnvAvailable()
                del envObj

            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                isAvailable = False
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsEnvAvailableRest', msgType='Error',
                                          msg=errorMsg, forDetailLogs=errorMsg)

        return Response(data={'isAvailable': isAvailable, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
     
class GetActiveUsers(APIView):
    env = openapi.Parameter(name='env', description="The name of the env",
                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    @swagger_auto_schema(tags=['/api/v1/env/activelist'], operation_description="Get a list of users using this env",
                         manual_parameters=[env])
    def get(self, request):
        """
        Description: 
            Return a list of actively reserved Envs
        
        No parameters required

        GET /api/v1/envs/activeUsers
        
        Example:
            curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X GET http://192.168.28.10:8000/api/v1/env/activeUsers?env=<env name>
            
        Return:
            A list of environments
        """
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        activeUsers = []
        env = None
        
        # http://ip:port/api/v1/env/activeUsers&env=env
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                env = request.GET.get('env')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetActiveUsers', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
             
        # JSON format
        if request.data:
            # <QueryDict: {'env': 'loadcoreSample', 'sessionId': '02-04-2023-08:53:15:021768_7277', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json', 'user': 'hgee', 'stage': 'Teardown', 'task': 'CustomPythonScripts', 'trackUtilization': False, 'webhook': True}
            try:
                env = request.data['env']
            except Exception as errMsg:
                errorMsg = f'getActiveUsers: Unexpected param: {request.data}'
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetActiveUsers', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            if env is None:
                return Response(data={'status': 'failed', 'errorMsg': 'You must provide an env name'}, status=HtmlStatusCodes.error)
            
            params = {"env": env}
            restApi = '/api/v1/env/activeUsers'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetActiveUsers')
            activeUsers = response.json()['activeUsers'] 
                   
        else:                                    
            try:    
                # env: Samples/pythonSample 
                envObj = EnvMgmt.ManageEnv(env=env)                     
                activeUsers = envObj.getActiveUsers()
                del envObj

            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                activeUsers = []
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetActiveUsers', msgType='Error',
                                          msg=errorMsg, forDetailLogs=errorMsg)
        
        return Response(data={'activeUsers': activeUsers, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ReserveEnv(APIView):
    env = openapi.Parameter(name='env', description="The env name to reserve",
                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)           
    @swagger_auto_schema(tags=['/api/v1/env/reserveEnv'], operation_description="Reserve an Env",
                         manual_parameters=[env])
    def post(self, request):
        """ 
        User manually clicked the reserve button on the UI
        Go on the env wait-list.
        Note: The reserve button has no stage and task
        
        curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X POST http://192.168.28.10:8000/api/v1/env/reserveEnv?env=hubogee
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        sessionId = getTimestamp()
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None

        if request.GET:
            # Rest APIs with inline params come in here
            envNamespace = request.GET.get('env', None)
            
            # For cron jobs
            reservationUser = request.GET.get('reservationUser', user)
            removeJobAfterRunning = convertStrToBoolean(request.GET.get('removeJobAfterRunning', False))

            # For cronjobs
            # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
            #  'month': '\\*', 'day': '\\*', 'hour': '17', 'minute': '48', 'dayOfWeek': '\\*'}
            release_minute        = request.GET.get('release_minute', '*')
            release_hour          = request.GET.get('release_hour', '*')
            release_dayOfMonth    = request.GET.get('release_dayOfMonth', '*')
            release_month         = request.GET.get('release_month', '*')
            release_dayOfWeek     = request.GET.get('release_dayOfWeek', '*')
             
        if request.data:
            # Scheduler comes in here
            # <QueryDict: {'env': pythonSample}
            # DOMAIN=Communal/Samples/demoEnv1
            envNamespace = request.data.get('env', None)
            
            # For cron jobs
            reservationUser = request.data.get('reservationUser', user)
            removeJobAfterRunning = convertStrToBoolean(request.data.get('removeJobAfterRunning', False))

            # releaseJob = f'{release_minute} {release_hour} {release_dayOfMonth} {release_month} {release_dayOfWeek} {cronjobUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&env={env}&removeJobAfterRunning=True&release_minute={release_minute}&release_hour={release_hour}&release_dayOfMonth={release_dayOfMonth}&release_month={release_month}&release_dayOfWeek={release_dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/env/releaseEnv'
            release_minute        = request.data.get('release_minute', '*')
            release_hour          = request.data.get('release_hour', '*')
            release_dayOfMonth    = request.data.get('release_dayOfMonth', '*')
            release_month         = request.data.get('release_month', '*')
            release_dayOfWeek     = request.data.get('release_dayOfWeek', '*')
                                            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"env": envNamespace, 'reservationUser': reservationUser, 'removeJobAfterRunning': removeJobAfterRunning}
            restApi = '/api/v1/env/reserveEnv'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ReserveEnv')
        else:
            # envNamespace: /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/qaSample.yml
            if envNamespace is None:
                return Response(data={'status': 'failed', 'errorMsg': 'You must provide an env name'}, status=HtmlStatusCodes.error)

            # env = /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/qaSample.yml
            if '-' in envNamespace:
                env = envNamespace.replace('-', '/')
            else:
                env = envNamespace
            
            try:
                if removeJobAfterRunning:
                    removeJobList = {'jobSearchPattern': f'env={env}', 'minute': release_minute, 'hour': release_hour, 
                                     'month': release_month, 'dayOfMonth': release_dayOfMonth, 'dayOfWeek': release_dayOfWeek} 
                    JobSchedulerAssistant().removeCronJobs([removeJobList], dbObj=DB.name, queryName='env')

                    '''
                    if RedisMgr.redis:
                        keyName = f'scheduler-remove-{env}'
                        
                        # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                         #  'month': '\\*', 'day': '\\*', 'hour': '8', 'minute': '28', 'dayOfWeek': '\\*'} 
                        removeJobList = {'jobSearchPattern': f'env={env}', 'minute': release_minute, 'hour': release_hour, 
                                          'month': release_month, 'dayOfMonth': release_dayOfMonth, 'dayOfWeek': release_dayOfWeek}  
                    
                        RedisMgr.redis.write(keyName=keyName, data=removeJobList)
                    
                    else:
                        # NOTE: redis is not connected
                        pass
                    '''
            
                envMgmtObj = EnvMgmt.ManageEnv(env)

                if envMgmtObj.isUserInActiveUsersList(reservationUser):
                    status = 'failed'
                    errorMsg = f'The user is already actively using the env: {reservationUser}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
                    return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)

                if envMgmtObj.isUserInWaitList(user):
                    status = 'failed'
                    errorMsg = f'the user is already in the wait list: {reservationUser}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
                    return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
                result = envMgmtObj.reserveEnv(sessionId=sessionId, user=reservationUser)
                if result and result[0] == 'success':
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Success',
                                              msg=result[1], forDetailLogs='')
                               
                if result and result[0] == 'failed':
                    status = 'failed'
                    if result:
                        errorMsg = result[1]
                    else:
                        errorMsg = 'Unknown reason'
                        
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')

                envFullPath = envMgmtObj.envFullPath 
                envDomain = envMgmtObj.getEnvDomain()                 
                envPortGroups = envMgmtObj.getPortGroups()
                for portGroup in envPortGroups:
                    if ManagePortGroup(envDomain, portGroup).isPortGroupExists():
                        ManagePortGroup(envDomain, portGroup).reservePortGroup(sessionId=sessionId, user=user)
                
            except Exception as errMsg:
                status = 'failed'
                errorMsg = errMsg
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

    
class ReserveEnvUI(APIView):
    swagger_schema = None
    
    def post(self, request):
        """
        Description:
            Called by keystack.py to automatically reserve an env

        POST /api/v1/env/reserve
        
        Parameters:
            sessionId: The keystack session ID
            overallSummaryFile: keystack.py overll summary detail json data
                        /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json
            env: The env to reserve. Example: pythonSample
            user: user from keystack
            stage: stage
            task: task
            trackUtilization: <bool>: For keystack.py.lockAndWaitForEnv().  This function calls reserveEnv() and amIRunning().
                         Both functions increment env utilization. We want to avoid hitting it twice.
                         So exclude hitting it here in reserveEnv and let amIRunning hit it.
        
        Usage:
            envObj = EnvMgmt.ManageEnv(env=self.taskProperties['env'])                          
            envMgmtObj.reserveEnv(sessionId=sessionId, overallSummaryFile=overallSummaryFile, 
                                  user=user, stage=stage, task=task, trackUtilization=False)
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/reserve
            
        Return:
            status and error
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                sessionId = request.GET.get('sessionId')
                overallSummaryFile = request.GET.get('overallSummaryFile')
                env = request.GET.get('env')
                userReserving = request.GET.get('user')
                stage = request.GET.get('stage')
                task = request.GET.get('task')
                trackUtilization = request.GET.get('trackUtilization')
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='reserveEnvUI', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'env': 'loadcoreSample', 'sessionId': '02-04-2023-08:53:15:021768_7277', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json', 'user': 'hgee', 'stage': 'Teardown', 'task': 'CustomPythonScripts', 'trackUtilization': False, 'webhook': True}
            try:
                sessionId = request.data['sessionId']
                overallSummaryFile = request.data['overallSummaryFile']
                env = request.data['env']
                userReserving = request.data['user']
                stage = request.data['stage']
                task = request.data['task']
                trackUtilization = request.data['trackUtilization']
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='reserveEnvUI', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"sessionId": sessionId, "overallSummaryFile": overallSummaryFile, "env": env, "user": userReserving,
                      "stage": stage, "task": task, "trackUtilization": trackUtilization}
            restApi = '/api/v1/env/reserve'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ReserveEnvUI')   
        else:            
            try:                       
                # env: Samples/pythonSample 
                envObj = EnvMgmt.ManageEnv(env=env) 
       
                result = envObj.reserveEnv(sessionId=sessionId, overallSummaryFile=overallSummaryFile, 
                                           user=user, stage=stage, task=task, trackUtilization=trackUtilization)

                if result and result[0] != 'success':
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReserveEnvUI', msgType='Failed',
                                              msg=result[1], forDetailLogs='')
                del envObj

                if result and result[0] == 'failed':
                    status = 'failed'
                    error = result[1]
                    statusCode = HtmlStatusCodes.error
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='reserveEnvUI', msgType='Failed',
                                              msg=f'sessionId:{sessionId} Env:{env}  user:{user} stage:{stage} task:{task}<br>error:{error}',
                                              forDetailLogs='')
                else:    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='reserveEnvUI', msgType='Success',
                                              msg=f'sessionId:{sessionId}, stage:{stage}, task:{task}, env:{env}', forDetailLogs='')
                
            except Exception as errMsg:
                errorMsg = f'envViews:reserve: {traceback.format_exc(None, errMsg)}'
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='reserveEnvUI', msgType='Error',
                                          msg=f'sessionId:{sessionId}, stage:{stage}, task:{task}, env:{env}<br>error: {errorMsg}', 
                                          forDetailLogs=errorMsg)
                               
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ReleaseEnv(APIView):
    env = openapi.Parameter(name='env', description="The env name to release",
                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)           
    @swagger_auto_schema(tags=['/api/v1/env/releaseEnv'], operation_description="Release an Env",
                         manual_parameters=[env])
    def post(self, request):
        """ 
        This function releases the env reserved manually and also while a pipeline session is actively running
        
        Release button to release the current active-usersession/user from the env
        
        Checks the env if a pipeline is actively using it
        Allow users to release the env while the pipeline status ==  Running
        Especially if the current status is holdEnvsIfFailed. Sometimes there is no link to releaseEnv.
        So this mechanisma is a way for users to release the env.
        
        curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X POST http://192.168.28.10:8000/api/v1/env/releaseEnv?env=testbed1
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        if request.GET:
            # Rest APIs with inline params come in here
            env = request.GET.get('env', None)
            
            # For cronjobs
            # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
            #  'month': '\\*', 'day': '\\*', 'hour': '17', 'minute': '48', 'dayOfWeek': '\\*'}
            removeJobAfterRunning = convertStrToBoolean(request.GET.get('removeJobAfterRunning', False))
            reservationUser       = request.GET.get('reservationUser', None)
            release_minute        = request.GET.get('release_minute', '*')
            release_hour          = request.GET.get('release_hour', '*')
            release_dayOfMonth    = request.GET.get('release_dayOfMonth', '*')
            release_month         = request.GET.get('release_month', '*')
            release_dayOfWeek     = request.GET.get('release_dayOfWeek', '*')
            
        if request.data:
            env = request.data.get('env', None)

            # For cronjobs
            # releaseJob = f'{release_minute} {release_hour} {release_dayOfMonth} {release_month} {release_dayOfWeek} {cronjobUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&env={env}&removeJobAfterRunning=True&release_minute={release_minute}&release_hour={release_hour}&release_dayOfMonth={release_dayOfMonth}&release_month={release_month}&release_dayOfWeek={release_dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/env/releaseEnv'
            removeJobAfterRunning = convertStrToBoolean(request.data.get('removeJobAfterRunning', False))
            reservationUser       = request.data.get('reservationUser', None)
            release_minute        = request.data.get('release_minute', '*')
            release_hour          = request.data.get('release_hour', '*')
            release_dayOfMonth    = request.data.get('release_dayOfMonth', '*')
            release_month         = request.data.get('release_month', '*')
            release_dayOfWeek     = request.data.get('release_dayOfWeek', '*')
                        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"env": env, 'removeJobAfterRunning': removeJobAfterRunning, 'reservationUser': reservationUser,
                      'release_minute': release_minute, 'release_hour': release_hour, 'release_dayOfMonth': release_dayOfMonth,
                      'release_month': release_month, 'release_dayOfWeek': release_dayOfWeek}
            restApi = '/api/v1/env/releaseEnv'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ReleaseEnv')       
        else:
            if env is None:
                return Response(data={'status': 'failed', 'errorMsg': 'You must provide an env name'}, status=HtmlStatusCodes.error)
            
            if '/' in env:
                envNamespace = env.replace('/', '-')
            else:
                envNamespace = env

            # releaseEnv: /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml
            try:      
                envMgmtObj = EnvMgmt.ManageEnv()
                # [{'sessionId': '11-08-2022-15:10:36:026486_1231', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/11-08-2022-15:10:36:026486_1231/overallSummary.json', 'user': 'hgee', 'stage': 'Test', 'task': 'CustomPythonScripts'}]
                envMgmtObj.setenv = env
                details = envMgmtObj.getEnvDetails()
                
                if len(details['activeUsers']) > 0:
                    # topActiveUser: {'sessionId': '11-16-2022-14:05:18:399384_hubogee', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/11-16-2022-14:05:18:399384_hubogee/overallSummary.json', 'user': 'hgee', 'stage': 'DynamicVariableSample', 'task': 'CustomPythonScripts'}
                    
                    topActiveUser = details['activeUsers'][0]
                    if topActiveUser["user"] not in [user, reservationUser] and getUserRole(request) != 'admin':
                        status = 'failed'
                        errorMsg = f'User not allowed to release a different active-user: {topActiveUser["user"]}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', 
                                                  msgType='Failed', msg=errorMsg, forDetailLogs='')
                        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
                    
                    # Check if the env session is currently runing. Can't just release the env when it's testing.
                    # But allow to release the env if it's manually reserved 
                    # If overallSummaryFile exists, this means the session is an automated test. Not manual user.           
                    if topActiveUser['overallSummaryFile']:
                        overallSummaryFile = topActiveUser['overallSummaryFile']
                        if os.path.exists(overallSummaryFile):
                            overallSummaryData = readJson(overallSummaryFile)
                            resultPath = '/'.join(overallSummaryFile.split('/')[:-1])
                            envMgmtFile = f'/{resultPath}/.Data/EnvMgmt/STAGE={topActiveUser["stage"]}_TASK={topActiveUser["task"]}_ENV={envNamespace}.json'
                            
                            # Note: Allow users to release the env while the pipeline status ==  Running
                            #       Especially if the current status is holdEnvsIfFailed. Sometimes there is no link to releaseEnv.
                            #       So this mechanisma is a way for users to release the env.
                            if overallSummaryData['status'] == 'Running':
                                #  [{'sessionId': '12-05-2024-08:11:06:107632_4558', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/12-05-2024-08:11:06:107632_4558/overallSummary.json', 'user': 'CLI: hgee', 'stage': 'Test', 'task': 'layer3'}]
                                currentActiveUser = envMgmtObj.getActiveUsers()
                                # removeFromActiveUsersList() will remove the active user from the env and calls refreshEnv() 
                                # to get the next task in the waitlist. The next task in the waitlist is prioritized by
                                # the current active-user sessionId
                                envMgmtObj.removeFromActiveUsersList(currentActiveUser)
                                
                                # Release portGroup too
                                envFullPath = envMgmtObj.envFullPath 
                                envDomain = envMgmtObj.getEnvDomain()                 
                                envPortGroups = envMgmtObj.getPortGroups()
                                for portGroup in envPortGroups:
                                    if ManagePortGroup(envDomain, portGroup).isPortGroupExists():
                                        ManagePortGroup(envDomain, portGroup).releasePortGroup()
                                        
                                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
                            else:
                                # Completed or Aborted
                                if overallSummaryData['holdEnvsIfFailed']:
                                    if RedisMgr.redis:
                                        keyName = f'envMgmt-{topActiveUser["sessionId"]}-STAGE={topActiveUser["stage"]}_TASK={topActiveUser["task"]}_ENV={envNamespace}'
                                        envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                                    else:
                                        envMgmtData = readJson(envMgmtFile)
                                    
                                    if 'result' in envMgmtData and envMgmtData['result'] == 'Failed' and envMgmtData['envIsReleased'] == False:
                                        status = 'failed'
                                        errorMsg = f'The Env:{env} is on hold for test failure debugging. It has to be released on the pipeline sessionId: {topActiveUser["sessionId"]}'
                                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', msgType='Error', msg=errorMsg, forDetailLogs='')
                                        return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
     
                    envMgmtObj.releaseEnv()
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', msgType='Success',
                                              msg=f'Env: {env}', forDetailLogs='') 
                    
                    envFullPath = envMgmtObj.envFullPath 
                    envDomain = envMgmtObj.getEnvDomain()                 
                    envPortGroups = envMgmtObj.getPortGroups()
                    for portGroup in envPortGroups:
                        if ManagePortGroup(envDomain, portGroup).isPortGroupExists():
                            ManagePortGroup(envDomain, portGroup).releasePortGroup()

                # Remove the job from the scheduler
                if removeJobAfterRunning:
                    # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                    #  'month': '\\*', 'day': '\\*', 'hour': '8', 'minute': '28', 'dayOfWeek': '\\*'} 
                    removeJobList = [{'jobSearchPattern': f'env={env}', 'minute': release_minute, 'hour': release_hour, 
                                      'month': release_month, 'dayOfMonth': release_dayOfMonth, 'dayOfWeek': release_dayOfWeek}]
                    
                    JobSchedulerAssistant().removeCronJobs(removeJobList, dbObj=DB.name, queryName='env')

                    '''
                    if RedisMgr.redis:
                        keyName = f'scheduler-remove-{env}'
                        
                        # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                        #  'month': '\\*', 'day': '\\*', 'hour': '8', 'minute': '28', 'dayOfWeek': '\\*'} 
                        removeJobList = {'jobSearchPattern': f'env={env}', 'minute': release_minute, 'hour': release_hour, 
                                        'month': release_month, 'dayOfMonth': release_dayOfMonth, 'dayOfWeek': release_dayOfWeek}  
                    
                        print('\n--- writeToRedis remove:', keyName, removeJobList)
                        RedisMgr.redis.write(keyName=keyName, data=removeJobList)
                    else:
                        # NOTE: redis is not connected
                        pass
                    '''
                    
            except Exception as errMsg:
                status = 'failed'
                errorMsg = traceback.format_exc(None, errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnv', msgType='Error',
                                          msg=errorMsg, 
                                          forDetailLogs=f'ReleaseEnv: {errorMsg}')
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class ReleaseEnvOnFailure(APIView):
    """ 
    sessionMgmt release-env button for each stage/task/env failure.
    If test failed, envs are on hold for debugging. A Release Envs button is created and blinking.
    
    curl -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X POST http://192.168.28.10:8000/api/v1/env/releaseEnvOnFailure?env=hubogee&stage=Test&task=Demo&sessionId=<sessionId>&resultTimestampPath=<timestamp path>
    """
    sessionId =   openapi.Parameter(name='sessionId', description="The sessionId of the test",
                                    required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 
    sessionUser = openapi.Parameter(name='sessionUser', description="The test sessionId user name",
                                    required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 
    stage =       openapi.Parameter(name='stage', description="The test stage name",
                                    required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 
    task =      openapi.Parameter(name='task', description="The test stage task name",
                                    required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    resultTimestampPath = openapi.Parameter(name='resultTimestampPath', description="The full path to the test sessionId result folder",
                                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)          
    env = openapi.Parameter(name='env', description="The env name to release",
                            required=True,
                            in_=openapi.IN_QUERY,
                            type=openapi.TYPE_STRING)           
    @swagger_auto_schema(tags=['/api/v1/env/releaseEnvOnFailure'],
                         operation_description="Release an Env from a test failure with param holdEnvsIfFailed",
                         manual_parameters=[sessionId, sessionUser, stage, task, resultTimestampPath, env])
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'

        if request.GET:
            # Rest APIs with inline params come in here
            sessionId   = request.GET.get('sessionId', None)
            sessionUser = request.GET.get('sessionUser', None)
            stage       = request.GET.get('stage', None)
            task        = request.GET.get('task', None)
            env         = request.GET.get('env', None)
            # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/07-30-2023-17:12:37:438387_9839
            resultTimestampPath = request.GET.get('resultTimestampPath', None)
                     
        if request.data:   
            sessionId     = request.data.get('sessionId', None)
            sessionUser   = request.data.get('user', None)
            stage         = request.data.get('stage', None)
            task          = request.data.get('task', None)
            env           = request.data.get('env', None)
            # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-pythonSample/07-30-2023-17:12:37:438387_9839
            resultTimestampPath = request.data.get('resultTimestampPath', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"user": sessionUser, 'sessionId': sessionId, 'stage': stage,
                      'task': task, 'env': env, 'resultTimestampPath': resultTimestampPath}
            restApi = '/api/v1/env/releaseEnvOnFailure'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ReleaseEnvOnFailure') 
        else:
            for verifyParam in [sessionId, sessionUser, stage, task, env]:
                if verifyParam is None:
                    return Response(data={'status': 'failed', 'errorMsg': 'You must provide param values for params: sessionId, sessionUser, stage, task, env, resultTimestampPath'}, status=HtmlStatusCodes.error)
            
            if '/' in env:
                env = env.replace('/', '-')
                
            envMgmtDataFile = f'{resultTimestampPath}/.Data/EnvMgmt/STAGE={stage}_TASK={task}_ENV={env}.json'
            testSessionLogPath = f'{resultTimestampPath}/{GlobalVars.sessionLogFilename}'
            timestampFolderName = resultTimestampPath.split('/')[-1]
            keyName = f'envMgmt-{timestampFolderName}-STAGE={stage}_TASK={task}_ENV={env}'
            
            # Change it back
            if '-' in env:
                env = env.replace('-', '/')

            regexMatch = search('DOMAIN=(.*?)/.*', env)
            if regexMatch:
                domain = regexMatch.group(1)
                                   
            for retry in range(1, 4):
                try:
                    if RedisMgr.redis:
                        envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                    else:            
                        envMgmtData = readJson(envMgmtDataFile)
                        
                    # env = DOMAIN=Communal/Samples/demoEnv1
                    envMgmtObj = EnvMgmt.ManageEnv(env)
                    envMgmtObj.setupLogger(testSessionLogPath)
                    session = {'sessionId':sessionId, 'stage':stage, 'task':task, 'user':sessionUser}
                    
                    envMgmtObj.removeFromActiveUsersList([session])
                    #envMgmtData['envIsReleased'] = True
                    
                    regexMatch = search('DOMAIN=(.*?)/.*', env)
                    if regexMatch:
                       domain = regexMatch.group(1)

                    #if RedisMgr.redis:
                    #    RedisMgr.redis.updateKey(keyName=keyName, data=envMgmtData)
                    #else:
                    #    writeToJson(envMgmtDataFile, envMgmtData)
                    
                    # Check env ymal file for port-group existence
                    envFilePath = f'{GlobalVars.envPath}/{env}.yml'
                    envData = readYaml(envFilePath) 
                    portGroups = envData.get('portGroups', None)
                    if portGroups:
                        for portGroup in portGroups:
                            ManagePortGroup(domain, portGroup).removeFromActiveUsersListUI([session])

                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnvOnFailure', msgType='Success',
                                              msg=f'{session}', forDetailLogs='')                    
                    break 
                   
                except Exception as errMsg:
                    if retry < 4:
                        sleep(3)
                        continue
                    else:
                        error = str(errMsg)
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleaseEnvOnFailure', msgType='Error',
                                                  msg=f'Updating .Data/EnvMgmt json file failed. Retrying {retry}/5x.<b>{errMsg}', 
                                                  forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
     
class DeleteEnvGroups(APIView):
    swagger_schema = None
    selectAll         = openapi.Parameter(name='selectAll', description="Delete all env groups",
                                          required=False, in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN)
    selectedEnvGroups = openapi.Parameter(name='selectedEnvGroups', description="A list of env groups to delete in full paths",
                                          required=False, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)           
    @swagger_auto_schema(tags=['/api/v1/env/deleteEnvGroups'], operation_description="Verify if the env is available",
                         manual_parameters=[selectAll, selectedEnvGroups])
    @verifyUserRole(webPage=Vars.webpage, action='DeleteEnvGroups', exclude='engineer')
    def post(self, request):
        """
        Description: 
            Delete Env Groups

        POST /api/v1/env/deleteEnvGroups
        
        Parameters:
            selectAll: True|False.  Delete all env groups.
            selectedEnvGroups: A list of env groups in full paths.
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/deleteEnvGroups
            
        Return:
            status and error
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                selectAll = request.GET.get('selectAll')
                selectedEnvGroups = request.GET.get('selectedEnvGroups')
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnvGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'env': 'loadcoreSample', 'sessionId': '02-04-2023-08:53:15:021768_7277', 'overallSummaryFile': '/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/02-04-2023-08:53:15:021768_7277/overallSummary.json', 'user': 'hgee', 'stage': 'Teardown', 'task': 'CustomPythonScripts', 'trackUtilization': False, 'webhook': True}
            try:
                selectAll = request.data['selectAll']
                selectedEnvGroups = request.data['selectedEnvGroups']
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnvGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"selectAll": selectAll, "selectedEnvGroups": selectedEnvGroups}
            restApi = '/api/v1/env/deleteEnvGroups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteEnvGroups') 
        else:            
            try:
                if selectAll:
                    envPath = f'{GlobalVars.keystackTestRootPath}/Envs'
                    for root,dirs,files in os.walk(envPath):
                        # /opt/KeystackTests/Envs/LoadCore
                        regexMatch = search(f'.+(/Envs.+)$', root)
                        if regexMatch:
                            # /opt/KeystackTests/Envs
                            # /opt/KeystackTests/Envs/qa
                            rmtree(regexMatch.group(1))
                
                if selectedEnvGroups:
                    for envGroup in selectedEnvGroups:
                        rmtree(envGroup)
                                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnvGroups', msgType='Success',
                                          msg=f'selectAll:{selectAll}, envs:{selectedEnvGroups}', forDetailLogs='')
                
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='deleteEnvGroups', msgType='Error',
                                          msg=f'selectAll:{selectAll}, envs:{selectedEnvGroups}<br>error: {errorMsg}', 
                                          forDetailLogs=errorMsg)
                               
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

    
class AmINext(APIView):
    swagger_schema = None

    def post(self, request):
        """
        Description: 
            Check to see if the task/env is running after reserving the env.
            It could be in the waitlist.

        POST /api/v1/env/amINext
        
        Parameters:
            sessionId: The keystack session ID
            env: The env to reserve. Example: pythonSample
            user: user from keystack
            stage: stage
            task: task
            webhook: <optional>
        
        Usage:
            envObj = EnvMgmt.ManageEnv(env=self.taskProperties['env'])
            envMgmtObj.amIRunning(user, sessionId, stage, task)                          
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/amINext
            
        Return:
            status and error
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if request.GET:
            # Rest APIs with inline params come in here
            try:
                sessionId = request.GET.get('sessionId')
                overallSummaryFile = request.GET.get('overallSummaryFile')
                env = request.GET.get('env')
                userReserving = request.GET.get('user')
                stage = request.GET.get('stage')
                task = request.GET.get('task')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AmINext', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                sessionId = request.data['sessionId']
                overallSummaryFile = request.data['overallSummaryFile']
                env = request.data['env']
                userReserving = request.data['user']
                stage = request.data['stage']
                task = request.data['task']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AmINext', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"overallSummaryFile": overallSummaryFile, "sessionId": sessionId, 
                      "user": userReserving, "env": env, "stage": stage, "task": task}
            restApi = '/api/v1/env/amINext'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='AmINext')
        else:                    
            try:      
                envObj = EnvMgmt.ManageEnv(env=env)                      
                result = envObj.amIRunning(user, sessionId, stage, task, overallSummaryFile) 
                del envObj

                # return ('failed', str(errMsg), traceback.format_exc(None, errMsg))
                if result not in [True, False] and result[0] == 'failed':
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AmINext', msgType='Error',
                                              msg=result[1], forDetailLogs=result[2])
                    result = False

            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                result = False
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AmINext', msgType='Error',
                                          msg=errorMsg, forDetailLogs=errorMsg)
                             
        return Response(data={'status': status, 'errorMsg': errorMsg, 'result':result}, status=statusCode)


class Reset(APIView):
    #swagger_schema = None
        
    @verifyUserRole(webPage=Vars.webpage, action='Reset', exclude='engineer')
    def post(self, request):
        """
        Description: 
            Remove the user/env from the active env list

        POST /api/v1/env/reset
        
        Parameters:
            env: The env to reset
            webhook: <optional>
        
        Usage:
            envObj = EnvMgmt.ManageEnv(env=self.taskProperties['env'])
            envObj.reset()                         
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/reset
            
        Return:
            status and error
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # http://ip:port/api/v1/envMgmt/reserveEnv?sessionId=sessionId&env=env
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                env = request.GET.get('env')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
             
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                env = request.data['env']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"env": env}
            restApi = '/api/v1/env/reset'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ResetEnv')
        else:                    
            try:    
                envObj = EnvMgmt.ManageEnv(env=env)
                result = envObj.resetEnv()
                del envObj
                if result != True:
                    status = 'failed'
                    errorMsg = "DB failed to perform an env reset"
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='resetEnv', msgType='Failed',
                                              msg=f'Env:{env}<br>error: {errorMsg}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='resetEnv', msgType='Success',
                                              msg=f'Env:{env}', forDetailLogs='')
                    
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='resetEnv', msgType='Error',
                                          msg=f'Env:{env}<br>error: {errorMsg}', forDetailLogs=errorMsg)
                               
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

            
class RemoveFromActiveUsersListUI(APIView):
    swagger_schema = None
 
    def post(self, request):
        """
        Description: 
            Called by keystack.py.  Remove the user/env from the active env list

        POST /api/v1/env/removeFromActiveUsersList
        
        Parameters:
            sessionId: The keystack session ID
            user: user from keystack
            stage: stage
            task: task
            webhook: <optional>
        
        Usage:
            envObj = EnvMgmt.ManageEnv(env=self.taskProperties['env'])
            envObj.removeFromActiveUsersList([{'user':self.user, 'sessionId':self.timestampFolderName, 
                                               'stage':self.stage, 'task':self.task}])                         
                                  
        Example:
            curl -X POST http://192.168.28.7:8000/api/v1/env/removeFromActiveUsersList
            
        Return:
            status and error
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        # http://ip:port/api/v1/envMgmt/reserveEnv?sessionId=sessionId&env=env
        if request.GET:
            # Rest APIs with inline params come in here
            try:
                sessionId = request.GET.get('sessionId')
                env = request.GET.get('env')
                removeUser = request.GET.get('user')
                stage = request.GET.get('stage')
                task = request.GET.get('task')
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromActiveUsersListUI', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                sessionId = request.data['sessionId']
                env = request.data['env']
                removeUser = request.data['user']
                stage = request.data['stage']
                task = request.data['task']
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromActiveUsersListUI', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"sessionId": sessionId, "env": env, "user": removeUser, "stage": stage, "task": task}
            restApi = '/api/v1/env/removeFromActiveUsersListUI'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveFromActiveUsersListUI')  
        else:            
            try:
                envObj = EnvMgmt.ManageEnv(env=env)
                result = envObj.removeFromActiveUsersList([{'user':removeUser, 'sessionId':sessionId, 'stage':stage, 'task':task}])
                del envObj

                if result == False:
                    error = result
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromActiveUsersListUI', msgType='Failed',
                                              msg=f'Env:{env}  user:{user} stage:{stage} task:{task}<br>error:{error}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromActiveUsersListUI', msgType='Success',
                                              msg=f'Env:{env}  user:{user} stage:{stage} task:{task}', forDetailLogs='')
                                
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromActiveUsersListUI', msgType='Failed',
                                          msg=f'Env:{env}  user:{user} stage:{stage} task:{task}<br>error:{errorMsg}',
                                          forDetailLogs=errorMsg)
                               
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class RemoveEnvFromWaitList(APIView):
    def post(self, request):
        """ 
        "waitList": [{"task": "LoadCore",
                      "sessionId": "11-01-2022-04:21:00:339301_rocky_200Loops",
                      "stage": "LoadCoreTest",
                      "user": "rocky"
                     },
                     {"task": "LoadCore",
                      "sessionId": "11-01-2022-04:23:05:749724_rocky_1test",
                      "stage": "Test",
                      "user": "bullwinkle"}]
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        
        # removeList: [{'env': 'loadcoreSample', 'sessionId': '11-06-2022-07:11:12:859325', 'stage': None, 'task': None}]
        removeList = request.data.get('removeList', None)
        
        envNamespace = request.data.get('env', None)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"removeList": removeList, "env": envNamespace}
            restApi = '/api/v1/env/removeEnvFromWaitList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveEnvFromWaitList')
        else: 
            # Need to use slash for creating the env path       
            if '-' in envNamespace:
                env = envNamespace.replace('-', '/')
            else:
                env = envNamespace

            try:            
                envMgmtObj = EnvMgmt.ManageEnv(env)
                excludeRemoveFromWaitList = ''
                removedFromWaitList = ''
                sayOnceOnly = False

                for index, waiting in enumerate(removeList):
                    waitingUser = waiting['user']
                    
                    # Hubert Gee, user=Bruce Wayne, userRole=engineer 
                    if waitingUser != user and getUserRole(request) != 'admin':
                        status = 'failed'
                        errorMsg = f'User not allowed to remove another user in the wait-list: {waitingUser}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveEnvFromWaitList', 
                                                  msgType='Failed', msg=errorMsg, forDetailLogs='')
                        continue
                    
                    # {'env': 'Samples/demoEnv1', 'user': 'fromCLI: hgee', 'sessionId': '12-21-2023-15:36:26:876177_2961', 
                    # stage': 'Bringup', 'task': 'bringup'}
                    removedFromWaitList += f'user:{waiting["user"]}  sessionId:{waiting["sessionId"]}  stage:{waiting["stage"]} task:{waiting["task"]}<br>'       
                    envMgmtObj.removeFromWaitList(sessionId=waiting['sessionId'],
                                                    user=waiting['user'], 
                                                    stage=waiting['stage'],
                                                    task=waiting['task'])
                if removedFromWaitList:    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveEnvFromWaitList', msgType='Success',
                                              msg=removedFromWaitList,  forDetailLogs=f'')
 
            except Exception as errMsg:
                status = 'failed'
                errorMsg = traceback.format_exc(None, errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveEnvFromWaitList', msgType='Error',
                                          msg=errMsg, forDetailLogs=errorMsg)
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
 

class RemoveFromActiveUsersList(APIView):
    def post(self, request):
        """ 
        Remove users or sessionId from using the env
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        removeList = request.data.get('removeList', None)
        envNamespace = request.data.get('env', None)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"removeList": removeList, 'env': envNamespace}
            restApi = '/api/v1/env/removeEnvFromActiveUsersList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveFromActiveUsersList')
        else:
            if '-' in envNamespace:
                env = envNamespace.replace('-', '/') 
            else:
                env = envNamespace

            try:
                envMgmtObj = EnvMgmt.ManageEnv(env)
                excludeRemovingActiveUsers = []

                if '/' in env:
                    env = env.replace('/', '-')

                # Check if the env session is currently runing. Can't just release the env when it's testing.
                # But allow to release the env if it's manually reserved   
                # removeList: 
                #     [{'env': 'pythonSample', 'sessionId': '04-25-2023-18:13:51:640030', 'overallSummaryFile': 'None', 'stage': 'None', 'task': 'None'}]        
                for index, activeUser in enumerate(removeList): 
                    # overallSummaryFile exists only if it is a test. It doesn't exists for 
                    # manual users reserving the env. 
                    activeUserUser = activeUser['user']
                    
                    if activeUserUser != user and getUserRole(request) != 'admin':
                        status = 'failed'
                        excludeRemovingActiveUsers.append(index)
                        errorMsg = f'User not allowed to remove another active-user: {activeUserUser}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveActiveUserFromEnv', 
                                                  msgType='Failed', msg=errorMsg, forDetailLogs='')
                        continue
                    
                    overallSummaryFile = activeUser['overallSummaryFile']                      
                    if activeUser['overallSummaryFile']:
                        if os.path.exists(overallSummaryFile):
                            overallSummaryData = readJson(overallSummaryFile)
                            resultPath = '/'.join(overallSummaryFile.split('/')[:-1])
                            envMgmtFile = f'/{resultPath}/.Data/EnvMgmt/STAGE={activeUser["stage"]}_TASK={activeUser["task"]}_ENV={env}.json'
                            
                            if overallSummaryData['status'] == 'Running':
                                excludeRemovingActiveUsers.append(index)
                                status = 'failed'
                                errorMsg = f'Cannot remove an active session from a actively running session: {activeUser["sessionId"]}'
                                statusCode = HtmlStatusCodes.error
                                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveActiveUserFromEnv', 
                                                            msgType='Failed', msg=errorMsg, forDetailLogs='')
                                Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                                
                            elif overallSummaryData['holdEnvsIfFailed']:
                                if RedisMgr.redis:
                                    keyName = f'envMgmt-{activeUser["sessionId"]}-STAGE={activeUser["stage"]}_TASK={activeUser["task"]}_ENV={env}'
                                    envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                                else:        
                                    envMgmtData = readJson(envMgmtFile)
                                    
                                if envMgmtData['result'] == 'Failed' and envMgmtData['envIsReleased'] == False:
                                    excludeRemovingActiveUsers.append(index)
                                    status = 'failed'
                                    errorMsg = f'The Env:{env} is on hold for test failure debugging. It must be released in the pipeline page on pipelineId: {activeUser["sessionId"]}'
                                    statusCode = HtmlStatusCodes.error
                                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveActiveUserFromEnv', msgType='Failed', msg=errorMsg, forDetailLogs='')
                                    Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                                    
                if len(excludeRemovingActiveUsers) > 0:
                    for index in excludeRemovingActiveUsers:
                        removeList.pop(index)
                            
                envMgmtObj.removeFromActiveUsersList(removeList)
                
                for env in removeList:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUsersFromEnvActiveList', 
                                              msgType='Success',
                                              msg=f'SessionId:{env["sessionId"]} stage:{env["stage"]} task:{env["task"]}', forDetailLogs='')
                    
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveActiveUsersFromEnv', msgType='Error',
                                        msg=errorMsg, forDetailLogs=f'RemoveUsersFromEnvActiveList: {traceback.format_exc(None, errMsg)}')
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        

class ForceRemoveFromActiveUsersList(APIView):
    def post(self, request):
        """ 
        Forcefully remove users or sessionId from using the env
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        removeList = request.data.get('removeList', None)
        envNamespace = request.data.get('env', None)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"removeList": removeList, 'env': envNamespace}
            restApi = '/api/v1/env/forceRemoveEnvFromActiveUsersList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ForceRemoveFromActiveUsersList')           
        else:   
            if '-' in envNamespace:
                env = envNamespace.replace('-', '/')
            else:
                env = envNamespace

            try:
                envMgmtObj = EnvMgmt.ManageEnv(env)
                excludeRemovingActiveUsers = []

                if '/' in env:
                    env = env.replace('/', '-')

                # Check if the env session is currently runing. Can't just release the env when it's testing.
                # But allow to release the env if it's manually reserved   
                # removeList: 
                #     [{'env': 'pythonSample', 'sessionId': '04-25-2023-18:13:51:640030', 'overallSummaryFile': 'None', 'stage': 'None', 'task': 'None'}]        
                for index,activeUser in enumerate(removeList): 
                    # overallSummaryFile exists only if it is a test. It doesn't exists for 
                    # manual users reserving the env. 
                    overallSummaryFile = activeUser['overallSummaryFile']                      
                    if activeUser['overallSummaryFile']:
                        if os.path.exists(overallSummaryFile):
                            overallSummaryData = readJson(overallSummaryFile)
                            resultPath = '/'.join(overallSummaryFile.split('/')[:-1])
                            envMgmtFile = f'/{resultPath}/.Data/EnvMgmt/STAGE={activeUser["stage"]}_TASK={activeUser["task"]}_ENV={env}.json'
                            
                            if RedisMgr.redis:
                                keyName = f'envMgmt-{activeUser["sessionId"]}-STAGE={activeUser["stage"]}_TASK={activeUser["task"]}_ENV={env}'
                                envMgmtData = RedisMgr.redis.getCachedKeyData(keyName=keyName)
                            else:
                                envMgmtData = readJson(envMgmtFile)

                            envMgmtObj.removeFromActiveUsersList([{'env': envMgmtData['env'], 'sessionId': envMgmtData['sessionId'],
                                                                   'overallSummaryFile': envMgmtData['overallSummaryFile'], 
                                                                   'stage': envMgmtData['stage'], 'task': envMgmtData['task']}])
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ForceRemoveFromActiveUsersList', msgType='Error',
                                          msg=errorMsg, forDetailLogs=f'RemoveUsersFromEnvActiveList: {traceback.format_exc(None, errMsg)}')
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ResetEnv(APIView):
    """ 
    If the DB is unrepairable, reset it as last resort. 
    """
    env = openapi.Parameter(name='env', description="The env name to reset",
                            required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)           
    @swagger_auto_schema(tags=['/api/v1/env/resetEnv'], operation_description="Reset / clear the env usage",
                         manual_parameters=[ env])
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None

        if request.GET:
            # Rest APIs with inline params come in here
            env = request.GET.get('env', None)
                     
        if request.data:   
            env = request.data.get('env', None)
            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'env': env}
            restApi = '/api/v1/env/resetEnv'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ResetEnv')
            if errorMsg:
                status = 'failed'
                   
        else:
            if env is None:
                return Response(data={'status': 'failed', 'errorMsg': 'You must provide the env'}, status=statusCode)
                        
            try:
                if getUserRole(request) != 'admin':
                    status = 'failed'
                    errorMsg = f'User must have admin privilege to perform an env reset'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetEnv', 
                                              msgType='Failed', msg=errorMsg, forDetailLogs='')
                else:                 
                    envMgmtObj = EnvMgmt.ManageEnv(env)
                    envMgmtObj.resetEnv()
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetEnv', msgType='Success',
                                            msg=f'Env: {env}', forDetailLogs='')
                            
            except Exception as errMsg:
                status = 'failed'
                errorMsg = errMsg
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=f'ResetEnv: {traceback.format_exc(None, errMsg)}')
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class UpdateEnvActiveUsersAndWaitList(APIView):
    def post(self, request):
        """
        Self update port-group active-users and wait-list
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/updateActiveUsersAndWaitList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='UpdateEnvActiveUsersAndWaitList')   
        else:        
            try:
                EnvMgmt.ManageEnv().update()

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdateEnvActiveUsersAndWaitList', msgType='Success',
                                          msg='',forDetailLogs='')      
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdateEnvActiveUsersAndWaitList', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    
# ---- Env Scheduler ----
 
class AddEnvSchedule(APIView):                                           
    @verifyUserRole(webPage=Vars.webpage, action='AddEnvSchedule', exclude=['engineer'])
    def post(self, request):
        """ 
        Schedule a cron job
        
            # Example of job definition:
            # .---------------- minute (0 - 59)
            # |  .------------- hour (0 - 23)
            # |  |  .---------- day of month (1 - 31)
            # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
            # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
            # |  |  |  |  |
            # *  *  *  *  * user-name command to be executed
        """
        # body: {'minute': '*', 'hour': '*', 'dayOfMonth': '*', 'month': '*', 'dayOfWeek': '*', 'removeJobAfterRunning': False, 'controller': '192.168.28.7:8000', 'playbook': '/opt/KeystackTests/Playbooks/pythonSample.yml', 'debug': False, 'emailResults': False, 'awsS3': False, 'jira': False, 'pauseOnError': False, 'holdEnvsIfFailed': False, 'abortTestOnFailure': False, 'includeLoopTestPassedResults': False, 'sessionId': '', 'domain': 'Communal'}
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        cronjobUser = GlobalVars.user
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        minute                = request.data.get('minute', None)
        hour                  = request.data.get('hour', None)
        dayOfMonth            = request.data.get('dayOfMonth', None)
        month                 = request.data.get('month', None)
        dayOfWeek             = request.data.get('dayOfWeek', None)
        
        release_minute        = request.data.get('release_minute', None)
        release_hour          = request.data.get('release_hour', None)
        release_dayOfMonth    = request.data.get('release_dayOfMonth', None)
        release_month         = request.data.get('release_month', None)
        release_dayOfWeek     = request.data.get('release_dayOfWeek', None)
        
        envs                  = request.data.get('envs', None)
        reservationUser       = request.data.get('reservationUser', user)
        removeJobAfterRunning = request.data.get('removeJobAfterRunning', False)
        reservationNotes      = request.data.get('reservationNotes', '')
    
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"minute": minute, "hour": hour, "dayOfMonth": dayOfMonth, "month": month, "dayOfWeek": dayOfWeek, 
                      "release_minute": release_minute, "release_hour": release_hour, "release_dayOfMonth": release_dayOfMonth, 
                      "release_month": release_month, "release_dayOfWeek": release_dayOfWeek,
                      "reservationUser": reservationUser, "removeJobAfterRunning": removeJobAfterRunning,
                      "reservationNotes": reservationNotes}
            restApi = '/api/v1/env/scheduler/add'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, request.data, 
                                                                           user, webPage=Vars.webpage, action='AddEnvSchedule')
        else:
            try:
                reserveFlag = False
                releaseJob = ''
                
                for reserve in [minute, hour, dayOfMonth, month, dayOfWeek]:
                    if reserve != "*":
                        reserveFlag = True
                        
                releaseFlag = False
                for release in [release_minute, release_hour, release_dayOfMonth, release_month, release_dayOfWeek]:
                    if release != "*":
                        releaseFlag = True
                
                localHostIp = keystackSettings.get('localHostIp', 'localhost')
                keystackIpPort = keystackSettings.get('keystackIpPort', '28028')
                envMgmtObj = EnvMgmt.ManageEnv()
                
                for env in envs:
                    envMgmtObj.setenv = env
                    if envMgmtObj.isEnvParallelUsage():
                        errorMsg = f'The env "{env.split(f"{GlobalVars.envPath}/")[1]}" is set as shareable. Scheduling a reservation is not required.'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvSchedule', 
                                                  msgType='Failed', msg=errorMsg)
                        return Response({'status':'failed', 'errorMsg': errorMsg}, status=statusCode)                        
                    
                    # env = /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/qa.yml
                    schedule = f'env={env} minute={minute} hour={hour} day={dayOfMonth} month={month} dayOfWeek={dayOfWeek}' 
                    
                    if JobSchedulerAssistant().isCronExists(env, minute, hour, dayOfMonth, month, dayOfWeek):
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvSchedule', 
                                                  msgType='Failed', msg=f'Cron job already exists: {schedule}')
                        return Response({'status':'failed', 'errorMsg': 'Cron Job already exists'}, status=statusCode)
                
                    # REST API: Run playbook function is in Playbook apiView.py
                    # For job scheduling, include the param -webhook to bypass verifying api-key
                    
                    # crontab command-line
                    newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} {cronjobUser} '
                    newJob += f'curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&env={env}'
                    newJob += f'&removeJobAfterRunning={removeJobAfterRunning}&release_minute={minute}&release_hour={hour}&release_dayOfMonth={dayOfMonth}'
                    newJob += f'&release_month={month}&release_dayOfWeek={dayOfWeek}&webhook=true" '
                    newJob += f'-H "Content-Type: application/x-www-form-urlencoded" -X  POST http://{localHostIp}:{keystackIpPort}/api/v1/env/reserveEnv'

                    if releaseFlag:
                        # removeJobAfterRunning: {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                        #                         'month': '\\*', 'day': '\\*', 'hour': '17', 'minute': '48', 'dayOfWeek': '\\*'}
                        releaseJob = f'{release_minute} {release_hour} {release_dayOfMonth} {release_month} {release_dayOfWeek} {cronjobUser} '
                        releaseJob += f'curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&env={env}'
                        releaseJob += f'&removeJobAfterRunning=True&release_minute={release_minute}&release_hour={release_hour}&release_dayOfMonth={release_dayOfMonth}'
                        releaseJob += f'&release_month={release_month}&release_dayOfWeek={release_dayOfWeek}&webhook=true" '
                        releaseJob += f'-H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/env/releaseEnv'
                        
                    # Leaving behind for debugging purpose
                    #cronJobs = f"""
                    #{newJob}
                    #* * * * * root date > /proc/1/fd/1 2>/proc/1/fd/2
                    #* * * * * root echo "Hello World! 8" >/proc/1/fd/1 2>/proc/1/fd/2
                    #"""
                    
                    # Put the cronjob in redis for the keystackScheduler to add the cron job
                    # NOTE: keyName for releaseEnv has to be unique because if user selects both reserveEnv and releaseEnv,
                    #       the env keyName is the same. So, using timestamp to make the keyName unique
                    # if reserveFlag:
                    #     if RedisMgr.redis:
                    #         keyName = f'scheduler-add-{env}'                    
                    #         RedisMgr.redis.write(keyName=keyName, data=newJob)
                    
                    # if releaseFlag:
                    #     if RedisMgr.redis:
                    #         keyName = f'scheduler-add-{getTimestamp()}-{env}'
                    #         RedisMgr.redis.write(keyName=keyName, data=releaseJob)

                    # Scheduler
                    data = {'cron': newJob, 'notes': reservationNotes}
                    JobSchedulerAssistant().addToScheduler(DB.name, 'env', data)
                    JobSchedulerAssistant().createCronJob(newJob)
                    
                    if releaseJob:
                        data2 = {'cron': releaseJob, 'notes': reservationNotes}
                        JobSchedulerAssistant().createCronJob(releaseJob)

                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvSchedule', msgType='Success', msg=newJob.replace('&webhook=true', ''))            
            
            except Exception as errMsg:
                status = 'failed'
                errorMsg = traceback.format_exc(None, errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddEnvSchedule', msgType='Error',
                                          msg=errorMsg, forDetailLogs=errorMsg)

        return Response(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeleteScheduledEnv(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteScheduledEnv', exclude=["engineer"])    
    def post(self, request):
        """ 
        Manually delete scheduled Envs in the scheduler
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        removeScheduledEnvs = request.data.get('removeScheduledEnvs', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"removeScheduledEnvs": removeScheduledEnvs}
            restApi = '/api/v1/env/scheduler/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteScheduledEnv')
        else:        
            try:
                #  [{env, month, day, hour, min}, {}, ...]
                removeJobList = []
                
                for cron in removeScheduledEnvs:
                    # cron: {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                    #        'month': '\\*', 'day': '\\*', 'hour': '14', 'minute': '51', 'dayOfWeek': '\\*'}
                    removeJobList.append(cron)
                
                # This removes from crontab and mongodb
                JobSchedulerAssistant().removeCronJobs(removeJobList, dbObj=DB.name, queryName='env') 
                   
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ScheduledEnvs(APIView):
    def post(self, request):        
        """         
        Create a data table of scheduled envs. Called by html template.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        envSearchName = request.data.get('env', 'all')
        html = ''
          
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/scheduler/scheduledEnvs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ScheduledEnvs')
            html = response.json()['envSchedules']
                       
        else: 
            html = '<table class="tableMessages table-bordered">'
            html += '<thead>'
            html += '<tr>'
            html += '<th>Delete</th>'
            html += '<th>User</th>'
            html += '<th>Envs</th>'
            html += '<th>Remove After Execution</th>'
            html += '<th>Reservation-Schedules</th>'
            html += '<th>Release-Schedules</th>'
            html += "<th>Notes</th>"
            html += '</tr>'
            html += '</thead>'

            try:
                cronjobs = JobSchedulerAssistant().getCurrentCronJobs(searchPattern='env=')
                   
                for eachCron in sorted(cronjobs):
                    # Handle the \t: '17 *\t* * *\troot    cd / && run-parts --report /etc/cron.hourly
                    eachCron = eachCron.replace('\t', ' ')
                    if eachCron == '':
                        continue

                    if envSearchName != 'all' and envSearchName not in eachCron:
                        continue

                    # * 3 * * * keystack curl -d "mainController=192.168.28.10:28028&remoteController=192.168.28.10:28028&reservationUser=Hubert Gee&env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml&removeJobAfterRunning=False&release_minute=*&release_hour=3&release_dayOfMonth=*&release_month=*&release_dayOfWeek=*&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X  POST http://192.168.28.10:28028/api/v1/env/reserveEnv                                 
                    match = search(' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*reservationUser=(.+)&.*env=([^ &]+).*removeJobAfterRunning=(True|False).*POST *http.+(reserveEnv|releaseEnv)', eachCron)
                    if match:
                        min                  = match.group(1)
                        hour                 = match.group(2)
                        day                  = match.group(3)
                        month                = match.group(4)
                        dayOfWeek            = match.group(5)
                        reservationUser      = match.group(6)
                        removeAfterExecution = match.group(8)
                                                
                        # /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/airMosaicSample.yml
                        env             = match.group(7)
                        envName         = 'unknown'
                        regexMatch = search('.*DOMAIN=[^ /]+?(/.+)', env)
                        if regexMatch:
                            envName = regexMatch.group(1)

                        typeOfReservation = match.group(9)

                        if removeAfterExecution == 'True':
                            remove = 'Yes'
                        else:
                            remove = 'No'
                                                    
                        reservationNotes = ''
                        cronJobReservationNotesData = JobSchedulerAssistant().getDetailsFromMongoDB(dbObj=DB.name, queryName='env')
                        countX = deepcopy(cronJobReservationNotesData)
                        count = len(list(countX))
                        if count > 0:
                            for cronInMongoDB in cronJobReservationNotesData[0]['cronJobs']:
                                if cronInMongoDB['cron'] == eachCron:
                                    reservationNotes = cronInMongoDB['notes']
                          
                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="envSchedulerMgmt" jobSearchPattern="env={env}" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        
                        html += f'<td>{reservationUser}</td>'
                        html += f'<td>{envName}</td>'
                        html += f'<td class="textAlignCenter">{remove}</td>'
                        
                        if typeOfReservation == 'reserveEnv':
                            html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                            html += '<td></td>'
                            
                        if typeOfReservation == 'releaseEnv':
                            html += '<td></td>'
                            html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                        
                        # Notes
                        html += f'<td class="textAlignCenter">{reservationNotes}</td>'
                            
                        html += '</tr>'
                    else:
                        match     = search(' *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+).*', eachCron)
                        min       = match.group(1)
                        hour      = match.group(2)
                        day       = match.group(3)
                        month     = match.group(4)
                        dayOfWeek = match.group(5)
                        
                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="envSchedulerMgmt" jobSearchPattern="" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                        html += f'<td></td>'
                        html += '</tr>'
                                            
                html += '</table>'
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ScheduledEnvs', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        # This is to tell javascript if there are any scheduled job.
        # If there is no job, then hide the remove and close modal buttons
        if '<td>' not in html:
            areThereJobs = False
        else:
            areThereJobs = True
                    
        return Response(data={'envSchedules': html, 'areThereJobs': areThereJobs,
                              'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class GetEnvCronScheduler(APIView):
    def post(self, request):
        """
        Dropdowns for minute, hour, day, month, dayOfWeek
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        minute = ''
        hour = ''
        dayOfMonth = ''
        month = ''
        dayOfWeek = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/scheduler/getCronScheduler'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetEnvCronScheduler')

            minute     = response.json()['minute']
            hour       = response.json()['hour']
            dayOfMonth = response.json()['dayOfMonth']
            month      = response.json()['month']
            dayOfWeek  = response.json()['dayOfWeek']                
        else:
            hour, minute, month, dayOfMonth, dayOfWeek = getSchedulingOptions(typeOfScheduler='reserve')
            schedulerDateTimePicker = f'{hour} {minute} {month} {dayOfMonth} {dayOfWeek}'

            hour, minute, month, dayOfMonth, dayOfWeek = getSchedulingOptions(typeOfScheduler='expiration')
            schedulerExpiresDateTimePicker = f'{hour} {minute} {month} {dayOfMonth} {dayOfWeek}'    
                                     
        return Response(data={'schedulerDateTimePicker': schedulerDateTimePicker,
                              'schedulerExpiresDateTimePicker': schedulerExpiresDateTimePicker,
                              'status':status, 'errorMsg':errorMsg}, status=statusCode)
        
        
class GetAutoSetupTaskCreatorTemplate(APIView):
    def post(self, request):
        """
        Allow users to create multiple auto-setup tasks.
        This class provides a template for each task.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        env = request.data.get('env', None)
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'env': env}
            restApi = '/api/v1/env/getAutoSetupTaskCreatorTemplate'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='getAutoSetupTaskCreatorTemplate')
            html = response.json()['autoSetupTaskCreatorTemplate']
        else:
            try:
                envFile = f'{GlobalVars.envPath}/{env}.yml'
                
                #envData = readYaml(envFile)
                # if 'autoStart' in envData.keys():
                #     print('\n---- getAutoSetupTaskCreatorTemplate:'. envData['autoStart'])
                # else:
                #     print('\n---- getAutoSetupTaskCreatorTemplate: no autoStart')
                    
            except Exception as errMsg:
                html = ''
                status = 'failed'
                                         
        return Response(data={'autoSetupTaskCreatorTemplate': html,
                              'status':status, 'errorMsg':errorMsg}, status=statusCode)
        
class EnvGroups(APIView):
    """
    Internal usage only: Get Env domain groups for sidebar Env dropdown menu
    
    /api/v1/env/envGroups
    """
    def post(self, request):
        """
        Get Env groups for sidebar Env menu
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        htmlEnvGroups = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/env/envGroups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='EnvGroups')
            htmlEnvGroups = response.json()['envGroups']               
        else:          
            try:
                envGroups = []
                trackDomainMenu = []
                htmlEnvGroups = ''
                userAllowedDomains = DomainMgr().getUserAllowedDomains(user)

                htmlEnvGroups += '<a href="/setups/envLoadBalancer" class="collapse-item pl-0 pt-3 pb-3 textBlack fontSize12px"><strong>Env Load-Balance Mgmt</strong></a>'
                
                for root,dirs,files in os.walk(GlobalVars.envPath):
                    currentDomain = root.split(f'{GlobalVars.envPath}/')[-1].split('/')[0].split('=')[-1]
                    # Envs/DOMAIN=Sanity/qa/dev
                    envGroup = root.split(f'{GlobalVars.keystackTestRootPath}/')[-1]
                    envGroupName = '/'.join(envGroup.split('/')[2:])
                    totalEnvs = len([envFile for envFile in files if '~' not in envFile and 'backup' not in envFile])
                    
                    if currentDomain in userAllowedDomains:
                        if currentDomain not in trackDomainMenu:
                            trackDomainMenu.append(currentDomain)
                            htmlEnvGroups += f'<p class="pl-2 pt-2 textBlack fontSize12px"><strong>Domain:&ensp;{currentDomain}</strong></p><br>'
                        
                        htmlEnvGroups += f'<a class="collapse-item pl-3 fontSize12px" href="/setups?group={envGroup}">{totalEnvs} <i class="fa-regular fa-folder pr-3"></i>{envGroupName}</a>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                htmlEnvGroups = ''
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            
        
        return Response(data={'envGroups':htmlEnvGroups, 'status':status, 'error':errorMsg}, status=statusCode)   
    
    
class UpdateEnv(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='UpdateEnv', exclude=["engineer"])    
    def post(self, request):
        """
        Description: 
            Update an Env Yaml file
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', None) 
        envFullPath = request.data.get('envFullPath', None)
        devices = request.data.get('devices', [])
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None        
        envData = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'envFullPath': envFullPath, 'devices': devices}
            restApi = '/api/v1/env/update'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='UpdateEnv')
            envData = response.json()['updatedEnvData']
        else:
            try:
                if envFullPath and os.path.exists(envFullPath):
                    envData = readYaml(envFullPath)
                    from LabInventory import InventoryMgmt
                    
                    for device in devices:
                        deviceDetails = InventoryMgmt(domain=domain, device=device).getDeviceDetailsForEnvFiles()
                        
                        if 'devices' not in envData.keys():
                            envData.update({'devices': deviceDetails})
                        else:
                            envData['devices'].update(deviceDetails)
                        
                    writeToYamlFile(envData, envFullPath)
                    envData = readFile(envFullPath)
                                                    
                else:
                    errorMsg = f'UpdateEnv: No such env Yaml file: {envFullPath}'
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage='labInventory', action='UpdateEnv', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
        
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                eenvData = ''
                
                SystemLogsAssistant().log(user=user, webPage='labInventory', action='UpdateEnv', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
        
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class SetShareable(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='SetShareable', exclude=["engineer"])    
    def post(self, request):
        """
        Description: 
            Set an env shareable
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        # env: DOMAIN=Communal/Samples/demoEnv1
        env = request.data.get('env', None)
        shareable = request.data.get('shareable')
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None        
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'env': env, 'shareable': shareable}
            restApi = '/api/v1/env/setShareable'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SetShareable')
        else:
            try:
                envMgmtObj = EnvMgmt.ManageEnv() 
                envMgmtObj.setenv = env 
                if shareable == "No":
                    parallelUsage = False
                else:
                    parallelUsage = True
                    
                envMgmtObj.setEnvParallelUsage(parallelUsage=parallelUsage) 
                             
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetShareable', msgType='Success',
                                          msg=f'Env:{env}  shareable={shareable}', forDetailLogs='')
                        
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetShareable', msgType='Error',
                                          msg=errorMsg, forDetailLogs='')
        
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)