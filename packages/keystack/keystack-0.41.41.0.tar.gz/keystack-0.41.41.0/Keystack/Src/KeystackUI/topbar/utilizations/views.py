import os
from re import search

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from domainMgr import DomainMgr
from globalVars import GlobalVars, HtmlStatusCodes    
 
def getEnvSelections():    
    dropdownMenu = f'<input type="checkbox" id="allEnvs" value="allEnvs" name="envCheckboxes"/>&ensp;<label class="modalTextColor" for="allEnvs" style="color:black">All Envs</label><br>'
    
    for root,dirs,files in os.walk(GlobalVars.envPath):
        # /Envs, /Envs/LoadCore, /Envs/qa
        envGroup = root.split(GlobalVars.keystackTestRootPath)[1]
        envGroup = envGroup.replace('/Envs', '')
        dropdownMenu += f'<i class="fa-regular fa-folder" style="color:black"></i>&ensp;<span style="color:black">{envGroup}</span><br>'
        
        for file in files:
            if bool(search('.*#|~|backup.*', file)):
                continue
            
            fullPath = f'{root}/{file}'
            match = search('.*/Envs/(.*)\.(yml|yaml)', fullPath)
            
            filename = file.split('.')[0]
            envGroupAndEnvName = match.group(1)
            
            dropdownMenu += f'&emsp;&emsp;<input type="checkbox" id="{envGroupAndEnvName}" value="{envGroupAndEnvName}" name="envCheckboxes"/>&ensp;<label class="modalTextColor" for="{envGroup}" style="color:black">{filename}</label><br>'
                
    return dropdownMenu

                       
class Utilizations(View):
    @authenticateLogin
    def get(self, request):
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        
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

        return render(request, 'utilizations.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': 'Utilizations',
                       'envDropdownMenu': getEnvSelections(),
                       'user': user,
                       'domainUserRole': domainUserRole,
                      }, status=statusCode)
