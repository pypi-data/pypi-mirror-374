import os, re, sys, json, datetime
from os import fdopen
from pathlib import Path
from glob import glob
from shutil import rmtree
import subprocess
import traceback
from time import sleep
from pprint import pprint

currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir)
from globalVars import GlobalVars
from Services import Serviceware
from keystackUtilities import readYaml, readJson, writeToJson, execSubprocess, chownChmodFolder, getTimestamp, getRunningContainerTagVersion, execSubprocessInShellMode, removeFile, convertStrToBoolean
from RedisMgr import RedisMgr
from db import DB

try:
    # If the test was executed by UI
    from execRestApi import ExecRestApi
except:
    # If test was executed from CLI
    from KeystackUI.execRestApi import ExecRestApi


class Vars:
    keystackMisc = 'keystackMisc'
    
    
class KeystackException(Exception):
    def __init__(self, msg=None):
        message = f'[Keystack Exception]: {msg}'
        super().__init__(message)
        showErrorMsg = f'\n{message}\n'
        print(showErrorMsg)


def parseForDomain(path):
    regexpMatch = re.search(f'.*DOMAIN=(.+?)/.*', path)
    if regexpMatch:
        return regexpMatch.group(1)
                              
def removePastFoldersBasedOnFolderTimestamp(folder, removeDaysOlderThan=2): 
    """
    Handling folders that has a date and timestamp.

    Examples:
       0 = Deleting starting with today
       1 = Keep today's results. Delete yesterday and beyond.

    Example:
        timestamp folder = /path/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=pythonSample/06-23-2022-12:06:22:953462_<sessionId>
    """     
    today = datetime.datetime.now()

    # /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=Samples-pythonSample
    for root in glob(f'{folder}/*'):
        # /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=pythonSample/06-23-2022-12:06:22:953462_pauseOnError3
        timestampFolderDate = '-'.join(root.split('/')[-1].split('_')[0].split('-')[:-1])
        format = '%m-%d-%Y'
        datetimeObj = datetime.datetime.strptime(timestampFolderDate, format)
        daysDelta = today.date() - datetimeObj.date()
        daysRecorded = daysDelta.days

        if int(daysRecorded) >= int(removeDaysOlderThan):
            try:
                if os.path.exists(f'{root}/overallSummary.json'):
                    overallSummary = readJson(f'{root}/overallSummary.json')
                    timestampFolderName = overallSummary['topLevelResultFolder'].split('/')[-1]

                    # Pipeline is still actively Running
                    pid = overallSummary['processId']
                    isPidExists = execSubprocessInShellMode(f'pgrep {pid}', showStdout=True)[1]
                    if len(isPidExists) > 0 or overallSummary['status'] == 'Running':
                        continue
                            
                    #print('removePastFoldersBasedOnFolderTimestamp:', root)
                    if os.path.isfile(root):
                        os.remove(root)
                        
                        if RedisMgr.redis:
                            redisOverallSummaryKeyName = f'overallSummary-domain={overallSummary["domain"]}-{timestampFolderName}'
                            RedisMgr.redis.deleteKey(keyName=redisOverallSummaryKeyName)
                        
                    if os.path.isdir(root):
                        rmtree(root)
                else:
                    syncRedis = False
                    # No overallSummary file and it's past results.  Remove it.
                    if os.path.isfile(root):
                        os.remove(root)
                        syncRedis = True
                        
                    if os.path.isdir(root):
                        rmtree(root)
                        syncRedis = True
                        
                    if syncRedis:
                        syncTestResultsWithRedis()
                                                
            except Exception as errMsg:
                print(f'removePastFoldersBasedOnFolderTimestamp error: {root}\n{errMsg}')
                pass

def netcat(ipAddress:str, port: str='None'):
    """
    Use netcat to verify ip:port connectivity
    
    nc -vz 10.36.67.37 443
    Ncat: Version 7.91 ( https://nmap.org/ncat )
    Ncat: Connected to 10.36.67.37:443.

    nc -vz 10.36.67.37 5555
    Ncat: Version 7.91 ( https://nmap.org/ncat )
    Ncat: No route to host.
    """
    result = False

    if convertStrToBoolean(port):
        output = execSubprocessInShellMode(f'nc -vz {ipAddress} port {port}', showStdout=False)[1]
        for line in output.split('\n'):
            if 'Ncat: Connected' in line:
                result = True   
    else:
        output = execSubprocessInShellMode(f'nmap {ipAddress}', showStdout=False)[1]
        for line in output.split('\n'):
            if 'Host is up' in line:
                result = True

    return result 
                
def logDebugMsg(msg):
    """ 
    User for logging debug messages inside a Keystack container
    """
    if os.path.exists(GlobalVars.debugLogFilePath) == False:
        with open(GlobalVars.debugLogFilePath, 'w') as fileObj:
            fileObj.write(f'\n')
            
        chownChmodFolder(GlobalVars.debugLogFilePath, GlobalVars.user, GlobalVars.userGroup)
     
    with open(GlobalVars.debugLogFilePath, 'a+', encoding='utf8') as fileObj:
        fileObj.write(f'\n{msg}\n')

def logSession(sessionLogFile, msg):
    """ 
    sessionLogFile: <timestampFolder>/<GlobalVars.sessionLogFilename>
    """
    if os.path.exists(sessionLogFile) == False:
        with open(sessionLogFile, 'w') as fileObj:
            fileObj.write(f'\n')
            
        chownChmodFolder(sessionLogFile, GlobalVars.user, GlobalVars.userGroup)
    
    with open(sessionLogFile, 'a+') as fileObj:
        fileObj.write(f'{getTimestamp()}: {msg}\n\n')
                        
def getHttpIpAndPort() -> tuple:
    """ 
    Get the HTTP/HTTPS method, web server IP and IP Port
    from /path/KeystackSystem/keystackSystemSettings.env
    """
    keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    httpIpAddress = keystackSettings.get('localHostIp', '0.0.0.0')
    keystackIpPort = keystackSettings.get('keystackIpPort', '28028')
    return (httpIpAddress, keystackIpPort)
        
def isKeystackUIAlive(ip:str, port:str, headers: dict={}, verifySslCert:bool=False, 
                      timeout:int=3, keystackLogger:object=None):
    """ 
    Check if the web UI server is alive.
    For EnvMgmt: If envs with parallelUsage=True
    
    Return:
       passed or failed == True|False
       https = True|False  <-- dynamically figure out the http protocol to use for the rest of the test
    """
    try:
        execRestApiObj = ExecRestApi(ip=ip, port=port, headers=None, verifySslCert=verifySslCert,
                                    https=False, keystackLogger=keystackLogger)
        
        response = execRestApiObj.post(restApi='/api/v1/system/ping', timeout=timeout, 
                                       maxRetries=1, ignoreError=False, silentMode=False)

        if response and response.status_code == 200:
            # 0:True=passed, 1:True=https is true
            return (True, execRestApiObj)
        else:
            return (False, None)
        
    except Exception as errMsg:
        execRestApiObj = ExecRestApi(ip=ip, port=port, headers=None, verifySslCert=verifySslCert,
                                     https=True, keystackLogger=keystackLogger)
        response = execRestApiObj.post(restApi='/api/v1/system/ping', timeout=timeout, 
                                       maxRetries=1, ignoreError=True, silentMode=False)

        if response and response.status_code == 200:
            # 0:True=failed, 1:True=https is false
            return (True, execRestApiObj)
        else:
            return (False, None)
        
    else:
        return (False, None)

def removeGunicornErrorLogFile():
    try:
        if os.path.exists('/var/log/gunicorn/error.log'):
            removeFile('sudo /var/log/gunicorn/error.log')
    except:
        pass
    
def removeNginxErrorLogFile():
    try:
        if os.path.exists('/var/log/nginx/error.log'):
            removeFile('sudo /var/log/nginx/error.log')
    except:
        pass

def isCliInsideContainer():
    """
    Enter docker ps -a
    Container doesn't have docker installed
    docker command will fail.  Return False.
    Return True if the command works
    """
    dockerExists = False
    
    try:
        result, output = execSubprocess(['docker', 'ps'])
    except FileNotFoundError:
        # Executing keystack inside docker container: 
        # FileNotFoundError: [Errno 2] No such file or directory: 'docker'
        return True
    
    for line in output.split('\n'):
        # Should fail inside a container
        regexMatch = re.search('.*command not found.*', line)
        if regexMatch:
            dockerExists = True

    return dockerExists
            
def getDockerInternalMongoDBIpAddress(searchPattern):
    """
    If executing Keystack in host CLI and docker container is running,
    get the docker internal IP address for the MongoDB.
    
    If executing Keystack inside the docker container, then use
    the mongo DB docker compose hostname: keystackMongoDBHostname
    from keystackSystemSettings.env
    
    - docker network ls
    - docker inspect <MongoDB bridge ID>
    
    "Containers": {
        "2224d4acc75d314df7cc1b32d456289509008c52a97dada77bcad2502228e1dd": {
            "Name": "keystack",
            "EndpointID": "50a76201a4180dbba4bb52e40539469bc01c58da1a589273ca0716c9ca89e6ae",
            "MacAddress": "02:42:ac:1b:00:03",
            "IPv4Address": "172.27.0.3/16",
            "IPv6Address": ""
        },
        "f91e9af5a0d192f6ef8551078280feb879cad3bb93f6442ae5568efe7bb6fafa": {
            "Name": "mongo",
            "EndpointID": "5102e8dcf10e6b6a58605c776afaa75d35f18382dd44b5131719c3da037f148c",
            "MacAddress": "02:42:ac:1b:00:02",
            "IPv4Address": "172.27.0.2/16",
            "IPv6Address": ""
        }
    }
    
    Params:
       searchPattern: What to search for on "docker network ls"
                      Output Example: keystacksetup_0250_keystack-net
                      Note: to get container ip from the host:
                            docker inspect <container ID> | grep "IPAddress"
    """
    mongoDBBridge = None
    mongoDockerIp = None

    try:
        result, output = execSubprocess(['docker', 'network', 'ls'])
    except FileNotFoundError:
        # Executing keystack inside docker container: 
        # FileNotFoundError: [Errno 2] No such file or directory: 'docker'
        return None
    
    for line in output.split('\n'):
        regexMatch = re.search(f'([^ ]+) +{searchPattern} .*', line)
        if regexMatch:
            mongoDBBridge = regexMatch.group(1)
            break

    if mongoDBBridge:
        result, output = execSubprocess(['docker', 'inspect', mongoDBBridge])

        mongodb = json.loads(output)[0]
        for key, value in mongodb['Containers'].items():
            if value['Name'] == 'mongo':
                mongoDockerIpAndPrefix = value['IPv4Address']
                mongoDockerIp = mongoDockerIpAndPrefix.split('/')[0]
                print(f'\nMongoDockerInternalIp: {mongoDockerIp}')
                break

    return mongoDockerIp
         
# This function needs to be on its own so KeystackUI could use it too
def createTestResultTimestampFolder(domain: str=None, playbookName: str=None, 
                                    sessionId: str=None, debugMode: bool=False) -> str:
    """ 
    Create a unique timestamp folder to store each test results and logs
    
    playbookName: Ex: DOMAIN=Communal-Samples-advance
    """
    playbookName = playbookName.replace('/', '-')
    stdout = False
    user = execSubprocessInShellMode('whoami', showStdout=False)[1].replace('\n', '')
    userGroup = GlobalVars.userGroup
    resultsRootFolder = f'{GlobalVars.keystackTestRootPath}/Results'
    
    if os.path.exists(resultsRootFolder) == False:
        execSubprocess(['mkdir', '-p', resultsRootFolder], stdout=stdout)
        chownChmodFolder(resultsRootFolder, user, userGroup, stdout=stdout)
        execSubprocess(['chmod', 'g+s', resultsRootFolder], stdout=stdout)
     
    # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance
    resultsPlaybookLevelFolder = f'{resultsRootFolder}/DOMAIN={domain}/PLAYBOOK={playbookName}'
    
    if os.path.exists(resultsPlaybookLevelFolder) == False:
        execSubprocess(['mkdir', '-p', resultsPlaybookLevelFolder], stdout=stdout)
        execSubprocess(['chmod', '770', resultsPlaybookLevelFolder], stdout=stdout)
        execSubprocess(['chown', f'{user}:{userGroup}', resultsPlaybookLevelFolder], stdout=stdout)
        execSubprocess(['chmod', 'g+s', resultsPlaybookLevelFolder], stdout=stdout)
            
    # Create a timestamp test folder
    todayFolder = getTimestamp()
      
    if debugMode:
        timestampFolder = f'{resultsPlaybookLevelFolder}/{todayFolder}_{sessionId}_debug'
    else:
        timestampFolder = f'{resultsPlaybookLevelFolder}/{todayFolder}_{sessionId}'

    execSubprocess(['mkdir', '-p', timestampFolder], stdout=False)
    
    # /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/04-12-2024-13:24:29:701951_4707
    return timestampFolder

def showVersion(stdout=True) -> list:
    """
    Show the Keystack framework version and the running docker container versions
    """
    runningDockerVersions = None
    
    try:
        runningDockerVersions = getRunningContainerTagVersion(containerName='keystack')
    except:
        pass
       
    if os.path.exists(GlobalVars.versionFile):
        contents = readYaml(GlobalVars.versionFile)
        if stdout:
            print(f'\nKeystack framework version=={contents["keystackVersion"]}')

    if runningDockerVersions:
        if stdout:
            print(f'Running docker container versions: {runningDockerVersions}\n')
    
    if stdout:
        print() 
           
    return (contents["keystackVersion"], runningDockerVersions)
    
def getLoginCredentials(loginCredentialKey):
    credentialYmlFile = f'{GlobalVars.loginCredentials}'

    if os.path.exists(credentialYmlFile) == False:
        raise Exception(f'Login credentials file not found: {credentialYmlFile}.')
    
    try:
        loginCredentialObj = readYaml(credentialYmlFile)
        
        if loginCredentialKey in list(loginCredentialObj.keys()):
            loginCredentials = loginCredentialObj[loginCredentialKey]
        else:
            loginCredentials = None
    except Exception as errMsg:
        raise Exception(errMsg)
    
    return loginCredentials
           
def generateManifestFile(resultsTimestampFolder: str, s3BucketName: str, awsRegion: str) -> str:
    """ 
    Create manifest.mf for S3 URLS
    
    resultsTimestampFolder <str>: The test top-level result folder to walk through
    """
    s3ManifestFilePath = f'{resultsTimestampFolder}/MANIFEST.mf'
    open(s3ManifestFilePath, 'w').close()
    versionFileContents = readYaml(GlobalVars.versionFile)
    s3ManifestContents = {'keystackVersion': versionFileContents['keystackVersion']}
            
    #s3HttpHeader = f"https://{os.environ['keystack_awsS3BucketName']}.s3.{os.environ['keystack_awsRegion']}.amazonaws.com"
    s3HttpHeader = f"https://{s3BucketName}.s3.{awsRegion}.amazonaws.com"
    
    for root, dirs, files in os.walk(resultsTimestampFolder):
        if 'JSON_KPIs' in root:
            # Don't insert a S3 URL for every KPI. There are over 600 KPIs.
            # The manifest file becomes enormous and in a loop test, this slows down
            # the test drastically.
            continue
                
        # root: /path/KeystacTests/kResults/PLAYBOOK=L3Testing/05-10-2022-10:33:29:705277_<sessionId>/STAGE=Bringup_MODULE=Bringups_ENV=None/dut1
        match = re.search('.*(PLAYBOOK.*)', root)
        if match:
            folder = match.group(1)
            s3FolderUrlPath = f"{folder}".replace(':', '%3A').replace('=', '%3D')
                    
            if files:
                s3FileList = []
                for eachFile in files:
                    if 'metadata.json' in eachFile:
                        continue
                    
                    # s3UrlObj:
                    # https://<bucketName>.s3.<region>.amazonaws.com/PLAYBOOK%3DL3Testing/05-10-2022-07%3A55%3A49%3A276512_<sessionId>/STAGE%3DTeardown_MODULE%3DCustomPythonScripts_ENV%3DNone/moduleTestReport
                    s3FileObj = f"{s3HttpHeader}/{s3FolderUrlPath}/{eachFile}"
                    s3FileList.append(s3FileObj)
                    if 'MANIFEST' in eachFile:
                        awsS3ManifestUrl = s3FileObj
                        
                s3ManifestContents.update({folder: {'files': s3FileList}})

    writeToJson(s3ManifestFilePath, s3ManifestContents, mode='w')
    return s3ManifestFilePath
        
def informAwsS3ServiceForUploads(playbookName, sessionId, resultsTimestampFolder, listOfFilesToUpload,
                                 loginCredentialPath, loginCredentialKey, logFile=None):
    """ 
    Create a timestamp json file containing a list of result paths to upload to S3
    
    sessionId <str>: The sessionId to include in the json filename to identify 
                     from which test it came from.
    
    resultsTimestampFolder: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/05-01-2025-07:33:28:950224_3596                 
    listOfFilesToUpload: A list of files and/or folders to upload
    
    aloginCredentialKey: The login credential yml fil key to use.
    
    logFile: Testcase log file
    """
    # NOTE!!  This must be consistent with keystackAwsS3.py
    # /opt/KeystackSystem/ServicesStagingArea/AwsS3Uploads/PLAYBOOK=DOMAIN=Communal-Samples-advance_05-01-2025-07:30:44:894723.json
    messageForAwsS3Service = f'{Serviceware.vars.awsS3StagingFolder}/PLAYBOOK={playbookName}_{getTimestamp()}.json'
    data = {'artifactsPath': listOfFilesToUpload, 'loginCredentialPath': loginCredentialPath, 'resultsTimestampFolder': resultsTimestampFolder,
            'playbookName':playbookName, 'sessionId': sessionId, 'loginCredentialKey': loginCredentialKey}

    awsS3ServiceObj = Serviceware.KeystackServices(typeOfService='keystackAwsS3')
    
    # NOTE!!  This must be consistent with keystackAwsS3.py 
    # /opt/KeystackSystem/Logs/PLAYBOOK=DOMAIN=Communal-Samples-advance_/opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance/05-01-2025-07:30:31:331148_8030.json
    #awsS3LogFile = f'{Serviceware.vars.keystackServiceLogsFolder}/PLAYBOOK={playbookName}_{resultsTimestampFolder}.json'
    awsS3LogFile = f'{resultsTimestampFolder}.json'
    msg = f'[informAwsS3ServiceForUploads]: {messageForAwsS3Service}'

    if awsS3ServiceObj.debugEnabled():
        awsS3ServiceObj.writeToServiceLogFile(msgType='debug', msg=msg, playbookName=playbookName, sessionId=sessionId, logFile=awsS3LogFile)
            
    for eachFile in listOfFilesToUpload:
        msg += f'\n\t- {eachFile}\n'
        
    print(f'informAwsS3ServiceForUploads: {msg}')
    
    # /opt/KeystackSystem/ServicesStagingArea/AwsS3Uploads/hgee2-04-10-2023-08:46:28:628596.json
    if os.path.exists(messageForAwsS3Service) == False:
        mode = 'w'
    else:
        mode = 'w+'
               
    writeToJson(jsonFile=messageForAwsS3Service, data=data, mode=mode)

def validatePlaylistExclusions(playlistExclusionList:list) -> tuple:
    """ 
    Verify playbook module playlist exclusions
    
    Return:
        1> problems
        2> excludeTestcases (list of full path testcase yaml files)
    """
    problems = []
    excludeTestcases = []
    
    # Verify excludes
    for eachExcludedTestcase in playlistExclusionList:
        regexMatch = re.search('.*((Modules|Testcases)/.*)', eachExcludedTestcase)
        if regexMatch:
            eachPath = f'{GlobalVars.keystackTestRootPath}/{regexMatch.group(1)}'
                            
            if eachPath.endswith('.yml') is False:
                eachPath = f'{eachPath}.yml'

            if os.path.isfile(eachPath):
                if os.path.exists(eachPath) == False:
                    problems.append(f'excludeInPlaylist error: No such path: {eachPath}')
                else:
                    excludeTestcases.append(eachPath)
       
            if os.path.isdir(eachPath):
                for root, dirs, files in os.walk(eachPath):
                    # root ex: starting_path/subFolder/subFolder
                    if files:
                        for eachFile in files:
                            if root[-1] == '/':
                                excludeTestcases.append(f'{root}{eachFile}')
                            else:
                                excludeTestcases.append(f'{root}/{eachFile}')
        else:
            problems.append(f'excludeInPlaylist error: Exepcting /Modules or /Testcases, but got {eachExcludedTestcase}')

    return problems, excludeTestcases
        
def validatePlaylist(playlist:list, playlistExclusions: list=[]) -> list:
    """
    Validate each testcase yaml file for ymal error.

    Parameters:
        playlistExclusions: <list|None>: If the playlist is a folder, users could 
                            exclude a list of testcase subfolders and files
    """
    from pathlib import Path
    
    testcaseSortedOrderList = []
    playlistProblems = []
    
    verifyExclusionsProblems, excludeTestcases = validatePlaylistExclusions(playlistExclusions)
    
    for eachPath in playlist:
        regexMatch = re.search('.*((Modules|Testcases)/.*)', eachPath)
        if regexMatch:
            eachPath = f'{GlobalVars.keystackTestRootPath}/{regexMatch.group(1)}'
        else:
            playlistProblems.append(f'{eachPath}: Must begin with /Modules or /Testcases.')
            continue
        
        if Path(eachPath).is_dir():
            # Run all file in folders and subfolders

            for root, dirs, files in os.walk(eachPath):
                # root ex: starting_path/subFolder/subFolder
                if files:
                    # Store files in numerical/alphabetic order
                    for eachFile in sorted(files):
                        if eachFile[-1] == '/':
                            # Testcase folder.  Not a file
                            eachFile = f'{root}{eachFile}'
                        else:
                            if root[-1] == '/':
                                eachFile = f'{root}{eachFile}'
                            else:
                                eachFile = f'{root}/{eachFile}'
                            
                        # Testcases/Nokia/nokia.yml
                        currentFilename = eachFile.split('/')[-1]

                        if eachFile in excludeTestcases:
                            continue
                                                
                        if bool(re.search('.*(#|~|backup|readme|__init__|pyc)', currentFilename, re.I)):
                            continue

                        # Not all testcases use the yml file method.  Such as custom python scripts.
                        if eachFile.endswith('.yml') or eachFile.endswith('.yaml'):
                            try:
                                readYaml(eachFile)
                            except Exception as errMsg:
                                playlistProblems.append(f'{eachFile}: {errMsg}')
                                
                        testcaseSortedOrderList.append(f'{eachFile}')
                        
        else:
            if eachPath.endswith('.yml') or eachPath.endswith('.yaml'):
                if eachPath in excludeTestcases:
                    continue
                
                if os.path.exists(eachPath) == False:
                    playlistProblems.append(f'Testcase path does not exists: {eachPath}')
                else:
                    # Run individual testcase yml file. Don't read .py files
                    try:
                        readYaml(eachPath)
                    except Exception as errMsg:
                        playlistProblems.append(f'{eachPath}: {errMsg}')
    
            testcaseSortedOrderList.append(eachPath)
               
    return playlistProblems
        
def validatePlaybook(playbook:str, playbookObj:dict, checkLoginCredentials:bool=False):
    """ 
    playbook: <str>: /opt/KeystackTests/Playbooks/DOMAIN=Communal/Samples/advance.yml
    playbookObj: <dict>: The playbook Yaml file data
    checkLoginCredentials: <bool>: If the test includes -awsS3 and or -jira
    
    - Validate the Yaml files for Playbook and the Envs
    
    - It is illegal to create a playbook with the same module and same env within the same stage
      because the results folder will be overwritten by the latter:
        STAGE=Test_TASK=CustomPythonScripts_ENV=qa
    
        Solution: 
            - Simply add the testcase to the playlist
            - Or put the module under a different stage 
    """
    globalApp = None  
    globalEnv = None
    loginCredentialKey = None
    checkList = ''
    validationPassed = True
    playbookDomain = None
    
    # Gather up all the Stage/Modules to run
    runList = []
    # A list of all the problems
    problems = []
    
    if playbookObj is None:
        problems.append(f'The playbook is empty: {playbook}')
        return False, problems
    
    if 'globalSettings' in playbookObj.keys():
        globalApp = playbookObj['globalSettings'].get('app', None)   
        globalEnv = playbookObj['globalSettings'].get('env', None)
        loginCredentialKey = playbookObj['globalSettings'].get('loginCredentialKey', None)
    
    playbookDomainSearch = match = re.search(f'.*DOMAIN=(.+?)/(.*)(\.yml)?', playbook) 
    if playbookDomainSearch:
        playbookDomain = playbookDomainSearch.group(1)
  
    if globalEnv and globalEnv != 'not-required':
        if '-' in globalEnv:
            problems.append(f'playbook:{playbook} -> Playbook Global Settings error: Env name cannot have dashes: {globalEnv}')
            
        if bool(re.search('.*\s+.*', globalEnv)):
            problems.append(f'playbook:{playbook} -> Playbook Global Settings error : Env name cannot have spaces: {globalEnv}')
    
        if bool(re.search('.*DOMAIN.+', globalEnv)) is False:
            problems.append(f'playbook:{playbook} -> Playbook Global Settings error: Env name must begin with DOMAIN={GlobalVars.defaultDomain} or DOMAIN={playbookDomain}: {globalEnv}')
        else:
            globalEnvDomainMatch = re.search(f'.*DOMAIN=(.+?)/(.*)(\.yml)?', globalEnv)  
            globalEnvDomain = globalEnvDomainMatch.group(1)
            if globalEnvDomain not in [GlobalVars.defaultDomain, playbookDomain]:
                problems.append(f'playbook:{playbook} -> Playbook Global Settings error: You could only use default DOMAIN={GlobalVars.defaultDomain} or the playbook DOMAIN={playbookDomain}. {globalEnv}')
                 
    # Validate login credentials
    if checkLoginCredentials:
        if loginCredentialKey is None:
            problems.append('- You included -awsS3 and/or -jira, but the loginCredentials in playbook globalSettings did not define which login-credential-key to use.')
    
        if os.path.exists(GlobalVars.loginCredentials) == False:
            problems.append('- The loginCredentials file does not exists.')
        else:
            loginCredentials = readYaml(GlobalVars.loginCredentials)
            if loginCredentialKey not in loginCredentials:
                problems.append(f'- The loginCredentialKey "{loginCredentialKey}" that is defined in the playbook for the test does not exist in loginCredentials file.')
                             
    for stage in playbookObj['stages'].keys():
        if playbookObj['stages'][stage].get('enable', True) in [False, 'False', 'false', 'No', 'no']:
            continue
        
        stageEnv = playbookObj['stages'][stage].get('env', None)
        stageApp = playbookObj['stages'][stage].get('app', None)

        if stageEnv and stageEnv != 'not-required':
            if '-' in stageEnv:
                problems.append(f'playbook:{playbook} -> Playbook Stage {stage} error: Env name cannot have dashes: {stageEnv}')

            if bool(re.search('.*\s+.*', stageEnv)):
                problems.append(f'playbook:{playbook} -> Playbook Stage {stage} error: Env name cannot have spaces: {stageEnv}')
        
            if bool(re.search('.*DOMAIN.+', stageEnv)) is False:
                problems.append(f'playbook:{playbook} -> Playbook Stage {stage} error: Env name must begin with DOMAIN={GlobalVars.defaultDomain} or DOMAIN={playbookDomain}: {stageEnv}')
            else:
                stageEnvDomainMatch = re.search(f'.*DOMAIN=(.+?)/(.*)(\.yml)?', stageEnv)  
                stageEnvDomain = stageEnvDomainMatch.group(1)
                if stageEnvDomain not in [GlobalVars.defaultDomain, playbookDomain]:
                    problems.append(f'playbook:{playbook} -> Playbook Stage error: You could only use default DOMAIN={GlobalVars.defaultDomain} or the playbook DOMAIN={playbookDomain}. {stageEnv}')
                                
        # Validate apps and envs     
        for task in playbookObj['stages'][stage]['tasks']:
            # {'/Modules/CustomPythonScripts': {'enable': True, 'env': 'None', 'playlist': ['/Modules/CustomPythonScripts/Samples/Bringups']}}
            for taskName, properties in task.items():
                if properties.get('enable', True) in [False, 'False', 'false', 'No', 'no']:
                    continue

                taskEnv = properties.get('env', None)
                                
                if 'env' in properties:
                    if taskEnv and taskEnv != 'not-required':
                        if '-' in taskEnv:
                            problems.append(f'- playbook:{playbook} -> Playbook Stage:[{stage}] Task:[{taskName}] error: Env name cannot have dashes: {taskEnv}')
                            
                        if bool(re.search('.*\s+.*', taskEnv)):
                            problems.append(f'- playbook:{playbook} -> Playbook Stage:[{stage}] Task:[{taskName}] error: Env name cannot have spaces: {taskEnv}')

                        if bool(re.search('.*DOMAIN.+', taskEnv)) is False:
                            problems.append(f'- playbook:{playbook} -> Playbook Stage:[{stage}] Task:[{taskName}] error: Env name must begin with DOMAIN={GlobalVars.defaultDomain} or DOMAIN={playbookDomain}: {taskEnv}\n\n')
                        else:
                            taskEnvDomainMatch = re.search(f'.*DOMAIN=(.+?)/(.*)(\.yml)?', taskEnv)  
                            taskEnvDomain = taskEnvDomainMatch.group(1)
                            if taskEnvDomain not in [GlobalVars.defaultDomain, playbookDomain]:
                                problems.append(f'playbook:{playbook} -> Playbook Stage:{stage} Task:{task} error: You could only use default DOMAIN={GlobalVars.defaultDomain} or the playbook DOMAIN={playbookDomain}. {taskEnv}')

                playlistExclusions = properties.get('excludeInPlaylist', [])
                if playlistExclusions:
                    problems += validatePlaylist(playlist=properties['playlist'], playlistExclusions=playlistExclusions)
                       
    if validationPassed and len(problems) == 0:
        return True, None
    
    if validationPassed == False:
        problems.append(f'- User error. Modules in the same stage must use different Envs. You might have set the env in globalSettings or at the Stage level that defaulted all the Modules within a Stage: {checkList}')
               
    if len(problems) > 0:
        #print(f'ValidatePlaybook Problems: {problems}')
        return False, problems
    
    sys.exit()
    
def getRunList(playbookDomain:str, playbookTasksObj:dict, user:str=None,
               userApiKey:str=None, execRestApiObj:object=None, playbookObj:object=None) -> list:
    """
    Get a list of all the enabled Stages/Modules/Envs for sessionMgmt
    to show what is expected to run next
    
    Verifying user and userApiKey for permission to use the envs' in 
    different domains in the playbook:
        - This function checks each env used in the playbook and this verifies
        - If the user/userApiKey is a user-group member in the specified env domain.
        - Running Keystack on the CLI without including the user api-key will not be verified
          because the Linux OS usernames are different in the Keytack user account
        - For env mgmt, users must include their api-key if running keystack on CLI.
        - If tests are executed from the Keystack UI or using rest-api to run playbooks, this 
          will be accepted.
    """
    runList = []
    
    if 'globalSettings' in playbookTasksObj and playbookTasksObj['globalSettings'].get('env', None):
        globalEnv = playbookTasksObj['globalSettings']['env']
        globalEnv = envFileHelper(playbookDomain, globalEnv, user, userApiKey, execRestApiObj, playbookObj)
    else:
        globalEnv = None
        
    for stage in playbookTasksObj['stages'].keys():
        if playbookTasksObj['stages'][stage].get('enable', True) == False:
            continue
 
        if playbookTasksObj['stages'][stage].get('env', None):
            stageEnv = playbookTasksObj['stages'][stage]['env']
            stageEnv = envFileHelper(playbookDomain, stageEnv, user, userApiKey, execRestApiObj, playbookObj)
        else:
            stageEnv = None
            
        autoTaskName = 1   
        for task in playbookTasksObj['stages'][stage]['tasks']:
            # {'/Modules/CustomPythonScripts': {'enable': True, 'env': 'None', 
            #  'playlist': ['/Modules/CustomPythonScripts/Samples/Bringups']}}
            for taskName, properties in task.items():
                if properties.get('enable', True) in [False, 'False', 'false', 'No', 'no']:
                    continue
        
                taskName = taskName.split('/')[-1]

                if properties.get('env', None):
                    env = properties['env']
                    env = envFileHelper(playbookDomain, env, user, userApiKey, execRestApiObj, playbookObj)    
                elif stageEnv:
                    env = stageEnv
                elif globalEnv:
                    env = globalEnv
                else:
                    env = None
                  
                if env:
                    # Get the env name with the namespace
                    regexMatch = re.search(f'.+/Envs/(.+)\.(yml|yaml)?', env)
                    if regexMatch:
                        env = regexMatch.group(1)
                
                autoTaskName += 1
                runList.append({'stage': stage, 'task': taskName, 'env': env})
    
    return runList
                
def envFileHelper(playbookDomain:str, envFile:str, user:str=None,
                  userApiKey:str=None, execRestApiObj:object=None,
                  playbookObj:object=None, bypassEnvDomainChecking:bool=False) -> str:
    """
    Helper function for the Playbook class.  Returns the env file full path.
    If the env domain is different from the playbook's domain, check if the running user
    is a member of a User-Group associated with the env domain.
    
    If the env doesn't include DOMAIN, default the env in the playbook's domain.
    """
    # envFile: Envs/DOMAIN=Communal/Samples/demoEnv
    if envFile in ['None', None, '']:
        return None
        
    if envFile == 'not-required':
        return 'not-required'
    
    if 'yml' not in envFile:
        envFile1 = f'{envFile}.yml'

    envDomain = None
    
    # Get just the file name after DOMAIN= path
    match = re.search(f'.*DOMAIN=(.+?)/(.*)(\.yml)?', envFile)
    if match:
        envDomain = match.group(1)
        envGroup = match.group(2)
    else:
        match2 = re.search(f'(.*)(\.yml)?', envFile)
        if match2:
            envDomain = playbookDomain
            envGroup = match2.group(1)

    if 'yml' not in envGroup:
        envGroupWithYmlExtension = f'{envGroup}.yml'
    
    #if bypassEnvDomainChecking is False and envDomain and envDomain != playbookDomain:
    if bypassEnvDomainChecking is False and envDomain and envDomain not in [GlobalVars.defaultDomain, playbookDomain]:
        # Check if the user who is running the test is a member 
        # of the user-group that belongs to the playbook domain
        # 1> What is the env domain
        # 2> Get all user-groups associated with the env domain
        # 3> Check if user is in any of the user-groups
        
        result = isUserAllowedInDomain(envDomain, user, userApiKey, execRestApiObj)
        if result is False:
            playbookObj.overallSummaryData['pretestErrors'].append(f'- The running playbook domain is "{playbookDomain}". One of the tasks specified an env in a domain different from the playbook domain and the Communal domain: {envFile1}.  You are only allowed to use envs from Communal domain or from the Playbook domain.')

    # /opt/KeystackTests/Envs/DOMAIN=Communal/Samples/demoEnv3.yml
    envFileFullPath = f'{GlobalVars.envPath}/DOMAIN={envDomain}/{envGroupWithYmlExtension}'
    if os.path.exists(envFileFullPath) == False:
        raise Exception(f'No such env found in playbook: {envFileFullPath}')
    
    return envFileFullPath

def isUserAllowedInDomain(domain:str=None, user:str=None, userApiKey:str=None, execRestApiObj:object=None): 
    """ 
    curl -H "API-Key: 6FGjMjVqPdQq4D6elqE0dQ" -d '{"domain": "KeystackQA", "user": user, "apiKey": "MapuIJcGvG--HCQIVs2RMQ"}' 
    -H "Content-Type: application/json" -X POST http://keystack/api/v1/system/domain/isUserAllowedInDomain
    """
    params = {'user':user, 'apiKey':userApiKey, 'domain':domain}
    result = execRestApiObj.post(restApi='/api/v1/system/domain/isUserAllowedInDomain', params=params, showApiOnly=True) 
    return result.json()['isUserAllowedInDomain']               
                          
def getTaskPlaylistCases(taskPlaylist, playlistExclusions=[]):
    """
    From a playbook, get the module's playlist
    
    getPlaylistCases(moduleProperties.get('playlistExclusions', []))
    """
    testcaseSortedOrderList = []
    problems, excludeTestcases = validatePlaylistExclusions(playlistExclusions)
    
    # self.modulePlaylist is the current module's playlist
    for eachPath in taskPlaylist:
        regexMatch = re.search('.*(Modules|Testcases/.*)', eachPath)
        if regexMatch:
            eachPath = f'{GlobalVars.keystackTestRootPath}/{regexMatch.group(1)}'
        else:
            raise Exception(f'Playbook playlist must begin with /Modules or /Testcases. Not: {eachPath}')
        
        if Path(eachPath).is_dir():
            # Run all file in folders and subfolders

            for root, dirs, files in os.walk(eachPath):
                # root ex: starting_path/subFolder/subFolder
                if files:
                    # Store files in numerical/alphabetic order
                    for eachFile in sorted(files):
                        if root[-1] == '/':
                            eachFile = f'{root}{eachFile}'
                        else:
                            eachFile = f'{root}/{eachFile}'
                            
                        # Testcases/Nokia/nokia.yml
                        currentFilename = eachFile.split('/')[-1]
                    
                        if eachFile in excludeTestcases:
                            continue
                        
                        if bool(re.search('.*(#|~|backup|readme|__init__|pyc)', currentFilename, re.I)):
                            continue
                        
                        testcaseSortedOrderList.append(f'{eachFile}')
                        
        else:
            if eachPath.endswith('.yml') or eachPath.endswith('yaml'):
                if eachPath in excludeTestcases:
                    continue
                
            testcaseSortedOrderList.append(eachPath)
            
    return testcaseSortedOrderList    

def syncTestResultsWithRedis():
    """ 
    If /KeystackTests/Results file is not in redis, put it into redis.
    If redis has a file that is not in the /KeystackTests/Results, remove it from redis.
    """
    print('commonLib:syncTestResultsWithRedis')

    RedisMgr.redis.deleteMatchingPatternKeys(pattern='overallSummary-domain=None*')
     
    # 1> Verify if all the redis overallSummary data exists in the filesystem /opt/KeystackTests/Results. If not, remove from redis.
    redisDBOverallSummaryData = RedisMgr.redis.getAllPatternMatchingKeys(pattern="overallSummary-*")
    for redisOverallSummaryData in redisDBOverallSummaryData:
        # overallSummary-domain=Regression-11-09-2024-20:26:31:668632_6810
        regexMatch = re.search('overallSummary-domain=(.+)-([0-9]+-[0-9]+-[0-9]+-[0-9]+:[0-9]+:.+)', redisOverallSummaryData)    
        if regexMatch:
            domain = regexMatch.group(1)
            timestamp = regexMatch.group(2)
            cwd = f'{GlobalVars.resultsFolder}/DOMAIN={domain}'
            if os.path.exists(cwd) is False:
                RedisMgr.redis.deleteKey(redisOverallSummaryData)
            else:
                result, output = execSubprocessInShellMode(command=f'find . -name "{timestamp}"', cwd=cwd, showStdout=False)
                if output == '': 
                    # If the result overallSummary file doesn't exists in the filesystem, remove it from redis DB   
                    RedisMgr.redis.deleteKey(redisOverallSummaryData)
    
    # 2> Verify if all the filesystem results are in redis. If not, put them in redis.                        
    for testResultDomain in glob(f'{GlobalVars.resultsFolder}/*'):
        # /opt/KeystackTests/Results/DOMAIN=Communal
        currentDomain = testResultDomain.split('/')[-1].split('=')[-1]
        # overallSummary-domain=Communal-04-13-2024-13:59:38:581313_2704
        allRedisDomainResults = RedisMgr.redis.getAllPatternMatchingKeys(pattern=f'overallSummary-domain={currentDomain}*')
        
        for playbook in glob(f'{testResultDomain}/PLAYBOOK*'):
            # playbook: /opt/KeystackTests/Results/DOMAIN=Communal/PLAYBOOK=Samples-advance
            playbookName = playbook.split('/')[-1].split('=')[-1]
            for file in glob(f'{playbook}/*'):
                # /opt/KeystackTests/Results/DOMAIN=Regression/PLAYBOOK=Samples-advance/04-13-2024-13:50:46:698963_5076                
                timestampFolder = file.split('/')[-1]
                insertOverallSummary = f'overallSummary-domain={currentDomain}-{timestampFolder}'
                
                # If result file is not in redis, put it into redis
                if insertOverallSummary not in allRedisDomainResults:
                    try:
                        overallSummaryData = readYaml(f'{file}/overallSummary.json')
                        RedisMgr.redis.write(keyName=insertOverallSummary, data=overallSummaryData)
                    except Exception as errMsg:
                        #print(f'syncTestResultsWithRedis Error: {errMsg}')
                        # OverallSummary.json file not found
                        pass
                               
            # If redis has a file that is not in the filesystem, remove it from redis
            currentDomainPlaybookResultFiles = glob(f'{playbook}/*')  
            for redisOverallSummaryFile in allRedisDomainResults:
                # Get the redis overallSummary timestamp folder
                # overallSummary-domain=Communal-04-13-2024-13:59:38:581313_2704
                regexMatch = re.search(f'overallSummary-domain=[^ ]+-([0-9]+-[0-9]+-[0-9]+-[0-9]+:[0-9]+:[0-9]+:[0-9]+_[0-9]+.*)', redisOverallSummaryFile)
                if regexMatch:
                    timestampFolderFullPath = f'{GlobalVars.resultsFolder}/DOMAIN={currentDomain}/PLAYBOOK={playbookName}/{regexMatch.group(1)}'
                    if timestampFolderFullPath not in currentDomainPlaybookResultFiles:
                        RedisMgr.redis.deleteKey(keyName=redisOverallSummaryFile) 


def getSortedPortList(data: list):
    """ 
    Internal: For portMgmt and portGroup
    data: data['portMgmt] | data['ports']
    
    [{'port': '1/1/1', 'connectedToDevice': None, 'connectedToPort': None, 'portGroups': ['Port-Group1'],
      'multiTenant': False, 'opticMode': None, 'vlanTagId': None, 'autoNeg': True, 'speed': '1G',
      'reserved': 'available', 'additionalKeyValues': {}}
    ]
    
    Usage:
        portMgmtSortedList = getSortedPortList(data=data['portMgmt'])
    """
    if len(data) == 0:
        return []

    tempList = []
    for port in data:
        # Ethernet2/1
        regexMatch = re.search('([a-zA-Z]+)?([0-9]+.+)', port['port'])
        if regexMatch:
            portPrefix = regexMatch.group(1)
            if portPrefix is None:
                portPrefix = ''
                
            portNumber = regexMatch.group(2)
            tempList.append(portNumber) 
            
            if '/' in portNumber:
                portStyle = '/' 
                 
            if '.' in portNumber:
                portStyle = '.'
    
    # sortedList: ['1/1/1', '1/1/2', '1/1/3', '2/1/1', '2/1/2', '2/1/3']
    if portStyle == '/':
        sortedList = sorted(tempList, key=lambda x: [int(i) for i in x.split("/")]) 
    else:
        sortedList == sorted(tempList, key=lambda x: [int(i) for i in x.split(".")])
    
    # sortedList2: ['eth1/1/1', 'eth1/1/2', 'eth1/1/3', 'eth2/1/1', 'eth2/1/2', 'eth2/1/3']
    sortedPortList2 = []     
    for port in sortedList:
        # ['0/1/1', '0/1/2', '0/1/3', '0/3/10', '0/3/11', '0/3/12', '0/3/13']    
        sortedPortList2.append(f'{portPrefix}{port}') 

    def helper(data, port):
        for index, portArray in enumerate(data):
            if portArray['port'] == port:
                return index
                            
    portList = []     
    for port in sortedPortList2:
        # ['0/1/1', '0/1/2', '0/1/3', '0/1/4', '0/1/5', '0/3/10', '0/3/11', '0/3/12', '0/3/13', '0/3/14', '0/3/15']
        index = helper(data, port)
        portList.append(data[index])
           
    return portList


def getSortedPortList2(portlist: list):
    """ 
    Internal: For sorting a list of ports
    Intakes a list of ports, sort the list with existing ports and return
    a sorted list of ports
    
    Usage:
        portMgmtSortedList = getSortedPortListForPortGroup(portlist)
    """
    if len(portlist) == 0:
        return []

    tempList = []
    for port in portlist:
        # Ethernet2/1
        regexMatch = re.search('([a-zA-Z]+)?([0-9]+.+)', port)
        if regexMatch:
            portPrefix = regexMatch.group(1)
            if portPrefix is None:
                portPrefix = ''
                
            portNumber = regexMatch.group(2)
            tempList.append(portNumber) 
            
            if '/' in portNumber:
                portStyle = '/' 
                 
            if '.' in portNumber:
                portStyle = '.'
    
    # sortedList: ['1/1/1', '1/1/2', '1/1/3', '2/1/1', '2/1/2', '2/1/3']
    if portStyle == '/':
        sortedList = sorted(tempList, key=lambda x: [int(i) for i in x.split("/")]) 
    else:
        sortedList == sorted(tempList, key=lambda x: [int(i) for i in x.split(".")])
    
    # sortedList2: ['eth1/1/1', 'eth1/1/2', 'eth1/1/3', 'eth2/1/1', 'eth2/1/2', 'eth2/1/3']
    sortedPortList2 = []     
    for port in sortedList:
        # ['0/1/1', '0/1/2', '0/1/3', '0/3/10', '0/3/11', '0/3/12', '0/3/13']    
        sortedPortList2.append(f'{portPrefix}{port}') 
        
    return sortedPortList2

def isPipModuleExists(pipModule):
    """ 
    pipModule: <str>: <pipModule_name> | <pipModule_name>==<version>
    
    Returns True if matched on pipModuleName and if ==<version> was included,
    match on both pipModule and the version.
    
    Returns False if no match
    """
    # load_dotenv(GlobalVars.keystackSystemSettingsFile)
    # dockerPython = os.environ.get('keystack_dockerPythonPath', None)
    
    keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    dockerPython = keystackSettings.get('dockerPythonPath', None)
    pipModuleExists = False 
    existingPipModuleVersion = None
    pipModuleVersion = None
    
    if dockerPython is None:
        return None
    
    if "==" in pipModule:
        pipModuleName = pipModule.split('==')[0]
        pipModuleVersion = pipModule.split('==')[-1]
    else:
        pipModuleName = pipModule
    
    result, output = execSubprocessInShellMode(f'sudo {dockerPython} -m pip show {pipModuleName}')
    
    for line in output.split('\n'):
        if line:
            if type(line) is bytes:
                line = line.decode('utf-8')
                
            regexMatch = re.search('^Version: ([^ ]+)', line)
            if regexMatch:
                pipModuleExists = True
                existingPipModuleVersion = regexMatch.group(1)
    
    if pipModuleExists:
        if pipModuleVersion:
            if existingPipModuleVersion == pipModuleVersion:
                return True
            else:
                return False
        else:
            return True
    else:
        return False
        
def pipInstallModule(module):
    # load_dotenv(GlobalVars.keystackSystemSettingsFile)    
    # pipInstalls = os.environ.get('keystack_pipInstalls', None).split(',')
    # dockerPython = os.environ.get('keystack_dockerPythonPath', None)
    
    keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    pipInstalls = keystackSettings.get('pipInstalls', None)
    dockerPython = keystackSettings.get('dockerPythonPath', None)
            
    if dockerPython:
        command = f'sudo {dockerPython} -m pip install {module}'
        # Note, bufsize=1 won't work without text=True or universal_newlines=True.        
        with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True) as output:
            # Flush stdout         
            with fdopen(sys.stdout.fileno(), 'wb', closefd=False) as stdout:                
                for line in output.stdout: 
                    print(f'pipInstallModule: {line}')
                        
        return output.stdout
    
def execCliCommand(command, keystackLogger=None):
    """ 
    Used by envHandler:autoSetup, envHandler:autoTeardown, envViews:reserveEnv, nvViews:releaseEnv
    """
    # Note, bufsize=1 won't work without text=True or universal_newlines=True.
    lineOutput = ''        
    with subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True) as output:
        # Flush stdout         
        with fdopen(sys.stdout.fileno(), 'wb', closefd=False) as stdout:                
            for line in output.stdout:
                if line: 
                    print(line.strip()) 
                    lineOutput += f'{line.strip()}\n'
                
    if keystackLogger:
        keystackLogger.debug(lineOutput)
        
         
class ConnectTelnet:
    def __init__(self, ip=None, port=23, login=None, password=None):
        try:
            from Exscript.protocols import Telnet
            from Exscript import Host, Account
            
            account = Account(login, password)
            self.telnetObj = Telnet(debug=1)
            self.telnetObj.connect(ip, port)
            if login:
                self.telnetObj.login(account)

        except Exception as errMsg:
            raise KeystackException(f'ConnectTelnet failed: {errMsg}')
            
    def sendCliCommand(self, cmd):
        self.telnetObj.execute(cmd)
        output = self.telnetObj.response
        return output
    
def addToKeystackMisc(key, value):
    """ 
    Add a new device location, device type, device vendor to the DB list
    
    The purpose of making user create these is for filtering and avoiding 
    human error if users were to be typing them.
    """
    if value != 'None':
        data = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                      fields={'name': key},
                                      includeFields=None)
        
        if value not in data[key]:
            result = DB.name.updateDocument(collectionName=Vars.keystackMisc,
                                            queryFields={'name': key},
                                            updateFields={key: value},
                                            appendToList=True)

def getKeystackMiscAddtionalFields(dbFieldsName):
    """ 
    dbFieldsName = labInventoryAdditionalKeys | portMgmtAdditionalKeys
    """
    data = DB.name.getOneDocument(collectionName=Vars.keystackMisc,
                                  fields={'name': dbFieldsName},
                                  includeFields=None)

    # {'assets1': {'type': 'options', 'defaultValue': 'a', 'options': ['a', 'b', 'c']}}
    if data:
        return data['additionalKeys']
    else:
        return {}
    
def isLabInventoryAdditonalKeysDBExists(dbFieldsName):
    """ 
    For lab-inventory device addtional fields and port-mgmt additional fields
    
    dbFieldsName = labInventoryAdditionalKeys | portMgmtAdditionalKeys
    """
    labInventoryAdditionalKeys = DB.name.isDocumentExists(collectionName=Vars.keystackMisc,
                                                          keyValue={'name': dbFieldsName})
    if not labInventoryAdditionalKeys:
        keystackMisc = DB.name.insertOne(collectionName=Vars.keystackMisc,
                                         data={'name': dbFieldsName,
                                               'additionalKeys': {}})
                        
def updateAdditionalKeyDB(dbFieldsName, keyValues: dict):
    """ 
    dbFieldsName = labInventoryAdditionalKeys | portMgmtAdditionalKeys
    """
    DB.name.updateDocument(collectionName=Vars.keystackMisc, 
                           queryFields={'name': dbFieldsName},
                           updateFields={'additionalKeys': keyValues})