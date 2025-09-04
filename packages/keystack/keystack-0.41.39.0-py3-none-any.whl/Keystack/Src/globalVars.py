import os, traceback
 
currentDir = os.path.abspath(os.path.dirname(__file__))
rootPath = currentDir.replace('/Src', '')
     
from keystackUtilities import readYaml

if os.path.exists('/etc/keystack.yml'):
    etcKeystackYml = readYaml('/etc/keystack.yml')
else:
    etcKeystackYml = None

    
class GlobalVars:        
    sessionTimestampFolder = ''
    versionFile   = f'{rootPath}/version'
    uiVersionFile = f"{currentDir}/KeystackUI/keystackUIVersion"
    user = 'keystack'
    userGroup = 'Keystack'
    jobSchedulerUser = 'Scheduled-Job'
    defaultDomain              = 'Communal'

    #if os.path.exists('/etc/keystack.yml'):
        #raise Exception('globalVars: /etc/keystack.yml not found')

    #etcKeystackYml = readYaml('/etc/keystack.yml')
    #if os.path.exists(etcKeystackYml['keystackTestRootPath']) == False:
    #    raise Exception(f'globalVars: /etc/keystack.yml keystackTestRootPath path not found: {etcKeystackYml["keystackTestRootPath"]}')

    if etcKeystackYml:
        keystackRootPath           = etcKeystackYml['keystackRootPath']
        keystackTestRootPath       = etcKeystackYml['keystackTestRootPath']    
        keystackSystemPath         = etcKeystackYml['keystackSystemPath']

        resultsFolder              = f'{keystackTestRootPath}/Results'
        archiveResultsFolder       = f'{keystackTestRootPath}/ResultsArchive'
        # Saved pipeline-names as files with test parameters
        modules                    = f'{keystackTestRootPath}/Modules'
        pipelineFolder             = f'{keystackTestRootPath}/Pipelines'
        playbooks                  = f'{keystackTestRootPath}/Playbooks'
        envPath                    = f'{keystackTestRootPath}/Envs'
        testcasesFolder            = f'{keystackTestRootPath}/Testcases'
        testConfigsFolder          = f'{keystackTestRootPath}/TestConfigs'
        keystackSystemSettingsFile = f'{keystackSystemPath}/keystackSystemSettings.yml'
        appsFolder                 = f'{keystackSystemPath}/Apps'
        keystackServiceLogPath     = f'{keystackSystemPath}/Logs'
        keystackAwsS3Logs          = f'{keystackServiceLogPath}/keystackAwsS3.json'
        awsS3DebugFile             = f'{keystackSystemPath}/ServicesStagingArea/debuggingAwsS3'
        resultHistoryPath          = f'{keystackSystemPath}/ResultDataHistory'
        restApiModsPath            = f'{keystackSystemPath}/RestApiMods'
        controllerRegistryPath     = f'{keystackSystemPath}/.Controllers'
        loginCredentials           = f'{keystackSystemPath}/.loginCredentials.yml'
        domainsFile                = f'{keystackSystemPath}/.DataLake/domains.yml'
        envMgmtPath                = f'{keystackSystemPath}/.DataLake/.EnvMgmt' 
        systemBackupPath           = f'{keystackSystemPath}/SystemBackups'
        systemBackupTempPath       = f'{keystackSystemPath}/SystemBackups/restoreBackupTemp'
        debugLogFilePath           = f'{keystackServiceLogPath}/devDebugLogs'
        sessionLogFilename         = 'testSession.log'
        customizeTestReportFile    = f'{keystackSystemPath}/customizeTestReport.yml'
        appStoreLocationsFile      = f'{keystackSystemPath}/appStoreLocations.yml'
        ciTestResultLocationFile   = f'{keystackTestRootPath}/ciTestResultPaths'
            
    removeResultFoldersAfterDays = 5
    
    # 4.4.7 | 6.0.2 -> Must use 4.4.7 because ubuntu 20.04 uses older CPU that
    #                  doesn't support MongoDB greater than 4.4.7
    # The latest version that can work WITHOUT CPU with AVX is 4.4.7
    mongoVersion               = '4.4.7'   


class HtmlStatusCodes:
    # Request is successful
    success = 200
    # Successfully created
    created = 201
    # Request received but not acted upon
    ok = 202
    # Bad request
    badRequest = 400
    # Unauthorized
    unauthorized = 401
    # Forbidden & unauthorized
    forbidden = 403
    # URL is not recognized
    urlNotRecognized = 404
    # Method is not allowed
    notAllowed = 405
    # Request is received but there is an error as result
    error = 406
    # Conflict with the current state of the server
    conflict = 409
    
    
