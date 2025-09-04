import os, sys, traceback
from glob import glob
from pprint import pprint 
from copy import deepcopy

from globalVars import GlobalVars
from keystackUtilities import readYaml, writeToYamlFile, mkdir, removeFile, chownChmodFolder, removeFolder, execSubprocessInShellMode
from accountMgr import AccountMgr
from RedisMgr import RedisMgr
from db import DB

class Vars:
    # This must be the same in accountMgmt Vars.webpage
    # It uses the same DB collection name
    webpage = 'domains'
    

class DomainMgr():        
    def dumpDomainDataToRedis(self):
        """ 
        Remove existing redis key-name domains.
        Then write domains to redis.
        """
        try:
            print('DomainMgr:dumpDomainDataToRedis')
            domainsData = DB.name.getDocuments(collectionName=Vars.webpage, fields={}, includeFields={'_id':0})
            count = deepcopy(domainsData)
            if len(list(count)) == 0:
                print('dumpDomainDataToRedis: Domains does not exists in MongoDB. Creating new domains collection')
                # Add default domain       
                response = DB.name.insertOne(collectionName=Vars.webpage, 
                                             data={'domain': GlobalVars.defaultDomain,
                                                   'users': {}})
                if response.acknowledged is False:
                    print('\ndumpDomainDataToRedis: Failed to initiate domains DB')
                    return False

            # Transfer fresh data from MongoDB to redis
            domainsData = DB.name.getDocuments(collectionName=Vars.webpage, fields={}, includeFields={'_id':0})
            count = deepcopy(domainsData)
            if len(list(count)) == 0:
                for domain in domainsData:
                    redisDomainKey = f'domain-{domain["domain"]}'
                    if RedisMgr.redis.keyExists(redisDomainKey):
                        print(f'dumpDomainDataToRedis: Deleting Redis existing domain data: {redisDomainKey}')   
                        RedisMgr.redis.deleteKey(keyName=redisDomainKey)
                    
                    print('dumpDomainDataToRedis: Transfer domain data from MongoDB to Redis')
                    RedisMgr.redis.write(keyName=redisDomainKey, data=domain['users'])
            
        except Exception as errMsg:
            print('dumDomainDataToRedis Error:', traceback.format_exc(None, errMsg))

    def createDefaultDomain(self):
        self.create(GlobalVars.defaultDomain)
                   
    def create(self, domain: str):
        """ 
        Create a domain
        """
        try:
            # Add all sys-admins to the domain
            allSysAdmins = AccountMgr().getAllAdminUsers()
            data = {}
            for user in allSysAdmins:
                data.update({user: {'userRole': 'admin', 'userIsSysAdmin': True}})
                        
            if RedisMgr.redis:
                redisData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
                if redisData == {}:
                    # Automatically add all sys-admins to the new domain
                    RedisMgr.redis.updateKey(keyName=f'domain-{domain}', data=data)
            
            domainsData = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': domain}, includeFields={'_id':0})
            count = deepcopy(domainsData)
            if len(list(count)) == 0:
                response = DB.name.insertOne(collectionName=Vars.webpage, 
                                             data={'domain': domain, 'users': data})    
                
                # Create domain Playbook and Envs folders
                playbookDomainPath = f'{GlobalVars.playbooks}/DOMAIN={domain}'
                envDomainPath = f'{GlobalVars.envPath}/DOMAIN={domain}'
                                    
                if os.path.exists(playbookDomainPath) is False:
                    mkdir(playbookDomainPath, user=GlobalVars.user, stdout=False)
                    chownChmodFolder(playbookDomainPath, GlobalVars.user, GlobalVars.userGroup, permission=770)
                    
                if os.path.exists(envDomainPath) is False:
                    mkdir(envDomainPath, user=GlobalVars.user, stdout=False)
                    chownChmodFolder(envDomainPath, GlobalVars.user, GlobalVars.userGroup, permission=770)
                
        except Exception as errMsg:
            print('\ncreate domain: error:', traceback.format_exc(None, errMsg))
            #raise Exception(errMsg)
                                    
    def delete(self, domain:str):
        try:
            if RedisMgr().redis:
                RedisMgr.redis.deleteKey(f'domain-{domain}')

            DB.name.deleteOneDocument(collectionName=Vars.webpage, fields={'domain': domain})
                
            removeFolder(f'{GlobalVars.envPath}/DOMAIN={domain}', stdout=False)
            removeFolder(f'{GlobalVars.playbooks}/DOMAIN={domain}', stdout=False)
            removeFolder(f'{GlobalVars.resultsFolder}/DOMAIN={domain}', stdout=False)
            removeFolder(f'{GlobalVars.archiveResultsFolder}/DOMAIN={domain}', stdout=False)
                
        except Exception as errMsg:
            raise Exception(errMsg)

    def domainExists(self, domain):
        if RedisMgr.redis.keyExists(key=f'domain-{domain}'):
            return True
        else:
            domainsData = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': domain}, includeFields={'_id':0})
            count = list(domainsData)
            if len(count) == 0:
                return False
            if len(count) > 0:
                return True
                        
    def addNewUserToDomains(self, user: str, domainsAndUserRoles: list=[]):
        """ 
        This is not for adding new user accounts.
        This is for moodifying: Add domains with domain user-roles to the user's account
        
        users: userFullName
        domainsAndUserRoles: [[domain1, userRole], [domain2, userRole]] 
        """ 
        try:
            if RedisMgr.redis:
                for domain, userRole in domainsAndUserRoles:
                    domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
                    if user not in domainData.keys():
                        userIsSysAdmin = AccountMgr().isUserSysAdmin(user)
                        if userIsSysAdmin:
                            domainUserRole = 'admin'
                        else:
                            #domainUserRole = user[1]
                            domainUserRole = userRole

                        domainData.update({user: {'userRole': domainUserRole, 'userIsSysAdmin': userIsSysAdmin}})
                        
                    RedisMgr.redis.updateKey(keyName=f'domain-{domain}', data=domainData)
 
            # Update MongoDB too
            for domain, userRole in domainsAndUserRoles:
                domainsData = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain': domain})
                if user not in domainsData['users'].keys():
                    userIsSysAdmin = AccountMgr().isUserSysAdmin(user)

                    if userIsSysAdmin:
                        domainUserRole = 'admin'
                    else:
                        domainUserRole = user[1]

                    domainsData['users'].update({user: {'userRole': userRole, 'domainUserRole': userIsSysAdmin}})
                
                    DB.name.updateDocument(collectionName=Vars.webpage, 
                                            queryFields={'domain': domain}, 
                                            updateFields={'users': domainsData['users']})
        except Exception as errMsg:
            pass

    def addUsersToDomains(self, users: list, domains: list):
        """ 
        This is not for adding new user accounts.
        This is for moodifying: Add domains with domain user-roles to the user's account
        
        users: [[userFullName, domainUserRole], [] ...]
        domains: [domain1, domain2] 
        """ 
        try:
            if RedisMgr.redis:
                for domain in domains:
                    domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
                    for user in users:
                        userFullName = user[0]
                        userIsSysAdmin = AccountMgr().isUserSysAdmin(userFullName)
                        if userIsSysAdmin:
                            domainUserRole = 'admin'
                        else:
                            domainUserRole = user[1]
                            
                        domainData.update({userFullName: {'userRole': domainUserRole, 'userIsSysAdmin': userIsSysAdmin}})
                        
                    RedisMgr.redis.updateKey(keyName=f'domain-{domain}', data=domainData)
 
            for domain in domains:
                domainsData = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain': domain})
                for user in users:
                    userFullName = user[0]
                    userIsSysAdmin = AccountMgr().isUserSysAdmin(userFullName)

                    if userIsSysAdmin:
                        domainUserRole = 'admin'
                    else:
                        domainUserRole = user[1]

                    domainsData['users'].update({userFullName: {'userRole': domainUserRole, 'userIsSysAdmin': userIsSysAdmin}})
                    
                DB.name.updateDocument(collectionName=Vars.webpage, 
                                        queryFields={'domain': domain}, 
                                        updateFields={'users': domainsData['users']})
        except Exception as errMsg:
            pass
        
    def removeUsersFromDomains(self, users: list, domains: str):
        """ 
        Remove domains from user accounst
        
        users: [userFullName, domainUserRole]
        domains: [domain1, domain2] 
        """ 
        try:
            if RedisMgr.redis:
                for domain in domains:
                    domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
                    for user in users:
                        userFullName = user[0]
                        if userFullName in domainData.keys():
                            del domainData[userFullName] 
                           
                    RedisMgr.redis.updateKey(keyName=f'domain-{domain}', data=domainData)
 
            for domain in domains:
                domainsData = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain': domain})
                # For each domain, remove each user
                for user in users:
                    userFullName = user[0]
                    if userFullName in domainsData['users'].keys():
                        del domainsData['users'][userFullName]
                    
                DB.name.updateDocument(collectionName=Vars.webpage, 
                                       queryFields={'domain': domain}, 
                                       updateFields={'users': domainsData['users']})
        except Exception as errMsg:
            pass
                                               
    def removeUserFromDomain(self, user: str, domains: list):
        if RedisMgr.redis:
            for domain in domains:
                domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
                if user in domainData.keys():
                    if domainData[user]['userIsSysAdmin'] is False:
                        del domainData[user]
                        RedisMgr.redis.updateKey(keyName=f'domain-{domain}', data=domainData)

        for domain in domains:
            data = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': domain}, includeFields={'_id':0})
            count = list(data)
            if len(data) > 0:
                for domainsData in data:
                    if user in domainsData['users'].keys():
                        if domainsData['users'][user]['userIsSysAdmin'] is False:
                            del domainsData['users'][user]
                            pprint(domainsData['users'])
                            result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                            queryFields={'domain': domain},
                                                            updateFields={'users': domainsData['users']})             
            
    def removeUserFromAllDomains(self, user):
        """ 
        For removing a user account. Remove user from all domains too.
        """
        if RedisMgr.redis:
            domains = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'domain-*')
            for domain in domains:
                domainData = RedisMgr.redis.getCachedKeyData(keyName=domain)

                if user in domainData.keys():
                    del domainData[user]
                    RedisMgr.redis.updateKey(keyName=domain, data=domainData)
  
        domains = DB.name.getDocuments(collectionName=Vars.webpage, fields={}, includeFields={'_id':0})
        countX = domains
        count = list(countX)
        if len(count) > 0:
            for domainsData in domains:
                if user in domainsData['users'].keys():
                    del domainsData['users'][user]

                    result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                    queryFields={'domain': domainsData['domain']},
                                                    updateFields={'users': domainsData['users']}) 
                             
    def updateUserRoleInDomain(self, domain, user, role):
        if RedisMgr.redis:
            domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
            if user in domainData.keys() and domainsData[user]['userIsSysAdmin'] is False:
                domainData[user].update({'userRole': role})
                RedisMgr.redis.updateKey(keyName=f'domain-{domain}', data=domainData[user])
        else:
            domainsData = DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain': domain}, includeFields={'_id':0})
            count = deepcopy(domainsData)
            if len(list(count)) > 0:
                if user in domainsData['users'] and domainsData['users'][user]['userIsSysAdmin'] is False:
                    domainsData['users'][user].update({'userRole': role})

                    result = DB.name.updateDocument(collectionName=Vars.webpage,
                                                    queryFields={'domain': domain},
                                                    updateFields=domainsData['user'][user])
                                                          
    def addUserGroups(self, domain:str, userGroups: list):
        domainsData = readYaml(GlobalVars.domainsFile)
        if RedisMgr:
            redisData = RedisMgr().redis.getCachedKeyData(keyName='domains')
                                
        for userGroup in userGroups:
            if userGroup:
                if userGroup not in domainsData[domain]['userGroups']:
                    domainsData[domain]['userGroups'].append(userGroup)
                
                if RedisMgr().redis:
                    redisData[domain]['userGroups'].append(userGroup)
                          
        if RedisMgr().redis:
            RedisMgr().redis.updateKey(keyName='domains', data=redisData)
           
        writeToYamlFile(domainsData, GlobalVars.domainsFile, retry=5)
        
    def removeUserGroups(self, domain:str, userGroups: list):
        try:
            domainsData = readYaml(GlobalVars.domainsFile)
            if RedisMgr.redis:
                redisData = RedisMgr().redis.getCachedKeyData(keyName='domains')
                
            for userGroup in userGroups:
                if userGroup in domainsData[domain]['userGroups']:
                    index = domainsData[domain]['userGroups'].index(userGroup)
                    domainsData[domain]['userGroups'].pop(index)
                
                if RedisMgr().redis:
                    if userGroup in redisData[domain]['userGroups']:
                        index = redisData[domain]['userGroups'].index(userGroup)
                        redisData[domain]['userGroups'].pop(index)
            
            RedisMgr().redis.updateKey(keyName='domains', data=redisData)
            writeToYamlFile(domainsData, GlobalVars.domainsFile, retry=5)
            domainsData = readYaml(GlobalVars.domainsFile)
            
            failedList = []
            redisFailedList = []
            for userGroup in userGroups:
                if userGroup in domainsData[domain]['userGroups']:
                    failedList.append(userGroup)
            
                if userGroup in redisData[domain]['userGroups']:
                    redisFailedList.append(userGroup)
        except Exception as errMsg:
            print('DeleteUserGroup:', traceback.format_exc(None, errMsg))
            
        if failedList:
            return failedList
        else:
            return []

    # def removeDomainsFromUserAccount(self, userFullName:str, domains:list):
    #     if RedisMgr.redis:
    #         for domain in domains:
    #             domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
    #             if userFullName in domainData.keys():
    #                 del domainData[userFullName]
    #                 RedisMgr.redis.updateKey(keyName=f'domain-{domain}', data=domainData)
                    
                    
    #     data = DB.name.getOneDocument(collectionName='accountMgmt', fields={'fullName': userFullName})
    #     if data:
    #         for domain in domains:
    #             if domain in data['domains'].keys():
    #                 del data['domains'][domain]
        
    #         DB.name.updateDocument(collectionName='accountMgmt', 
    #                                queryFields={'fullName': userFullName}, 
    #                                updateFields={'domains': data['domains']})
                    
    def isUserAllowedInDomain(self, domain:str, user:str):
        if RedisMgr.redis:
            domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
            if user in domainData.keys():
                return True
        else:
            data = DB.name.getOneDocument(collectionName=Vars.webpage, fields={'domain': domain})
            if data:
                if user in data['users'].keys():
                    return True
       
    def getUserGroups(self, domain:str):
        """ 
        Get all user-groups in the domain
        """        
        if RedisMgr().redis:
            data = RedisMgr().redis.getKeyValue(keyName='domains', keys=domain)
            return sorted(data['userGroups'])
        else:
            domainsData = readYaml(GlobalVars.domainsFile)   
            if domain in domainsData:
                return sorted(domainsData[domain]['userGroups'])
            else:
                return []
        
    def getAllDomains(self):
        domainList = []
        if RedisMgr.redis:
            domains = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'domain-*', sort=True)
            for domain in domains:
                domainList.append(domain.split('-')[1])
        else:
            domainsData = DB.name.getDocuments(collectionName=Vars.webpage, fields={}, includeFields={'_id':0})
            domainList = [domain['domain'] for domain in domainsData]
            
        return sorted(domainList)

    def getUserRoleForDomain(self, user, domain):
        """ 
        If user is system admin, automatic admin user-role
        """
        if domain:
            if RedisMgr.redis:
                domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
                if user in domainData.keys():
                    return  domainData[user]['userRole']
            else:
                domainData = DB.name.getDocuments(collectionName=Vars.webpage,
                                                  fields={'domain': domain},
                                                  includeFields={'_id':0})
                
                count = deepcopy(domainData)
                if len(list(count)) > 0:
                    if user in domainData[0]['users'].keys():
                        return  domainData[0]['users'][user]['userRole']

                                                                           
    def getUserAllowedDomains(self, user):
        """ 
        Get all the domains allowed for the user
        """
        domainsAllowedForUser = []    
        if RedisMgr.redis:
            # ['domain-Communal', 'domain-keystackQA', 'domain-yabba']
            domainData = RedisMgr.redis.getAllPatternMatchingKeys(pattern='domain-*')
            for domainKey in domainData:
                data = RedisMgr.redis.getCachedKeyData(keyName=domainKey)
                if user in data.keys():  
                    domainsAllowedForUser.append(domainKey.split('-')[1])
        else:
            domainData = DB.name.getDocuments(collectionName=Vars.webpage,
                                            fields={},
                                            includeFields={'_id':0})
            count = deepcopy(domainData)
            if len(list(count)) == 0:
                return []
            else:
                for domain in domainData:
                    if user in domain['users'].keys():
                        domainsAllowedForUser.append(domain['domain'])
                
        return domainsAllowedForUser
    
    def getUserAllowedDomainsAndRoles(self, user):
        """ 
        Get all the domains allowed for the user and user roles
        """
        domainsAllowedForUser = []    
        if RedisMgr.redis:
            # ['domain-Communal', 'domain-keystackQA', 'domain-yabba']
            domainData = RedisMgr.redis.getAllPatternMatchingKeys(pattern='domain-*')
            for domainKey in domainData:
                data = RedisMgr.redis.getCachedKeyData(keyName=domainKey)
                if user in data.keys():
                    domain = domainKey.split('-')[1]
                    userRole = data[user]['userRole']  
                    domainsAllowedForUser.append((domain, userRole))
        else:
            domainData = DB.name.getDocuments(collectionName=Vars.webpage,
                                            fields={},
                                            includeFields={'_id':0})
            count = deepcopy(domainData)
            if len(list(count)) == 0:
                return []
            else:
                for domain in domainData:
                    if user in domain['users'].keys():
                        domainName = domain['domain']
                        userRole = domain['users'][user]['userRole']
                        domainsAllowedForUser.append((domainName, userRole))
                
        return domainsAllowedForUser
    
    def isUserSysAdmin(self, domain, user):
        if RedisMgr.redis:
            # ['domain-Communal', 'domain-keystackQA', 'domain-yabba']
            domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
            if user in domainData.keys():
                if domainData[user]['userIsSysAdmin']:
                    return True
                else:
                    return False                  
        else:
            domainData = DB.name.getDocuments(collectionName=Vars.webpage,
                                            fields={},
                                            includeFields={'_id':0})
            count = deepcopy(domainData)
            if len(list(count)) == 0:
                return False
            else:
                if user in domain['users'].keys():
                    return domain['users'][user]['userIsSysAdmin']
                                            
    def getAllUsersInDomain(self, domain:str=None):
        """           
        Get all users for adding users to User-Groups & for scheduling
        """
        if domain:
            if RedisMgr.redis:
                # {'Jane Doe': {'userRole': 'director'}}
                domainData = RedisMgr.redis.getCachedKeyData(keyName=f'domain-{domain}')
                usersList = [user for user in domainData.keys()]
                return usersList
            else:
                domainData = DB.name.getDocuments(collectionName=Vars.webpage,
                                            fields={'domain': domain},
                                            includeFields={'_id':0})
                count = deepcopy(domainData)
                if len(list(count)) == 0:
                    return None
                else:
                    usersList = [user for user in domainData[0]['users'].keys()]
                    return usersList                                                                        

    
   
        
        
        
        

