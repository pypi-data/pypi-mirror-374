import re
from django import template
from globalVars import GlobalVars

register = template.Library()

@register.simple_tag
def shortenDisplayPath(path):
    """
    Don't show full path. 
    """
    pathList = path.split('/')
    modulesIndex = pathList.index('Modules')
    shortenPathList = pathList[modulesIndex+1:]
    displayPath = '/'.join(shortenPathList)
    displayPath = f'/{displayPath}'
    return displayPath

@register.simple_tag
def getPlaybookPath(playbookPath):
    """ 
        ('/Samples/pythonSample.yml', '/opt/KeystackTests/Playbooks/Samples/pythonSample.yml')
    """
    return playbookPath[1]

@register.simple_tag
def getPlaybookName(playbookPath):
    """
        Return the playbook and its namespace: /Samples/pythonSample 
         
        ('/Samples/pythonSample.yml', '/opt/KeystackTests/Playbooks/Samples/pythonSample.yml')
    """
    playbook = playbookPath[0].split('.')[0]
    if playbook[0] == '/':
        playbook = playbook[1:]
    
    return playbook



