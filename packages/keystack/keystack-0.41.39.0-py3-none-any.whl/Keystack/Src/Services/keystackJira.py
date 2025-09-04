import os, sys, traceback

currentDir = currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(currentDir.replace('/Services', ''))

from JiraLib import Jira
from utilities import readYaml, getTimestamp, makeFolder, updateLogFolder
from Serviceware import vars, writeToServiceLogFile
 
try:
    updateLogFolder(logFolderSearchPath=f'{vars.keystackServiceLogsFolder}/jiraServiceLogs*',
                    removeAfterDays=vars.removeLogsAfterDays) 
    
    issueList = ['Hubert jira dev issue test1', 'Hubert jira dev issue test2']
    
    jiraObj = Jira(jiraServer=os.environ['keystack_jiraServer'], username=os.environ['keystack_jiraLogin'],
                    password=os.environ['keystack_jiraPassword'], project=os.environ['keystack_jiraProject'],
                    logFile=vars.jiraServiceLogFile)
        
    jiraObj.connect()
    jiraObj.createIssueList(issueList=issueList)
    jiraObj.showIssues()
                
except Exception as errMsg:
    writeToServiceLogFile(vars.jiraServiceLogFile, 
                          f'keystack_jira: Exception: {traceback.format_exc(None, errMsg)}')