import os, sys, traceback

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

from db import DB
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from globalVars import HtmlStatusCodes

class Vars:
    webpage = 'userGroup'
    

class UserGroup(View):
    @authenticateLogin   
    def get(self, request):
        """
        UserLevel: user:      RX everything in its home domains.
                   manager:   RWX everything in its home domains including creating user/eng users. RW its own domain logs.
                   admin:     RWX all domains, system settings, create users, upgrade, 
        """
        user = request.session['user']
        statusCode = HtmlStatusCodes.success

        return render(request, 'userGroup.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': f'User Group Mgmt',
                       'user': user,
                      }, status=statusCode)
    
