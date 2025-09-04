import os, sys
from re import search
from django.shortcuts import render
from django.views import View

from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from domainMgr import DomainMgr
from accountMgr import AccountMgr
from globalVars import HtmlStatusCodes, GlobalVars


class PortGroup(View):
    @authenticateLogin
    def get(self, request):
        """
        """
        user = request.session['user']
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
         
        # User selected domain in Pipelines sidebar menu
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
            
        return render(request, 'portGroup.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                       'domain': domain,
                       'topbarTitlePage': f'Port-Group Mgmt: Domain:{domain} ',
                      }, status=HtmlStatusCodes.success)