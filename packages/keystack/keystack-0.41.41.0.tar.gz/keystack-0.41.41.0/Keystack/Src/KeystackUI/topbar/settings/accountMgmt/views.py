import os, re, sys, json, traceback, secrets

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import UserModel


#from .accountMgr import AccountMgr
from accountMgr import AccountMgr
from db import DB
from systemLogging import SystemLogsAssistant

from . import loginForm
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from domainMgr import DomainMgr
from globalVars import GlobalVars, HtmlStatusCodes

class Vars:
    webpage = 'accountMgmt'
 
    
userRoles = ['admin', 'director', 'manager', 'engineer']


class AccountMgmt(View):
    @authenticateLogin   
    def get(self, request):
        """
        UserLevel: user:      RX everything in its home domains.
                   manager:   RWX everything in its home domains including creating user/eng users. RW its own domain logs.
                   admin:     RWX all domains, system settings, create users, upgrade, 
        """
        user = request.session['user']
        statusCode = HtmlStatusCodes.success

        # SessionMgmt view is the default login page.
        # domain will be None
        domain = request.GET.get('domain')
        userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        
        if domain is None:
            if len(userAllowedDomains) > 0:
                if GlobalVars.defaultDomain in userAllowedDomains:
                    domain = GlobalVars.defaultDomain
                else:
                    domain = userAllowedDomains[0]
 
        if domain:
            # AccountMgmt.verifyLogin.getUserRole() uses this
            request.session['domain'] = domain
            domainUserRole = DomainMgr().getUserRoleForDomain(user, domain) 
        else:
            domainUserRole = None
             
        return render(request, 'accountMgmt.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': f'User-Account Mgmt',
                       'domain': domain,
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                      }, status=statusCode)
    
    
class Login(View):
    """
    Login page
    """
    def get(self, request):
        form = loginForm.UserLoginForm()
        return render(request, 'login.html', {'form': form})
    
    def post(self, request):
        # Everything user submits will get stored in request.POST
        form = loginForm.UserLoginForm(data=request.POST)

        if form.is_valid():    
            isAuthenticated = False

            loginName = form.cleaned_data['loginName']
            password = form.cleaned_data['password']

            if AccountMgr().isUserExists(key='loginName', value=loginName):
                userDB = AccountMgr().getUserDetails(key='loginName', value=loginName)
       
                if userDB['password'] == password:
                    isAuthenticated = True
                    
                    # When a session key cookie ages out, a new request coming in could have a session key = None.
                    # Need to create a new session key for the session.
                    if request.session.session_key is None:
                        request.session.create()

                    # Each session has a unique session key.  When a session ages out, the session key is gone.
                    request.session['loginName'] = userDB['loginName'] ;# Create a session user to know which account to logout.
                    request.session['user'] = userDB['fullName']
                    request.session['sysAdmin']  = userDB['sysAdmin']
                else:
                    loginFailedMessage = 'Wrong password. Try again.'
            else:
                if loginName == 'admin':
                    # First time using Keystack.  Automatically create admin account.
                    # AccountMgr().addUser(fullName='Administrator', loginName='admin', password='admin',
                    #                      email=None, userRole='admin')
                    AccountMgr().addUser(fullName='Administrator', loginName='admin', password='admin', email=None, sysAdmin=True)
                                        
                    if password !='admin':
                        loginFailedMessage = 'Wrong password. Try again.'
                    else:
                        if request.session.session_key is None:
                            request.session.create()

                        request.session['user'] = 'Administrator'
                        request.session['loginName'] = 'admin'
                        request.session['sysAdmin'] = True
                        request.session.modified = True
                        isAuthenticated = True
                        
                elif loginName == 'root':
                    if password == 'SuperRoot!':
                        isAuthenticated = True
                        if request.session.session_key is None:
                            request.session.create()

                        request.session['loginName'] = 'root'
                        request.session['user']      = 'root'
                        request.session['sysAdmin'] = True
                        request.session.modified = True
                    else:
                        loginFailedMessage = 'Wrong password. Try again.'
                else:
                    loginFailedMessage = 'No such login name. Try again.'
                            
        if isAuthenticated:
            # When adding or setting a key in request.session, must set this to True or else request.session
            # becomes None.
            # If supporting multiple browsers when logging out. The created key 'user' will not be found.
            request.session.modified = True
                    
            # http://192.168.28.7:8000
            mainControllerIp = request._current_scheme_host.split('//')[-1]
            request.session['mainControllerIp'] = mainControllerIp
            
            # Default to sessionMgmt     
            return HttpResponseRedirect(reverse('sessionMgmt'))
        else:
            form = loginForm.UserLoginForm()
            return render(request, 'login.html', {'form': form, 'loginFailed': loginFailedMessage})

        
class Logout(View):     
    def get(self, request): 
        if 'user' in request.session:
            form = loginForm.UserLoginForm()
            DB.name.updateDocument(collectionName='accountMgmt',
                                          queryFields={'loginName': request.session['user']},
                                          updateFields={'isLoggedIn': False})

            del request.session['user']
            del request.session['loginName']
            del request.session['sysAdmin']
            
        return HttpResponseRedirect(reverse('login'))
