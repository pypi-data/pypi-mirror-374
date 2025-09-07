import os, sys, json, traceback
from glob import glob

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole

from execRestApi import ExecRestApi
from globalVars import GlobalVars, HtmlStatusCodes


class Apps(View):
    @authenticateLogin
    def get(self, request):
        """
        Main app page
        """
        user = request.session['user']

        return render(request, 'apps.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': 'Apps',
                       'user': user,
                      }, status=HtmlStatusCodes.success)
