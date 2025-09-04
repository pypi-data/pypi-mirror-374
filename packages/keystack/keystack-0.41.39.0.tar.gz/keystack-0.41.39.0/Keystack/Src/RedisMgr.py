""" 
REQUIREMENTS
   - pip install redis
   - dnf install -y redis
   - sudo systemctl start redis
"""

import sys
from redis import Redis, exceptions
import json
import traceback
    
""" 
Notes:
   If docker exists and user runs Keystack on local Linux host CLI,
   redis is not reachable.
   
   For better performance by using redis, run CLI inside Keystack container.
"""


class RedisMgr:
    """ 
    Usage:
        from RedisMgr import RedisMgr
        RedisMgr().connect(host='0.0.0.0', port=os.environ.get('keystack_jiraPort', '6379'))
        if  RedisMgr.redis:
            # Do something
    """
    # Use this across the Keystack app to read/write data
    redis = None
    
    def connect(self, host: str='0.0.0.0', port: int=6379, db: int=0):
        self.redisObj = Redis(host=host, port=port, charset='utf-8', decode_responses=True)  
        if self.pingRedisServer():
            print('\nRedisMgr:connect: success')
            # Share the single Redis instance object for the app
            RedisMgr.redis = self
               
    def pingRedisServer(self):
        result = None
        try:
            result = self.redisObj.ping()
        except Exception as errMsg:
            print(f'\nRedisMgr():pingRedisServer() failed: {errMsg}')

        if result:
            if RedisMgr.redis is None:
                RedisMgr.redis = self
            return True
        else:
            RedisMgr.redis = None
            return False

    def keyExists(self, key):
        ''' 
        Returns 0|1
        '''
        result = self.redisObj.exists(key)
        if result == 0:
            return False
        else:
            return True

                
    def write(self, keyName: str, data: dict) -> bool:
        """ 
        Writing data in redis uses json.dumps to convert dict to string
        """
        if RedisMgr.redis is None:
            return False
   
        return self.redisObj.set(keyName, json.dumps(data))
      
    def getAllKeyNames(self) -> list:
        """
        Get all the redis DB key names
        
        Returns a list []
        """
        return self.redisObj.keys()

    def getAllKeys(self, keyName: str) -> list:
        """ 
        Get all the root level keys from a redis key
        
        Returns a list
        """
        data = self.getCachedKeyData(keyName=keyName)
        if data:
            return list(data.keys())
        else:
            return []

    def getAllPatternMatchingKeys(self, pattern:str, sort=True) -> list:
        """ 
        pattern require including "*"
        
        Returns:
           list: ['overallSummary-domain=Communal-04-12-2024-10:47:42:071439_7124',
                  'overallSummary-domain=Communal-04-12-2024-10:53:40:872379_1008']
        """
        if RedisMgr.redis:
            if sort:
                return sorted([key for key in self.redisObj.scan_iter(pattern)])
            else:
                return [key for key in self.redisObj.scan_iter(pattern)]
        else:
            return []
          
    def getCachedKeyData(self, keyName:str, isJson=True):
        """
        Get all the data from a key and return it as a dict object
        
        Returns: {} | dict object
        """
        # Convert the string object to dict object
        if RedisMgr.redis:
            data = self.redisObj.get(keyName)
            if data:
                if isJson:
                    return json.loads(data)
                else:
                    return data
            else:
                return {}
        else:
            print('\nRedisMgr():getCachedKeyData: redisServer is not alive')
            
    def getKeyValue(self, keyName: str, keys: str, default=None):
        """ 
        Get nested dict object value.
        
        Params:
           - keyName: The redis name used for saving the cached data
           - keys: A string in dotted notation.
                   For example: car.1=keyName, keys='model.trim'
                                This returns the value toyota
                   
                    car = {"colour":"blue",
                           "make":"toyota",
                           "model": {
                               "trim" : "supra",
                               "name" : 93
                           },
                           "features": [ "powerlocks", "moonroof" ]
                        }
                        
        Returns: None | value 
        """
        from functools import reduce
        
        data = self.getCachedKeyData(keyName)
        
        # Convert string to dict
        deepData = reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), data)
        if deepData:
            return deepData
          
    def updateKey(self, keyName: str, data: dict) -> bool:
        """ 
        First, call self.getCachedKeyData(key='car.1') to get the the current data of a key.
        Update the dict object as you normally do.
        Then use this function to rewrite the redis key with replacement data.
        
        Params
           keyName: The redis key name used for saving the cached data
           data: The entire object
           
        Returns True|False
        """
        return self.write(keyName, data)
    
    def appendStringValue(self, keyName, stringValue):
        self.redisObj.append(keyName, stringValue)
        
    def deleteKey(self, keyName: str) -> int:
        """ 
        Returns 0|1
        """
        return self.redisObj.delete(keyName)
    
    def deleteMatchingPatternKeys(self, pattern):
        """ 
        pattern must include "*"
        
        redis-cli --scan --pattern "pipeline*" | xargs redis-cli del
        """
        for key in self.redisObj.scan_iter(pattern):
            self.redisObj.delete(key)

         
if __name__ == '__main__':
    car = {"colour":"blue",
           "make":"saab",
           "model": {
               "trim" : "aero",
               "name" : 93
           },
           "features": [ "powerlocks", "moonroof" ]
          }
          
    redisObj = RedisMgr()
    redisObj.connect()
    
    print('\n--- writing 1:', car)
    redisObj.write(keyName='car.1', data=car)
    
    print('----- getKey:', redisObj.redisObj.get('car.1'))

    car['features'].pop(1)
    print('\n--- updating:', car)
    redisObj.updateKey('car.1', car)
    
    car = redisObj.getCachedKeyData(keyName='car.1')
    print('\n--- get:', type(car), car)
    
    result = redisObj.getKeyValue('car.1', 'features')
    print('\n--- result:', result, type(result))
    