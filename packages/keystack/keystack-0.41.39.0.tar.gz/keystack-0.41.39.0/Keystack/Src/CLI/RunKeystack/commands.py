import click 
import sys
import os
import traceback
from re import search
import datetime
from glob import glob

from globalVars import GlobalVars
from keystackUtilities import readYaml, readJson, writeToJson, execSubprocessInShellMode
from commonLib import getHttpIpAndPort
from runPlaybook import Playbook
from domainMgr import DomainMgr
from accountMgr import AccountMgr
from RedisMgr import RedisMgr
from KeystackUI.execRestApi import ExecRestApi


@click.command()
@click.option('-domain',
              required=False, default=None, type=str,
              help='The domain for the test. If the -playbook param does not include DOMAIN=<domain>, \
                  then default to Communal domain. This means the playbook and envs in playbooks must be using the Communal domain.')

@click.option('-playbook',
              required=False, default=None, type=str, 
              help='The playbook to run: Begins with DOMAIN=<domain>/<playbook>')

@click.option('-pipeline',   
              required=False, default=None, type=str,  
              help='The saved pipeline name to run')

@click.option('-debug',      
              required=False, is_flag=True, 
              help='debug mode')

@click.option('-session_id', 
              required=False, default=None, type=str,  
              help='A name to identify your test')

@click.option('-user',       
              required=False, default=None, type=str,  
              help='For KeystackUI internal use only: Get KeystackUI logged-in user')

@click.option('-api_key',    
              required=False, default=None, type=str,  
              help='User API-Key for CLI secured-mode')

@click.option('-results_folder',   
              required=False, default=None, type=str,  
              help='Internal usage: From KeystackUI')

@click.option('-email_results',   
              required=False, default=False, is_flag=True, 
              help='Send email results at the end of the test')


# multiple=True: --test_configs demo1 --test_configs demo2
@click.option('-test_configs', multiple=True,
              help='Which config file(s) to use to modify test params. Use --test_configs for each file.')

@click.option('-pause_on_failure',   
              required=False, default=False, is_flag=True, 
              help='Pause the test on failure and error for debugging')

@click.option('-hold_envs_if_failed',   
              required=False, default=False, is_flag=True,
              help='Hold the Envs after task completion for debugging if the test failed')

@click.option('-ci',   
              required=False, default=False, is_flag=True,  
              help='Is the test a Continuous Integration')

@click.option('-verbose',   
              required=False, default=False, is_flag=True,  
              help='Show tracebacks for debugging')

@click.option('-include_loop_test_passed_results',   
              required=False, default=False, is_flag=True, 
              help='By default, loop-test passed results are not saved to save storage space.')

@click.option('-abort_test_on_failure',   
              required=False, default=False, is_flag=True,
              help='Abort the test immediately upon a failure')

@click.option('-track_results',   
              required=False, default=False, is_flag=True,
              help='Record result in CSV for graph view')

@click.option('-aws_s3',   
              required=False, default=False, is_flag=True, 
              help='Upload results to AWS S3 data-lake')

@click.option('-jira',   
              required=False, default=False, is_flag=True,
              help='Create/Update Jira issues on failures')

@click.option('-is_from_keystack_ui',   
              required=False, default=False, is_flag=True,
              help='Internal usage: If test is executed from KeystackUI')

# ('-arg1 value1 -arg2 value2',)
@click.option('-app_args',
              required=False,  multiple=True,
              help='Args that you would normally passed into a CLI command app. \
                    Wrap args inside double quotes. For example. Pytest "arg1 value1 arg2 value2"')

# @click.option('-start_lsu', 
#               required=False, is_flag=True,
#               help='For airMosaic app')

# @click.option('-wireshark', 
#               required=False, is_flag=True,
#               help='For Air-Mosaic test tool only: Enable Wirehsark packet capturing')

@click.option('-version',      
              required=False, is_flag=True,
              help='Keystack and docker version')

# kwargs: all the above click.options in a dict
def run(**kwargs):
    """ 
    Parameters for running Keystack
    """
    try:
        runPlaybookObj = RunPlaybook(kwargs)
        runPlaybookObj.checkParams()
        runPlaybookObj.instantiatePlaybook()
        runPlaybookObj.run()
        
    except KeyboardInterrupt:
        isTestAborted = True
        if runPlaybookObj.playbookObj.timestampFolder:
            keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
            
            overallSummaryDataFile = f'{runPlaybookObj.playbookObj.timestampFolder}/overallSummary.json'
            if os.path.exists(overallSummaryDataFile):
                overallSummaryData = readJson(overallSummaryDataFile)
                testStopTime = datetime.datetime.now()
                processId = overallSummaryData['processId']
                sessionId = overallSummaryData['sessionId']
                overallSummaryData['status'] = 'Terminated'
                overallSummaryData['result'] = 'Incomplete'
                overallSummaryData['stopped'] = testStopTime.strftime('%m-%d-%Y %H:%M:%S:%f')
                overallSummaryData['currentlyRunning'] = ''
                overallSummaryData['testAborted'] = True
                overallSummaryData['exceptionErrors'].append('CTRL-C was entered')
                if RedisMgr.redis:
                    runPlaybookObj.playbookObj.overallSummaryData.update(overallSummaryData)
                    runPlaybookObj.playbookObj.updateOverallSummaryFileAndRedis()
                else:
                    writeToJson(overallSummaryDataFile, data=overallSummaryData, mode='w')
                        
                httpIpAddress, keystackIpPort = getHttpIpAndPort()
                execRestApiObj = ExecRestApi(ip=httpIpAddress, port=keystackIpPort)
                
                if execRestApiObj:
                    # .Data/EnvMgmt keeps track of all the current session's envs being used.
                    # This is used in EnvMgmt.py
                    # Create an env mgmt file for each pipeline session to track all the
                    # envs used. This file is used in EnvMgmt to figure out which sessionID
                    # has priority to use the env next in line: 

                    for envMgmtDataFile in glob(f'{runPlaybookObj.playbookObj.timestampFolder}/.Data/EnvMgmt/*.json'):
                        envMgmtData = readJson(envMgmtDataFile)
                        env = envMgmtData['env']
                        envSessionId = envMgmtData['sessionId']
                        envUser = envMgmtData['user']
                        envStage = envMgmtData['stage']
                        envTask = envMgmtData['task']
                        
                        params = {'user':envUser, 'sessionId':envSessionId, 'stage':envStage, 'task':envTask, 'env':env, 'webhook':True}
                        execRestApiObj.post(restApi='/api/v1/env/removeFromActiveUsersListUI', params=params, showApiOnly=True)

                        params = {'removeList': [params], 'env': env, 'webhook': True}
                        execRestApiObj.post(restApi='/api/v1/env/removeEnvFromWaitList', params=params, showApiOnly=True)
                        
                    execRestApiObj.post(restApi='/api/v1/portGroup/updateActiveUsersAndWaitList', params={}, showApiOnly=True)
                        
                print(f'\nCTRL-C aborted: {runPlaybookObj.playbookObj.timestampFolder}\n') 
                                               
                # Terminate the running the process
                if  keystackSettings['platform'] == 'linux':
                    result, process = execSubprocessInShellMode(f'sudo kill -9 {processId}')
                    
                if keystackSettings['platform'] == 'docker':
                    result, process = execSubprocessInShellMode(f'kill -9 {processId}')
                                
    except Exception as errMsg:
        if runPlaybookObj and runPlaybookObj.playbookObj.timestampFolder:
            overallSummaryDataFile = f'{runPlaybookObj.playbookObj.timestampFolder}/overallSummary.json'
            if os.path.exists(overallSummaryDataFile):
                testStopTime = datetime.datetime.now()
                overallSummaryData = readJson(overallSummaryDataFile)
                overallSummaryData['status'] = 'Aborted'
                overallSummaryData['result'] = 'Incomplete'
                overallSummaryData['stopped'] = testStopTime.strftime('%m-%d-%Y %H:%M:%S:%f')
                overallSummaryData['currentlyRunning'] = ''
                overallSummaryData['testAborted'] = True
                overallSummaryData['exceptionErrors'].append(traceback.format_exc(None, errMsg))
                
                if RedisMgr.redis:
                    runPlaybookObj.playbookObj.overallSummaryData.update(overallSummaryData)
                    runPlaybookObj.playbookObj.updateOverallSummaryFileAndRedis()
                else:
                    writeToJson(overallSummaryDataFile, data=overallSummaryData, mode='w')
                
                
class RunPlaybook:        
    def __init__(self, kwargs):
        self.playbookObj = None
        self.testSessionParams = kwargs
    
    def checkParams(self):
        if self.testSessionParams['pipeline']:
            if '.yml' not in self.testSessionParams['pipeline']:
                self.testSessionParams['pipeline'] = f'{self.testSessionParams["pipeline"]}.yml'
            
            pipelineFile = f'{GlobalVars.pipelineFolder}/{self.testSessionParams["pipeline"]}'
            if os.path.exists(pipelineFile) == False:
                sys.exit(f'\nError: No such pipeline: {self.testSessionParams["pipeline"]}\n')
                
            pipelineArgs = readYaml(pipelineFile)

            regexMatch = search(f'DOMAIN=(.*?)/.*', pipelineArgs['playbook'])
            if regexMatch is None:
                sys.exit(f'Playbook {pipelineArgs["playbook"]} did not include the DOMAIN=<domain>')
            
            pipelinePlaybookDomain = regexMatch.group(1) 
                    
            if self.testSessionParams['api_key']:
                apiKeyUser = AccountMgr().getApiKeyUser(self.testSessionParams['api_key'])
                userAllowedDomains = DomainMgr().getUserAllowedDomains(apiKeyUser)
                if pipelinePlaybookDomain not in DomainMgr().getUserAllowedDomains(apiKeyUser): 
                    sys.exit(f'User {apiKeyUser} is not a member of the domain: {pipelinePlaybookDomain}')   
                        
            for key, value in pipelineArgs.items():
                if key == 'pipelineName':
                    continue
                
                if value:
                    if key == 'playbook':
                        match = search('(.*/Playbooks/)?(.*)', value)
                        value = match.group(2)
                        
                    self.testSessionParams.update({key: value})
        else:
            if self.testSessionParams['playbook'] is None:
                sys.exit('\nKeystack.py error: Must include a playbook to run test\n')
        
            if self.testSessionParams['domain'] is None and 'DOMAIN' not in self.testSessionParams['playbook']:
                sys.exit('\nMissing domain.  Include param -domain or include DOMAIN=<domain> in param value -playbook\n')
                
        if len(self.testSessionParams['app_args']) == 0:
            self.appArgs = ''
        else:
            self.appArgs = self.testSessionParams['app_args'][0]

    def instantiatePlaybook(self):
        try:
            self.playbookObj = Playbook(domain = self.testSessionParams['domain'],
                                        user = self.testSessionParams['user'],
                                        cliUserApiKey = self.testSessionParams['api_key'],
                                        playbook = self.testSessionParams['playbook'],
                                        appArgs = self.appArgs,
                                        abortTestOnFailure = self.testSessionParams['abort_test_on_failure'],
                                        emailResults = self.testSessionParams['email_results'],
                                        debug = self.testSessionParams['debug'],
                                        continuousIntegration = self.testSessionParams['ci'],
                                        timestampFolder = self.testSessionParams['results_folder'],
                                        sessionId = self.testSessionParams['session_id'],
                                        pauseOnFailure = self.testSessionParams['pause_on_failure'], 
                                        holdEnvsIfFailed = self.testSessionParams['hold_envs_if_failed'], 
                                        testConfigs = self.testSessionParams['test_configs'],
                                        includeLoopTestPassedResults = self.testSessionParams['include_loop_test_passed_results'],
                                        isFromKeystackUI = self.testSessionParams['is_from_keystack_ui'],
                                        trackResults = self.testSessionParams['track_results'],
                                        awsS3Upload = self.testSessionParams['aws_s3'],
                                        jira = self.testSessionParams['jira'])
        except Exception as errMsg:
            if self.testSessionParams['verbose']:
                sys.exit(f'Keystack error: {traceback.format_exc(None, errMsg)}')
            else:
                sys.exit(f'Keystack error: {errMsg}')
                
    def run(self):
        timestampFolder = self.playbookObj.timestampFolder
        del self.testSessionParams['version']
        self.playbookObj.overallSummaryData['testParameters'] = self.testSessionParams
        
        try:
            result = self.playbookObj.executeStages()
            if result == 'Passed':
                sys.exit(0)
            else:
                sys.exit(1)
                
        except Exception as errMsg:
            if self.testSessionParams['verbose']:
                sys.exit(f'Playbook error: {traceback.format_exc(None, errMsg)}')
            else:
                sys.exit(f'Playbook error : {errMsg}')
                

   