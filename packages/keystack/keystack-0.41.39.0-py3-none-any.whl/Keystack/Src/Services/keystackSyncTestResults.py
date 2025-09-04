import sys, os, traceback
from time import sleep
from RedisMgr import RedisMgr
from commonLib import  syncTestResultsWithRedis

currentDir = os.path.abspath(os.path.dirname(__file__))
keystackRootPath = currentDir.replace('/Services', '')
sys.path.insert(0, keystackRootPath)

from keystackUtilities import chownChmodFolder, readYaml
from globalVars import GlobalVars

keystackObj = readYaml('/etc/keystack.yml')
keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)

# Ex: /opt/KeystackSystem
keystackSystemPath = keystackObj['keystackSystemPath']
keystackTestPath = keystackObj["keystackTestRootPath"]

class SyncTestResults:
    def __init__(self):
        self.redisObj = None
        self.connectToRedis()
        
    def connectToRedis(self):
        try:
            RedisMgr().connect(host='0.0.0.0', port=keystackSettings.get('redisPort', '6379'))
            if RedisMgr.redis:
                self.redisObj = RedisMgr.redis
                
                self.callSyncTestResultsWithRedis() 
                   
        except Exception as errMsg:
            print('\nkeystackScheduler:SyncTestResults: ConnectToRedis error:', traceback.format_exc(None, errMsg))
            
    def callSyncTestResultsWithRedis(self):
        while True:
            syncTestResultsWithRedis()
            sleep(60)
        
        
SyncTestResults()
                

    
