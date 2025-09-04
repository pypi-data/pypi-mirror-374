"""
jiraLib.py

Description:
    Automate opening new or closed defects in Jira.
    
    - If an Jira issue already exists and the issue is opened, append failure description.
    - If the issue is closed, reopen it and append the faiure description.
    
    - If an issueKey is provided in the testcase yml file, then use the issueKey to append
      the failure description and change the status to a "To Do" status.
      An open status word is customizable in Jira.  So it depends on what word is used.

Dev notes:
    https://jira.readthedocs.io/
    
Requirements
    - pip install: jira requests
    - utilities.py module located in the same local folder
    - This module requires linux environment variables set in the keystackSystemSettings.evn file:
        /KeystackTests/KeystackSystem/keystackSystemSettings.env
    
        keystack_jiraConnectMethod = token
        keystack_jiraServer   = https://jira.it.company.com
        keystack_jiraUsername = username
        keystack_jiraPassword = password
        keystack_jiraEmail =
        keystack_jiraToken =  
        keystack_jiraProject  = project
        keystack_jiraSetFailedStatus = To Do
        keystack_jiraRemoveLogsAfterDays = 5

Author: Hubert Gee 
"""
import os, sys, traceback, json
from datetime import datetime

from jira import JIRA

from Services import Serviceware
from keystackUtilities import getTimestamp, writeToFile, updateLogFolder, readYaml
from globalVars import GlobalVars

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    
def getLoginCredentials(credentialYmlFile, loginCredentialKey):
    if os.path.exists(credentialYmlFile) == False:
        raise Exception(f'Login credentials file not found: {credentialYmlFile}.')
    
    loginCredentialObj = readYaml(credentialYmlFile)
    loginCredentials = loginCredentialObj[loginCredentialKey]      
    return loginCredentials

  
class Jira():
    def __init__(self, logFile=None, logFolder=None, loginCredentialKey=None):
        """
        Requires a Linux environment file containing keystack_ parameters.
        
        Parameters:
           logFile <str>: Defaults to Keystack Services.Serviceware
        """
        etcKeystackYml = readYaml('/etc/keystack.yml')
        self.keystackSystemPath = etcKeystackYml['keystackSystemPath']
        self.loginCredentialsFile = f'{self.keystackSystemPath}/.loginCredentials.yml'
        self.loginCredentials = getLoginCredentials(self.loginCredentialsFile, loginCredentialKey)
        
        self.connectionMethod = self.loginCredentials['jiraConnectionMethod']
        self.jiraServer       = self.loginCredentials['jiraServer']
        self.username         = self.loginCredentials['jiraUsername']
        self.password         = self.loginCredentials['jiraPassword']
        self.email            = self.loginCredentials['jiraEmail']
        self.token            = self.loginCredentials['jiraToken']
        self._project         = self.loginCredentials['jiraProject']
        self.jiraObj = None
        
        if logFile:
            self.logFile = logFile
        else:
            self.logFile = Serviceware.vars.jiraServiceLogFile

        if os.path.exists(self.logFile) == False:
            open(self.logFile, 'w').close()
                            
        if logFolder is None:
            logFolder = f'{Serviceware.vars.keystackServiceLogsFolder}/jiraServiceLogs*'
            
        updateLogFolder(logFolderSearchPath=logFolder, removeAfterDays=keystackSettings.get('removeLogsAfterDays', 3))
                
    def log(self, msg):
        if self.logFile:
            writeToFile(self.logFile, f'{getTimestamp()}: {msg}')
        
    def connect(self):
        """
         Few ways to connect:
           1> Cookie Based Authentication (auth): JIRA(auth=('username', 'password'))
           2> HTTP Basic (basic_auth): JIRA(basic_auth=('username', 'password'))
           3> Token: JIRA(basic_auth=('email', 'API token'))
        """   
        try:
            self.log(f'JiraLib: connect: {self.jiraServer} as {self.username} ...')
            if self.connectionMethod == 'cookieBased':
                self.jiraObj = JIRA(server=self.jiraServer, auth=(self.username, self.password))
                
            if self.connectionMethod == 'httpBasic':
                self.jiraObj = JIRA(server=self.jiraServer, basic_auth=(self.username, self.password))                

            if self.connectionMethod == 'token':
                self.jiraObj = JIRA(server=self.jiraServer, basic_auth=(self.email, self.token))
            
            if self.jiraObj is None:
                raise Exception(f'JiraLib: No connection made using: {self.connectionMethod}')
                              
        except Exception as errMsg:
            self.log(errMsg)
            raise Exception(errMsg)
        
    @property
    def project(self):
        return self._project
    
    @project.setter
    def project(self, projectName):
        self._project = projectName
                                    
    def createIssueList(self, issueList, addCommentToExistingIssue=False):
        """ 
        Pass in a list of new issues using the below dict format. 
        Some parameters are optional such as: components, priority, assignee

            issueList = [
                {'project': {'key': jiraProject},
                'summary': 'Bug title',
                'description': f'Date bug found: {getTimestamp()}\n\nDescription:\n\t{description}',
                'issuetype': {'name': 'Bug'},
                'components': 'components',
                'assignee': {'name': 'name'},
                'priority': {'name': 'Medium'}
                }
            ]
        """
        jiraIssueList = []
        for newIssue in issueList:
            if self.isIssueCreated(newIssue['summary']):
                # Append failure to existing issue
                currentStatus = self.getIssueFields(field='status', bySummary=newIssue['summary'])
                # inactiveStatus could be examples: Closed, Passed, NotRunning
                inactiveStatus = [x.strip() for x in self.loginCredentials['jiraInactiveStatus'].split(',')]
                projectKey = self.getIssueKeyBySummary(newIssue['summary'])
                
                if str(currentStatus) in inactiveStatus:
                    self.log(f'createIssueList: The issue is already exist in Jira: Key={projectKey}: {newIssue["summary"]}:  Status={currentStatus}')
                    self.changeIssueStatus(projectKey, self.loginCredentials['jiraSetActiveStatus'])
                    
                if addCommentToExistingIssue:
                    self.addComments(projectKey, comments=f"Encountered failure again!\n\n{newIssue['description']}")

                continue
            else:
                jiraIssueList.append(newIssue)
            
        if jiraIssueList:
            self.log(f'JiraLib: createIssueList: {json.dumps(jiraIssueList, indent=4)}')                 
            self.jiraObj.create_issues(field_list=jiraIssueList)
    
    def updateIssue(self, issueKey, description, setStatus=False):
        """ 
        Update an existing issue with new description and optionally
        set the status to a failed status.  
        Sometimes, an issue just needs to be updated with comments 
        without changing the status.
        """
        self.log(f"updateIssue: {issueKey}: {description}")
        currentStatus = self.getIssueFields(field='status', byKey=issueKey)
        self.log(f"updateIssue: current status: {currentStatus}")
        
        # ['Closeed', 'Passed']
        inactiveStatus = [x.strip() for x in self.loginCredentials['jiraInactiveStatus'].split(',')]
        self.log(f"updateIssue: inactive status: {inactiveStatus}")
        if str(currentStatus) in inactiveStatus:
            if setStatus:
                self.changeIssueStatus(issueKey, setStatus)
            
        self.addComments(issueKey, comments=description)
                                    
    def getIssueFields(self, bySummary=None, byKey=None, field=None):
        """ 
        field properties: assignee, comment, components, created, description, priority,
        progress, project, reporter, status, summary, id, key 
        """
        if bySummary:
            issues = self.jiraObj.search_issues(f'project={self._project}')
            for issue in issues:
                if bySummary == issue.fields.summary:
                    return getattr(issue.fields, field)
        
        if byKey:
            self.log(f'Jira.getIssueFields:{byKey}')
            issue = self.jiraObj.issue(byKey)
            return getattr(issue.fields, field)
                
    def changeIssueStatus(self, projectKey, changeStatusTo):
        self.log(f'changeIssueStatus: Key={projectKey}  ChangeStatusTo={changeStatusTo}')
        self.jiraObj.transition_issue(projectKey, changeStatusTo)

    def getIssueKeyBySummary(self, issueSummary):
        """ 
        Get the issue key by the summary
        """
        issues = self.jiraObj.search_issues(f'project={self._project}')
        for issue in issues:
            if issueSummary == issue.fields.summary:
                return issue.key
                
    def getIssueByKey(self, issueKey):
        """
        Parameter: 
            issueKey <str>: KEYS-18
        
        ['add_field_value', 'delete', 'expand', 'fields', 'find', 'get_field', 'id', 
        'key', 'permalink', 'raw', 'self', 'update']
        
        Usage:
            issue = jiraObj.getIssueByKey('KEYS-18)
            print(issue.fields.summary)
        """
        return self.jiraObj.issue(issueKey)
    
    def addComments(self, projectKey, comments):
        self.log(f'addComments: projectKey:{projectKey}  comments:{comments}')
        self.jiraObj.add_comment(projectKey, comments)
                    
    def isIssueCreated(self, searchForIssue):
        """ 
        Verify if there is an existing issue by the summary
        """
        issues = self.jiraObj.search_issues(f'project={self._project}')
        for issue in issues:
            existingSummary = issue.fields.summary
            if existingSummary.strip() == searchForIssue.strip():
                return True
        
        return False
     
    def showIssues(self):
        issues = self.jiraObj.search_issues(f'project={self._project}')
        while True:
            if len(issues) == 0:
                break
            
            for issue in issues:
                print(f'Ticket Number: {issue}\nIssueType: {issue.fields.issuetype.name}\nStatus: {issue.fields.status.name}\nSummary: {issue.fields.summary}\n') 
          
            break

    def getProjects(self):
        return self.jira.projects()
    

if __name__ == "__main__":       
    try:
        # For test development  
        #from dotenv import load_dotenv 
        #load_dotenv('/Users/hubergee/KeystackSystem/keystackSystemSettings.env')
        logFile = '/Users/hubergee/KeystackSystem/Logs/jiraServiceLogs'
        
        jiraObj = Jira(logFile=logFile)          
        jiraObj.connect()
        
        issueList = [                
                {'project': {'key': 'KEYS'},
                'summary': 'TEST2 TEST2 TEST2',
                'description': 'Not a real bug.  Testing Python Jira development',
                'issuetype': {'name': 'Bug'},
                'assignee': {'name': keystackSettings['jiraAssignee']},
                'priority': {'name': keystackSettings['jiraPriority']}
                }]
         
        #jiraObj.createIssueList(issueList=issueList, addCommentToExistingIssue=True)
        #jiraObj.showIssues()
        projects = jiraObj.getProjects()
        print('\nprojects:', projects)
        
        issue = jiraObj.getIssueByKey('KEYS-43')
        print('\nissue:', issue.fields.status)
            
        status = jiraObj.getIssueFields(byKey='KEYS-43', field='status')
        print('\ncurrent status:', status)
        
        jiraObj.updateIssue(issueKey='KEYS-43', description='Dev test', setStatus=keystackSettings['jiraSetActiveStatus'])
        
    except Exception as errMsg:
        sys.exit(f'\njiraLib: {traceback.format_exc(None, errMsg)}')
   
