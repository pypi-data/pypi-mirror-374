import os
#from dotenv import load_dotenv

from django.shortcuts import render
from django.views import View

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from globalVars import GlobalVars, HtmlStatusCodes
from domainMgr import DomainMgr
from accountMgr import AccountMgr
from keystackUtilities import readYaml
from globalVars import GlobalVars


class SystemLogs(View):
    @authenticateLogin
    def get(self, request):
        user = request.session['user']
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        # User selected domain
        domain = request.GET.get('domain')
        userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
        
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
        
        keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
       
        return render(request, 'systemLogs.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'deleteLogs': keystackSettings.get('removeLogsAfterDays', 3),
                       'topbarTitlePage': 'System Logs',
                       'domain': domain,
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                      }, status=HtmlStatusCodes.success)


    