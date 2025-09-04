import os, traceback
from re import search
from pprint import pprint

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from db import DB
from globalVars import GlobalVars, HtmlStatusCodes
from commonLib import logDebugMsg, getSortedPortList
from keystackUtilities import readYaml, getTimestamp, convertNoneStringToNoneType, convertStrToBoolean, getDictIndexFromList
from scheduler import JobSchedulerAssistant, getSchedulingOptions
from domainMgr import DomainMgr

# Located in /Keystack/Src/
from PortGroupMgmt import ManagePortGroup
from RedisMgr import RedisMgr

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    
class Vars:
    webpage = 'portGroup'
    portMgmt = 'portMgmt'
 

class GetPortGroupDomains(APIView):
    def post(self,request):
        """
        Sidebar menu called by base.html/base.js
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/portGroup/domains'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetPortGroupDomains')
            html = response.json()['domains']       
        else:        
            try:
                userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
                for domain in userAllowedDomains:
                    html += f'<a class="collapse-item pl-3 textBlack" href="/portGroup?domain={domain}"><i class="fa-regular fa-folder pr-3"></i>{domain}</a>'
                                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPortGroupDomains', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'domains': html, 'status':status, 'errorMsg': errorMsg}, status=statusCode)
    
                          
class CreatePortGroup(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='CreatePortGroup', exclude=['engineer'])
    def post(self, request):
        """
        Create port group
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        portGroup = request.data.get('portGroup', None)
        domain = request.data.get('domain', GlobalVars.defaultDomain)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup}
            restApi = '/api/v1/portGroup/create'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='CreatePortGroup')
        else:        
            try:
                isPortGroupExists = result = ManagePortGroup(domain=domain, portGroup=portGroup).isPortGroupExists()
                if isPortGroupExists:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreatePortGroup', msgType='Info',
                                              msg=f'Port Group {portGroup} already exists in domain {domain}', forDetailLogs='')
                    return Response(data={'status': 'failed', 'errorMsg': f'Error: Domain:{domain} Port-Group {portGroup} already exists'}, status=statusCode) 
                
                result = ManagePortGroup(domain=domain, portGroup=portGroup).createPortGroup()
                if result:
                    dbStatus = 'Success'
                else:
                    dbStatus = 'Failed'
                    
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreatePortGroup', msgType=dbStatus,
                                          msg=f'Port-Group: {portGroup}', forDetailLogs='')                       
            except Exception as errMsg:
                statusCode = HtmlStatusCodes.error
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreatePortGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class GetPortGroupTableData(APIView):
    def post(self, request):
        """
        Get port group table data for viewing and delete
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', None) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/portGroup/getTableData'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPortGroupTableData')
            portGroupTableData = response.json()['portGroupTableData']
        else:        
            try:
                domainUserRole = DomainMgr().getUserRoleForDomain(user, domain)
                portlist = []

                portGroups = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': domain},
                                                  includeFields={'_id':0}, sortBy=[('name', 1)], limit=None)
                
                for index, portGroupObj in enumerate(portGroups):
                    concatDropdown = ''
                    totalActiveUsers = len(portGroupObj['activeUsers'])
                    totalWaiting = len(portGroupObj['waitList'])
                    onSchedulerCronJobs = len(JobSchedulerAssistant().getCurrentCronJobs(searchPattern=f'portGroup={portGroupObj["name"]}'))

                    if portGroupObj['ports'] == {}:
                        portlist = []
                        portsDropdown = '<div class="dropdown"></div>'  
                    else: 

                        # Each device has its own dropdown ports to show
                        for device in portGroupObj['ports'].keys():
                            portlist = portGroupObj["ports"][device]["ports"]
                            domain =  portGroupObj["domain"]
                            portsDropdown = '<div class="dropdown">'

                            portsDropdown += f"<div class='dropdown-toggle textBlack openedPortConfigsClass' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>"
                            portsDropdown += f"<a class='textBlack' href='#' portGroup={portGroupObj['name']} type='button'>Device: {device}</a>"
                            portsDropdown += "</div>" 
                                           
                            portsDropdown += '<ul class="dropdown-menu dropdownSizeMedium" aria-labelledby="portsDropdown">'
                            portsDropdown += f'<li><span class="mainFontSize textBlack paddingLeft20px">Domain={domain} &emsp; Device={device}</span></li><br>'
                 
                            for index, port in enumerate(portlist):
                                portsDropdown += f'<li><span class="mainFontSize textBlack paddingLeft40px">{index+1}: Port {port}</span></li>'

                            portsDropdown += '</ul>'
                            portsDropdown += '</div>'
                            concatDropdown += portsDropdown
                            
                    html += '<tr>'
                    html += f'<td><input type="checkbox" name="portGroupCheckboxes" portGroup="{portGroupObj["name"]}"></td>'
                    html += f'<td class="paddingLeft5px">{portGroupObj["name"]}</td>'
                    html += f'<td class="textAlignLeft">{concatDropdown}</td>'
                                        
                    html += f'<td class="textAlignCenter"><a href="#"  onclick="activeUsersList(this)" portGroup="{portGroupObj["name"]}" data-bs-toggle="modal" data-bs-target="#portGroupActiveUsersModal">Active-Users:{totalActiveUsers}&emsp;&ensp;Users-Waiting:{totalWaiting}</a></td>'
                    
                    # Disabling port-group scheduler. Don't think it's neccessary.  Reserving/Releasing Envs will reserve/release port-groups
                    '''
                    # # Get total cron jobs for this Port-Group
                    html += f'<td class="textAlignCenter"><a href="#"  data-bs-toggle="modal" data-bs-target="#createPortGroupSchedulerModal" portGroup="{portGroupObj["name"]}" onclick="getPortGroupCronScheduler(this)">{onSchedulerCronJobs}</a></td>'
                               
                    # The reserve button has no stage and task                                                     
                    html += f'<td class="paddingLeft5px"><button type="button" class="btn btn-outline-primary" portGroup={portGroupObj["name"]} onclick="reservePortGroup(this)">Reserve Now</button></td>'
                    
                    if totalActiveUsers > 0: 
                        html += f'<td class="textAlignCenter"><button class="btn btn-sm btn-outline-primary" portGroup={portGroupObj["name"]} onclick="releasePortGroup(this)">Release</button></td>'
                    else:
                        html += '<td></td>'
                    ''' 
                    
                    if domainUserRole == 'engineer':
                        html += f'<td class="paddingLeft5px"><button type="button" class="btn btn-outline-primary" portGroup="{portGroupObj["name"]}" onclick="resetPortGroup(this)" disabled>Reset</button></td>' 
                    else:                       
                        html += f'<td class="paddingLeft5px"><button type="button" class="btn btn-outline-primary" portGroup="{portGroupObj["name"]}" onclick="resetPortGroup(this)">Reset</button></td>'
                        
                    html += '</tr>'
                    
                # Must add additional row so each row height is exactly the the height of the row's data.
                # Otherwise, the rows will resize to fit the size of the table size
                html += '<tr></tr>'
                                                            
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                #print('---- GetPortGroupTableData ERROR:', traceback.format_exc(None, errMsg))
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPortGroupTableData', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg).replace('<td>', '[td]')) 

        return Response(data={'portGroupTableData': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetPortGroupActiveUsersMgmtTable(APIView):
    swagger_schema = None
    def post(self, request):
        """ 
        Get active-list/wait-list mgmt table
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        portGroup = request.data.get('portGroup', None)
        domain = request.data.get('domain', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup}
            restApi = '/api/v1/portGroup/activeUsersTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPortGroupActiveUsersMgmtTable')
            html = response.json()['tableData'] 
                      
        else:                
            try:
                data = ManagePortGroup(domain=domain, portGroup=portGroup).getPortGroupDetails()
                if data:         
                    html += '<table id="portGroupActiveUsersTable" class="mt-2 table table-sm table-bordered table-fixed tableFixHead tableMessages">' 
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

                    for inUsedBy in data['activeUsers']:
                        sessionId = inUsedBy.get('sessionId')
                        overallSummaryFile = inUsedBy.get('overallSummaryFile', None)
                        stage = inUsedBy.get('stage', None)
                        task = inUsedBy.get('task', None)
                        reservationUser = inUsedBy.get('user', 'Unknown')

                        if overallSummaryFile and os.path.exists(overallSummaryFile):
                            data = readYaml(overallSummaryFile)
                            user = data['user']
                        
                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="portGroupActiveUsersCheckboxes" portGroup="{portGroup}" sessionId="{sessionId}" stage="{stage}" task="{task}" user="{reservationUser}" /></td>'
                        html += f'<td class="textAlignCenter">{reservationUser}</td>'
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
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPortGroupActiveUsersMgmtTable', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response(data={'tableData': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
 
class GetPortGroupWaitListTable(APIView):
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
        portGroup = request.data.get('portGroup', None)
        domain = request.data.get('domain', None)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        portGroup = request.data.get('portGroup', None)
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup}
            restApi = '/api/v1/portGroup/waitListTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPortGroupWaitListTable')
            html = response.json()['tableData'] 
                   
        else:
            try:
                html = '<table id="portGroupWaitListTable" class="mt-2 table table-sm table-bordered table-fixed tableFixHead tableMessages">' 
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
                    
                data = ManagePortGroup(domain=domain, portGroup=portGroup).getPortGroupDetails()
                if data:
                    for eachWait in data['waitList']:
                        sessionId = eachWait['sessionId']
                        stage =     eachWait['stage']
                        task =      eachWait['task']
                        user =      eachWait.get('user', 'Unknown')
                        overallSummaryFile = eachWait.get('overallSummaryFile', None)
                        
                        if overallSummaryFile and os.path.exists(overallSummaryFile):
                            data = readYaml(overallSummaryFile)
                            user = data['user']
                
                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="portGroupWaitListCheckboxes" portGroup="{portGroup}" user="{user}" sessionId="{sessionId}" stage="{stage}" task="{task}"/></td>'
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
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPortGroupWaitListTable',
                                          msgType='Error', msg=errorMsg,
                                          forDetailLogs=f'GetPortGroupWaitList: {traceback.format_exc(None, errMsg)}') 
            
        return Response(data={'tableData': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)

    
class GetPortsConfigurationTable(APIView):
    def post(self, request):
        """
        Get port-group ports table
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        portGroup = request.data.get('portGroup', None)
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"portGroup": portGroup}
            restApi = '/api/v1/portGroup/portsTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPortsConfigurationTable')
            portsTable = response.json()['portsTable']   
        else:        
            try:
                portGroupData = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'name': portGroup})
                if portGroupData:                         
                    html += """
                        <div class="row">
                        <table id="portConfigurationTable" class="tableFixHead2">
                        <thead>
                            <tr>
                                <th>Domain</th>
                                <th>Device</th>
                                <th>Port</th>
                            </tr>
                        </thead> <tbody>
                        """
                        
                    # For each port in current device
                    for device in portGroupData['ports'].keys():
                        for port in portGroupData['ports'][device]['ports']:
                            html += '<tr>'
                            html += f'<td>{portGroupData["ports"][device]["domain"]}</td>'
                            html += f'<td>{device}</td>'
                            html += f'<td>{port}</td>'
                            html += '</tr>'                
                        
                html += '</tbody></table></div>'
                                        
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPortsConfigurationTable', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg).replace('<td>', '[td]')) 

        return Response(data={'portsTable': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class DeletePortGroups(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeletePortGroup', exclude=['engineer'])
    def post(self, request):
        """
        Delete Port Groups
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroups = request.data.get('portGroups', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'portGroups': portGroups}
            restApi = '/api/v1/portGroup/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeletePortGroups')
        else:        
            try:
                successfullyDeleted = []
                failedToDelete = []
                
                for portGroup in portGroups:
                    # Don't delete the port-group if it's actively used
                    if ManagePortGroup(domain=domain, portGroup=portGroup).isPortGroupAvailable():
                        # Delete the port-group from switch device too

                        # ports{'device-10': {'domain': 'Communal', 'ports': ['1/1', '1/2']}}
                        ports = ManagePortGroup(domain=domain, portGroup=portGroup).getAllPorts()

                        if ports != {}:
                            deviceList = []
                            for device in ports.keys():
                                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                                if portMgmtData:
                                    for portMgmtIndex, portDetails in enumerate(portMgmtData['portMgmt']):
                                        if portGroup in portDetails['portGroups']:
                                            # portDetails['portGroups'] is a list of port-groups
                                            # Remove the port-group from the list
                                            portGroupIndex = portDetails['portGroups'].index(portGroup)                                        
                                            portDetails['portGroups'].pop(portGroupIndex)
                                            
                                            portMgmtData['portMgmt'].pop(portMgmtIndex)
                                            
                                            # Update portMgmt with updated data
                                            portMgmtData['portMgmt'].insert(portMgmtIndex, portDetails)
                                            
                                    result = DB.name.updateDocument(collectionName='labInventory',
                                                                    queryFields={'domain': domain, 'name': device},
                                                                    updateFields={'portMgmt': portMgmtData['portMgmt']})
              
                        result = ManagePortGroup(domain=domain, portGroup=portGroup).removePortGroup()
                        if result:
                            successfullyDeleted.append(portGroup)
                        else:
                            failedToDelete.append(portGroup)
                    else:
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePortGroups', msgType='Failed',
                                                  msg=f'Cannot delete an active port-group: {portGroup} in domain {domain}', forDetailLogs='') 
                                            
                if len(successfullyDeleted) > 0:
                    if len(successfullyDeleted) == len(portGroups):
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePortGroups', msgType='Success',
                                                  msg=portGroups, forDetailLogs=None)  
                    else:
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePortGroups', msgType='Failed',
                                                  msg=f'Failed to delete: {failedToDelete} in domain {domain}', forDetailLogs='')                                           
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePortGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status':status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class ReservePortGroupUI(APIView):
    def post(self, request):
        """
        Keystack reserving a port-group.  User did not click on reserve button.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        sessionId = request.data.get('sessionId', None)
        stage = request.data.get('stage', None)
        task = request.data.get('task', None)
        env = request.data.get('env', None)
        userReserving = request.data.get('user', None)
        overallSummaryFile = request.data.get('overallSummaryFile', None)
        #trackUtilization = request.data.get('trackUtilization', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup, "sessionId": sessionId, "stage": stage, "task": task,
                      "env": env, "userReserving": userReserving, "overallSummaryFile": overallSummaryFile}
            restApi = '/api/v1/portGroup/reserveUI'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ReservePortGroupUI') 
        else:        
            try:
                result = ManagePortGroup(domain=domain, portGroup=portGroup).reservePortGroup(sessionId=sessionId,
                                                                                              overallSummaryFile=overallSummaryFile,
                                                                                              user=userReserving,
                                                                                              stage=stage,
                                                                                              task=task,
                                                                                              env=env)
                # ('failed', '[ReservePortGroup]: mongoDB portGroupMgmt has no data: port-group1')
                if result[0] == 'failed':
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReservePortGroupUI', msgType='Error',
                                              msg=f'Domain:{domain} PortGroup:{portGroup}  SessionId:{sessionId} error:<br>{result[1]}',
                                              forDetailLogs='') 
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReservePortGroupUI', msgType='Error',
                                          msg=f'Domain:{domain} PortGroup:{portGroup}  SessionId:{sessionId} error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class ReservePortGroupButton(APIView):
    def post(self, request):
        """
        User clicked on the reserve button
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        
        # For cron jobs
        reservationUser = request.data.get('reservationUser', user)
        removeJobAfterRunning = convertStrToBoolean(request.data.get('removeJobAfterRunning', False))

        # releaseJob = f'{release_minute} {release_hour} {release_dayOfMonth} {release_month} {release_dayOfWeek} {cronjobUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&portGroup={portGroup}&removeJobAfterRunning=True&release_minute={release_minute}&release_hour={release_hour}&release_dayOfMonth={release_dayOfMonth}&release_month={release_month}&release_dayOfWeek={release_dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/portGroup/release'
        release_minute        = request.data.get('release_minute', '*')
        release_hour          = request.data.get('release_hour', '*')
        release_dayOfMonth    = request.data.get('release_dayOfMonth', '*')
        release_month         = request.data.get('release_month', '*')
        release_dayOfWeek     = request.data.get('release_dayOfWeek', '*')
            
        sessionId = getTimestamp()
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup}
            restApi = '/api/v1/portGroup/reserve'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ReservePortGroupButton') 
        else:        
            try:
                if removeJobAfterRunning:
                    if RedisMgr.redis:
                        keyName = f'scheduler-remove-{portGroup}'
                        
                        # {'jobSearchPattern': 'portGroup=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                         #  'month': '\\*', 'day': '\\*', 'hour': '8', 'minute': '28', 'dayOfWeek': '\\*'} 
                        removeJobList = {'jobSearchPattern': f'portGroup={portGroup}', 'minute': release_minute, 'hour': release_hour, 
                                          'month': release_month, 'dayOfMonth': release_dayOfMonth, 'dayOfWeek': release_dayOfWeek}  
                    
                        RedisMgr.redis.write(keyName=keyName, data=removeJobList)
                    else:
                        # NOTE: redis is not connected
                        pass
                    
                portGroupMgmtObj = ManagePortGroup(domain=domain, portGroup=portGroup)
                if portGroupMgmtObj.isUserInActiveUsersList(reservationUser):
                    status = 'failed'
                    errorMsg = f'The user={reservationUser} is already actively using the port-group={portGroup} in domain {domain}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReservePortGroupButton', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
                    return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
                
                if portGroupMgmtObj.isUserInWaitList(reservationUser):
                    status = 'failed'
                    errorMsg = f'The user={reservationUser} is already in the wait-list in port-group:{portGroup} in domain {domain}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReservePortGroupButton', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
                    return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
             
                result = portGroupMgmtObj.reservePortGroup(sessionId=sessionId, user=reservationUser)

                if result and result[0] == 'success':
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReservePortGroupButton', msgType='Info',
                                              msg=result[1], forDetailLogs='')
                                    
                if result and result[0] == 'failed':
                    status = 'failed'
                    if result:
                        errorMsg = result[1]
                    else:
                        errorMsg = 'Unknown reason'
                        
                    statusCode = HtmlStatusCodes.error
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReservePortGroupButton', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
                                                        
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReservePortGroupButton', msgType='Error',
                                          msg=f'Domain:{domain} PortGroup:{portGroup}  SessionId:{sessionId} error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ReleasePortGroupButton(APIView):
    def post(self, request):
        """
        Button to manually release a port-group
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        
        # For cronjobs
        # releaseJob = f'{release_minute} {release_hour} {release_dayOfMonth} {release_month} {release_dayOfWeek} {cronjobUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&env={env}&removeJobAfterRunning=True&release_minute={release_minute}&release_hour={release_hour}&release_dayOfMonth={release_dayOfMonth}&release_month={release_month}&release_dayOfWeek={release_dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/env/releaseEnv'
        removeJobAfterRunning = convertStrToBoolean(request.data.get('removeJobAfterRunning', False))
        reservationUser       = request.data.get('reservationUser', user)
        release_minute        = request.data.get('release_minute', '*')
        release_hour          = request.data.get('release_hour', '*')
        release_dayOfMonth    = request.data.get('release_dayOfMonth', '*')
        release_month         = request.data.get('release_month', '*')
        release_dayOfWeek     = request.data.get('release_dayOfWeek', '*')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup}
            restApi = '/api/v1/portGroup/release'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ReleasePortGroup')
        else:        
            try:
                ManagePortGroup(domain=domain, portGroup=portGroup).releasePortGroup()

                # Remove the job from the scheduler
                if removeJobAfterRunning:
                    # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                    #  'month': '\\*', 'day': '\\*', 'hour': '8', 'minute': '28', 'dayOfWeek': '\\*'} 
                    removeJobList = [{'jobSearchPattern': f'portGroup={portGroup}', 'minute': release_minute, 'hour': release_hour, 
                                      'month': release_month, 'dayOfMonth': release_dayOfMonth, 'dayOfWeek': release_dayOfWeek}]                  
                    #JobSchedulerAssistant().removeCronJobs(listOfJobsToRemove=removeJobList)
                    
                    if removeJobAfterRunning:
                        if RedisMgr.redis:
                            keyName = f'scheduler-remove-{portGroup}'
                            
                            # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                            #  'month': '\\*', 'day': '\\*', 'hour': '8', 'minute': '28', 'dayOfWeek': '\\*'} 
                            removeJobList = {'jobSearchPattern': f'portGroup={portGroup}', 'minute': release_minute, 'hour': release_hour, 
                                            'month': release_month, 'dayOfMonth': release_dayOfMonth, 'dayOfWeek': release_dayOfWeek}  
                        
                            RedisMgr.redis.write(keyName=keyName, data=removeJobList)
                        else:
                            # NOTE: redis is not connected
                            pass
                                                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ReleasePortGroup', msgType='Error',
                                          msg=f'PortGroup:{portGroup} error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class AmINextPortGroup(APIView):
    def post(self, request):
        """
        Verify if a sessionId or user is next to use the Port-Group
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        sessionId = request.data.get('sessionId', None)
        sessionUser = request.data.get('user', None)
        stage = request.data.get('stage', None)
        task = request.data.get('task', None)
        env = request.data.get('env', None)
        overallSummaryFile = request.data.get('overallSummaryFile', None)
        amINext = False
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup, "sessionId": sessionId, 'sessionUser': sessionUser,
                      'stage': stage, 'task': task, 'env': env, 'overallSummaryFile': overallSummaryFile}
            restApi = '/api/v1/portGroup/amINext'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='AmINextToUsePortGroup')
            amINext = response.json()['amINext'] 

        else:        
            try:
                amINext = ManagePortGroup(domain=domain, portGroup=portGroup).amIRunning(sessionUser, sessionId, stage, task, env, overallSummaryFile)

            except Exception as errMsg:
                statusCode = HtmlStatusCodes.error
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AmINextToUsePortGroup', msgType='Error',
                                          msg=f'Domain:{domain} PortGroup:{portGroup}  SessionId:{sessionId} error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'amINext': amINext, 'status': status, 'errorMsg': errorMsg}, status=statusCode)    
    
    
class IsPortGroupAvailable(APIView):
    def post(self, request):
        """
        Verify if the port-group is available
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        isAvailable = False
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup}
            restApi = '/api/v1/portGroup/isPortGroupAvailable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='IsPortGroupAvailable')
            isAvailable = response.json()['isAvailable']   
        else:        
            try:
                isAvailable = ManagePortGroup(domain=domain, portGroup=portGroup).isPortGroupAvailable()
                            
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsPortGroupAvailable', msgType='Error',
                                          msg=f'Domain:{domain} PortGroup:{portGroup}  error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'isAvailable': isAvailable, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class RemoveFromActiveUserListPortGroup(APIView):
    def post(self, request):
        """
        Remove a user or sessionId from the active-user list.
        This is used by pipelines when a task is done and 
        release the port-group.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        sessionId = request.data.get('sessionId', None)
        removeUser = request.data.get('user', None)
        stage = request.data.get('stage', None)
        task = request.data.get('task', None)
            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup, "sessionId": sessionId, "user": removeUser,
                      "stage": stage, "task": task}
            restApi = '/api/v1/portGroup/removeFromActiveUsersListUI'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='RemoveFromActiveUserListPortGroup') 
        else:        
            try:
                result = ManagePortGroup(domain=domain, portGroup=portGroup).removeFromActiveUsersListUI([{'user':removeUser, 'sessionId':sessionId, 'stage':stage, 'task':task}])  
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromActiveUserListPortGroup', msgType='Error',
                                          msg=f'Domain:{domain}  PortGroup:{portGroup}  error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
 

class RemoveFromActiveUserListPortGroup2(APIView):
    def post(self, request):
        """
        Remove a list of active-users/sessionId from the active-user list.
        This is used by users selecting active-user checkboxes manually.
        Users could select 1 or more in a list
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)
        # [{'user':removeUser, 'sessionId':sessionId, 'stage':stage, 'task':task}]
        activeUsersList = request.data.get('activeUsersList', [])

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain,"portGroup": portGroup, "activeusersList": activeUsersList}
            restApi = '/api/v1/portGroup/removeFromActiveUsersListManually'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveFromActiveUserListPortGroup2')
        else:        
            try:
                if activeUsersList:
                    result = ManagePortGroup(domain=domain, portGroup=portGroup).removeFromActiveUsersListUI(activeUsersList)  
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromActiveUserListPortGroup', msgType='Error',
                                          msg=f'Domain:{domain} PortGroup:{portGroup}  error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    

class RemoveFromWaitListPortGroup(APIView):
    def post(self, request):
        """
        Remove one user or sessionId from the waitList.
        Mainly used by keystack UI automation.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        waitListUsers = request.data.get('waitListUsers', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "waitListUsers": waitListUsers}
            restApi = '/api/v1/portGroup/removeFromWaitList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveFromWaitList')  
        else:        
            try:
                # [{'sessionId': '10-28-2024-08:16:24:541387_5274', 'portGroup': 'portGroup1', 'stage': 'Test', 'task': 'layer3', 'user': 'CLI: hgee'},
                #  {'sessionId': '10-28-2024-09:17:20:795922_1278', 'portGroup': 'portGroup1', 'stage': 'Test', 'task': 'layer3', 'user': 'CLI: hgee'}]
                for waiting in waitListUsers:
                    data = ManagePortGroup(domain=domain, portGroup=waiting['portGroup']).removeFromWaitList(sessionId=waiting['sessionId'],
                                                                                                             user=waiting['user'],
                                                                                                             stage=waiting['stage'],
                                                                                                             task=waiting['task'])    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFromWaitList', msgType='Error',
                                          msg=f'Domain:{domain}<br>{waitListUsers} error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
             
class ResetPortGroup(APIView):
    def post(self, request):
        """
        Reset PortGroup
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        portGroup = request.data.get('portGroup', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "portGroup": portGroup}
            restApi = '/api/v1/portGroup/reset'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ResetPortGroup')   
        else:        
            try:
                result = ManagePortGroup(domain=domain, portGroup=portGroup).resetPortGroup()
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetPortGroup', msgType='Success',
                                          msg=f'Domain:{domain} PortGroup:{portGroup}',
                                          forDetailLogs='')      
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ResetPortGroup', msgType='Error',
                                          msg=f'Domain:{domain} PortGroup:{portGroup}  error:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 


class UpdatePortGroupActiveUsersAndWaitList(APIView):
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
            restApi = '/api/v1/portGroup/updateActiveUsersAndWaitList'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='UpdatePortGroupActiveUsersAndWaitList')   
        else:        
            try:
                ManagePortGroup().selfUpdateActiveUsersAndWaitList()
                                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdatePortGroupActiveUsersAndWaitList', msgType='Info',
                                          msg='',forDetailLogs='')      
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='UpdatePortGroupActiveUsersAndWaitList', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    
    
# ---- Port-Group Scheduler ----
       
class AddPortGroupSchedule(APIView):                                           
    @verifyUserRole(webPage=Vars.webpage, action='AddPortGroupSchedule', exclude=['engineer'])
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
        keystackUser = GlobalVars.user
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
        
        domain                = request.data.get('domain', None)
        portGroups            = request.data.get('portGroups', None)
        reservationUser       = request.data.get('reservationUser', user)
        removeJobAfterRunning = request.data.get('removeJobAfterRunning', False)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            restApi = '/api/v1/portGroup/scheduler/add'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, request.data, 
                                                                           user, webPage=Vars.webpage, action='AddPortGroupSchedule')
        else:
            try:
                reserveFlag = False
                for reserve in [minute, hour, dayOfMonth, month, dayOfWeek]:
                    if reserve != "*":
                        reserveFlag = True
                        
                releaseFlag = False
                for release in [release_minute, release_hour, release_dayOfMonth, release_month, release_dayOfWeek]:
                    if release != "*":
                        releaseFlag = True
                         
                localHostIp = keystackSettings.get('localHostIp', 'localhost')
                keystackIpPort = keystackSettings.get('keystackIpPort', '28028')
                 
                for portGroup in portGroups: 
                    schedule = f'portGroup={portGroup} minute={minute} hour={hour} day={dayOfMonth} month={month} dayOfWeek={dayOfWeek}' 
                    
                    if JobSchedulerAssistant().isCronExists(portGroup, minute, hour, dayOfMonth, month, dayOfWeek):
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPortGroupSchedule', 
                                                  msgType='Failed', msg=f'Cron job already exists: {schedule}')
                        return Response({'status':'failed', 'errorMsg': 'Cron Job already exists'}, status=statusCode)
                
                    # REST API: Run playbook function is in Playbook apiView.py
                    # For job scheduling, include the param -webhook to bypass verifying api-key
                    #newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} keystack curl -d "sessionId={sessionId}&playbook={playbook}&awsS3={awsS3}&jira={jira}&pauseOnError={pauseOnError}&debug={debugMode}&domain={domain}&holdEnvsIfFailed={holdEnvsIfFailed}&abortTestOnFailure={abortTestOnFailure}&includeLoopTestPassedResults={includeLoopTestPassedResults}&scheduledJob=\'{schedule}\'&removeJobAfterRunning={removeJobAfterRunning}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/playbook/run'
                    
                    # crontab command-line
                    # newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} {keystackUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&domain={domain}&reservationUser={reservationUser}&portGroup={portGroup}&removeJobAfterRunning={removeJobAfterRunning}&release_minute={minute}&release_hour={hour}&release_dayOfMonth={dayOfMonth}&release_month={month}&release_dayOfWeek={dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X  POST http://{localHostIp}:{keystackIpPort}/api/v1/portGroup/reserve'
                    newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} {keystackUser} '
                    newJob += f'curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&domain={domain}'
                    newJob += f'&reservationUser={reservationUser}&portGroup={portGroup}&removeJobAfterRunning={removeJobAfterRunning}'
                    newJob += f'&release_minute={minute}&release_hour={hour}&release_dayOfMonth={dayOfMonth}&release_month={month}&release_dayOfWeek={dayOfWeek}&webhook=true" '
                    newJob += f'-H "Content-Type: application/x-www-form-urlencoded" -X  POST http://{localHostIp}:{keystackIpPort}/api/v1/portGroup/reserve'
                    
                    if releaseFlag:
                        # removeJobAfterRunning: {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                        #                         'month': '\\*', 'day': '\\*', 'hour': '17', 'minute': '48', 'dayOfWeek': '\\*'}
                        releaseJob = f'{release_minute} {release_hour} {release_dayOfMonth} {release_month} {release_dayOfWeek} {keystackUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&domain={domain}&reservationUser={reservationUser}&portGroup={portGroup}&removeJobAfterRunning=True&release_minute={release_minute}&release_hour={release_hour}&release_dayOfMonth={release_dayOfMonth}&release_month={release_month}&release_dayOfWeek={release_dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/portGroup/release'

                    if reserveFlag:
                        if RedisMgr.redis:
                            keyName = f'scheduler-add-{portGroup}'                    
                            RedisMgr.redis.write(keyName=keyName, data=newJob)
                    
                    if releaseFlag:
                        if RedisMgr.redis:
                            keyName = f'scheduler-add-{getTimestamp()}-{portGroup}'
                            RedisMgr.redis.write(keyName=keyName, data=releaseJob)
                            
                    #JobSchedulerAssistant().createCronJob(newJob)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPortGroupSchedule', msgType='Info', msg=newJob.replace('&webhook=true', ''))            
            
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPortGroupSchedule', msgType='Error',
                                          msg=errMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeleteScheduledPortGroup(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteScheduledPortGroup', exclude=["engineer"])    
    def post(self, request):
        """ 
        Delete a scheduled portGroup.  Called from template.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        removeScheduledPortGroups = request.data.get('removeScheduledPortGroups', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"removeScheduledPortGroups": removeScheduledPortGroups}
            restApi = '/api/v1/portGroup/scheduler/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteScheduledPortGroup')
        else:        
            try:
                #  [{portGroup, month, day, hour, min}, {}, ...]
                removeJobList = []
                for cron in removeScheduledPortGroups:
                    removeJobList.append(cron)
                    
                    # Put the cronjob in redis for the keystackScheduler to remove the cron job
                    if RedisMgr.redis:
                        keyName = f'scheduler-remove-{cron["jobSearchPattern"]}'
                        RedisMgr.redis.write(keyName=keyName, data=cron)
                        
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledPortGroup', msgType='Info',
                                                  msg=cron, forDetailLogs='')
                    else: 
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledPortGroup', msgType='Failed',
                                                  msg='Lost connection to redis server. Failed to remove scheduled job:<br>{cron}', forDetailLogs='')
                        
                JobSchedulerAssistant().removeCronJobs(listOfJobsToRemove=removeJobList)
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledPortGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ScheduledPortGroups(APIView):
    def post(self, request):        
        """         
        Create a data table of scheduled port-groupss. Called by html template.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        portGroupSearchName = request.data.get('portGroup', 'all')
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        html = ''
            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'portGroup': portGroupSearchName}
            restApi = '/api/v1/portGroup/scheduler/scheduledPortGroups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ScheduledPortGroups')
            html = response.json()['portGroupSchedules']
                       
        else: 
            html = '<table class="tableMessages table-bordered">'
            html += '<thead>'
            html += '<tr>'
            html += '<th>Delete</th>'
            html += '<th>User</th>'
            html += '<th>PortGroups</th>'
            html += '<th>Reservation-Schedules</th>'
            html += '<th>Release-Schedules</th>'
            html += '</tr>'
            html += '</thead>'
            
            try:
                cronjobs = JobSchedulerAssistant().getCurrentCronJobs(searchPattern='portGroup=')
                # ['* * * * * hgee /usr/local/python3.10.0/bin/python3.10 /opt/Keystack/Src/crontabTest.py', 
                #  '* */2 * * * hgee /usr/local/python3.10.0/bin/python3.10 /opt/Keystack/Src/crontabTest2.py']
                
                for eachCron in cronjobs:
                    # Handle the \t: '17 *\t* * *\troot    cd / && run-parts --report /etc/cron.hourly
                    eachCron = eachCron.replace('\t', ' ')
                    
                    if portGroupSearchName != 'all' and portGroupSearchName not in eachCron:
                        continue
                    
                    # [{playbook, month, day, hour, min}]
                    # 00 14 31 3 * root curl -d "playbook=sanity&user=Hubert Gee"

                    # eachCron: 23 10 * * * keystack curl -d "mainController=192.168.28.10:28028&remoteController=192.168.28.10:28028&reservationUser=Hubert Gee&portGroup=port-group1&removeJobAfterRunning=True&release_minute=23&release_hour=10&release_dayOfMonth=*&release_month=*&release_dayOfWeek=*&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.10:28028/api/v1/portGroup/release
                    match = search(' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*reservationUser=(.+)&.*portGroup=([^ &]+).*POST *http.+(reserve|release)', eachCron)
                    if match:
                        min               = match.group(1)
                        hour              = match.group(2)
                        day               = match.group(3)
                        month             = match.group(4)
                        dayOfWeek         = match.group(5)
                        reservationUser   = match.group(6)
                        portGroup         = match.group(7)
                        typeOfReservation = match.group(8)

                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="portGroupSchedulerMgmt" jobSearchPattern="portGroup={portGroup}" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        
                        html += f'<td>{reservationUser}</td>'
                        html += f'<td>{portGroup}</td>'
                        
                        if typeOfReservation == 'reserve':
                            html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                            html += '<td></td>'
                            
                        if typeOfReservation == 'release':
                            html += '<td></td>'
                            html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                              
                        html += '</tr>'
                        
                    else:
                        match     = search(' *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+).*', eachCron)
                        min       = match.group(1)
                        hour      = match.group(2)
                        day       = match.group(3)
                        month     = match.group(4)
                        dayOfWeek = match.group(5)
                        
                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="portGroupSchedulerMgmt" jobSearchPattern="" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; DayOfMonth:{day}&emsp; Month:{month}&emsp; DayOfWeek:{dayOfWeek}</td>'
                        html += '</tr>'
                                            
                html += '</table>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ScheduledPortGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        # This is to tell javascript if there are any scheduled job.
        # If there is no job, then hide the remove and close modal buttons
        if '<td>' not in html:
            areThereJobs = False
        else:
            areThereJobs = True
                    
        return Response(data={'portGroupSchedules': html, 'areThereJobs': areThereJobs,
                              'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class GetPortGroupCronScheduler(APIView):
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
            restApi = '/api/v1/portGroup/scheduler/getCronScheduler'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPortGroupCronScheduler')

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
 