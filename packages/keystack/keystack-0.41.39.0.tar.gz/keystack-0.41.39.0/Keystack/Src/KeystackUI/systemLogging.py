import os, sys, traceback
from datetime import datetime
from glob import glob
from shutil import rmtree
from copy import deepcopy

# /Keystack/KeystackUI
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir.replace('/KeystackUI', ''))
from db import DB
from globalVars import GlobalVars

class Vars:
    collectionName = 'logs'
    

class SystemLogsAssistant:
    def getDatetime(self):
        now = datetime.now()
        return now.strftime('%m-%d-%Y')
    
    def getInstantMessages(self, webPage):
        """ 
        For instant message on individual pages
        """
        messages = DB.name.getOneDocument(collectionName=Vars.collectionName, 
                                        fields={'_id': webPage}, 
                                        includeFields=None)
        html = ''

        if messages:
            for date, messageList in messages[webPage].items():
                if date == self.getDatetime():
                    for message in reversed(messageList):
                        html += f"""<tr>
                                    <td style="text-align:center">{message['datetime']}</td>
                                    <td style="text-align:center">{message['user']}</td>
                                    <td style="text-align:center">{message['action']}</td>
                                    <td style="text-align:center">{message['msgType']}</td>
                                    <td style="text-align:left">{message['msg']}</td>
                                </tr>"""
                                
            html += '<tr></tr>'
                    
        return html

    def getLogMessages(self, webPage:str) -> str:
        """
        System logs: get logs based on topic
        Called by systemLogs.views.py.GetLogMessages()
        
        webPage: labInventory, pipelines, playbooks, etc
        """
        self.deletePastLogs(webPage)
        
        logObj = DB.name.getDocuments(collectionName=Vars.collectionName,
                                      fields={'_id': webPage}, 
                                      includeFields=None)
                                
        count = deepcopy(logObj)
        if len(list(count)) > 0:
            messages = logObj[0]
        else:
            messages = None
            
        html = ''

        if messages:
            reversedOrderList = []      
            for date, messageList in messages[webPage].items():
                reversedOrderList.append(messageList)
                
            for msg in reversed(reversedOrderList):
                for message in reversed(msg): 
                    detailedMessage = f'{message["msg"]}<br>{message["forDetailLogs"]}'  
                    html += '<tr>'
                    html += f'<td class="col-1">{message["datetime"]}</td>'
                    html += f'<td class="col-1">{message["user"]}</td>'
                    html += f'<td class="col-1">{message["action"]}</td>'
                    html += f'<td class="col-1">{message["msgType"]}</td>'
                    html += f'<td class="col-2 textAlignLeft">{detailedMessage}</td>'
                    html += '</tr>'
                    
            html += '<tr></tr>'
               
        return html
                
    def log(self, user:str, webPage:str, action:str, msgType:str, msg:str, forDetailLogs='') -> None:
        """
        collection = logs
        
        todayInstantMessages: [{'datetime': timestamp, 'user': user, 'module': None, 'action': action.capitalize(), 'msgType': msgType.capitalize(), 'msg': msg}]
        playbook:
            date: [{'datetime': timestamp, 'user': user, 'module': None, 'action': action.capitalize(), 'msgType': msgType.capitalize(), 'msg': msg}]
        sessions:
            date: []
        results:
            date: []
        
        webPage: options: todayInstantMessages, playbooks, sessions, results, 
        action:  options: get, create, modify, delete 
        msgType: options: info, debug, warning, error, success, failed
        forDetailLogs: A filter to log in detailLogs.  Don't show in todayInstantMessages.
        
        datetime, user, action, webPage, msgType, msg
        """
        now = datetime.now()
        timestamp = now.strftime('%m-%d %H:%M:%S')
        date = now.strftime('%m-%d-%Y')
        
        logData = {'datetime':timestamp, 
                   'user':user, 
                   'action':action, 
                   'webPage':webPage,
                   'msgType':msgType.capitalize(), 
                   'msg':msg, 
                   'forDetailLogs':forDetailLogs}
        
        try:
            if 'td>' in msg:
                msg = msg.replace('<td>', '')
                msg = msg.replace('</td>', '')
            
            result1 = DB.name.updateDocument(collectionName=Vars.collectionName, 
                                             queryFields={'_id': webPage},
                                             updateFields={f'{webPage}.{date}': logData},
                                             appendToList=True,
                                             upsert=True)
                
        except Exception as errMsg:
            #result = DB.name.insertOne(collectionName=Vars.collectionName, data={'_id': webPage, webPage: {date: [logData]}})
            pass
        
    def delete(self, logPage):
        """
        Delete all the logs of a log's category
        """
        result = DB.name.deleteOneDocument(collectionName=Vars.collectionName, fields={'_id': logPage})

    def getLogTitles(self):
        logObj = DB.name.getDocuments(collectionName=Vars.collectionName, fields={}, includeFields={'_id':0})
        titles = [key for obj in logObj for key, properties in obj.items()] 
        return titles
    
    def deletePastLogs(self, topic=None):
        """ 
        Remove past logs based on keystack_removeLogsAfterDays=<days> in keystackSystemSettings.env.
        Defaults to 1 day old logs
        
        Mainly used by keystackLogs.py
        """
        try:
            from keystackUtilities import readYaml

            etcKeystackYml = readYaml('/etc/keystack.yml')
            keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
            removeLogsAfterDays = keystackSettings.get('removeLogsAfterDays', 3)
            
            # ['playbooks', 'loginCredentials', 'debug', 'fileMgmt', 'EnvUtilizations', 'apps', 'globals', 'modules', 'controllers', 'accountMgmt', 'testResults', 'testcase', 'portMgmt', 'envs', 'labInventory', 'portGroup', 'userGroup', 'domains', 'redis', 'userGuides', 'system', 'pipelines']
            if topic:
                allLogCategories = [topic]
            else:
                allLogCategories = self.getLogTitles()
                
            today = datetime.now()

            for logCategory in allLogCategories:
                logs = DB.name.getDocuments(collectionName=Vars.collectionName, 
                                            fields={'_id': logCategory}, 
                                            includeFields=None)
                                
                # logs[0]: {'accountMgmt': {}}
                count = deepcopy(logs)
                if len(list(count))> 0:
                    for recordedDate in logs[0][logCategory]:
                        format = '%m-%d-%Y'
                        datetimeObj = datetime.strptime(recordedDate, format)
                        daysDelta = today.date() - datetimeObj.date()
                        daysRecorded = daysDelta.days
                        
                        # recoredDate:01-03-2025 daysDelta:116 days, 0:00:00  daysRecorded:116
                        #print(f'logs:{logCategory}  daysDelta:{daysDelta}  daysRecorded:{daysRecorded}  recoredDate:{recordedDate}   removeLogsAfterDays:{removeLogsAfterDays}')
                        if int(daysRecorded) >= int(removeLogsAfterDays):
                            DB.name.removeKeyFromDocument(collectionName=Vars.collectionName,
                                                          queryFields={'_id': logCategory}, 
                                                          updateFields={"$unset": {f'{logCategory}.{recordedDate}': 1}})
                            
        except Exception as errMsg:
            #print('\n--- deletePastLogs error:', traceback.format_exc(None, errMsg))     
            pass
                       
if __name__ == "__main__":
    SystemLogsAssistant().deletePastLogs()
