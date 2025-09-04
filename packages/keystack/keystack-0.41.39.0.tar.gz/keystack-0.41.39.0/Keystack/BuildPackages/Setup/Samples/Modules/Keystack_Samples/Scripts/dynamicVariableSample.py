import time, sys, json
from keystackEnv import keystack

# Instead of using print, use the followings which will get logged into testcase test.log:
#    keystack.logInfo
#    keystack.logWarning
#    keystack.logDebug
#    keystack.logFailed
#    keystack.logError  <- This will abort the test immediately.

# Get dynamic variables from the Env parameter/values that was used in the playbook 
keystack.logInfo(f': {keystack.taskProperties["envParams"]}')

# Get dynamic variables passed in from the playbook                  
keystack.logInfo(f'ServerName from Playbook: {keystack.taskProperties["playbookVars"]["serverName"]}')
keystack.logInfo(f'ServerIp from Playbook: {keystack.taskProperties["playbookVars"]["serverIp"]}')

keystack.logWarning('dynamicVariableSample warning message')
keystack.logDebug('debug message')

# Create a failure
#keystack.logFailed('Failed: This is a sample test failed message')

# Create artifacts and put them in a shared location for other tests to access them
jsonFile = f'{keystack.taskProperties["artifactsFolder"]}/myTestData.json'
data = {'test': 'server', 'result': 'Passed'}
with open(jsonFile, mode='w', encoding='utf-8') as fileObj:
          json.dump(data, fileObj)

time.sleep(0)

# Supports running multi thread jobs
import threading

def print_cube(num):
    # function to print cube of given num
    print("Cube: {}" .format(num * num * num))

def print_square(num):
    # function to print square of given num
    print("Square: {}" .format(num * num))

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
print("Done!")

