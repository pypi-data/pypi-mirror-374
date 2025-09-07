import os, sys, traceback

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

# /path/WebUI/ControlView/topbar/settings
# currentDir = os.path.abspath(os.path.dirname(__file__))
# sys.path.append(currentDir)

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from keystackUtilities import execSubprocessInShellMode
from globalVars import GlobalVars, HtmlStatusCodes

class Vars:
    webpage = 'systemInstallations'


class SystemInstallations(View):
    @authenticateLogin   
    def get(self, request):
        """
        Install Python packages and Linux OS packages to support 
        scripts and apps
        """
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
                
        return render(request, 'systemInstallations.html',
                     {'mainControllerIp': request.session['mainControllerIp'],
                      'topbarTitlePage': f'System Setup and Info',
                       'user': user,
                      }, status=statusCode)

