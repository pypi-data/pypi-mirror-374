import os, sys
import threading
import json 
import traceback
from time import sleep

from RedisMgr import RedisMgr
from globalVars import GlobalVars
from keystackUtilities import readYaml, execSubprocessInShellMode
from commonLib import getHttpIpAndPort, isKeystackUIAlive

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)


class MonitorDevices:
    def __init__(self):
        self.redisObj = None
        self.restApiObj()
        self.connectToRedis()
 
    def restApiObj(self):
        keystackHttpIpAddress, keystackIpPort = getHttpIpAndPort()
        
        isKeystackUIExists = isKeystackUIAlive(ip=keystackHttpIpAddress,
                                               port=keystackIpPort,
                                               timeout=3,
                                               keystackLogger=None)
        if isKeystackUIExists[0] is False:
            sys.exit()
               
    def connectToRedis(self):
        try:
            RedisMgr().connect(host='0.0.0.0', port=keystackSettings.get('redisPort', '6379'))
            if RedisMgr.redis:
                self.redisObj = RedisMgr.redis
                
        except Exception as errMsg:
            print('\nkeystackMonitorDeviceStatus: ConnectToRedis error:', traceback.format_exc(None, errMsg))
            
    def closeRedisConnection(self):
        if self.redisObj:
            self.redisObj.redisObj.close()

    def readRedisEnvMgmt(self, keyName):
        if RedisMgr.redis:
            return RedisMgr.redis.getCachedKeyData(keyName=keyName)
        
    def readRedisTaskSummaryData(self, keyName):
        if RedisMgr.redis:
            return RedisMgr.redis.getCachedKeyData(keyName=keyName)

        # If users using the CLI, the redis task-summary-data needs to be transferred to redis in Docker
        if self.isFromKeystackUI is False and self.isKeystackAlive:
            # restapi to call the webUI to write to redis
            params = {'keyName': keyName, 'webhook': True}
            response = self.execRestApiObj.post(restApi='/api/v1/redis/readTaskSummaryData', params=params, showApiOnly=True)
            if response.status_code == 200:
                return response.json()['data']
            
            return {}
                    
    def updateStatus(self):
        """ 
        Get all the current scheduler-add-* from redis
        """
        if self.redisObj:
            addCronJobs = self.redisObj.getAllPatternMatchingKeys(pattern='scheduler-add-*', sort=False)
            cronJobData = self.redisObj.getCachedKeyData(keyName='cronjob')
            self.redisObj.deleteKey(keyName='cronjob')
                    
    def removeCron(self):
        if self.redisObj:
            scheduledForRemoval = self.redisObj.getAllPatternMatchingKeys(pattern='scheduler-remove-*', sort=False)
            
            if len(scheduledForRemoval) > 0:
                for cronjob in scheduledForRemoval:
                    self.redisObj.deleteKey(keyName=cronjob)
    
    def getDevices(self):
        pass
        
    def checkDevices(self):
        """ 
        What this does is ping the server with one packet, and greps the output for the
        string " 0% packet loss". (the space before the 0% is important) 
        If the command returns a row, you are connected, otherwise, not connected.
        """
        result = execSubprocessInShellMode('ping -c 1 www.yourtrustedserver.com | grep " 0% packet loss"')
    
    
monitorDevicesObj = MonitorDevices()    
   
while True:
    threadList = []
    # threadObj = threading.Thread(target=schedulerObj.addCron, name=None)
    # threadList.append(threadObj)
    
    threadObj = threading.Thread(target=monitorDevicesObj.check, name=None)
    threadList.append(threadObj)

    for eachThread in threadList:
        eachThread.start()
        
    for eachThread in threadList:
        eachThread.join()
   
    sleep(10)