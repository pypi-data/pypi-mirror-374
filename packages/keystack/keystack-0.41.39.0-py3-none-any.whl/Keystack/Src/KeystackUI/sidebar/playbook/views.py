from re import search
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from globalVars import HtmlStatusCodes, GlobalVars
from domainMgr import DomainMgr
from accountMgr import AccountMgr
    
    
class Playbook(View):
    @authenticateLogin
    def get(self, request):
        """
        Called by base.html sidebar/playbook <module>
        User selects a playbook
        """
        user = request.session['user']
        group = request.GET.get('group')
        isUserSysAdmin = AccountMgr().isUserSysAdmin(user)
        status = HtmlStatusCodes.success
        domain = 'Unknown'
        playbookGroup = 'Unknown'
        
        # group: Playbooks/DOMAIN=Communal/Samples
        regexMatch = search('.*Playbooks/DOMAIN=(.+?)/(.*)', group)
        if regexMatch:
            domain = f'DOMAIN={regexMatch.group(1)}'
            playbookGroup = f'GROUP={regexMatch.group(2)}'
        else:
            regexMatch = search('.*Playbooks/DOMAIN=(.+)', group)
            if regexMatch:
                domain = f'DOMAIN={regexMatch.group(1)}'
                playbookGroup = f'GROUP=None'

        # SessionMgmt view is the default login page.
        # domain will be None
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
            
        return render(request, 'playbook.html',
                      {'mainControllerIp': request.session['mainControllerIp'], 
                       'selectedPlaybookGroupToView': group,
                       'domain': domain,
                       'playbookGroup': playbookGroup,
                       'topbarTitlePage': f'Playbooks',
                       'user': user,
                       'isUserSysAdmin': isUserSysAdmin,
                       'domainUserRole': domainUserRole,
                      }, status=status)
