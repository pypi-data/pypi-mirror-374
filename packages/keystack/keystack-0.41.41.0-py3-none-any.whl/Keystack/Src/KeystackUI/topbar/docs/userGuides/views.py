from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from django.views import View
from django.shortcuts import render
        
class UserGuides(View):
    @authenticateLogin
    def get(self, request):
        user = request.session['user']
        status = 200

        return render(request, 'userGuides.html',
                      {'mainControllerIp': request.session['mainControllerIp'],
                       'topbarTitlePage': f'User Guides',
                       'user': user,
                      }, status=status)
        

