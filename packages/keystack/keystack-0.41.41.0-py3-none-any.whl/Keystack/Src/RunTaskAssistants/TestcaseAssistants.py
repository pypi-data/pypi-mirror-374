import os, re
from pathlib import Path
from pydantic import Field, dataclasses

from globalVars import GlobalVars
from keystackUtilities import readYaml, mkdir2
from commonLib import validatePlaylistExclusions
from RedisMgr import RedisMgr


@dataclasses.dataclass
class TestcaseAssistant:
    runTaskObj: object
    
    def readYmlTestcaseFile(self, ymlTestcaseFile):
        """
        Internal use only.  Read each testcase yml file and store data into a dict.
        
        ymlTestcaseFile: Ex: /opt/KeystackTests/Modules/CustomPythonScripts/Testcases/bgp.yml
        """
        testcaseData = readYaml(ymlTestcaseFile, threadLock=self.runTaskObj.statusFileLock)
        if testcaseData is None:
            raise Exception(f'Synxtax error in testcase yml file: {ymlTestcaseFile}')
        
        self.runTaskObj.testcaseDict[ymlTestcaseFile] = testcaseData

        # Check if the testcase is modified by rest api call
        if self.runTaskObj.playbookObj.restApiMods:
            for testcaseModFileDict in self.runTaskObj.playbookObj.restApiMods['testcases']:
                # {'/Modules/CustomPythonScripts/Testcases/bgp.yml': {'script': '/Modules/CustomPythonScripts/Scripts/ospf.py'}}
                for testcaseModFile, dataToModify in testcaseModFileDict.items():
                    if testcaseModFile in ymlTestcaseFile:
                        self.runTaskObj.testcaseDict[ymlTestcaseFile].update(dataToModify)
                            
    def getAllTestcaseFiles(self, playlistExclusions=[]):
        """
        Collect all the testcases to run from the playbook playlist.
        This function will make a copy of all the playbook playlist testcase yml
        to an internal folder and Keystack will execute testcases from the internal
        folders.  This allows users to modify the testase configurations and this 
        allows each test to make unique modifications.
        
        Users could also manually copy test cases to the /{keystackTestRootPath}/ClonedTestcases folder
        by creating a subfolder used as a namespace.  The namspace subfolder could be passed into 
        the CLI to use instead of the playlist in the playbook.
        
        Users could also do the same in the Keystack UI
        """
        self.runTaskObj.testcaseSortedOrderList = []
        if self.runTaskObj.taskProperties.get('playlist', None) is None:
            return
        
        problems, excludeTestcases = validatePlaylistExclusions(playlistExclusions)
  
        def makeTestcaseFolder(testcase):
            """ 
            Make a copy of the playbook playlist testcase paths to the 
            test session folder:
                /<test_sessionId_folder>/.Data/ResultsMeta
                
            generateTestResults() will get results from .Data/ResultsMeta/...
            
            Purpose:
                - So users could modify the testcase configurations without changing 
                  the original testcase yml files.
            """

            # testcase: /opt/KeystackTests/Modules/Demo/Samples/Testcases/Bringups/bringupDut1.yml
            # testcaseResultsMetaFolder: /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=Samples-pythonSample/11-12-2023-19:31:33:537786_9075/.Data/ResultsMeta/opt/KeystackTests/Modules/Demo/Samples/Testcases/Bringups
            testcaseFileName = testcase.split('/')[-1]
            testcaseResultsMetaFolder = '/'.join(f'{self.runTaskObj.playbookObj.resultsMetaFolder}{testcase}'.split('/')[:-1])
            mkdir2(testcaseResultsMetaFolder, stdout=False)
                     
        # self.runTaskObj.taskPlaylist is the current module's playlist
        # ['/Modules/Demo/Testcases/L2L3_Testcases/bgp.yml', '/Modules/Demo/Scripts/standalonePython.py', 
        # '/Modules/Demo/Scripts/shellScript.bash', '/Modules/Demo/Scripts/plainPythonScript.py']
        for eachPath in self.runTaskObj.taskPlaylist:
            # eachPath: /Modules/Demo/Samples/Testcases/Bringups or /Cases/Demo/Samples/Testcases/Bringups
            # eachPath: /opt/KeystackTests/Modules/Demo/Scripts/standalonePython.py -arg1 hello -arg2 world
            regexMatch = re.search(f'({GlobalVars.keystackTestRootPath})?(.+)', eachPath)
            if regexMatch:
                eachPath = regexMatch.group(2)
                if regexMatch.group(2).startswith('/'):
                    eachPath = f'{GlobalVars.keystackTestRootPath}{regexMatch.group(2)}'
                else:
                    eachPath = f'{GlobalVars.keystackTestRootPath}/{regexMatch.group(2)}'
           
            if len(eachPath.split(' ')) > 1:
                cmdLineArgs = ' '.join(eachPath.split(' ')[1:])
                # Handling playbook playlist: /opt/KeystackTests/Modules/Demo/Scripts/standalonePython.py -arg1 hello -arg2 world
                eachPath = eachPath.split(' ')[0]
            else:
                cmdLineArgs = ''
            
            if os.path.exists(eachPath) is False:
                raise Exception(f'Playbook Stage:{self.runTaskObj.stage} Task:{self.runTaskObj.task}: No such path/file found in playlist: {eachPath}')
                       
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

                            copiedTestcaseYmlFile = makeTestcaseFolder(eachFile)
                                                            
                            # Not all testcases use the yml file method.  
                            # Such as custom pythonscripts.                                                            
                            if eachFile.endswith('.yml') or eachFile.endswith('yaml'):
                                self.readYmlTestcaseFile(eachFile)

                            self.runTaskObj.testcaseSortedOrderList.append((eachFile, cmdLineArgs))            
            else:
                if eachPath in excludeTestcases:
                    continue
                
                # /opt/KeystackTests/Results/DOMAIN=Default/PLAYBOOK=Samples-pythonSample/11-17-2023-06:33:27:361583_9623/.Data/ResultsMeta/opt/KeystackTests/Modules/Demo/Samples/Testcases/dynamicVariableSample.yml
                copiedTestcaseYmlFile = makeTestcaseFolder(eachPath)

                if eachPath.endswith('.yml') or eachPath.endswith('yaml'):                   
                    # Run individual testcase yml file. Don't read .py files
                    self.readYmlTestcaseFile(eachPath)
 
                self.runTaskObj.testcaseSortedOrderList.append((eachPath, cmdLineArgs))
                
        # Keep track of overall test cases from every test module for final playbook report
        self.runTaskObj.playbookObj.totalCases += len(self.runTaskObj.testcaseSortedOrderList)
                  
    def getLoopTestcaseCount(self, eachTestcase):
        """
        Verify if users set any folders and/or testcases to loop testing more than one time
         
        Looping feature: 
           - Loop allTestcases
           - Loop all scripts inside folders and subfolders
           - Loop selected testcases
           - If no condition is met, default running testcases one time
           - Allows user to do all three. The loop count will increment in this case.
           
        Usage in the modulePreferences file:
           loop:
                # Set allTestcases to None to disable looping all test cases
                allTestcases: 2
                
                folders: 
                    # Run everything in a folder including subfolders
                    - /KeystackTests/Modules/SanityScripts/Testcases: 2
                    
                testcases:
                    # Selecting specific testcases
                    - /KeystackTests/Modules/SanityScripts/Testcases/bgp.py: 3
                    - /KeystackTests/Modules/SanityScripts/Testcases/isis.py: 5
        """
        loopTestcase = 0
        if 'innerLoop' in self.runTaskObj.taskProperties:
            if self.runTaskObj.taskProperties['innerLoop']['allTestcases'] not in ["None", '', 0]:
                loopTestcase = int(self.runTaskObj.taskProperties['innerLoop']['allTestcases'])
                
            if 'folders' in self.runTaskObj.taskProperties['innerLoop'] and \
                self.runTaskObj.taskProperties['innerLoop']['folders'] not in ["None", '', 0]:
                for eachFolderDict in self.runTaskObj.taskProperties['innerLoop']['folders']:
                    # eachFolderDict = {'/Modules/CustomPythonScripts/Testcases': 3}
                    folder = list(eachFolderDict.keys())[0]
                    if folder.startswith('/Modules/'):
                        folder = f'{self.runTaskObj.keystackTestRootPath}{folder}'
                    if folder.startswith('Modules/'):
                        folder = f'{self.runTaskObj.keystackTestRootPath}/{folder}'
                                        
                    for root, dirs, files in os.walk(folder):
                        if files:
                            for file in files:
                                if f'{root}/{file}' == eachTestcase:
                                    loopCount = list(eachFolderDict.values())[0]
                                    if loopTestcase > 0:
                                        loopTestcase += loopCount
                                    else:
                                        loopTestcase = loopCount
                                        
                                    break

            if 'testcases' in self.runTaskObj.taskProperties['innerLoop'] and \
                self.runTaskObj.taskProperties['innerLoop']['testcases'] not in ["None", '', 0]:
                try:
                    for tc in self.runTaskObj.taskProperties['innerLoop']['testcases']:
                        # tc = {'/Modules/CustomPythonScripts/Testcases/bgp.py': 4}
                        for eachDependentTestcase in tc.keys():
                            if eachDependentTestcase in eachTestcase:
                                loopCount = list(tc.values())[0]

                    if loopTestcase > 0:
                        loopTestcase += loopCount
                    else:
                        loopTestcase = loopCount             
                    
                except IndexError:
                    # User selected specified testcases from a folder.
                    # If a testcases isn't selected in the loop feature, then default the loop to run once only.
                    if loopTestcase == 0:
                        loopTestcase = 1

        if loopTestcase == 0:
            # Default to run testcases 1 one if no loop condition is met
            loopTestcase = 1
                    
        return loopTestcase
    
    def getTestcaseScript(self, typeOfScript='standalonePythonScripts', testcase=None):
        """ 
        Look into the testcase yml file to see the type of script to execute and get
        the script's command line args if any
        
        Note:
           Scripts could reside anywhere in the Keystack server filesystem
           Provide a list of full path scripts to run
            
        This function will:
            - Set self.runTaskObj.testcaseScriptArgv with scriptCmdlineArgs
            - return the script's full path
        
        typeOfScript:
             standalone python scripts:   sttandalonePythonScripts
             keystackIntegration scripts: pythonScripts
             shell scripts: shellScripts
        
        Test case yml file example:
            # To include script cmdline args
            # User could enter the script to run followed by the script's parameters/values
            pythonScripts: 
               - /opt/KeystackTests/Modules/IxNetworkDataModel/Scripts/runIxNetwork.py
            
            scriptCmdlineArgs:
               - arg: -dataModelFile /opt/KeystackTests/Modules/<module_name>/ConfigParameters/<file>.yml
               - arg: -email 
            
            - The main script could be part of the APP.
              In this case:
                 pythonScripts:
                    - /Apps/<AppName>/path/script.py
             
        Returns:
            Script full path
        """
        scriptTypeSearch = False       
        for eachType in ['pythonScripts', 'standalonePythonScripts', 'shellScripts']:
            if eachType in self.runTaskObj.testcaseDict[testcase]:
                scriptTypeSearch = True
        
        if scriptTypeSearch is False:
            self.runTaskObj.abortTestCaseErrors.append(f"The testcase yml file '{testcase}' expects a type of script to run. Options: pythonScripts, standalonePythonScripts, shellScripts. None found. Don't know which Python script to execute")
            return
        
        # /Modules/IxNetworkDataModel/Scripts/runIxNetwork.py -arg1 <value> -arg2 <value>        
        userDefinedScripts = self.runTaskObj.testcaseDict[testcase][typeOfScript]

        for eachScript in userDefinedScripts:
            if os.path.exists(eachScript) is False:
                self.runTaskObj.abortTestCaseErrors.append(f'The testcase yml file:{testcase}states a script that does not exists. Please check the script full path: {eachScript}')
              
        # Scripts that takes in external parameters/values uses scriptCmdlineArgs
        if self.runTaskObj.playbookObj.reconfigData and testcase in self.runTaskObj.playbookObj.reconfigData.keys():
            scriptCmdlineArgNeatList = self.runTaskObj.playbookObj.reconfigData[testcase]['scriptCmdlineArgs']
        else:
            scriptCmdlineArgNeatList = self.runTaskObj.testcaseDict[testcase].get('scriptCmdlineArgs', [])

        if typeOfScript in ['shellScripts', 'standalonePythonScripts']:
            self.runTaskObj.testcaseScriptArgv = ''       
            for eachArg in scriptCmdlineArgNeatList:
                self.runTaskObj.testcaseScriptArgv += f'{eachArg} '
        else:
            # Python scripts integrated with Keystack
            # testcaseScriptArgv is a list so argparse can consume the args
            self.runTaskObj.testcaseScriptArgv = []
            for eachArg in scriptCmdlineArgNeatList:
                self.runTaskObj.testcaseScriptArgv.append(eachArg)                    
        
        return userDefinedScripts

    def getTestcaseApp(self, testcaseYmlFile):
        """ 
        Testcase yml file might be using an app to run a main script.
        Verify the yml file for an 'app' key
        """
        data = readYaml(testcaseYmlFile)
        app = data.get('app', None)
        
        if app is None:
            self.runTaskObj.abortTestCaseErrors.append(f'Testcase yml file is missing the app to use: {testcaseYmlFile}')
            return None
  
        if os.path.exists(f'{GlobalVars.appsFolder}/{app}') is False:
            self.runTaskObj.abortTestCaseErrors.append(f'App does not exists: {app}. In testcase yml file: {testcaseYmlFile}')
            return None

        regexMatch = re.search('(.*)/(applet.*).py', app)
        if regexMatch:
            appName = regexMatch.group(1)
            applet = regexMatch.group(2)
            appPath = f'{GlobalVars.appsFolder}/{appName}'

            # ('/opt/KeystackSystem/Apps/CustomPython', 'applet_CustomPython')
            return (appPath, applet)
        else:
            self.runTaskObj.abortTestCaseErrors.append(f'App does not exists: {app}')

    def getTestcaseAppLibraryPath(self, testcaseYmlFile):
        """ 
        Scripts want to import some app libraries.
        
        The testcase yml file uses a keyword importAppLibraries.
        The value needs to be a list of app names only. Exclude applets.
        """
        data = readYaml(testcaseYmlFile)
        appLibraryPaths = data.get('importAppLibraryPaths', None)
        if appLibraryPaths is None:
            return []
        
        if type(appLibraryPaths) is not list:
            self.runTaskObj.abortTestCaseErrors.append(f'The appLibraryPaths value needs to be a list in testcase yml file beginning with /Apps or /Modules: {testcaseYmlFile}')  
            return []
        
        appPathList = []
        for appLibraryPath in appLibraryPaths:
            regexMatch = re.search('.*(Apps|Modules)/(.*)', appLibraryPath)
            if regexMatch:
                if 'Apps' in regexMatch.group(1):
                    appPath = f'{GlobalVars.appsFolder}/{regexMatch.group(2)}'
                    
                if 'Modules' in regexMatch.group(1):
                    appPath = f'{GlobalVars.keystackTestRootPath}/Modules/{regexMatch.group(2)}'
                     
                if os.path.exists(appPath) is False:
                    self.runTaskObj.abortTestCaseErrors.append(f'No such app path: {appPath}') 
                else:
                    appPathList.append(appPath)
            
        return appPathList 
