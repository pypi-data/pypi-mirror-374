""" 
Delete past logs every time this script is executed.
Then go into the while loop to delete every 24 hours
"""
import os, sys
from time import sleep

currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir.replace('/Services', '/KeystackUI'))
from systemLogging import SystemLogsAssistant

# ['results', 'accountMgmt', 'modules', 'sessions']

SystemLogsAssistant().deletePastLogs()

while True:
    # 3600=1hr, 86400=24hrs
    sleep(86400)
    SystemLogsAssistant().deletePastLogs()
    



