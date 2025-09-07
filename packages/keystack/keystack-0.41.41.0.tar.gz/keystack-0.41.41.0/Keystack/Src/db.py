from ctypes import util
import subprocess, os, time, sys, traceback
from pymongo import MongoClient, errors

#from dotenv import load_dotenv

from django.conf import settings
import keystackUtilities
from globalVars import GlobalVars

# MUST 
#   Be sudo user to run this app
#   Have directory created: /dbRootPath, /dbRootPath/loggingData and /dbRootPath/storageData
#   In /Keystack/keystackSystemSettings, set platform to linux or docker
#      If linux: do systemctl start mongod

class DB:
    # connectToDB.py will update the name when it establishes a mongodb connection
    name = None

    currentDir = os.path.abspath(os.path.dirname(__file__))

    etcKeystackYml = keystackUtilities.readYaml('/etc/keystack.yml')
    if os.path.exists(etcKeystackYml['keystackTestRootPath']) == False:
        raise Exception(f'db.py: keystackTestRootPath path not found: {etcKeystackYml["keystackTestRootPath"]}')
                
    keystackSystemPath = etcKeystackYml['keystackSystemPath']
    keystackTestRootPath = etcKeystackYml['keystackTestRootPath']
    keystackSettings = keystackUtilities.readYaml(GlobalVars.keystackSystemSettingsFile)
    localHostIp =  keystackSettings.get('localHostIp', 'localhost')
    dbLogFile = f"{keystackSystemPath}/Logs/mongodb.log"
    dbIp       = keystackSettings.get('mongoDbIp', 'localhost')
    dbIpPort   = keystackSettings.get('dbIpPort', 27017)
    dbName     = 'Keystack'
    userGroup  = keystackSettings.get('fileGroupOwnership', "Keystack")
        
    if keystackSettings.get('platform') == 'docker':
        dbRootPath = '/data/db'
    else:
        dbRootPath = f'{keystackSystemPath}/MongoDB'
        
"""
To avoid errno 24 can't open file error: set ulimit -n 65000
edit /etc/security/limits.conf and reboot.  This will make all terminals with the same ulimits. Then verify using ulimit -n
https://docs.mongodb.com/manual/reference/ulimit
   * hard nofile 100000
   * soft nofile 100000
   root hard nofile 100000
   root soft nofile 100000

sudo -u hgee mongod --bind_ip 0.0.0.0 --port 27017 --dbpath /opt/KeystackSystem/MongoDB/storageData --logpath /opt/KeystackSystem/MongoDB/loggingData/mongodb.log --pidfilepath /data/db/mongod.pid --fork

Troubleshoot
   Cannont connect to 127.0.0.1:27017
      systemctl daemon-reload
      system start mongod
      sudo mongod --fork .....<the rest of the parameters>

   Can't open PID file:
      If starting mongod using systemctl, edit: /etc/systemd/system/multi-user.target.wants/mongod.service
      PIDFile=/data/db/mongod.pid

   status 14:
      chown mongod.mongod /tmp/mongod-27017.sock
      chown mongod.mongod /var/lib/mongo/mongd.lock

   status 48: 
      another process already using port 27017
      
      sudo lsof -i tcp:27017
      COMMAND  PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
      mongod  1246 mongod   12u  IPv4  34840      0t0  TCP testops:27017 (LISTEN)
[   
    sudo kill -9 1246

   status 38:
      Failed to open /data/db/loggingData/mongodb.log
     
   IP:27017 already in use
      lsof -n -i: To verify if Mongod port and IP already opened and listening
      pkill -9 mongod
    
sudo lsof -i :27017
   COMMAND      PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
   MongoDB     8474 hgee   45u  IPv4 6926519      0t0  TCP dagabah.com:58642->dagabah.com:27017 (ESTABLISHED)
   mongod    393630 root   11u  IPv4 6926503      0t0  TCP *:27017 (LISTEN)
   mongod    393630 root   44u  IPv4 6926520      0t0  TCP dagabah.com:27017->dagabah.com:58642 (ESTABLISHED)

   kill -9 <PID>

#   - If status code = 48, mongodb port 27017 is being used. Kill it.
#   sudo netstat -plten | grep 27017
#   tcp        0      0 127.0.0.1:27017         0.0.0.0:*               LISTEN      974        31328      1102/mongod
#   sudo kill -9 1102

shutdown server cleanly: 
   - mongo
   - use admin  
   - db.shutdownServer()
"""

def writeToLogFile(logMsg):
    if DB.dbLogFile != 'None':
        if os.path.exists(DB.dbLogFile) == False:
            open(DB.dbLogFile, 'w').close()
            keystackUtilities.execSubprocessInShellMode(f'chmod 660 {DB.dbLogFile}')
            keystackUtilities.execSubprocessInShellMode(f'chown :Keystack {DB.dbLogFile}')
            
        detailMsg = f'{keystackUtilities.getDate()} {keystackUtilities.getTime()}: {logMsg}'
        print(f'db.py: {detailMsg}\n')
            
        with open(DB.dbLogFile, mode='a', encoding='utf-8') as msgFile:
            msgFile.write(f'{detailMsg}\n')

def killMongoProcess():
    """ 
    Sometimes mongod port and ip are already opened and listening.
    Use pkill to kill mongod service
    
    Note: Use the following to verify opened ip:port bindings: lsof -n -i
    """

    try:
        writeToLogFile('sudo pkill -9 mongod: Kill all mongod ip:port bindings')
        keystackUtilities.execSubprocess(['sudo', 'pkill', '-9', 'mongod'])
    except:
        pass

        
class ManageDB(object):
    """
    Manage mongod process

    1> systemctl start mongod
    2> Start mongo DB
    """
    verifyMongodLockFileOwnershipFlag = 0
    startDBFlag = 0

    def whoami(self):
        output = subprocess.Popen('whoami', stdout=subprocess.PIPE, shell=True)
        whoami = output.stdout.readline().rstrip().decode('utf-8')
        return whoami
    
    def startDB(self):
        """
        Start Mongod
 
        Returns:
            0 -- If Mongod is running
            1 -- Something went wrong
        """     
        # dbRootPath: /data/db or /KeystackSystem/MongoDB   
        print('\ndb.startDB() dbRootPath:', DB.dbRootPath)         
        if os.path.exists(DB.dbRootPath) == False:
            writeToLogFile(f'startDB() mkdir {DB.dbRootPath}')
            keystackUtilities.execSubprocess(['mkdir', DB.dbRootPath])
            keystackUtilities.execSubprocess(['mkdir', f'{DB.dbRootPath}/storageData'])
            keystackUtilities.execSubprocess(['mkdir', f'{DB.dbRootPath}/loggingData'])
            
            if DB.userGroup is None:
                DB.userGroup = self.whoami()

        self.verifyMongodLockFileOwnership()
        mongodProcess = False
        for counter in range(3):
            # Verify systemctl status mongod
            if self.verifyMongodStatus() == False:
                self.startMongodProcess()
                time.sleep(1)
            else:
                mongodProcess = True
                break
            
        if mongodProcess == False:
            writeToLogFile(f'startDB() Tried to start mongod 3x and failed.')
            return False

        if self.verifyMongodProcess(verifyPattern='--fork') == False:
            # Mongod is running.
            self.executeMongod()
        
    def executeMongod(self, debugMode=False):
        # sudo mongod --fork --dbpath /data/db/storageData/ --bind_ip 0.0.0.0 --port 27017 --logpath /data/db/loggingData/mongodb.log --pidfilepath /data/db/mongod.pid
        if debugMode == False:
            command = 'mongod --fork'
        else:
            command = 'mongod'
            
        command += f" --dbpath {DB.dbRootPath}/storageData "
        command += f"--bind_ip {DB.dbIp} --port {DB.dbIpPort} "
        command += f"--logpath {DB.dbRootPath}/loggingData/mongodb.log "
        command += f"--pidfilepath {DB.dbRootPath}/mongod.pid"
        
        if self.whoami() != 'root':
            command = f'sudo {command}'
        
        writeToLogFile(f'executeMongod() Starting mongo DB process:\n\t--> {command} <--')
        result, stdout = keystackUtilities.execSubprocess(command.split(' '))

        if type(stdout) == bytes:
            stdout = stdout.decode('utf-8')

        writeToLogFile(stdout)
        if debugMode:
            sys.exit(1)
            
        if self.verifyMongodProcess(verifyPattern='mongod --fork') == False:
            writeToLogFile('executeMongod() Starting mongod process failed.  Trying again without --fork ...')
            self.executeMongod(debugMode=True)
            
            if self.verifyMongodLockFileOwnership() == False:
                if ManageDB.startDBFlag == 0:
                    ManageDB.startDBFlag = 1
                    writeToLogFile('executeMongod() Executing startDB() again ...')
                    self.startDB()
                else:
                    return 1
        else:
            writeToLogFile("executeMongod() Verifying /tmp/mongodb-27017.sock is owned by mongod")
            if self.verifyMongodLockFileOwnership() == False:
                return 1

            return 0
        
        if 'ERROR' in stdout:
            writeToLogFile(f'{stdout}Do you have root or sudo privilege? Don\'t use localhost. Try using actual IP.')
            return 1

    def shutdownDB(self):
        """
        Graceful Mongod shutdown

        Returns:
            None -- No error
            1 -- Error
        """
        if self.verifyMongodProcess(verifyPattern='mongod --fork'):
            command = f"mongod --shutdown --dbpath {DB.dbRootPath}/storageData"
            if self.whoami() != 'root':
                command = f'sudo {command}'
            
            writeToLogFile(f'Shutting down mongod process: {command}')
            result, stdout = keystackUtilities.execSubprocess(command.split(' '))
            if type(stdout) == bytes:
                stdout = stdout.decode('utf-8')

            # Close all mongod ip:port bindings
            keystackUtilities.execSubprocess(['pkill', '-9', 'mongod'])
            
            writeToLogFile(f'stdout: {stdout}')
            if 'killing process with pid' not in stdout:
                writeToLogFile('Failed: Shutdown failed')
                return 1
            else:
                return 0

        else:
            writeToLogFile('shutdownDB: Mongod is not running. No need to shut it down.')
            return 0
   
    def restartDB(self):
        result = 0
        writeToLogFile('restartDB')
        if self.verifyMongodProcess(verifyPattern='mongod --fork'):
            result = self.shutdownDB()

        if result == 0:
            self.startDB()

    def verifyMongodProcess(self, verifyPattern):
        """
        mongo --fork ... 
        """
        writeToLogFile(f'VerifyMongodProcess: whoami: {self.whoami()}')
        psCommand = 'ps -ef | grep mongod'
        writeToLogFile(f'Verifying mongod process: Entering: {psCommand}')
        stdout1 = subprocess.Popen(psCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout = stdout1.communicate()
        
        print('\ndb: VERIFYING PATTERN:', verifyPattern)
        mongoProcessFlag = False
        for line in stdout:
            if type(line) is bytes:
                line = line.decode('utf-8')
            
            if line:
                writeToLogFile(f'\nstdout: {line}')
            
            if verifyPattern in line:
                mongoProcessFlag = True
                break

        if mongoProcessFlag:
            writeToLogFile('VerifyMongodProcess: MongoDB process is started')
            return True
        else:
            writeToLogFile('VerifyMongodProcess: MongoDB process is not started')
            return False
                
    def startMongodProcess(self):
        killMongoProcess()
        
        psCommand = 'systemctl start mongod'
        if self.whoami() != 'root':
            psCommand = f'sudo {psCommand}'
        
        writeToLogFile(f'startMongodprocess: {psCommand}')
        stdout1 = subprocess.Popen(psCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout = stdout1.communicate()

    def verifyMongodStatus(self):
        psCommand = 'systemctl status mongod'
        if self.whoami() != 'root':
            psCommand = f'sudo {psCommand}'
        
        writeToLogFile(f'verifyMongodStatus: {psCommand}')
        stdout1 = subprocess.Popen(psCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout = stdout1.communicate()

        for line in stdout:
            if type(line) is bytes:
                line = line.decode('utf-8')
            
            if line:
                writeToLogFile(f'stdout: {line}')
            
            if 'Active: active (running)' in line:
                return True

            if 'Active: inactive (dead)' in line:
                return False

        return False
    
    def verifyMongodLockFileOwnership(self):
        psCommand = 'ls -l /tmp/mongodb-27017.sock'
        if self.whoami() != 'root':
            psCommand = f'sudo {psCommand}'
            
        writeToLogFile(f'verifyMongodLockFileOwnership: {psCommand}')
        stdout1 = subprocess.Popen(psCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        stdout = stdout1.communicate()

        noSuchFile = False
        mongoProcessFlag = False
        for line in stdout:
            if type(line) is bytes:
                line = line.decode('utf-8')
            
            if line:
                writeToLogFile(f'stdout: {line}')
            
            if 'mongod mongod' in line:
                mongoProcessFlag = True
                break

            if 'cannot access' in line:
                noSuchFile = True
                break

        if noSuchFile:
            writeToLogFile('Passed: File doesn\'t exists: /tmp/mongodb-27017.sock')
            return True
        
        if mongoProcessFlag:
           writeToLogFile('Passed: /tmp/mongodb-27017.sock is owned by mongod')
           return True

        if ManageDB.verifyMongodLockFileOwnershipFlag == 0:
            ManageDB.verifyMongodLockFileOwnershipFlag = 1

            # Change owner and group
            psCommand = 'chown mongod: /tmp/mongodb-27017.sock'
            
            # Docker runs as root user. Don't run as sudo in this case.
            if self.whoami() != 'root':
                psCommand = f'sudo {psCommand}'
            
            writeToLogFile(f'/tmp/mongodb-27017.sock is not owned by mongod. Changing ownership: {psCommand}')
            stdout1 = subprocess.Popen(psCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout = stdout1.communicate()
            
            self.verifyMongodLockFileOwnership()
        else:
            writeToLogFile("Failed to change file ownership to mongod: /tmp/mongod-27017.sock")
            return False
        

def retry(func):
    """
    Creating a connection retry decorator.
    """
    def retryMongo(*args, **kwargs):
        for attempt in range(3):
            try:
                return func(*args, **kwargs)
            except errors.AutoReconnect as errMsg:
                writeToLogFile(f'\n\nretryMongo: MongoDB AutoConnect Error: {errMsg}.\nRetrying dbMgmt.restartDB {attempt}/10 attempts\n\n')

                ManageDB().restartDB()
                time.sleep(2)

        print('\ndb error: MongoDB reconnect retries exhausted 3x')

    return retryMongo


class ConnectMongoDB:
    """ 
    Usage:
        import db
        dbName  = db.ConnectMongoDB(ip=keystackSettings.get('keystack_mongoDbIp', 'localhost'),
                                    port=keystackSettings.get('keystack_dbIpPort', 27017)),
                                    dbName=db.DB.dbName)
        db.DB.name = dbName
    """
    def __init__(self, ip=None, port=27017, dbName=None, collectionName=None):        
        try:         
            # connectTimeoutMS=1000,   
            writeToLogFile(f'\nConnectMongoDB() {ip}:{port} dbName={dbName}')
            self.mongoClient = MongoClient(f'mongodb://{ip}:{port}',
                                           serverSelectionTimeoutMS=10000,
                                           maxPoolSize=100, waitQueueTimeoutMS=10000)            

            self.mongoClient.server_info()
            
        except errors.ConnectionFailure as errMsg:
            msg = f'\ndb: Mongod ConnectionFailure: {errMsg}\n\n  Restarting mongod...\n'
            writeToLogFile(f'\n\ndb: ConnectionFailure errMsg: {traceback.format_exc(None, msg)}\n\n')
            raise Exception(errMsg)

        except errors.ServerSelectionTimeoutError as errMsg:
            msg = f'\ndatabaseQuery: Mongod serverSelectionTimeoutError: {traceback.format_exc(None, errMsg)}'
            writeToLogFile(msg)
            raise Exception(msg)

        except Exception as errorMsg:
            msg = f'\nMongod failed to start: {traceback.format_exc(None, errorMsg)}'
            writeToLogFile(msg)
            raise Exception(f'\nMongod failed to start: {msg}')

        self.dbName = self.mongoClient[dbName]
        self.db = self.mongoClient[dbName]

        writeToLogFile(f'\ndb.py.ConnectMongoDB(): Connected to MongoDB: {dbName} -> {ip}')

    @retry
    def insertOne(self, collectionName=None, data=None):
        """ 
        Returns True = success.  False = failed
        """
        collection = self.dbName[collectionName]
        
        try:
            result = collection.insert_one(data)
            if result.acknowledged:
                return result
            
        except Exception as errMsg:
            writeToLogFile(f'insertOne(): Error: {traceback.format_exc(None, errMsg)}')
            return errMsg

    @retry
    def insertMany(self, collectionName=None, data=None):
        collection = self.dbName[collectionName]

        try:
            result = collection.insert_many(data)
            if result.acknowledged:
                return result
            else:
                raise Exception(f'insertMany: collection={collectionName} {data}')

        except Exception as errMsg:
            return writeToLogFile(f'insertMany() {traceback.format_exc(None, errMsg)}')
    
    @retry
    def getCollection(self, collectionName):
        return self.dbName[collectionName]

    @retry
    def getAllCollections(self):
        """ 
        Domains are Collections 
        """
        collections = self.dbName.list_collection_names()

        # if 'Global_Domain' not in collections:
        #     collections.insert(0, 'Global_Domain')

        # Remove some built-in collections from the list
        removeBuiltInCollections = ['Logs', 'InventoryLogs', 'Playlist', 'PlaylistLogs', 'TestcaseData']
        for builtInItem in removeBuiltInCollections:
            if builtInItem in collections:
                collections.remove(builtInItem)

        return collections

    @retry
    def isCollectionExists(self, collection):
        """ Domains are Collections """
        flag = False

        if collection in self.getAllCollections():
            flag = True
        else:
            flag = False

        return flag

    @retry
    def deleteCollection(self, collectionName):
        collection = self.dbName[collectionName]
        collection.drop()

    @retry
    def countDocuments(self, collectionName, keyValue, limit=1):
        collection = self.dbName[collectionName]
        count = collection.count_documents(keyValue, limit=limit)
        return count
    
    @retry
    def isDocumentExists(self, collectionName, key=None, value=None, keyValue=None, regex=True):
        """
        For keyValue with regex:
            keyValue={'Group': {'$regex': topologyGroup, '$options': 'i'}})

        Examples:
            # Check if an element exists in the group array
            exists = DB.inventory.isDocumentExists(collectionName='Filters', 
                                                keyValue={f'domain.{currentDomain}.groups': value})
            if exists:
                # Do something
                
            Return
            True:  Topology exists
            False: Topology doesn't exists
        
            # Query for an array key value   
            'suites:' [{'module': 'LoadCore'}, {'module': 'AirMosaic'}]
            keyValue={'suites.module': 'LoadCore'} -> Returns True
            keyValue={'suites.module': 'LoadCore'2} -> Returns False
        """
        collection = self.dbName[collectionName]
        
        if keyValue:
            if collection.count_documents(keyValue, limit=1):
                return True
            else:
                return False

        else:
            if regex:
                if collection.count_documents({key: {'$regex':value, '$options': 'i'}}, limit=1) > 0:
                    return True
                else:
                    return False
            else:
                if collection.count_documents({key: value}, limit=1) > 0:
                    return True
                else:
                    return False

    @retry           
    def getDistinct(self, collectionName, fieldName):
        """
        Query all documents in a collection for a field and return
        a list of distinctive values without empty strings.
        """
        collection = self.dbName[collectionName]
        documents = collection.distinct(fieldName)
        while ('' in documents):
            documents.remove('')
            
        return documents
    
    @retry           
    def getOneDocument(self, collectionName, fields, includeFields=None):
        """
        Get documents based on the fields.

        Parameters:
           fields Ex 1:  {'FullName': value}
           
           # Query all documents with multiple values
           fields Ex 2:  {'domain':domain, 'deviceType': {'$in': ['layer1 switch', 'layer2 switch', 'linux']}}
           
           includeFields: {'_id':0, 'Group':1}
                          IMPORTANT: Must include all fields with either 0 or 1.
                                     If only one field is include, then some fields values might be empty
        """
        collection = self.dbName[collectionName]
        try:
            if includeFields is None:
                document = collection.find_one(fields)
            else:
                document = collection.find_one(fields, includeFields)
        except Exception as errMsg:
            return errMsg
        
        return document
                
    @retry                
    def getDocuments(self, collectionName, fields, includeFields=None, sortBy=None, limit=None):
        """
        Get documents based on the fields.

        Parameters:
           fields Ex 1:  {'FullName': value}
           
           # Query all documents with multiple values
           fields Ex 2:  {'domain':domain, 'deviceType': {'$in': ['layer1 switch', 'layer2 switch', 'linux']}}
           
           includeFields: {'_id':0, 'DT_RowId': 0}  <- Use 0 to exclude and 1 to include
                          IMPORTANT: Must include all fields with either 0 or 1.
                          If only one field is include, then some fields values might be empty
                                     
           sortBy: Sort numerically or alphatically by input.
                   Ex 1: [(keyName, 1), (keyName2, -1)]
                   Ex 2: [(keyName, 1)] <- This will sort alphabetically
                   
           limit: Get total amount of documents

        Usage:
            controllerData = DB.name.getDocuments(collectionName='controllers',
                                                  fields={'controller': controllerIp})
                                                  
            # To check if the document is empty:
                if len(list(controllerData)) > 0
                
            if len(list(controllerData)) > 0:
                 # Data is in index[0]
                 controllerData[0]['apiKey']
                 
        Example:
            userData = userAccountDB.getDocuments({'LoginName':loginName}, {'_id':0, 'DT_RowId': 0})[0]

            # Get all the Groups that is not None
            DB.topologies.getDocuments(collectionName=currentDomain, fields={'Group': {'$ne': None}},
                                       includeFields={'_id':0, 'Group':1}, sortBy=[('Group',1)])

            # Query all documents for a field name and return all the values.
            DB.inventory.getDocuments(collectionName=currentDomain,fields={}, includeFields={'Group':1, '_id':0})

            # Return all PlayName: <value>, exclude _id and return in alphabetic order
            DB.dbName.getDocuments(collectionName='Playlist', fields={}, includeFields={'_id':0, 'PlayName':1}, sortBy=[('PlayName', 1)])

            # OR
            db.customers.find({$or: [{Country: "Germany"}, {Country: "France"}]})

            # AND and OR
            db.customers.find({$and: [{$or: [{"Country": "Germany"}, {"Country": "France"}]}, {VIP: true}]})

            # Not equal
            Query docuemnts !=: db.customers.find({Country: {$ne: "Germany"}})
            
            # But since a country is bound to have multiple customers younger than 30 we would get an unnecessarily long list with repeated countries.
            # Use the distinct function:
            Query documents <:  db.customers.distinct("Country",{age: {$lt: 30}})
            Query documents elemtn in a list: db.customers.find({"Country": { $in: ["Germany", "France"] } })

            # Find two keys values in a array of dicts
            db.collection.find({"waitList": { $elemMatch: { name: "x", value: "1" } }})

            # Continue from above using OR 
            db.collection.find({$or: [{ "waitList": { $elemMatch: { name: "x", value: "1" } } },
                                      { "waitList": { $elemMatch: { name: "y", value: "2" } } } ]})

            # Continue from above using AND
            db.collection.find({$and: [{ "waitList": { $elemMatch: { name: "x", value: "1" } } },
                                       { "waitList": { $elemMatch: { name: "y", value: "2" } } }  ]})

            # files: [{'xyz': 1}, ...]
            db.test.find({'files.xyz': {'$exists': 1}})

            # Remove all the docs containing xyz keys from an array of dict
            db.test.update({'files.xyz': {'$exists': 1}},
                           {'$pull': {'files': {'xyz': {'$exists': 1}}}}, multi=True)
            
            # query a key within a key (dict in dict) -> Returns all documents that has keyname in domains
            # fields = {f'domains.{keyname}': {'$exists': 1}}
                           
            len(list(userData)): 0=No document found. 1=document found
            # Query for all the docs for the 'name' field with different values
            DB.name.getDocuments(collectionName=Vars.webpage, fields={'domain':domain, 'name': {'$in': ['device1', 'device2']}} 
               
        Usage:
            if len(list(dbObj)) == 0:
               # Do something
           
        """
        collection = self.dbName[collectionName]
        
        try:
            if includeFields:
                if sortBy:
                    allDocuments = collection.find(fields, includeFields).sort(sortBy)
                else:
                    allDocuments = collection.find(fields, includeFields)
            else:
                if sortBy:
                    allDocuments = collection.find(fields).sort(sortBy)
                else:
                    allDocuments = collection.find(fields)
                
        except Exception as errMsg:
            writeToLogFile(f'getDocuments() {traceback.format_exc(None, errMsg)}')
            return None
        
        if limit:
            return allDocuments.limit(limit)
        else:
            return allDocuments

    @retry    
    def getAllDocuments(self, collectionName, includeFields=None, sortBy=None):
        """
        query documents by indicating which field to include and exclude

        Parameter
           includeFields: This returns the specified includeFields. All other fields are excluded.
                          For each field, specify 0 or 1: Ex:  0=excludeTheField or 1=includeTheField

           sortBy: Ex 1: [(keyName, 1), (keyName2, -1)]
                   Ex 2: [(keyName, 1)] <- This will sort alphabetically

        includeFields usage example:
           accounts = self.userAccountDB.getAllDocuments(includeFields={'_id':0}, sortBy=[('FullName',1)])

           topologyObj = self.collection.find({}, {'_id':0, 'TopologyName': 1})
           # Excludes _id field
           Returns: [{'TopologyName': 'Training'}, {'TopologyName': 'Sales'}, {'TopologyName': 'ProductManagement'}]

        Examples:
            userGroupDB = DB.accountMgmt.getAllDocuments(collectionName='UserGroups',
                                                         includeFields={'_id':0, 'users':0},
                                                         sortBy=[('userGroup', 1)])
        
            userGroupSortedList = [{'label': "Select", "value": None}]
            for userGroup in userGroupDB:
                userGroupSortedList.append({'label': userGroup['userGroup'], 'value': userGroup['userGroup']})
                
        
            controllerData = db.DB.name.getAllDocuments(collectionName=GlobalVars.webpage, includeFields={})
            # To check if the document is empty:
                if len(list(controllerData)) > 0
                    
            if len(list(controllerData)) > 0:
                # do something
        """
        collection = self.dbName[collectionName]
                        
        if includeFields:
            if sortBy:
                return collection.find({}, includeFields).sort(sortBy)
            else:
                return collection.find({}, includeFields)
        else:
            if sortBy:
                return collection.find({}).sort(sortBy)
            else:
                return collection.find({})

    @retry
    def getDates(self, collectionName, unwind=None, match=None):
        """
        unwind: The key to the list of dates.  Ex: "$usage"
        match:  The query: {"env":env, 'usage.date': {'$gte': ISODate("2011-05-01") }
        """
        collection = self.dbName[collectionName]
        
        # Find matching documents (would benefit from an index on `{uid: 1}`)
        # Unpack the "usage" array
        # Find the assignments ending after given date
        return collection.aggregate([{'$match': match}])
        
    @retry
    def removeKeyFromDocument(self, collectionName, queryFields, updateFields):
        """ 
        Given: 'sessions': {'10-8-2022': [x,y,z]}
        
        # Removes the '10-8-2022'  field from 'sessions'
        results = DB.name.removeKeyFromDocument(collectionName='logs', 
                                                queryFields={'_id': 'sessions'},
                                                updateFields={"$unset": {f'sessions.{recordedDate}': 1}})
        
        results: {'n': 1, 'nModified': 1, 'ok': 1.0, 'updatedExisting': True}
        
        # Delete 'sessions' and everything beneath it
        result = DB.name.removeKeyFromDocument(collectionName='logs',
                                               queryFields={'_id': 'sessions'}, 
                                               updateFields={'$unset': {'session': {recordedDate: 1}}})
                               
        """
        collection = self.dbName[collectionName]
        
        # Use update for single document.
        # Use updateMany for all documents
        result = collection.update_one(queryFields, updateFields)
            
        return result
        
    @retry
    def updateDocument(self, collectionName, queryFields, updateFields, removeKey=False, multi=False, appendToList=False, 
                       appendListToList=False, removeFromList=False, upsert=False):
        """
        Update one or all documents. This could also replace entire array with new array.

        Handling Document Existence (Upsert):
        When the entire document might not exist, and the operation should either insert a 
        new document or update an existing one, the upsert: true option is used with updateOne or replaceOne.

        To update all documents:
           - Set queryFields={}. This will match every record.
           - Set multi:True. Otherwise, only the first matching document will be updated.

        Parameters:
           query: The field(s) to query
           update: The field(s) to update
           appendToList: Append items to a list
           appendListToList: Append a list of items to a list
           removeFromList: Remove an item from a list
           multi: True|False.  True for updating multiple records.
           upsert: True|False  True=Create the object if not exists.
                               This doesn't always work for some situations.
                               Creating a parameter to handle some situation where it is needed.

        Examples:
           # Remove a key and array object:

           # To remove a key from existing key:
           updateFields={ $unset: { "details.awards": "" } 
           
           # To add new key/value pair to existing key. In this example, Devices is the existing key.
           # Adding {'Domains': 'keysight'}
           DB.topologies.updateDocument(queryFields={'TopologyName': topologyName},
                                        updateFields={'$set': {'Devices.Domains': 'keystack'}})
                                        
           DB.topologies.updateDocument(queryFields={'_id': id}, updateFields={'$set': updateFields})

           DB.topologies.updateDocument(queryFields={'TopologyName': topologyName},
                                        updateFields={'$set': {'Devices.Domains': {selectedDomain: []}}})

           # Append to list
           DB.topologies.updateDocument(queryFields={'TopologyName': topologyName},
                                        updateFields={f'Devices.Domains.{selectedDomain}': device},
                                        appendToList=True)

           DB.accountMgmt.updateDocument(collectionName='UserAccounts',
                                         queryFields={'FullName': fullname},
                                         updateFields={'domains': {'domain': domain, 'level': privilegeLevel}},
                                         appendToList=True)

           # Query for nested key
           result = DB.accountMgmt.updateDocument(collectionName='UserAccounts',
                                                  queryFields={'playbooks.02-22-2022': {'$exists': True}},
                                                  updateFields={'playbooks.02-22-2022': item},
                                                  appendToList=True)
           if result['updatedExisting'] == True:
               # Do something
           else:
              DB.name.insertOne(collectionName='logs', data={webPage: {date: [logData]}})
              
                                         
           # Add element to beginning of the array
           DB.logs.updateDocument(collectionName=self.domain,
                                  queryFields={'typeOfLog': self.typeOfLog},
                                  updateFields={'logs': {'$each': [fields], '$position':0}},
                                  appendToList=True)

           DB.topologies.updateDocument(queryFields={'TopologyName': topologyName},
                                        updateFields={f'Devices.Domains.{domain}': device}, removeFromList=True)

           # Remove a dictionary object from an array on a match in queryFields ($pull examples)
           Ex 1:
             DB.topologies.updateDocument(collectionName=topologyDomain,
                                          queryFields={'$and': [{'TopologyName': topologyName}, {'Reservation-WaitList': {'$elemMatch': {'sessionId': self.mainObj._sessionId}}}]},
                                          updateFields={'Reservation-WaitList': {'sessionId': self.mainObj._sessionId}},
                                          removeFromList=True)
           Ex 2:
              Remove array objects from a list: queryFields={'device': deviceName}, 
                                                updateFields={'$pull': {'ports': {'$in': [item1, item2]}}, removeFromList=True
                                                
            DB.name.updateDocument(collectionName=Vars.envLoadBalanceDB,
                                   queryFields={'name': loadBalanceGroup},
                                   updateFields={f'envs.{eachEnv}': ""}, removeKey=True)

           Ex 3:
              Remove array object from a list
              [{'domin': domainName, 'level': 'Engineer'}, {'domin': domainName, 'level': 'Manager'}]
              DB.accountMgmt.updateDocument(collectionName='UserAccounts',
                                            queryFields={'$and': [{'FullName': fullname}, {'domains': {'$elemMatch': {'domain': domain}}}]},
                                            updateFields={'domains': {'domain': domain}},
                                            removeFromList=True)

           # Match one
           db.collection.find( {
              "A": { $elemMatch: { name: "x", value: "1" } }
           })

           # Find documents which have (name:"x", value:"1") or (name:"y", value:"2") in same query:
           db.collection.find( {
              $or: [
                 { "A": { $elemMatch: { name: "x", value: "1" } } },
                 { "A": { $elemMatch: { name: "y", value: "2" } } }
              ]  
           })

           # Find documents which have (name:"x", value:"1") and (name:"y", value:"2") in same query:
           db.collection.find( {
              $and: [
                 { "A": { $elemMatch: { name: "x", value: "1" } } },
                 { "A": { $elemMatch: { name: "y", value: "2" } } }
              ]  
           })

           # Update a dict object in an array
           # domains: [{'domain': 'Global_Domain', 'level': 'admin'}]
           # Must query for a key in the array object.  Then use $ to change the value
           queryFields={'LoginName': loginNameOriginal, 'domains.domain': currentDomain},
           updateFields={f'domains.$.level': privilegeLevel}) == False:

        Return
            result: {'n': 1, 'nModified': 0, 'ok': 1.0, 'updatedExisting': True}
        """
        collection = self.dbName[collectionName]
                 
        try:
            if appendToList:
                # upsert will create the objects if doesn't exists
                if multi:
                    if upsert is False:
                        result = collection.update_many(queryFields, {'$push': updateFields})
                    else:
                        result = collection.update_many(queryFields, {'$push': updateFields}, upsert=True)
                else:
                    if upsert is False:
                        result = collection.update_one(queryFields, {'$push': updateFields})
                    else:
                        result = collection.update_one(queryFields, {'$push': updateFields}, upsert=True)

                # '_UpdateResult__in_client_bulk', '_UpdateResult__raw_result', '_WriteResult__acknowledged', '__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '_raise_if_unacknowledged', 'acknowledged', 'did_upsert', 'matched_count', 'modified_count', 'raw_result', 'upserted_id']

                return result.acknowledged

            if appendListToList:
                # Example: {'device': deviceName}, updateFields={'$push': {'ports': {'$each': [item1, item2...]}}}
                #    upsert: Create the record if doesn't exists
                #    multi:  indicates if all documents matching criteria should be updated rather than just one
                if multi:
                    result = collection.update_many(queryFields, {'$push': updateFields}, upsert=True)
                else:
                    result = collection.update_one(queryFields, {'$push': updateFields}, upsert=True)
                    
                if result.acknowledged:
                    return result.acknowledged
                else:
                    raise Exception(f'updateDocument: collection={collectionName} appendToList={updateFields}')
                
            if removeFromList:
                if multi:
                    result = collection.update_many(queryFields, {'$pull': updateFields})
                else:
                    result = collection.update_one(queryFields, {'$pull': updateFields})
                    
                return result.acknowledged
            
            if removeKey:
                if multi:
                    result = collection.update_many(queryFields, {'$unset': updateFields})
                else:
                    result = collection.update_one(queryFields, {'$unset': updateFields})
                    
                return result.acknowledged
             
            if multi:
                result = collection.update_many(queryFields, {'$set': updateFields})  
            else:        
                #result = collection.update_one(queryFields, {'$set': updateFields}, multi=multi)
                result = collection.update_one(queryFields, {'$set': updateFields})
                
            # Returns True|False
            return result.acknowledged
        
        except Exception as errMsg:
            writeToLogFile(f'updateDocument() {traceback.format_exc(None, errMsg)}')

    @retry
    def deleteOneDocument(self, collectionName, key=None, value=None, fields=None):
        """ 
        Example:
            result = db.DB.name.deleteOneDocument(collectionName=GlobalVars.webpage, key='controller', value=controller)
            if result != True:
                # Do something
        """
        collection = self.dbName[collectionName]

        try:
            if fields is None:
                result = collection.delete_one({key: value})

            if fields:
                result = collection.delete_one(fields)

            if result.acknowledged:
                return result.acknowledged
            else:
                raise Exception(f'deleteOneDocument failed: collection={collectionName} key={key} value={value} fields={fields}')
                
        except Exception as errMsg:
            writeToLogFile(f'deleteOneDocument() {traceback.format_exc(None, errMsg)}')

    @retry
    def deleteManyDocuments(self, collectionName, key, valueList):
        """
        Remove many documents in one query.

        key: The field
        valueList: A list of values. [domain] or [domain, sessionId]

        Example: 
            self.accountDB.deleteManyDocuments(key='UserGroup', valueList=userGroupList)
        """
        collection = self.dbName[collectionName]
        
        try:
            result = collection.delete_many({key: {"$in": valueList}})
            if result.acknowledged:
                return True
            else:
                raise Exception(f'deleteManyDocument: collection={collectionName} key={key} valueList={valueList}')

        except Exception as errMsg:
            writeToLogFile(f'deleteManyDocuments() {traceback.format_exc(None, errMsg)}')

    @retry
    def removeDocument(self, collectionName, fields):
        """
        Removes a single document or all documents that match the criteria

        Usage: removeDocument({'domain': self.domain, 'timestamp': {'$gte':pastDate, '$lte':datetime.now()}})
        """
        collection = self.dbName[collectionName]
        
        try:
            result = collection.remove(fields)
            if result.acknowledged:
                return True
            else:
                msg = f'removeDocument: collection={collectionName} fields={fields}'
                raise Exception(msg)
        except Exception as errMsg:
            writeToLogFile(f'removeDocument() {traceback.traceback.format_exc(None, errMsg)}')
        
    @retry
    def deleteCollection(self, collectionName):
        """
        Must connect to a domain collection first.

        Example:
            db = SessionDatabase(domain='Ixia')
            db.deleteCollection()
        """
        collection = self.dbName[collectionName]
        collection.drop()


if __name__ == "__main__":
    # For debugging locally
    ManageDB().startDB()
    dbName = ConnectMongoDB(ip=DB.dbIp, port=DB.dbIpPort, dbName=DB.dbName)

    #result = dbName.isDocumentExists(collectionName='playbook', 
    #                                        keyValue={f'Hubert.module': 'LoadCore2'})
    
    #esult = dbName.getDocuments(collectionName='playbook', fields={'Hubert.#module': {'$exists':'LoadCore'}})
    result = dbName.getDocuments(collectionName='playbook', fields={}, includeFields={'_id': 0})
    
    for suite in result:
        for suiteName, modules in suite.items():
            for module in modules:
                print('---- module:', module)
    
    
    #print(f'\nDjango settings.py -> import connectToDB: {DB.name}')
    #if DB.name is None:
    #    writeToLogFile('\nConnecting to MongoDB from settings')
    #    import connectToDB
