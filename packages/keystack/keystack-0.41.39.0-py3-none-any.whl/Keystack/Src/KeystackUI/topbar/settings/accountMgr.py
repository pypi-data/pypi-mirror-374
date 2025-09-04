import os, re, sys, json, traceback, secrets

import keystackUtilities
from db import DB

class Vars:
    # This must be the same in accountMgmt Vars.webpage
    # It uses the same DB collection name
    webpage = 'accountMgmt'
    

class AccountMgr():
    def addUser(self, fullName:str, loginName:str, password:str, email:str, userRole:str):
        response = DB.name.insertOne(collectionName=Vars.webpage, 
                                     data={'fullName': fullName, 'loginName': loginName, 'password': password,
                                           'email': email, 'userRole': userRole, 'isLoggedIn': False,
                                           'apiKey': secrets.token_urlsafe(16),
                                           'defaultDomain': None, 'domains': [], 'userPreferences': {}})
        if response.acknowledged:
            return True
                        
    def isUserExists(self, key:str, value:str):
        isExists = DB.name.isDocumentExists(Vars.webpage, key=key, value=value, regex=False)
        if isExists:        
            return True

    def deleteUser(self, fullName):
        if fullName in ['Administrator', 'root']:
            return
        
        DB.name.deleteOneDocument(collectionName=Vars.webpage, fields={'fullName': fullName})

    def getUserDetails(self, key:str, value:str):
        """
        key: field. Example: fullName | loginName
        value: value
        """
        userDetails = DB.name.getDocuments(collectionName=Vars.webpage, fields={key: value.strip()}, includeFields={'_id':0})
            
        if userDetails.count() == 0:
            return None
        else:
            return userDetails[0]

    def getAllUsers(self, domain:str=None):
        """           
        Get all users for adding users to User-Groups & for scheduling
        """
        if domain:
            fields = {'domains': {'$in': domain}}
        else:
            fields = {}
            
        users = DB.name.getDocuments(collectionName=Vars.webpage,
                                     fields=fields,
                                     includeFields={'_id':0, 'loginName':0, 'password':0, 'email':0, 
                                                    'userRole':0, 'isLoggedIn':0, 'apiKey':0,
                                                    'defaultDomain':0, 'domains':0, 'userGroup':0,
                                                    'userPreferences':0},
                                                    sortBy=[('fullName', 1)])
        if users.count() == 0:
            return None
        else:
            # Returns a generated object: <pymongo.cursor.Cursor object at 0x7fd1e421d480>                                                                         
            return users

    def getUserGroupUsers(self, userGroup):
        """           
        Get user group users
        """
        users = DB.name.getDocuments(collectionName=Vars.webpage,
                                     fields={'userGroup:', userGroup},
                                     includeFields={'_id':0, 'loginName':0, 'password':0, 'email':0, 
                                                    'userRole':0, 'isLoggedIn':0, 'apiKey':0,
                                                    'defaultDomain':0, 'domains':0, 'userGroup':0,
                                                    'userPreferences':0},
                                                    sortBy=[('fullName', 1)])
        if users.count() == 0:
            return None
        else:
            # Returns a generated object: <pymongo.cursor.Cursor object at 0x7fd1e421d480>                                                                         
            return users
        
    def updateUser(self, fullName, modifyFields):
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
            if fullName:
                userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                              fields={'fullName': fullName}, includeFields={'_id':0})[0]
                return userDB['apiKey']
            
            if login:
                userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                              fields={'login': login}, includeFields={'_id':0})[0]
                return userDB['apiKey']
                        
        except:
            return None

    def getApiKeyUser(self, apiKey):
        """ 
        Get the user full name with the api key
        """
        userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                      fields={'apiKey': apiKey}, includeFields={'_id':0})

        try:
            return userDB[0]['fullName']
        except:
            return None

    def isApiKeyValid(self, apiKey):
        """ 
        For CLI usage. Verify if the API-Key is valid.
        """
        userDB = DB.name.getDocuments(collectionName=Vars.webpage,
                                      fields={'apiKey': apiKey}, includeFields={'_id':0})
        if userDB.count() > 0:
            return userDB[0]['fullName']
        else:
            return None           

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
    
    def getUserRole(self, fullName):
        """ 
        admin, manager, engineer
        """
        data = self.getUserDetails(key='fullName', value=fullName)
        if data:
            return data['userRole']
        
    def getAllAdminUsers(self):
        adminUsers = DB.name.getDocuments(collectionName=Vars.webpage,
                                          fields={'userRole:', 'admin'},
                                          includeFields={'_id':0, 'loginName':0, 'password':0, 'email':0, 
                                                         'userRole':0, 'isLoggedIn':0, 'apiKey':0,
                                                         'defaultDomain':0, 'domains':0, 'userGroup':0,
                                                         'userPreferences':0},
                                                         sortBy=[('fullName', 1)])
        
        print('\n--- accountMgr:getAllAdminUsers():', adminUsers)
        return adminUsers
        