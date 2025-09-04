import os, sys, traceback

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

# /path/WebUI/ControlView/topbar/settings
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(currentDir)

from db import DB
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from keystackUtilities import readFile, writeToFile
from globalVars import GlobalVars, HtmlStatusCodes

class Vars:
    webpage = 'settings'


class Settings(View):
    @authenticateLogin   
    def get(self, request):
        """
        Show keystackSystemSettings.yml
        """
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
                
        return render(request, 'systemSettings.html',
                     {'mainControllerIp': request.session['mainControllerIp'],
                      'topbarTitlePage': f'System Settings',
                       'user': user,
                      }, status=statusCode)

