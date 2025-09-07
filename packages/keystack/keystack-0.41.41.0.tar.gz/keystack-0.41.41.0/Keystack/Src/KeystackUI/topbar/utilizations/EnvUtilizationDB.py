from db import DB
from datetime import datetime, timedelta

class GlobalVars:
    collectionName = 'utilization'

class EnvUtilizationDB:
    """ 
    Tracking env usage and who is using them
    """
    def insert(self, env, user):
        """ 
        datetime.utcnow() will produce:
            date: 2022-11-18T21:48:09.857+00:00
        """
        date = datetime.now()
        
        try:
            # expires in 3 years: 946080000 seconds
            data = {'timestamp': date, 'meta': {'env': env, 'user': user}, 'expireAfterSuccess': 94608000}
            dbObj = DB.name.insertOne(collectionName=GlobalVars.collectionName, data=data)
            
        except Exception as errMsg:
            raise Exception(errMsg)
        
    def queryEnvs(self, env='all', lastDays=None, daysLessThan=None, daysGreaterThan=None):
        """ 
        env: <list>: One or more env to query
        lastDays: <int>: Get the last number of days records
        daysLessThan: <int>: Get a range of timestamps. This is paired with daysGreaterThan.
        daysGreaterThan: <int>: Same as above 
        
        Example:
            env = ['pythonSample', 'hubert']
            self.queryOneEnv(env=env, lastDays=2, daysLessThan=None, daysGreaterThan=None)
        """
        if lastDays:
            # all: <days0  today: >=days1
            days = datetime.now() - timedelta(days=lastDays)

            if env != 'all':
                data = DB.name.getDocuments(collectionName=GlobalVars.collectionName, 
                                            fields={'timestamp': {'$gte': days}, 'meta.env': {'$in': env}},
                                            includeFields={'_id':0, 'expireAfterSuccess': 0},
                                            sortBy=[('timestamp', 1)])
            else:
                data = DB.name.getDocuments(collectionName=GlobalVars.collectionName, 
                                            fields={'timestamp': {'$gte': days}},
                                            includeFields={'_id':0, 'expireAfterSuccess': 0},
                                            sortBy=[('timestamp', 1)])
                                
        if daysLessThan and daysGreaterThan:
            lessThan     = datetime.now() - timedelta(days=daysLessThan)
            greaterThan  = datetime.now() - timedelta(days=daysGreaterThan)
        
            if env != 'all':
                data = DB.name.getDocuments(collectionName=GlobalVars.collectionName, 
                                            fields={'$and': [{'timestamp': {'$lte': lessThan, '$gte': greaterThan}}], 
                                                    'meta.env': env},
                                            includeFields={'_id':0, 'expireAfterSuccess': 0},
                                            sortBy=[('timestamp', -1)])
            else:
                data = DB.name.getDocuments(collectionName=GlobalVars.collectionName, 
                                            fields={'$and': [{'timestamp': {'$lte': lessThan, '$gte': greaterThan}}]},
                                            includeFields={'_id':0, 'expireAfterSuccess': 0},
                                            sortBy=[('timestamp', -1)])
        return data 
           
    def queryOneUser(self, env, user):
        result = DB.name.getDocument(collectionName=GlobalVars.collectionName, 
                                     queryFields={'env': env, 
                                                  'usage': {'user':user,
                                                  'date': {'$gt': datetime(2015, 12, 1) }}})
        count = result.count()
        
    def queryAllUsers(self, env):
        result = DB.name.getDocument(collectionName=GlobalVars.collectionName, 
                                     queryFields={'env': env, 
                                                  'usage': {'date': {'$gt': datetime(2015, 12, 1)}}})
        count = result.count()
        # TODO: parse users and env usage
        
                