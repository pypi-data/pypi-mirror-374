import os, sys
from re import search, I
import subprocess
from setuptools import setup

# Assuming that the dev folder is in /opt/keystack_src
# currentDir: /opt/keystack_src/BuildPackages
currentDir = os.path.abspath(os.path.dirname(__file__))
rootPath = '/opt/keystack_src'
srcPath = '/opt/keystack_src/Src'

# importing from keystackUtilities doesn't work. Cannot import yaml.
def execSubprocessInShellMode(command, showStdout=True):
    """
    Linux CLI commands
    """
    print(f'-> {command}')
    result = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result,err = result.communicate()
    
    if showStdout:
        for line in result:
            if type(line) is bytes:
                line = line.decode('utf-8')
                print('line:', line)
                if bool(search('ERROR.*', line, I)):
                    sys.exit(1)

    return result.decode('utf-8')


# This creates the Keystack folder for pip installation located in site-packates/Keystack
os.makedirs(f'{currentDir}/Keystack', exist_ok=True)
os.makedirs(f'{currentDir}/Keystack/Src', exist_ok=True)
os.makedirs(f'{currentDir}/Keystack/BuildPackages/', exist_ok=True)
os.makedirs(f'{currentDir}/Keystack/BuildPackages/Setup', exist_ok=True)

# Copy all required files to be packaged to the local directory folder call Keystack
# /opt/keystack_src/BuildPackages/PackageKeystack/Keystack. 
# The  MANIFEST.in file will do an include from this local Keystack folder to
# site-packages/Keystack
cmdList = [f'cp {rootPath}/version ./Keystack',
           f'cp {rootPath}/LICENSE ./Keystack',
           f'cp {rootPath}/releaseNotes ./Keystack',
           f'cp {rootPath}/__init__.py ./Keystack',
           f'cp {srcPath}/__init__.py ./Keystack/Src',
           f'cp {srcPath}/keystack.py ./Keystack/Src',
           f'cp {srcPath}/runPlaybook.py ./Keystack/Src',
           f'cp {srcPath}/EnvMgmt.py ./Keystack/Src',
           f'cp {srcPath}/sshAssistant.py ./Keystack/Src',          
           f'cp {srcPath}/accountMgr.py ./Keystack/Src',
           f'cp {srcPath}/domainMgr.py ./Keystack/Src',
           f'cp {srcPath}/PortGroupMgmt.py ./Keystack/Src',
           f'cp {srcPath}/LabInventory.py ./Keystack/Src',
           f'cp {srcPath}/RedisMgr.py ./Keystack/Src',
           f'cp {srcPath}/globalVars.py ./Keystack/Src',
           f'cp {srcPath}/commonLib.py ./Keystack/Src',
           f'cp {srcPath}/keystackUtilities.py ./Keystack/Src',
           f'cp {srcPath}/scheduler.py ./Keystack/Src',
           f'cp {srcPath}/db.py ./Keystack/Src',
           f'cp {srcPath}/LoggingAssistants.py ./Keystack/Src',
           f'cp {rootPath}/BuildPackages/Setup/setupKeystack.py ./Keystack/BuildPackages/Setup',
           f'cp {rootPath}/BuildPackages/Setup/userEnvSettings.yml ./Keystack/BuildPackages/Setup',
           f'cp -r {rootPath}/BuildPackages/Setup/Templates ./Keystack/BuildPackages/Setup',
           f'cp -r {rootPath}/BuildPackages/Setup/Samples ./Keystack/BuildPackages/Setup',
           f'cp {rootPath}/Src/KeystackUtilities.py ./Keystack/BuildPackages/Setup',
           f'cp -r {srcPath}/CLI ./Keystack/Src',
           f'cp -r {srcPath}/RunTaskAssistants ./Keystack/Src',
           f'cp -r {srcPath}/KeystackAssistants ./Keystack/Src',
           f'cp -r {srcPath}/KeystackUI ./Keystack/Src',
           f'cp -r {srcPath}/Services ./Keystack/Src',
           #f'cp -r {rootPath}/BuildPackages/Setup ./Keystack',
           f'cp -r {rootPath}/Docs ./Keystack',
           #f'rm -rf ./Keystack/Setup/Apps/AirMosaic',
           #f'rm -rf ./Keystack/Setup/Apps/LoadCore',
           #f'rm -rf ./Keystack/Setup/Apps/IxSuiteStore',
           #f'rm -rf ./Keystack/Setup/Apps/IxNetworkDataModel'
           ]

for cmd in cmdList:
    execSubprocessInShellMode(cmd)
        
setup()
