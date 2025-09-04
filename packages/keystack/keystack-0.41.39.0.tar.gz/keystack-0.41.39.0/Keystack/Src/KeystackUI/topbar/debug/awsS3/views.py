from django.shortcuts import render
from django.views import View

from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from globalVars import HtmlStatusCodes
    
class AwsS3(View):
    @authenticateLogin
    def get(self, request):
        user = request.session['user']
        module = request.GET.get('module')
        statusCode = HtmlStatusCodes.success

        return render(request, 'awsS3.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': 'AWS S3 Debug',
                       'user': user
                      }, status=statusCode)
