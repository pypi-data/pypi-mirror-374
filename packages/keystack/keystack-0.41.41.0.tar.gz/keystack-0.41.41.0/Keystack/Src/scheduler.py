import os, sys
import traceback
from re import search
from time import sleep
from copy import deepcopy

from keystackUtilities import execSubprocessInShellMode
from globalVars import GlobalVars
from db import DB


class JobSchedulerAssistant():
    def syncCronJobs(self, dbObj: object):
        """
        Sync env and playbook tasks from MongoDB scheduler collection to /etc/crontab
        
        dbObj: DN.name 
        """
        try:
            notFoundJobsInCrontab = []
            
            currentCronJobs = self.getCurrentCronJobs(searchPattern='all')
            envCronJobsSavedInMongoDB = self.getDetailsFromMongoDB(dbObj, 'env')   
            count = deepcopy(envCronJobsSavedInMongoDB)
            if len(list(count)) > 0:
                for cronInMongoDB in envCronJobsSavedInMongoDB[0]['cronJobs']:
                    # {'query': 'env', 'cronJobs': []}
                    # {'cron': '* 1 * * * keystack curl -d "mainController=192.168.28.10:28028&remoteController=192.168.28.10:28028&reservationUser=Hubert Gee&env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml&removeJobAfterRunning=False&release_minute=*&release_hour=1&release_dayOfMonth=*&release_month=*&release_dayOfWeek=*&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X  POST http://192.168.28.10:28028/api/v1/env/reserveEnv', 'notes': ''}
                    
                    if cronInMongoDB['cron'] not in currentCronJobs:
                        notFoundJobsInCrontab.append(cronInMongoDB['cron'])

            playbookCronJobsSavedInMongoDB = self.getDetailsFromMongoDB(dbObj, 'playbook')
            count = deepcopy(playbookCronJobsSavedInMongoDB)
            if len(list(count)) > 0:
                for cronInMongoDB in playbookCronJobsSavedInMongoDB[0]['cronJobs']:
                    if cronInMongoDB['cron'] not in currentCronJobs:
                        notFoundJobsInCrontab.append(cronInMongoDB['cron'])
                                
            if len(notFoundJobsInCrontab) > 0:
                for cron in notFoundJobsInCrontab:
                    execSubprocessInShellMode(f"sudo sed -i -e $'$a\\\n{cron}\\n\\n' /etc/crontab")
                    
            print('JobSchederAssistant:syncCronJobs')
            
        except Exception as errMsg:
            print(f'JobSchedulerAssistant:syncCronJobs error: {traceback.format_exc(None, errMsg)}')

    def addToScheduler(self, dbObj: object, query: str, data: dict):
        """ 
        This function adds to MongoDB under the "schedulder" collection
        
        dbObj: The DB.name object
        query: env|playbook
        data: {'cron': newJob, 'notes': reservationNotes} 
        """
        if dbObj.isCollectionExists('scheduler') is False:
            dbObj.insertOne(collectionName='scheduler', data={'query': query, 'cronJobs':[data]})  
        else:
            if dbObj.isDocumentExists(collectionName='scheduler', key='query', value=query) is False:
                dbObj.insertOne(collectionName='scheduler', data={'query': query, 'cronJobs':[data]}) 
            else:
                dbObj.updateDocument(collectionName='scheduler', queryFields={'query': query}, updateFields={'cronJobs': data}, appendToList=True)
    
    def getDetailsFromMongoDB(self, dbObj: object, queryName: str):
        """ 
        dbObj: The DB.name object
        queryName: env|playbook
        """
        return dbObj.getDocuments(collectionName='scheduler', fields={'query': queryName}, includeFields={'_id':0})
                                                 
    def createCronJob(self, newJob: str):
        """ 
        Add task to /etc/crontab
        """
        # Get the current cron jobs and add the new job to the current cron jobs
        cronJobs = self.getCurrentCronJobs()
        cronJobs.append(newJob)
        
        cronCommandLines = ''
        for cronJob in cronJobs:
            cronCommandLines += f'{cronJob}\n\n'
            
        execSubprocessInShellMode(f"sudo echo '{cronCommandLines}' | sudo tee /etc/crontab", showStdout=False)
                    
    def getCurrentCronJobs(self, searchPattern: str='all'):
        """ 
        Get the as-is /etc/crontab file
        """
        cronlist = []

        if os.path.exists('/etc/crontab'):
            with open('/etc/crontab', 'r') as cronObj:
                currentCron = cronObj.readlines()
        
            for line in currentCron:
                line = line.strip()
                if not line or line == '':
                    continue
                              
                if bool(search('.*SHELL', line)) or bool(search('.*PATH', line)):
                    continue
                            
                if line.startswith('#'):
                    continue
            
                if searchPattern == 'all':
                    cronlist.append(line)
                else:
                    if searchPattern in line:
                        cronlist.append(line)

        return cronlist
     
    def isCronExists(self, searchPattern, min, hour, day, month, dayOfWeek):
        currentCronList = self.getCurrentCronJobs(searchPattern='all')
        if len(currentCronList) == 0:
            return False
        
        for eachCron in currentCronList:
            # eachCron: * 19 * * * keystack curl -d "mainController=192.168.28.10:28028&remoteController=192.168.28.10:28028&user=keystack&sessionId=&playbook=DOMAIN=Communal/Samples/advance&awsS3=False&jira=False&pauseOnError=False&debug=None&domain=Communal&reconfigs=&holdEnvsIfFailed=False&abortTestOnFailure=False&includeLoopTestPassedResults=False&scheduledJob=playbook=DOMAIN=Communal/Samples/advance minute=* hour=19 day=* month=* dayOfWeek=*&removeJobAfterRunning=False&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.10:28028/api/v1/playbook/runPlaybook

            match = search(f' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*{searchPattern}', eachCron)
            if match:
                cronMin       = match.group(1)
                cronHour      = match.group(2)
                cronDay       = match.group(3)
                cronMonth     = match.group(4)
                cronDayOfWeek = match.group(5)

                cronList = [cronMin, cronHour, cronDay, cronMonth, cronDayOfWeek]
                newList  = [min, hour, day, month, dayOfWeek]

                if set(cronList) == set(newList):
                    # Found existing cron
                    return True
     
        return False
        
    def removeCronJobs(self, listOfJobsToRemove, dbObj=None, queryName=None):
        """
        This function is called by envViews.py:DeleteScheduledEnv
        envViews.py:DeleteScheduledEnv removes the cron jobs from MongoDB.by passing in the dbObj
        
        dbObj: DB.name
        queryName: env|playbook
        
        Crontab example: 
            25 12 24 3 * root curl -d "playbook=goody&user=Hubert Gee" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://172.16.1.16:8000/api/playbook
         
        listOfJobsToRemove: <list of dicts>:  
            {'jobSearchPattern': 'playbook=DOMAIN=Communal/Samples/advance', 
             'month': '\\*', 'day': '\\*', 'hour': '21', 'minute': '\\*', 'dayOfWeek': '\\*'}
        """
        
        cronJobs = self.getCurrentCronJobs(searchPattern='all')
        if not cronJobs:
            return
                                         
        for removeJob in listOfJobsToRemove:
            # DeleteScheduledJob: {'jobSearchPattern': 'playbook=DOMAIN=Communal/Samples/advance', 
            #                      'month': '\\*', 'day': '\\*', 'hour': '21', 'minute': '\\*', 'dayOfWeek': '\\*'}
            jobSearchPattern =  removeJob['jobSearchPattern']
            min              =  removeJob["minute"]
            hour             =  removeJob["hour"]
            day              =  removeJob["dayOfMonth"]
            month            =  removeJob["month"]
            dayOfWeek        =  removeJob["dayOfWeek"]
            
            for cronProperty in [{'min':min}, {'hour':hour}, {'dayOfMonth':day}, {'month':month}, {'dayOfWeek':dayOfWeek}]:
                for key,value in cronProperty.items():
                    if value == "*":
                        # The template already added slashes.  runPlaybook does not add slashes.
                        if key == 'min':
                            min = '\\*'
                        if key == 'hour':
                            hour = '\\*'
                        if key == 'dayOfMonth':
                            day = '\\*'
                        if key == 'month':
                            month = '\\*'
                        if key == 'dayOfWeek':
                            dayOfWeek = '\\*'
            
            # Look for the jobs in redis-db to be removed in crontab           
            for index,eachCron in enumerate(cronJobs):
                # each cron: * * * * * keystack curl -d "sessionId=&playbook=pythonSample&awsS3=False&jira=False&pauseOnError=False&debug=False&domain=Communal&scheduledJob="minute=* hour=* dayOfMonth=* month=* dayOfWeek=*"&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/run

                # eachCron: 18 19 24 3 * root curl -d "playbook=playbookName&user=user" 
                if bool(search(f'{min}\s+{hour}\s+{day}\s+{month}\s+{dayOfWeek}\s+{GlobalVars.user}.*{jobSearchPattern}.*', eachCron)):
                    cronJobs.pop(index)

                    try:
                        if dbObj:
                            # This dbObj was passed in from envViews:DeleteScheduledEnv
                            # MongoDB will do a $pull from the cronJobs list
                            dbObj.updateDocument(collectionName='scheduler',
                                                 queryFields={'query': queryName},
                                                 updateFields={'cronJobs': {'cron': eachCron}},
                                                 removeFromList=True)
                    except Exception as errMsg:
                        raise Exception(f'Error from scheduler: {errMsg}')  
                      
                    break
                    
        # Below is for keystackScheduler.py service to remove tasks from /etc/crontab   
        if len(cronJobs) > 0:
            updatedCronJobs = ''
            # Build a crontab file with updated cronjobs
            for cron in cronJobs:
                # The crontab file may contain some unknown Linux OS cron jobs. Exclude them.
                # Look for specific cron jobs
                if 'playbook=' in cron or 'env=' in cron or 'portGroup=' in cron:
                    updatedCronJobs += f'{cron}\n\n'
            
            # The Problem: Both reservation read the crontab file at the same time.
            # So even though one cron job got removed, but the second still in there and kept the existing cron job
            
            execSubprocessInShellMode(f"sudo echo '{updatedCronJobs}' | sudo tee /etc/crontab", showStdout=False)
                                
        else:
            execSubprocessInShellMode('sudo echo "" | sudo tee /etc/crontab', showStdout=False)
                        
def getSchedulingOptions(typeOfScheduler='reserve'):
    
    """ 
    typeOfScheduler: reserve | expiration
    """
    if typeOfScheduler in ['reserve', 'schedulePlaybook']:
        hourId = 'reserve-hour'
        minuteId = 'reserve-minute'
        monthId = 'reserve-month'
        dayOfMonthId = 'reserve-dayOfMonth'
        dayOfWeekId = 'reserve-dayOfWeek'
        
    if typeOfScheduler in ['expiration', 'removePlaybook']:
        hourId = 'release-hour'
        minuteId = 'release-minute'
        monthId = 'release-month'
        dayOfMonthId = 'release-dayOfMonth'
        dayOfWeekId = 'release-dayOfWeek'        
        
    minute = f'<label for="{minuteId}">Minute:&emsp; </label>'
    minute += f'<select id="{minuteId}">'
    minute += '<option value="*" selected="selected">*</option>'
    for option in range(0, 61):            
        minute += f'<option value="{option}">{option}</option>'
    minute += '</select> &emsp;&emsp;'
    
    hour = f'<label for="{hourId}">Hour:&emsp; </label>'
    hour += f'<select id="{hourId}">'
    hour += '<option value="*" selected="selected">*</option>'
    for option in range(0, 24):            
        hour += f'<option value="{option}">{option}</option>'
    hour += '</select> &emsp;&emsp;'

    dayOfMonth = f'<label for="{dayOfMonthId}">Date:&emsp; </label>'
    dayOfMonth += f'<select id="{dayOfMonthId}">'
    dayOfMonth += '<option value="*" selected="selected">*</option>'
    for option in range(1, 32):            
        dayOfMonth += f'<option value="{option}">{option}</option>'
    dayOfMonth += '</select> &emsp;&emsp;'

    month = f'<label for="{monthId}">Month:&emsp; </label>'
    month += f'<select id="{monthId}">'
    month += '<option value="*" selected="selected">*</option>'
    for option in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:            
        month += f'<option value="{option}">{option}</option>'
    month += '</select> &emsp;&emsp;'

    dayOfWeek = f'<label for="{dayOfWeekId}">Day Of Week:&emsp; </label>'
    dayOfWeek += f'<select id="{dayOfWeekId}">'
    dayOfWeek += '<option value="*" selected="selected">*</option>'
    for option in ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']:            
        dayOfWeek += f'<option value="{option}">{option}</option>'
    dayOfWeek += '</select>'
    
    return hour, minute, month, dayOfMonth, dayOfWeek


if __name__ == "__main__":
    '''
    while True:
        if RedisMgr.redis:
            scheduledForRemoval = RedisMgr.redis.getAllPatternMatchingKeys(pattern='scheduler-remove', sort=False)
            print('\n--- scheduler: redis remove:', scheduledForRemoval)
    '''
    pass
    