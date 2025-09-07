import os, sys, json, traceback
from re import search
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from globalVars import GlobalVars, HtmlStatusCodes
from db import DB
from systemLogging import SystemLogsAssistant
from accountMgr import AccountMgr
from topbar.settings.accountMgmt.verifyLogin import  verifyUserRole
from topbar.utilizations.EnvUtilizationDB import EnvUtilizationDB
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp

class Vars:
    webpage = 'EnvUtilizations'
    colorIndex = 0
    colors = ['blue', 'red', 'brown', 'orange', 'green', 'yellow', 'purple', 'aqua', 'aquamarine', 
              'blueviolet', 'coral', 'chocolate', 'cyan', ' crimson,', 'darkblue', 'darkcyan', 
              'cornflowerblue', 'darkgreen', 'darkmagenta', 'darkgrey', 'darkkhaki', 'darkorange',
              'darkred', 'darkorchid', 'darkslategray', 'darkturquoise'] 
 
def getNextColor():
    totalColors = len(Vars.colors)
    
    if Vars.colorIndex == totalColors:
        Vars.colorIndex = 0
        
    if Vars.colorIndex < totalColors:
        nextColor = Vars.colors[Vars.colorIndex]
        Vars.colorIndex += 1
        return nextColor


class GetEnvBarChart(APIView):
    def post(self,request):
        """ 
        Env bar chart
        """
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        selectedEnvs     = request.data.get('selectedEnvs', None)
        lastNumberOfDays = request.data.get('lastNumberOfDays', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        dataValues = []
        envList = []
        envCounters = {}
        colors = []
        utiliziations = []

        #print(f'\n---- utilization: remotecontroller:{remoteController}  mainControllerIp:{mainControllerIp} ---')
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'selectedEnvs': selectedEnvs, 'lastNumberOfDays': lastNumberOfDays}
            restApi = '/api/v1/utilization/envsBarChart'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetEnvBarChart')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                envList = response.json()['envs']
                trackUtilization = response.json()['trackUtilization']
                colors = response.json()['colors']
        else:   
            try:
                if selectedEnvs == [] or 'allEnvs' in selectedEnvs:
                    selectedEnvs = 'all'
                       
                #print(f'\nutilization: selectedEnvs:{selectedEnvs} lastDays:{lastNumberOfDays}')         
                envUtilizations = EnvUtilizationDB().queryEnvs(env=selectedEnvs, lastDays=int(lastNumberOfDays), 
                                                               daysLessThan=None, daysGreaterThan=None)
                
                # var xValues = ["Italy", "France", "Spain", "USA", "Argentina"];
                # var yValues = [55, 49, 44, 24, 15];
                # var barColors = ["red", "green","blue","orange","brown"];
                
                for timestamp in envUtilizations:
                    # {'timestamp': datetime.datetime(2022, 11, 20, 15, 29, 18, 785000), 
                    #  'meta': {'env': 'loadcoreSample', 'user': 'Hubert Gee'}}

                    envName = timestamp['meta']['env']
                    theUser = timestamp['meta']['user']
                    # 2022-11-25 12:57:21.653000
                    
                    if envName not in envList:
                        envList.append(envName)
                        envCounters[envName] = {'usageCounter':0, 'userTimestamp':[]}
                                
                    # Get the number of usage for each env
                    envCounters[envName]['usageCounter'] += 1
                    
                trackUtilization = []
                
                for index,env in enumerate(envList):
                    trackUtilization.append(envCounters[env]['usageCounter'])
                    colors.append(getNextColor())
                
            except Exception as errMsg:
                statusCode = HtmlStatusCodes.error
                errorMsg = errMsg
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvBarChart', 
                                          msgType='Error', msg=errMsg,
                                          forDetailLogs=f'{traceback.format_exc(None, errMsg)}')

        return Response({'envs':envList, 'trackUtilization':trackUtilization, 'colors':colors,
                         'errorMsg': errorMsg}, status=statusCode)
 
        
class GetUserUsageBarChart(APIView):
    def post(self,request):
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        user = AccountMgr().getRequestSessionUser(request)
        selectedEnvs = request.data.get('selectedEnvs', None)
        lastNumberOfDays = request.data.get('lastNumberOfDays', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        envList = []
        envCounters = {}

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {'selectedEnvs': selectedEnvs, 'lastNumberOfDays': lastNumberOfDays}
            restApi = '/api/v1/utilization/usersBarChart'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetUserUsageBarChart')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.error
            else:
                envs = response.json()['envs']
        else:  
            try:
                if selectedEnvs == [] or 'allEnvs' in selectedEnvs:
                    selectedEnvs = 'all'
               
                #print(f'\nutilization: selectedEnvs:{selectedEnvs} lastDays:{lastNumberOfDays}')         
                envUtilizations = EnvUtilizationDB().queryEnvs(env=selectedEnvs, lastDays=int(lastNumberOfDays), 
                                                               daysLessThan=None, daysGreaterThan=None)
                # var xValues = ["user1", "user2", "user3", "user4", "user5"];
                # var yValues = [55, 49, 44, 24, 15];
                # var barColors = ["red", "green","blue","orange","brown"];
                
                for timestamp in envUtilizations:
                    # {'timestamp': datetime.datetime(2022, 11, 20, 15, 29, 18, 785000), 
                    #  'meta': {'env': 'loadcoreSample', 'user': 'Hubert Gee'}}
                    envName = timestamp['meta']['env']
                    theUser = timestamp['meta']['user']
                    
                    if envName not in envList:
                        envList.append(envName)
                        envCounters[envName] = {}
                    
                    if theUser not in list(envCounters[envName].keys()):
                        envCounters[envName][theUser] = {}
                        envCounters[envName][theUser].update({'usageCounter': 0})
                                
                    # Get the number of usage for each env
                    envCounters[envName][theUser]['usageCounter'] += 1

                envs = [] 
                for index, env in enumerate(envList):
                    print(f'\n{index}:  {env}')
                    # For each env, create a list of users and a list corresponding to their counters.
                    usersList = []
                    for user in envCounters[env].keys():
                        # {'timestamp': datetime.datetime(2022, 11, 20, 15, 29, 18, 785000), 
                        #  'meta': {'env': 'loadcoreSample', 'user': 'Hubert Gee'}}
                        usersList.append([user, envCounters[env][user]['usageCounter'], getNextColor()])
                        
                    envs.append([env, usersList])

            except Exception as errMsg:
                statusCode = HtmlStatusCodes.error
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetUserUsageBarChart', 
                                        msgType='Error', msg=errMsg,
                                        forDetailLogs=f'{traceback.format_exc(None, errMsg)}')

        return Response(data={'envs':envs, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
        
  
class GetEnvBarChart2(APIView):
    def post(self,request):
        """ 
        https://developers.google.com/chart/interactive/docs/gallery/barchart#examples
        
        Bar Chart data:
        var data = google.visualization.arrayToDataTable([
            ['City', '2010 Population',],
            ['New York City, NY', 8175000],
            ['Los Angeles, CA', 3792000],
            ['Chicago, IL', 2695000],
            ['Houston, TX', 2099000],
            ['Philadelphia, PA', 1526000]
        ]);
        
        User pie chart data:
        var data = google.visualization.arrayToDataTable([
            ['Task', 'Hours per Day'],
            ['Work',     11],
            ['Eat',      2],
            ['Commute',  2],
            ['Watch TV', 2],
            ['Sleep',    7]
        ]);
  
        var options = {
            title: 'My Daily Activities',
            pieHole: 0.4,
        };
        """
        body = json.loads(request.body.decode('UTF-8'))
        user = request.session['user']
        selectedEnvs = body['selectedEnvs']
        lastNumberOfDays = body['lastNumberOfDays']
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        dataValues = []
        envList = []
        envCounters = {}
        envBarChartList = [['Env', f'{lastNumberOfDays} Day Usage', {'role': 'style'}]]

        if selectedEnvs == [] or 'allEnvs' in selectedEnvs:
            selectedEnvs = 'all'
          
        # getBarChart: selectedEnvs:['/opt/KeystackTests/Envs/hubert.yml', '/opt/KeystackTests/Envs/bringup.yml'] lastNumberOfDays:14
        
        barChartOptions = {'title': 'Env Utilizations',
                           'legend': 'none',
                           'chartArea': {'width': '75%'},
                           'hAxis': {'title': f'Amount Of Usage: Last {lastNumberOfDays} days', 'minValue': 0},
                           'vAxis': {'title': 'Envs'},
                          }
        
        userUsageTimestamp = '<table id="sessionsTable" class="table table-sm table-fixed tableFixHead tableMessages mt-1">' 
        userUsageTimestamp += '<thead>'
        userUsageTimestamp += '<tr>'
        userUsageTimestamp += '<th scope="col">Env</th>'
        userUsageTimestamp += '<th scope="col">User</th>'
        userUsageTimestamp += '<th scope="col">Timestamp</th>'
        userUsageTimestamp += '</tr>'
        userUsageTimestamp += '</thead>'
   
        try:   
            print(f'\nutilization: selectedEnvs:{selectedEnvs} lastDays:{lastNumberOfDays}')         
            envUtilizations = EnvUtilizationDB().queryEnvs(env=selectedEnvs, lastDays=int(lastNumberOfDays), 
                                                           daysLessThan=None, daysGreaterThan=None)
            
            for timestamp in envUtilizations:
                # {'timestamp': datetime.datetime(2022, 11, 20, 15, 29, 18, 785000), 
                #  'meta': {'env': 'loadcoreSample', 'user': 'Hubert Gee'}}

                envName = timestamp['meta']['env']
                theUser = timestamp['meta']['user']
                # 2022-11-25 12:57:21.653000
                when  = timestamp['timestamp'].strftime('%m-%d-%Y %H:%M:%S')
                
                if envName not in envList:
                    envList.append(envName)
                    envCounters[envName] = {'usageCounter':0, 'userTimestamp':[]}
                               
                # Get the number of usage for each env
                envCounters[envName]['usageCounter'] += 1
                envCounters[envName]['userTimestamp'].append([theUser, when])
             
            finalUserPieData = []                            
            for index,env in enumerate(envList):
                envBarChartList.append([env, envCounters[env]['usageCounter'], getNextColor()])
                
                # For each env, get user total usage (counter)
                userUsage = {}
                userPieChartDataList = [['Users', 'Percentage']]
                userPieChartOptions = {'title': f'Users on Env: {env}', 
                                       'pieHole': 0.5, 
                                       'pieSliceTextStyle': {'color': 'black'},
                                       'chartArea': {'width': '50%'}
                                       }
                
                for tStamp in envCounters[env]['userTimestamp']:
                    # {'timestamp': datetime.datetime(2022, 11, 20, 15, 29, 18, 785000), 
                    #  'meta': {'env': 'loadcoreSample', 'user': 'Hubert Gee'}}
                    tUser = tStamp[0]
                    dateTimeLog = tStamp[1]
                    data = [tUser, envCounters[env]['usageCounter']]
                    
                    if user not in userUsage:
                        userUsage[user] = 0

                    userUsage[user] += 1
                    userUsageTimestamp += '<tr>'
                    userUsageTimestamp += f'<td>{env}</td>'
                    userUsageTimestamp += f'<td>{tUser}</td>'
                    userUsageTimestamp += f'<td>{dateTimeLog}</td>'
                    userUsageTimestamp += '</tr>'
                    
                for uniqueUser,counter in userUsage.items():        
                    userPieChartDataList.append([uniqueUser, int(counter)])
                    
                finalUserPieData.append([userPieChartDataList, userPieChartOptions])
            
            userUsageTimestamp += '</table>'
            
        except Exception as errMsg:
            statusCode = HtmlStatusCodes.error
            error = str(errMsg)
            status = 'failed'
            SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetEnvBarChart', 
                                      msgType='Error', msg=errMsg,
                                      forDetailLogs=traceback.format_exc(None, errMsg))
        
        if len(envBarChartList) == 1:
            envBarChartList = []

        return Response(data={'envBarChartList':envBarChartList, 'barChartOptions':barChartOptions,
                              'userPieChartList':finalUserPieData, 'userUsageTimestamps':userUsageTimestamp,
                              'status':status, 'errorMsg': error}, status=statusCode)
        

