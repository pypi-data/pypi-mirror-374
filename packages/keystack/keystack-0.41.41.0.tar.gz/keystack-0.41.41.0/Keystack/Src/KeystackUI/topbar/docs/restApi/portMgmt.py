import os, sys, traceback
from re import search, IGNORECASE
from copy import deepcopy
from pprint import pprint

from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole, getUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from db import DB
from globalVars import GlobalVars, HtmlStatusCodes
from commonLib import logDebugMsg, netcat, getSortedPortList, getSortedPortList2
from keystackUtilities import readYaml, execSubprocessInShellMode, convertStrToBoolean, convertNoneStringToNoneType
from commonLib import addToKeystackMisc, getKeystackMiscAddtionalFields, isLabInventoryAdditonalKeysDBExists, updateAdditionalKeyDB
from PortGroupMgmt import ManagePortGroup

from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets

currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir)
                
from .labInventory import Vars as LabInventoryVars

class Vars:
    webpage = 'labInventory'
    keystackMisc = 'keystackMisc'
    labInventory = 'labInventory'
    
    portGroup = 'portGroup'
    portTypes = ['None', 'access', 'trunk'] 
    portSpeed = ['None', 'Auto-Neg', '1G', '10G', '25G', '40G', '50G', '100G', '200G', '400G', '800G']                  


def getPortConnectionsTable(user, userRole, domain, deviceName, setCheckboxTableInputNameId):
    """ 
    setCheckboxTableInputNameId: For name="portMgmtCheckboxes-{setCheckboxTableInputNameId}"
    """
    try:
        html = ''
        additionalKeysForJS = []
                    
        data = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': deviceName})   
        additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB)
        
        if data:
            if data['portMgmt']:
                # ['eth0/1/1', 'eth0/1/2', 'eth0/1/3', 'eth0/3/10', 'eth0/3/11', 'eth0/3/12']
                portMgmtSortedList = getSortedPortList(data=data['portMgmt'])
            else:
                portMgmtSortedList = []

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

            # Set VLAN ID and access port-type for all ports
            if userRole != 'engineer':
                vlanDropdownAddVlanId = f'<select class="selectAccessVlanIdForAllPorts mainTextColor" device="{deviceName}" style="background-color:black; border-color:black;">'
                vlanDropdownAddVlanId += '<option label="VLAN" value></option>'
                for vlanId in range(0,4095):
                    vlanDropdownAddVlanId += f'<option value="{vlanId}">{vlanId}</option>'
                vlanDropdownAddVlanId += '</select>'
            else:
                vlanDropdownAddVlanId = 'VLAN'

            if userRole != 'engineer': 
                multiTenantDropdownForAllPorts = f'<select class="selectMultiTenantForAllPorts mainTextColor" device="{deviceName}" style="background-color:black; border-color:black;">'
                multiTenantDropdownForAllPorts += '<option label="PG-Multi-Tenant" hidden selected value></option>'
                multiTenantDropdownForAllPorts += f'<option value="true">True</option>'
                multiTenantDropdownForAllPorts += f'<option value="false">False</option>'
                multiTenantDropdownForAllPorts += '</select>'  
            else:
                multiTenantDropdownForAllPorts = 'PG-Multi-Tenant'
                
            if userRole != 'engineer':            
                opticModeDropdownForAllPorts = f'<select class="opticModeForAllPorts mainTextColor" device="{deviceName}" style="background-color:black; border-color:black;">'
                opticModeDropdownForAllPorts += '<option label="Optic-Mode" hidden selected value></option>'
                opticModeDropdownForAllPorts += f'<option value="multi-mode">multi-mode</option>'
                opticModeDropdownForAllPorts += f'<option value="single-mode">single-mode</option>'
                opticModeDropdownForAllPorts += '</select>'
            else:
                opticModeDropdownForAllPorts = 'Optic-Mode'

            if userRole != 'engineer':  
                portSpeedDropdownForAllPorts = f'<select class="portSpeedForAllPorts mainTextColor" device="{deviceName}" style="background-color:black; border-color:black;">'
                portSpeedDropdownForAllPorts += f'<option label="Port-Speed" value="">None</option>'
                
                for speed in Vars.portSpeed:
                    portSpeedDropdownForAllPorts += f'<option value={speed}>{speed}</option>'
                    
                portSpeedDropdownForAllPorts += '</select>'
            else:
                portSpeedDropdownForAllPorts = 'Port-Speed'
                                                                     
            html += '<div class="row">'
            html += '<table id="portMgmtTable" class="tableFixHead3">'
            html += '<thead>'
            html += '<tr>'

            # Create the table headers
            # <i class="fa-solid fa-arrow-down-long">
            html += '<th><input type="checkbox" id="selectAllPortsCheckboxes" name="selectAllPorts"></th>'
            html += '<th>Src-Ports</th>'
            html += '<th>Connected-To-Device</th>'
            html += '<th>Connected-To-Port</th>'
            html += '<th>Port-Type</th>'
            html += f'<th>{vlanDropdownAddVlanId}</th>'
            html += f'<th>{portSpeedDropdownForAllPorts}</th>'
            html += '<th>Port-Groups</th>'
            html += f'<th>{multiTenantDropdownForAllPorts}</th>'
            #html += f'<th>{opticModeDropdownForAllPorts}</th>'
            
            # Headers for additional fields
            if userRole != 'engineer':
                if len(additionalKeyObj.keys()) > 0:
                    for additionalKey in additionalKeyObj.keys():
                        addedKeySelectOptionsForAllRows = ''
                        fieldType = additionalKeyObj[additionalKey] ['type']
                    
                        addedKeySelectOptionsForAllRows = f'<select class="addKeyForAllPorts mainTextColor" field="{additionalKey}" type="{fieldType}" device="{deviceName}" style="background-color:black; border-color:black;">'
                        addedKeySelectOptionsForAllRows += f'<option label="{additionalKey}" value></option>'
                                                    
                        for option in additionalKeyObj[additionalKey] ['options']:
                            addedKeySelectOptionsForAllRows += f'<option value="{option}">{option}</option>'

                        addedKeySelectOptionsForAllRows += '</select>'
                        html += f'<th>{addedKeySelectOptionsForAllRows}</th>'
                # else:
                #     addedKeySelectOptionsForAllRows = additionalKey
                #     html += f'<th>{addedKeySelectOptionsForAllRows}</th>'
                    
            html += '</tr></thead>'
            html += '<tbody>'
            
            # For each port in current device
            #     portDetails: {'port': '1/1', 'connectedToDevice': 'mySwitch101', 'connectedToPort': '1/1', 'portGroups': ['Port-Group1'], 
            #                   'multiTenant': False, 'opticMode': None, 'vlanTagId': None, 'speed': '1G', 
            #                   'reserved': 'available', 'additionalKeyValues': {'f1': {'type': 'string', 'value': 'Yes'}}}
            for index, portDetails in enumerate(portMgmtSortedList):
                row = index+1
                # Column: Connected-To (device)              
                connectedToDevice = convertNoneStringToNoneType(portDetails['connectedToDevice'])

                # Column: Remote-Port
                if connectedToDevice:
                    if portDetails['connectedToPort'] in [None, '']:
                        if userRole != 'engineer':
                            cellDisplay = 'Select Port'
                        else:
                            cellDisplay = 'None'
                    else:
                        cellDisplay = portDetails['connectedToPort']

                    if userRole != 'engineer':    
                        connectToPortsDropdown = '<div class="dropdown">'
                        connectToPortsDropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{cellDisplay}</a>"                  
                        connectToPortsDropdown += f'<ul class="dropdown-menu remotePortDropdown" aria-labelledby="remotePortDropdown">'
                        if connectedToDevice:
                            # Only if the user selected a connectToDevice, evenremotePortClassEventt
                            # show all of the available ports on the connectedToDevice (remote)
                            for connectingPort in allConnectedDevices[connectedToDevice]['ports']:
                                connectToPortsDropdown += f'<li><a class="mainFontSize textBlack paddingLeft20px" srcDevice="{deviceName}" srcPort="{portDetails["port"]}" remoteDevice="{connectedToDevice}" remotePort="{connectingPort}" href="#">{connectingPort}</a></li>'
                                
                        connectToPortsDropdown += '</ul></div>'
                    else:
                        connectToPortsDropdown = cellDisplay
                else:
                    connectToPortsDropdown = 'None'
                                        
                # Show ports-groups the port belongs to    
                pg = portDetails["portGroups"]
                if len(pg) > 0:
                    portGroups = '<div class="dropdown">'
                    portGroups += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{len(pg)} PortGroups</a>" 
                    # index+1 because portMgmt.js:getPortConnection loops the table rows beginning with row 1 to ignore the header row                 
                    portGroups += f'<ul class="dropdown-menu" aria-labelledby="portGroups">'
                    for portGroup in portDetails['portGroups']:
                        portGroups += f'<li class="mainFontSize textBlack paddingLeft20px">{portGroup}</li>'
                    portGroups += '</ul></div>'
                else:
                    portGroups = None

                if userRole != 'engineer':
                    portType = '<div class="dropdown">'
                    portType += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{portDetails['portType']}</a>" 
                    # index+1 because portMgmt.js:getPortConnection loops the table rows beginning with row 1 to ignore the header row                 
                    portType += f'<ul class="dropdown-menu portTypeDropdown" aria-labelledby="portTypeDropdown">'
                    
                    for pType in Vars.portTypes:
                        portType += f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]}>{pType}</li>'
                        
                    portType += '</ul></div>'
                else:
                    portType = portDetails['portType']

                # Port-type: Access | Trunk:  If Trunk, create a link to add/remove vlan IDs
                vlanIdList = portDetails["vlanIDs"]
                vlanDropdownAddVlanId = 'None'
                
                if portDetails['portType'] == 'access':
                    if len(vlanIdList) > 0:
                        vlanId = vlanIdList[0]
                    else:
                        vlanId = 'Select VlanId'
                    
                    if userRole != 'engineer':
                        vlanDropdownAddVlanId = '<div class="dropdown stylePositionAbsolute">'
                        vlanDropdownAddVlanId += f'<a class="dropdown-toggle textBlack" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>{vlanId}</a>'
                        vlanDropdownAddVlanId += f'<ul class="dropdown-menu selectAccessVlanIdDropdown" aria-labelledby="vlanIds">'
                        for vlanId in range(0,4095):
                            vlanDropdownAddVlanId += f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]} vlan="{vlanId}">{vlanId}</li>'
                            
                        vlanDropdownAddVlanId += '</ul></div>'
                    else:
                        vlanDropdownAddVlanId = vlanId
                        
                if portDetails['portType'] == 'trunk':
                    # Make new variable for this view dropdown and put two dropdowns side-by-side: vlanDropdownAddVlanId  flexRowInlineBlockCenter
                    selectVlanId = '<div class="dropdown">'
                    selectVlanId += f'<a class="textBlack" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false><i class="fa-regular fa-square-plus"></i></a>'  
                    selectVlanId += f'<ul class="dropdown-menu portRow-{row}" aria-labelledby="vlanIds">'
                    for vlanId in range(1,4095):
                        selectVlanId += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" class="selectVlanTrunkIdCheckboxes-{row}" name="selectVlanTrunkIdCheckboxes-{row}" device="{deviceName}" vlanId="{vlanId}" />&ensp;{vlanId}</li>'
                        
                    selectVlanId += f'<br><li class="paddingLeft20px"><button class="btn btn-outline-primary selectVlanTrunkIDsButton" device={deviceName} port={portDetails["port"]} portRow={row} type="button">Select Vlan IDs</button></li>'
                    selectVlanId += '</ul></div>'
                    
                    # Show which Vlan IDs are configured for the port
                    viewCurrentVlanIDs = '<div class="dropdown">'
                    viewCurrentVlanIDs += f'<a class="dropdown-toggle textBlack" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>View</a>'
                    viewCurrentVlanIDs += f'<ul class="dropdown-menu" aria-labelledby="vlanIds">'
                    if len(portDetails['vlanIDs']) > 0:
                        for vlanId in portDetails['vlanIDs']:
                            viewCurrentVlanIDs += f'<li class="mainFontSize textBlack paddingLeft20px">{vlanId}</li>'
                    else:
                        viewCurrentVlanIDs += f'<li class="mainFontSize textBlack paddingLeft20px">No VlanId Selected</li>'
                        
                    viewCurrentVlanIDs += '</ul></div>' 
                    
                    if userRole != 'engineer':               
                        vlanDropdownAddVlanId = f'<div class="flexRowInlineBlockCenter">{viewCurrentVlanIDs} &ensp;&ensp;&ensp; {selectVlanId}</div>'
                    else:
                        vlanDropdownAddVlanId = f'<div class="textAlignCenter">{viewCurrentVlanIDs}</div>'
                                    
                # Multi-Tenant
                if portDetails['multiTenant']:
                    currentMultiTenant = True
                    multiTenantOption = f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]}>False</li>'
                else:
                    currentMultiTenant = False
                    multiTenantOption = f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]}>True</li>'

                if userRole != 'engineer':
                    multiTenant = '<div class="dropdown">'
                    multiTenant += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{currentMultiTenant}</a>" 
                    # index+1 because portMgmt.js:getPortConnection loops the table rows beginning with row 1 to ignore the header row                 
                    multiTenant += f'<ul class="dropdown-menu multiTenantDropdown" aria-labelledby="multiTenantDropdown">'
                    multiTenant += multiTenantOption
                    multiTenant += '</ul></div>'
                else:
                    multiTenant = currentMultiTenant
                    
                # Optic-Mode
                """
                if portDetails['opticMode'] == 'single-mode':
                    currentOpticMode = 'single-mode'
                    opticModeOption = f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]}>multi-mode</li>'
                else:
                    currentOpticMode = 'multi-mode'
                    opticModeOption = f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]}>single-mode</li>'

                if userRole != 'engineer':
                    opticMode = '<div class="dropdown">'
                    opticMode += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{currentOpticMode}</a>" 
                    # index+1 because portMgmt.js:getPortConnection loops the table rows beginning with row 1 to ignore the header row                 
                    opticMode += f'<ul class="dropdown-menu opticModeDropdown" aria-labelledby="opticModeDropdown">'
                    opticMode += opticModeOption
                    opticMode += '</ul></div>'
                else:
                    opticMode = currentOpticMode
                """
                
                if portDetails["speed"] != "None":
                    currentPortSpeed = portDetails["speed"]
                else:
                    currentPortSpeed = 'Select Port-Speed'
                        
                if portDetails['speed']:                                            
                    # Make new variable for this view dropdown and put two dropdowns side-by-side: vlanDropdownAddVlanId  flexRowInlineBlockCenter
                    selectPortSpeed = '<div class="dropdown">'
                    selectPortSpeed += f'<a class="dropdown-toggle textBlack" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>{currentPortSpeed}</a>'  
                    selectPortSpeed += f'<ul class="dropdown-menu portSpeedDropdown" aria-labelledby="portSpeed">'
                    
                    for speed in Vars.portSpeed:
                        selectPortSpeed += f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]} speed={speed}>{speed}</li>'
                        
                    selectPortSpeed += '</ul></div>'
                                                                                                       
                html += '<tr>'
                html += f'<td><input type="checkbox" class="selectAllPortsClassName" name="portMgmtCheckboxes-{setCheckboxTableInputNameId}" domain="{domain}" device="{deviceName}" port={portDetails["port"]} portGroup={portDetails["portGroups"]}></td>'             
                html += f'<td>{portDetails["port"]}</td>'
                html += f'<td>{connectedToDevice}</td>'
                html += f'<td>{connectToPortsDropdown}</td>'
                html += f'<td>{portType}</td>'
                html += f'<td>{vlanDropdownAddVlanId}</td>'
                html += f'<td>{selectPortSpeed}</td>'
                html += f'<td class="portGroup" row="row{row}">{portGroups}</td>'
                html += f'<td>{multiTenant}</td>'
                #html += f'<td>{opticMode}</td>'
                
                # For each additional field, add the value for each port
                for keyName in additionalKeyObj.keys():
                    if keyName in portDetails['additionalKeyValues'].keys():
                        keyValue   = portDetails['additionalKeyValues'][keyName]['value']
                        valueType  = additionalKeyObj[keyName]['type']

                        if additionalKeyObj[keyName]['type'] == 'options':
                            options = additionalKeyObj[keyName]['options']

                        if valueType == 'boolean':
                            dropdown = '<div class="dropdown">'
                            dropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{keyValue}</a>"        
                            dropdown += f'<ul class="dropdown-menu additionalKeys" aria-labelledby="additionalKey">'
                            
                            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]} additionalKey="{keyName}" valueType="{valueType}" >True</li>'
                            dropdown += f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]} additionalKey="{keyName}" valueType="{valueType}">False</li>'
                                                        
                            dropdown += '</ul></div>'
                            html += f'<td>{dropdown}</td>'

                        elif valueType == 'options':
                            dropdown = '<div class="dropdown">'
                            dropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>{keyValue}</a>"        
                            dropdown += f'<ul class="dropdown-menu additionalKeys" aria-labelledby="additionalKey">'
                            
                            for option in options:
                                dropdown += f'<li class="mainFontSize textBlack paddingLeft20px" device={deviceName} port={portDetails["port"]} additionalKey="{keyName}" valueType="{valueType}">{option}</li>'
                                                                                              
                            dropdown += '</ul></div>'
                            html += f'<td>{dropdown}</td>'
                        
                html += '</tr>'
        
            if data:        
                html += '<tr></tr></tbody></table></div>'
                         
    except Exception as errMsg:
        status = "failed"
        errorMsg = str(errMsg)
        SystemLogsAssistant().log(user=user, webPage=Vars.labInventory, action='GetPortConnections', msgType='Error',
                                  msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg).replace('<td>', '[td]')) 

    return html, additionalKeysForJS

                                                                                                
class GetSidebarMenu(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='GetSidebarMenu', exclude=['engineer'])
    def post(self, request):
        """
        Create a layer1 device
        
        Each layer1 switch must have its own device profile that contains
        the IP address and login credentials
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/portMgmt/getSidebarMenu'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='getSidebarMenu')
            html = response.json()['layer1SidebarMenu']    
        else:        
            try:
                data = DB.name.getAllDocuments(collectionName=Vars.webpage,
                                               includeFields={'_id':0, 'name':1}, 
                                               sortBy=[('name', 1)])
                countX = deepcopy(data)
                count = len(list(countX))
                
                html += '<p class="pt-3 pl-3"><a href="#" class="textBlack fontSize12px">Device Inventory</a></p>'
                                
                # <i class="fa-solid fa-gauge-high"></i>&emsp;
                html += '<p class="pt-1 pl-3"><a href="/portMgmt/portGroup" class="textBlack fontSize12px">Port-Group Mgmt</a></p>'
                  
                # <i class="fa-regular fa-square-plus"></i>&emsp; 
                # href="/portMgmt" goes to portMgmt view             
                html += '<p class="pt-1 pl-3"><a href="/portMgmt" id="createLayer1Profile" class="textBlack fontSize12px">Create L1/L2 Link Profile</a></p>'

                if count > 0:
                    html += '<p class="pt-3 pl-3 textBlack fontSize12px">Go to L1/L2 Link Profile:</p>'
                    for layer1Switch in data:    
                        html += f'<p><a href="/portMgmt/showProfile/{layer1Switch["name"]}" class="textBlack fontSize12px paddingLeft40px">{layer1Switch["name"]}</a></p>'
                    
            except Exception as errMsg:
                hmtl = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='getSidebarMenu', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'layer1SidebarMenu': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class ModifyPortAdditionalKeyValue(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='ModifyPortAdditionalDropdownKeyValue', exclude=['engineer'])
    def post(self, request):
        """
        Edit an additional-field format: boolean, opions, list
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', 'None')
        device = request.data.get('device', 'None')
        port   = request.data.get('port', 'None')
        key    = request.data.get('key', 'None')
        value  = request.data.get('value', 'None')
        type   = request.data.get('type', 'None')

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'device': device, 'port': port, 'key': key, 'value': value}
            restApi = '/api/v1/portMgmt/portConnection/modifyPortAdditionalDropdownKeyValue'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ModifyPortAdditionalKeyValue')
        else:  
            try:                 
                portMgmtData = DB.name.getOneDocument(collectionName=Vars.labInventory, fields={'domain':domain, 'name': device})
                if portMgmtData:
                    for index, portMgmt in enumerate(portMgmtData['portMgmt']):
                        portMgmtDBResult = None
                        if port == portMgmt['port']:
                            portMgmt['additionalKeyValues'][key].update({'value': value})
                            break

                        if port == 'all':
                            # Continue with the for loop
                            portMgmt['additionalKeyValues'][key].update({'value': value})
 
                    portMgmtDBResult = DB.name.updateDocument(collectionName=Vars.labInventory,
                                                                queryFields={'domain': domain,
                                                                             'name': device},
                                                                updateFields={'portMgmt': portMgmtData['portMgmt']})
                     
                    if portMgmtDBResult:   
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyPortAdditionalKeyValue', msgType='Success',
                                                  msg=f'Device:{device}  Port:{port}  Key:{key} Value:{value} ', forDetailLogs='')
                    else:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ModifyPortAdditionalKeyValue', msgType='Failed',
                                                  msg=f'Device:{device}  Port:{port}  Key:{key} Value:{value}', forDetailLogs='')                                  
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage='labInventory', action='ModifyPortAdditionalKeyValue', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)        


class GetPortConnections(APIView):
    def post(self, request):
        """
        Get port connections for the showProfile page
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        deviceName = request.data.get('deviceName', None)
        setCheckboxTableInputNameId = request.data.get('setCheckboxTableInputNameId')
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain,
                      "deviceName": deviceName, 
                      'setCheckboxTableInputNameId': setCheckboxTableInputNameId}
            restApi = '/api/v1/portMgmt/getPortConnections'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetPortConnections')
            html = response.json()['portConnections']    
        else:
            userRole = getUserRole(request)
            html, additionalKeysForJS = getPortConnectionsTable(user, userRole, domain, deviceName, setCheckboxTableInputNameId) 

        return Response(data={'portConnections': html,
                              'additionalKeysForJS': additionalKeysForJS,
                              'status': status, 'errorMsg': errorMsg}, status=statusCode)

                                    
class TestConnection(APIView):
    def post(self, request):
        """
        Connect to port device to test reachability
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        netcatResult = 'Failed'
        device      = request.data.get('device', None)
        ipAddress    = convertNoneStringToNoneType(request.data.get('ipAddress', None))
        ipPort       = request.data.get('ipPort', None)
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"device": device, "ipAddress": ipAddress, "ipPort":ipPort}
            restApi = '/api/v1/portMgmt/testConnection'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='TestConnection')
            html = response.json()['html']  
        else:        
            try:
                if ipAddress:
                    testConnection = netcat(ipAddress, ipPort)

                    if testConnection:
                        html += '<span class="fa-solid fa-circle greenColorStatus"></span>'
                        netcatResult = 'Success'
                    else:
                        html += '<span class="fa-solid fa-circle redColorStatus"></span>'     
                    
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='TestConnection', msgType=netcatResult,
                                              msg=f'Port Device Profile={device} ipAddress={ipAddress} ipPort={ipPort}', forDetailLogs='')
                else:
                    errorMsg = f'Profile={device} has no IP Address'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='TestConnection', msgType='Error',
                                              msg=errorMsg, forDetailLogs='')
                    return Response(data={'html': '<span class="fa-solid fa-circle redColorStatus"></span>', 
                                          'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
                                        
            except Exception as errMsg:
                html = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='TestConnection', msgType='Error',
                                          msg=f'Port Device Profile={device} ipAddress={ipAddress} ipPort={ipPort}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'html': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class SelectPortGroupToAddPorts(APIView):
    def post(self, request):
        """
        Port-Group dropdown selection to add ports into a port-group
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', None) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        netcatResult = 'Failed'
        selectPortGroupDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain}
            restApi = '/api/v1/portMgmt/selectPortGroupToAddPorts'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SelectPortGroupToAddPorts')
            selectPortGroupDropdown = response.json()['portGroupOptions']   
        else:        
            try:
                selectPortGroupDropdown = '<div class="dropdown">'
                selectPortGroupDropdown += "<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Add-Ports-To-Port-Group</a>"                  
                selectPortGroupDropdown += f'<ul id="selectPortGroupToAddPorts" class="dropdown-menu" aria-labelledby="portGroupDropdown">' 
                
                for portGroup in ManagePortGroup(domain=domain).getAllPortGroups():
                    selectPortGroupDropdown += f'<li><a class="mainFontSize textBlack paddingLeft20px" href="#">{portGroup["name"]}</a></li>'
                    
                selectPortGroupDropdown += '</ul></div>'

            except Exception as errMsg:
                selectPortGroupDropdown = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SelectPortGroupToAddPorts', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'portGroupOptions': selectPortGroupDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class SelectPortGroupToRemovePorts(APIView):
    def post(self, request):
        """
        Port-Group dropdown selection to remove ports from a port-group
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', None)  
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        netcatResult = 'Failed'
        selectPortGroupDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain}
            restApi = '/api/v1/portMgmt/selectPortGroupToRemovePorts'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SelectPortGroupToRemovePorts')
            selectPortGroupDropdown = response.json()['portGroupOptions']    
        else:        
            try:
                selectPortGroupDropdown = '<div class="dropdown">'
                selectPortGroupDropdown += "<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Remove-Ports-From-Port-Group</a>"                  
                selectPortGroupDropdown += f'<ul id="selectPortGroupToRemovePorts" class="dropdown-menu" aria-labelledby="portGroupDropdown">'
                 
                for portGroup in ManagePortGroup(domain=domain).getAllPortGroups():
                    selectPortGroupDropdown += f'<li><a class="mainFontSize textBlack paddingLeft20px" href="#">{portGroup["name"]}</a></li>'
                    
                selectPortGroupDropdown += '</ul></div>'

            except Exception as errMsg:
                selectPortGroupDropdown = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SelectPortGroupToRemovePorts', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'portGroupOptions': selectPortGroupDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class AddPortsToPortGroup(APIView):
    def post(self, request):
        """
        Put ports to a portGroup
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        portGroup = request.data.get('portGroup', None)
        portsToBeAdded = request.data.get('ports', None)
 
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'device': device,
                      'portGroup': portGroup, 'ports': portsToBeAdded}
            restApi = '/api/v1/portMgmt/addPortsToPortGroup'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='addPortsToPortGroup')  
        else:        
            try:
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory',
                                                      fields={'domain': domain, 'name': device})
                portGroupData = ManagePortGroup(domain=domain, portGroup=portGroup).getPortGroupDetails()
         
                def isPortValidForPortGroup():
                    """ 
                    Check if the port is multi-tenant before adding to the port-group
                    """
                    portInPortGroupAlready = []
                    for port in portsToBeAdded:
                        for eachPort in portMgmtData['portMgmt']:
                            # {'port': '1/5', 'connectedToDevice': None, 'connectedToPort': None, 'portGroups': [], 
                            #  'multiTenant': False, 'opticMode': None, 'vlanTagId': None, 'speed': '1G', 'reserved': 'available'}                             
                            existingPort = eachPort['port']
                            existingPortGroups = eachPort['portGroups']
                            multiTenant = eachPort['multiTenant']
                                                             
                            if existingPort == port:
                                # Request to add another port-group and multiTenant is False
                                if len(existingPortGroups) > 0 and portGroup not in existingPortGroups and multiTenant is False:
                                    portInPortGroupAlready.append(port)

                                # Request to add port to the same port-group
                                if len(existingPortGroups) > 0 and portGroup in existingPortGroups:
                                    portInPortGroupAlready.append(port)
                                    
                    return portInPortGroupAlready
                
                portInPortGroupAlready = isPortValidForPortGroup()    
                if len(portInPortGroupAlready) > 0:
                    errorMsg = f'Selected ports are in a port-group already and these ports are not multi-tenant=True. Either remove the ports from the existing portGroups or set the ports to multi-tenant=True:<br>{portInPortGroupAlready}'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='addPortsToPortGroup', msgType='Failed',
                                              msg=errorMsg, forDetailLogs='')                
                    return Response(data={'status':'failed', 'errorMsg': errorMsg}, status=statusCode)

                if portGroupData:
                    toBeAddedSortedPortList = getSortedPortList2(portsToBeAdded)

                    # There is domain. Check for device.
                    if device not in portGroupData['ports'].keys():
                        #portGroupData['ports'][device] = {}
                        portGroupData['ports'][device] = {'domain': domain, 'ports': []}
                        
                    # Device exists. Check if ports need to be added is in the port-group
                    addPortList = []
                    for port in toBeAddedSortedPortList:                                     
                        if port not in portGroupData['ports'][device]['ports']:
                            addPortList.append(port)

                    addSortedPortList = getSortedPortList2(portGroupData['ports'][device]['ports'] + addPortList)
                    portGroupData['ports'][device]['ports'] = addSortedPortList
                    portGroupDBResult = ManagePortGroup(domain, portGroup).update(key='ports', value=portGroupData['ports'])
                    
                    if portGroupDBResult:   
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='addPortsToPortGroup', msgType='Success',
                                                  msg=f'Domain:{domain} PortGroup:{portGroup}  Ports:{portsToBeAdded}', forDetailLogs='')
                    else:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='addPortsToPortGroup', msgType='Failed',
                                                  msg=f'Domain:{domain} PortGroup:{portGroup}  Ports:{portsToBeAdded}', forDetailLogs='') 
                      
                    # Update labInventory PortMgmtDB: adding ports to a portGroup
                    if portMgmtData:
                        addPortsToPortMgmt = []

                        # Ports that the user wants to add to the port-group
                        for port in portsToBeAdded:
                            # Loop through each port in the device's list to get its port-group        
                            for index, existingPort in enumerate(portMgmtData['portMgmt']):
                                if existingPort['port'] == port:
                                    existingPort['portGroups'].append(portGroup)
                                    portMgmtData['portMgmt'].pop(index)
                                    portMgmtData['portMgmt'].insert(index, existingPort)

                        portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                                  queryFields={'domain': domain, 'name': device},
                                                                  updateFields={'portMgmt': portMgmtData['portMgmt']})
                     
                        if portMgmtDBResult:   
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='addPortsToPortGroup', msgType='Success',
                                                      msg=f'Domain:{domain} PortGroup:{portGroup}  Ports:{portsToBeAdded}', forDetailLogs='')
                        else:
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='addPortsToPortGroup', msgType='Failed',
                                                      msg=f'Domain:{domain} PortGroup:{portGroup}  Ports:{portsToBeAdded}', forDetailLogs='') 
                                                                                              
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='addPortsToPortGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                        
        return Response(data={'status':status, 'errorMsg': errorMsg}, status=statusCode)
    

class RemovePortsFromPortGroup(APIView):
    def post(self, request):
        """
        Remove ports from a port-group
        Note: Each port could reside in different port-groups (multi-tenancy)
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        portGroup = request.data.get('portGroup', None)
        
        # Format: ['1/1', '1/2', '1/3']
        ports = request.data.get('ports', [])

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'device': device, 'portGroup': portGroup, 'ports': ports}
            restApi = '/api/v1/portMgmt/removePortsFromPortGroup'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                            user, webPage=Vars.webpage, action='removePortsFromPortGroup')
        else:        
            try:
                portGroupData = ManagePortGroup(domain=domain, portGroup=portGroup).getPortGroupDetails()
                if portGroupData:
                    if len(portGroupData['activeUsers']) > 0:
                        errorMsg = f'PortGroup is currently in-used by:<br>{portGroupData["activeUsers"]}. The port-group must be released in order to be removed.'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removePortsFromPortGroup', msgType='Failed',
                                                  msg=errorMsg, forDetailLogs='') 
                        return Response(data={'status':'failed', 'errorMsg': errorMsg}, status=statusCode)

                    if len(portGroupData['waitList']) > 0:
                        errorMsg = f'The port-group has a wait-list by:<br>{portGroupData["waitList"]}. The wait-list must be cleared in order to be removed.'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removePortsFromPortGroup', msgType='Failed',
                                                  msg=errorMsg, forDetailLogs='') 
                        return Response(data={'status':'failed', 'errorMsg': errorMsg}, status=statusCode)
                    
                    notLocatedPorts = []                      
                    for port in ports:
                        try:
                            for index, eachExistingPort in enumerate(portGroupData['ports'][device]['ports']):
                                if eachExistingPort == port:
                                    portGroupData['ports'][device]['ports'].pop(index)
                        except:
                            # Arriving here mean domain/device keys are not found in portGroupData['ports']
                            notLocatedPorts.append(port)
                    
                    if len(notLocatedPorts) > 0:
                        errorMsg = f'The port(s) are not in port-group: {portGroup}<br>Ports: {notLocatedPorts[0:]}'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removePortsFromPortGroup', msgType='Failed',
                                                  msg=errorMsg, forDetailLogs='') 
                        return Response(data={'status':'failed', 'errorMsg': errorMsg}, status=statusCode)
                                            
                    portGroupDBResult = ManagePortGroup(domain, portGroup).update(key='ports', value=portGroupData['ports'])
                    if portGroupDBResult:   
                        SystemLogsAssistant().log(user=user, webPage=Vars.portGroup, action='removePortsFromPortGroup', msgType='Success',
                                                  msg=ports, forDetailLogs='')
                    else:
                        SystemLogsAssistant().log(user=user, webPage=Vars.portGroup, action='removePortsFromPortGroup', msgType='Failed',
                                                  msg=ports, forDetailLogs='') 
                                     
                    # Update portMgmt DB:  Remove the port-group from each port
                    portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                    if portMgmtData:
                        for port in ports:
                            for index, eachPortDetails in enumerate(portMgmtData['portMgmt']):
                                if eachPortDetails['port'] == port:
                                    if portGroup in eachPortDetails['portGroups']:
                                        index2 = eachPortDetails['portGroups'].index(portGroup)
                                        eachPortDetails['portGroups'].pop(index2)
                                        portMgmtData['portMgmt'].pop(index)
                                        portMgmtData['portMgmt'].insert(index, eachPortDetails)                            
                
                        portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                                  queryFields={'domain': domain, 'name': device},
                                                                  updateFields={'portMgmt': portMgmtData['portMgmt']})
                        if portMgmtDBResult:   
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removePortGroupFromPorts', msgType='Success',
                                                    msg=ports, forDetailLogs='')
                        else:
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removePortGroupFromPorts', msgType='Failed',
                                                    msg=ports, forDetailLogs='')                      
                    
                    # TODO: If port-group is empty, remove the device from the port-group
                    ManagePortGroup(domain, portGroup).removeDevicesFromPortGroupIfNoPorts()
                                          
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='removePortsFromPortGroup', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                        
        return Response(data={'status':status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetConnectPortsToLinkDeviceDropdown(APIView):
    def post(self, request):
        """
        User selects ports to connected-to. 
        Get a dropdown of link device names to select.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        linkDevicesHtml = ''
        linkDevicePortsHtml = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/portMgmt/getConnectPortsToLinkDeviceDropdown'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetConnectPortsToLinkDeviceDropdown')
            linkDevicesHtml = response.json()['linkDevicesHtml']
            linkDevicePortsHtml = response.json()['linkDevicePortsHtml']
                
        else:        
            try:
                allDevicesObj = DB.name.getAllDocuments(collectionName='labInventory',
                                                        includeFields={'_id':0, 'name':1, 'ports':1},
                                                        sortBy=[('name', 1)])
                allDevices = list(allDevicesObj)
                if allDevices:          
                    linkDevicesHtml = '<div class="dropdown">'
                    linkDevicesHtml += "<a class='dropdown-toggle textBlack' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Connect-Ports-To-Device</a>"                  
                    linkDevicesHtml += f'<ul id="selectConnectToLinkDevice" class="dropdown-menu" aria-labelledby="connectedTo">'
                    
                    for linkDevice in allDevices:
                        linkDevicesHtml += f'<li><a class="mainFontSize textBlack paddingLeft20px" href="#">{linkDevice["name"]}</a></li>'
                        
                    linkDevicesHtml += '</ul></div>'
                
            except Exception as errMsg:
                linkDevicesHtml = ''
                linkDevicePortsHtml = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetConnectPortsToLinkDeviceDropdown', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'linkDevicesHtml': linkDevicesHtml, 'linkDevicePortsHtml': linkDevicePortsHtml, 
                              'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
        
class ConnectToLinkDevice(APIView):
    def post(self, request):
        """
        Connect ports to the link-device
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain         = request.data.get('domain', None)
        fromLinkDevice = request.data.get('fromLinkDevice', None)
        fromPorts      = request.data.get('ports', None)
        toLinkDevice   = request.data.get('toLinkDevice', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 
                      'fromLinkDevice': 'fromLinkDevice', 
                      'fromPorts': fromPorts,
                      'toLinkDevice': toLinkDevice}
            restApi = '/api/v1/portMgmt/connectToLinkDevice'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ConnectToLinkDevice')
        else:        
            try:
                portAlreadyConnectedToDevice = []
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': fromLinkDevice})
                if portMgmtData:
                    for index, portObj in enumerate(portMgmtData['portMgmt']):
                        port = portObj['port']
                        isConnectedToDevice = portObj['connectedToDevice']
                        if port in fromPorts:
                            if isConnectedToDevice:
                                portAlreadyConnectedToDevice.append(port)

                    if len(portAlreadyConnectedToDevice) == 0:
                        for index, portObj in enumerate(portMgmtData['portMgmt']):
                            port = portObj['port']                        
                            if port in fromPorts:
                                portObj['connectedToDevice'] = toLinkDevice
                                portMgmtData['portMgmt'].pop(index)
                                portMgmtData['portMgmt'].insert(index, portObj)
                                
                        portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                                  queryFields={'domain': domain, 'name': fromLinkDevice},
                                                                  updateFields={'portMgmt': portMgmtData['portMgmt']})
                        if portMgmtDBResult:   
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ConnectPortsToLinkDevice', msgType='Success',
                                                    msg=f'Link device:{fromLinkDevice} ports:{fromPorts} connect to link device:{toLinkDevice}', forDetailLogs='')
                        else:
                            status = 'failed'
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ConnectPortsToLinkDevice', msgType='Failed',
                                                    msg=f'Failed to connect ports to link device. fromDevice:{fromLinkDevice} toDevice:{toLinkDevice}', forDetailLogs='')      
                        
                    else:
                        # 1 or more src ports are currently connected to a device. User must disconect the src port first.
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ConnectPortsToLinkDevice', msgType='Failed',
                                                  msg=f'Failed to connect ports to link device. fromDevice:{fromLinkDevice} toDevice:{toLinkDevice}<br>Must disconnect srcPorts first: {portAlreadyConnectedToDevice}', forDetailLogs='') 
                        
                        return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode) 

            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ConnectPortsToLinkDevice', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
   

class DisconnectPorts(APIView):
    def post(self, request):
        """
        Disconnect ports. Set connectTo=None on selected ports.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        ports = request.data.get('ports', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'device': device, 'ports': ports}
            restApi = '/api/v1/portMgmt/disconnectPorts'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DisconnectPorts')
        else:        
            try:
                # Get a list of ports from each connectedToDevice to remove after removing from the src profile
                remoteDevice = {}
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                if portMgmtData:
                    for index, portObj in enumerate(portMgmtData['portMgmt']):
                        port = portObj['port']
                        connectedToDevice = portObj['connectedToDevice']
                        connectedToPort = portObj['connectedToPort']
                        if port in ports:
                            # Clear the src device
                            portObj['connectedToDevice'] = None
                            portObj['connectedToPort'] = None
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portObj)
                            
                            # Gather remote device and ports
                            if connectedToDevice not in list(remoteDevice.keys()):
                                remoteDevice.update({connectedToDevice: {'ports': []}})
                
                            remoteDevice[connectedToDevice]['ports'].append(connectedToPort)

                    portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                              queryFields={'domain': domain, 'name': device},
                                                              updateFields={'portMgmt': portMgmtData['portMgmt']})
                    if portMgmtDBResult:   
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DisconnectPorts', msgType='Success',
                                                  msg=f'Disconnected: From Link device:{device} ports:{ports}', forDetailLogs='')
                    else:
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DisconnectPorts', msgType='Failed',
                                                  msg=f'Disconnected: From Link device:{device} ports:{ports}', forDetailLogs='') 
                        
                for remoteDevice, value in remoteDevice.items():
                    remotePortMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': remoteDevice})
                    
                    # Not all devices have portMgmt (ports)
                    if remotePortMgmtData and 'portMgmt' in remotePortMgmtData:
                        for index, portObj in enumerate(remotePortMgmtData['portMgmt']):
                            if portObj['port'] in value['ports']:
                                portObj['connectedToDevice'] = None
                                portObj['connectedToPort'] = None
                                remotePortMgmtData['portMgmt'].pop(index)
                                remotePortMgmtData['portMgmt'].insert(index, portObj)

                        portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                                  queryFields={'domain': domain, 'name': remoteDevice},
                                                                  updateFields={'portMgmt': remotePortMgmtData['portMgmt']})
                        if portMgmtDBResult:   
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DisconnectPorts', msgType='Success',
                                                      msg=f'Disconnected: From Link device:{remoteDevice} ports:{value["ports"]}',
                                                      forDetailLogs='')
                        else:
                            status = 'failed'
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DisconnectPorts', msgType='Failed',
                                                      msg=f'Disconnected: From Link device:{remoteDevice} ports:{value["ports"]}',
                                                      forDetailLogs='')                                  
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DisconnectPorts', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                 
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)     
    

class SetRemotePortConnection(APIView):
    def post(self, request):
        """
        Set the remote link port: connectedToPort
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        srcDevice = request.data.get('srcDevice', None)
        srcPort = request.data.get('srcPort', None)
        remoteDevice = request.data.get('remoteDevice', None)
        remotePort = request.data.get('remotePort', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 
                      'device': srcDevice, 
                      'srcPort': srcPort, 
                      'remoteDevice': remoteDevice,
                      'remotePort': remotePort}
            restApi = '/api/v1/portMgmt/setRemotePortConnection"'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SetRemotePortConnection')
        else:  
            try:
                currentConnectedToRemotePorts = []
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': srcDevice})
                if portMgmtData:
                    for index, portObj in enumerate(portMgmtData['portMgmt']):
                        if portObj['port'] == srcPort:
                            currentConnectedToRemotePorts.append(portObj['connectedToPort'])
                            portObj['connectedToPort'] = remotePort
                            portObj['connectedToDevice'] = remoteDevice
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portObj)

                    portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                              queryFields={'name': srcDevice},
                                                              updateFields={'portMgmt': portMgmtData['portMgmt']})
                
                # On the remote device, set new port connection                      
                remoteDevicePortData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': remoteDevice})
                if remoteDevicePortData:
                    for index, remotePortObj in enumerate(remoteDevicePortData['portMgmt']):
                        if remotePortObj['port'] == remotePort:
                            remotePortObj['connectedToPort'] = srcPort
                            remotePortObj['connectedToDevice'] = srcDevice
                            remoteDevicePortData['portMgmt'].pop(index)
                            remoteDevicePortData['portMgmt'].insert(index, remotePortObj)
                    
                            # Remove current port connection
                        if remotePortObj['port'] in currentConnectedToRemotePorts and remotePortObj['port'] is not None:
                            remotePortObj['connectedToPort'] = None
                            remotePortObj['connectedToDevice'] = None
                            remoteDevicePortData['portMgmt'].pop(index)
                            remoteDevicePortData['portMgmt'].insert(index, remotePortObj)   

                    portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                              queryFields={'domain': domain, 'name': remoteDevice},
                                                              updateFields={'portMgmt': remoteDevicePortData['portMgmt']})                                        
                    if portMgmtDBResult:   
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetRemotePortConnection', msgType='Success',
                                                  msg=f'On device:{srcDevice}. SrcPort:{srcPort} connected to remote port: {remotePort}', forDetailLogs='')
                    else:
                        status = 'failed'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetRemotePortConnection', msgType='Failed',
                                                  msg=f'On device:{srcDevice}. Failed to connect from Srcport:{srcPort} to remote port: {remotePort}', forDetailLogs='')                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetRemotePortConnection', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                 
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)     
    
        
class SetPortMultiTenant(APIView):
    def post(self, request):
        """
        Set the port's multi-tenant True|False to allow or not 
        allow ports in multiple port-groups
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        port   = request.data.get('port', None)
        
        # Dropdown selection values are string type. Must convert string to boolean.
        multiTenantSelection = convertStrToBoolean(request.data.get('multiTenantSelection', None))
    
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "device": device, "port": port, 'multiTenantSelection': multiTenantSelection}
            restApi = '/api/v1/portMgmt/setMultiTenant'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SetPortMultiTenant')
        else:        
            try:

                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                if portMgmtData:
                    
                    for index, portMgmtPort in enumerate(portMgmtData['portMgmt']):
                        if port != 'all' and portMgmtPort['port'] == port:
                            if len(portMgmtPort['portGroups']) > 1 and multiTenantSelection is False:
                                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortMultiTenant', msgType='Failed',
                                                          msg=f'Domain: {domain} device: {device}: Multi-Tenant on port {port} cannot be set to {multiTenantSelection} because the port currently belongs to multiple Port-Groups. Remove the port from Port-Groups.', forDetailLogs='')
                                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
                            
                            portMgmtPort.update({'multiTenant': multiTenantSelection})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                            break

                        if port == 'all':
                            if len(portMgmtPort['portGroups']) > 1 and multiTenantSelection is False:
                                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortMultiTenant', msgType='Failed',
                                                          msg=f'Domain: {domain} device: {device}: Multi-Tenant on port {port} cannot be set to {multiTenantSelection} because the port currently belongs to multiple Port-Groups. Remove the port from Port-Groups.', forDetailLogs='')
                                return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.error)
                            
                            portMgmtPort.update({'multiTenant': multiTenantSelection})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                                                        
                portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                          queryFields={'domain': domain, 'name': device},
                                                          updateFields={'portMgmt': portMgmtData['portMgmt']})
                if portMgmtDBResult:   
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortMultiTenant', msgType='Success',
                                              msg=f'Domain: {domain} Device: {device}: Multi-Tenant on port {port} = {multiTenantSelection}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortMultiTenant', msgType='Failed',
                                              msg=f'Domain: {domain} Device: {device}: DB failure: Multi-Tenant on port {port} = {multiTenantSelection}', forDetailLogs='')
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortMultiTenant', msgType='Error',
                                          msg=f'Domain: {domain} Device: {device}  Port: {port} MultiTenant: {multiTenantSelection}:<br>{traceback.format_exc(None, errMsg)}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class SetOpticMode(APIView):
    def post(self, request):
        """
        Set the port's fiber mode: single|multi
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        port   = request.data.get('port', None)
        opticMode = request.data.get('opticMode', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "device": device, "port": port, 'opticMode': opticMode}
            restApi = '/api/v1/portMgmt/setOpticMode'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SetOpticMode')
        else:        
            try:
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                if portMgmtData:
                    for index, portMgmtPort in enumerate(portMgmtData['portMgmt']):
                        if port != 'all' and portMgmtPort['port'] == port:
                            portMgmtPort.update({'opticMode': opticMode})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                            break
                        
                        if port == 'all':
                            portMgmtPort.update({'opticMode': opticMode})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                                                        
                portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                          queryFields={'domain': domain, 'name': device},
                                                          updateFields={'portMgmt': portMgmtData['portMgmt']})
                if portMgmtDBResult:   
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetOpticMode', msgType='Success',
                                              msg=f'Port device: {device}: Optic-Mode on port {port} = {opticMode}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetOpticMode', msgType='Failed',
                                              msg=f'Port device: {device}: DB failure: Optic-Mode on port {port} = {opticMode}', forDetailLogs='')
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetOpticMode', msgType='Error',
                                          msg=f'Device: {device}  Port: {port} optic-mode: {opticMode}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class SetPortSpeed(APIView):
    def post(self, request):
        """
        Set the port's speed
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        port   = request.data.get('port', None)
        speed  = request.data.get('speed', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "device": device, "port": port, 'speed': speed}
            restApi = '/api/v1/portMgmt/setPortSpeed'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SetPortSpeed')
        else:        
            try:
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                if portMgmtData:
                    for index, portMgmtPort in enumerate(portMgmtData['portMgmt']):
                        if port != 'all' and portMgmtPort['port'] == port:
                            portMgmtPort.update({'speed': speed})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                            break
                        
                        if port == 'all':
                            portMgmtPort.update({'speed': speed})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                                                        
                portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                          queryFields={'domain': domain, 'name': device},
                                                          updateFields={'portMgmt': portMgmtData['portMgmt']})
                if portMgmtDBResult:   
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortSpeed', msgType='Success',
                                              msg=f'Port device: {device}: Port-Speed on port {port} = {speed}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortSpeed', msgType='Failed',
                                              msg=f'Port device: {device}: DB failure: Speed on port {port} = {speed}', forDetailLogs='')
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortSpeed', msgType='Error',
                                          msg=f'Device: {device}  Port: {port} Speed: {speed}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
    
class SetPortType(APIView):
    def post(self, request):
        """
        Set the port type: None|Access|Truck
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        port   = request.data.get('port', None)
        portType = request.data.get('portType', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "device": device, "port": port, 'portType': portType}
            restApi = '/api/v1/portMgmt/setPortType'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SetPortType')
        else:        
            try:
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                if portMgmtData:
                    for index, portMgmtPort in enumerate(portMgmtData['portMgmt']):
                        if portMgmtPort['port'] == port:
                            # Set port type and reset the vlan IDs
                            portMgmtPort.update({'portType': portType, 'vlanIDs': []})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                            break
                        
                portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                          queryFields={'domain': domain, 'name': device},
                                                          updateFields={'portMgmt': portMgmtData['portMgmt']})
                if portMgmtDBResult:   
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortType', msgType='Success',
                                              msg=f'Domain: {domain} Device: {device}: Port: {port}  PortType: {portType}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortType', msgType='Failed',
                                              msg=f'Domain: {domain} Device: {device}: Port: {port}  PortType: {portType}', forDetailLogs='')
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetPortType', msgType='Error',
                                          msg=f'Domain: {domain} Device: {device}: Port: {port}  PortType: {portType}:<br>{traceback.format_exc(None, errMsg)}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class SetVlanId(APIView):
    def post(self, request):
        """
        Set the port vlan ID
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        port   = request.data.get('port', None)
        vlanIdList = request.data.get('vlanIdList', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "device": device, "port": port, 'vlanIdList': vlanIdList}
            restApi = '/api/v1/portMgmt/setPortVlanIDs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='SetVlanId')
        else:        
            try:
                portMgmtData = DB.name.getOneDocument(collectionName='labInventory', fields={'domain': domain, 'name': device})
                if portMgmtData:
                    for index, portMgmtPort in enumerate(portMgmtData['portMgmt']):
                        if port != 'allPorts' and portMgmtPort['port'] == port:
                            portMgmtPort.update({'vlanIDs': vlanIdList})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                            break
                        
                        if port == 'allPorts':
                            portMgmtPort.update({'vlanIDs': vlanIdList, 'portType': 'access'})
                            portMgmtData['portMgmt'].pop(index)
                            portMgmtData['portMgmt'].insert(index, portMgmtPort)
                            
                portMgmtDBResult = DB.name.updateDocument(collectionName='labInventory',
                                                          queryFields={'domain': domain, 'name': device},
                                                          updateFields={'portMgmt': portMgmtData['portMgmt']})
                if portMgmtDBResult:   
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetVlanId', msgType='Success',
                                              msg=f'Domain: {domain} Device: {device}: Port: {port}  VlanIDs: {vlanIdList}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetVlanId', msgType='Failed',
                                              msg=f'Domain: {domain} Device: {device}: Port: {port}  VlanIDs: {vlanIdList}', forDetailLogs='')
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='SetVlanId', msgType='Error',
                                          msg=f'Domain: {domain} Device: {device}: Port: {port}  VlanIDs: {vlanIdList}:<br>{traceback.format_exc(None, errMsg)}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
        
class PortConnectionAddKey(APIView):
    def post(self, request):
        """
        Add additional field in Port-Connections
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain       = request.data.get('domain', None)
        device       = request.data.get('device', None)
        keyName      = request.data.get('keyName', None)
        keyValue     = request.data.get('keyValue', None)
        defaultValue = request.data.get('defaultValue', '')
        valueType    = request.data.get('valueType', None)
                
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain":     domain,
                      "device":     device,
                      "keyName":    keyName,
                      "keyValue":   keyValue,
                      "valueType":  valueType}
            
            restApi = '/api/v1/portMgmt/portConnection/addKey'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='PortConnectionAddKey')
        else:        
            try:
                keystackMiscData = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                                          fields={'name': LabInventoryVars.portMgmtAdditionalKeyNameInDB})
                                      
                # Add the key/value to all the ports
                for existingField in keystackMiscData['additionalKeys'].keys():
                    if bool(search(keyName, existingField, IGNORECASE)):
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='PortConnectionAddKey', msgType='Error',
                                                  msg=f'Key name already exists: {keyName}', forDetailLogs='')
                        
                        return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.success)

                if valueType == 'options':
                    if defaultValue == '':
                        defaultValue = keyValue.split(',')[0]
                        
                    keystackMiscData['additionalKeys'].update({keyName: {'type': valueType, 
                                                                         'options': keyValue.split(','), 
                                                                         'defaultValue': defaultValue}}) 

                if valueType in ['Boolean: True', 'Boolean: False']:
                    value = convertStrToBoolean(valueType.split(' ')[-1])
                    keystackMiscData['additionalKeys'].update({keyName: {'type': 'boolean', 
                                                                         'options': [True, False], 
                                                                         'defaultValue': value}})
                
                updateAdditionalKeyDB(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB, 
                                      keyValues= keystackMiscData['additionalKeys'])
                
                # Options
                if valueType == 'options':
                    # keyValue is a user defined list of options for dropdown menu
                    if defaultValue == '':
                        if ',' in keyValue:
                            defaultValue = keyValue.split(',')[0]
                        else:
                            defaultValue = keyValue
                            
                    # User defined list of options
                    if ',' in keyValue:
                        keyValue = keyValue.split(',')
                    else:
                        keyValue = [keyValue] 

                # Boolean
                if valueType in ['Boolean: True', 'Boolean: False']:
                    booleanValue = valueType.split(' ')[-1].strip()
                    value = convertStrToBoolean(booleanValue)
                                                                        
                portMgmtData = DB.name.getOneDocument(collectionName=Vars.labInventory, fields={'domain': domain, 'name': device})
                if portMgmtData:              
                    # Add the key/value to all the ports
                    for index, portMgmt in enumerate(portMgmtData['portMgmt']): 
                        if valueType == 'options':
                            portMgmt['additionalKeyValues'].update({keyName: {'value': defaultValue}})
                                                                            
                        elif valueType in ['Boolean: True', 'Boolean: False']:
                            portMgmt['additionalKeyValues'].update({keyName: {'value': value}})

                    result = DB.name.updateDocument(collectionName=Vars.labInventory,
                                                    queryFields={'domain': domain,
                                                                 'name':   device},
                                                    updateFields={'portMgmt': portMgmtData['portMgmt']},
                                                    appendToList=False)
                    if result:
                        SystemLogsAssistant().log(user=user, webPage=Vars.labInventory, action='PortConnectionAddKey', msgType='info',
                                                  msg=f'Added keyName:{keyName}',
                                                  forDetailLogs='')                                                                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='PortConnectionAddKey', msgType='Error',
                                          msg=f'Adding additional keys failed: {keyName}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class PortConnectionGetRemoveKeysTable(APIView):
    def post(self, request):
        """
        Get remove-fields table data
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        tableRowsHtml = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"device": device, "domain": domain}
            restApi = '/api/v1/portMgmt/portConnection/removeKeysTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='PortConnectionGetRemoveKeysTable')
            tableRowsHtml = response.json()['removeKeyTable'] 
                  
        else:        
            try:
                additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB)

                # {'asset1': {'defaultValue': 'b', 'options': ['a', 'b', 'c'], 'type': 'options'}}
                for additionalKey in additionalKeyObj.keys():
                    tableRowsHtml += f'<tr>'
                    tableRowsHtml += f'<td><input type="checkbox" name="portMgmtRemoveKeyCheckboxes" device="{device}" domain="{domain}" key="{additionalKey}"></td>'
                    tableRowsHtml += f'<td>{additionalKey}</td>'
                    tableRowsHtml += f'<td>{additionalKeyObj[additionalKey]["type"]}</td>'
                    tableRowsHtml += f'<td>{additionalKeyObj[additionalKey]["defaultValue"]}</td>'
                    
                    optionsDropdown = ''
                    if additionalKeyObj[additionalKey]["type"] == 'options':
                        optionsDropdown = '<div class="dropdown">'
                        optionsDropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' id='portMgmtFieldOptionsDropdown' role='button' aria-haspopup=true aria-expanded=false>View</a>" 
    
                        optionsDropdown += f'<div class="dropdown-menu dropdownSizeSmall editFieldOptionsDropdown">' 
                        optionsDropdown += '<center><span class="textBlack">Add / Remove Field Options</span></center><br>'
                        
                        optionsDropdown += f'<div class="input-group paddingLeft10px">'
                        optionsDropdown += f'<input type="text" class="form-control inputBoxWidth200px textBlack" id="portMgmt-{additionalKey}" name="addFieldOption">'
                        optionsDropdown += f'<button class="btn btn-primary portMgmtAddFieldOptionClass" type="button" field="{additionalKey}">Add Option 2</button><br><br>'
                        optionsDropdown += '</div><br>'
                        
                        # Remove Options
                        optionsDropdown += f'<a href="#" class="paddingLeft20px portMgmtRemoveFieldOptionsClass" fieldName="{additionalKey}" action="remove">Remove Options</a><br><br>'

                        optionsDropdown += f'<table class="marginLeft20px tableFixHead3" id="field-option-table-{additionalKey}">'
                        optionsDropdown += f'   <thead>'
                        optionsDropdown += f'      <tr>'
                        optionsDropdown += f'         <th></th>'
                        optionsDropdown += f'         <th>Option List</th>'            
                        optionsDropdown += '       </tr>'
                        optionsDropdown += '    </thead>'
                        optionsDropdown += '    <tbody>'
                        
                        # Fields to remove
                        options = ''
                        for option in sorted(additionalKeyObj[additionalKey]["options"]):
                            options += f'<tr>'
                            options += f'<td><input type="checkbox" name="portMgmtFieldOptionRemoveCheckbox" option="{option}" /></td>'
                            options += f'<td option="{option}">{option}</td>'
                            options += '</tr>'
        
                        optionsDropdown += f'{options}<tr></tr>'
                        optionsDropdown += f'</tbody></table>'
                        optionsDropdown += '</div></div>'
                                                
                    tableRowsHtml += f'<td>{optionsDropdown}</td>'
                    tableRowsHtml += f'</tr>'
    
                if tableRowsHtml != '':
                    # Add extra row to support the tableFixHead2 body with height:0 to 
                    # show a presentable table. Otherwise, if there are a few rows, the row 
                    # height will be large to fill the table size
                    tableRowsHtml += '<tr></tr>'
                                                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                tableRowsHtml = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.labInventory, action='PortConnectionGetRemoveKeysTable', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'removeKeyTable': tableRowsHtml, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
 
class PortConnectionRemoveKeys(APIView):
    def post(self, request):
        """
        Remove fields
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        # List format: [domain, device, field]
        # List [['Communal', 'mySwitch1', 'f1']]
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        keys = request.data.get('keys', None)
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain":domain, "device":device, "keys": keys}
            restApi = '/api/v1/portMgmt/portConnection/removeKeys'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='PortConnectionRemoveKeys')
        else:        
            try:
                portMgmtData = DB.name.getOneDocument(collectionName=Vars.labInventory, fields={'domain': domain, 'name': device})
                additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB)
                  
                # field: ['Communal', 'mySwitch1', 'f1']
                for key in keys:
                    key = key[2]
                    if portMgmtData:
                        if key in additionalKeyObj['additionalKeys']:
                            del additionalKeyObj['additionalKeys'][key]
                            
                        for portMgmt in portMgmtData['portMgmt']:
                            if key in portMgmt['additionalKeyValues'].keys():
                                del portMgmt['additionalKeyValues'][key]

                updateAdditionalKeyDB(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB,
                                      keyValues=additionalKeyObj['additionalKeys'])
                
                result = DB.name.updateDocument(collectionName=Vars.labInventory,
                                                queryFields={'domain': domain,
                                                             'name':   device},
                                                updateFields={'portMgmt': portMgmtData['portMgmt']})  
                
                if result:
                    SystemLogsAssistant().log(user=user, webPage=Vars.labInventory, action='PortConnectionGetRemoveKeys', msgType='Success',
                                              msg=f'Removed keys={keys}',
                                              forDetailLogs='') 
                                                                       
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.labInventory, action='PortConnectionGetRemoveKeys', msgType='Error',
                                          msg=f'Removing fields failed: {keys}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
 
 
class PortMgmtAddFieldOption(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='PortMgmtAddFieldOption', exclude=['engineer'])
    def post(self, request):
        """
        Port-Mgmt: Add additonal field option to the existing list
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        field = request.data.get('field', None)
        option = request.data.get('option', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'field': field, 'option': option}
            restApi = '/api/v1/portMgmt/portConnection/addFieldOption'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='PortMgmtAddFieldOption')
        else:        
            try:
                additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB)
                additionalKeyObj[field]['options'].append(option)
                updateAdditionalKeyDB(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB, keyValues=additionalKeyObj)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='PortMgmtAddFieldOptions', msgType='Success',
                                          msg=f'Added options: {option} to Field:{field}', forDetailLogs='') 
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='PortMgmtAddFieldOption', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg), forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
       
class PortMgmtRemoveFieldOptions(APIView):
    def post(self, request):
        """
        Remove additonal field options in an existing list
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        fieldName = request.data.get('fieldName', None)
        options   = request.data.get('options', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'fieldName': fieldName, 'options': options}
            restApi = '/api/v1/portMgmt/portConnection/removeFieldOptions'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='PortMgmtRemoveFieldOptions')
        else:        
            try:
                additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB)
                pprint(additionalKeyObj)
                for option in options:
                    index = additionalKeyObj[fieldName]['options'].index(option)
                    additionalKeyObj[fieldName]['options'].pop(index)

                updateAdditionalKeyDB(dbFieldsName=LabInventoryVars.portMgmtAdditionalKeyNameInDB, keyValues=additionalKeyObj)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='PortMgmtRemoveFieldOptions', msgType='Success',
                                          msg=f'Removed: {options}', forDetailLogs='') 
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='PortMgmtRemoveFieldOptions', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg), forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)