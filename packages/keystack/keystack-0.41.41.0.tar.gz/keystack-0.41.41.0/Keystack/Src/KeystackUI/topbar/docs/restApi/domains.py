import os, sys, json, traceback, secrets
from pprint import pprint

from rest_framework.views import APIView
from rest_framework.response import Response

from keystackUtilities import readYaml, writeToYamlFile
from globalVars import GlobalVars, HtmlStatusCodes
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import  verifyUserRole, isUserRoleAdmin
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from domainMgr import DomainMgr
from topbar.settings.userGroup.userGroupMgr import UserGroupMgr


class Vars:
    webpage = 'domains'
    

class CreateDomain(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='CreateDomain', ignoreDomainUserRole=True, adminOnly=True) 
    def post(self, request):
        """ 
        Create a new domain
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = None

        if request.GET:
            domain = request.GET.get('domain', None)

        # REST API        
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            domain = request.data.get('domain', None)
                 
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain}
            restApi = '/api/v1/system/domain/create'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='CreateDomain')
        else:     
            try:    
                if domain in ['', None]:
                    status = 'failed'
                    statusCode = HtmlStatusCodes.error
                    errorMsg = f"A domain name cannot be blank"
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateDomain', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')
                    return Response({'status': status, 'error': errorMsg}, status=statusCode)
                
                else:
                    try:
                        if domain == GlobalVars.defaultDomain:
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateDomain', msgType='Failed',
                                                      msg=f'Cannot create a domain name used by Kesytack: {domain}', 
                                                      forDetailLogs='')
                            return Response({'status': 'failed', 'error': errorMsg}, status=HtmlStatusCodes.success) 
                                                
                        DomainMgr().create(domain)
                        
                    except Exception as errMsg:
                        errorMsg = str(errMsg)
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateDomain', msgType='Error',
                                                    msg=errMsg, 
                                                    forDetailLogs=traceback.format_exc(None, errMsg))
                        return Response({'status': 'failed', 'error': errorMsg}, status=HtmlStatusCodes.error) 

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateDomain', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class DeleteDomains(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='deleteDomains', ignoreDomainUserRole=True, adminOnly=True) 
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = None

        if request.data:
            # list
            domains = request.data.get('domains', None)
        
        if request.GET:
            domains = request.GET.get('domain', None)
            
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domains': domains}
            restApi = '/api/v1/system/domain/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('delete', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeleteDomains')
        else:        
            try:
                if domains in ['', None]:
                    status = 'failed'
                    statusCode = HtmlStatusCodes.error
                    errorMsg = "A domain name cannot be blank"
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDomains', msgType='Error',
                                              msg=f'Failed: A domain name cannot be blank and must be a list', forDetailLogs='')
                    return Response({'status': status, 'error': errorMsg}, status=statusCode)
                
                # /opt/KeystackSystem/.DataLake/domains.yml
                #domainsData = readYaml(GlobalVars.domainsFile)
                for domain in domains:
                    if domain == GlobalVars.defaultDomain:
                        status = 'failed'
                        errorMsg = f"Cannot delete the default domain: {GlobalVars.defaultDomain}"
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDomains', msgType='Error',
                                                msg=f'Cannot delete the default {GlobalVars.defaultDomain} domain', forDetailLogs='')
                        break
                    
                    DomainMgr().delete(domain)
                    
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDomains', msgType='Success',
                                            msg=domains, forDetailLogs='')

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDomains', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class GetDomains(APIView):
    """ 
    The domain landing page
    """
    #@verifyUserRole(webPage=Vars.webpage, action='GetDomains', exclude=['engineer']) 
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        tableData = ''
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/domain/get'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDomains')
            tableData = response.json()['tableData']
        else:        
            try:
                dominsAllowedForUser = DomainMgr().getUserAllowedDomains(user)
                tableData = ''

                for domain in dominsAllowedForUser:
                    users = DomainMgr().getAllUsersInDomain(domain)
                    
                    if len(users) > 0:
                        totalUsers = len(users)
                        usersDropdown = '<div class="dropdown">'
                        usersDropdown += f"<a class='' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{totalUsers} Users&ensp;&ensp;</a>"
                        usersDropdown += '<ul  class="dropdown-menu dropdownSizeSmall" aria-labelledby="">'
                        
                        for index, user in enumerate(users):
                            userRole = DomainMgr().getUserRoleForDomain(user, domain)
                            usersDropdown += f'<li class="mainFontSize textBlack paddingLeft20px">{index+1}: {user} &emsp;&emsp;{userRole}</li>'
                            
                        usersDropdown += '</li>'
                        usersDropdown += '</ul></div>'
                    else:
                        usersDropdown = '0 user' 
                                              
                    tableData += '<tr>'
                    tableData += f'<td class="textAlignCenter"><input type="checkbox" name="domainsCheckboxes" domain="{domain}" /></td>'
                    tableData += f'<td class="textAlignCenter">{domain}</td>'
                    tableData += f'<td class="textAlignCenter">{usersDropdown}</td>'
                    tableData += '</tr>'
                    tableData += '<tr></tr>'
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg).replace("<td>", "").replace("</td>", "")
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDomains', msgType='Error',
                                          msg=errorMsg, forDetailLogs=f'getDomains() -> {traceback.format_exc(None, errMsg).replace("<td>", "").replace("</td>", "")}')
         
        return Response(data={'tableData': tableData, 'status': status, 'errorMsg': errorMsg}, status=statusCode)

                        
class GetAllUsersTableData(APIView):
    """ 
    Add users and user-roles to selected domains
    """
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        data = ''
        tableBody = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/domain/getAllUsersTableData'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetAllUsersTableData')

            tableData = response.json()['tableData']
        else:        
            try:
                allUsers = AccountMgr().getAllUsers()
                
                data += '''<table class="mt-0 table table-sm table-bordered tableFixHead3">
                            <thead>
                                <tr>
                                    <th scope="col" class="textAlignCenter">Select</th>
                                    <th scope="col" class="textAlignCenter">Users</th>
                                    <th scope="col" class="textAlignCenter">User-Roles For The Domain</th>
                                </tr>
                            </thead>'''
                                                    
                for index, eachUser in enumerate(allUsers):
                    tableBody += '<tr>'
                    tableBody += f'<td class="textAlignCenter"><input type="checkbox" userIndex="{index}" name="selectedUserForDomain" userFullName="{eachUser}"></td>'
                    tableBody += f'<td class="textAlignCenter">{eachUser}</td>'
                    
                    tableBody += '<td class="textAlignCenter">'
                    tableBody += f'<label class="paddingTop3px" for="admin-{index}">Admin&emsp;&emsp;&ensp;</label> <input id="admin-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="admin">&emsp;&emsp;'
                    tableBody += f'<label class="paddingTop3px"  for="director-{index}">Director&emsp;&ensp;&emsp;</label> <input id="director-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="director">&emsp;&emsp;'
                    tableBody += f'<label class="paddingTop3px"  for="manager-{index}">Manager&emsp;&emsp;&ensp;</label> <input id="manager-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="manager">&emsp;&emsp;'
                    tableBody += f'<label class="paddingTop3px"  for="engineer-{index}">Engineer&emsp;&emsp;&ensp;</label> <input id="engineer-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="engineer" checked>'
                    tableBody += '</td>'
                    tableBody += '</tr>'
                 
                tableBody += '<tr></tr>'   
                data += f'<tbody>{tableBody}</tbody>'
                data += '</table>'
                                                    
            except Exception as errMsg:
                errorMsg = str(errMsg).replace('<td>', '').replace('</td>', '')
                status = 'failed'
                data = ''
                tableBody = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAllUsersTableData', msgType='Error',
                                        msg=errorMsg, forDetailLogs=f'GetAllUsersTableData() -> {traceback.format_exc(None, errMsg).replace("<td>", "").replace("</td>", "")}')
         
        return Response(data={'tableData': data, 'status': status, 'errorMsg': errorMsg}, status=statusCode)    
    

class AddUsersToDomains(APIView):
    """ 
    Add users to selected domains
    """
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        userAndDomainRoles  = request.data.get('usersAndDomainRoles', [])
        domains = request.data.get('domains', [])

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/domain/addUsersToDomains'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='AddUsersToDomains')
        else:        
            try:
                if len(domains) > 0 and len(userAndDomainRoles) > 0:  
                    DomainMgr().addUsersToDomains(userAndDomainRoles, domains)
                    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUsersToDomains', msgType='Success',
                                              msg=f'Users: {userAndDomainRoles}<br>domains: {domains}', forDetailLogs='')
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUsersToDomains', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
         
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)   
    

class RemoveUsersFromDomains(APIView):
    """ 
    Remove users from selected domains
    """
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        userAndDomainRoles  = request.data.get('usersAndDomainRoles', [])
        domains = request.data.get('domains', [])

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/domain/removeUsersFromDomains'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveUsersFromDomains')
        else:        
            try:
                if len(domains) > 0 and len(userAndDomainRoles) > 0:    
                    DomainMgr().removeUsersFromDomains(userAndDomainRoles, domains)
                    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUsersFromDomains', msgType='Success',
                                              msg=f'Users: {userAndDomainRoles}<br>domains: {domains}', forDetailLogs='')
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUsersFromDomains', msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
         
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)   
    
                                    
class GetDomainsDropdown(APIView):
    """ 
    For selecting a domain
    """
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        tableData = ''
        statusCode = HtmlStatusCodes.success
        domainsDropdown = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/domain/getDomainsDropdown'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDomainsDropdown')

            domainsDropdown = response.json()['domainsDropdown']
        else:        
            try:
                if os.path.exists(GlobalVars.domainsFile):
                    domainsData = readYaml(GlobalVars.domainsFile)
                    tableData = ''
                    for domain in domainsData.keys():
                        domainsDropdown += f'<li class="dropdown-item">{domain}</li>'
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDomainsDropdown', msgType='Error',
                                        msg=errorMsg, forDetailLogs=f'getDomains() -> {traceback.format_exc(None, errMsg)}')
         
        return Response(data={'domainsDropdown': domainsDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)    
      

class RemoveUserGroupsFromDomain(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemoveUserGroupsFromDomain', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)

        domain  = request.data.get('domain', None)
        # type = list
        userGroups  = request.data.get('userGroups', None)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'userGroups': userGroups}
            restApi = '/api/v1/system/domain/removeUserGroups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='RemoveUserGroupsFromDomain')
        else:
            try: 
                result = DomainMgr().removeUserGroups(domain, userGroups)
                if len(result) == 0:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUserGroupsFromDomain', msgType='Success',
                                            msg=f'Removed user-groups from domain: domain={domain}  user-groups={userGroups}', 
                                            forDetailLogs=None)
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUserGroupsFromDomain', 
                                                msgType='Failed',
                                                msg=f'User-Groups not successfully removed from domain {domain}: {result}', 
                                                forDetailLogs=None)
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUserGroupsFromDomain', 
                                          msgType='Error',
                                          msg=f'Error: {errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class AddUserGroupsToDomain(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddUserGroupsToDomain', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)

        domain  = request.data.get('domain', None)
        # type = list
        userGroups  = request.data.get('userGroups', None)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'userGroups': userGroups}
            restApi = '/api/v1/system/domain/addUserGroups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='AddUserGroupsToDomain')
        else:
            try:  
                DomainMgr().addUserGroups(domain, userGroups)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUserGroupsToDomain', msgType='Success',
                                            msg=f'Added user-groups to domain: domain={domain}  user-groups={userGroups}', 
                                            forDetailLogs=None)
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUserGroupsToDomain', 
                                          msgType='Error',
                                          msg=f'Error: {errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
     
class GetDomainUserGroups(APIView):
    """ 
    Get domain user-groups. Show user-groups that have been added to a domain .
    Right side of the screen
    """
    @verifyUserRole(webPage=Vars.webpage, action='GetDomainUserGroups', adminOnly=True) 
    def post(self,request):
        """ 
        The right side of the screen
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        domain  = request.data.get('domain', None)
        errorMsg = None
        status = 'success'
        tableData = ''
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain}
            restApi = '/api/v1/system/domain/getUserGroups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetDomainUserGroups')

            tableData = response.json()['userGroupTableData']
        else:        
            try:
                userGroups = DomainMgr().getUserGroups(domain)
                
                for userGroup in userGroups:
                    usersInUserGroup = UserGroupMgr().getUserGroupUsers(userGroup)
                    userGroupUsersDropdown = f'<div class="dropdown"> \
                                                <a class=" mt-2 textBlue" href="#" role="button" data-toggle="dropdown" aria-expanded=false>{userGroup}</a> \
                                                <ul class="dropdown-menu">'
                    for user in usersInUserGroup:
                        userGroupUsersDropdown += f'<li class="pl-2 textBlack">{user}</li>'  
                    userGroupUsersDropdown += '</ul></div>'
                    
                    if userGroup != GlobalVars.defaultDomain:
                        tableData += '<tr>'
                        tableData += f'<td class="textAlignCenter"><input type="checkbox" name="domainUserGroupCheckboxes" userGroup="{userGroup}"/></td>' 
                        tableData += f'<td class="textAlignLeft">{userGroupUsersDropdown}</td>'
                        tableData += '</tr>'
                 
                tableData += '<tr></tr>'
                                   
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDomainUserGroups', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
         
        return Response(data={'userGroupTableData': tableData, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
class IsUserAllowedInDomain(APIView):
    """ 
    Verify if a user has privilege to a domain.
    If the rest api includes an apiKey, then check apiKey as the user.
    The apiKey is most likely from CLI commnd in cli-secured-mode.
    """
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        domain  = request.data.get('domain', None)
        apiKey  = request.data.get('apiKey', None)
        
        # This user is the user running the test. Could be from CLI
        # apiKey has precedence over this user
        verifyUser   = request.data.get('user', None)
        
        errorMsg = None
        status = 'success'
        tableData = ''
        statusCode = HtmlStatusCodes.success
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'user': user, 'apiKey': apiKey}
            restApi = '/api/v1/system/domain/isUserAllowedInDomain'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='IsUserAllowedInDomain')
            
            isUserAllowedInDomain = response.json()['isUserAllowedInDomain']
        else:        
            try:
                accountMgr = AccountMgr()
                result = False
                
                if verifyUser == 'Administrator' or accountMgr.getUserRole(fullName=verifyUser) == 'admin':
                    result = True
                else:            
                    if apiKey:
                        theUser = accountMgr.getApiKeyUser(apiKey=apiKey)
                        if theUser and accountMgr.getUserRole(fullName=theUser) == 'admin':
                            result = True
                                          
                        if theUser is None and verifyUser is None:
                            return Response(data={'isUserAllowedInDomain': False, 'status': 'failed', 
                                                'errorMsg': 'User=None and provided apiKey is invalid user'}, 
                                            status=statusCode)
                    else:
                        isUserExists = accountMgr.isUserExists(key='fullName', value=verifyUser)
                        if isUserExists:
                            theUser = verifyUser
                        else:
                            result = False
                    
                    if result:
                        userGroups = DomainMgr().getUserGroups(domain)
                        for userGroup in userGroups:
                            usersInUserGroup = UserGroupMgr().getUserGroupUsers(userGroup)
                            if theUser in usersInUserGroup:
                                result = True
                                break
                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='IsUserAllowedInDomain', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
         
        return Response(data={'isUserAllowedInDomain': result, 'status': status, 'errorMsg': errorMsg}, status=statusCode)       
    
    
   
    
