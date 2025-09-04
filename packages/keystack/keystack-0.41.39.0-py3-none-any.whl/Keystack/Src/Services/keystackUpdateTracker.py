import os, sys
from time import sleep

currentDir = os.path.abspath(os.path.dirname(__file__))
keystackRootPath = currentDir.replace('/Services', '')
sys.path.insert(0, keystackRootPath)
sys.path.append(f'{keystackRootPath}/KeystackUI')

from KeystackUI.topbar.settings.domains.domainMgr import DomainMgr
from RedisMgr import RedisMgr
from keystackUtilities import readYaml
from commonLib import syncTestResultsWithRedis
from globalVars import GlobalVars

if os.path.exists('/etc/keystack.yml') == False:
    sys.exit()

etcKeystackYml = readYaml('/etc/keystack.yml')
if os.path.exists(etcKeystackYml['keystackTestRootPath']) == False:
    sys.exit(f'keystackProvision error: keystackTestRootPath path not found: {etcKeystackYml["keystackTestRootPath"]}')
            
keystackTestRootPath = etcKeystackYml['keystackTestRootPath']
keystackSystemPath= etcKeystackYml['keystackSystemPath']

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)

RedisMgr().connect(host='0.0.0.0', port=keystackSettings.get('redisPort', '6379'))

startCounter = 0
stopCounter = 3

while True:
    if  RedisMgr.redis:
        DomainMgr().dumpDomainDataToRedis()
        
        # Sync all filesystem test results to Redis
        syncTestResultsWithRedis()
        print(f'\n--- counter: {startCounter}/{stopCounter}')
        startCounter += 1
        break