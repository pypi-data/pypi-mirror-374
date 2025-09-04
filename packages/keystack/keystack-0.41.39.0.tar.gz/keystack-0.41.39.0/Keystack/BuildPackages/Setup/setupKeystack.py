"""
Description:
   This script does 3 different things:

      1> For new install:            
            Do a pip install keystack or install using the wheel package first
                - Then enter: setupKeystack -setup docker
                
            If no pip install, you must have the keystackSetup-<version>.zip package
                - Unzip the package: keystackSetup-<version>.zip
                - python3 setupKeystack.py -setup docker -dockerFile dockerKeystack_<version>.tar
                
      2> Update existing Keystack:
            - Same as above, but replace -setup with -update
            
      3> To generate sample scripts: python3 setupKeystack.py -getSamples -sampleDest .
                                     This creates a folder called KeystackSamples 

   Setup Keystack environment:
      - Create a keystack user and a Keystack group on your Linux OS
      - Create /opt folder
           KeystackTests
              Envs
              Playbooks
              Modules
              Results
              ResultsArchive
           KeystackSystem
              keystackSystemSettings.yml
              Logs
              ServiceStagingArea
              ResultDataHistory
              SystemBackups
              .loginCredentials.yml
  
   docker load -i dockerKeystack_v#.tar  <-- Install keystack docker container
    
   if docker-compose exists:           
        docker-compose will pull mongod:6.0.2
        start both docker containers using docker-compose
   else:     
        docker pull mongod:6.0.2
        docker run mongo
        docker run keystack

Requirements:
   - Must be a sudo user
   - Python 3.7+
   - Python pip install packages: dotenv
   - Docker
   - Know the path to put Keystack folders: Modules/Playbooks/Envs folders
   - Know the python full path. If you don't know this, enter: which <python>

For non Docker setup:
   - PIP install the keystack.whl file
   - sudo <your python full path> -m pip install keystack-<version>.whl
"""

import sys, os, re, subprocess, traceback, argparse, shutil
from time import sleep
from re import search

#/Keystack/BuildPackages/Setup
currentDir = os.path.abspath(os.path.dirname(__file__))

try:
    # Has done a pip install keystack or installed the Keystack wheel package
    from keystackUtilities import execSubprocessInShellMode, execSubprocess2, readYaml, saveFileToBackupFile, mkdir, mkdir2, readFile, writeToYamlFile, stopDockerContainer, removeDockerImage, verifyContainers, getRunningContainerTagVersion
except:
    # No pip install
    from keystackUtilities import execSubprocessInShellMode, execSubprocess2, readYaml, saveFileToBackupFile, mkdir, mkdir2, readFile, writeToYamlFile, stopDockerContainer, removeDockerImage, verifyContainers, getRunningContainerTagVersion    


class SetupVar:
    keystackRootPath   = None
    keystackTestPath   = None
    keystackSystemPath = None
    userEnvSettings = readYaml(f'{currentDir}/userEnvSettings.yml')
    keystackVersion = None
    systemFiles     = ['keystackSystemSettings.yml', '.loginCredentials.yml', 'customizeTestReport.yml', 'appStoreLocations.yml']

    # 4.4.7 | 6.0.2 -> Must use 4.4.7 because ubuntu 20.04 uses older CPU that
    #                  doesn't support MongoDB greater than 4.4.7
    # The latest version that can work WITHOUT CPU with AVX is 4.4.7
    mongoVersion = '4.4.7'
    
    # Do not touch this variable: Docker's Python path
    # Unbuntu's path
    #dockerPythonFullPath = '/usr/bin/python3.8'
    
    # Alpine's path
    dockerPythonFullPath = '/usr/bin/python3.10'
    
    pythonFullPath = None
    dockerHubUsername = 'hubertgee'
    
    # Internal setting.  Cannot be changed by user.
    keystackUserUid = 8000
    keystackGroupGid = 8001


try:
    # This is only for installations with keystack docker tar file
    # Using setupKeystack from a provided folder (no internet connection)
    versionFile = f'{currentDir}/version'

    if os.path.exists(versionFile):
        SetupVar.keystackVersion = readYaml(versionFile)['keystackVersion']
    else:
        # Using setupKeystack by pip install
        versionFile = currentDir.replace('/BuildPackages/Setup', '/version')
        if os.path.exists(versionFile):
            SetupVar.keystackVersion = readYaml(versionFile)['keystackVersion']
except:
    pass


class Setup:
    def generateSamples(self, keystackRootPath=None, destinationPath=None, alreadyBackedUpSystemFiles=False):
        """ 
        This function serves -setup and -getSamples
        
        Bundle up all samples.
        Dynamically generate a docker sample script with dynamic user defined path

        keystackRootPath: The Keystack folder location. This is automatically obtained by 
                          reading the /etc/keystack.py looking the the path to KeystackTests.
                          For ex: /opt/KeystackTests
        destinationPath: The path to where to put the generated samples
        """
        if destinationPath is None:
            # Called by -setup
            setup = True
            # Default
            samplesTargetPath = f'{keystackRootPath}/KeystackTests'
        else:
            # Called by -getSamples
            # User wants to get samples
            setup = False
            if os.path.exists(destinationPath) == False:
                sys.exit(f'\nYour stated dest path does not exists: {destinationPath}')

            samplesTargetPath = f'{destinationPath}/KeystackSamples'
            user = execSubprocessInShellMode('whoami')[-1]
            mkdir2(samplesTargetPath)

        # The included/excluded Modules are done by packageRelease already. So what ever is in the Samples are it. 
        execSubprocessInShellMode(f'sudo cp -R {currentDir}/Samples/* {samplesTargetPath}')        

        # Backup
        if setup == False:
            # Get samples: ['keystackSystemSettings.yml', '.loginCredentials.yml', 'customizeTestReport.yml', 'appStoreLocations.yml']
            for systemFile in SetupVar.systemFiles:
                execSubprocessInShellMode(f'sudo cp {currentDir}/Templates/{systemFile} {samplesTargetPath}/{systemFile}')
            
        # Docker test samples
        for dockerFile in [f'{currentDir}/Samples/Samples/Docker/dockerQuickTest', 
                           f'{currentDir}/Samples/Samples/Docker/dockerLoadcoreSample']:            
            filenameOnly = dockerFile.split('/')[-1]
            dockerSampleTemplateFile = dockerFile
            dockerSampleTemplate = readFile(dockerSampleTemplateFile).strip()
            dockerSampleTemplate = dockerSampleTemplate.replace('{path}', keystackRootPath)
            execSubprocessInShellMode(f"sudo echo '{dockerSampleTemplate}\n' | sudo tee {samplesTargetPath}/Docker/{filenameOnly}.sh")
        if setup == False:
           execSubprocessInShellMode(f'sudo chown -R {user}:{user} {samplesTargetPath}')
           execSubprocessInShellMode(f'sudo chmod -R 770 {samplesTargetPath}')  
           print(f'\ngetSamples: Done. Samples are in {samplesTargetPath}\n')
                    
        # Clean up
        execSubprocessInShellMode(f'sudo rm {SetupVar.keystackRootPath}/KeystackTests/Modules/__init__.py')        

    def installDockerImageKeystack(self, dockerBuildImagePath=None):
        """
        Install the docker image with docker tar file and start the container

        dockerBuildImagePath: The full path including file name to the docker tar file 
                         that gets installed as a docker image
        """
        ipPort = SetupVar.userEnvSettings["keystackPort"]
        keystackSecuredPort = SetupVar.userEnvSettings["keystackSecuredPort"]      
        dockerKeystackFilePath = currentDir.replace('/Setup', '')
        dockerKeystackFile = f'dockerKeystack_{SetupVar.keystackVersion}.tar'

        if dockerBuildImagePath is None:
            dockerBuildImagePath = f'{currentDir}/{dockerKeystackFile}'            

        if os.path.exists(dockerBuildImagePath):
            execSubprocessInShellMode(f'sudo docker load -i {dockerBuildImagePath}')
            sleep(2)

    def startDockerContainerKeystack(self, version):
        """ 
        Start the Keystack container with Docker run.
        Not by docker-compose
        """
        version = '0.41.3.0'
        ipPort = SetupVar.userEnvSettings["keystackPort"]
        keystackSecuredPort = SetupVar.userEnvSettings["keystackSecuredPort"]  
        execSubprocessInShellMode(f'sudo docker run -p {ipPort}:{ipPort} -p {keystackSecuredPort}:{keystackSecuredPort} -d -v {SetupVar.keystackTestPath}:{SetupVar.keystackTestPath} -v {SetupVar.keystackSystemPath}:{SetupVar.keystackSystemPath} --name keystack --rm hubertgee/keystack:{version}', showStdout=True)
                        
    def installAndStartDockerContainers(self, mongoIp='keystackMongoDBHostname', dockerBuildImagePath=None):
        if dockerBuildImagePath:
            # User has no internet to install from docker hub
            # docker.tar file needs to be provided to the user to build the docker image on the host
            # docker load -i <keystack:version> (To create Keystack docker image)
            self.installDockerImageKeystack(dockerBuildImagePath=dockerBuildImagePath)
        else:
            self.dockerPullKeystack()
            self.dockerPullMongo()
            
        # Auto-Generate the docker-compose.yml file
        # docker compose will pull the mongoDB
        dockerComposeTemplateFile = f'{currentDir}/Templates/docker-compose.yml'
        dockerComposeTemplate = readFile(dockerComposeTemplateFile)
        for replacement in [('{keystackVersion}',     SetupVar.keystackVersion),
                            ('{mongoVersion}',        SetupVar.mongoVersion),
                            ('{mongoPort}',           SetupVar.userEnvSettings["mongoPort"]),
                            ('{keystackTestPath}',    SetupVar.keystackTestPath),
                            ('{keystackSystemPath}',  SetupVar.keystackSystemPath),
                            ('{mongoDpIp}',           mongoIp),
                            ('{keystackIp}',          SetupVar.userEnvSettings["keystackIp"]),
                            ('{keystackSecuredPort}', SetupVar.userEnvSettings["keystackSecuredPort"]),
                            ('{keystackPort}',        SetupVar.userEnvSettings["keystackPort"])
                        ]:
            dockerComposeTemplate = dockerComposeTemplate.replace(replacement[0], str(replacement[1]))

        if dockerBuildImagePath is None:
            dockerComposeTemplate = dockerComposeTemplate.replace('{dockerHubUsername}', f'{SetupVar.dockerHubUsername}/')
        else:
            dockerComposeTemplate = dockerComposeTemplate.replace('{dockerHubUsername}', '')

        execSubprocessInShellMode(f'sudo echo "{dockerComposeTemplate}" | sudo tee {currentDir}/docker-compose.yml', showStdout=True)
        execSubprocessInShellMode(f'sudo docker compose up -d', cwd=currentDir, showStdout=True)
        
    def dockerPullKeystack(self):
        """ 
        Pull from Docker hub
        """
        execSubprocessInShellMode(f'sudo docker pull {SetupVar.dockerHubUsername}/keystack:{SetupVar.keystackVersion}', showStdout=True)
        '''
        if SetupVar.keystackVersion:
            execSubprocessInShellMode(f'sudo docker pull {SetupVar.dockerHubUsername}/keystack:{SetupVar.keystackVersion}', showStdout=True)
        else:    
            if version:
                execSubprocessInShellMode(f'sudo docker pull {SetupVar.dockerHubUsername}/keystack:{version}', showStdout=True)
            else:
                execSubprocessInShellMode(f'sudo docker pull {SetupVar.dockerHubUsername}/keystack', showStdout=True)
        '''
        
    def dockerPullMongo(self):
        execSubprocessInShellMode(f'sudo docker pull mongo:{SetupVar.mongoVersion}', showStdout=True)

    def dockerStartMongo(self):
        print(f'sudo docker run -d -p {SetupVar.userEnvSettings["mongoPort"]}:{SetupVar.userEnvSettings["mongoPort"]} -v {SetupVar.keystackSystemPath}/MongoDB:/data/db --name mongo --rm mongo:{SetupVar.mongoVersion}')
        
        execSubprocessInShellMode(f'sudo docker run -d -p {SetupVar.userEnvSettings["mongoPort"]}:{SetupVar.userEnvSettings["mongoPort"]} -v {SetupVar.keystackSystemPath}/MongoDB:/data/db --name mongo --rm mongo:{SetupVar.mongoVersion}', showStdout=True)
                    
    def askUserForIpAddress(self):
        """
        This is for -setup linux
        
        If using Docker without docker-compose or kubernettes to bring up
        the Keystack and Mongo containers, connecting to MongoDB requires
        a static IP address.  localhost, 0.0.0.0 and dns will not work.
        """                                                                                                        
        while True:
            mongoIp = input('\nWhich IP address on your host server should Keystack use? ')
            match = re.search('[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+', mongoIp)
            if not match:
                print(f'The IP format is incorrect. Please try again ...')
            else:
                break 

        return mongoIp

    def setup(self, platform='docker', dockerBuildImagePath=None, version=None):     
        try:
            if version:
                SetupVar.keystackVersion = version

            print(f'\nSetup Keystack: Version: {SetupVar.keystackVersion}')
            
            # Verify if user has sudo priviledges
            whoami = execSubprocessInShellMode('whoami')[-1]
            isUserSudo = execSubprocessInShellMode(f'sudo -l -U {whoami}')[-1]
            if 'is not allowed' in isUserSudo:
                raise Exception(f'User {whoami} is not a sudo user. You must be a sudo user to setup Keystack. Also, if you must enter sudo password for each system wide command, then install this as the root user.')

            # Show instructions in the terminal
            os.system('clear')
            print('\n--- YOU MUST HAVE SUDO PRIVILEGES TO SETUP KEYSTACK! ---\n')
            #print('\nSetting up Keystack requires you to answer a few questions:\n')
            # print('\t1> Are you using Keystack in docker? Default=docker')
            #print('\t- Where do you want to put Keystack Playbooks/Modules/Envs/TestResult folders?')
            #print('\t   (Ex: /, /opt, /usr/local)\n')
            print('\t- What is the Python full path to use for running Python?')
            print('\t   (Ex: /usr/local/python3.10.0/bin/python3.10')
            print('\n\t   If you don\'t know, enter "which python3.10" on the CLI.\n\t   Copy and paste the full string.')
            print('\n\t   python3.10 is just an example.  It could be different in your system.')
            print('\n\nBegin setup ...')

            # Default the Keystack installation to /opt
            keystackRootPath = '/opt'
            # while True:
            #     keystackRootPath = input('\nWhere do you want to install Keystack folders? (Ex: /, /opt, /usr/local. Default=/opt): ')
            #     if keystackRootPath == '':
            #         keystackRootPath = '/opt'
            #         print('\nDefaulting to /opt')
            #         break
            #     else:
            #         if os.path.exists(keystackRootPath) == False:
            #             print('\nThere is no such path. Please try again ...')
            #             continue
            #         else:
            #             break

            if os.path.isdir(keystackRootPath) == False:
                execSubprocessInShellMode(f'sudo mkdir /opt')
                
            if os.path.exists('/opt') == False:
                raise Exception(f'No such folder exists: {keystackRootPath}\n')
            
            keystackSystemPath = f'{keystackRootPath}/KeystackSystem'
            keystackTestsPath = f'{keystackRootPath}/KeystackTests'
            SetupVar.keystackRootPath = keystackRootPath
            SetupVar.keystackTestPath = keystackTestsPath
            SetupVar.keystackSystemPath = keystackSystemPath
            
            import random, string 
            characters = string.ascii_letters + string.digits + string.punctuation
            randomKey = ''.join(random.choice(characters) for i in range(50))
            # /etc/keystack.yml
            execSubprocessInShellMode(f'sudo echo "keystackRootPath: {keystackRootPath}\nkeystackTestRootPath: {keystackTestsPath}\nkeystackSystemPath: {keystackSystemPath}\nwebToken: {randomKey}\n" | sudo tee /etc/keystack.yml', showStdout=False)

            while True:
                if os.path.exists(f'{keystackSystemPath}'):
                    response = input(f'\nThere is an existing Keystack installation. Do you want to blank out the existing Keystack installation?  (y or n): ')
                    if response.lower() not in ['y', 'n']:
                        print(f'\nYou entered "{response}". Please enter either y or n.')
                        continue

                    if response.lower().startswith('y'):
                        execSubprocessInShellMode(f'sudo rm -rf {keystackSystemPath}', showStdout=True)
                        execSubprocessInShellMode(f'sudo rm -rf {keystackTestsPath}', showStdout=True)
                        break
                    else:
                        break
                else:
                    break

            # NOTE: Don't ask for IP address anymore. Don't expect MongoDB on Linux host. Use MongoDB Container
            # if platform == 'linux':
            #     mongoIp = self.askUserForIpAddress()

            while True:
                # The Python path is used for running Serviceware background process python files 
                SetupVar.pythonFullPath = input('\nWhat is the localhost Python execution full path? ')
                if os.path.exists(SetupVar.pythonFullPath) == False:
                    print(f'\nNo such Python path found in: {SetupVar.pythonFullPath}. Please try again ...')
                else:
                    break

            # Generate web token
            import random, string
            characters = string.ascii_letters + string.digits + "~!@#%^&*()_-+=<>"
            randomKey = ''.join(random.choice(characters) for i in range(50))
            # /etc/keystack.yml                                                                                                
            if os.path.exists('/etc/keystack.yml'):
                execSubprocessInShellMode('sudo rm /etc/keystack.yml')

            execSubprocessInShellMode(f'sudo touch /etc/keystack.yml')
            execSubprocessInShellMode(f'sudo chmod o+w /etc/keystack.yml')
            keystackEtc = {'keystackRootPath': keystackRootPath,
                           'keystackSystemPath': keystackSystemPath,
                           'keystackTestRootPath': keystackTestsPath,
                           'webToken': randomKey
                           }
            writeToYamlFile(keystackEtc, '/etc/keystack.yml', mode='w')
            execSubprocessInShellMode(f'sudo chmod o-w /etc/keystack.yml')

            if platform == 'docker':
                # mongoIp = self.askUserForIpAddress()
                mongoIp = SetupVar.userEnvSettings['mongoIp']
                 
                # This will verify if Keystack container is currently running.
                # Stop the container if it is running.  If the container is the same version, remove the docker image
                stopDockerContainer(containerName='keystack', removeContainer=True, sudo=True)
                stopDockerContainer(containerName='mongo', removeContainer=True, sudo=True)
                removeDockerImage(SetupVar.keystackVersion, sudo=True)
                self.killListeningIpPorts()

            # Create keystack user
            isKeystackUserExists = execSubprocessInShellMode(f'sudo useradd -u {SetupVar.keystackUserUid} keystack')[-1]
            if 'already exists' in isKeystackUserExists:
                print('Keystack user already exists')
                # TODO: verify the user uid and correct accordingly if necessary
            else:
                print('Keystack user does not exists')

            # Create Keystack group
            # hgee wheel docker Keystack
            isKeystackGroupExists = execSubprocessInShellMode('groups')[-1]
            print('isKeystackGroupExists:', isKeystackGroupExists.replace('\n', '').split(' '))
 
            if 'Keystack' in isKeystackGroupExists.replace('\n', '').split(' '):
                print('Keystack user group already exists')
                isKeystackGroupExists2 = True  
                # TODO: verify the user uid and correct accordingly if necessary
            else:
                print('Keystack user group does not exists. Creating Keystack user group on Linux OS ...')
                execSubprocessInShellMode(f'sudo groupadd -g {SetupVar.keystackGroupGid} Keystack')
                isKeystackGroupExists2 = False  

            # hgee : hgee wheel docker Keystack
            addedSetupUser = False
            installationUser = os.environ['USER']
            
            for user in ['keystack', installationUser]:
                isUserInKeystackGroup = execSubprocessInShellMode(f'groups {user}')[-1]

                if 'Keystack' not in isUserInKeystackGroup.split(':')[-1]:
                    print(f'User {user} is not in group Keystack')
                    result = execSubprocessInShellMode(f'sudo usermod -aG Keystack {user}')[-1]
                    print(f'Verifying user {user} in Keystack group ...')
                    isUserInKeystackGroup = execSubprocessInShellMode(f'groups {user}')[-1]

                    if 'Keystack' not in isUserInKeystackGroup.split(':')[-1]:
                        raise Exception(f'Failed to add user {user} to user group Keystack')
                    else:
                        print(f'Successfully added user {user} to user group Keystack')
                        addedSetupUser = True
                else:
                    print(f'The user {user} is already in group Keystack')

            if isKeystackGroupExists2 == False:
                 # Activate the new group now so no need to logout/login
                execSubprocessInShellMode(f'sudo newgrp Keystack')

            # Create a list of Keystack folders
            keystackFolderList = [f'{keystackTestsPath}/Playbooks/DOMAIN=Keystack',
                                  f'{keystackTestsPath}/Envs/DOMAIN=Keystack',
                                  f'{keystackTestsPath}/Docker',
                                  f'{keystackTestsPath}/Modules',
                                  f'{keystackTestsPath}/Results',
                                  #f'{keystackTestsPath}/Testcases',
                                  f'{keystackTestsPath}/TestConfigs',
                                  f'{keystackTestsPath}/ResultsArchive',
                                  f'{keystackSystemPath}/Apps',
                                  f'{keystackSystemPath}/.DataLake',
                                  f'{keystackSystemPath}/Logs',
                                  f'{keystackSystemPath}/RestApiMods',
                                  f'{keystackSystemPath}/MongoDB',
                                  f'{keystackSystemPath}/SystemBackups',
                                  f'{keystackSystemPath}/MongoDB/storageData',
                                  f'{keystackSystemPath}/MongoDB/loggingData',
                                  f'{keystackSystemPath}/ResultDataHistory',
                                  f'{keystackSystemPath}/ServicesStagingArea/AwsS3Uploads',
                                ]

            for keyFolder in [keystackTestsPath, keystackSystemPath]:
                execSubprocessInShellMode(f'sudo mkdir -p {keyFolder}')

            for eachKeystackTestFolder in keystackFolderList:
                execSubprocessInShellMode(f'sudo mkdir -p {eachKeystackTestFolder}')

            # # Auto-generate keystackSystemSettings.env
            keystackSystemSettings = readFile(f"{currentDir}/Templates/keystackSystemSettings.yml")
            systemSettingReplacements = [('{pythonFullPath}', SetupVar.pythonFullPath),
                                         ('{dockerPythonFullPath}', SetupVar.dockerPythonFullPath),
                                         ('{platform}', platform),
                                         ('{mongoIp}', mongoIp),
                                         ('{mongoPort}', SetupVar.userEnvSettings["mongoPort"]),
                                         ('{keystackIp}', SetupVar.userEnvSettings["keystackIp"]),
                                         ('{keystackPort}', SetupVar.userEnvSettings["keystackPort"]),
                                         ('{redisPort}', SetupVar.userEnvSettings["redisPort"])
                                         ]

            for replacement in systemSettingReplacements:
                keystackSystemSettings = keystackSystemSettings.replace(replacement[0], str(replacement[1]))

            execSubprocessInShellMode(f'sudo echo "{keystackSystemSettings}" | sudo tee {keystackSystemPath}/keystackSystemSettings.yml')
            
            execSubprocessInShellMode(f'sudo cp {currentDir}/Templates/.loginCredentials.yml {SetupVar.keystackSystemPath}')
            execSubprocessInShellMode(f'sudo cp {currentDir}/Templates/domains.yml {SetupVar.keystackSystemPath}/.DataLake')
            execSubprocessInShellMode(f'sudo cp {currentDir}/Templates/customizeTestReport.yml {SetupVar.keystackSystemPath}')
            execSubprocessInShellMode(f'sudo cp {currentDir}/Templates/appStoreLocations.yml {SetupVar.keystackSystemPath}')
            
            # NGINX
            # execSubprocessInShellMode(f'sudo cp {currentDir}/keystackNginx_ubuntu.conf {SetupVar.keystackSystemPath}')
            # execSubprocessInShellMode(f'sudo cp {currentDir}/keystack-selfsigned.crt {SetupVar.keystackSystemPath}')
            # execSubprocessInShellMode(f'sudo cp {currentDir}/keystack-selfsigned.key {SetupVar.keystackSystemPath}')
            
            # Transfer samples to the created Keystack folders
            self.generateSamples(keystackRootPath=keystackRootPath, destinationPath=None, alreadyBackedUpSystemFiles=True)

            execSubprocessInShellMode(f'sudo cp -R {currentDir}/Apps {keystackSystemPath}')
            execSubprocessInShellMode(f'sudo rm {keystackTestsPath}/Modules/__init__.py')     
            execSubprocessInShellMode(f'sudo chmod -R 660 {keystackSystemPath}/.loginCredentials.yml')

            for keystackPath in [SetupVar.keystackTestPath, SetupVar.keystackSystemPath]:
                execSubprocessInShellMode(f'sudo chmod -R 770 {keystackPath}')
                execSubprocessInShellMode(f'sudo chown -R keystack:Keystack {keystackPath}')
                execSubprocessInShellMode(f'sudo chmod g+s {keystackPath}')

            execSubprocessInShellMode(f'sudo chmod -R 660 {SetupVar.keystackSystemPath}/.loginCredentials.yml')
            execSubprocessInShellMode(f'sudo mkdir -pv /var/log/nginx')
            execSubprocessInShellMode(f'sudo mkdir -pv /var/lib/nginx')
            execSubprocessInShellMode(f'sudo mkdir -pv /var/log/gunicorn')
            execSubprocessInShellMode(f'sudo mkdir -pv /var/run/gunicorn')
            execSubprocessInShellMode(f'sudo chmod -R 777 /var/log/nginx')
            execSubprocessInShellMode(f'sudo chmod -R 777 /var/lib/nginx')
            execSubprocessInShellMode(f'sudo chmod -R 777 /var/log/gunicorn')
            execSubprocessInShellMode(f'sudo chmod -R 777 /var/run/gunicorn')
            execSubprocessInShellMode(f'touch /run/nginx.pid')
            execSubprocessInShellMode(f'sudo chmod -R 777 /nginx.pid')

            if platform == 'docker':                
                # Start the keystack and mongo containers
                self.installAndStartDockerContainers(mongoIp, dockerBuildImagePath=dockerBuildImagePath)
                if verifyContainers(['mongo', 'keystack']) == False:
                    sys.exit('Keystack containers failed!')

                # Create a Keystack domain
                try:
                    # If setup was performed by pip
                    from Src.KeystackUI.execRestApi import ExecRestApi
                except:
                    # If setup was performed locally by running setupKeystack.py -setup
                    from execRestApi import ExecRestApi
                    
                httpIpAddress  = SetupVar.userEnvSettings["keystackIp"]
                keystackIpPort = SetupVar.userEnvSettings["keystackPort"]
                execRestApiObj = ExecRestApi(ip=httpIpAddress, port=keystackIpPort, headers=None, verifySslCert=None,
                                             https=False, keystackLogger=None)
                
                params = {'domain': 'Keystack', 'webhook': True}
                execRestApiObj.post(restApi='/api/v1/system/domain/create', params=params, showApiOnly=True)

            self.removeKeystackRunningServices()
            print('\nKeystack installation is done')

            if addedSetupUser:
                print(f'\nYOU MUST LOG OUT AND LOG BACK IN to use Keystack.  Otherwise, you cannot enter Keystack folders\n')
                
            # if keystackSystemSettingsFileExists:
            #     print(f'\nNOTE! Found existing keystackSystemSettings.env file. Backed it up to: {backupSystemSettingsFile}')

            print(f'\nNOTE! If you will be using AWS S3 and/or Jira with Keystack, you need to edit the following to add your login credentials: {keystackSystemPath}/.loginCredentials.yml\n')
        
            sys.exit(f'\nKeystack folders are installed at: {keystackTestsPath} and {keystackSystemPath}\n\n')

        except Exception as errMsg:
            sys.exit(f'\nsetupKeystack.py error: {traceback.format_exc(None,errMsg)}\n')

    def update(self, platform='docker', dockerBuildImagePath=None, version=None):
        """
        Update existing Keystack
           - Update the existing keystackSystemSettings.yml file with new parameters.
           - Update apps and samples
           - Restart AWS-S3 and Logs services if they're running.e
           - Install new Keystack Docker image.
        """
        if version:
            SetupVar.keystackVersion = version

        print(f'Update Keystack: Version: {SetupVar.keystackVersion}')
        
        if os.path.exists('/etc/keystack.yml'):
            etcKeystackYml              = readYaml('/etc/keystack.yml')
            SetupVar.keystackRootPath   = etcKeystackYml['keystackRootPath']
            SetupVar.keystackTestPath   = etcKeystackYml['keystackTestRootPath']
            SetupVar.keystackSystemPath = etcKeystackYml['keystackSystemPath']
            SetupVar.pythonFullPath     = etcKeystackYml['pythonPath']
        
        currentKeystackSystemSettingsFile = f'{SetupVar.keystackSystemPath}/keystackSystemSettings.yml'
        if os.path.exists(currentKeystackSystemSettingsFile) == False:
            raise Exception(f'setupKeystack update: Not found: {currentKeystackSystemSettingsFile}')

        #execSubprocessInShellMode(f'sudo {SetupVar.pythonFullPath} -m pip install keystack=={version}', showStdout=True)
        
        # Should not cp -r Samples/*. Has to be individually copied because not every setup
        # has LoadCore, AirMosaic, IxNetwork, IxLoad, etc
        execSubprocessInShellMode(f'cp -r Apps/* {SetupVar.keystackSystemPath}/Apps')
        execSubprocessInShellMode(f'cp -r Samples/Playbooks/* {SetupVar.keystackTestPath}/Playbooks')
        execSubprocessInShellMode(f'cp -r Samples/Envs/* {SetupVar.keystackTestPath}/Envs')
        
        if os.path.exists(f'{SetupVar.keystackTestPath}/Modules/Keystack_Samples'):
            execSubprocessInShellMode(f'cp -r Samples/Modules/Keystack_Samples/* {SetupVar.keystackTestPath}/Modules/Keystack_Samples')
            
        # if os.path.exists(f'{SetupVar.keystackTestPath}/Modules/LoadCore'):
        #     execSubprocessInShellMode(f'cp -r Samples/Modules/LoadCore/* {SetupVar.keystackTestPath}/Modules/LoadCore')

        execSubprocessInShellMode(f'cp Templates/restApiSamples {SetupVar.keystackTestPath}/Samples')
        execSubprocessInShellMode(f'sudo chmod -R 770 {SetupVar.keystackSystemPath}')
        execSubprocessInShellMode(f'sudo chmod -R 770 {SetupVar.keystackTestPath}')
        execSubprocessInShellMode(f'sudo chown -R :Keystack {SetupVar.keystackSystemPath}')
        execSubprocessInShellMode(f'sudo chown -R :Keystack {SetupVar.keystackTestPath}')

        # Get current list of keystack system settings parameteres
        currentKeystackSystemSettingKeys = []
        currentKeystackSystemSettings = readFile(currentKeystackSystemSettingsFile)

        for line in currentKeystackSystemSettings.split('\n'):
            match = search('.*(keystack_.+)=', line)
            if match:
                currentKeystackSystemSettingKeys.append(match.group(1))

        # Get updated list of parameters
        latestKeystackSystemSettings = readFile(f'{currentDir}/Templates/keystackSystemSettings.yml')
        latestKeystackSystemSettingsDict = dict()
        latestKeystackSystemSettingKeys = []

        for line in latestKeystackSystemSettings.split('\n'):
            match = search('.*(keystack_.+)=(.*)', line)
            if match:
                latestKeystackSystemSettingKeys.append(match.group(1))
                latestKeystackSystemSettingsDict[match.group(1)] = match.group(2)

        diff = list(set(latestKeystackSystemSettingKeys) - set(currentKeystackSystemSettingKeys))

        # Add new Keystack parameters to the bottom of the file
        if len(diff) > 0:
            print(f'\nAdding new Keystack params to the bottom of your existing file: {currentKeystackSystemSettingsFile}: {diff}')
            execSubprocessInShellMode(f'echo "\n#Added new params from Keystack version={SetupVar.keystackVersion} update" >> {currentKeystackSystemSettingsFile}\n')
            for newParam in diff:
                execSubprocessInShellMode(f'echo "{newParam}={latestKeystackSystemSettingsDict[newParam]}" >> {currentKeystackSystemSettingsFile}\n')

        # TODO: Do the same for customizeTestReport.yml

        self.removeKeystackRunningServices()
        
        if platform == 'docker':
            # This will verify if Keystack container is currently running.
            # Stop the container if it is running.  If the container is the same version, remove the docker image
            stopDockerContainer(containerName='keystack', removeContainer=True, sudo=True)
            stopDockerContainer(containerName='mongo', removeContainer=True, sudo=True)
            removeDockerImage(SetupVar.keystackVersion, sudo=True)

            #mongoIp = self.askUserForIpAddress()
            mongoIp = SetupVar.userEnvSettings['mongoIp']
            self.killListeningIpPorts()

            self.installAndStartDockerContainers(mongoIp, dockerBuildImagePath=dockerBuildImagePath)
            if verifyContainers(['mongo', 'keystack']) == False:
                sys.exit('Keystack containers failed!')
                
        sys.exit('\nKeystack update is done\n')

    def killListeningIpPorts(self):
        # Kill the Keystack port and Mongo port if they exist
        ipPortExistList = [f'{SetupVar.userEnvSettings["keystackPort"]}', f'{SetupVar.userEnvSettings["mongoPort"]}']
        for eachIpPort in ipPortExistList:
            isKeystackPortExists = execSubprocessInShellMode(f'sudo lsof -i tcp:{eachIpPort}')
            if isKeystackPortExists[-1]:
                execSubprocessInShellMode(f'sudo kill -9 {eachIpPort}')
                            
    def removeKeystackRunningServices(self):
        try:
            from Keystack.Src.Services import Serviceware
        except:
            from Services import Serviceware
            
        print('\nVerifying if Keytack services are running ...')  
        serviceObj = Serviceware.KeystackServices()
        if serviceObj.isServiceRunning('keystackAwsS3'):
            serviceObj.stopService('keystackAwsS3')

        if serviceObj.isServiceRunning('keystackLogs'):
            serviceObj.stopService('keystackLogs')
       
    def getVersion():
        pass
    
                             
def argParse():
    """
    For a new installation, you have to prime your the server with the followings:
        - Keystack folder structure
        - Add /etc/keystack.yml
        - Add keystackSystemSettings.yml
    """    
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    # This combination allows None defaulting to 'docker' or user defined value
    parser.add_argument('-setup',  nargs="?", default=None, const='docker', type=str, help='Setup initial Keystack environment. docker or linux')
    parser.add_argument('-update', nargs="?", default=None, const='docker', type=str, help='Update existing Keystack. docker or linux')
    
    parser.add_argument('-dockerFile', nargs="?", default=None, type=str, help='Where is the full path to the docker image tar file')
    
    parser.add_argument('-reinstallContainer', default=False, action='store_true', help='Reinstall the Keystack container')
    parser.add_argument('-stop',    default=False, action='store_true', help='Stop and remove the Keystack container')
    
    parser.add_argument('-getSamples', default=False, action='store_true', help='Generate sample scripts. Must include the -sampleTarget param stating the path to put the samples')
    parser.add_argument('-sampleDest', nargs="+", default=None, help='Provide a destination path for the sample files')
    parser.add_argument('-version',    default=False, action='store_true', help='Get the Keystack framework version')
    args = parser.parse_args()

    if args.dockerFile is not None:
        if os.path.exists(args.dockerFile) == False:
            sys.exit(f'\nError: -dockerFile cannot be located: {args.dockerFile}')
                
    if args.setup:
        if args.update is None:
            setup = 'docker'
        else:
            setup = args.update

        Setup().setup(platform=setup, dockerBuildImagePath=args.dockerFile)
        
    elif args.update:
        if args.update is None:
            update = 'docker'
        else:
            update = args.update

        Setup().update(platform=update, dockerBuildImagePath=args.dockerFile)
        
    elif args.getSamples:
        if args.sampleDest is None:
            sys.exit('\nYou must include the -sampleDest parameter that states the path to put the sample files.\n')
            
        Setup().generateSamples(destinationPath=args.sampleDest[0])
    
    elif args.reinstallContainer:
        reinstallContainer()
        
    elif args.stop:
        stop()
        
    elif args.version:
        from commonLib import showVersion
        showVersion()
        
    else:
        sys.exit('\nA parameter is required: -setup | -update | -getSamples -sampleDest\n')

def setup():
    """
    This is an entry-point for the CLI command setupKeystack
    
    By default, if dockerImagePath is None, setup and update will default to downloading
    the Keystack image from docker hub
    
    setupKeystack -setup docker 
     
    setupKeystack -setup -dockerBuildImagePath <full path to docker tar file>
    setupKeystack -update -dockerBuildImagePath <full path to docker tar file>   
    """
    result, output = execSubprocessInShellMode('which docker')
    if bool(re.search('.*docker', output)) == False:
        sys.exit('\nError: docker needs to be installed in this Linux host.\n')
        
    argParse()

def reinstallContainer():
    """ 
    This is an entry-point for the CLI command reinstall the container in setup.cfg
    """
    execSubprocessInShellMode('docker compose down')
    sleep(2)
    execSubprocessInShellMode('docker compose up -d')
    if verifyContainers(['mongo', 'keystack']) == False:
        sys.exit('Keystack containers failed!')
        
    print('\nKeystack docker container is reinstaalled\n')

def stop():
    """ 
    This is an entry-point for the CLI command stopKeystack in setup.cfg
    """
    execSubprocessInShellMode('docker compose down')
    if verifyContainers(['mongo', 'keystack']) == False:
        print('\nKeystack docker container is stopped and removed\n')
    else:
        sys.exit('Failed to bring down Keystack containers')
 
def help():
    os.system('clear')
    print('\nsetupKeystack command line help')
    print('-------------------------------')
    print('** Keystack installation/update requires a SUDO user and docker already installed')
    print('** You could still use Keystack test framework as a CLI without the docker container')
    print('** but Env mgmt, App store and many more features will not be supported')
    print('** If using env yaml files as testbeds, each env ymal file must set parallelUsage=True.\n\n')
    print('   -setup: Set up Keystack test framework and docker container for testing\n')
    print('   -update: Update Keystack test framework and docker container\n')
    print('   -dockerBuildImagePath: Full path to the docker tar file to be installed')
    print('                          Requires a zip file provided by a Keystack maintaniner')
    print('                          Mainly used by environment with no internet')
    print('                          Include this parameter and value along with either -setup or -update\n')  
    print('   -reinstallContainer: Reinstall the Keystack docker container\n')
    print('   -stop: Stop and remove the active Keystack container\n')
    print()
    
                          
if __name__ == "__main__":
    argParse()
    
    


