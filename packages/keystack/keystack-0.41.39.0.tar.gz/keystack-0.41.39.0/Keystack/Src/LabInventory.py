from db import DB

    
class InventoryMgmt:
    def __init__(self, domain=None, device=None):
        self.domain = domain
        self.device = device
        self.dbCollectionName = 'labInventory'

    def getDeviceDetails(self) -> dict:
        """ 
        Returns
            {'device_1': {'additionalKeys': 'None',
                          'connectionProtocol': 'telnet',
                          'deviceType': None,
                          'domain': 'Communal',
                          'ipAddress': '192.168.28.11',
                          'ipPort': 'None',
                          'location': None,
                          'loginName': 'hgee',
                          'model': 'None',
                          'name': 'device_1',
                          'notes': 'Now is the time for all good men',
                          'password': 'myPassword',
                          'ports': ['1/1', '1/2', '1/3', '1/4', '1/5'],
                          'serialNumber': 'None',
                          'vendor': None}}
        """
        data = DB.name.getOneDocument(self.dbCollectionName,
                                      fields={'domain': self.domain, 'name': self.device},
                                      includeFields={'_id':0, 'portMgmt':0})
        if data:
            return {self.device: data}

    def getDeviceDetailsForEnvFiles(self) -> dict:
        """ 
        Returns
            {'device_1': {'additionalKeys': 'None',
                          'connectionProtocol': 'telnet',
                          'deviceType': None,
                          'domain': 'Communal',
                          'ipAddress': '192.168.28.11',
                          'ipPort': 'None',
                          'location': None,
                          'loginName': 'hgee',
                          'model': 'None',
                          'name': 'device_1',
                          'notes': 'Now is the time for all good men',
                          'password': 'myPassword',
                          'ports': ['1/1', '1/2', '1/3', '1/4', '1/5'],
                          'serialNumber': 'None',
                          'vendor': None}}
        """
        # data = DB.name.getOneDocument(self.dbCollectionName,
        #                               fields={'domain': self.domain, 'name': self.device},
        #                               includeFields={'_id':0, 'ipAddress':1,
        #                                              'ipPort':1, 'deviceType':1, 'loginName':1, 'password':1,
        #                                              'connectionProtocol':1})
        data = DB.name.getOneDocument(self.dbCollectionName,
                                      fields={'domain': self.domain, 'name': self.device},
                                      includeFields={'_id':0, 'portMgmt':0})
        if data:
            return {self.device: data}
    
    def getAllDomainDeviceNames(self):
        data = DB.name.getDocuments(self.dbCollectionName, fields={'domain': self.domain}, includeFields={'name'}, sortBy=[('name', 1)])
        if data:
            return data
        else:
            return []
                                
    def getPortsInPortMgmt(self, ports: list=[]) -> list:
        """ 
        ports:['1/1', '1/2']
        
        Returns:
        [{'port': '1/1', 'connectedToDevice': 'device-2', 'connectedToPort': '2/1', 'portGroups': ['port-group1'],
          'multiTenant': False, 'opticMode': 'single-mode', 'portType': None, 'vlanIDs': [], 'autoNeg': True,
          'speed': '1G', 'reserved': 'available', 'additionalKeyValues': {}}]
        """
        portList = []
        portDict = {}
        data = DB.name.getOneDocument(self.dbCollectionName,
                                      fields={'domain': self.domain, 'name': self.device},
                                      includeFields={'_id':0, 'portMgmt':1})
        if data:
            for portMgmt in data['portMgmt']:
                if portMgmt['port'] in ports:
                    portList.append(portMgmt)
                    portDict.update({portMgmt['port']: portMgmt})
                
        return portDict
        
        