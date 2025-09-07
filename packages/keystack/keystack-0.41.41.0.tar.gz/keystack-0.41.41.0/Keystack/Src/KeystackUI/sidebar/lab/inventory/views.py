import json, os, sys, traceback
      
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from domainMgr import DomainMgr
from accountMgr import AccountMgr
from globalVars import GlobalVars, HtmlStatusCodes
from db import DB

class Vars:
    webpage = 'labInventory'

   
class Inventory(View):
    @authenticateLogin
    def get(self, request):
        """
        Get lab inventory
        """
        user = request.session['user']
        # User selected domain
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
                                              
        # mainControllerIp: Informs base.html the main controller IP
        #                   Every view page must include this.
        return render(request, 'inventory.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'domain': domain,
                       'topbarTitlePage': 'Lab Inventory',
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                      }, status=HtmlStatusCodes.success)   


