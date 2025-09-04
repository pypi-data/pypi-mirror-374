import os, sys, traceback

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

# /path/WebUI/ControlView/topbar/settings
# currentDir = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(currentDir)

from db import DB
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from globalVars import GlobalVars, HtmlStatusCodes
from accountMgr import AccountMgr
from domainMgr import DomainMgr

class LoginCredentials(View):
    @verifyUserRole(webPage='loginCredentials', action='LoginCredentials', adminOnly=True)
    def get(self, request):
        """
        Show keystackSystemSettings.env
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
                
        return render(request, 'loginCredentials.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': f'Login Credentials',
                       'user': user,
                        'isUserSysAdmin': isUserSysAdmin,
                       'domain': domain,
                       'domainUserRole': domainUserRole,
                      }, status=statusCode)


