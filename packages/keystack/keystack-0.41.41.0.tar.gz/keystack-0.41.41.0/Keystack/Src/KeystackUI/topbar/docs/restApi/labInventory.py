import os, json, traceback
from re import search, match, I
from pathlib import Path
import csv
from copy import deepcopy
from pprint import pprint 


from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse, FileResponse, HttpResponse, HttpResponseRedirect

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from db import DB
from commonLib import logDebugMsg, netcat, getSortedPortList2, addToKeystackMisc, getKeystackMiscAddtionalFields, isLabInventoryAdditonalKeysDBExists, updateAdditionalKeyDB
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole, authenticateLogin, getUserRole
from accountMgr import AccountMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from domainMgr import DomainMgr
from execRestApi import ExecRestApi
from globalVars import GlobalVars, HtmlStatusCodes
from EnvMgmt import ManageEnv
from PortGroupMgmt import ManagePortGroup
from LabInventory import InventoryMgmt
from keystackUtilities import readYaml, readFile, removeFile, makeFolder, execSubprocess, execSubprocessInShellMode, convertStrToBoolean, convertNoneStringToNoneType, getDictIndexFromList


class Vars:
    """ 
    For logging the correct log topic.
    To avoid human typo error and be consistant
    """
    webpage = 'labInventory'
    keystackMisc = 'keystackMisc'
    additionalKeyNameInDB = 'labInventoryAdditionalKeys'
    portMgmtAdditionalKeyNameInDB = 'portMgmtAdditionalKeys'

    # Keys must be in the order of the the CSV headers
    # The GetInventory should get the fields from here to create the inventory table data
    deviceDefaultFields = {'domain': None, 'name': None, 'deviceType': None, 'vendor': None, 'model': None,
                           'serialNumber': None, 'location': None, 'ipAddress': None, 'ipPort': None,
                           'loginName': None, 'password': None, 'connectionProtocol': None, 'ports': [], 'notes': ''}
    
    initialDeviceTypes = ['Layer1 Switch',
                          'Layer2 Switch',
                          'Layer3 Router',
                          'Traffic Generator',
                          'Linux',
                          'Windows',
                          'Access Point',
                          'Storage',
                          'Jump Host',
                          'Terminal Server']

    # Removed: 'opticMode': None,
    defaultPortProperties = {'port': None,
                             'connectedToDevice': None,
                             'connectedToPort': None,
                             'portGroups': [],
                             'multiTenant': False,
                             'portType': None,
                             'vlanIDs': [],
                             'speed': 'None',
                             'reserved': 'available',
                             'additionalKeyValues': {}}
    
def getDeviceFieldsList():
    """ 
    Field names for users to export/import csv file.
    This list does not include other internal fields.
    
    deviceFieldNames = ['domain', 'name', 'deviceType', 'vendor', 'model', 'serialNumber', 'location',
                        'ipAddress', 'ipPort', 'loginName', 'password', 'connectionProtocol', 'ports']
    """
    fieldList = []
    for key in Vars.deviceDefaultFields.keys():
        fieldList.append(key)
        
    return fieldList


def addDeviceHelper(domain, user, deviceKeyValues):
    try:
        portList = []
        portsKeyList = []
        portPrefixVerifyConsistency = []
        isPortPrefixExists = False
        portErrorList = []
        
        if deviceKeyValues['ports']:
            for port in deviceKeyValues['ports'].split(','):
                if port in ['\n', '']:
                    continue

                # split(',') adds a leading white space. Remove leading white spaces.
                port = port.strip()
                
                # Ethernet2/1
                regexMatch = search('([a-zA-Z]+)?([0-9]+.+)', port)
                if regexMatch:
                    portPrefix = regexMatch.group(1)
                    portNumber = regexMatch.group(2)
                    portPrefixVerifyConsistency.append(portPrefix)
                    if portPrefix:
                        isPortPrefixExists = True
                    
                    # Is a range:  1/1-10
                    if '-' in portNumber:
                        startingPortRange = port.split('-')[0]
                        endingPortNumber   = int(portNumber.split('-')[1])

                        # 1/1-10
                        if '/' in startingPortRange:
                            regexMatch = search('(.*/)([0-9]+)', startingPortRange)
                            if regexMatch:
                                prefix = regexMatch.group(1)
                                startingPortNumber = int(regexMatch.group(2))

                                if endingPortNumber < startingPortNumber:
                                    portErrorList.append(port)
                                                
                                for portNumber in range(startingPortNumber, endingPortNumber+1):
                                    showPort = f'{prefix}{portNumber}'
                                    
                                    if showPort in portList:
                                        continue
                                    
                                    portList.append(f'{showPort}')                                                            
                                            
                        # 1.1-1.10       
                        if '.' in startingPortRange:
                            regexMatch = search('(.*\.)([0-9]+)', startingPortRange)
                            if regexMatch:
                                prefix = regexMatch.group(1)
                                startingPortNumber = int(regexMatch.group(2))

                                if endingPortNumber < startingPortNumber:
                                    portErrorList.append(port)
                                                                    
                                for portNumber in range(startingPortNumber, endingPortNumber+1):
                                    showPort = f'{prefix}{portNumber}'
                                    if showPort in portList:
                                        continue
                                    
                                    portList.append(f'{showPort}')          
                    else:
                        # Not in a range.  Must be individual ports.
                        portList.append(port.replace('\n', ''))
            
            deviceKeyValues['ports'] = portList
                    
        if portList:  
            # portType: None|access|trunk|hybrid
            for port in portList:
                tempProperties = deepcopy(Vars.defaultPortProperties)
                tempProperties.update({'port': port})
                portsKeyList.append(tempProperties)
          
            additionalPortKeys = {'portMgmt': portsKeyList}
            deviceKeyValues.update(additionalPortKeys)
            
        else:
            # addtionalHeaders: contains keys, values, types
            additionalPortKeys = {'ports': [], 'portMgmt': [], 'In-Used-By': []}
            
        deviceKeyValues.update(additionalPortKeys)
        
        # Add additional fields to the new device
        additionalFieldData = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                                     fields={'name': Vars.additionalKeyNameInDB},
                                                     includeFields=None)
        if 'inventoryAdditionalKeyValues' not in deviceKeyValues:
            deviceKeyValues.update({'inventoryAdditionalKeyValues': {}})
            

        for field, properties in additionalFieldData['additionalKeys'].items():
            # field: assets1 {'type': 'options', 'options': ['a', 'b', 'c'], 'defaultValue': 'b'}
            deviceKeyValues['inventoryAdditionalKeyValues'].update({field: {'type':properties['type'], 
                                                                            'value': properties['defaultValue'], 
                                                                            'options': properties['options']}})
                
        if isPortPrefixExists:
            def checkPortPrefixForConsistency(list):
                return len(set(list)) == 1
            
            result = checkPortPrefixForConsistency(portPrefixVerifyConsistency)
            if result is False:
                return "portPrefixInconsistency"
        
        if len(portErrorList) > 0:
            return "portRangeError"
            
        if deviceKeyValues:
            return deviceKeyValues
        else:
            return None
        
    except Exception as errMsg:
        status = "failed"
        errorMsg = str(errMsg)
        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDevice', msgType='Error',
                                  msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

def getInventoryTableHeader():
    """ 
    Use MongoDB keystackMisc to store lab inventory headers
    """        
    try:
        isLabInventoryAdditonalKeysDBExists(dbFieldsName=Vars.additionalKeyNameInDB)
        isLabInventoryAdditonalKeysDBExists(dbFieldsName=Vars.portMgmtAdditionalKeyNameInDB)
        
        additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=Vars.additionalKeyNameInDB) 
        
        headers = ''
        headers += f'<table class="tableFixHead2" id="inventoryTable">'
        headers += f'<thead>'
        headers += f'<tr>'
        headers += f'<th><input type="checkbox" id="selectAllDevicesForDelete"></th>'
        headers += f"<th>Status</th>"
        headers += f"<th>Name</th>"
        headers += f'<th class="zIndex10"><div id="insertDeviceTypeFilterOptions"></div></th>'
        headers += f'<th class="zIndex10"><div id="insertDeviceVendorFilterOptions"></div></th>'
        headers += f"<th>Model</th>"
        headers += f"<th>Serial #</th>"
        headers += f'<th class="zIndex10"><div id="insertDeviceLocationFilterOptions"></div></th>'
        headers += f"<th>IP Address</th>"
        headers += f"<th>IP Port</th>"
        headers += f"<th>Login</th>"
        headers += f"<th>Password</th>"
        headers += f"<th>ConnectProtocol</th>"
        headers += f"<th>Ports</th>"
        
        for additionalKey in additionalKeyObj.keys():
            addedKeySelectOptionsForAllRows = ''
            fieldType = additionalKeyObj[additionalKey]['type']
        
            addedKeySelectOptionsForAllRows = f'<select class="inventoryAddKeyForAllDevices mainTextColor" field="{additionalKey}" type="{fieldType}" style="background-color:black; border-color:black;">'
            addedKeySelectOptionsForAllRows += f'<option label="{additionalKey}" value></option>'
                                        
            for option in sorted(additionalKeyObj[additionalKey] ['options']):
                addedKeySelectOptionsForAllRows += f'<option value="{option}">{option}</option>'

            addedKeySelectOptionsForAllRows += '</select>'
            headers += f'<th>{addedKeySelectOptionsForAllRows}</th>'
        
        headers += '<th>Notes</th>'               
        headers += '</tr>'
        headers += '</thead>'

        return headers
    
    except Exception as errMsg:
        pass
          
                    
class GetDevices(APIView):
    def post(self, request):
        """
        Get inventory
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        userRole = getUserRole(request)
        
        domain                = request.data.get('domain', None)
        
        deviceTypeFilter      = request.data.get('deviceTypeFilter', 'All')
        deviceLocationFilter  = request.data.get('deviceLocationFilter', 'All')
        deviceVendorFilter    = request.data.get('deviceVendorFilter', 'All')

        getCurrentPageNumber  = request.data.get('getCurrentPageNumber', None)
        devicesPerPage        = request.data.get('devicesPerPage', None)
                
        # ['0:2'] <-- In a list
        # pageIndexRange: The document range to get from the collective pool of document data
        pageIndexRangeOriginal = request.data.get('pageIndexRange', None)
        
        # 0:2
        pageIndexRange = pageIndexRangeOriginal[0]
        
        indexStart     = int(pageIndexRange.split(':')[0])
        indexEnd       = int(pageIndexRange.split(':')[1])
        startingRange  = pageIndexRange.split(":")[0]
                                   
        html = ''
        portConnectionTableRowsJson = {}
        addPortsTableRows = []
        removePortsTableRows = []
        addPortsToPortGroupTableRows = []
        removePortsFromPortGroupTableRows = []
        connectPortsToLinkDeviceTableRows = []
        disconnectDeviceFromLinkDeviceTableRows = []
        addRemoveKeysTableRows = []
        refreshTableRows = []
        pageNumber = 1
        pagination = 1
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain":               domain, 
                      "deviceTypeFilter":     deviceTypeFilter,
                      "deviceLocationFilter": deviceLocationFilter,
                      "deviceVendorFilter":   deviceVendorFilter,
                      "pageIndexRange":       pageIndexRange,
                      "getCurrentPageNumber": getCurrentPageNumber,
                      "devicesPerPage":       devicesPerPage}
            
            restApi = '/api/v1/lab/inventory/getDevices'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDevices')

            html = response.json()['device']
            pagination = response.json()['pagination']
            pageNumber = response.json()['totalPages']
            portConnectionTableRowsJson = response.json()['portConnectionTableRowsJson']
            addPortsTableRows = response.json()['addPortsTableRows']
            removePortsTableRows = response.json()['removePortsTableRows']
            addPortsToPortGroupTableRows = response.json()['addPortsToPortGroupTableRows']
            removePortsFromPortGroupTableRows = response.json()['removePortsFromPortGroupTableRows']
            connectPortsToLinkDeviceTableRows = response.json()['connectPortsToLinkDeviceTableRows']
            disconnectDeviceFromLinkDeviceTableRows = response.json()['disconnectDeviceFromLinkDeviceTableRows']
            addRemoveKeysTableRows = response.json()['addRemoveKeysTableRows']
            refreshTableRows = response.json()['refreshTableRows']    
        else:
            from .portMgmt import getPortConnectionsTable
            pageNumber = 0
                    
            try:                
                fields = {'domain': domain}                
                if deviceTypeFilter != 'All':
                    fields.update({'deviceType': {'$in': deviceTypeFilter}})
                    
                if deviceLocationFilter != 'All':
                    fields.update({'location': {'$in': deviceLocationFilter}})

                if deviceVendorFilter != 'All':
                    fields.update({'vendor': {'$in': deviceVendorFilter}})

                additionalFields = getKeystackMiscAddtionalFields(dbFieldsName=Vars.additionalKeyNameInDB)
             
                """ 
                For the next 10 objects:     db.collection.find({_id: {$gt: object_id}}).limit(10)
                For the previous 10 objects: db.collection.find({_id: {$lte: object_id}}).sort({_id:-1}).limit(10)
            
                When you sort with _id, you will get the documents sorted (descending or ascending) by their creation timestamps.
                """
                data = DB.name.getDocuments(collectionName=Vars.webpage, fields=fields,
                                            includeFields={'_id':0}, sortBy=[('name', 1)], limit=None)
                countX = deepcopy(data) 
                count = len(list(countX)) 
                
                pagination = """<nav aria-label="">
                                    <ul class="pagination pagination-sm">
                                        <li class="page-item">
                                            <a class="page-link" id="previousPage" href="#" aria-label="Previous">
                                                <span aria-hidden="true">&laquo;</span>
                                            </a>
                                        </li>"""

                # devicesPerPage:5  getPageNumber:1  pageIndexRange:0:5  indexStart:0  indexEnd:5  startingRange:0
                for index, startingIndex in enumerate(range(0, count, devicesPerPage)):
                    # Creating page buttons with specific range of devices to show
                    pageNumber = index+1
                    endingIndex = startingIndex + devicesPerPage

                    if pageNumber > 1 and endingIndex == count:
                        # Don't create a 2nd page button if there's only 1 page of results to show
                        pagination += f'<li class="page-item"><a class="page-link" href="#" onclick="getInventory(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{count}">{pageNumber}</a></li>'
                    else:
                        # Note: if endingIndex != count:
                        # getPageNumber: Is to show the current page number
                        if int(pageNumber) == int(getCurrentPageNumber):
                            pagination += f'<li class="page-item active"><a class="page-link" href="#" onclick="getInventory(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</a></li>'
                        else:
                            pagination += f'<li class="page-item"><a class="page-link" href="#" onclick="getInventory(this)" getCurrentPageNumber="{pageNumber}" pageIndexRange="{startingIndex}:{endingIndex}">{pageNumber}</a></li>'
                        
                pagination += """<li class="page-item">
                                    <a class="page-link" id="nextPage" href="#" aria-label="Next">
                                        <span aria-hidden="true">&raquo;</span>
                                    </a>
                                    </li></ul></nav>"""
                        
                if data and count > 0:
                    # Each row represents a device
                    row = 1
                    
                    # For each device
                    indexStart = int(pageIndexRange.split(':')[0])
                    indexEnd   = int(pageIndexRange.split(':')[1])
                    
                    for index, device in enumerate(data[indexStart:indexEnd]):
                        portListDropdown = '<div class="dropdown">'
                        portListDropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' id='devicePortstDropdown' role='button' aria-haspopup=true aria-expanded=false>Ports</a>"                  
                        portListDropdown += f'<ul class="dropdown-menu remotePortDropdown" aria-labelledby="devicePortstDropdown">'
                        if device['ports']:
                            for port in device['ports']:
                                portListDropdown += f'<li class="paddingLeft10px textBlack">{port}</li>' 
                        portListDropdown += '</ul></div>'
                         
                        if device['ports'] is None or len(device['ports']) == 0:
                            portList = ''
                        else:
                            portList = portListDropdown
                        
                        # Device inventory row
                        html += '<tr>'   
                        html += f'<td><input type="checkbox" name="devices" domain="{domain}" deviceName="{device["name"]}"></td>'                  
                        
                        html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" ipAddress={device["ipAddress"]} ipPort={device["ipPort"]} deviceName="{device["name"]}" href="#"><div id="insertProfileStatus"</div></a></td>'

                        # In-Used-By
                        #html += f'<td class="paddingLeft5px">Yes</td>'
                                             
                        # Don't allow users to edit the device name.  The device name is all over the place.  Need time to work on this.                                                 
                        #html += f'<td class="paddingLeft5px"><a class="textBlack" id="selectedPortDeviceName" role="button" field="name" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["name"]}</a></td>'
                        html += f'<td class="paddingLeft5px">{device["name"]}</td>' 
                        
                        if userRole != 'engineer':                                           
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="deviceType" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["deviceType"]}</a></td>'
                        else:
                            html += f'<td class="paddingLeft5px">{device["deviceType"]}</td>'
                        
                        if userRole != 'engineer':      
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="vendor" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["vendor"]}</a></td>'
                        else:
                            html += f'<td>{device["vendor"]}</td>'
                        
                        if userRole != 'engineer':  
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="model" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["model"]}</a></td>'
                        else:
                            html += f'<td>{device["model"]}</td>'
                           
                        if userRole != 'engineer':  
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="serialNumber" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["serialNumber"]}</a></td>'
                        else:
                            html += f'<td>{device["serialNumber"]}</td>'
                            
                        if userRole != 'engineer':          
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="location" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["location"]}</a></td>'
                        else:
                            html += f'<td>{device["location"]}</td>'
                          
                        if userRole != 'engineer':  
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="ipAddress" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["ipAddress"]}</a></td>'
                        else:
                            html += f'<td>{device["ipAddress"]}</td>'
                       
                        if userRole != 'engineer':  
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="ipPort" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["ipPort"]}</a></td>'
                        else:
                            html += f'<td>{device["ipPort"]}</td>'
                          
                        if userRole != 'engineer':  
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="loginName" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["loginName"]}</a></td>'
                        else:
                            html += f'<td>{device["loginName"]}</td>'

                        # Password
                        html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="password" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)"><span class="fa-solid fa-eye"></span></a></td>'
                            
                        if userRole != 'engineer':  
                            html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="connectionProtocol" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{device["connectionProtocol"]}</a></td>'
                        else:
                            html += f'<td>{device["connectionProtocol"]}</td>'
    
                        # Each device uses accordion to expand a port-connection table
                        # Each row represents one device
                        addPortsId                      = f'addPortsId-{row}'
                        removePortsId                   = f'removePortsId-{row}'
                        portConnectionsTableId          = f'portConnectionsTableId-{row}'
                        addPortsToPortGroupId           = f'addPortsToPortGroupId-{row}'
                        removePortsFromPortGroupId      = f'removePortsFromPortGroupId-{row}'
                        connectPortsToLinkDeviceId      = f'connectPortsToLinkDeviceId-{row}'
                        disconnectPortsFromLinkDeviceId = f'disconnectPortsFromLinkDeviceId-{row}'
                        addRemoveKeysId                 = f'addRemoveKeysId-{row}'
                        refreshTableId                  = f'refreshTableId-{row}'
                        
                        # In JS, get the hidden table ID corresponding to the device name
                        portConnectionTableRowsJson[device['name']] = f'#{portConnectionsTableId}'
                        addPortsTableRows.append(addPortsId)
                        removePortsTableRows.append(removePortsId)
                        addPortsToPortGroupTableRows.append(addPortsToPortGroupId)
                        removePortsFromPortGroupTableRows.append(removePortsFromPortGroupId)
                        connectPortsToLinkDeviceTableRows.append(connectPortsToLinkDeviceId)
                        disconnectDeviceFromLinkDeviceTableRows.append(disconnectPortsFromLinkDeviceId)
                        addRemoveKeysTableRows.append(addRemoveKeysId)
                        refreshTableRows.append(refreshTableId)
                                                                            
                        # Accordion sample: https://wpdatatables.com/table-with-collapsible-rows/
                        html += f'<td class="accordion-toggle marginTop5px flexRowInlineBlockCenter" data-toggle="collapse" data-target="#portConnections-{row}">'
                        html += f'<button class="btn btn-default btn-xs" onclick="unhidePortConnectionsRow(this)"'
                        html +=        f'addPortsId="#{addPortsId}"'
                        html +=        f'removePortsId="#{removePortsId}"'
                        html +=        f'addPortsToPortGroupId="#{addPortsToPortGroupId}"'
                        html +=        f'removePortsFromPortGroupId="#{removePortsFromPortGroupId}"'
                        html +=        f'connectPortsToLinkDeviceId="#{connectPortsToLinkDeviceId}"'
                        html +=        f'disconnectPortsFromLinkDeviceId="#{disconnectPortsFromLinkDeviceId}'
                        html +=        f'insertPortConnectsTableId="#{portConnectionsTableId}"'
                        html +=        f'addRemoveKeysId="#{addRemoveKeysId}"'
                        html +=        f'refreshTableId="#{refreshTableId}"'
                        html +=        f'row="{row}" device="{device["name"]}">'
                        
                        # Down-arrow icon to expand the port's table
                        html +=        f'<i class="fa-solid fa-angles-down textBlack"></i></button>&ensp;'
                        
                        # Show a list of ports in a dropdown 
                        if len(portList) > 0:
                            html += f'<a class="textBlack" role="button" field="ports" deviceName="{device["name"]}" href="#">{portList}</a></td>'
                        else:
                            html += f'<a class="textBlack" role="button" field="ports" deviceName="{device["name"]}" href="#">None </a></td>'
                            
                        # Additional field / values
                        '''
                        additionalField: assets1
                        values:  {'defaultValue': False, 'options': [True, False],   'type': 'boolean'}
                                 {'defaultValue': 'b',   'options': ['a', 'b', 'c'], 'type': 'options'}
                        '''
                        if len(additionalFields) > 0:
                            for field in additionalFields.keys():
                                if field in device['inventoryAdditionalKeyValues']:
                                    currentValue = device['inventoryAdditionalKeyValues'][field]['value']
                                else:
                                    currentValue = None
                                    
                                additionalFieldValueDropdown = '<div class="dropdown">'
                                additionalFieldValueDropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' id='additionalFieldValueDropdown' role='button' aria-haspopup=true aria-expanded=false>{currentValue}</a>"  

                                additionalFieldValueDropdown += f'<ul class="dropdown-menu {field}" aria-labelledby="additionalFieldValueDropdown">'
                                
                                if additionalFields[field]['type'] == 'options':
                                    if field in device['inventoryAdditionalKeyValues']:
                                        for option in sorted(additionalFields[field]['options']):
                                            additionalFieldValueDropdown += f'<li class="paddingLeft10px textBlack" device="{device["name"]}" domain="{domain}" field="{field}" value="{option}">{option}</li>'                                     

                                if additionalFields[field]['type'] == 'boolean':
                                    if field in device['inventoryAdditionalKeyValues']:
                                        if convertStrToBoolean(device['inventoryAdditionalKeyValues'][field]['value']) is True:
                                            additionalFieldValueDropdown += f'<li class="paddingLeft10px textBlack" device="{device["name"]}" domain="{domain}" field="{field}" value="False">False</li>' 
                                        else:
                                            additionalFieldValueDropdown += f'<li class="paddingLeft10px textBlack" device="{device["name"]}" domain="{domain}" field="{field}" value="True">True</li>'  
                                                                                                     
                                additionalFieldValueDropdown += '</ul></div>'
                                html += f'<td>{additionalFieldValueDropdown}</td>'                            
                        
                        # Notes  
                        if device['notes'] == 'None':
                            currentValue = 'Add'
                            currentNotes = ''
                        else:
                            currentValue = 'View'
                            currentNotes = device['notes']
                            
                        html += f'<td class="paddingLeft5px"><a class="textBlack" role="button" field="notes" currentNotes="{currentNotes}" deviceName="{device["name"]}" href="#" onclick="editDeviceField(this)">{currentValue}</a></td>'
                                                                                                                                          
                        html += '</tr>'
                        
                        # Add collapsed row that shows port-connections                        
                        html += '<tr class="hideFromUser">'
                        html += '<td></td><td colspan="12" class="marginLeft5px">'
                        html +=    f'<div class="accordian-body collapse" id="portConnections-{row}">'

                        # Add port-connection links
                        html += f"""<div class="flexRowInlineBlockLeft marginBottom10px">
                                        <div><a id="{addPortsId}" domain="{domain}" deviceName="{device["name"]}" href="#" class="textBlack noTextDecoration paddingTop10px addPortsClass">Add-Ports</a></div>&emsp;&emsp;
                        
                                        <div><a id="{removePortsId}" href="#" class="textBlack noTextDecoration paddingTop10px removePortsClass" domain="{domain}" device="{device["name"]}">Remove-Ports</a></div>&emsp;&emsp;
                                        
                                        <div id={addPortsToPortGroupId}><a href="#" class="textBlack noTextDecoration paddingTop10px">Add-Ports-To-Port-Group</a></div>&emsp;&emsp;
                                        
                                        <div id={removePortsFromPortGroupId}><a href="#" class="textBlack noTextDecoration paddingTop10px">Remove-Ports-From-Port-Group</a></div>&emsp;&emsp;
                                        
                                        <div id={connectPortsToLinkDeviceId}><a href="#" class="textBlack noTextDecoration paddingTop10px">Connect-Ports-To-Device</a></div>&emsp;&emsp;
                                        
                                        <div id={disconnectPortsFromLinkDeviceId}><a href="#" class="textBlack noTextDecoration paddingTop10px">Disconnect-Device</a></div>&emsp;&emsp;
                                        
                                        <div id={addRemoveKeysId}><a href="#" domain="{domain}" device="{device["name"]}" class="textBlack noTextDecoration paddingTop10px" data-bs-toggle="modal" data-bs-target="#addRemoveKeysPortMgmtModal">Add / Remove Fields</a></div>&emsp;&emsp;
                                        
                                        <div id={refreshTableId}><a href="#" device="{device["name"]}" class="textBlack noTextDecoration paddingTop10px">Refresh-Table</a></div>&emsp;&emsp;
                                    </div>
                                """

                        html +=        f'<div id="{portConnectionsTableId}"></div>'
                        html +=    '</div>'
                        html += '</td>'
                        html += '</tr>'

                        row += 2
 
                html += f'<tr></tr>'
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDevices', msgType='Error',
                                          msg=errorMsg, forDetailLogs=f"{traceback.format_exc(None, errMsg).replace('<td>', '[td]')}")
       
            inventoryTable = getInventoryTableHeader() 
            inventoryTable += f'<tbody>{html}</tbody>'
            inventoryTable += '</table>'
                
        return Response(data={'devices': html,
                              'pagination': pagination,
                              'totalPages': pageNumber,
                              'portConnectionTableRowsJson': portConnectionTableRowsJson,
                              'addPortsId': addPortsTableRows,
                              'removePortsId': removePortsTableRows,
                              'addPortsToPortGroupTableRows': addPortsToPortGroupTableRows,
                              'removePortsFromPortGroupTableRows': removePortsFromPortGroupTableRows,
                              'connectPortsToLinkDeviceTableRows': connectPortsToLinkDeviceTableRows,
                              'disconnectDeviceFromLinkDeviceTableRows': disconnectDeviceFromLinkDeviceTableRows,
                              'addRemoveKeysTableRows': addRemoveKeysTableRows,
                              'refreshTableRows': refreshTableRows,
                              'inventoryTable': inventoryTable,
                              'additionalFieldNames': list(additionalFields.keys()),
                              'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
                                                       
class GetInventoryDomains(APIView):
    def post(self,request):
        """
        Sidebar menu called by base.html/base.js
        Lab inventory
        """
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/domains'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetInventoryDomains')
            html = response.json()['inventoryDomains']       
        else:        
            try:
                userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
                for domain in userAllowedDomains:
                    html += f'<a class="collapse-item pl-3 textBlack" href="/lab/inventory/?domain={domain}"><i class="fa-regular fa-folder pr-3"></i>{domain}</a>'
                                                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetInventoryDomains', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'inventoryDomains': html, 'status':status, 'errorMsg': errorMsg}, status=statusCode)
    

class CreateInitialDeviceFilters(APIView):
    def post(self, request):
        """
        When the inventory page is loaded, it will check for initial device filters existance.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/createInitialDeviceFilterss'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='CreateInitialDeviceFilters')
        else:        
            try:
                for filter in [('deviceTypes', Vars.initialDeviceTypes), ('deviceLocations', []), ('deviceVendors', [])]:
                    filterName = filter[0]
                    initialFilters = filter[1]
                    data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': filterName}, includeFields=None)
                    if data is None:
                        response = DB.name.insertOne(collectionName=Vars.keystackMisc, data={'name': filterName, filterName: initialFilters})
                        if response.acknowledged is False:
                            SystemLogsAssistant().log(user=user, webPage=Vars.keystackMisc, action='CreateInitialDeviceFilters', msgType='Failed',
                                                    msg=f'Creating initial filters failed for: filterName:{filterName} filters:{initialFilters}',
                                                    forDetailLogs='')                                  
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.keystackMisc, action='CreateInitialDeviceFilters', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class GetDeviceTypeFilterOptions(APIView):
    def post(self, request):
        """
        Get a dropdown list in html of all the device types for filtering
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        deviceTypesDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceTypeFilterOptions'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDeviceTypeFilterOptions')
            deviceTypesDropdown = response.json()['deviceTypesDropdown']
              
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceTypes'}, includeFields=None)
                if data:
                    deviceTypes = sorted(data['deviceTypes'])
                    deviceTypes.insert(0, 'None')
                    deviceTypes.insert(1, 'All')
                    
                    deviceTypesDropdown = "<a class='dropdown-toggle deviceTypeHoverColor mainTextColor' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded='false'>Device Types&ensp;&ensp;</a>"     
                    deviceTypesDropdown += '<div class="dropdown">'
                                     
                    deviceTypesDropdown += f'<ul id="selectDeviceLocationFilter" class="dropdown-menu" aria-labelledby="" style="max-height:200px; overflow-y:auto;">'                     
                    for deviceType in deviceTypes:
                        if deviceType == 'All':
                            deviceTypesDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" id="selectedAllDeviceTypes" name="selectedAllDeviceTypes">&ensp;&ensp;All</li>'
                        else:
                            deviceTypesDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox"  name="selectedDeviceTypes" deviceTypeSelected="{deviceType}">&ensp;&ensp;{deviceType}</li>'
                    
                    deviceTypesDropdown += '<br>'
                    deviceTypesDropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectDeviceTypeFilterButton" type="submit" class="btn btn-sm btn-outline-primary">Go</button></li>'
                    deviceTypesDropdown += '</ul></div></div>'
                    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                deviceTypesDropdown = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceTypeFilterOptions', msgType='Error',
                                          msg=f'',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceTypesDropdown': deviceTypesDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class GetDeviceTypeOptions(APIView):
    def post(self, request):
        """ 
        For add-device.  Dropdown options of all the recorded types
        for user to select
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        deviceTypes = []
        deviceTypesDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceTypeOptions'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetDeviceTypeOptions')
            deviceTypesDropdown = response.json()['deviceTypes']  
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                              fields={'name': 'deviceTypes'},
                                              includeFields=None)
                
                if data:
                    deviceTypes = sorted(data['deviceTypes'])
                    deviceTypesDropdown = '<div class="dropdown">'
                    deviceTypesDropdown += "<a class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Select Device Type&ensp;&ensp;</a>"
                    deviceTypesDropdown += f'<ul id="selectDeviceTypeOptions" class="dropdown-menu" aria-labelledby="">'
                    
                    for deviceType in sorted(deviceTypes):
                        deviceTypesDropdown += f'<li class="mainFontSize textBlack paddingLeft20px">&ensp;&ensp;{deviceType}</li>'
                    
                    deviceTypesDropdown += '</ul></div>'
                                        
            except Exception as errMsg:
                deviceTypesDropdown = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceTypeOptions', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceTypes': deviceTypesDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetDeviceTypeDropdownForEditing(APIView):
    #@verifyUserRole(webPage=Vars.webpage, action='GetDeviceTypeDropdownForEditing', exclude=['engineer'])
    def post(self, request):
        """
        Get HTML dropdown menu for editing device type
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceTypeDropdownForEditing'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetDeviceTypeDropdownForEditing')
            html = response.json()['deviceTypeDropdownForEditing']
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceTypes'}, includeFields=None)
                deviceTypes = sorted(data['deviceTypes'])
                deviceTypes.insert(0, 'None')
                    
                html = '<div class="dropdown">'
                html += '<a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>Select a Device type</a>'                
                html += '<ul class="dropdown-menu dropdownMedium dropdownFontSize editDeviceTypeSelection hide" id="selectDeviceTypeForEdit">'
                
                for deviceType in deviceTypes:
                    html += f'<li class="dropdown-item">{deviceType}</li>'

                html += '</ul></div>'
               
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceTypeDropdownForEditing', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceTypeDropdownForEditing': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class AddDeviceType(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddDeviceType', exclude=['engineer'])
    def post(self, request):
        """ 
        For add-device.  Add a new device type to DB
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        deviceType = request.data.get('deviceType', 'None')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/addDeviceType'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='AddDeviceType')
        else:        
            try:
                if deviceType:
                    addToKeystackMisc(key='deviceTypes', value=deviceType)
                else:
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDeviceType', msgType='Error',
                                              msg='Location name cannot be None',
                                              forDetailLogs='')                                      
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDeviceType', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class RemoveDeviceType(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemoveDeviceType', exclude=['engineer'])
    def post(self, request):
        """ 
        Remove one or more device-types
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        deviceTypes = request.data.get('deviceTypes', 'None')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/removeDeviceType'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='RemoveDeviceType')
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceTypes'}, includeFields=None)
                if data:
                    for deviceType in deviceTypes:
                        if deviceType in  data['deviceTypes']:
                            index = data['deviceTypes'].index(deviceType)
                            data['deviceTypes'].pop(index)

                    result = DB.name.updateDocument(collectionName=Vars.keystackMisc,
                                                    queryFields={'name': 'deviceTypes'},
                                                    updateFields={'deviceTypes': data['deviceTypes']})

                    if result is False:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDeviceType', msgType='Failed',
                                                  msg=f'Failed to remove: {deviceTypes}', forDetailLogs='')
                                                                    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDeviceType', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
     
class GetDeviceTypeFilterMgmtTable(APIView):
    def post(self, request):
        """ 
        Get device-types table for removal
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceTypeFilterMgmtTable'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDeviceTypeFilterMgmtTable')
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceTypes'}, includeFields=None)
                
                html += """<table class="tableMessages table-bordered">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="selectAllDeviceTypesForDelete"></th>
                            <th>Device Types</th>
                        </tr>        
                    </thead>

                    <tbody>"""
                    
                if data:
                    for deviceType in sorted(data['deviceTypes']):
                        if deviceType in Vars.initialDeviceTypes:
                            continue
                        
                        html += '<tr>'
                        html += f'<td><center><input type="checkbox" name="removeDeviceTypeCheckbox" deviceType="{deviceType}"></center></td>'
                        html += f'<td>{deviceType}</td>'
                        html += '</tr>'               
                    
                html += "</tbody></table>"
                                                 
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceTypeFilterMgmtTable', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'table': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)  
    
      
class GetDeviceLocationFilterOptions(APIView):
    def post(self, request):
        """ 
        Filter dropdown options list of all the recorded locations
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        deviceLocationsDropdown = ''
        deviceLocations = []
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceLocationFilterOptions'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetDeviceLocationFilterOptions')
            deviceLocationsDropdown = response.json()['deviceLocations']  
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                              fields={'name': 'deviceLocations'},
                                              includeFields=None)
                
                if data:
                    deviceLocations = sorted(data['deviceLocations'])
                    deviceLocations.insert(0, 'None')
                    deviceLocations.insert(1, 'All')  

                    deviceLocationsDropdown = "<a class='dropdown-toggle deviceTypeHoverColor mainTextColor' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Location&ensp;&ensp;</a>"
                    deviceLocationsDropdown += '<div class="dropdown">'
                    deviceLocationsDropdown += f'<ul id="selectDeviceLocationFilter" class="dropdown-menu" aria-labelledby="">'
                    
                    for deviceLocation in deviceLocations:
                        if deviceLocation == 'All':
                            deviceLocationsDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" id="selectedAllDeviceLocations" name="selectedAllDeviceLocations">&ensp;&ensp;All</li>'
                        else:
                            deviceLocationsDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox"  name="selectedDeviceLocations" deviceLocationSelected="{deviceLocation}">&ensp;&ensp;{deviceLocation}</li>'
                    
                    deviceLocationsDropdown += '<br>'
                    deviceLocationsDropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectDeviceLocationFilterButton" type="submit" class="btn btn-sm btn-outline-primary">Go</button></li>'
                    deviceLocationsDropdown += '</ul></div>'
                                        
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                deviceLocationsDropdown = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceLocationFilterOptions', msgType='Error',
                                          msg='',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceLocations': deviceLocationsDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
 
class GetDeviceLocationOptions(APIView):
    def post(self, request):
        """ 
        For add-device.  Dropdown options of all the recorded locations
        for user to select
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        deviceLocations = []
        deviceLocationsDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceLocationOptions'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetDeviceLocationOptions')
            deviceLocationsDropdown = response.json()['deviceLocations']  
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                              fields={'name': 'deviceLocations'},
                                              includeFields=None)
                
                if data:
                    deviceLocations = sorted(data['deviceLocations'])
                    deviceLocationsDropdown = '<div class="dropdown">'
                    deviceLocationsDropdown += "<a class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Select Device Location&ensp;&ensp;</a>"
                    deviceLocationsDropdown += f'<ul id="selectDeviceLocationOptions" class="dropdown-menu" aria-labelledby="">'
                    
                    for deviceLocation in sorted(deviceLocations):
                        deviceLocationsDropdown += f'<li class="mainFontSize textBlack paddingLeft20px">&ensp;&ensp;{deviceLocation}</li>'
                    
                    deviceLocationsDropdown += '</ul></div>'
                                        
            except Exception as errMsg:
                deviceLocationsDropdown = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceLocationOptions', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceLocations': deviceLocationsDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetDeviceLocationDropdownForEditing(APIView):
    #@verifyUserRole(webPage=Vars.webpage, action='GetDeviceLocationDropdownForEditing', exclude=['engineer'])
    def post(self, request):
        """
        Get HTML dropdown menu for editing device location
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceLocationDropdownForEditing'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDeviceLocationDropdownForEditing')
            html = response.json()['deviceLocationDropdownForEditing']
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceLocations'}, includeFields=None)
                deviceLocations = sorted(data['deviceLocations'])
                deviceLocations.insert(0, 'None')
                
                html = '<div class="dropdown">'
                html += '<a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>Select a Location</a>'                
                html += '<ul class="dropdown-menu dropdownMedium dropdownFontSize editDeviceLocationSelection hide" id="selectDeviceLocationForEdit">'
                
                for deviceLocation in deviceLocations:
                    html += f'<li class="dropdown-item">{deviceLocation}</li>'

                html += '</ul></div>'
               
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceLocationDropdownForEditing', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceLocationDropdownForEditing': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetDeviceLocationFilterMgmtTable(APIView):
    def post(self, request):
        """ 
        Get device-types table for removal
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceLocationFilterMgmtTable'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDeviceLocationFilterMgmtTable')
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceLocations'}, includeFields=None)

                html += """<table class="tableMessages table-bordered">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="selectAllDeviceLocationsForDelete"></th>
                            <th>Device Locations</th>
                        </tr>        
                    </thead>

                    <tbody>"""
                    
                if data:
                    for deviceLocation in sorted(data['deviceLocations']):
                        html += '<tr>'
                        html += f'<td><center><input type="checkbox" name="removeDeviceLocationCheckbox" deviceLocation="{deviceLocation}"></center></td>'
                        html += f'<td>{deviceLocation}</td>'
                        html += '</tr>'               
                    
                html += "</tbody></table>"
                                                 
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceLocationFilterMgmtTable', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'table': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)  
    
    
        
class AddDeviceLocation(APIView):
    def post(self, request):
        """ 
        In add-device page.  Add a new device location to DB.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        location = request.data.get('location', 'None')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/addDeviceLocation'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='AddDeviceLocation')
        else:        
            try:
                if location:
                    addToKeystackMisc(key='deviceLocations', value=location)
                else:
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDeviceLocation', msgType='Error',
                                              msg='Location name cannot be None',
                                              forDetailLogs='')                                      
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDeviceLocation', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
 

class RemoveDeviceLocation(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemoveDeviceLocation', exclude=['engineer'])
    def post(self, request):
        """ 
        Remove one or more device-types
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        locations = request.data.get('deviceLocations', 'None')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/removeDeviceLocation'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='RemoveDeviceLocation')
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceLocations'}, includeFields=None)
                if data:
                    for location in locations:
                        if location in data['deviceLocations']:
                            index = data['deviceLocations'].index(location)
                            data['deviceLocations'].pop(index)

                    result = DB.name.updateDocument(collectionName=Vars.keystackMisc,
                                                    queryFields={'name': 'deviceLocations'},
                                                    updateFields={'deviceLocations': data['deviceLocations']})

                    if result is False:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDeviceLocation', msgType='Failed',
                                                  msg=f'Failed to remove: {locations}', forDetailLogs='')
                                                                    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDeviceLocation', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
            
class GetDeviceVendorFilterOptions(APIView):
    def post(self, request):
        """ 
        Filter dropdown options list of all the recorded vendors
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        deviceVendorsDropdown = ''
        deviceVendors = []
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceVendorFilterOptions'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetDeviceVendorFilterOptions')
            deviceVendorsDropdown = response.json()['deviceVendors']  
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                              fields={'name': 'deviceVendors'},
                                              includeFields=None)
                
                if data:
                    deviceVendors = sorted(data['deviceVendors'])
                    deviceVendors.insert(0, 'None')
                    deviceVendors.insert(1, 'All')  
                    
                    deviceVendorsDropdown = "<a class='dropdown-toggle deviceTypeHoverColor mainTextColor' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Vendor&ensp;&ensp;</a>"                                        
                    deviceVendorsDropdown += '<div class="dropdown">'
                    deviceVendorsDropdown += f'<ul id="selectDeviceVendorFilter" class="dropdown-menu" aria-labelledby="">'
                    
                    for deviceVendor in deviceVendors:
                        if deviceVendor == 'All':
                            deviceVendorsDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox" id="selectedAllDeviceVendors" name="selectedAllDeviceVendors">&ensp;&ensp;All</li>'
                        else:
                            deviceVendorsDropdown += f'<li class="mainFontSize textBlack paddingLeft20px"><input type="checkbox"  name="selectedDeviceVendors" deviceVendorSelected="{deviceVendor}">&ensp;&ensp;{deviceVendor}</li>'
                    
                    deviceVendorsDropdown += '<br>'
                    deviceVendorsDropdown += '<li class="mainFontSize textBlack paddingLeft20px"><button id="selectDeviceVendorFilterButton" type="submit" class="btn btn-sm btn-outline-primary">Go</button></li>'
                    deviceVendorsDropdown += '</ul></div>'
                                        
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                deviceVendorsDropdown = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceVendorFilterOptions', msgType='Error',
                                          msg='',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceVendors': deviceVendorsDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
 
class GetDeviceVendorOptions(APIView):
    def post(self, request):
        """ 
        Dropdown options of all the recorded vendors
        for user to select
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        deviceVendors = []
        deviceVendorsDropdown = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceVendorOptions'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDeviceVendorOptions')
            deviceVendorsDropdown = response.json()['deviceVendors']  
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                              fields={'name': 'deviceVendors'},
                                              includeFields=None)
                
                if data:
                    deviceVendors = sorted(data['deviceVendors'])
                    deviceVendorsDropdown = '<div class="dropdown">'
                    deviceVendorsDropdown += "<a class='dropdown-toggle' data-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Select Device Vendor&ensp;&ensp;</a>"
                    deviceVendorsDropdown += f'<ul id="selectDeviceVendorOptions" class="dropdown-menu" aria-labelledby="">'
                    
                    for deviceVendor in sorted(deviceVendors):
                        deviceVendorsDropdown += f'<li class="mainFontSize textBlack paddingLeft20px">&ensp;&ensp;{deviceVendor}</li>'
                    
                    deviceVendorsDropdown += '</ul></div>'
                                        
            except Exception as errMsg:
                deviceVendorsDropdown = ''
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceVendorOptions', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceVendors': deviceVendorsDropdown, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetDeviceVendorDropdownForEditing(APIView):
    def post(self, request):
        """
        Get HTML dropdown menu for editing device vendor
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceVendorDropdownForEditing'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDeviceVendorDropdownForEditing')
            html = response.json()['deviceVendorDropdownForEditing']
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceVendors'}, includeFields=None)
                deviceVendors = sorted(data['deviceVendors'])
                deviceVendors.insert(0, 'None')
                
                html = '<div class="dropdown">'
                html += '<a class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup=true aria-expanded=false>Select a Vendor</a>'                
                html += '<ul class="dropdown-menu dropdownMedium dropdownFontSize editDeviceVendorSelection hide" id="selectDeviceVendorForEdit">'
                
                for deviceVendor in deviceVendors:
                    html += f'<li class="dropdown-item">{deviceVendor}</li>'

                html += '</ul></div>'
               
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceVendorDropdownForEditing', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'deviceVendorDropdownForEditing': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetDeviceVendorFilterMgmtTable(APIView):
    def post(self, request):
        """ 
        Get device-types table for removal
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceVendorFilterMgmtTable'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDeviceVendorFilterMgmtTable')
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceVendors'}, includeFields=None)

                html += """<table class="tableMessages table-bordered">
                    <thead>
                        <tr>
                            <th><input type="checkbox" id="selectAllDeviceVendorsForDelete"></th>
                            <th>Device Vendors</th>
                        </tr>        
                    </thead>

                    <tbody>"""
                    
                if data:
                    for deviceVendor in sorted(data['deviceVendors']):
                        if deviceVendor == 'None':
                            continue
                        
                        html += '<tr>'
                        html += f'<td><center><input type="checkbox" name="removeDeviceVendorCheckbox" deviceVendor="{deviceVendor}"></center></td>'
                        html += f'<td>{deviceVendor}</td>'
                        html += '</tr>'               
                    
                html += "</tbody></table>"
                                                 
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                html = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceVendorFilterMgmtTable', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'table': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)  
    
    
        
class AddDeviceVendor(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddDeviceVendor', exclude=['engineer'])
    def post(self, request):
        """ 
        Add a new device vendor to DB.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        vendor = request.data.get('vendor', 'None')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/addDeviceVendor'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='AddDeviceVendor')
        else:        
            try:
                if vendor:
                    addToKeystackMisc(key='deviceVendors', value=vendor)
                else:
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDeviceVendor', msgType='Error',
                                              msg='Vendor name cannot be None',
                                              forDetailLogs='')                                      
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDeviceVendor', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class RemoveDeviceVendor(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemoveDeviceVendor', exclude=['engineer'])
    def post(self, request):
        """ 
        Remove one or more device-vendors
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        vendors = request.data.get('deviceVendors', 'None')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/removeDeviceVendor'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='RemoveDeviceVendor')
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': 'deviceVendors'}, includeFields=None)
                if data:
                    for vendor in vendors:
                        if vendor == 'None':
                            continue
                        
                        if vendor in data['deviceVendors']:
                            index = data['deviceVendors'].index(vendor)
                            data['deviceVendors'].pop(index)

                    result = DB.name.updateDocument(collectionName=Vars.keystackMisc,
                                                    queryFields={'name': 'deviceVendors'},
                                                    updateFields={'deviceVendors': data['deviceVendors']})

                    if result is False:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDeviceVendor', msgType='Failed',
                                                  msg=f'Failed to remove: {vendor}', forDetailLogs='')
                                                                    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveDeviceVendor', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg),
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
        

class AddDevice(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddDevice', exclude=['engineer'])
    def post(self, request):
        """
        Add a device in Lab Inventory
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        deviceKeyValues = request.data.get('deviceKeyValues', 'None')
        domain = deviceKeyValues.get('domain', None)

        """
        deviceKeyValues: From portMgmt.js:addDevice()
        let deviceKeyValues = {domain:             document.querySelector("#inventoryAttributes").getAttribute("domain"),
                               name:               deviceName.trim(),
                               description:        document.querySelector('input[id=newDeviceDescription]').value,
                               deviceType:         deviceType,
                               vendor:             commons.capitalizeWords(deviceVendor),
                               model:              document.querySelector('input[id=newDeviceModel]').value,
                               serialNumber:       document.querySelector('input[id=newDeviceSerialNumber]').value,
                               location:           commons.capitalizeWords(deviceLocation),
                               ipAddress:          document.querySelector('input[id=newDeviceIpAddress]').value,
                               ipPort:             document.querySelector('input[id=newDeviceIpPort]').value,
                               loginName:          document.querySelector('input[id=newDeviceLoginName]').value,
                               password:           document.querySelector('input[id=newDevicePassword]').value,
                               connectionProtocol: document.querySelector('input[name=connectProtocol]:checked').value,
                               ports:              ports,
                              }
        """ 
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'deviceKeyValues': deviceKeyValues}
            restApi = '/api/v1/lab/inventory/addDevice'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='AddDevice')
        else:   
            try:
                deviceName = deviceKeyValues['name']
                ports = deviceKeyValues['ports']
                
                isPortDeviceExists = DB.name.isDocumentExists(collectionName=Vars.webpage,
                                                              keyValue={'domain': domain, 'name': deviceKeyValues['name']},
                                                              regex=True)
                if isPortDeviceExists:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDevice', msgType='Success',
                                              msg=f'Name={deviceKeyValues["name"]} already exists', forDetailLogs='')
                    return Response(data={'status': 'failed', 'errorMsg': f'Name={deviceKeyValues["name"]} already exists'}, status=statusCode)     

                
                deviceKeyValues2 = addDeviceHelper(domain, user, deviceKeyValues)
   
                if deviceKeyValues2 == "portPrefixInconsistency":
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDevice', msgType='Failed',
                                              msg=f'Some of the port prefixes were not the same. For example: Eth1/1, Eht1/2', forDetailLogs='')
                    return Response(data={'status': 'failed', 'errorMsg': None}, status=statusCode) 
                
                if deviceKeyValues2 == "portRangeError":            
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDevice', msgType='Error',
                                              msg=f'Domain:{domain} Device:{deviceName}<br>Port range ending number cannot be less than the starting port number. The range ending number must be the last incrementing port number:<br>{ports}', forDetailLogs='')
                    return Response(data={'status': 'failed', 'errorMsg': None}, status=statusCode) 
                            
                elif deviceKeyValues2 is not None:
                    response = DB.name.insertOne(collectionName=Vars.webpage, data=deviceKeyValues2)
                    if response.acknowledged:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDevice', msgType='Success',
                                                  msg=deviceKeyValues2['name'],
                                                  forDetailLogs='')
                    else:
                        status = "failed"
                        errorMsg = f'Failed to add a new port device profile: {deviceKeyValues2["name"]} in MongoDB.'
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDevice', msgType='Failed',
                                                msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                    
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddDevice', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class EditDevice(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='EditDevice', exclude=['engineer'])
    def post(self, request):
        """
        Edit a device
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        deviceName = request.data.get('deviceName', None)
        field = request.data.get('field', None)
        value = request.data.get('value', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'deviceName': deviceName, 'field': field, 'value': value}
            restApi = '/api/v1/lab/inventory/editDevice'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='EditDevice')
        else:        
            try:
                result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                queryFields={'domain': domain, 'name': deviceName},
                                                updateFields={field: value})

                if result:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='EditDevice', msgType='Success',
                                              msg=f'Domain: {domain} Device: {deviceName}  {field}={value}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='EditDevice', msgType='Failed',
                                              msg=f'Domain: {domain} Device: {deviceName}', forDetailLogs='')                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='EditDevice', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class DeleteDevices(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteDevice', exclude=['engineer'])
    def post(self, request):
        """
        Delete 1 or more devices
        
        TODO:
           - Check if the device belongs to any portgroup
           - Don't import if the device port-group is reserved
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        devices = request.data.get('devices', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "devices": devices}
            restApi = '/api/v1/lab/inventory/deleteDevices'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteDevices')
        else:        
            try:
                # Query for the 'name' field with different values
                data = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain':domain, 'name': {'$in': devices}}, 
                                            includeFields=None, sortBy=None )
                countX = deepcopy(data)
                count = len(list(countX))
                
                if count > 0:
                    for device in data:
                        deviceName = device['name']
                        activePortGroups = []
                        deviceAttachedPortGroups = []
                        
                        # Verify if any ports in the deleting device is attached to an active port-group
                        if len(device['portMgmt']) > 0:
                            for portMgmtIndex, portDetails in enumerate(device['portMgmt']):
                                for portGroup in portDetails['portGroups']:
                                    if ManagePortGroup(domain, portGroup).isPortGroupActiveOrInWaitlist():
                                        # The port-group is still actively used
                                        if portGroup not in activePortGroups:
                                            activePortGroups.append(portGroup)
                                    else:
                                        if portGroup not in deviceAttachedPortGroups:
                                            deviceAttachedPortGroups.append(portGroup)     
                        
                        if len(activePortGroups) > 0:
                            status = 'failed'
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDevices', msgType='Failed',
                                                      msg=f'Cannot delete device: {deviceName} in domain:{domain}. There are ports in port-groups that are actively used. Port-Groups: {activePortGroups}', forDetailLogs='') 
                        else: 
                            # The device is not attached to any active port-group. Remove the device                                                       
                            result = DB.name.deleteOneDocument(collectionName=Vars.webpage, fields={'domain': domain, 'name': deviceName})
                            if result:
                                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDevices', msgType='Success',
                                                          msg=f'Domain: {domain} Device: {deviceName}', forDetailLogs='')
                            else:
                                status = 'failed'
                                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDevices', msgType='Failed',
                                                          msg=f'Domain: {domain} Device: {deviceName}', forDetailLogs='')
 
                        # In portGroup DB, remove the device from all port-groups
                        for pg in deviceAttachedPortGroups:    
                            data = ManagePortGroup(domain, pg).getPortGroupDetails()
                            """ 
                            {'activeUsers': [],
                             'available': True,
                             'domain': 'Communal',
                             'loadBalanceGroups': [],
                             'name': 'portGroup1',
                             'ports': {'device-2': {'domain': 'Communal', 'ports': ['1/1', '1/2']}},
                             'waitList': []}
                            """
                            if data:
                                if deviceName in data['ports'].keys():
                                    data['ports'].pop(deviceName, None)

                                ManagePortGroup(domain, pg).update(key='ports', value=data['ports'])
                                
                                SystemLogsAssistant().log(user=user, webPage='portGroup', action='DeleteDevices',
                                                          msgType='Success',
                                                          msg=f'Deleting device:{deviceName} in domain:{domain}. Subsequently, deleting ports in port-group:{pg}',  forDetailLogs='')                                
            except Exception as errMsg:
                status = "failed"
                errorMsg = traceback.format_exc(None, errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDevices', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg), forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

  
class AddPorts(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddPorts', exclude=['engineer'])
    def post(self, request):
        """
        Add ports to a device
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', 'None')
        device = request.data.get('device', 'None')
        ports = request.data.get('ports', 'None')
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'device': device, 'ports': ports}
            restApi = '/api/v1/lab/inventory/addPorts'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='AddPorts')
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain':domain, 'name': device}, includeFields=None)
                if data:
                    currentPorts = data['ports']
                    
                    portList = []
                    portErrorList = []
                    portPrefixVerifyConsistency = []
                    isPortPrefixExists = False
                    
                    if ports:
                        for port in ports.split(','):
                            if port in ['\n', '']:
                                continue

                            # split(',') adds a leading white space. Remove leading white spaces.
                            port = port.strip()
                            
                            # Ethernet2/1
                            regexMatch = search('([a-zA-Z]+)?([0-9]+.+)', port)
                            if regexMatch:
                                portPrefix = regexMatch.group(1)
                                portNumber = regexMatch.group(2)
                                portPrefixVerifyConsistency.append(portPrefix)
                                if portPrefix:
                                    isPortPrefixExists = True
                                
                                # Is a range:  1/1-10
                                # Example:startingPortRange:2/6, endingPortNumber:4
                                if '-' in portNumber:
                                    startingPortRange = port.split('-')[0]
                                    endingPortNumber   = int(portNumber.split('-')[1])

                                    # 1/1-10
                                    if '/' in startingPortRange:
                                        regexMatch = search('(.*/)([0-9]+)', startingPortRange)
                                        if regexMatch:
                                            prefix = regexMatch.group(1)
                                            startingPortNumber = int(regexMatch.group(2))
                                            
                                            if endingPortNumber < startingPortNumber:
                                                portErrorList.append(port)
                                                
                                            for portNum in range(startingPortNumber, endingPortNumber+1):
                                                showPort = f'{prefix}{portNum}'

                                                if showPort in portList:
                                                    continue
                                                
                                                portList.append(f'{showPort}')                                                            
                                                        
                                    # 1.1-1.10       
                                    if '.' in startingPortRange:
                                        regexMatch = search('(.*\.)([0-9]+)', startingPortRange)
                                        if regexMatch:
                                            prefix = regexMatch.group(1)
                                            startingPortNumber = int(regexMatch.group(2))
                                            
                                            if endingPortNumber < startingPortNumber:
                                                portErrorList.append(port)
                                                
                                            for portNumber in range(startingPortNumber, endingPortNumber+1):
                                                showPort = f'{prefix}{portNumber}'
                                                if showPort in portList:
                                                    continue
                                                
                                                portList.append(f'{showPort}')          
                                else:
                                    # Not in a range.  Must be individual ports.
                                    portList.append(port.replace('\n', ''))
                    
                    if len(portErrorList) > 0:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPorts', msgType='Error',
                                                msg=f'Domain:{domain} Device:{device}<br>Port range ending number cannot be less than the starting port number. The range ending number must be the last incrementing port number:<br>{portErrorList}', forDetailLogs='')                        
                        return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
                        
                    combinedList = currentPorts + portList
                    combinedSortedPorts = getSortedPortList2(combinedList)
                    
                    if portList:               
                        for port in portList:
                            tempPortMgmt = deepcopy(Vars.defaultPortProperties)
                            tempPortMgmt.update({'port': port})
                            data['portMgmt'].append(tempPortMgmt)

                    if isPortPrefixExists:
                        def checkPortPrefixForConsistency(list):
                            return len(set(list)) == 1
                        
                        result = checkPortPrefixForConsistency(portPrefixVerifyConsistency)
                        if result is False:
                            return "portPrefixInconsistency"

                    result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                    queryFields={'domain': domain, 'name': device},
                                                    updateFields={'ports': combinedSortedPorts,
                                                                  'portMgmt': data['portMgmt']})

                    if result:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPorts', msgType='Success',
                                                msg=f'Domain: {domain} Device: {device}  Ports={ports}', forDetailLogs='')
                    else:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPorts', msgType='Failed',
                                                msg=f'Domain: {domain} Device: {device}  Ports={ports}', forDetailLogs='')  
                                          
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPorts', msgType='Error',
                                          msg=f"Failed to add ports on device: {device} in domain: {domain}<br>Error: {errorMsg}",
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class RemovePorts(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='RemovePorts', exclude=['engineer'])
    def post(self, request):
        """
        Remove ports from a device
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', 'None')
        device = request.data.get('device', 'None')
        ports = request.data.get('ports', 'None')
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/removePorts'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='RemovePorts')
        else:        
            try:
                # Does the port belong to a port-group?
                #     Is the port-group active?
                #         If yes, cannot remove ports
                #
                # Is the port connected to a device?
                #    If yes, inform the user to disconnect the port
                isPortInPortGroups = []
                isPortConnectedToRemoteDevice = []
                failedMessages = ''

                data = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain': domain, 'name': device}, includeFields=None)
                if data:
                    for portDetails in data['portMgmt']:
                        if portDetails['port'] in ports:
                            if len(portDetails['portGroups']) > 0:
                                isPortInPortGroups.append((portDetails['port'], portDetails['portGroups']))
                            
                            if portDetails['connectedToPort'] != None:
                                if portDetails['connectedToDevice'] != None:
                                    if portDetails['connectedToDevice'] not in isPortConnectedToRemoteDevice:
                                        isPortConnectedToRemoteDevice.append((portDetails['port'], portDetails['connectedToDevice'], portDetails['connectedToPort']))
                
                if len(isPortInPortGroups) > 0:
                    for port, portGroup in isPortInPortGroups:   
                        failedMessages += f'Port {port} needs to be removed from port-group: {portGroup}<br>'
                        
                if len(isPortConnectedToRemoteDevice) > 0:
                    for port, connectedToDevice, connectedToPort in isPortConnectedToRemoteDevice:
                        failedMessages += f'Port {port} needs to be disconnected from device {connectedToDevice} on remote port {connectedToPort}<br>'
                    
                if failedMessages != '':
                    status = 'failed'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemovePorts', msgType='Error',
                                              msg=failedMessages, forDetailLogs='') 
                else:
                    for port in ports:
                       if port in data['ports']:
                            index = data['ports'].index(port)
                            data['ports'].pop(index)
                            data['ports'].insert(index, 'removeMe')

                    while 'removeMe' in data['ports']:
                        data['ports'].remove('removeMe')
                                                
                    for port in ports:        
                        for index, portInPortMgmt in enumerate(data['portMgmt']):
                            if portInPortMgmt != "removeMe" and portInPortMgmt['port'] == port:
                                data['portMgmt'].pop(index)
                                data['portMgmt'].insert(index, 'removeMe')
                                break
                      
                    while 'removeMe' in data['portMgmt']:
                        data['portMgmt'].remove('removeMe')                    

                    result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                    queryFields={'domain': domain, 'name': device},
                                                    updateFields={'ports': data['ports'],
                                                                  'portMgmt': data['portMgmt']})
                    if result:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemovePorts', msgType='Success',
                                                  msg=f'Domain: {domain} Device: {device}  Ports={ports}', forDetailLogs='')
                    else:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemovePorts', msgType='Failed',
                                                  msg=f'Domain: {domain} Device: {device}  Ports={ports}', forDetailLogs='')
                                                                            
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemovePorts', msgType='Error',
                                          msg=f"Failed to get device password<br>Error: {errorMsg}",
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
                                   
class ExportCSV(APIView):
    def get(self, request):
        """
        Export all inventory of a domain into a zipped CSV formatted file
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.GET.get('domain', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain}
            restApi = '/api/v1/lab/inventory/exportCSV'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='ExportCSV')
        else:        
            try:
                import mimetypes
                import zipfile
                import csv

                data = DB.name.getDocuments(collectionName=Vars.webpage,
                                            fields={'domain': domain},
                                            includeFields={'_id':0, 'portMgmtAdditionalKeys':0, 'inventoryAdditionalKeys':0, 'portMgmt':0},
                                            sortBy=[('name', 1)],
                                            limit=None)
                countX = deepcopy(data)
                count = len(list(countX))
                
                #headers = ['domain', 'name', 'deviceType', 'vendor', 'model', 'serialNumber',
                #           'location', 'ipAddress', 'ipPort', 'loginName', 'password',
                #           'connectionProtocol', 'ports', 'notes']

                # Create a temp folder first
                currentDir = os.path.abspath(os.path.dirname(__file__))
                # /opt/Keystack/KeystackUI/topbar/docs/restApi/tempFolderToStoreZipFiles
                tempFolderToStoreZipFiles = f'{currentDir}/labInventory_tempFolderToStoreZipFiles'
                makeFolder(tempFolderToStoreZipFiles)

                exportCsvFilename = f'exported-{domain}-inventory'
                csvFileName = f'{exportCsvFilename}.csv'
                exportCsvFileFullPath = f'{tempFolderToStoreZipFiles}/{exportCsvFilename}.csv'
                zipFileFullPath = f'{tempFolderToStoreZipFiles}/{exportCsvFilename}.zip'
                zipFileName = f'{exportCsvFilename}.zip'

                # Add additonal fields to the default fields
                defaultFields = getDeviceFieldsList()
                notesIndexPosition = defaultFields.index('notes')
                additionalFields = getKeystackMiscAddtionalFields(dbFieldsName=Vars.additionalKeyNameInDB)
                if len(additionalFields) > 0:   
                    defaultFields[notesIndexPosition:notesIndexPosition] = additionalFields
  
                with open(exportCsvFileFullPath, 'w') as outfile:
                    write = csv.DictWriter(outfile, fieldnames=defaultFields)
                    write.writeheader()
                    
                    if data and count > 0:
                        for device in data:
                            flattened_record = {}
                            
                            for field in defaultFields:
                                if field == 'ports':
                                    portValue = str(device[field]).replace('[', '').replace(']', '')

                                    if '"' in portValue:
                                        portValue = portValue.replace('"', '')
                                        
                                    if "'" in portValue:
                                        portValue = portValue.replace("'", '')
                                        
                                    flattened_record.update({field: portValue})
                                else:
                                    if field in additionalFields:
                                        flattened_record.update({field: device['inventoryAdditionalKeyValues'][field]['value']})
                                    else:
                                        flattened_record.update({field: device[field]})
                                    
                            write.writerow(flattened_record)

                os.chdir(tempFolderToStoreZipFiles)
                # .zip and .csv files without their paths
                zipfile.ZipFile(zipFileName, 'w').write(csvFileName)
                fileType, encoding = mimetypes.guess_type(zipFileFullPath)
                
                if fileType is None:
                    fileType = 'application/octet-stream'

                response = HttpResponse(open(zipFileFullPath, 'rb'))
                response['Content-Type'] = fileType
                response['Content-Length'] = str(os.stat(zipFileFullPath).st_size)
                if encoding is not None:
                    response['Content-Encoding'] = encoding
                
                # Filename = file name without the path    
                response['Content-Disposition'] = f'attachment; filename={zipFileName}'
                
                # Remove the .csv and .zip files
                for fileToRemove in [exportCsvFileFullPath, zipFileFullPath]:
                    if os.path.exists(fileToRemove):
                        removeFile(fileToRemove)
                       
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ExportCSV', msgType='Success',
                                          msg=f'Exported domain {domain} inventory to CSV: {zipFileName}')
                return response

            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ExportCSV', msgType='Error',
                                        msg=f'Exporting a zipped inventory to CSV file on domain {domain} failed:<br>{errorMsg}',
                                        forDetailLogs=traceback.format_exc(None, errMsg))
                 
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

    
class ImportCSV(APIView):
    def post(self, request):
        """
        Import a CSV file of devices to be added
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        # Have to use request.data.get
        domain = request.data.get('domain', None)
        overwriteExistingDevices = convertStrToBoolean(request.data.get('overwriteExistingDevices', False))
        
        # importCsvFile: input name:
        #    <input id="importDomainInventoryCSVInput" name="importCsvFile" type="file" class="hideFromUser"/>
        # 'importCsvFile' is obtain from tne input name. Not from JS post
        importedCsvFile = request.FILES.get('importCsvFile', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, 'overwriteExistingDevices': overwriteExistingDevices}
            restApi = '/api/v1/lab/inventory/ImportCSV'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='ImportCSV')
        else:        
            try:
                # Get current device to check if the importing device existing
                # Get domain, name and ipAddress only
                existingDeviceData = DB.name.getDocuments(collectionName=Vars.webpage,
                                                          fields={'domain': domain},
                                                          includeFields={'_id': 0, 'deviceType': 0, 'vendor': 0, 'model': 0,
                                                                         'serialNumber': 0, 'location': 0, 'ipPort': 0, 'loginName': 0,
                                                                         'password': 0, 'connectionProtocol': 0, 'ports': 0, 'notes':0,
                                                                         'portMgmtAdditionalKeys': 0, 'inventoryAdditionalKeyValues': 0},
                                                          sortBy=[('name', 1)],
                                                          limit=None)
                data = list(existingDeviceData)
                
                currentDir = os.path.abspath(os.path.dirname(__file__))
                # /opt/Keystack/KeystackUI/topbar/docs/restApi/tempFolderToStoreZipFiles
                tempFolder = f'{currentDir}/labInventory_tempFolderForImportedCsvFiles'
                if os.path.exists(tempFolder) is False:
                    makeFolder(tempFolder)

                # Store the imported file from memory into a temp folder
                from django.core.files.storage import FileSystemStorage
                
                # importedCsvFile.name=exported-Communal-inventory.csv    importedCsvFile=exported-Communal-inventory.csv
                FileSystemStorage(location=tempFolder).save(importedCsvFile.name, importedCsvFile)
                
                importedFile = str(importedCsvFile)
                tempFileFullPath = f'{tempFolder}/{importedFile}'
                fileNameOnly = importedFile.split('.csv')[0]
                tempFiles = f'{tempFolder}/{fileNameOnly}*'
                                             
                if importedFile.split('.')[-1] != 'csv':
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ImportCSV', msgType='Error',
                                              msg=f'Importing an inventory file must have extension .csv',
                                              forDetailLogs='')
                    
                    return Response(data={'status': 'failed', f'Importing an inventory file must have extension .csv': errorMsg},
                                    status=statusCode)

                csvData = []
                deviceExists = []
                modifiedDevices = []
                noNameDevices = 0

                defaultFields = getDeviceFieldsList()
                notesIndexPosition = defaultFields.index('notes')
                additionalFields = getKeystackMiscAddtionalFields(dbFieldsName=Vars.additionalKeyNameInDB)
                if len(additionalFields) > 0:   
                    defaultFields[notesIndexPosition:notesIndexPosition] = additionalFields

                noSuchFieldsExists = []          
                csvInputFile = readFile(tempFileFullPath)

                for index,line in enumerate(csvInputFile.splitlines()):
                    if index == 0:
                        for field in line.split(','):
                            if field.strip() not in defaultFields:
                                noSuchFieldsExists.append(field) 
                    break
                
                if len(noSuchFieldsExists) > 0:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ImportCSV', msgType='Failed',
                                                msg=f'Cannot add non-existing field/value in the CSV file. You must create the new fields first on the GUI and then export a CSV file for editing: {noSuchFieldsExists}',
                                                forDetailLogs='') 
                    return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
                                                            
                with open(tempFileFullPath, mode ='r') as fileObj:
                    csvObj = csv.DictReader(fileObj, fieldnames=defaultFields)
                    
                    for index, csvRow in enumerate(csvObj):
                        if index == 0:
                            # Skip the headers row
                            continue

                        try:
                            del csvRow[None]
                        except:
                            pass
                        
                        if csvRow['name'] != '':
                            deviceName = csvRow['name'].strip()
                        else:
                            noNameDevices += 1
                            continue
                                                     
                        # row: {'domain': 'Communal', 'name': 'mySwitch2', 'deviceType': 'Layer1 Switch', 'vendor': 'None', 'model': 'None', 'serialNumber': 'None', 'location': 'None', 'ipAddress': 'None', 'ipPort': 'None', 'loginName': 'None', 'password': 'None', 'connectionProtocol': 'ssh', 'ports': 'eth1/1, eth1/2, eth1/3, eth1/4, eth1/5, eth5/1, eth5/2, eth5/3, eth5/4, eth5/5'}

                        # Use deepcopy to refresh the tempData variable with default values.
                        # Otherwise, this variable will get overwritten in memory
                        tempData = deepcopy(Vars.deviceDefaultFields)
                        if len(additionalFields) > 0:
                            for additionalField in additionalFields:
                                tempData.update({additionalField: None})
                                
                        for key, value in csvRow.items():
                            # Overwrite default values with user defined values in the csv rows 
                            if value == '':
                                value = None 
                                
                            tempData.update({key: value})
                        
                        # csvRows: {'domain': 'Communal', 'name': 'device_20', 'deviceType': '', 'vendor': '', 'model': 'None', 'serialNumber': 'None', 'location': '', 'ipAddress': '192.168.28.11', 'ipPort': 'None', 'loginName': 'hgee', 'password': '!Flash128', 'connectionProtocol': 'telnet', 'ports': '1/1, 1/2, 1/3, 1/4, 1/5', 'notes': 'Now is the time for all good men'}
                        totalRowColumns = len([key for key in csvRow.keys()])
                        totalHeaderColumns = len(defaultFields)

                        # Use deepcopy to completely refresh the variable
                        # addDeviceHelper renders the port's formatting if there is any port
                        deviceKeyValues = deepcopy(addDeviceHelper(domain, user, tempData))
                        index = getDictIndexFromList(listOfDicts=data, key='name', value=deviceName, secondLayerDictSearch=False) 

                        if index is not None: 
                            # If there is an index, this means the device exists  
                            deviceExists.append(deviceName)
                            if overwriteExistingDevices:
                                #    - Check if the device belongs to any portgroup
                                #    - Don't import if the device port-group is reserved
                                index = getDictIndexFromList(listOfDicts=data, key='name', value=deviceName, secondLayerDictSearch=False)

                                # device: {'domain': 'Communal', 'name': 'device-1', 'ipAddress': 'None', 'portMgmt': []}
                                device = data[index]
                                activePortGroups = []
                                deviceAttachedPortGroups = []
                    
                                # Verify if any ports in the deleting device is attached to an active port-group
                                if len(device['portMgmt']) > 0:
                                    for portMgmtIndex, portDetails in enumerate(device['portMgmt']):
                                        for portGroup in portDetails['portGroups']:
                                            if ManagePortGroup(domain, portGroup).isPortGroupActiveOrInWaitlist():
                                                # The port-group is still actively used
                                                if portGroup not in activePortGroups:
                                                    activePortGroups.append(portGroup)
                                            else:
                                                if portGroup not in deviceAttachedPortGroups:
                                                    deviceAttachedPortGroups.append(portGroup)        

                                if len(activePortGroups) > 0:
                                    status = 'failed'
                                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteDevices', msgType='Failed',
                                                              msg=f'Cannot import device: {deviceName} in domain:{domain}.<br>There are ports in port-groups that   are actively  used.<br>Port-Groups: {activePortGroups}', forDetailLogs='') 
                                else: 
                                    modifiedDevices.append(deviceName)
                                    result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                                    queryFields={'domain': domain, 'name': deviceName},
                                                                    updateFields=deviceKeyValues)
                        else:
                            # Append a list of non existing devices to be added as new devices
                            csvData.append(deviceKeyValues)

                if noNameDevices > 0:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ImportCSV', msgType='Failed',
                                              msg=f'There were {noNameDevices} devices with no names, which was excluded.',
                                              forDetailLogs='')
                            
                if len(deviceExists) > 0 and overwriteExistingDevices is False:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ImportCSV', msgType='Failed',
                                              msg=f'{len(deviceExists)} devices already exist. Must either select overwriteExistingDevices to modify the parameter values or remove them from the CSV file.<br>{deviceExists}',
                                              forDetailLogs='') 
                    return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
                                       
                if len(csvData) > 0:
                    # Adding new devices as a list                 
                    response = DB.name.insertMany(collectionName=Vars.webpage, data=csvData)

                    if len(response.inserted_ids) == len(csvData): 
                        message = f'Imported {len(response.inserted_ids)} devices'
                        if len(modifiedDevices) > 0:
                            messsage += f'<br>Modified devices: {len(modifiedDevices)}' 
                                     
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ImportCSV', msgType='Success',
                                                  msg=message,
                                                  forDetailLogs='') 
                    else:
                        delta = len(csvData) - len(response.inserted_ids) 
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ImportCSV', msgType='Failed',
                                                  msg=f'Failed to import {delta} devices. Expected to import {len(csvData)} devices',
                                                  forDetailLogs='')                     
                
                # exported-Communal-inventory.csv    exported-Communal-inventory_vW4H3yM.csv 
                # /opt/Keystack/Src/KeystackUI/topbar/docs/restApi/labInventory_tempFolderForImportedCsvFiles/exported-Communal-inventory.csv 
                removeFile(tempFileFullPath)
                execSubprocessInShellMode(f'rm -rf {fileNameOnly}*', cwd=tempFolder)

            except Exception as errMsg:
                removeFile(tempFileFullPath)
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ImportCSV', msgType='Error',
                                          msg=f'Importing a CSV inventory file on domain {domain} failed:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg))
                 
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetDevicePassword(APIView):
    def post(self, request):
        """
        Show the device password in the inventory page when user clicks on the eye icon
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', 'None')
        device = request.data.get('device', 'None')
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        password = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDevicePassword'
            response, errorMsg, status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                          user, webPage=Vars.webpage, action='GetDevicePassword')
            passwordd = response.json()['password']
        else:        
            try:
                data = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain': domain, 'name': device}, includeFields=None)
                if data:
                    password = data['password']
                              
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                password = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDevicePassword', msgType='Error',
                                          msg=f"Failed to get device password<br>Error: {errorMsg}",
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'password': password, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetDomainEnvsDropdownMenu(APIView):
    """
    Internal usage only: Get Env dropdown menu for add-devices-to-Env
    
    /api/v1/lab/inventory/getDomainEnvsDropdown
    """
    def post(self, request):
        """
        Get Env groups for sidebar Env menu
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', 'None') 
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDomainEnvsDropdown'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDomainEnvsDropdwnMenu')
            html = response.json()['envsDropdown']               
        else:          
            try:
                userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
                domainPath = f'{GlobalVars.envPath}/DOMAIN={domain}'
                
                if os.path.exists(domainPath) is False:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDomainEnvsDropdwnMenu', msgType='Error',
                                              msg='There are no Envs created in the domain: {domain}', forDetailLogs='traceback.format_exc(None, errMsg)') 
                                         
                    return Response(data={'envsDropdown':html, 'status':status, 'error':errorMsg}, status=statusCode)

                html = '<div class="dropright">'
                html += "<a class='dropdown-toggle' data-bs-toggle='dropdown' role='button' aria-haspopup=true aria-expanded=false>Select an Env</a>"
                html += f'<ul id="selectedEnvForAddingDevices" class="dropdown-menu" style="width: 300px; height: 400px; overflow: auto; font-size: 13px;" aria-labelledby="">'
                                     
                if domain in userAllowedDomains:
                    for root,dirs,files in os.walk(domainPath):
                        for envFile in files:
                            if bool(search('.*(\.yml|\.ymal)$', envFile)):
                                envGroup = root.split(f'{GlobalVars.envPath}/')[-1].split(f'DOMAIN={domain}')[-1]
                                envGroupAndFile = f'{envGroup}/{envFile}'
                                envFullPath = f'{root}/{envFile}'
                                html += f'<li class="mainFontSize textBlack paddingLeft20px" envFullPath="{envFullPath}">{envGroupAndFile}</li>'
                
                html += '</ul></div>'
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                html = ''
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDomainEnvsDropdwnMenu', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            
        
        return Response(data={'envsDropdown':html, 'status':status, 'error':errorMsg}, status=statusCode)   
    

class GetDeviceNames(APIView):
    """
    Internal usage only: Get a list of domain devices.
                         Allow users to click on the devices to view
    """
    def post(self, request):
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        domain = request.data.get('domain', 'None') 
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        html = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/lab/inventory/getDeviceNames'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetDeviceNames')
            html = response.json()['deviceNames']               
        else:          
            try:
                deviceNames = InventoryMgmt(domain=domain).getAllDomainDeviceNames()
                countX = deepcopy(deviceNames)
                count = len(list(countX))
                html += 'Add devices to the  selected Env:'
                html += f'<ul id="selectedDevicesToAddToEnv" class="listNoBullets">'
                  
                if count > 0:          
                    for device in deviceNames:
                        html += f'<li class="mainFontSize textBlack"><input type="checkbox" name="addSelectedDevicesToEnv" domain="{domain}" deviceName="{device["name"]}" />&emsp;<span class="marginBottom10px">{device["name"]}</span></li>'
                
                html += '</ul>'
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                html = ''
                
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetDeviceNames', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            
        
        return Response(data={'deviceNames':html, 'status':status, 'error':errorMsg}, status=statusCode)   
    

class InventoryAddKey(APIView):
    def post(self, request):
        """
        Add additional field in lab inventory table
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain       = request.data.get('domain', None)
        keyName      = request.data.get('keyName', None)
        keyValue     = request.data.get('keyValue', None)
        defaultValue = request.data.get('defaultValue', '')
        valueType    = request.data.get('valueType', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain":     domain,
                      "keyName":    keyName,
                      "keyValue":   keyValue,
                      "defaultValue": defaultValue,
                      "valueType":  valueType}
            
            restApi = '/api/v1/lab/inventory/addKey'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='InventoryAddKey')
        else:        
            try:
                keystackMiscData = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': Vars.additionalKeyNameInDB})
                if keystackMiscData:                                        
                    # Add the key/value to all the ports
                    for existingField in keystackMiscData['additionalKeys'].keys():
                        if bool(search(keyName, existingField, I)):
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='InventoryAddKey', msgType='Error',
                                                      msg=f'Field name already exists: {keyName}', forDetailLogs='')
                            
                            return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.success)

                    # Boolean: True | Boolean: false
                    if 'Boolean' in valueType:
                        value = convertStrToBoolean(valueType.split(' ')[-1])

                        keystackMiscData['additionalKeys'].update({keyName: {'type': 'boolean', 
                                                                             'options': [True, False], 
                                                                             'defaultValue': value}})  
                    else:
                        if defaultValue == '':
                            defaultValue = keyValue.split(',')[0]
                            
                        keystackMiscData['additionalKeys'].update({keyName: {'type': valueType, 
                                                                             'options': keyValue.split(','), 
                                                                             'defaultValue': defaultValue}}) 
                     
                    DB.name.updateDocument(collectionName=Vars.keystackMisc,
                                           queryFields={'name': Vars.additionalKeyNameInDB},
                                           updateFields={'additionalKeys': keystackMiscData['additionalKeys']}) 
                
                # Update all devices with new field/value                        
                inventoryData = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': domain})

                if inventoryData:
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
                
                    # Result is None if there is no devices to update
                    result = None
                    
                    # Update all devices                                                    
                    for deviceData in inventoryData:
                        if valueType == 'options':
                            deviceData['inventoryAdditionalKeyValues'].update({keyName: {'value': defaultValue}})
                                                                                
                        if valueType in ['Boolean: True', 'Boolean: False']:
                            deviceData['inventoryAdditionalKeyValues'].update({keyName: {'value': value}})
                           
                        result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                        queryFields={'domain': domain, 'name': deviceData['name']},
                                                        updateFields={'inventoryAdditionalKeyValues': deviceData['inventoryAdditionalKeyValues']},
                                                        appendToList=False)
                    if result:
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='InventoryAddKey', msgType='info',
                                                  msg=f'Added keyName:{keyName}',
                                                  forDetailLogs='') 
                                                                        
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='InventoryAddKey', msgType='Error',
                                          msg=f'Adding additional keys failed: {keyName}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class RemoveKeysTable(APIView):
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
        tableRowsHtml = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain}
            restApi = '/api/v1/lab/inventory/removeKeysTable'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveKeysTable')
            tableRowsHtml = response.json()['removeKeyTable'] 
                  
        else:        
            try:
                keystackMiscData = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': Vars.additionalKeyNameInDB})
                
                for additionalKey in sorted(keystackMiscData['additionalKeys'].keys()):
                    tableRowsHtml += f'<tr>'
                    tableRowsHtml += f'<td><input type="checkbox" name="inventoryRemoveKeyCheckboxes" domain="{domain}" key="{additionalKey}"></td>'
                    tableRowsHtml += f'<td>{additionalKey}</td>'
                    tableRowsHtml += f'<td>{keystackMiscData["additionalKeys"][additionalKey]["type"]}</td>'
                    tableRowsHtml += f'<td>{keystackMiscData["additionalKeys"][additionalKey]["defaultValue"]}</td>'
                    
                    if keystackMiscData["additionalKeys"][additionalKey]["type"] == 'options':
                        optionsDropdown = '<div class="dropdown">'
                        optionsDropdown += f"<a class='dropdown-toggle textBlack' data-toggle='dropdown' id='fieldOptionsDropdown' role='button' aria-haspopup=true aria-expanded=false>View</a>" 
    
                        optionsDropdown += f'<div class="dropdown-menu dropdownSizeSmall editFieldOptionsDropdown">' 
                        optionsDropdown += '<center><span class="textBlack">Add / Remove Field Options</span></center><br>'
                        
                        optionsDropdown += f'<div class="input-group paddingLeft10px">'
                        optionsDropdown += f'<input type="text" class="form-control inputBoxWidth200px textBlack" id="{additionalKey}" name="addFieldOption">'
                        optionsDropdown += f'<button class="btn btn-primary addFieldOptionClass" type="button" field="{additionalKey}">Add Option</button><br><br>'
                        optionsDropdown += '</div><br>'
                        
                        optionsDropdown += f'<a href="#" class="paddingLeft20px removeFieldOptionsClass" fieldName="{additionalKey}" action="remove">Remove Options</a><br><br>'

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
                        for option in sorted(keystackMiscData["additionalKeys"][additionalKey]["options"]):
                            options += f'<tr>'
                            options += f'<td><input type="checkbox" name="fieldOptionRemoveCheckbox" option="{option}" /></td>'
                            options += f'<td option="{option}">{option}</td>'
                            options += '</tr>'
        
                        optionsDropdown += f'{options}<tr></tr>'
                        optionsDropdown += f'</tbody></table>'
                        optionsDropdown += '</div></div>'
                    else:
                        optionsDropdown = ''
                        
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
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveKeysTable', msgType='Error',
                                          msg=errorMsg,
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'removeKeyTable': tableRowsHtml, 'status': status, 'errorMsg': errorMsg}, status=statusCode)

        

class RemoveKeys(APIView):
    def post(self, request):
        """
        Remove fields
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        domain = request.data.get('domain', None)
        keys = request.data.get('keys', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"domain": domain, "keys": keys}
            restApi = '/api/v1/lab/inventory/removeKeys'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveKeys')
        else:        
            try:
                keystackMiscData = DB.name.getOneDocument(collectionName=Vars.keystackMisc, fields={'name': Vars.additionalKeyNameInDB})
                if len(keystackMiscData['additionalKeys']) > 0:
                    for key in keys:
                        if key in keystackMiscData['additionalKeys'].keys():
                            del keystackMiscData['additionalKeys'][key]

                    result = DB.name.updateDocument(collectionName=Vars.keystackMisc,
                                                    queryFields={'name': Vars.additionalKeyNameInDB},
                                                    updateFields={'additionalKeys': keystackMiscData['additionalKeys']})  
                                                                    
                inventoryData = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': domain})
                for device in inventoryData: 
                    for key in keys:
                        if key in device['inventoryAdditionalKeyValues'].keys():
                            del device['inventoryAdditionalKeyValues'][key]

                    result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                    queryFields={'domain': domain, 'name': device['name']},
                                                    updateFields={'inventoryAdditionalKeyValues': device['inventoryAdditionalKeyValues']})  

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveKeys', msgType='Success',
                                          msg=f'Removed keys={keys}',
                                          forDetailLogs='') 
                                                                       
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveKeys', msgType='Error',
                                          msg=f'Removing fields failed: {keys}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class ChangeDeviceAdditionalFieldValue(APIView):
    def post(self, request):
        """
        Edit a device additional field value
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        
        domain = request.data.get('domain', None)
        device = request.data.get('device', None)
        field = request.data.get('field', None)
        value = request.data.get('value', None)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'domain': domain, 'device': device, 'field': field, 'value': value}
            restApi = '/api/v1/lab/inventory/changeDeviceAdditionalFieldValue'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ChangeDeviceAdditionalFieldValue')
        else:        
            try:
                if device != 'all':
                    data = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain': domain, 'name': device}, includeFields=None)
                    data['inventoryAdditionalKeyValues'][field].update({'value': value})
                    
                    result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                    queryFields={'domain': domain, 'name': device},
                                                    updateFields={'inventoryAdditionalKeyValues': data['inventoryAdditionalKeyValues']})

                if device == 'all':
                    data = DB.name.getDocuments(collectionName=Vars.webpage, fields={},
                                                 includeFields={'_id':0}, limit=None)
                    for deviceData in data:
                        deviceData['inventoryAdditionalKeyValues'][field]['value'] = value
                        result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                        queryFields={'domain': domain,'name': deviceData['name']},
                                                        updateFields={'inventoryAdditionalKeyValues': deviceData['inventoryAdditionalKeyValues']})
                        
                if result:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ChangeDeviceAdditionalFieldValue', msgType='Success',
                                              msg=f'Domain: {domain} Device: {device}  {field}={value}', forDetailLogs='')
                else:
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ChangeDeviceAdditionalFieldValue', msgType='Failed',
                                              msg=f'Domain: {domain} Device: {device}', forDetailLogs='')                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ChangeDeviceAdditionalFieldValue', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class AddFieldOption(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='AddFieldOption', exclude=['engineer'])
    def post(self, request):
        """
        Add additonal field option to the existing list
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
            restApi = '/api/v1/lab/inventory/addFieldOption'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='AddFieldOption')
        else:        
            try:
                additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=Vars.additionalKeyNameInDB)
                additionalKeyObj[field]['options'].append(option)
                updateAdditionalKeyDB(dbFieldsName=Vars.additionalKeyNameInDB, keyValues=additionalKeyObj)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddFieldOptions', msgType='Success',
                                          msg=f'Added options: {option} to Field:{field}', forDetailLogs='') 
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddFieldOption', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg), forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class RemoveFieldOptions(APIView):
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
            restApi = '/api/v1/lab/inventory/removeFieldOptions'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='RemoveFieldOptions')
        else:        
            try:
                additionalKeyObj = getKeystackMiscAddtionalFields(dbFieldsName=Vars.additionalKeyNameInDB)

                for option in options:
                    index = additionalKeyObj[fieldName]['options'].index(option)
                    additionalKeyObj[fieldName]['options'].pop(index)

                updateAdditionalKeyDB(dbFieldsName=Vars.additionalKeyNameInDB, keyValues=additionalKeyObj)

                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFieldOptions', msgType='Success',
                                          msg=f'Removed: {options}', forDetailLogs='') 
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='RemoveFieldOptions', msgType='Error',
                                          msg=traceback.format_exc(None, errMsg), forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
                                                                       
class TestConnection(APIView):
    def post(self, request):
        """
        Connect to device to test reachability
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
            restApi = '/api/v1/lab/inventory/testConnection'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='TestConnection')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
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
                                              msg=f'Port Device Device={device} ipAddress={ipAddress} ipPort={ipPort}', forDetailLogs='')
                else:
                    errorMsg = f'Device={device} has no IP Address'
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='TestConnection', msgType='Error',
                                              msg=errorMsg, forDetailLogs='')
                    return Response(data={'html': '<span class="fa-solid fa-circle redColorStatus"></span>', 
                                          'status': 'failed', 'errorMsg': errorMsg}, status=statusCode)
                                        
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='TestConnection', msgType='Error',
                                          msg=f'Port Device Device={device} ipAddress={ipAddress} ipPort={ipPort}:<br>{errorMsg}',
                                          forDetailLogs=traceback.format_exc(None, errMsg)) 

        return Response(data={ 'html': html, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    