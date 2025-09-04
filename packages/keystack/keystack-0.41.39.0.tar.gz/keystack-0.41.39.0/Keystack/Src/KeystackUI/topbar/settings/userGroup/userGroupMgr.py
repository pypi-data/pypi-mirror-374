from db import DB
from domainMgr import DomainMgr
from globalVars import GlobalVars

class Vars:
    # This must be the same in accountMgmt Vars.webpage
    # It uses the same DB collection name
    webpage = 'userGroup'
    

class UserGroupMgr():  
    def createUserGroup(self, userGroup: str):
        DomainMgr().addUserGroups(domain=GlobalVars.defaultDomain, userGroups=[userGroup])
        
        if self.isUserGroupExists(userGroup=userGroup) is None:
            response = DB.name.insertOne(collectionName=Vars.webpage, 
                                         data={'userGroup': userGroup, 'users': []})
            if response.acknowledged:
                return True
        else:
            return True

    def removeUserGroups(self, userGroups: list=[str]):
        '''
        Usage:
           removeUserGroup()
           isUserGroupExists()
        '''
        DomainMgr().removeUserGroups(domain=GlobalVars.defaultDomain, userGroups=userGroups)
                
        for userGroup in userGroups:
            result = DB.name.deleteOneDocument(collectionName=Vars.webpage,
                                               fields={'userGroup': userGroup})

    def isUserGroupExists(self, userGroup: str):
        ''' 
        Returns None if user group doesn't exists
        '''
        isExists = DB.name.isDocumentExists(collectionName=Vars.webpage,
                                            key='userGroup', value=userGroup, regex=True)
        if isExists:        
            return True
    
    def isUserInUserGroup(self, userGroup: str, user: str):
        result = DB.name.getDocuments(collectionName=Vars.webpage,
                                      fields={'userGroup': userGroup, 'users': {"$in": [user]}},
                                      includeFields={"_id": 0})
        if result.count() == 0:
            return False
        else:
            return True

    def getUserGroupUsers(self, userGroup):
        ''' 
        Usage:
           Use userGroups.count() to verify user group length
        '''
        users = DB.name.getDocuments(collectionName=Vars.webpage,
                                     fields={'userGroup':userGroup},
                                     includeFields={'_id':0, 'userGroup':0})
        if users.count() == 0:
            return []
        else:
            # Returns a generated object: <pymongo.cursor.Cursor object at 0x7fd1e421d480>
            return users[0]['users']    
                            
    def getAllUserGroups(self):
        ''' 
        Usage:
           Use userGroups.count() to verify user group length
        '''
        userGroups = DB.name.getAllDocuments(collectionName=Vars.webpage,
                                             includeFields={'_id':0, 'userGroup':1}, 
                                             sortBy=[('userGroup', 1)])
        if userGroups.count() == 0:
            return []
        else:
            # Returns a generated object: <pymongo.cursor.Cursor object at 0x7fd1e421d480>
            userGroupList = []
            for userGroup in userGroups:
                userGroupList.append(userGroup['userGroup'])

            return userGroupList    

    def addUsers(self, userGroup: str, users: list=[str]):
        if self.isUserGroupExists(userGroup) is None:
            self.createUserGroup(userGroup)

        for user in users: 
            if self.isUserInUserGroup(userGroup, user):
                continue
            else:
                result = DB.name.updateDocument(collectionName=Vars.webpage, 
                                                queryFields={'userGroup': userGroup}, 
                                                updateFields={'users': user},
                                                appendToList=True)
            # result['updatedExisting] = None|True|False
  
    def removeUsersFromUserGroup(self, userGroup: str, users: list=[str]):
        for user in users:
            # result: {'n': 1, 'nModified': 0, 'ok': 1.0, 'updatedExisting': True}
            result = DB.name.updateDocument(collectionName=Vars.webpage, 
                                              queryFields={'userGroup': userGroup},
                                              updateFields={'users': user}, removeFromList=True)

