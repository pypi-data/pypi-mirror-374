import os, re, sys
from pydantic import Field, dataclasses

from globalVars import GlobalVars
from commonLib import KeystackException, validatePlaybook
from keystackUtilities import readYaml

@dataclasses.dataclass
class ValidatePlaybookAssistant:
    """ 
    This class is only called by keystack.
    """
    keystackObj: object

    def validatePlaybook(self):
        # Default: Dynamically-Created
        self.keystackObj.userDefinedPlaybook = self.keystackObj.playbook
        
        if self.keystackObj.userDefinedPlaybook != 'Dynamically-Created':
            # /path/KeystackTests/Playbooks/DOMAIN=Communal/Samples/advance
            if 'Playbooks/' in self.keystackObj.userDefinedPlaybook:
                match = re.search('.*Playbooks/(.*)', self.keystackObj.userDefinedPlaybook)
                if match:
                    playbook = match.group(1)
                else:
                    # NOTE: At of time, entering /Playbooks/<group>/<playbook> will not work
                    #       Just pass in DOMAIN=<domain>/<group>/<playbook>
                    playbook = self.keystackObj.userDefinedPlaybook
            else:
                # DOMAIN=Communal/Samples/advance
                if 'DOMAIN' not in self.keystackObj.userDefinedPlaybook:
                    playbook = f'DOMAIN={self.keystackObj.domain}/{self.keystackObj.userDefinedPlaybook}'
                else:
                    playbook = self.keystackObj.userDefinedPlaybook
               
            if '.yml' not in playbook:
                playbookName = f'{playbook}.yml'
            if '.yml' in playbook:
                playbookName = playbook
                    
            # Playbook full path:  /opt/KeystackTests/Playbooks/DOMAIN=Communal/Samples/pythonSample.yml
            self.keystackObj.playbook = f'{GlobalVars.playbooks}/{playbookName}'
            self.keystackObj.overallSummaryData['playbook'] = self.keystackObj.playbook
            if os.path.exists(self.keystackObj.playbook) is False:
                errorMsg = f'validatePlaybook(): No playbook found in: {self.keystackObj.playbook}'
                self.keystackObj.overallSummaryData['pretestErrors'].append(errorMsg)
                    
            # Samples-advance -> For creating result timestamp folder name
            # playbookAndNamespace: DOMAIN=Regression-Samples-advance
            self.keystackObj.playbookAndNamespace = self.keystackObj.playbook.split(f'{GlobalVars.playbooks}/')[1].split('.')[0].replace('/', '-')
            self.keystackObj.playbookName = self.keystackObj.playbookAndNamespace
        else:
            self.keystackObj.playbookName = 'Dynamically-Created'
         
        if os.path.exists(self.keystackObj.playbook) is False:
            raise KeystackException(f'validatePlaybook(): No such playbook located: {self.keystackObj.playbook}')
           
        try:
            readYaml(self.keystackObj.playbook)
        except Exception as errMsg:
            errorMsg = f'validatePlaybook(): The playbook yml file has syntax errors: {self.keystackObj.playbook}'
            self.keystackObj.overallSummaryData['pretestErrors'].append(errorMsg)
            return
        
        # Read the playbook yml file first. Then if rest api, overwrite the playbook settings
        if self.keystackObj.userDefinedPlaybook != "Dynamically-Created":
            self.keystackObj.playbookTasks = readYaml(self.keystackObj.playbook, threadLock=self.keystackObj.lock)       
            if self.keystackObj.playbookTasks is None:
                errorMsg = f'validatePlaybook(): Playbook is empty.  Check ymal syntaxes: {self.keystackObj.playbook}'
                self.keystackObj.overallSummaryData['pretestErrors'].append(errorMsg)
            else:
                # This will validate playlist and envs
                # Will abort test after self.keystackObj.overallSummaryData is created a little further down
                validatePlaybookResult, validatePlaybookProblems = validatePlaybook(self.keystackObj.playbook, 
                                                                                    self.keystackObj.playbookTasks,
                                                                                    checkLoginCredentials=self.keystackObj.checkLoginCredentials)

                if validatePlaybookResult is False:
                    for problem in validatePlaybookProblems:
                        self.keystackObj.overallSummaryData['pretestErrors'].append(problem)

                    # Put pipeline results on redis 
                    self.keystackObj.connectToRedis()
                    self.keystackObj.updateOverallSummaryFileAndRedis()

        else:
            # This will get updated in getRestApiMods()
            # The playbook will get validated from restApi/playbookView
            self.keystackObj.playbookTasks = {}    
    
    def verifyPlaybookEnvUserGroup(self):
        playbookData = readYaml(self.keystackObj.playbook)
        
        