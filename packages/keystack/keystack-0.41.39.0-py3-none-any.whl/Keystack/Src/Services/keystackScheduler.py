import os
import threading
import json 
import traceback
from time import sleep

from scheduler import JobSchedulerAssistant
from RedisMgr import RedisMgr
from globalVars import GlobalVars
from keystackUtilities import readYaml

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)

    
class Scheduler:
    def __init__(self):
        self.redisObj = None
        self.connectToRedis()
        
    def connectToRedis(self):
        try:
            RedisMgr().connect(host='0.0.0.0', port=keystackSettings.get('redisPort', '6379'))
            if RedisMgr.redis:
                self.redisObj = RedisMgr.redis
                
        except Exception as errMsg:
            print('\nkeystackScheduler:Scheduler: ConnectToRedis error:', traceback.format_exc(None, errMsg))
            
    def closeRedisConnection(self):
        if self.redisObj:
            self.redisObj.redisObj.close()
            
    def addCron(self):
        """ 
        Get all the current scheduler-add-* from redis
        """
        if self.redisObj:
            addCronJobs = self.redisObj.getAllPatternMatchingKeys(pattern='scheduler-add-*', sort=False)
            if len(addCronJobs) > 0:
                for cronjob in addCronJobs:
                    cronJobData = self.redisObj.getCachedKeyData(keyName=cronjob)
                    JobSchedulerAssistant().createCronJob(cronJobData)
                    self.redisObj.deleteKey(keyName=cronjob)
                    
    def removeCron(self):
        if self.redisObj:
            scheduledForRemoval = self.redisObj.getAllPatternMatchingKeys(pattern='scheduler-remove-*', sort=False)
            
            if len(scheduledForRemoval) > 0:
                for cronjob in scheduledForRemoval:
                    self.redisObj.deleteKey(keyName=cronjob)
        

schedulerObj = Scheduler()
#schedulerObj.addCron()
#schedulerObj.removeCron()

while True:
    threadList = []
    # threadObj = threading.Thread(target=schedulerObj.addCron, name=None)
    # threadList.append(threadObj)
    
    threadObj = threading.Thread(target=schedulerObj.removeCron, name=None)
    threadList.append(threadObj)

    for eachThread in threadList:
        eachThread.start()
        
    for eachThread in threadList:
        eachThread.join()
   
    sleep(1)


