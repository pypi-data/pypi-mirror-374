from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from globalVars import GlobalVars, HtmlStatusCodes

from django.views import View
from accountMgr import AccountMgr
from domainMgr import DomainMgr

class RestAPI(View):
    @authenticateLogin
    def get(self, request):
        """
        In order for swagger-ui to be displayed in a view,
        the initial topbar api url must go here to state the .html
        file to open.
        
        In the swagger-ui.html file, use JS to call the schema-swagger-ui url 
        that will render the rest api contents.
        
        Called by base.html sidebar/playbook <module>
        """
        from django.shortcuts import render
        #user = 'Unknown'

        user = request.session['user']
        
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
            
        return render(request, 'swagger-ui.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': f'ReST APIs',
                       'user': user,
                        'isUserSysAdmin': isUserSysAdmin,
                       'domain': domain,
                       'domainUserRole': domainUserRole,
                      }, status=HtmlStatusCodes.success)
        

