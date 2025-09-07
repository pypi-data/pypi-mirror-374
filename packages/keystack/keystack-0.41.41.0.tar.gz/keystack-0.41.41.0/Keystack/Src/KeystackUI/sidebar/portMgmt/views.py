import json, os, sys, traceback
      
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from domainMgr import DomainMgr
from globalVars import GlobalVars, HtmlStatusCodes
from db import DB


class Vars:
    webpage = 'portGroup'

'''
class PortMgmt(View):
    @authenticateLogin
    def get(self, request):
        """
        """
        user = request.session['user']
        # User selected domain in Pipelines sidebar menu
        domain = request.GET.get('domain')
        domains = DomainMgr().getUserAllowedDomains(user)
        
        if domain is None and len(domains) > 0:
            domain = domains[0]
        elif domain is None and GlobalVars.defaultDomain in domains:
            domain = GlobalVars.defaultDomain
                              
        # current|archive
        view = request.GET.get('view', 'current') 
        print('\n-- -portMgmt: view:', view)
        
        return render(request, 'portMgmt.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'showDomainSessions': domain,
                       'showDomainView': view,
                       'topbarTitlePage': 'Port Mgmt: Create New Profile',
                       'user': user,
                       'userLevel': request.session['userRole'],
                      }, status=HtmlStatusCodes.success)   
'''

class ShowProfile(View):
    @authenticateLogin
    def get(self, request, profileName=None):
        """
        """
        user = request.session['user']
        
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
            
        data = DB.name.getOneDocument(collectionName='labInventory', fields={'name': profileName})
        if data:
            ipAddress = data['ipAddress']
            ipPort = data['ipPort']
        else:
            ipAddress = None
            ipPort = None
                           
        return render(request, 'showProfile.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'user': user,
                       'domainUserRole': domainUserRole,
                       'topbarTitlePage': f'Port Mgmt: {profileName}',
                       'domain': domain,
                       'profile': profileName,
                       'device': profileName,
                       'ipAddress': ipAddress,
                       'ipPort': ipPort,
                      }, status=HtmlStatusCodes.success)   
        
