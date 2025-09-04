from django.shortcuts import render
from django.views import View

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin, verifyUserRole
from globalVars import GlobalVars, HtmlStatusCodes
    
class Controllers(View):
    @verifyUserRole(webPage='controllers', action='DeleteTestResults', adminOnly=True)
    @authenticateLogin
    def get(self, request):
        """
        Controller Link Manager
        """
        # task: addController | registerAccessKey
        task = request.GET.get('task')
        user = request.session['user']
        statusCode = HtmlStatusCodes.success
        
        if task == 'addController':
            template = 'addControllers.html'
            topbarTitle = 'Add Remote Controller'
            
        if task == 'registerAccessKey':
            template = 'registerAccessKey.html'
            topbarTitle = 'Register Remote Access-Key'
            
        return render(request, template,
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': topbarTitle,
                       'user': user,
                      }, status=statusCode)

