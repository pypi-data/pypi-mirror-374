from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from globalVars import HtmlStatusCodes
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars
from domainMgr import DomainMgr
from scheduler import JobSchedulerAssistant

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets


class Vars:
    webpage = 'scheduler'


class GetDomainUsers(APIView):
    def post(self, request):
        """
        Get a dropdown list of the domain users for users to select
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', GlobalVars.defaultDomain)
        domainUsersDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/scheduler/getDomainUsers'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDomainUsers')
            usersInDomainDropdown = response.json()['usersInDomainDropdown']
                              
        else:         
            try:
                # Select a user for the reservation
                # Show a list of all users allowed in this domain
                usersAllowedInThisDomains = DomainMgr().getAllUsersInDomain(domain=domain)

                #  class="form-select form-select-sm" 
                domainUsersDropdown = f'<select id="reservationDomainUserSelections">'
                
                for reservationUser in usersAllowedInThisDomains:
                    if reservationUser == user:
                        domainUsersDropdown += f'<option selected value="{reservationUser}">{reservationUser}</option>'
                    else:
                        domainUsersDropdown += f'<option value="{reservationUser}">{reservationUser}</option>'

                domainUsersDropdown += '</select>'
            
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                domainUsersDropdown = ''
                import traceback
                print('\n--- error:', traceback.format_exc(None, errMsg))
            
        return Response(data={'domainUsersDropdown': domainUsersDropdown, 'status':status, 'errorMsg':errorMsg}, status=statusCode)

    
class GetSchedulerCount(APIView):
    def post(self, request):
        """
        Get the total amount of scheduled jobs
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        # searchPattern='env='|'portGroup='|'playbook='
        searchPattern = request.data.get('searchPattern', None)
        totalCronJobs = 0

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'searchPattern': searchPattern}
            restApi = '/api/v1/scheduler/getSchedulerCount'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetSchedulerCount')

            totalCronJobs = response.json()['totalScheduledCronJobs']     
        else:         
            try:
                totalCronJobs = len(JobSchedulerAssistant().getCurrentCronJobs(searchPattern))
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                totalCronJobs = 0
                import traceback

        return Response(data={'totalScheduledCronJobs': totalCronJobs, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    