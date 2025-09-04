import traceback
from copy import deepcopy

from rest_framework.views import APIView
from rest_framework.response import Response

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.settings.userGroup.userGroupMgr import UserGroupMgr
from domainMgr import DomainMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes
  
class Vars:
    webpage = 'userGroup'


class GetUserAccountDataTable(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetUserAccountDataTable', adminOnly=True)
    def post(self, request):
        """ 
        The left side of the screen       
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        userNames = None
        tableData: str = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/userGroup/getUserAccountDataTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetUserAccountDataTable')
        else:
            try:
                allUserAccounts = AccountMgr().getAllUsers()
                countX = deepcopy(allUserAccounts)
                count = len(list(countX))
                if count > 0:
                    # account: {'fullName': 'john doe'}
                    for account in allUserAccounts:
                        if account['fullName'] == "Administrator":
                            continue
                        
                        tableData += '<tr>'
                        tableData += f'<td class="textAlignCenter"><input type="checkbox" name="userAccountCheckboxes" account="{account["fullName"]}"/></td>'
                        tableData += f'<td class="textAlignLeft">{account["fullName"]}</td>'
                        tableData += '</tr>'

                    # Add extra row to support the tableFixHead2 body with height:0 to 
                    # show a presentable table. Otherwise, if there are a few rows, the row 
                    # height will be large to fill the table size
                    tableData += '<tr></tr>'
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetUserAccountDataTable',
                                          msgType='Error',
                                          msg=f'Failed to get all user accounts:<br>{errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'userNamesDataTable': tableData, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
           
class GetUserGroupUsers(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetUserGroupUsers', adminOnly=True)
    def post(self, request):
        """ 
        The right side of the screen
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userGroupMgr = UserGroupMgr()
        userGroup  = request.data.get('userGroup', None)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        tableData: str = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'userGroup': userGroup}
            restApi = '/api/v1/system/userGroup/users'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetUserGroupUsers')
        else:
            try:
                users = userGroupMgr.getUserGroupUsers(userGroup)
                #allUserAccounts = AccountMgr().getAllUsers()
                
                for accountUser in users:
                    if accountUser == "Administrator":
                        continue
                    
                    tableData += '<tr>'
                    tableData += f'<td class="textAlignCenter"><input type="checkbox" name="userGroupUsersCheckboxes" account="{accountUser}"/></td>'
                    tableData += f'<td class="textAlignLeft">{accountUser}</td>'
                    tableData += '</tr>'
                
                # Add extra row to support the tableFixHead2 body with height:0 to 
                # show a presentable table. Otherwise, if there are a few rows, the row 
                # height will be large to fill the table size
                tableData += '<tr></tr>'
                            
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetUserGroupUsers', msgType='Error',
                                          msg=f'Error: {errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'userGroupUsers': tableData, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
                        
class CreateUserGroup(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='CreateUserGroup', adminOnly=True)
    def post(self, request):

        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userGroupMgr = UserGroupMgr()
        userGroupName  = request.data.get('userGroupName', None).strip()
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'userGroupName': userGroupName}
            restApi = '/api/v1/system/userGroup/create'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='CreateUserGroup')
        else:
            try:
                result = userGroupMgr.isUserGroupExists(userGroupName)
                if result:
                    errorMsg = f'User Group already exists: {userGroupName}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateUserGroup', msgType='Info',
                                                msg=errorMsg, 
                                                forDetailLogs=None)
                    return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)
                        
                response = userGroupMgr.createUserGroup(userGroup=userGroupName)
                if response:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateUserGroup', msgType='Success',
                                                msg=f'Added User Group: {userGroupName}', 
                                                forDetailLogs=None)
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreateUserGroup', msgType='Error',
                                                msg=f'Error: {userGroupName}', 
                                                forDetailLogs=traceback.format_exc(None, errMsg))
                    
                    return Response({'status':'failed', 'errorMsg': f'Failed to create user group: {userGroupName}'}, status=statusCode)            
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUser', msgType='Error',
                                          msg=f'Add user-group error: {userGroupName}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class AddUsersToUserGroup(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddUsersToUserGroup', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userGroupMgr = UserGroupMgr()
        userGroup  = request.data.get('userGroup', None)
        # type = list
        users  = request.data.get('users', None)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'userGroup': userGroup, 'users': users}
            restApi = '/api/v1/system/userGroup/addUsersToUserGroup'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='AddUsersToUserGroup')
        else:
            try: 
                userAlreadyExists = []
                addNonExistingUsers = []

                for verifyUser in users:
                    result = userGroupMgr.isUserInUserGroup(userGroup, verifyUser)
                    
                    if result:
                        userAlreadyExists.append(verifyUser)
                    else:
                        addNonExistingUsers.append(verifyUser)

                if len(addNonExistingUsers) > 0:
                    result = userGroupMgr.addUsers(userGroup, addNonExistingUsers)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUsersToUserGroup', msgType='Success',
                                                msg=f'Added users to User Group: {userGroup}<br>{addNonExistingUsers}<br>Users already exists: {userAlreadyExists}', 
                                                forDetailLogs=None)

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUsersToUserGroup', 
                                          msgType='Error',
                                          msg=f'Error: {errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    

class RemoveUsersFromUserGroup(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemoveUsersFromUserGroup', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userGroupMgr = UserGroupMgr()
        # type = list
        userGroup  = request.data.get('userGroup', None)
        users  = request.data.get('users', None)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'userGroup': userGroup, 'users': users}
            restApi = '/api/v1/system/userGroup/removeUsersFromUserGroup'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='RemoveUsersFromUserGroup')
        else:
            try:        
                result = userGroupMgr.removeUsersFromUserGroup(userGroup, users)

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveUsersFromUserGroup', 
                                          msgType='Error',
                                          msg=f'Error: {errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
 
class DeleteUserGroups(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteUserGroups', adminOnly=True)
    def post(self, request):

        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userGroupMgr = UserGroupMgr()
        # type = list
        userGroup  = request.data.get('userGroup', None).strip()
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'userGroup': userGroup}
            restApi = '/api/v1/system/userGroup/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='DeleteUserGroups')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        else:
            try:       
                userGroupMgr.removeUserGroups(userGroups=[userGroup])

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                # Return not acceptable
                statusCode = HtmlStatusCodes.error
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteUserGroups', msgType='Error',
                                          msg=f'Error: {errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
        
class GetUserGroupsDropdown(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetAllUserGroups', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userGroupMgr = UserGroupMgr()
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        userGroupsDropdownHtml = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/userGroup/getUserGroupsDropdown'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params,
                                                                  user, webPage=Vars.webpage, action='GetAllUserGroupsDropdown')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        else:
            try:
                userGroups = userGroupMgr.getAllUserGroups()
                for userGroup in userGroups:
                    userGroupsDropdownHtml += f'<li class="dropdown-item">{userGroup}</li>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status ='failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetAllUserGroupsDropdown', msgType='Error',
                                          msg=f'Error: {errMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'userGroupsDropdownHtml': userGroupsDropdownHtml, 'status':status, 'errorMsg':errorMsg}, status=statusCode)


class GetUserGroupTable(APIView):
    """ 
    For Domain page left side of the screen.  Show all user-groups for 
    users to add to a domain.
    """
    @verifyUserRole(webPage=Vars.webpage, action='GetUserGroupTable', adminOnly=True)
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userGroupMgr = UserGroupMgr()
        domain  = request.data.get('domain', None)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        userGroupTable: str = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain}
            restApi = '/api/v1/system/userGroup/getUserGroupTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetUserGroupTable')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
        else:
            try:
                userGroupsInDomain = DomainMgr().getUserGroups(domain)
                if GlobalVars.defaultDomain in userGroupsInDomain:
                    defaultDomainIndex = userGroupsInDomain.index(GlobalVars.defaultDomain)
                    userGroupsInDomain.pop(defaultDomainIndex)

                # The left side of the screen
                userGroups = userGroupMgr.getAllUserGroups()
                 
                for userGroup in userGroups:              
                    # {'userGroup': 'myNewGroup'}

                    usersInUserGroup = UserGroupMgr().getUserGroupUsers(userGroup)

                    # Allow users to click on the userGroup to view users in the user-group
                    userGroupUsersDropdown = f'<div class="dropdown"> \
                                                <a class="mt-2 textBlue" href="#" role="button" data-toggle="dropdown" aria-expanded=false>{userGroup}</a> \
                                                <ul class="dropdown-menu">'
                    for user in usersInUserGroup:
                        userGroupUsersDropdown += f'<li class="pl-2 textBlack">{user}</li>'  
                    userGroupUsersDropdown += '</ul></div>'
                
                    # Don't show user-groups that is already in the domain
                    if userGroup in userGroupsInDomain:
                        continue
                    
                    userGroupTable += '<tr>'
                    if userGroup == GlobalVars.defaultDomain:
                        userGroupTable += f'<td class="textAlignCenter"><input type="checkbox" name="userGroupsTableCheckboxes" userGroup="{userGroup}" disabled/></td>'
                    else:
                        userGroupTable += f'<td class="textAlignCenter"><input type="checkbox" name="userGroupsTableCheckboxes" userGroup="{userGroup}"/></td>'
                        
                    userGroupTable += f'<td class="textAlignLeft">{userGroupUsersDropdown}</td>'
                    userGroupTable += '</tr>'
                
                userGroupTable += '<tr></tr>'
                        
            except Exception as errMsg:
                errorMsg = traceback.format_exc(None, errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetUserGroupsTable', msgType='Error',
                                          msg=errorMsg, 
                                          forDetailLogs=errorMsg)

        return Response({'userGroupTable': userGroupTable, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    


    