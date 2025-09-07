import os

from django.shortcuts import render
from django.views import View

from globalVars import HtmlStatusCodes, GlobalVars
from keystackUtilities import readYaml
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from topbar.settings.userGroup.userGroupMgr import UserGroupMgr
from domainMgr import DomainMgr

class Vars:
    webpage = 'domains'
    
    
class Domains(View):
    @authenticateLogin   
    def get(self, request):
        """
        Domain Mgmt
        """
        user = request.session['user']
        domain = request.session['domain']
        domainUserRole = DomainMgr().getUserRoleForDomain(user, domain)
        statusCode = HtmlStatusCodes.success
        
        return render(request, 'domains.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': 'Domain Mgmt',
                       'domain': domain,
                       'domainUserRole': domainUserRole,
                       'user': user,
                      }, status=statusCode)

