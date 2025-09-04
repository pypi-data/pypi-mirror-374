import os, re, sys, json, traceback, secrets
from pprint import pprint 
from copy import deepcopy

import keystackUtilities
from commonLib import getHttpIpAndPort
from RedisMgr import RedisMgr
from db import DB

currentDir = os.path.abspath(os.path.dirname(__file__))
keystackUIPath = currentDir.replace('accountMgr', 'KeystackUI')
sys.path.insert(0, keystackUIPath)
from execRestApi import ExecRestApi

class Vars:
    # This must be the same in accountMgmt Vars.webpage
    # It uses the same DB collection name
    webpage = 'accountMgmt'
    

class AccountMgr():
    def syncAccountsWithRedis(self):
        if RedisMgr.redis:
            print('Account:SyncAccountsWithRedis')
            accounts = DB.name.getDocuments(collectionName=Vars.webpage, fields={}, includeFields={'_id':0})
 
            countX = deepcopy(accounts)
            count = len(list(countX))
            if count > 0:
                userAccountRedis = {}
                # {'fullName': 'Administrator', 'loginName': 'admin', 'password': 'admin', 'apiKey': '6FGjMjVqPdQq4D6elqE0dQ', 
                # 'email': None, 'isLoggedIn': True, 'defaultDomain': None, 'userPreferences': {}, 'sysAdmin': True}
                for user in accounts:
                    userAccountRedis.update({user['fullName']: {'fullName': user['fullName'],
                                                                'sysAdmin': user['sysAdmin'],
                                                                'loginName': user['loginName'],
                                                                'password': user['password'],
                                                                'apiKey': user['apiKey'],
                                                                'email': user['email'],
                                                                'isLoggedIn': user['isLoggedIn'],
                                                                'userPreferences': user['userPreferences']
                                                                }})

                RedisMgr.redis.write(keyName='accounts', data=userAccountRedis)
                
    def addUser(self, fullName:str, loginName:str, password:str, email:str, sysAdmin:bool):
        if RedisMgr.redis:
            data = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            if fullName not in data.keys():
                data.update({fullName: {'fullName': fullName, 'loginName': loginName, 'password': password,
                                        'email': email, 'sysAdmin': sysAdmin, 'isLoggedIn': False,
                                        'apiKey': secrets.token_urlsafe(16), 'userPreferences': {}}})
                RedisMgr.redis.updateKey(keyName=f'accounts', data=data)
            
        response = DB.name.insertOne(collectionName=Vars.webpage, 
                                     data={'fullName': fullName, 'loginName': loginName, 'password': password,
                                           'email': email, 'sysAdmin': sysAdmin, 'isLoggedIn': False,
                                           'apiKey': secrets.token_urlsafe(16), 'userPreferences': {}})
        if response.acknowledged:
            return True
                        
    def isUserExists(self, key:str, value:str):
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            for user, properties in accounts.items():
                if properties[key] == value:
                    return True
        else:
            isExists = DB.name.isDocumentExists(Vars.webpage, key=key, value=value, regex=False)
            if isExists:        
                return True

        return False
    
    def deleteUser(self, fullName):
        if fullName in ['Administrator', 'root']:
            # Cannot delete the Admin
            return
        
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            if fullName in accounts.keys():
                del accounts[fullName]
                RedisMgr.redis.updateKey(keyName='accounts', data=accounts)
                
        DB.name.deleteOneDocument(collectionName=Vars.webpage, fields={'fullName': fullName})

    def getUserDetails(self, key:str, value:str):
        """
        key: field. Example: fullName | loginName
        value: value
        """
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            for user, properties in accounts.items():
                if properties[key] == value:
                    return properties
        else:
            userDetails = DB.name.getDocuments(collectionName=Vars.webpage, fields={key: value.strip()}, includeFields={'_id':0})
            countX = deepcopy(userDetails)
            count = len(list(count))
            if count == 0:
                return None
            else:
                return userDetails
        
    def getAllUsers(self):
        """           
        Get all users for adding users to User-Groups & for scheduling
        """
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            return [user for user in accounts.keys()]
        else:
            users = DB.name.getDocuments(collectionName=Vars.webpage,
                                        fields={},
                                        includeFields={'_id':0, 'loginName':0, 'password':0, 'email':0, 
                                                        'sysAdmin':0, 'isLoggedIn':0, 'apiKey':0,
                                                        'defaultDomain':0, 'domains':0,
                                                        'userPreferences':0},
                                                        sortBy=[('fullName', 1)])
            count = users
            if len(list(count)) == 0:
                return None
            else:
                # Returns a generated object: <pymongo.cursor.Cursor object at 0x7fd1e421d480> 
                # returns list : [{'fullName': name}  ...]                                                                       
                return users

    def getAllUsersDetails(self):
        """           
        Internal use only: Get Get all user details for acouunt table data
        """
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            return [properties for user, properties in accounts.items()]
        else:
            users = DB.name.getDocuments(collectionName=Vars.webpage,
                                        fields={},
                                        includeFields={'_id':0})
            count = users
            if len(list(count)) == 0:
                return []
            else:
                # Returns a generated object: <pymongo.cursor.Cursor object at 0x7fd1e421d480> 
                # returns list : [{'fullName': name}  ...]                                                                       
                return users
            
    def updateUser(self, fullName, modifyFields):
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            if fullName in accounts.keys():
                accounts[fullName].update(modifyFields)
                RedisMgr.redis.updateKey(keyName='accounts', data=accounts)
       
        result = DB.name.updateDocument(collectionName=Vars.webpage, queryFields={'fullName': fullName}, updateFields=modifyFields) 
        # True | False
        return result
        
    def isUserLoggedIn(self, loginName:str):
        userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                      fields={'loginName': loginName}, includeFields={'_id':0})[0]
        if userDB['isLoggedIn']:
            return True
  
    def getApiKey(self, fullName=None, login=None):
        try:
            if RedisMgr.redis:
                accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')   
                if fullName:
                    if fullName in accounts.keys():
                        return accounts[fullName]['apiKey']
                
                if login:
                    for user, properties in accounts.items():
                        if properties['loginName'] == login:
                            return properties['apiKey']
            else:   
                if fullName:
                    userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                                fields={'fullName': fullName}, includeFields={'_id':0})[0]
                    return userDB['apiKey']
                
                if login:
                    userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                                fields={'loginName': login}, includeFields={'_id':0})[0]
                    return userDB['apiKey']
                        
        except:
            return None

    def getApiKeyUser(self, apiKey):
        """ 
        Get the user full name with the api key
        """
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            for user, properties in accounts.items():
                if properties['apiKey'] == apiKey:
                    return user
        else:            
            userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                          fields={'apiKey': apiKey}, includeFields={'_id':0})

            try:
                return userDB[0]['fullName']
            except:
                return None

    def isApiKeyValid(self, apiKey):
        """ 
        For CLI usage. Verify if the API-Key is valid.
        If user runs Keystack on local host CLI, need to validate the user's api-key
        in docker container because it needs to get value from mongodb
        """
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            for user, properties in accounts.items():
                if properties['apiKey'] == apiKey:
                    return user
        else:
            keystackHttpIpAddress, keystackIpPort = getHttpIpAndPort()
            execRestApiObj = ExecRestApi(ip=keystackHttpIpAddress, port=keystackIpPort,
                                         https=False, keystackLogger=None)
            
            response = execRestApiObj.post(restApi='/api/v1/system/account/isApiKeyValid', params={'apiKey': apiKey}, 
                                           timeout=10, maxRetries=3, ignoreError=False, silentMode=True)
            return response.json()['result']

    def getRequestSessionUser(self, request):
        """ 
        Used internally by rest api views.
         
        rest api views could be viewed by Keystack UI logins or by rest apis.
        If user is logged into the UI, the request.session should have the 'user' name.
        If user is using rest api, an api-key is required.
        """
        if 'user' in request.session:
            # Keystack UI logged in
            user = request.session['user']
        elif 'API-Key' in request.headers:
            # REST API
            apiKey = request.headers.get('API-Key')
            user = self.getApiKeyUser(apiKey=apiKey)
        else:
            # CLI user: Not logged in
            # [True, '<user>\n']
            cliUser = keystackUtilities.execSubprocessInShellMode('whoami', showStdout=False)[1].replace('\n', '')
            user = f'CLI: {cliUser}'
        
        return user
                          
    def getPassword(self, fullName):
        try:
            if RedisMgr.redis:
                accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
                if fullName in accounts.keys():
                    return accounts[fullName]['password']
            else:
                userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                            fields={'fullName': fullName}, includeFields={'_id':0})[0]
                return userDB['password']
        except:
            return None
 
    def regenerateApiKey(self, fullName):
        newApiKey = secrets.token_urlsafe(16)
        
        try:
            self.updateUser(fullName, {'apiKey': newApiKey})
        except Exception as errMsg:
            return None

        return newApiKey

    def isUserSysAdmin(self, fullName):
        """ 
        Verify if the user is a system administrator
        """
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            if fullName in accounts.keys():
                return accounts[fullName]['sysAdmin']
        else:    
            data = self.getUserDetails(key='fullName', value=fullName)
            if data:
                return data['sysAdmin']
              
    def getAllAdminUsers(self):
        """ 
        Returns a list of admin user full names
        """
        if RedisMgr.redis:
            accounts = RedisMgr.redis.getCachedKeyData(keyName='accounts')
            return [user for user, properties in accounts.items() if properties['sysAdmin']]         
  
        else:
            adminUsers = DB.name.getDocuments(collectionName=Vars.webpage,
                                            fields={'sysAdmin': True},
                                            includeFields={'_id':0, 'loginName':0, 'password':0, 'email':0, 
                                                            'userRole':0, 'isLoggedIn':0, 'apiKey':0,
                                                            'defaultDomain':0, 'domains':0,
                                                            'userPreferences':0},
                                                            sortBy=[('fullName', 1)])
            if adminUsers:
                return [adminUser['fullName'] for adminUser in adminUsers]
            else:
                return []
        
        