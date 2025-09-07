from keystackEnv import keystack
import time, sys

keystack.logInfo('Running Sample Module Demo/bgp.py')

# Create a failure
keystack.logFailed('Failed: No BGP routes discovered')

keystack.logDebug('Debug message')
keystack.logWarning('Warning message')

try:
    # Examples: How to dynamically get passed-in parameters/values from envs, testcases and playbookVars
    
    keystack.logInfo(f'----  keystack.taskParams: {keystack.taskProperties}')
    keystack.logInfo(f'----  envParams: {keystack.taskProperties["envParams"]}')
    
    keystack.logInfo(f'----  keystack.testcaseParams: {keystack.testcaseParams}')

    keystack.logInfo(f'----  keystack.testcaseParams.scriptCmdlineArgs: {keystack.testcaseParams["scriptCmdlineArgs"]}')
    keystack.logInfo(f'----  keystack.testcaseParams.exportedConfigsFile: {keystack.testcaseParams["exportedConfigsFile"]}')
    keystack.logInfo(f'----  keystack.testcaseParams.dataConfigsFile: {keystack.testcaseParams["dataConfigsFile"]}')
    keystack.logInfo(f'----  keystack.testcaseParams.dataConfigs: {keystack.testcaseParams["dataConfigs"]}')

    keystack.logInfo(f'----  keystack.portGroupsData: {keystack.portGroupsData} ---')

    keystack.logInfo(f'----  keystack.portsData: {keystack.portsData}')

    keystack.logInfo(f'----  keystack.deviceData.device-2.: {keystack.devicesData}')

    keystack.logInfo(f'----  keystack.taskParams.playbookVars: {keystack.taskProperties["playbookVars"]}')
    keystack.logInfo(f'----  keysack.taskParams.artifactsFolder: {keystack.taskProperties["artifactsFolder"]}')
except:
    pass

time.sleep(0)

import threading

def print_cube(num):
    # function to print cube of given num
    keystack.logInfo("Cube: {}" .format(num * num * num))

def print_square(num):
    # function to print square of given num
    keystack.logInfo("Square: {}" .format(num * num))

t1 = threading.Thread(target=print_square, args=(10,))
t2 = threading.Thread(target=print_cube, args=(10,))

# starting thread 1
t1.start()
# starting thread 2
t2.start()

# wait until thread 1 is completely executed
t1.join()
# wait until thread 2 is completely executed
t2.join()

# both threads completely executed
keystack.logInfo("Done!")

