import os, sys, subprocess, json, traceback
from re import search
from glob import glob
from time import sleep

from commonLib import createTestResultTimestampFolder,  validatePlaybook
from keystackUtilities import convertStringToDict, getDeepDictKeys, readFile, readYaml, writeToJson, convertStrToBoolean, mkdir2, writeToFile, getTimestamp
from systemLogging import SystemLogsAssistant
from topbar.settings.accountMgmt.verifyLogin import verifyUserRole
from accountMgr import AccountMgr
from topbar.settings.accountMgmt.verifyLogin import authenticateLogin
from domainMgr import DomainMgr
from topbar.docs.restApi.controllers import executeRestApiOnRemoteController, getMainAndRemoteControllerIp
from globalVars import GlobalVars, HtmlStatusCodes
from db import DB
from scheduler import JobSchedulerAssistant, getSchedulingOptions
from RedisMgr import RedisMgr

from django.views import View
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets


class Vars:
    """ 
    For logging the correct topics.
    To avoid human typo error, always use a variable instead of typing the word.
    """
    webpage = 'playbooks'


keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    
           
class GetPlaybookDetails(APIView):
    playbook = openapi.Parameter(name='playbook', description="Name of the Playbook", example="qaPlaybook",
                                 required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING) 
    @swagger_auto_schema(tags=['/api/v1/playbook/details'], manual_parameters=[playbook], 
                         operation_description="Get playbook details")

    def get(self, request, data=None):
        """
        Description:
            Get details of a playbook
        
        GET /api/vi/playbook/details
        
        ---
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET http://192.168.28.7:8000/api/v1/playbook/details?playbook=pythonSample
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "playbook=pythonSample" -H "Content-Type: application/x-www-form-urlencoded" -X GET http://192.168.28.7:8000/api/v1/playbook/details 
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"playbook": "pythonSample"}' -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/playbook/details
            
            session = requests.Session()
            response = session.request('Get', 'http://localhost:8000/api/v1/playbook/details')
            return Response({'playbooks': response.json()['playbooks']})
        """
        status = HtmlStatusCodes.success
        playbookDetails = None
        playbookName = None
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        # http://ip:port/api/v1/playbook/details?playbook=myCoolPlaybook
        if request.GET:
            try:
                playbookName = request.GET.get('playbook')
            except Exception as error:
                errorMsg = f'Expecting key playbook, but got: {request.GET}'
                return Response(data={'playbookDetails': playbookDetails, 'status': 'failed', 
                                      'errorMsg': errorMsg}, status=HtmlStatusCodes.success)
            
        # JSON format
        if request.data:
            # <QueryDict: {'playbook': pythonSample}
            try:
                playbookName = request.data['playbook']
            except Exception as errMsg:
                errorMsg = f'Expecting key playbook, but got: {request.data}'
                return Response(data={'playbookDetails': playbookDetails, 'status': 'failed', 
                                      'errorMsg': errorMsg}, status=HtmlStatusCodes.success)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"playbook": playbookName}
            restApi = '/api/v1/playbook/details'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetPlaybookDetails')
            playbookDetails = response.json()['playbookDetails']
                      
        else:
            try:
                if '.yml' not in playbookName:
                    playbookName = f'{playbookName}.yml'
                
                playbookPath = f'{GlobalVars.playbooks}/{playbookName}'
                playbookDetails = readYaml(playbookPath)
        
            except Exception as errMsg:
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='GetPlaybookDetails', 
                                          msgType='Error', msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
                return Response(data={'playbookDetails': playbookDetails, 'status': 'failed', 
                                      'errorMsg': errorMsg}, status=HtmlStatusCodes.success)
        
        return Response(data={'playbookDetails': playbookDetails, 'errorMsg': errorMsg, 'status': 'success'}, status=status)


class RunPlaybook(APIView):
    #serializers = RunPlaybookSerializer
    # Parameter([('name', 'playbook'), ('in', 'query'), ('type', 'string')]) 
    # Parameter([('name', 'sessionId'), ('in', 'query'), ('type', 'string')])
    playbook        = openapi.Parameter(name='playbook',
                                        description="Name of the Playbook to execute", example="pythonSample",
                                        required=False, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    sessionId       = openapi.Parameter(name='sessionId',
                                        description="Give a name for the test to help locate the result", 
                                        in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    domain          = openapi.Parameter(name='domain',
                                        description="The domain to put the results under. Defauls={GlobalVars.defaultDomain}", 
                                        in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)                               
    playbookConfigs = openapi.Parameter(name='playbookConfigs',
                                        description="Playbook JSON configs", in_=openapi.IN_QUERY, 
                                        type=openapi.TYPE_STRING,
                                        example='Modify anything in the Playbook using JSON format (Modifications are done in memory. Not in actual files). Note: Modules are in a list.  This means you must include all module parameters/values that the playbook has even if you are modifying just one parameter.  Example: Let say we want to modify the env, we must include the playlist also. This is the nature of modifying json list.  {"stages": {"Test": {"Modules": [{"/Modules/CustomPythonScripts": {"env": "rack2", "playlist": ["/opt/KeystackTests/Modules/CustomPythonScripts/Testcases"]}}] }}}}')
    testcaseConfigs = openapi.Parameter(name='testcaseConfigs',
                                       description="Modify a Playbook playlist testcase yml files (Modifications are done in memory. Not in actual files)", 
                                       in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                                       example="A list of testcase yml files associating with modifications in json format: [{'/Modules/IxNetwork/Testcases/bgp.yml': {'script': 'script1.py'}}, {}, ...]")
           
    envConfigs      = openapi.Parameter(name='envConfigs', description="Modify the playbook's env params (in memory)", 
                                       in_=openapi.IN_QUERY, type=openapi.TYPE_STRING,
                                       example="A list of json env settings. Example: [{'stage': 'Test', 'module': 'LoadCore', 'params':   {'mwIp': '10.1.2.3'}, {'stage': 'teardown', 'module': 'cleanup', 'params': {'serverIp': '1.1.1.1'}, {}} ...}]")
    jira            = openapi.Parameter(name='jira', description="Open/Update Jira Issue", in_=openapi.IN_QUERY, 
                                        type=openapi.TYPE_BOOLEAN)
    awsS3           = openapi.Parameter(name='awsS3', description="Push results to AWS S3", in_=openapi.IN_QUERY, 
                                        type=openapi.TYPE_BOOLEAN)
    emailResults    = openapi.Parameter(name='emailResults', description="Email results", in_=openapi.IN_QUERY, 
                                        type=openapi.TYPE_BOOLEAN)
    trackResults    = openapi.Parameter(name='trackResults', 
                                        description="Track and monitor results in a CSV file for graphing", 
                                        in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN)   
    holdEnvsIfFailed = openapi.Parameter(name='holdEnvsIfFailed', description="Keep the env reserved for debugging if test failed", in_=openapi.IN_QUERY, 
                                        type=openapi.TYPE_BOOLEAN)
    debug           = openapi.Parameter(name='debug', description="Debug/Dev mode", 
                                        in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN)
    emailResults    = openapi.Parameter(name='emailResults', description="Email results", 
                                        in_=openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN)        
    @swagger_auto_schema(tags=['/api/v1/playbook/run'], manual_parameters=[playbook, sessionId, domain,
                         playbookConfigs, testcaseConfigs, envConfigs, jira, awsS3, emailResults, trackResults, debug])
    
    @verifyUserRole(webPage=Vars.webpage, action='RunPlaybook')
    def post(self, request, data=None):
        """
        Run a playbook. Minimum param requirement: playbook=[playbooName]
         
        If you want to create a playbook from scratch, leave the playbook param blank and put the
        playbook json string in the param playbookConfigs. 
        
        POST: /api/v1/playbook/run
        
        parameters:
            playbook:         Optional: Playbook name to run
            sessionId:        Optional
            domain:           Optiona: The name of the domain to put the results.
            playbookConfigs:  Optional <JSON object>: To modify a playbook.
            emailResults:     Optional: True|False.  Example: inline=emailResults=true  json={"emailResults": "true"}
            debug:            Optional: True|False.  Example: inline=debug=true  json={"debug": "true"}
            awsS3:            Optional: True|False.  Example: inline=awsS3=true  json={"awsS3": "true"}
            jira:             Optional: True|False.  Example: inline=jira=true   json={"jira": "true"}
            trackResults:     Optional  True|False.  Example: inline=trackResults=true  json={"trackResults": "true"}
            holdEnvsIfFailed: Optional  True|False.  Example: inline=holdEnvsIfFailed=true  json={"holdEnvsIfFailed": "true"}
            testcaseConfigs:  Optional: [{testcase: jsonDetailsOfTheTestcaseToModify}].
            removeJobAfterRunning Optional: True|False: For jobScheduling. Remove the scheduled job after running the job.
            scheduledJob      Optional: <JSON object>: cron job properties.
            
            # You could modify the env file or state an env file to use for the stage/module
            # To modify an env file, use 'configs'.
            # To state a different env file, use 'envFile'.
            envConfigs:      Optional: [{env: jsonDetailsOfTheEnvToModify}].
            
                             Example 1: [{'stage': 'Test', 'module': 'LoadCore', 'configs': {'mwIp': '10.1.2.3'}, 
                                         {'stage': 'teardown', 'module': 'cleanup', configs: {'serverIp': '1.1.1.1'}, {}} ...}]
                                                 
                             Example 2: [{'stage': 'Test', 'module': 'LoadCore', 'envFile': 'sanityTest.yml', 
                                         {'stage': 'teardown', 'module': 'cleanup', configs: {'serverIp': '1.1.1.1'}, {}} ...}]
                                                 
            createDynamicPlaybook Optional: <Json object> Create a playbook from blank.
        
        Examples:
            # Inline parameters must wrap rest api in quotes
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/playbook/run?playbook=pythonSample&sessionId=awesomeTest2&awsS3=true&pauseOnFailure=false'
            
            curl --insecure -L -X POST 'https://192.168.28.17/api/v1/playbook/run?playbook=pythonSample&sessionId=awesomeTest'
        
            # works
            curl -d "domain=Communal&playbook=DOMAIN=Communal/Samples/advance" -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X POST http://192.168.28.10:28028/api/v1/playbook/runPlaybook   
            
            curl -d '{"domain": "Communal", "playbook": "DOMAIN=Communal/Samples/advance"}' -H "Content-Type: application/json" -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X POST http://192.168.28.10:28028/api/v1/playbook/runPlaybook

            curl -d "sessionId=hello&playbook=DOMAIN=Communal/Samples/advance&domain=Communal" -H "Content-Type: application/x-www-form-urlencoded" -H "API-Key: xyWGHy8fkzTgaCiRQ-Q0mA" -X POST http://192.168.28.10:28028/api/v1/playbook/runPlaybook
                    
            # playbookConfigs
            curl -H "API-Key: VZleFqgtRtfwvHwlSujOXA" -d '{"playbook": "pythonSample", "sessionId": "awesomeTest", "awsS3": true, "playbookConfigs": {"stages": {"Test": {"Modules": [{"/Modules/CustomPythonScripts": {"env": "hubert", "playlist": ["/opt/KeystackTests/Modules/CustomPythonScripts/Testcases"]}}] }}}}' -H "Content-Type: application/json"  -X POST http://192.168.28.7:8000/api/v1/playbook/run

            # Not work: Curly braces are unsafe. You must use urlencode or -d.
            #    Or include -g|--globoff
            # This  option  switches  off  the "URL globbing parser". When you set this option, you can
            # specify URLs that contain the letters {}[] without having them being interpreted by  curl
            # itself.  Note  that  these  letters  are not normal legal URL contents but they should be
            # encoded according to the URI standard.
            curl -X POST 'http://192.168.28.17:8000/api/v1/playbook/run?playbook=pythonSample&sessionId=awesomeTest2&playbookConfigs={"stages": {"Test": {"/Modules/CustomPythonScripts": {"enable": false}}}}'
                        
            curl -d '{"playbook": "pythonSample", "sessionId": "awesomeTest", "playbookConfigs": {"globalSettings": {"loginCredentialKey": "regressionTest"}, "stages": {"Test": {"/Modules/CustomPythonScripts": {"enable": false}}}}}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/run
            
            # Modify the playlist TESTCASES (Not the playbook itself)
            curl -d '{"playbook": "pythonSample", "sessionId": "awesomeTest", "playlistMods": [{"/Modules/CustomPythonScripts/Testcases/bgp.yml": {"script": "ospf.py"}}]}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/run
            
            # Modify playbook module's ENV configs (Not the playbook itself)
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"playbook": "pythonSample", "sessionId": "awesomeTest", "envConfigs": [{"stage": "Test", "module": "CustomPythonScripts",  "params": {"login": false}}]}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/run

            # Create a dynamic playbook

        Use form-data. Don't use RAW because it requires csrf token. A hassle to insert it.
        Must do a GET to get it and then insert it as a RAW with Content-Type: application/JSON
        
        If the URL contains the data such as the following, then use request.GET.get('<parameter_name>')
           http://ip:port/api/v1/runPlaybook?playbook=myCoolPlaybook&sessionId=myCoolTestSession
           
        If you pass in the data as raw format, then use request.data
        
        Returns:
           - The sessionId
           - The result path
        """
        sessionIdPath = None
        resultTimestampFolderName = None
        
        # action: runPlaybook or runPipeline
        action = 'runPlaybook'
        self.playbookName = 'Dynamically-Created'
        self.awsLoginFile = None
        self.awsAccessKey = None
        self.awsSecretKey = None
        self.awsRegion = None
        self.s3BucketPath = None
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        errorMsg = None 
        status = 'success'
        statusCode = HtmlStatusCodes.success

        try:
            # http://ip:port/api/v1/playbook/run?playbook=myPlaybook&sessionId=mySessionId
            if request.GET:
                self.scheduledJob          = convertStrToBoolean(request.GET.get('scheduledJob', False))
                self.removeJobAfterRunning = convertStrToBoolean(request.GET.get('removeJobAfterRunning', False))
                self.pipeline              = request.GET.get('pipeline', None)
                self.sessionId             = request.GET.get('sessionId', None)
                self.domain                = request.GET.get('domain', None)
                # <QueryDict: {'playbook': ['pythonSample'], 'sessionId': ['awesomeTest2'], 'awsS3': ['']}>
                self.playbook              = request.GET.get('playbook', None)
                # ['demo2.yml', 'demo1.yml', 'qa/sample2.yml']
                self.testConfigs             = request.GET.get('testConfigs', [])
  
                self.envConfigs            = request.GET.get('envConfigs', None)
                if self.envConfigs:
                    self.envConfigs        = json.loads(self.envConfigs)                
                
                self.playlistMods          = request.GET.get('playlistMods', None)
                if self.playlistMods:
                    self.playlistMods      = json.loads(self.playlistMods)
                    
                self.playbookConfigs       = request.GET.get('playbookConfigs', None)
                if self.playbookConfigs is not None:
                    self.playbookConfigs   = json.loads(self.playbookConfigs)
    
                self.awsS3                 = convertStrToBoolean(request.GET.get('awsS3', False))
                # awsLoginFile=<playbook>.globalSettings.awsLogin.<value>
                self.loginCredentialKey    = request.GET.get('loginCredentialKey', None)
                self.jira                  = convertStrToBoolean(request.GET.get('jira', False))
                self.trackResults          = convertStrToBoolean(request.GET.get('trackResults', False))
                self.env                   = request.GET.get('env', None)
                self.debug                 = convertStrToBoolean(request.GET.get('debug', False))          
                self.emailResults          = convertStrToBoolean(request.GET.get('emailResults', False))
                self.pauseOnFailure          = convertStrToBoolean(request.GET.get('pauseOnFailure', False))
                self.holdEnvsIfFailed      = convertStrToBoolean(request.GET.get('holdEnvsIfFailed', False))
                self.abortTestOnFailure    = convertStrToBoolean(request.GET.get('abortTestOnFailure', False))
                self.includeLoopTestPassedResults  = convertStrToBoolean(request.GET.get('includeLoopTestPassedResults', False))
                self.reservationUser       = request.GET.get('reservationUser', user)
                
        except Exception as errMsg:
            errorMsg = str(errMsg)
            print('\nrunPlaybook error: request.GET error:', errMsg)
            SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error',
                                        msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 
            return Response(data={'status': 'failed', 'errorMsg': errorMsg, 'sessionIdPath': None, 
                                  'sessionId': None, 'testGroup':self.group}, status=HtmlStatusCodes.success)

        # Calls from sessionMgmt template comes here
        # curl -d {} and keystackUI
        if request.data:
            # Rest API json data 
            # {'playbook': '/opt/KeystackTests/Playbooks/pythonSample.yml', 'debug': True, 'emailResults': True, 'awsS3': True, 'jira': True, 'pauseOnFailure': True}
            
            # RUN DATA: <QueryDict: {'sessionId': [''], 'playbook': ['pythonSample'], 'awsS3': ['False'], 'jira': ['False'], 'pauseOnFailure': ['False'], 'debug': ['False'], 'domain': ['Communal'], 'holdEnvsIfFailed': ['False'], 'abortTestOnFailure': ['False'], 'includeLoopTestPassedResults': ['False'], 'scheduledJob': ['minute=* hour=* dayOfMonth=* month=* dayOfWeek=*'], 'webhook': ['true']}
            try:
                # These 3 are from jobScheduler only
                self.mainControllerIp              = request.data.get('mainController', None)
                self.remoteControllerIp            = request.data.get('remoteController', None)
                
                # schedule = f'playbook={playbook} minute={minute} hour={hour} day={dayOfMonth} month={month} dayOfWeek={dayOfWeek}'
                self.scheduledJob                  = request.data.get('scheduledJob', None)
                self.removeJobAfterRunning         = convertStrToBoolean(request.data.get('removeJobAfterRunning', False))
                self.reservationUser               = request.data.get('reservationUser', None)
                                             
                # This user comes from mainController, when it's different from the remoteController
                # Default the user from above AccountMgr()
                user                               = request.data.get('user', user)
                
                self.pipeline                      = request.data.get('pipeline', None)
                self.sessionId                     = request.data.get('sessionId', None)
                self.domain                        = request.data.get('domain', None)
                self.playbook                      = request.data.get('playbook', None)
                 # ['demo2.yml', 'demo1.yml', 'qa/sample2.yml']
                self.testConfigs                     = request.data.get('testConfigs', [])
                self.playlistMods                  = request.data.get('playlistMods', None)
                
                #<JSON object>: To modify a playbook
                self.playbookConfigs               = request.data.get('playbookConfigs', None)
                self.envConfigs                    = request.data.get('envConfigs', None)
                self.awsS3                         = convertStrToBoolean(request.data.get('awsS3', False))
                self.loginCredentialKey            = request.data.get('loginCredentialKey', None)
                self.jira                          = convertStrToBoolean(request.data.get('jira', False))
                self.trackResults                  = convertStrToBoolean(request.data.get('trackResults', False))
                self.env                           = request.data.get('env', None)
                self.debug                         = convertStrToBoolean(request.data.get('debug', False))
                self.emailResults                  = convertStrToBoolean(request.data.get('emailResults', False))
                self.pauseOnFailure                = convertStrToBoolean(request.data.get('pauseOnFailure', False))
                self.holdEnvsIfFailed              = convertStrToBoolean(request.data.get('holdEnvsIfFailed', False))
                self.abortTestOnFailure            = convertStrToBoolean(request.data.get('abortTestOnFailure', False))
                self.includeLoopTestPassedResults  = convertStrToBoolean(request.data.get('includeLoopTestPassedResults', False))

            except Exception as errMsg:
                errorMsg = str(errMsg)
                print('\nrunPlaybook error: request.data error:', errMsg)
                SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg)) 
                return Response(data={'status': 'failed', 'errorMsg': errorMsg, 'sessionIdPath': None, 
                                      'sessionId': None, 'domain':self.domain}, status=HtmlStatusCodes.success)

        # If job came from cron scheduler, self.testConfigs is a string. Needs to be a list.
        if type(self.testConfigs) == str:
            self.testConfigs = self.testConfigs.split(',')
            
        # Came from ReST-API 
        if 'Api-Key' in request.headers:
            self.apiKey = request.headers['Api-Key']
        else:
            self.apiKey = None
  
        if self.scheduledJob:
            user = f'Scheduled: {self.reservationUser}'
        else:
            self.mainControllerIp, self.remoteControllerIp = getMainAndRemoteControllerIp(request)

        #print(f'\nDebugging playbookView: mainController:{self.mainControllerIp}  remoteController:{self.remoteControllerIp} ---' )       
        if self.remoteControllerIp and ":" in  self.remoteControllerIp:
            ipPort = self.remoteControllerIp.split(':')[-1]
        else:
            ipPort = None

        if self.remoteControllerIp and self.remoteControllerIp != self.mainControllerIp:                
            user = f'{self.mainControllerIp}:{user}'

            params = {'remoteController': self.remoteControllerIp, 'scheduledJob': self.scheduledJob, 
                      'removeJobAfterRunning': self.removeJobAfterRunning, 'user': user, "cliUserApiKey": self.apiKey,
                      'pipeline': self.pipeline, 'sessionId': self.sessionId, 'domain': self.domain, 'playbook': self.playbook,
                      'playlistMods': self.playlistMods, 'playbookConfigs': self.playbookConfigs, 'envConfigs': self.envConfigs,
                      'awsS3': self.awsS3, 'loginCredentialKey': self.loginCredentialKey, 'jira': self.jira, 'trackResults': self.trackResults,
                      'env': self.env, 'debug': self.debug, 'emailResults': self.emailResults, 'pauseOnFailure': self.pauseOnFailure,
                      'holdEnvsIfFailed': self.holdEnvsIfFailed, 'abortTestOnFailure': self.abortTestOnFailure, 'testConfigs': self.testConfigs,
                      'includeLoopTestPassedResults': self.includeLoopTestPassedResults}

            restApi = '/api/v1/playbook/runPlaybook'
            response, errorMsg , status = executeRestApiOnRemoteController(sendHttp='post', remoteControllerIp=self.remoteControllerIp, 
                                                                           restApi=restApi, params=params, 
                                                                           user=user, webPage=Vars.webpage, action='RunPlaybook')

            resultTimestampFolder      = response.json()['sessionIdPath']
            resultTimestampFolderName  = response.json()['sessionId']
            self.domain                = response.json()['domain']

        else: 
            #  /opt/KeystackTests/Pipelines/Samples-Simple1.yml           
            if self.pipeline:
                # KeystackUI: User wants to run a saved pipeline
                regexMatch = search('(.*Pipelines/)?(.+)', self.pipeline)
                if regexMatch:
                    pipelineFullPath = f'{GlobalVars.pipelineFolder}/{regexMatch.group(2)}'
                    if '.yml' not in pipelineFullPath:
                        pipelineFullPath = f'{pipelineFullPath}.yml'
                   
                if os.path.exists(pipelineFullPath) is False:
                    SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error',
                                              msg=f'No such pipeline: {self.pipeline}', forDetailLogs='')            
                    return Response(data={'status': 'failed', 
                                          'errorMsg': f'No such pipeline: {self.pipeline}'}, status=HtmlStatusCodes.success)
                
                pipelineArgs = readYaml(pipelineFullPath)

                # pipeline:samples-pythonSample
                # playbook = DOMAIN=Communal/Samples/advance
                regexNatch2 = search(f'DOMAIN=(.*?)/.*', pipelineArgs['playbook'])
                if regexNatch2 is None:
                    return Response(data={'status': 'failed', 
                                        'errorMsg': f'Playbook {pipelineArgs["playbook"]} did not include the DOMAIN'}, status=HtmlStatusCodes.success)
                
                pipelinePlaybookDomain = regexNatch2.group(1)
                      
                if self.apiKey is None:
                    if pipelinePlaybookDomain not in DomainMgr().getUserAllowedDomains(user):      
                        return Response(data={'status': 'failed', 
                                             'errorMsg': f'User {user} is not a member of the playbook domain: {pipelinePlaybookDomain}'},
                                        status=HtmlStatusCodes.success)
                if self.apiKey:
                    apiKeyUser = AccountMgr().getApiKeyUser(self.apiKey)
                    userAllowedDomains = DomainMgr().getUserAllowedDomains(apiKeyUser)
                    if pipelinePlaybookDomain not in DomainMgr().getUserAllowedDomains(apiKeyUser):      
                        return Response(data={'status': 'failed', 
                                             'errorMsg': f'User {apiKeyUser} is not a member of the playbook domain: {pipelinePlaybookDomain}'},
                                        status=HtmlStatusCodes.success)
                                                       
                for key,value in pipelineArgs.items():
                    if key == 'pipeline':
                        continue
                    
                    if value:
                        setattr(self, key, value)

                action = 'runPipeline'

            if self.sessionId and len(self.sessionId.split(' ')) > 1:
                return Response(data={'status': 'failed', 
                                      'errorMsg': f'The parameter sessionId cannot have spaces: {self.sessionId}'}, status=HtmlStatusCodes.success)

            if self.sessionId is None or self.sessionId == '':
                import random
                self.sessionId = str(random.sample(range(1,10000), 1)[0])
                                            
            if self.playbook is None:
                pipelineName = self.pipeline.split('/')[-1].split('.')[0]
                SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error',
                                          msg=f'Pipeline has no playbook defined: {pipelineName}', forDetailLogs='')            
                return Response(data={'status': 'failed', 
                                      'errorMsg': f'Pipeline has no playbook defined: {pipelineName}'}, status=HtmlStatusCodes.success)
                                           
            if self.playbook is None and self.playbookConfigs is None:            
                return Response(data={'status': 'failed', 
                                      'errorMsg': 'Must include a playbook name and/or playbookConfigs to modify the playbook or create from blank'}, status=HtmlStatusCodes.success)

            # self.playbook: DOMAIN=Communal/Samples/advance
            if self.playbook:
                # In case user state the full Playbook path and/or included the .yml extension
                matchedParse = search('.*DOMAIN=(.+?)/(.*)', self.playbook)
                if matchedParse:
                    self.playbookName = matchedParse.group(2).replace('.yml', '')
                    self.domain = matchedParse.group(1)
                else:
                    self.playbookName = self.playbook.replace('.yml', '')
                    
                if '/' in self.playbookName:
                    self.playbookName = self.playbookName.replace('/', '-')
                
                match = search(f'({GlobalVars.playbooks}/)?(.*)(\.yml)?', self.playbook)
                # DOMAIN=Communal/Samples/advance or Samples/advance
                playbook = match.group(2)
                
                # playbookPath: /opt/KeystackTests/Playbooks/DOMAIN=Communal/Samples/advance.yml
                self.playbookPath = f'{GlobalVars.playbooks}/{playbook}'
                if '.yml' not in self.playbookPath:
                    self.playbookPath = f'{self.playbookPath}.yml'
                
                try:
                    # Verify for ymal syntax error
                    readYaml(self.playbookPath)
                except Exception as errMsg:
                    errorMsg = f'The playbook yml file has syntax errors: {self.playbookPath}. ErrorMsg: {str(errMsg)}'
                    SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error',
                                              msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))  
                             
                    return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.success)

            # Commenting this out for now until groups is used correctly
            if self.domain != GlobalVars.defaultDomain and DomainMgr().domainExists(self.domain) is False:
                if 'user 'in request.session:
                    SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error',
                                              msg=f'runPlaybook: No domain name: {self.domain}', forDetailLogs='')
                                        
                return Response(data={'status': 'failed',
                                      'errorMsg': f'The domain {self.domain} does not exists. Please create the domain first.'},
                                status=HtmlStatusCodes.success)
                
            # For validatePlaybook
            if self.awsS3 or self.jira:
                checkLoginCredentials = True
            else:
                checkLoginCredentials = False
                
            # If users want to modify something prior to testing.
            # Initialize the keys.
            reconfigData = {'KeystackSystemEnv': {}, 'env': [], 'playbook': {}, 'testcases': [], "createDynamicPlaybook": False}

            if self.playbookConfigs:
                # jsonStrObj = json.dumps(playbookConfigs)
                # testConfigs = json.loads(jsonStrObj)
                reconfigData['playbook'].update(self.playbookConfigs)
                playbookObj = readYaml(self.playbookPath)    
                playbookObj.update(self.playbookConfigs)
                result, problems = validatePlaybook(self.playbook, playbookObj, checkLoginCredentials=checkLoginCredentials)
            
                if result == False:
                    errorMsg = problems
                    SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error', msg=errorMsg, forDetailLogs='')
                    
                    return Response(data={'status': 'failed', 'errorMsg': errorMsg, 'sessionIdPath':None, 'sessionId': None}, 
                                    status=HtmlStatusCodes.success)
             
            # Create a playbook from blank
            if self.playbook is None and self.playbookConfigs:
                reconfigData['createDynamicPlaybook'] = True
                if self.awsS3:
                    try:
                        'loginCredentialKey' in self.playbookConfigs['globalSettings']
                    except:
                        return Response(data={'status': 'failed',
                                              'errorMsg': 'awsS3 param was set to True, but missing playbook globalSettings.loginCredentialKey setting'}, 
                                              status=HtmlStatusCodes.success)                          
            # Modify playbook
            if self.playbook and self.playbookConfigs:
                reconfigData['createDynamicPlaybook'] = False
                                    
            if self.playlistMods:
                reconfigData['testcases'] = self.playlistMods

            if self.envConfigs:
                reconfigData['env'] = self.envConfigs

            # /opt/KeystackTests/Results/PLAYBOOK=pythonSample/09-21-2022-08:53:04:330610_awesomeTest
            resultTimestampFolder = createTestResultTimestampFolder(domain=self.domain, playbookName=self.playbookName, 
                                                                    sessionId=self.sessionId, debugMode=self.debug)

            if self.playbookConfigs:
                resultTimestampFolderName = resultTimestampFolder.split('/')[-1]
                # /opt/KeystackSystem/RestApiMods/12-12-2023-15:41:10:220274_hgee2
                sessionTempFile = f'{GlobalVars.restApiModsPath}/{resultTimestampFolderName}'   
                writeToJson(sessionTempFile, reconfigData, mode='w', sortKeys=False, indent=4)
                
            if self.playbook and self.playbookConfigs is None:
                if os.path.exists(self.playbookPath) == False: 
                    SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error', msg=f'Playbook does not exists: {self.playbookPath}', forDetailLogs='') 
                    return Response(data={'status': 'failed', 'errorMsg': f'Playbook does not exists: {self.playbookPath}'},
                                    status=HtmlStatusCodes.success)
                else:
                    # Run a pipeline name
                    playbookObj = readYaml(self.playbookPath)
                    result,problems = validatePlaybook(self.playbook, playbookObj, checkLoginCredentials=checkLoginCredentials)
                    if result == False:
                        errorMsg = problems
                        SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, 
                                                  msgType='Error', msg=errorMsg, forDetailLogs='')
                        return Response(data={'status': 'failed', 'errorMsg': errorMsg, 
                                              'sessionIdPath':None, 'sessionId': None}, status=HtmlStatusCodes.success)
           
            try:
                # request.session['mainControllerIp'] was set at login.
                # But if this runPlaybook was called by rest api or ExecRestApi, the
                # request doesn't have session['mainControllerIp']
                # If this was called by rest api, it uses http://ipAddress. It will
                # run on the local controller of the ipAddress. Also, it will include
                # parameter webhook as a way to bypass verifyApiKey
                if self.remoteControllerIp and self.remoteControllerIp != self.mainControllerIp:
                    runOnLocalController = False
                            
                if self.remoteControllerIp is None or self.remoteControllerIp == self.mainControllerIp:
                    runOnLocalController = True
                    
            except:
                runOnLocalController = True

            if runOnLocalController:
                # Run Keystack on local controller     REST-API requires -> -apiKey {self.apiKey}
                if os.environ.get('DJANGO_DEBUG', False):
                    command = f'{sys.executable} /opt/keystack_src/Src/keystack.py run -playbook {self.playbookPath} -is_from_keystack_ui -domain {self.domain} -results_folder {resultTimestampFolder} -user "{user}"'
                else:
                    command = f'keystack run -playbook {self.playbookPath} -is_from_keystack_ui -results_folder {resultTimestampFolder} -domain {self.domain} -user "{user}"'
                    
                if self.sessionId:                    command += f' -session_id {self.sessionId}'
                if self.apiKey:                       command += f' -api_key {self.apiKey}'
                if self.awsS3:                        command += ' -aws_s3'
                if self.jira:                         command += ' -jira'
                if self.trackResults:                 command += ' -track_results'
                if self.debug:                        command += ' -debug'
                if self.emailResults:                 command += ' -email_results'
                if self.pauseOnFailure:               command += ' -pause_on_failure'
                if self.holdEnvsIfFailed:             command += ' -hold_envs_if_failed'
                if self.abortTestOnFailure:           command += ' -abort_test_on_failure' 
                if self.includeLoopTestPassedResults: command += ' -include_loop_test_passed_results'
                if self.testConfigs:  
                    for testConfig in self.testConfigs:                  
                        command += f' -test_configs  {testConfig}'
                                                            
                command += ' > /dev/null 2>&1 &'

                try:
                    #print(f'\nrunPlaybook: {command}')
                    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    result, err = result.communicate()
                    if err:
                        errMsg = err.decode("utf-8")
                        errMsg = errMsg.replace('\n', '')
                        errorMsg = errMsg
                        SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error', msg=errMsg, forDetailLogs='')
                        return Response(data={'status': 'failed', 'errorMsg': errorMsg}, status=HtmlStatusCodes.success)

                    didTestRunSuccessfully = False
                    timeout = 30
                    for counter in range(0,timeout):
                        # If the test had executed successfully, an overallSummary.json file is created
                        overallSummary = f"{resultTimestampFolder}/overallSummary.json"
                        if os.path.exists(overallSummary) == False:
                            #print(f'Waiting for the session {overallSummary} creation: {counter}/{timeout}')
                            sleep(1)
                        else:
                            didTestRunSuccessfully = True
                            break

                    if didTestRunSuccessfully is False:         
                        errorMsg = 'Test failed to run. No overallSummary.json created.'
                        SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error', msg=errorMsg, forDetailLogs='')
                        return Response(data={'status': 'failed', 'errorMsg': errorMsg, 'sessionIdPath': resultTimestampFolder, 
                                              'sessionId': resultTimestampFolderName, 'domain':self.domain}, status=statusCode)

                    SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Success', msg=command, forDetailLogs='')
                                
                except Exception as errMsg:
                    errorMsg = f'Test failed to run: {errMsg}'
                    SystemLogsAssistant().log(user=user, webPage='pipelines', action=action, msgType='Error',
                                              msg=f'user:{user}<br>command:{command}<br>error: {errorMsg}',
                                              forDetailLogs=traceback.format_exc(None, errMsg))
                finally:
                    if self.removeJobAfterRunning:
                        searchPattern, minute, hour, dayOfMonth, month, dayOfWeek = self.scheduledJob.split(' ') 
                        removeJobList = [{'jobSearchPattern': searchPattern, 
                                          'minute': minute.split('=')[1],
                                          'hour': hour.split('=')[1], 
                                          'month': month.split('=')[1],
                                          'dayOfMonth': dayOfMonth.split('=')[1],
                                          'dayOfWeek': dayOfWeek.split('=')[1]}]  

                        JobSchedulerAssistant().removeCronJobs(listOfJobsToRemove=removeJobList, dbObj=DB.name, queryName='playbook')
                        
                # Must delay returning back to user in case there are many back-2-back testings occur
                # Give time to update env DB
                sleep(3)
                
        #serializer = RunPlaybookSerializer(data=request.data)
        #return Response(serializer.data, data={'message': message}, status=statusCode)
        return Response(data={'status': 'success', 'errorMsg': None, 'sessionIdPath': resultTimestampFolder, 
                              'sessionId': resultTimestampFolderName, 'domain':self.domain}, status=statusCode)


class GetPlaybookEnvDetails(APIView):
    playbook = openapi.Parameter(name='playbook', description="Name of the Playbook",
                                 required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    stage    = openapi.Parameter(name='stage', description="The stage name",
                                 required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)
    module   = openapi.Parameter(name='module', description="The module name",
                                 required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)   
    @swagger_auto_schema(tags=['/api/v1/playbook/env/details'], operation_description="Get detail configs of an Env",
                         manual_parameters=[playbook, stage, module])
    def get(self, request):
        """
        Description:
            Return an Env parameters/values of a Playbook.Stage.Module
        
        GET /api/v1/playbook/env/details?playbook=[playbookName]&stage=[stageName]&module=[module]
        
        Replace [playbookName] [stageName] [module]
        
        Parameter:
            playbook:  The playbook name
            stage:     The stage name
            module:    The stage module name

        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET 'http://192.168.28.7:8000/api/v1/playbook/env/details?playbook=loadcoreSample&stage=LoadCoreTest&module=/Modules/LoadCore'
            
            curl -d "playbook=loadcoreSample&stage=LoadCoreTest&module=/Modules/LoadCore" -H "Content-Type: application/x-www-form-urlencoded" -X GET http://192.168.28.7:8000/api/v1/playbook/env/details 
            
            curl -d '{"playbook": "loadcoreSample", "stage": "LoadCoreTest", "module": "/Modules/LoadCore"}' -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/playbook/env/details
        """
        playbook = None
        stage = None
        module = None
        envFile = None
        envParams = {}
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        status = 'success'
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        playbook = ''
        listOfModuleEnvParams = [] 
                
        # /api/v1/playbook/env/details?playbook=<playbook_name>&envXPath=<stageName>.<module>
        if request.GET:
            try:
                playbook = request.GET.get('playbook')
                stage = request.GET.get('stage')
                module = request.GET.get('module')
            except Exception as error:
                errorMsg = f'Expecting parameters playbook, stage, module, but got: {request.GET}'
                return Response(data={'error': errorMsg, 'status': 'failed'}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'sessionId': <session_name>}
            try:
                playbook = request.data['playbook']
                stage = request.data['stage']
                module = request.data['module']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters playbook, stage, module, but got: {request.data}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"playbook": playbook, "stage": stage, "module": module}
            restApi = '/api/v1/playbook/env/details'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPlaybookEnvDetails')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.success 
            else:
                # 'playbook': playbook, 'envList': listOfModuleEnvParams,
                playbook = response.json()['playbook']
                listOfModuleEnvParams  = response.json()['envList'] 
    
        else:        
            for param in [playbook, stage, module]:
                if param is None:
                    return Response(data={'status': 'failed', 'errorMsg': f'Must include param {param}'}, status=HtmlStatusCodes.success)
                            
            if '.yml' not in playbook:
                playbook = f'{playbook}.yml'

            # In case the user included the /Module path.  Get just the module name.
            if 'Modules/' not in module:
                module = f'Modules/{module}'
            if module.startswith('/') == False:
                module = f'/{module}'
                            
            playbookFullPath = f'{GlobalVars.playbooks}/{playbook}'
            if os.path.exists(playbookFullPath) == False:
                return Response(data={'status': 'failed', 'errorMsg': f'No playbook found: {playbookFullPath}'}, status=HtmlStatusCodes.success)

            playbookData = readYaml(playbookFullPath)
            listOfModuleEnvParams = []
            for eachModule in playbookData['stages'][stage]['modules']:
                # {'/Modules/LoadCore': {'env': 'loadcoreSample', 'playlist': ['/Modules/LoadCore/Testcases/fullcoreBase.yml'], 'innerLoop': {'allTestcases': 1}, 'rebootAgentsBeforeEachTest': False, 'deleteTestLogsAndResultsOnLoadCore': True, 'waitTimeBetweenTests': 0, 'deleteSession': True, 'deleteSessionOnFailure': True, 'abortOnFailure': False, 'getPdfResultsFile': True, 'getCsvResultsFile': True, 'getCapturesAndLogs': True}}
                
                if module in list(eachModule.keys()):
                    actualModuleSpellingInPlaybook = list(eachModule.keys())[0]
                    
                    if 'env' in list(eachModule[module].keys()):
                        env = eachModule[actualModuleSpellingInPlaybook]['env']
                        if env == 'None':
                            env = None
                            
                        if env:
                            if '.yml' not in env:
                                env = f'{env}.yml'
                            
                            envFile = f'{GlobalVars.envPath}/{env}'
                            
                            if os.path.exists(envFile) == False:
                                status = 'failed'
                                errorMsg = f'The env "{env}" in playbook:{playbook} stage:{stage} module:{module} does not exists in the Env inventory.'
                                return Response(data={'playbook': playbook, 'data': {}, 'errorMsg': errorMsg, 'status': status}, status=HtmlStatusCodes.success)
                            
                            try:
                                envParams = readYaml(envFile)
                                listOfModuleEnvParams.append({'env': env, 'data': envParams})
                                
                            except Exception as errMsg:
                                statusCode = HtmlStatusCodes.success
                                status = 'failed'
                                errorMsg = str(errMsg)
                
        return Response(data={'playbook': playbook, 'envList': listOfModuleEnvParams, 'errorMsg': errorMsg, 'status': status}, status=statusCode)


class GetPlaybookPlaylist(APIView):
    playbook  = openapi.Parameter(name='playbook', description="The Playbook name",
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    stage     = openapi.Parameter(name='stage', description="The Playbook Stage",
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    module    = openapi.Parameter(name='module', description="The Playbook Stage Module name in which the testcases are located",
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)      
    @swagger_auto_schema(tags=['/api/v1/playbook/playlist'], operation_description="Get the playlist of a Playbook Stage/Module",
                         manual_parameters=[playbook, stage, module])
    def get(self, request):
        """
        Description:
           Get playbook playlist
        
        GET /api/v1/playbook/playlist?playbook=<playbook>&stage=<stage>&module=<module>
        
        Parameter:
            playbook: The name of the playbook (without the .yml extension)
            stage:  The stage where the playlist is located
            module: Just the module's name.  The playbook/stage/module where the playlist is located
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET 'http://192.168.28.7:8000/api/v1/playbook/playlist?playbook=loadcoreSample&stage=LoadCoreTest&module=LoadCore'
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "playbook=loadcoreSample&stage=LoadCoreTest&module=LoadCore" -H "Content-Type: application/x-www-form-urlencoded" -X GET http://192.168.28.7:8000/api/v1/playbook/playlist 
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"playbook": "loadcoreSample", "stage": "LoadCoreTest", "module": "LoadCore"}' -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/playbook/playlist
                        
        Return:
            the Playbook/Stage/Module playlist
        """     
        statusCode = HtmlStatusCodes.success
        modulePlaylist = []
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        
        if request.GET:
            try:
                playbook = request.GET.get('playbook')
                stage = request.GET.get('stage')
                module = request.GET.get('module')
            except Exception as error:
                errorMsg = f'Expecting parameters apiKey, playbook, stage and module, but got: {request.GET}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                playbook  = request.data['playbook']
                stage  = request.data['stage']
                module = request.data['module']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters apiKey, playbook, stage and module, but got: {request.data}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"playbook": playbook, "stage": stage, "module": module}
            restApi = '/api/v1/playbook/playlist'
            response, errorMsg , status = executeRestApiOnRemoteController('get', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='GetPlaybookPlaylist')
            if errorMsg:
                status = 'failed'
                statusCode = HtmlStatusCodes.success 
            else:
                modulePlaylist = response.json()['playlist'] 
                      
        else:            
            # In case the user included the /Module path.  Get just the module name.
            if 'Modules/' not in module:
                module = f'Modules/{module}'
            if module.startswith('/') == False:
                module = f'/{module}'
            
            if '.yml' not in playbook:
                playbook = f'{playbook}.yml'

            playbookPath = f'{GlobalVars.playbooks}/{playbook}'
            if os.path.exists(playbookPath) == False:
                errorMsg = f'No such playbook exists: {playbookPath}'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='getPlaybookPlaylist', 
                                        msgType='Error', msg='')
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

            try:
                playbookData = readYaml(playbookPath)
                stageAndModuleExists = False
                
                if stage not in playbookData['stages'].keys():
                    errorMsg = f"No such stage in playbook: {stage}"
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='getPlaybookPlaylist', 
                                            msgType='Error', msg=errorMsg)
                    return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

                # Each Stage could have multiple same modules with different env
                for eachModule in playbookData['stages'][stage]['modules']:                      
                    if module in list(eachModule.keys()):
                        stageAndModuleExists = True
                        actualModuleSpellingInPlaybook = list(eachModule.keys())[0]
                        env = eachModule[actualModuleSpellingInPlaybook].get('env', None)
                            
                        if 'playlist' in list(eachModule[module].keys()):
                            playlist = eachModule[actualModuleSpellingInPlaybook]['playlist']
                            modulePlaylist.append({'module': module, 'env': env, 'playlist': playlist})
                        else:
                            errorMsg = f"No playlist defined in playbook:{playbook} stage:{stage}: {module}"
                            SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='getPlaybookPlaylist', 
                                                    msgType='Error', msg=errorMsg)
                            return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)                          

                if stageAndModuleExists == False:
                    errorMsg = f"No such stage:module in playbook:{playbook} stage:{stage}: module:{module}"
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='getPlaybookPlaylist', 
                                                msgType='Error', msg=errorMsg)
                    return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)    
                                        
            except Exception as errMsg:
                errorMsg = errMsg
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='getPlaybookPlaylist', 
                                        msgType='Error', msg=traceback.format_exc(None, errMsg))
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

        return Response(data={'playlist': modulePlaylist, 'status': 'success', 'errorMsg': errorMsg}, status=statusCode)


class GetPlaybooks(APIView):
    playbookGroup  = openapi.Parameter(name='playbookGroup', description="The playbook group",
                                       required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
  
    @swagger_auto_schema(tags=['/api/v1/playbook'], operation_description="Get playbooks from playbook group",
                         manual_parameters=[playbookGroup])
    def post(self, request, data=None):
        """
        Description:
           Get playbooks table data from a playbook group for the playbook page
        
        POST /api/v1/playbook?playbookGroup=<playbookGroup>
        
        Parameter:
            playbookGroup: The name of the playbook group
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/playbook?playbookGroup=<group>
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "playbookGroup=loadcoreSample" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"playbookGroup": "loadcoreSample"}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook
                        
        Return:
            None
        """     
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        tableData: str = ''
        
        if request.GET:
            try:
                # Playbooks/DOMAIN=dagabah/Samples 
                playbookGroup = request.GET.get('playbookGroup')
            except Exception as error:
                errorMsg = f'Expecting parameters apiKey, playbook, stage and module, but got: {request.GET}'
                return Response(data={'tableData': tableData, 'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                # Playbooks/DOMAIN=dagabah/Samples 
                playbookGroup  = request.data['playbookGroup']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters apiKey, playbook, stage and module, but got: {request.data}'
                return Response(data={'tableData': tableData, 'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)
        
        """
        Construct each table <tr> with multiple modules in the <td>
        
        <tr>
            <td>1</td>
            <td>nightly test</td>
            <td>LoadCore<br>AirMosaic</td>
            <td>env.yml<br>rack1.yml</td>
            <td>
                <div class="dropdown">
                    <div class="dropdown-toggle" type="text" data-toggle="dropdown" id="drop1">
                        View Playlist
                        <ul class="dropdown-menu mt-0" aria-labelledby="drop1">
                            <li class="dropdown-item">/Testcases/01_testcase.yml</li>
                            <li class="dropdown-item">/Testcases/02_testcase.yml</li>
                            <li class="dropdown-item">/Testcases/03_testcase.yml</li>
                        </ul>
                    </div>
                </div>
                <div class="dropdown">
                    <div class="dropdown-toggle" type="text" data-toggle="dropdown" id="drop2">
                        View Playlist
                        <ul class="dropdown-menu mt-0" aria-labelledby="drop2">
                            <li class="dropdown-item">/Testcases/01_20UE_NGRAN.yml</li>
                            <li class="dropdown-item">/Testcases/02_80UE_NGRAN.yml</li>
                            <li class="dropdown-item">/Testcases/03_80UE_NGRAN.yml</li>
                        </ul>   
                    </div>
                </div>                    
            </td>
            <td>Yes</td>
            <td>No</td>
        </tr>
        """

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"playbookGroup": playbookGroup}
            restApi = '/api/v1/playbook/get'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPlaybooks')
            tableData = response.json()['tableData']
                       
        else:
            try:
                playbookPath = GlobalVars.playbooks

                # /opt/KeystackTests/Playbooks/DOMAIN=Communal/KeystackQA
                for playbookYmlFile in glob(f'{GlobalVars.keystackTestRootPath}/{playbookGroup}/*'):
                    if os.path.isdir(playbookYmlFile):
                        continue
                    
                    # /opt/KeystackTests/Playbooks/DOMAIN=Communal/qa1.yml
                    if playbookYmlFile.endswith('.yml'):
                        playbookName = playbookYmlFile.split('/')[-1].split('.')[0]
                        tableData += '<tr>'
                        # Delete
                        tableData += f'<td><input type="checkbox" name="playbookCheckboxes" value="{playbookYmlFile}"/></td>'

                        tableData += f'<td><button class="btn btn-sm btn-outline-primary" value="{playbookYmlFile}" onclick="getFileContents(this)" data-bs-toggle="modal" data-bs-target="#viewEditPlaybookModal">View / Edit</button></td>'
                                    
                        tableData += f'<td style="text-align:left">{playbookName}</td>'
                        tableData += '</tr>'
                
                if tableData != '':
                    tableData += '<tr></tr>'
                        
            except Exception as errMsg:
                errorMsg= str(errMsg)
                status = 'failed'
                tableData = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='GetPlaybooks', 
                                          msgType='Error', msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'tableData': tableData, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class CreatePlaybook(APIView):
    playbook  = openapi.Parameter(name='playbook', description="The Playbook name",
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    playbookGroup  = openapi.Parameter(name='playbookGroup', description="The Playbook group",
                                       required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
    jsonObject     = openapi.Parameter(name='jsonObject', description="Playbook contets",
                                       required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)    
    @swagger_auto_schema(tags=['/api/v1/playbook/create'], operation_description="Create a playbook",
                         manual_parameters=[playbook, playbookGroup, jsonObject])

    @verifyUserRole(webPage=Vars.webpage, action='CreatePlaybook', exclude=['engineer'])
    def post(self, request, data=None):
        """
        Description:
           Create a new playbook
        
        POST /api/v1/playbook/create?playbook=<playbook>&playbookGroup=<playbookGroup>&jsonObject=<contents>
        
        Parameter:
            playbook: The name of the playbook (without the .yml extension)
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/playbook/create?playbook
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "newPlaybook=loadcoreSample" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/create
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"newPlaybook": "loadcoreSample", "playbookGroup": "qa", "jsonObject": object}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/create

            curl -H "API-Key: uJNmx1WuSvruOgLUehMJlw" -d '{"newPlaybook": "loadcoreSample", "playbookGroup": "qa", "textArea": {"howdy": "doody"}}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/create                        
        Return:
            None
        """     
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        playbookExists = True
        
        if request.GET:
            try:
                playbook      = request.GET.get('newPlaybook')
                domain        = request.GET.get('domain')
                playbookGroup = request.GET.get('playbookGroup')
                textArea      = request.GET.get('textArea')
            except Exception as errMsg:
                errorMsg = f'Expecting parameters newPlaybook, playbookGroup, textArea, but got: {request.GET}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                # ['/opt/KeystackTests/Playbooks/qa/qa1.yml']
                #  {textArea: textArea, newPlaybook: newPlaybook, playbookGroup:playbookGroup})
                playbook      = request.data['newPlaybook']
                domain        = request.data['domain']
                playbookGroup = request.data['playbookGroup']
                textArea      = request.data['textArea']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters newPlaybook, playbookGroup, textArea, but got: {request.data}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"newPlaybook": playbook, "playbookGroup": playbookGroup, "textArea": textArea}
            restApi = '/api/v1/playbook/create'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='CreatePlaybook')              
        else:
            try:
                if '.yml' not in playbook:
                    playbook = f'{playbook}.yml'

                if playbookGroup:
                    if playbookGroup[0] == '/':
                        playbookGroup = f'{playbookGroup}'
                    
                    playbookGroupPath = f'{GlobalVars.playbooks}/{domain}/{playbookGroup}'
                    if os.path.exists(playbookGroupPath) == False:    
                        mkdir2(playbookGroupPath)
                    
                    fullPathFile = f'{GlobalVars.playbooks}/{domain}/{playbookGroup}/{playbook}'
                    if os.path.exists(fullPathFile) == False:
                        playbookExists = False
                        writeToFile(fullPathFile, textArea, mode='w', printToStdout=False)
                        
                else:
                    playbookGroup = None
                    fullPathFile = f'{GlobalVars.playbooks}/{domain}/{playbook}' 
                    if os.path.exists(fullPathFile) == False:
                        playbookExists = False  
                        writeToFile(fullPathFile, textArea, mode='w', printToStdout=False)
                    
                try:
                    # Verify for YAML synatx error
                    readYaml(fullPathFile)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='VerifyCreatePlaybook', 
                                              msgType='Info',
                                              msg=f'Playbook:{playbook} Group:{playbookGroup}', forDetailLogs='') 
                except Exception as errMsg:
                    status = 'failed'
                    errorMsg = f"Error: YAML syntax error."
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='CreatePlaybook', 
                                              msgType='Error',
                                              msg=errorMsg, forDetailLogs='') 
                
            except Exception as errMsg:
                status = "failed"
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage='playbooks', action='CreatePlaybook', msgType='Error',
                                          msg=errMsg, forDetailLogs=traceback.format_exc(None, errMsg))

            if playbookExists:
                status = 'failed'
                statusCode = HtmlStatusCodes.success
                errorMsg = f'Playbook already exists: {playbook}'
            
        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
class DeletePlaybooks(APIView):
    playbook  = openapi.Parameter(name='playbook', description="The Playbook name",
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
  
    @swagger_auto_schema(tags=['/api/v1/playbook/delete'], operation_description="Delete a list of playbooks",
                         manual_parameters=[playbook])
    @verifyUserRole(webPage=Vars.webpage, action='DeletePlaybook', exclude=['engineer'])
    def post(self, request, data=None):
        """
        Description:
           Delete one or more playbooks
        
        POST /api/v1/playbook/delete?playbook=<playbook>
        
        Parameter:
            playbook: The name of the playbook (without the .yml extension)
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X Delete 'http://192.168.28.7:8000/api/v1/playbook/delete?playbook
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "playbook=loadcoreSample&stage=LoadCoreTest&module=LoadCore" -H "Content-Type: application/x-www-form-urlencoded" -X DELETE http://192.168.28.7:8000/api/v1/playbook/delete
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"playbook": "loadcoreSample"}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/delete
                        
        Return:
            None
        """     
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        
        if request.GET:
            try:
                playbooks = request.GET.get('deletePlaybooks')
            except Exception as error:
                errorMsg = f'Expecting parameters deletePlaybooks, but got: {request.GET}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)
            
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                # ['/opt/KeystackTests/Playbooks/qa/qa1.yml']
                playbooks  = request.data['deletePlaybooks']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters deletePlaybooks, but got: {request.data}'
                return Response(data={'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"deletePlaybooks": playbooks}
            restApi = '/api/v1/playbook/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeletePlaybooks')    
        else:
            try:
                for playbook in playbooks:
                    os.remove(playbook)
                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeletePlaybooks', 
                                              msgType='Info', msg=playbooks)
            except Exception as errMsg:
                errorMsg= str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='DeletePlaybooks', 
                                        msgType='Error', msg=traceback.format_exc(None, errMsg))

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)

    
class IsExists(APIView):
    playbook  = openapi.Parameter(name='playbook', description="The playbook name",
                                  required=True, in_=openapi.IN_QUERY, type=openapi.TYPE_STRING)  
  
    @swagger_auto_schema(tags=['/api/v1/playbook/isExists'], operation_description="Verify if playbook exists",
                         manual_parameters=[playbook])
    def post(self, request, data=None):
        """
        Description:
           Is playbook exists
        
        POST /api/v1/playbook/isExists?playbook=<playbook>
        
        Parameter:
            playbook: Playbook name
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/playbook/isExists?playbook=<playbook>
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d "playbook=loadcoreSample&stage=LoadCoreTest&module=LoadCore" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/isExists
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -d '{"playbook": "loadcoreSample"}' -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/isExists
                        
        Return:
            None
        """     
        statusCode = HtmlStatusCodes.success
        status = 'success'
        error = None
        isExists = True
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        isExists = False
        
        if request.GET:
            try:
                playbook = request.GET.get('playbook')
            except Exception as error:
                errorMsg = f'Expecting parameters playbook, but got: {request.GET}'
                return Response(data={'isExists': False, 'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)
        
        # JSON format
        if request.data:
            # <QueryDict: {'testcasePath': </Modules/LoadCore>}
            try:
                # ['/opt/KeystackTests/Playbooks/qa/qa1.yml']
                playbook  = request.data['playbook']
            except Exception as errMsg:
                errorMsg = f'Expecting parameters playbook, but got: {request.data}'
                return Response(data={'isExists': False, 'errorMsg': errorMsg, 'status': 'failed'}, status=statusCode)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"playbook": playbook}
            restApi = '/api/v1/playbook/isExists'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='IsPlaybookExists')
            isExists = response.json()['exists'] 
                   
        else:            
            try:
                isExists = DB.name.isDocumentExists(collectionName=Vars.webpage, key='playbook', value=f'^{playbook}$', regex=True)        
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                isExists = False
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='isPlaybookExists', 
                                          msgType='Error', msg=errorMsg)

        return Response(data={'exists': isExists, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class PlaybookTemplate(APIView):
    swagger_schema = None
    
    def post(self, request, data=None):
        """
        Description:
           Get playbook template for creating new playbook
        
        POST /api/v1/playbook/template
        
        Parameter:
            None
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/playbook/template
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/template
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/template
                        
        Return:
            None
        """     
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)

        playbookTemplate = """# Playbook template
---
globalSettings:
    abortOnFailure: False
    abortStageFailure: True

stages:
    Test:
        enable: True
        modules:
        - /Modules/Demo:
            enable: True
            #env: None
            playlist:
                - /Modules/Demo/Samples/Bringups/bringupDut1.yml
            """
                                    
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/playbook/template'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                  user, webPage=Vars.webpage, action='PlaybookTemplate')
            playbookTemplate = response.json()['playbookTemplate']
                               
        return Response(data={'playbookTemplate': playbookTemplate, 'status': status, 'errorMsg': errorMsg}, status=statusCode)


class PlaybookGroups(APIView):
    swagger_schema = None
    
    def post(self, request, data=None):
        """
        Description:
           Get playbook groups
        
        POST /api/v1/playbook/groups
        
        Parameter:
            None
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X POST 'http://192.168.28.7:8000/api/v1/playbook/groups
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.7:8000/api/v1/playbook/groups
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X POST http://192.168.28.7:8000/api/v1/playbook/groups
                        
        Return:
            playbook groups in hmtl
        """     
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg= None
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        htmlPlaybookGroups = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/playbook/groups'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='PlaybookGroups')
            htmlPlaybookGroups = response.json()['playbookGroups']
                       
        else:        
            try:
                playbookGroups = []
                trackDomainMenu = []
                userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
                
                for root,dirs,files in os.walk(GlobalVars.playbooks):
                    currentDomain = root.split(f'{GlobalVars.playbooks}/')[-1].split('/')[0].split('=')[-1]
                    
                    # Playbooks/DOMAIN=Sanity/qa/dev
                    playbookGroup = root.split(f'{GlobalVars.keystackTestRootPath}/')[-1]
                    playbookGroupName = '/'.join(playbookGroup.split('/')[2:])
                    totalPlaybooks = len([playbookFile for playbookFile in files if '~' not in playbookFile and 'backup' not in playbookFile])

                    if currentDomain in userAllowedDomains:
                        if currentDomain not in trackDomainMenu:
                            trackDomainMenu.append(currentDomain)
                            htmlPlaybookGroups += f'<p class="pl-2 pt-2 textBlack fontSize12px"><strong>Domain:&ensp;{currentDomain}</strong></p><br>'
                        
                        htmlPlaybookGroups += f'<a class="collapse-item pl-3 fontSize12px" href="/playbooks?group={playbookGroup}">{totalPlaybooks} <i class="fa-regular fa-folder pr-3"></i>{playbookGroupName}</a>'

            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                htmlPlaybookGroups = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='getPlaybookGroups', 
                                          msgType='Error', msg=errorMsg)

        return Response(data={'playbookGroups': htmlPlaybookGroups, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    

class GetPlaybookNames(APIView):
    swagger_schema = None
    
    def post(self, request, data=None):
        """
        Description:
           For sessionMgmt page.
           Get playbook names dropdown that includes the group
           
            [('ixnetwork.yml', '/opt/KeystackTests/Playbooks/ixnetwork.yml'),
             ('/qa/qa1.yml', '/opt/KeystackTests/Playbooks/qa/qa1.yml')
            ]
        
        POST /api/v1/playbook/names
        
        Parameter:
            None
        
        Examples:
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -X GET 'http://192.168.28.7:8000/api/v1/playbook/names
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/x-www-form-urlencoded" -X GET http://192.168.28.7:8000/api/v1/playbook/names
            
            curl -H "API-Key: iNP29xnXdlnsfOyausD_EQ" -H "Content-Type: application/json" -X GET http://192.168.28.7:8000/api/v1/playbook/names
                        
        Return:
            playbook groups in hmtl
        """
        from baseLibs import getPlaybookNames

        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request) 
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        playbookNames = ''
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/playbook/names'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPlaybookNames')
            playbookNames = response.json()['playbookNames']
                       
        else:   
            try:
                userAllowedDomains = userAllowedDomains = DomainMgr().getUserAllowedDomains(user)
                trackDomain = []
                
                for playbookPath in getPlaybookNames():
                    if 'DOMAIN=' not in playbookPath[0]:
                        continue
                    
                    # ('/DOMAIN=Communal/Samples/standalone.yml', '/opt/KeystackTests/Playbooks/DOMAIN=Communal/Samples/standalone.yml')
                    regexMatch = search('DOMAIN=(.+?)/.*', playbookPath[0])
                    if regexMatch:
                        playbookDomain = regexMatch.group(1)
                        if playbookDomain not in userAllowedDomains:
                            continue
                     
                    if playbookDomain not in trackDomain:
                        trackDomain.append(playbookDomain)
                        playbookNames += f'<li class="ml-2"><strong>DOMAIN: {playbookDomain}</strong></li>'
                          
                    playbook = playbookPath[0].split('.')[0]
                    if playbook[0] == '/':
                        # DOMAIN=Sanity/KeystackQA/playbook1
                        playbook = playbook[1:]
            
                    playbookNames += f'<li class="dropdown-item pl-4">{playbook}</li>'
                    
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                playbookNames = ''
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage , action='GetPlaybookNames', 
                                          msgType='Error', msg=errorMsg)

        return Response(data={'playbookNames':playbookNames, 'status': status, 'errorMsg': errorMsg}, status=statusCode)
    
    
# ---- Scheduler ----
 
class AddPlaybookSchedule(APIView):                                           
    @verifyUserRole(webPage=Vars.webpage, action='AddPlaybookSchedule', exclude=['engineer'])
    def post(self, request):
        """ 
        Schedule a cron job
        
            # Example of job definition:
            # .---------------- minute (0 - 59)
            # |  .------------- hour (0 - 23)
            # |  |  .---------- day of month (1 - 31)
            # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
            # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
            # |  |  |  |  |
            # *  *  *  *  * user-name command to be executed
        """
        # body: {'minute': '*', 'hour': '*', 'dayOfMonth': '*', 'month': '*', 'dayOfWeek': '*', 'removeJobAfterRunning': False, 'controller': '192.168.28.7:8000', 'playbook': '/opt/KeystackTests/Playbooks/pythonSample.yml', 'debug': False, 'emailResults': False, 'awsS3': False, 'jira': False, 'pauseOnFailure': False, 'holdEnvsIfFailed': False, 'abortTestOnFailure': False, 'includeLoopTestPassedResults': False, 'sessionId': '', 'domain': 'Communal'}
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        cronjobUser = GlobalVars.user
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None

        minute                = request.data.get('minute', None)
        hour                  = request.data.get('hour', None)
        dayOfMonth            = request.data.get('dayOfMonth', None)
        month                 = request.data.get('month', None)
        dayOfWeek             = request.data.get('dayOfWeek', None)
        
        release_minute        = request.data.get('release_minute', None)
        release_hour          = request.data.get('release_hour', None)
        release_dayOfMonth    = request.data.get('release_dayOfMonth', None)
        release_month         = request.data.get('release_month', None)
        release_dayOfWeek     = request.data.get('release_dayOfWeek', None)
        
        playbooks             = request.data.get('playbooks', None)
        reservationUser       = request.data.get('reservationUser', user)
        removeJobAfterRunning = request.data.get('removeJobAfterRunning', False)

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"minute": minute, "hour": hour, "dayOfMonth": dayOfMonth, "month": month, "dayOfWeek": dayOfWeek, 
                      "release_minute": release_minute, "release_hour": release_hour, "release_dayOfMonth": release_dayOfMonth, 
                      "release_month": release_month, "release_dayOfWeek": release_dayOfWeek,
                      "reservationUser": reservationUser, "removeJobAfterRunning": removeJobAfterRunning}
            restApi = '/api/v1/playbook/scheduler/add'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, request.data, 
                                                                           user, webPage=Vars.webpage, action='AddPlaybookSchedule')
        else:
            try:
                reserveFlag = False
                for reserve in [minute, hour, dayOfMonth, month, dayOfWeek]:
                    if reserve != "*":
                        reserveFlag = True
                        
                releaseFlag = False
                for release in [release_minute, release_hour, release_dayOfMonth, release_month, release_dayOfWeek]:
                    if release != "*":
                        releaseFlag = True
                
                localHostIp = keystackSettings.get('localHostIp', 'localhost')
                keystackIpPort = keystackSettings.get('keystackIpPort', '28028')
                 
                for playbook in playbooks:
                    # env = /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/qa.yml
                    schedule = f'playbook={playbook} minute={minute} hour={hour} day={dayOfMonth} month={month} dayOfWeek={dayOfWeek}' 
                    
                    if JobSchedulerAssistant().isCronExists(playbook, minute, hour, dayOfMonth, month, dayOfWeek):
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPlaybookSchedule', 
                                                  msgType='Failed', msg=f'Cron job already exists: {schedule}')
                        return Response({'status':'failed', 'errorMsg': 'Cron Job already exists'}, status=statusCode)
                
                    # REST API: Run playbook function is in Playbook apiView.py
                    # For job scheduling, include the param -webhook to bypass verifying api-key
                    
                    # crontab command-line
                    newJob = f'{minute} {hour} {dayOfMonth} {month} {dayOfWeek} {cronjobUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&env={playbook}&removeJobAfterRunning={removeJobAfterRunning}&release_minute={minute}&release_hour={hour}&release_dayOfMonth={dayOfMonth}&release_month={month}&release_dayOfWeek={dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X  POST http://{localHostIp}:{keystackIpPort}/api/v1/playbook/reserve'

                    if releaseFlag:
                        # removeJobAfterRunning: {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                        #                         'month': '\\*', 'day': '\\*', 'hour': '17', 'minute': '48', 'dayOfWeek': '\\*'}
                        releaseJob = f'{release_minute} {release_hour} {release_dayOfMonth} {release_month} {release_dayOfWeek} {cronjobUser} curl -d "mainController={mainControllerIp}&remoteController={remoteControllerIp}&reservationUser={reservationUser}&env={playbook}&removeJobAfterRunning=True&release_minute={release_minute}&release_hour={release_hour}&release_dayOfMonth={release_dayOfMonth}&release_month={release_month}&release_dayOfWeek={release_dayOfWeek}&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://{localHostIp}:{keystackIpPort}/api/v1/playbook/release'
                        
                    # Leaving behind for debugging purpose
                    #cronJobs = f"""
                    #{newJob}
                    #* * * * * root date > /proc/1/fd/1 2>/proc/1/fd/2
                    #* * * * * root echo "Hello World! 8" >/proc/1/fd/1 2>/proc/1/fd/2
                    #"""
                    
                    # Put the cronjob in redis for the keystackScheduler to add the cron job
                    # NOTE: keyName for releaseEnv has to be unique because if user selects both reserveEnv and releaseEnv,
                    #       the env keyName is the same. So, using timestamp to make the keyName unique
                    if reserveFlag:
                        if RedisMgr.redis:
                            keyName = f'scheduler-add-{playbook}'                    
                            RedisMgr.redis.write(keyName=keyName, data=newJob)
                    
                    if releaseFlag:
                        if RedisMgr.redis:
                            keyName = f'scheduler-add-{getTimestamp()}-{playbook}'
                            RedisMgr.redis.write(keyName=keyName, data=releaseJob)

                    SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPlaybookSchedule', msgType='Info', msg=newJob.replace('&webhook=true', ''))            
            
            except Exception as errMsg:
                status = 'failed'
                errorMsg = str(errMsg)
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='AddPlaybookSchedule', msgType='Error',
                                          msg=errMsg, forDetailLogs=traceback.format_exc(None, errMsg))

        return Response(data={'status':status, 'errorMsg':errorMsg}, status=statusCode)


class DeleteScheduledPlaybook(APIView):
    @verifyUserRole(webPage=Vars.webpage, action='DeleteScheduledPlaybook', exclude=["engineer"])    
    def post(self, request):
        """ 
        Manually delete scheduled Playbooks in the scheduler
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        removeScheduledPlaybooks = request.data.get('removeScheduledEnvs', None)
        status = 'success'
        statusCode = HtmlStatusCodes.success
        errorMsg = None
        
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {"removeScheduledPlaybooks": removeScheduledPlaybooks}
            restApi = '/api/v1/playbook/scheduler/delete'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='DeleteScheduledPlaybook')
        else:        
            try:
                #  [{env, month, day, hour, min}, {}, ...]
                removeJobList = []
                
                for cron in removeScheduledPlaybooks:
                    # {'jobSearchPattern': 'env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml', 
                    #  'month': '\\*', 'day': '\\*', 'hour': '14', 'minute': '51', 'dayOfWeek': '\\*'}
                    removeJobList.append(cron)
                    
                    # Put the cronjob in redis for the keystackScheduler to remove the cron job
                    if RedisMgr.redis:
                        keyName = f'scheduler-remove-{cron["jobSearchPattern"]}'
                        RedisMgr.redis.write(keyName=keyName, data=cron)
                        
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledPlaybook', msgType='Info',
                                                  msg=cron, forDetailLogs='')
                    else: 
                        SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledPlaybook', msgType='Failed',
                                                  msg='Lost connection to redis server. Failed to remove scheduled job:<br>{cron}', forDetailLogs='')
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='DeleteScheduledPlaybook', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))            

        return Response(data={'status': status, 'errorMsg': errorMsg}, status=statusCode)


class ScheduledPlaybooks(APIView):
    def post(self, request):        
        """         
        Create a data table of scheduled playbooks. Called by html template.
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        status = 'success'
        errorMsg = None
        statusCode = HtmlStatusCodes.success
        playbookSearchName = request.data.get('playbook', 'all')
        html = ''
          
        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/playbook/scheduler/scheduledEnvs'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='ScheduledEnvs')
            html = response.json()['playbookSchedules']
                       
        else: 
            html = '<table class="tableMessages table-bordered">'
            html += '<thead>'
            html += '<tr>'
            html += '<th>Delete</th>'
            html += '<th>User</th>'
            html += '<th>Playbooks</th>'
            html += '<th>Reservation-Schedules</th>'
            html += '<th>Release-Schedules</th>'
            html += '</tr>'
            html += '</thead>'

            try:
                cronjobs = JobSchedulerAssistant().getCurrentCronJobs(searchPattern='playbook=')
                   
                for eachCron in sorted(cronjobs):
                    # Handle the \t: '17 *\t* * *\troot    cd / && run-parts --report /etc/cron.hourly
                    eachCron = eachCron.replace('\t', ' ')
                    # 21 10 * * * keystack curl -d "mainController=192.168.28.10:28028&remoteController=192.168.28.10:28028&user=Hubert Gee&env=/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/airMosaicSample.yml&removeJobAfterRunning=False&webhook=true" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.10:28028/api/v1/env/reserveEnv
 
                    if playbookSearchName != 'all' and playbookSearchName not in eachCron:
                        continue
                                        
                    match = search(' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*reservationUser=(.+)&.*playbook=([^ &]+).*POST *http.+(reserve|release)', eachCron)
                    
                    # 31 11 * * * keystack curl -d "{"mainController": 192.168.28.10:28028, "remoteController": "192.168.28.10:28028", "reservationUser": "Hubert Gee", "env": "/opt/KeystackTests/Envs/DOMAIN=Communal/Samples/bobafett.yml", "removeJobAfterRunning": "False", "webhook": "true"}" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://192.168.28.10:28028/api/v1/env/reserveEnv
                    #match = search(' *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+) *([0-9\*]+).*"reservationUser": "(.+)",.*"env": "([^ ,]+)",.*POST.*(reserveEnv|releaseEnv)', eachCron)
                    if match:
                        min             = match.group(1)
                        hour            = match.group(2)
                        day             = match.group(3)
                        month           = match.group(4)
                        dayOfWeek       = match.group(5)
                        reservationUser = match.group(6)
                        
                        # /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/airMosaicSample.yml
                        playbook             = match.group(7)
                        playbookName         = 'unknown'
                        regexMatch = search('.*DOMAIN=[^ /]+?(/.+)', playbook)
                        if regexMatch:
                            playbookName = regexMatch.group(1)
                        
                        typeOfReservation = match.group(8)
                        
                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="playbookSchedulerMgmt" jobSearchPattern="playbook={playbook}" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        
                        html += f'<td>{reservationUser}</td>'
                        html += f'<td>{playbookName}</td>'
                        
                        if typeOfReservation == 'reserve':
                            html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                            html += '<td></td>'
                            
                        if typeOfReservation == 'release':
                            html += '<td></td>'
                            html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                              
                        html += '</tr>'
                    else:
                        match     = search(' *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+) *([0-9*]+).*', eachCron)
                        min       = match.group(1)
                        hour      = match.group(2)
                        day       = match.group(3)
                        month     = match.group(4)
                        dayOfWeek = match.group(5)
                        
                        html += '<tr>'
                        html += f'<td class="textAlignCenter"><input type="checkbox" name="playbookSchedulerMgmt" jobSearchPattern="" dayOfWeek={dayOfWeek} month={month} day={day} hour={hour} minute={min} /></td>'
                        html += f'<td></td>'
                        html += f'<td></td>'
                        html += f'<td>Hour:{hour}&emsp; Minute:{min}&emsp; Month:{month}&emsp; Date:{day}&emsp; DayOfWeek:{dayOfWeek}</td>'
                        html += '</tr>'
                                            
                html += '</table>'
                
            except Exception as errMsg:
                errorMsg = str(errMsg)
                status = 'failed'
                SystemLogsAssistant().log(user=user, webPage=Vars.webpage, action='ScheduledPlaybooks', msgType='Error',
                                          msg=errorMsg, forDetailLogs=traceback.format_exc(None, errMsg))
        
        return Response(data={'playbookSchedules': html, 'status':status, 'errorMsg':errorMsg}, status=statusCode)
    
 
class GetPlaybookCronScheduler(APIView):
    def post(self, request):
        """
        Dropdowns for minute, hour, day, month, dayOfWeek
        """
        user = AccountMgr().getRequestSessionUser(request)
        mainControllerIp, remoteControllerIp = getMainAndRemoteControllerIp(request)
        statusCode = HtmlStatusCodes.success
        status = 'success'
        errorMsg = None
        minute = ''
        hour = ''
        dayOfMonth = ''
        month = ''
        dayOfWeek = ''

        if remoteControllerIp and remoteControllerIp != mainControllerIp:
            params = {}
            restApi = '/api/v1/playbook/scheduler/getCronScheduler'
            response, errorMsg , status = executeRestApiOnRemoteController('post', remoteControllerIp, restApi, params, 
                                                                           user, webPage=Vars.webpage, action='GetPlaybookCronScheduler')

            minute     = response.json()['minute']
            hour       = response.json()['hour']
            dayOfMonth = response.json()['dayOfMonth']
            month      = response.json()['month']
            dayOfWeek  = response.json()['dayOfWeek']                
        else:
            hour, minute, month, dayOfMonth, dayOfWeek = getSchedulingOptions(typeOfScheduler='reserve')
            schedulerDateTimePicker = f'{hour} {minute} {month} {dayOfMonth} {dayOfWeek}'

            hour, minute, month, dayOfMonth, dayOfWeek = getSchedulingOptions(typeOfScheduler='expiration')
            schedulerExpiresDateTimePicker = f'{hour} {minute} {month} {dayOfMonth} {dayOfWeek}'    
                                     
        return Response(data={'schedulerDateTimePicker': schedulerDateTimePicker,
                              'schedulerExpiresDateTimePicker': schedulerExpiresDateTimePicker,
                              'status':status, 'errorMsg':errorMsg}, status=statusCode)
        