import os
from pydantic import Field, dataclasses
from keystackUtilities import sendEmail, readYaml
from globalVars import GlobalVars

keystackSettings = readYaml(GlobalVars.keystackSystemSettingsFile)
    
@dataclasses.dataclass
class EmailAssistant:
    keystackObj: object

    def emailReport(self):
        """ 
        Emailing depends on the Linux server running 
        Keystack having postfix installed and running
        """
        self.keystackObj.keystackLogger.debug()
        sendTo = None
        attachments = []
        
        if self.keystackObj.emailResults:
            if self.keystackObj.debug and 'devModeEmailTo' in keystackSettings:
                sendTo = keystackSettings['devModeEmailTo']
            else:
                if 'emailTo' in keystackSettings:
                    sendTo = keystackSettings['emailTo']
            
            if sendTo is None:
                self.keystackObj.keystackLogger.debug('\nNo Email sent.  emailTo was not defined in keystackSystemSettings\n')
                #print('\nNo Email sent.  keystack_emailTo was not defined in keystackSystemSettings.env\n')
                return

            if self.keystackObj.trackResults:
                self.keystackObj.keystackLogger.debug(f'Appending attachment file: {self.keystackObj.updateCsvDataFile}')
                attachments.append(self.keystackObj.updateCsvDataFile)
            
            self.keystackObj.keystackLogger.debug(f'SendTo:{sendTo} fromSender:{keystackSettings["emailFrom"]}')    
            sendEmail(emailTo=sendTo,
                      fromSender=keystackSettings['emailFrom'],
                      subject=self.keystackObj.subjectLine,
                      bodyMessage=self.keystackObj.reportBody,
                      emailAttachmentList=attachments) 
            print()