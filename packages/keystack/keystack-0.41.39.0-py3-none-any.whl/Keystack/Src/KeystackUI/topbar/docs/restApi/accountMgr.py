import os, re, sys, json, traceback, secrets
from pprint import pprint

from rest_framework.views import APIView
from rest_framework.response import Response

from db import DB
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole, getUserRole
from accountMgr import AccountMgr
from topbar.settings.userGroup.userGroupMgr import UserGroupMgr
from domainMgr import DomainMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
  
class Vars:
    webpage = 'accountMgmt'
        
        
class GetDomainSelectionForUserAccount(APIView):
    """ 
    Select domain memberships when creating a new user account 
    """
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode = HtmlStatusCodes.success
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/account/getDomainSelectionForUserAccount'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDomainSelectionForUserAccount')
        else:        
            try:
                #allDomains = DomainMgr().getAllDomains()
                allDomains = DomainMgr().getUserAllowedDomains(user)            

                domainSelectionDropdown = '<div class="dropdown">'
                domainSelectionDropdown += "<a class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Select&ensp;&ensp;</a>"
                domainSelectionDropdown += f'<ul id="selectDomainsForUserAccountDropdown" class="dropdown-menu dropdownSizeLarge" aria-labelledby="">'
                
                for index, domain in enumerate(allDomains):
                    domainCharLength = 30 - len(domain)

                    domainSelectionDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" domainIndex="{index}" name="selectedDomains" domain="{domain}">&ensp;&ensp;{domain} {"."*domainCharLength}&emsp;&emsp;'
                    
                    domainSelectionDropdown += f'<label class="testParameterSessionIdLabel" for="admin-{index}">Admin&emsp;&emsp;</label> <input id="admin-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="admin">&emsp;&emsp;&emsp;'
                    
                    domainSelectionDropdown += f'<label for="director-{index}">Director&emsp;&emsp;</label>  <input id="director-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="director">&emsp;&emsp;&emsp;'
                    
                    domainSelectionDropdown += f'<label for="manager-{index}">Manager&emsp;&emsp;</label>  <input id="manager-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="manager">&emsp;&emsp;&emsp;'
                    
                    domainSelectionDropdown += f'<label for="engineer-{index}">Engineer&emsp;&emsp;</label> <input id="engineer-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="engineer" checked></li>'
                    
                domainSelectionDropdown += '<br>'
                domainSelectionDropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectDomainsForUserAccountButton" type="submit" class="btn btn-sm btn-outline-primary">Submit</button></li>'
                domainSelectionDropdown += '</ul></div>'
                      
            except Exception as errMsg:
                domainSelectionDropdown = ''
                errorMsg = str(errMsg)
                status = 'failed'

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDomainSelectionForUserAccount', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
         
        return Response(data={'domainSelections': domainSelectionDropdown, 'status': status, 'errorMsg': errorMsg}, 
                        status=statusCode) 
    
            
class AddUser(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddUser', exclude=['engineer'])
    def post(self, request):
        #body      = json.loads(request.body.decode('UTF-8'))
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user      = AccountMgr().getRequestSessionUser(request)
        domain    = request.data.get('domain', GlobalVars.defaultDomain)
        fullName  = request.data.get('fullName', None).strip()
        loginName = request.data.get('loginName', None).strip()
        password  = request.data.get('password', None).strip()
        email     = request.data.get('email', None).strip()
        sysAdmin  = request.data.get('sysAdmin', False)
        
        # [['KeystackQA', 'engineer'], ['Regression', 'Manager'], ['Sanity', 'director']]
        selectedDomainsCheckboxes = request.data.get('selectedDomainsCheckboxes', [[GlobalVars.defaultDomain, 'engineer']])

        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'fullName': fullName, 'loginName': loginName, 'password': password, 
                      'email': email, 'sysAdmin': sysAdmin, selectedDomainsCheckboxes: selectedDomainsCheckboxes}
            restApi = '/api/v1/system/account/add'
            response, errorMsg , status  = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                            user, webPage=Vars.webpage, action='AddUser')
        else:
            try:  
                if selectedDomainsCheckboxes is None:
                    selectedDomainsCheckboxes = [[GlobalVars.defaultDomain, 'engineer']]
                              
                isFullNameExists = AccountMgr().isUserExists(key='fullName', value=fullName)  
                if isFullNameExists:
                    errorMsg = f'User already exists: {fullName}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUser', 
                                              msgType='Failed', msg=errorMsg)
                    return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)

                isLoginExists = AccountMgr().isUserExists(key='loginName', value=loginName)                    
                if isLoginExists:
                    errorMsg = f'User login name already exists: {loginName}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUser', 
                                              msgType='Failed', msg=errorMsg)
                    return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)

                if email:
                    isEmailExists = AccountMgr().isUserExists(key='email', value=email)                    
                    if isEmailExists:
                        errorMsg = f'User email address already exists: {email}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUser', 
                                                msgType='Failed', msg=errorMsg)
                        return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)
                 
                # if bool(re.search(f'[^ ]+@[^ ]+', email)) is False:
                #     failFlag = True
                #     errorMsg = f'Email address format is incorrect: {email}'
                #     SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUser', 
                #                               msgType='Failed', msg=errorMsg)
                #     return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)
                                                            
                AccountMgr().addUser(fullName=fullName, loginName=loginName, password=password, email=email, sysAdmin=sysAdmin)
                DomainMgr().addNewUserToDomains(user=fullName, domainsAndUserRoles=selectedDomainsCheckboxes)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUser', msgType='Success', msg=f'Added new user: {fullName}')

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddUser', msgType='Error',
                                          msg=f'Add user error: {fullName}<br>{traceback.format_exc(None, errMsg)}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeleteUser(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteUser', adminOnly=True)
    def post(self, request):        
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        fullName = request.data.get('fullName', None).strip()
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'fullName': fullName}
            restApi = '/api/v1/system/account/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteUser')
        else:        
            try:    
                if fullName in ['root', 'Administrator']:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteUser', msgType='Failed',
                                              msg=f'{fullName} cannot be deleted', 
                                              forDetailLogs='')
                elif fullName == user:
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteUser', msgType='Failed',
                                              msg=f'Cannot delete your own account: {fullName}', 
                                              forDetailLogs='')
                else:
                    AccountMgr().deleteUser(fullName=fullName) 
                    DomainMgr().removeUserFromAllDomains(fullName)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteUser', msgType='Success', msg=f'{fullName}')
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteUser', msgType='Error',
                                          msg=f'accountMgmt().DeleteUser() Failed to delete user: {fullName}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status': status, 'errorMsg': errorMsg}, status=statusCode) 

    
class GetUserAccountTableData(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetUserAccountTableData', exclude=['engineer'])
    def post(self, request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None  
        tableData = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/account/tableData'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetUserAccountTableData')

            tableData = response.json()['tableData']    
        else:        
            try:
                userAccountData = AccountMgr().getAllUsersDetails()
                isUserSysAdmin = AccountMgr().isUserSysAdmin(user)

                tableData += '<tr>'
                # {'fullName': 'John Doe', 'loginName': 'jdoe', 'password': 'password', 'email': 'jdoe@domain.com', 'userRole': 'admin',
                # {'domains': {'Communal': {'userRole': 'admin'}}
                
                for index, userAccount in enumerate(userAccountData) :
                    userAllowedDomains = DomainMgr().getUserAllowedDomains(userAccount['fullName'])   
                    isUserAccountSysAdmin = AccountMgr().isUserSysAdmin(userAccount['fullName'])
                            
                    domainSelectionDropdown = '<div class="dropdown">'
                    domainSelectionDropdown += "<a class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>View Domain User-Role&ensp;&ensp;</a>"
                    domainSelectionDropdown += '<ul id="selectDomainsToRemoveDropdown" class="dropdown-menu dropdownSizeMedium" aria-labelledby="">'
                    
                    for domain in userAllowedDomains:
                        domainUserRole = DomainMgr().getUserRoleForDomain(userAccount['fullName'], domain) 
                        if isUserAccountSysAdmin is False:                   
                            domainSelectionDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" name="selectedDomainsToRemove-{index}" domain="{domain}">&ensp;&ensp;Domain: {domain} &emsp; User-Role: {domainUserRole}</li>'
                        else:
                            domainSelectionDropdown += f'<li class="mainFontSize textBlack paddingLeft20px">Domain: {domain} &emsp; User-Role: {domainUserRole}</li>'                            
                            
                    if isUserAccountSysAdmin is False:
                        domainSelectionDropdown += '<br>'
                        domainSelectionDropdown += f'<li class="mainFontSize textBlack paddingLeft20px">'
                        domainSelectionDropdown += f'<button userIndex="{index}" user="{userAccount["fullName"]}" type="submit" class="btn btn-sm btn-outline-primary removeDomainsFromUserButton">Remove Domains</button>&emsp;&emsp;'
                        domainSelectionDropdown += '</li>'
                    
                    domainSelectionDropdown += '</ul></div>'
            
                    if userAccount['fullName'] == 'Administrator':
                        tableData += f'<td></td>'
                    else:
                        tableData += f'<td><a href="#" style="text-decoration:none" userFullName="{userAccount["fullName"]}"onclick="deleteUser(this)">Delete</a></td>'
                        
                    tableData += f'<td><a href="#" user="{userAccount["fullName"]}" onclick="modifyUserForm(this)">{userAccount["fullName"]}</a></td>'
                    tableData += f'<td>{userAccount["loginName"]}</td>'
                    tableData += f'<td>{userAccount["sysAdmin"]}</td>'
                    tableData += f'<td>{domainSelectionDropdown}</td>'
                    tableData += f'<td>{userAccount["email"]}</td>'
                    
                    if isUserSysAdmin or user == userAccount['fullName']:
                        tableData += f'<td><button class="btn btn-sm btn-outline-primary" type="button" user="{userAccount["fullName"]}" onclick="getPassword(this)">Password</button></td>'
                    else:
                        tableData += f'<td><button class="btn btn-sm btn-outline-primary" type="button" user="{userAccount["fullName"]}" onclick="getPassword(this)" disabled>Password</button></td>'
                     
                    if isUserSysAdmin or user == userAccount['fullName']:   
                        tableData += f'<td><button class="btn btn-sm btn-outline-primary" type="button" user="{userAccount["fullName"]}" onclick="openApiKeyModal(this)" data-bs-toggle="modal" data-bs-target="#apiKeyModal">api-key</button></td>'
                    else:
                        tableData += f'<td><button class="btn btn-sm btn-outline-primary" type="button" user="{userAccount["fullName"]}" onclick="openApiKeyModal(this)" data-bs-toggle="modal" data-bs-target="#apiKeyModal" disabled>api-key</button></td>'
                        
                    tableData += '</tr>'            

                tableData += '<tr></tr>'
            except Exception as errMsg:
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='Get', msgType='Error', 
                                          msg=f'GetUserAccountTableData() Error: {errMsg}', 
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'tableData': tableData, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
            
            
class GetDomainSelectionsForExistingUsers(APIView):
    def post(self, request):
        """
        Get user current details.  Used by modify user in accountMgmt template
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        fullName = request.data.get('fullName', None).strip()
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/system/account/getDomainSelectionsForExistingUsers'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDomainSelectionsForExistingUsers')      
        else:            
            allDomains = DomainMgr().getUserAllowedDomains(user)  
                                    
            domainSelectionDropdown = f'<ul id="selectDomainsForExistingUsersDropdown" class="dropdown-menu dropdownSizeLarge" aria-labelledby="">'
            
            for index, domain in enumerate(allDomains):
                domainCharLength = 30 - len(domain)

                domainSelectionDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" domainIndex="{index}" name="selectedDomains" domain="{domain}">&ensp;&ensp;{domain} {"."*domainCharLength}&emsp;&emsp;'
                
                domainSelectionDropdown += f'<label class="testParameterSessionIdLabel" for="admin-{index}">Admin&emsp;&emsp;</label> <input id="admin-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="admin">&emsp;&emsp;&emsp;'
                
                domainSelectionDropdown += f'<label for="director-{index}">Director&emsp;&emsp;</label>  <input id="director-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="director">&emsp;&emsp;&emsp;'
                
                domainSelectionDropdown += f'<label for="manager-{index}">Manager&emsp;&emsp;</label>  <input id="manager-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="manager">&emsp;&emsp;&emsp;'
                
                domainSelectionDropdown += f'<label for="engineer-{index}">Engineer&emsp;&emsp;</label> <input id="engineer-{index}" class="form-check-input" type="radio" name="userRole-{index}" value="engineer" checked></li>'
                
            domainSelectionDropdown += '<br>'
            domainSelectionDropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectDomainsForExistingUsersButton" type="submit" class="btn btn-sm btn-outline-primary">Submit</button></li>'
            domainSelectionDropdown += '</ul></div>'

        return Response({'status':status, 'errorMsg':errorMsg}, status=statusCode)
            
     
class GetUserDetails(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetUserDetails')
    def post(self, request):
        """
        Get user current details.  Used by modify user in accountMgmt template
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        fullName = request.data.get('fullName', None).strip()
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'fullName': fullName}
            restApi = '/api/v1/system/account/getUserDetails'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetUserDetails')
            userDetails['loginName'] = response.json()['loginName']
            userDetails['email']     = response.json()['email']
            userDetails['password']  = response.json()['password']
            userDetails['sysAdmin']  = response.json()['sysAdmin']         
        else:        
            try:
                userDetails = AccountMgr().getUserDetails(key='fullName', value=fullName)
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetUserDetails', msgType='Error', 
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'loginName': userDetails['loginName'], 'email': userDetails['email'],
                         'password': userDetails['password'], 'sysAdmin': userDetails['sysAdmin'], 
                         'status':status, 'errorMsg':errorMsg}, status=statusCode)


class ModifyUserAccount(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='Modify', exclude=['engineer'])
    def post(self, request):
        """
        Modify user details
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request).strip()
        # {'userRole': 'engineer'}
        modifyFields = request.data.get('modifyFields', None)
        userFullName = request.data.get('userFullName', None).strip()
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'modifyFields': modifyFields, 'userFullName': userFullName}
            restApi = '/api/v1/system/account/modify'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ModifyUserAccount')
        else:
            try:
                print('\n--- ModifyUserAccount:', userFullName, modifyFields)
                if 'fullName' in modifyFields:
                    isFullNameExists = AccountMgr().isUserExists(key='fullName', value=modifyFields['fullName'])  
                    if isFullNameExists:
                        errorMsg = f'User already exists: {modifyFields["fullName"]}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyUser', 
                                                  msgType='Failed', msg=errorMsg)
                        return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)

                if 'loginName' in modifyFields:
                    isLoginExists = AccountMgr().isUserExists(key='loginName', value=modifyFields['loginName'])                    
                    if isLoginExists:
                        errorMsg = f'User login name already exists: {modifyFields["loginName"]}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyUser', 
                                                  msgType='Failed', msg=errorMsg)
                        return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)

                if 'email' in modifyFields:
                    isEmailExists = AccountMgr().isUserExists(key='email', value=modifyFields['email'])                    
                    if isEmailExists:
                        errorMsg = f'User email address already exists: {modifyFields["email"]}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyUser', 
                                                  msgType='Failed', msg=errorMsg)
                        return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)
                
                    if bool(re.search(f'[^ ]+@[^ ]+', modifyFields['email'])) is False:
                        errorMsg = f'Email address format is incorrect: {modifyFields["email"]}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyUser', 
                                                  msgType='Failed', msg=errorMsg)
                        return Response({'status':'failed', 'errorMsg':errorMsg}, status=statusCode)
              
                if modifyFields:
                    result = AccountMgr().updateUser(userFullName, modifyFields)
                    if result:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyAccount', msgType='Success', 
                                                msg=f'Modified user account: {userFullName}') 
                    else:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyAccount', msgType='Failed', 
                                                msg=f'Modified user account: {userFullName}')
                        errorMsg = f"Failed to modify user: {userFullName}"
                        status = 'failed'
                                                                            
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyAccount', msgType='Error', 
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status': status, 'errorMsg':errorMsg}, status=statusCode)    


class RemoveDomainsFromUserAccount(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemoveDomainsFromUserAccount', exclude=['engineer'])
    def post(self, request):
        """
        Remove domains from an user account
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request).strip()
        accountUser = request.data.get('accountUser', None)
        domains = request.data.get('domains', [])
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'accountUser': accountUser, 'domains': domains}
            restApi = '/api/v1/system/account/removeDomainsFromUserAccount'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveDomainsFromUserAccount')
        else:
            try:
                DomainMgr().removeUserFromDomain(accountUser, domains)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDomainsFromUserAccount', msgType='success', 
                                          msg=f'Removed domains from user account:<br>user:{accountUser}<br>{domains}')
                                                                  
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDomainsFromUserAccount', msgType='Error', 
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'status': status, 'errorMsg':errorMsg}, status=statusCode)    
    
    
class GetApiKey(APIView):
    @verifyUserRole()
    def post(self, request):
        """
        Get user API-Key from Keystack UI
        For rest api, use accountMgmtViews.py
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userFullName = request.data.get('userFullName', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None                    
        apiKey = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'userFullName': userFullName}
            restApi = '/api/v1/system/account/getApiKey'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetApiKey')
            apiKey = response.json()['apiKey']
        else:
            try:
                if userFullName is None:
                    raise Exception('You must provide a user full name')
                            
                if userFullName == user or getUserRole(request) == 'admin':
                    apiKey = AccountMgr().getApiKey(fullName=userFullName)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetApiKey', msgType='Success', 
                                              msg=userFullName)  
                else:
                    apiKey = "You have no privilege to view other user API-Keys"
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetApiKey', msgType='Failed', 
                                              msg=f'User {userFullName} does not have privilege to view other user API Keys')  
                                        
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetApiKey', msgType='Error', 
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'apiKey': apiKey, 'status':status, 'errorMsg':errorMsg}, status=statusCode)


class RegenerateApiKey(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RegenerateApiKey', exclude=['engineer'])
    def post(self, request):
        """
        Regenerate user API-Key
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userFullName = request.data.get('userFullName', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None       
        apiKey = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'userFullName': userFullName}
            restApi = '/api/v1/system/account/regenerateApiKey'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='RegenerateApiKey')
            apiKey = response.json()['apiKey'] 
        else:
            try:
                if userFullName:            
                    apiKey = AccountMgr().regenerateApiKey(userFullName)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RegenerateApiKey', msgType='Success', 
                                              msg=userFullName)  
                else:
                    status = 'failed'
                    statusCode = HtmlStatusCodes.success
                    errorMsg = 'You must provide the user full name'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RegenerateApiKey', msgType='Error', 
                                              msg=errorMsg)                 
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                statusCode = HtmlStatusCodes.success
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RegenerateApiKey', msgType='Error', 
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
            
        return Response({'apiKey': apiKey, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
        
class GetPassword(APIView):
    @verifyUserRole()
    def post(self, request):
        """
        Get user Password
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        userFullName = request.data.get('userFullName', None)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        password = "No privilege viewing other user passwords"
        
        try:
            if userFullName == user or getUserRole(request) == 'admin':
                password = AccountMgr().getPassword(userFullName)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPassword', msgType='Success', 
                                          msg=userFullName)  
            else:
               SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPassword', msgType='Failed', 
                                         msg=f'{userFullName} does not have privilege to view other user passwords') 
                                       
        except Exception as errMsg:
            errorMsg = str(errMsg)
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPassword', msgType='Error', 
                                      msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response({'password': password, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
    
class CreateAdminAccount:
    """ 
    Create admin account for new controller
    """
    def create(self):
        import secrets
   
        isAdminUserExists = AccountMgr().isUserExists(key='fullName', value='Administrator')
        if isAdminUserExists is False:
            AccountMgr().addUser(fullName='Administrator', loginName='admin', password='admin',
                                 email=None, sysAdmin=True)
                

class GetApiKeyFromRestApi(APIView):
    login = openapi.Parameter(name='login', description="Login name",
                              required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    password = openapi.Parameter(name='password', description="Password",
                              required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)      
    @swagger_auto_schema(tags=['/api/v1/accountMgmt/apiKey'], operation_description="Get user API-Key with login credentials",
                         manual_parameters=[login, password])
    #@verifyUserRole(webPage=Vars.webpage, action='getApiKey', exclude=['engineer'])
    def post(self, request):
        """
        Description:
           Get user API-Key
        
        POST /api/v1/system/accountMgmt/apiKey?login=<login>&password=<password>
        
        Replace <login> and <password>
        
        Parameter:
            login: The login name
            password: The login password
        
        Examples:
            curl -X POST 'http://192.168.28.10:28028/api/v1/system/accountMgmt/apiKey?login=admin&password=admin'
            
            curl -d "login=admin&password=admin" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.10:28028/api/v1/system/accountMgmt/apiKey
            
            curl -d '{"login": "admin", "password": "admin"}' -H "Content-Type: application/json" -X POST http://192.168.28.10:28028/api/v1/system/accountMgmt/apiKey
                      
        Return:
            testcase details
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        login = None
        password = None
        apiKey = None
        errorMsg = None
        status = 'success'
        statusCode =  HtmlStatusCodes.success

        # /api/v1/accountMgmt?login=admin&password=admin
        if request.GET:
            try:
                login = request.GET.get('login')
                password = request.GET.get('password')
                
            except Exception as error:
                errorMsg = f'Expecting parameter login and password, but got: {request.GET}'
                return Response(data={'status': 'failed', 'error': errorMsg}, status=HtmlStatusCodes.error)
            
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                login = request.data['login']
                password = request.data['password']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters login and password, but got: {request.data}'
                status = 'failed'
                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'login': login, 'password': password}
            restApi = '/api/v1/system/account/apiKey'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetApiKeyFromRestApi')
            apiKey = response.json()['apiKey']
                
        else:
            for param in [('login', login), ('password', password)]:
                if param[1] is None:
                    return Response(data={'status': 'failed', 'errorMsg': f'The param {param[0]} is incorrect. Please correct the parameter'},
                                    status=HtmlStatusCodes.error)
            
            try:
                userDetails = AccountMgr().getUserDetails(key='loginName', value=login)
                if password == userDetails['password']:
                    apiKey = userDetails['apiKey']
                else:
                    errorMsg = f'Login name and password failed: {login} / {password}'
                    status = 'failed'
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'

        return Response(data={'status': status, 'apiKey': apiKey, 'errorMsg': errorMsg}, status=statusCode)
   
    
class IsApiKeyValid(APIView):
    def post(self, request):
        """
        Description:
           For internal use only. Verify if the user API-Key is valid.
        
        POST /api/v1/system/account/isApiKeyValid

        Parameter:
            apiKey: The user's api-key
            
        Return:
           fullName | None
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None
        status = 'success'
        statusCode =  HtmlStatusCodes.success
        apiKey = request.data['apiKey']
        result = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'apiKey': apiKey}
            restApi = '/api/v1/system/account/isApiKeyValid'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='IsApiKeyValid')
            result = response.json()['result']                
        else:
            try:
                userDB = DB.name.getDocuments(collectionName='accountMgmt',
                                              fields={'apiKey': apiKey}, includeFields={'_id':0})
                if userDB.count() > 0:
                    result = userDB[0]['fullName']
                else:
                    result = None    
    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                result = None

        return Response(data={'status': status, 'result': result, 'errorMsg': errorMsg}, status=statusCode)
    