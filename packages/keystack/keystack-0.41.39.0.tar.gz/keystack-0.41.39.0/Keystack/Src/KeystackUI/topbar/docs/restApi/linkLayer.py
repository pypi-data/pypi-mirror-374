import sys, traceback
from systemLogging import SystemLogsAssistant
from globalVars import HtmlStatusCodes, GlobalVars
from commonLib import getSortedPortList
from pprint import pprint 

from PortGroupMgmt import ManagePortGroup
from db import DB
from RedisMgr import RedisMgr
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets

class Vars:
    webpage = 'linkLayer'
    
    
class ConfigureLinkLayer(APIView):
    def post(self, request):
        """
        Configure Link Layer
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        deviceName = request.data.get('deviceName', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/linkLayer/configure'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ConfigureLinkLayer')   
        else:        
            try:
                domain = 'Communal'
                deviceName = 'device_1'
                print('---- LinkLayer 1 ---- ')
                sys.path.insert(0, '/opt/KeystackSystem/Apps')  
                from Link_Layer.Cisco.Cat6k.layer1 import Layer1      
                Layer1()
                print('---- LinkLayer 2 ---- ')                

                data = DB.name.getOneDocument(collectionName='labInventory',
                                              fields={'domain': domain, 'name': deviceName})   
            
                # TODO: 
                #   Users have to create profiles:
                #       - State which ports to use from which device
                if data:
                    """ 
                    [{'additionalKeyValues': {},
                      'connectedToDevice': 'device-2',
                      'connectedToPort': '2/1',
                      'multiTenant': False,
                      'opticMode': 'single-mode',
                      'port': '1/1',
                      'portGroups': ['portGroup1'],
                      'portType': None,
                      'reserved': 'available',
                      'speed': '1G',
                      'vlanIDs': []},
                      {'additionalKeyValues': {},
                      'connectedToDevice': 'device-2',
                      'connectedToPort': '2/2',
                      'multiTenant': False,
                      'opticMode': None,
                      'port': '1/2',
                      'portGroups': ['portGroup1'],
                      'portType': None,
                      'reserved': 'available',
                      'speed': '1G',
                      'vlanIDs': []},
                      {'additionalKeyValues': {},
                      'connectedToDevice': 'device-2',
                      'connectedToPort': '2/3',
                      'multiTenant': False,
                      'opticMode': None,
                      'port': '1/3',
                      'portGroups': [],
                      'portType': None,
                      'reserved': 'available',
                      'speed': '1G',
                      'vlanIDs': []},
                      {'additionalKeyValues': {},
                      'connectedToDevice': None,
                      'connectedToPort': None,
                      'multiTenant': False,
                      'opticMode': None,
                      'port': '1/4',
                      'portGroups': [],
                      'portType': None,
                      'reserved': 'available',
                      'speed': '1G',
                      'vlanIDs': []},
                      {'additionalKeyValues': {},
                      'connectedToDevice': None,
                      'connectedToPort': None,
                      'multiTenant': False,
                      'opticMode': None,
                      'port': '1/5',
                      'portGroups': [],
                      'portType': None,
                      'reserved': 'available',
                      'speed': '1G',
                      'vlanIDs': []}]
                    """
                    if data['portMgmt']:
                        # ['eth0/1/1', 'eth0/1/2', 'eth0/1/3', 'eth0/3/10', 'eth0/3/11', 'eth0/3/12']
                        portMgmtSortedList = getSortedPortList(data=data['portMgmt'])
                    else:
                        portMgmtSortedList = []

                    pprint(portMgmtSortedList)
                    
                    # Get all the connected-to remote devices
                    allConnectedDevices = {}
                    for index, portDetails in enumerate(portMgmtSortedList):   
                        device = portDetails['connectedToDevice']
                        if device and device not in allConnectedDevices.keys():
                            allConnectedDevices.update({device: {'ports': []}})

                    for device in list(allConnectedDevices.keys()):
                        data1 = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                        if data1:
                            # The device may not have any ports
                            if 'portMgmt' in data1:
                                availablePorts = []
                                for portDetails in data1['portMgmt']:
                                    if portDetails['connectedToPort'] is None:
                                        availablePorts.append(portDetails['port'])
                                        
                                allConnectedDevices[device].update({'ports': availablePorts})
                
                print('\n--- allConections:', allConnectedDevices) 
                      
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ConfigureLinkLayer', msgType='Info',
                                          msg='',forDetailLogs='')      
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                print('---- ConfigureLinkLayer: error:', traceback.format_exc(None, errMsg))
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ConfigureLinkLayer', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode) 
    