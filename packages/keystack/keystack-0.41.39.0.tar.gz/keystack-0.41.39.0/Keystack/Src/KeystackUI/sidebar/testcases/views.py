from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from globalVars import HtmlStatusCodes
    
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from domainMgr import DomainMgr
from accountMgr import AccountMgr
from globalVars import GlobalVars
    

class GetTestcaseFiles(View):
    @authenticateLogin
    def get(self, request, testcase):
        """
        Get all the top-level folders for each module for users to 
        navigate the file system.
        
        When a user clicks on a module folder, the content page has 
        a dropdown menu to select subfolders and files to view or modify.
        """
        user = request.session['user']
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        domain = request.GET.get('domain')
        userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
        
        if domain is None:
            if len(userAllowedDomains) > 0:
                if GlobalVars.defaultDomain in userAllowedDomains:
                    domain = GlobalVars.defaultDomain
                else:
                    domain = userAllowedDomains[0]
 
        if domain:
            request.session['domain'] = domain
            domainUserRole = DomainMgr().getUserRoleForDomain(user, domain) 
        else:
            domainUserRole = None
         
        return render(request, 'testcaseFiles.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': f'Testcases: {testcase}',
                       'testcase': testcase,
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domain': domain,
                       'domainUserRole': domainUserRole,
                      })        