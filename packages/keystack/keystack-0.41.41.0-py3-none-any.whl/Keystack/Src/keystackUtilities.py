import os, re, io, json, yaml, datetime, subprocess, time, platform, traceback
from pathlib import Path
from glob import glob
import errno
import fcntl
from shutil import copyfile, rmtree

def getDateTime():
    """
    Returns a floating time integer: 1590854435.325839
    """
    return int(str(time.time()).replace('.', ''))
    #return int(time.time())

def getTime():
    """
    Returns: 15:14:18.053384
    """
    dateAndTime = str(datetime.datetime.now()).split(' ')
    return dateAndTime[1]

def getDate():
    """
    Returns: 08-27-2018
    """
    dateAndTime = str(datetime.datetime.now()).split(' ')
    currentDate = dateAndTime[0]
    year = currentDate.split('-')[0]
    month = currentDate.split('-')[1]
    date = currentDate.split('-')[2]
    return month + '-' + date + '-' + year

def getTimestamp(includeMillisecond:bool=True) -> str:
    now = datetime.datetime.now()
    
    if includeMillisecond:
        timestamp = now.strftime('%m-%d-%Y-%H:%M:%S:%f')
    else:
        timestamp = now.strftime('%m-%d-%Y-%H:%M:%S')
        
    return timestamp
        
def dictKeyExists(dictObj, keys):
    """
    Verify if nested keys exists in a dict object.

    Parameters
       dictObj: The dictionary object
       keys: (list): A list of keys to verify against the dictObj
    """
    _dictObj = dictObj
    for key in keys:
        try:
            _dictObj = _dictObj[key]
        except KeyError:
            return False
    
    return True

def getDictItemFromList(listOfDict, key, value):
    """
    Return the dict index in the list
    """
    for index,item in enumerate(listOfDict):
        if key in item:
            if item[key] == value:
                return index
    
def execSubprocess(args, cwd=None, stdout=False):
    """
    Enter the OS command.
    
    args = ['chmod', '777', fileName]
    """
    result = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result,err = result.communicate()

    if stdout:
        print(f'keystackUtilities.execSubprocess: {" ".join(args)}')
        
    for line in result.decode('utf-8').split('\n'):
        if line:
            if type(line) is bytes:
                line = line.decode('utf-8')
            
            if stdout:
                print('keystackUtilities.execSubprocess: ', line)
             
    if err:
        return False, err.decode('utf-8')
    else:
        return True, result.decode('utf-8')

def execSubprocess2(command, shell=True, cwd=None, showStdout=False):
    """
    Enter the OS command. Returns nothing.  Displays immediately.
    
    shell: <bool>: subprocess shell
    cwd: <str|None>: The path to CD into prior to entering the subprocess command
    showStdout: <bool>: Display command on stdout
    """
    if showStdout:
        print(f'-> {command}')
        
    process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)

    while True:
        #process.poll()
        output = process.stdout.readline()
                
        if output:
            print(output.decode('utf-8'), end='')

        if process.poll() is not None:
            break
    
def execSubprocessInShellMode(command, cwd=None, showStdout=False):
    """
    Enter the OS command. Returns stdout.
    
    command: <string>
    """

    if showStdout:
        print(f'\n-> {command}')

    process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)    
    result,err = process.communicate()

    if showStdout:
        for line in result.decode('utf-8').split('\n'):
            if line:
                if type(line) is bytes:
                    line = line.decode('utf-8')

                print('keystackUtilities.execSubprocessInShellMode -> ', line)

    return True, result.decode('utf-8')

    
def readJson(jsonFile, threadLock=None, retry=5):
    """
    Read JSON data

    :returns: JSON data
    """
    if isFileExists(jsonFile, raiseException=True):
        if threadLock:
            threadLock.acquire()

        counter = 1
        while True:
            try:
                with open(jsonFile, mode='r', encoding='utf8') as jsonData:
                    jsonData = json.load(jsonData)
                
                break
            except Exception as errMsg:
                if counter == retry:
                    print(f'\keystackUtilities: readJson failed on file: {jsonFile}:\nError: {errMsg}')
                    raise Exception(errMsg)
                    break
                else:
                    counter += 1
                    time.sleep(1)
                    
        if threadLock:
            threadLock.release()

        return jsonData
            
def writeToJson(jsonFile, data, mode='w+', sortKeys=False, indent=4, threadLock=None, retry=5):
    """
    Write data to JSON file. Use file lock to avoid collisions if test is 
    multithreaded.
    
    :param jsonFile: <str>: The .json file to write to.
    :param data: <dict>: The json data.
    :param mode: <str>: w|w+ append to the file
    :param backoff: <int>: Number of times to retry.  Sometimes if multiple instances tries to access
                           the same file might clash.
    """
    if threadLock:
        threadLock.acquire()

    counter = 1
    while True:
        try:
            if mode == 'w+' and os.path.exists(jsonFile) is False:
                break
            
            with open(jsonFile, mode=mode, encoding='utf-8') as fileObj:
                json.dump(data, fileObj, indent=indent, sort_keys=sortKeys)
            
            break
        
        except Exception as errMsg:
            if counter == retry:
                print(f'\nwriteToJson failed: {jsonFile}: {errMsg}')
                raise(errMsg)
            else:
                print(f'\nwriteToJson failed/clashed: {errMsg}: {jsonFile}: retry {counter}/{retry}')
                counter += 1
                time.sleep(1)
                             
    if threadLock:
        threadLock.release()

def readYaml(yamlFile, threadLock=None, retry=5):
    """
    Read YAML data

    :returns: YAML data
    """
    if isFileExists(yamlFile, raiseException=True):
        if threadLock:
            threadLock.acquire()
         
        counter = 1
        while True:
            try:
                with open(yamlFile, mode='r', encoding='utf8') as yamlData:
                    try:
                        # For yaml version >5.1
                        yamlData = yaml.load(yamlData, Loader=yaml.FullLoader)
                    except yaml.YAMLError as exception:
                        # Show the Yaml syntax error
                        raise exception
                    except:
                        yamlData = yaml.safe_load(yamlData)   
                break
            except Exception as errMsg:
                if counter == retry:
                    #print(f'keystackUtilities: readYaml error: {errMsg}')
                    raise(errMsg)
                else:
                    counter += 1
                    time.sleep(1)
                    
        if threadLock:
            threadLock.release()
    
        return yamlData
    
def writeToYamlFile(contents, yamlFile, mode='w', threadLock=None, retry=5):
    """ 
    mode: w | w+
    """
    if threadLock:
        threadLock.acquire()
        
    counter = 1
    while True:
        try: 
            with open(yamlFile, mode) as fileObj:           
                yaml.dump(contents, fileObj, default_flow_style=False, indent=4)
                
            break
        except Exception as errMsg:
            if counter == retry:
                print(f'keystackUtilities.writetoYamlFile failed: {errMsg}')
                raise Exception(errMsg)
            else:
                counter += 1
                time.sleep(1)
                
    if threadLock:
        threadLock.release()
                                        
def readFile (filename, threadLock=None):
    if isFileExists(filename, raiseException=True):
        if threadLock:
            threadLock.acquire()
             
    counter = 1
    retry = 5
    
    while True:
        try:        
            with open(filename, 'r', encoding='utf-8') as fileObj:
                contents = fileObj.read()
            break
        except Exception as errMsg:
            if counter == retry:
                print(f'keystackUtilities.readFile failed: {errMsg}')
                raise Exception(errMsg)
            else:
                counter += 1
                time.sleep(1)
                
    if threadLock:
        threadLock.release()
            
    return contents
      
def writeToFile(filename, msg, mode='a+', threadLock=None, printToStdout=False):
    """
    Log message to file.

    :param mode: <str>: w = new, a+ = append to file.
    """

    if threadLock:
        threadLock.acquire()

    if printToStdout:
        print(f'{msg}\n')
    
    counter = 1
    retry = 5
    
    while True:
        try:    
            with open(filename, mode=mode, encoding='utf-8') as msgFile:
                msgFile.write(f'{msg}\n')
            break
        except Exception as errMsg:
            if counter == retry:
                print(f'keystackUtilities.writeToFile failed: {errMsg}')
                raise Exception(errMsg)
            else:
                counter += 1
                time.sleep(1)
                
    if threadLock:
        threadLock.release()

def writeToFileNoFileChecking(filename, msg, mode='a+', threadLock=None):
    """
    Log message to file.

    :param mode: <str>: a+ = append to file.
    """
    if threadLock:
        threadLock.acquire()
    
    with open(filename, mode=mode, encoding='utf-8') as msgFile:
        msgFile.write(f'{msg}\n')
    
    if threadLock:
        threadLock.release()
            
def makeFolder(targetPath, permission=0o774, stdout=False):
    if platform.system() == 'Windows':
        target = targetPath.replace('/', '\\\\')
    else:
        target = targetPath
    
    try: 
        # Might not be able to set the defined permissions
        # because the permission bits may be turned off by umask 000.
        # This os.umask(0) will clear the mask first so the mode takes full effect.
        # Then set it back afterwards.
        oldMask = os.umask(0)
        Path(target).mkdir(mode=permission, parents=True, exist_ok=True)
        os.umask(oldMask)
    except OSError:
        raise Exception(f'keystackUtilities.py.makeFolder(): Failed: {targetPath} {permission}')
    
    if stdout:
        print(f'keystackUtilities.py.makeFolder(): {targetPath} {permission}')
        
def mkdir(directory, user=None, permissionLevel='770', stdout=False):
    """
    Create a directory
    """
    if os.path.exists(directory) == False:
        result, stdout = execSubprocess(['sudo', '-u', user, 'mkdir', '-p', directory], stdout=stdout)
        if result == False:
            raise Exception(f'keystackUtilities.mkdir: Failed to create new directory: {directory}\n{stdout}You need to be root user.')

        if permissionLevel is not None:
            result, stdout = execSubprocess(['sudo', '-u', user, 'chmod', '-R', permissionLevel, directory], stdout=stdout)
            if result == False:
                raise Exception(f'keystackUtilities.mkdir: Failed to chmod {permissionLevel} on directory: {directory}.\nYou need to be root user')

    return True

def mkdir2(directory, stdout=False):
    """
    Create a directory
    """
    if os.path.exists(directory) == False:
        if stdout:
            print(f'\keystackUtilities.mkdir2: {directory}')
            
        result, stdout = execSubprocess(['mkdir', '-p', directory], stdout=stdout)
        if result == False:
            raise Exception(f'keystackUtilities.mkdir2: Failed to create new directory: {directory}\n{stdout}')

def createNewFile(filename, permissionLevel='770'):
    """
    Create a new blank file.
    
    :param filename: <str>: The path+file to create.
    """
    if isFileExists(os.path.dirname(filename)) == False:
        mkdir(os.path.dirname(filename))

    try:
        with open(filename, mode='w') as msgFile:
            msgFile.write('')

    except Exception as errMsg:
        raise Exception(f'utilikeystackUtilitieslities.createNewFile: Failed to create empty file: {filename}.')

    result, stdout = execSubprocess(['chmod', permissionLevel, filename])
    if result == False:
        raise Exception(f'keystackUtilities.createNewFile: Failed to chmod {permissionLevel} for file: {filename}.\n{stdout}')

def removeFile(pathFile):
    if os.path.exists(pathFile):
        result, stdout = execSubprocess(['rm', pathFile])
        if result == False:
            raise Exception(f'keystackUtilities.removeFile: Failed to remove file: {pathFile}\n{stdout}')
    else:
        raise Exception(f'keystackUtilities.removeFile: File does not exists: {pathFile}')
    
def removeFolder(path, stdout=False):
    if os.path.exists(path):
        result, stdout = execSubprocess(['rm', '-rf', path], stdout=stdout)
        if result == False:
            raise Exception(f'keystackUtilities.removeFolder: Failed to remove folder: {path}\n{stdout}')

def removeTree(path):
    try:
        if os.path.exists(path):
            rmtree(path)
    except Exception as errMsg:
        raise Exception(errMsg)
    
def renameFolder(path, newPath):
    result, stdout = execSubprocess(['mv', path, newPath])
    if result == False:
        raise Exception (f'keystackUtilities.renameFolder: Failed to rename folder: {path} -> {newPath}\n{stdout}')

    return True

def isFileExists(filename, raiseException=False):
    """
    Verify if file exists.

    :return: True|False if raiseException == False.
    :raise: Exception if raiseException == True.
    """
    if os.path.exists(filename) == False:
        if raiseException == True:
            raise Exception(f'keystackUtilities.isFileExists: No such file: {filename}')

        return False
        
    return True

def chownChmodFolder(topLevelFolder, user, userGroup, permission=770, stdout=False):
    try:
        execSubprocessInShellMode(f'sudo chown -R {user}:{userGroup} {topLevelFolder}', showStdout=stdout)
    except:
        execSubprocessInShellMode(f'chown -R {user}:{user} {topLevelFolder}', showStdout=stdout)
    
    try:
        execSubprocessInShellMode(f'sudo chmod -R {permission} {topLevelFolder}', showStdout=stdout) 
    except:
        execSubprocessInShellMode(f'chmod -R {permission} {topLevelFolder}', showStdout=stdout)
        
def getDeepDictKeys(dictObj, keys, default=None):
    """
    Convert dotted strings to a dictionary

    Example:
       datacenters:
          location: California
          rack1:
             server1: 1.1.1.1
             server2: 1.1.1.2

    resourcesToUse =  datacenters.location.rack1.server2
    getDeepDictKeys(masterInventoryDictObj, resourcesToUse))
    Returns: {'dataceters': {'locations': {'rack1': {'server2': '1.1.1.2'}}}}
    """
    from functools import reduce
    return reduce(lambda d, key: d.get(key, default) if isinstance(d, dict) else default, keys.split("."), dictObj)

def getDictIndexList(listOfDicts, key, deepSearch=False):
    """
    Get the index of a dict element in a list.
    This supports nested layer search. Examples are show below
    
    This function pairs with getIndexWithValue()
    
    x = []
    x.append({'apple':  {'env': 'hubert', 'result':'Passed'}})
    x.append({'orange': {'env': 'jadyn',  'result':'Failed'}})
    x.append({'banana': {'env': 'lily',   'result':'Aborted'}})
    x.append({'apple':  {'env': 'taylor', 'result':'Aborted'}})
    x.append({'orange': {'env': 'audra',  'result':'Aborted'}})

    Example 1:
       indexPropertyList = getDictIndexList(x, 'orange')
       index = getDictIndexFromList(indexPropertyList, 'env', 'audra')
    
       Returns:
          [{1: {'env': 'jadyn', 'result': 'Failed'}}
           {4: {'env': 'audra', 'result': 'Aborted'}}]

    Example 2:
       y = []
       y.append({'apple':  {'sf': {'env': 'hubert', 'result':'Passed'}}})
       y.append({'orange': {'sf': {'env': 'jadyn',  'result':'Failed'}}})
       y.append({'banana': {'sf': {'env': 'lily',   'result':'Aborted'}}})
       y.append({'apple':  {'lv': {'env': 'taylor', 'result':'Aborted'}}})
       y.append({'orange': {'sf': {'env': 'audra',  'result':'Aborted'}}})

       indexPropertyList1 = getDictIndexList(y, 'orange')
    
       # If the key is in deep multi-layers, use deepSearch until the last layer
       indexPropertyList2 = getDictIndexList(indexPropertyList1, 'sf', deepSearch=True)
       index = getDictIndexFromList(indexPropertyList2, 'env', 'audra')
    
       Returns
          The final index of the list of nested dict
    """
    listOfIndexes = []
    for index,element in enumerate(listOfDicts):
        for item, values in element.items():
            if deepSearch == False:
                if item == key:
                    listOfIndexes.append({index: values})

            if deepSearch:
                for property,value in values.items():
                    if property == key:
                        listOfIndexes.append({item: value})
                
    return listOfIndexes
                 
def getDictIndexFromList(listOfDicts, key, value, secondLayerDictSearch=True):
    """
    This is in conjunction with getIndex()

    This is the final execution layer search for the deep dict 
    key/value search.
    """
    for index, element in enumerate(listOfDicts):
        for k,v in element.items():          
            # {4: {'result': None, 'env': 'DOMAIN=Communal/Samples/demoEnv1', 'progress': '', 'currentlyRunning': None}}
            if secondLayerDictSearch is False:
                if key == k and value == v:
                    return index
                    #return k
            else:
                for property, values2 in v.items():
                    if property == key and values2 == value:
                        return index
                        #return k
                                
def convertStringToDict(dottedString, value):
    """
    Convert dotted string into a dict with value.

    Example:
      From this: datacenters.location.rack1.server2
      To this: {'dataceters': {'locations': {'rack1': {'server2': '1.1.1.2'}}}}
    """
    dottedStringToList = dottedString.split('.')
    newDict = current = {}
    for name in dottedStringToList:
        if name == dottedStringToList[-1]:
            current[name] = value
        else:
            current[name] = {}
            current = current[name]

    return newDict

def convertDotStringKeysToDict(dictString):
    """
    Verify if key or nested key exists in the dictObj.
    Returns the value if key exists.
    Returns None if key does not exists.

    dictString: '{"obj1": {"obj2": 2}}'
    """
    import json
    return json.loads(dictString)

def updateDict(mainDictObj, dictUpdates):
    """
    Return a new dictionary by merging two dictionaries recursively
    """
    import collections.abc
    from copy import deepcopy

    result = deepcopy(mainDictObj)

    for key, value in dictUpdates.items():
        if isinstance(value, collections.abc.Mapping):
            result[key] = updateDict(result.get(key, {}), value)
        else:
            result[key] = deepcopy(dictUpdates[key])

    return result
    
def replaceDictKeyCharacter(data, replacing='.', replaceWith='\u2024'):
    """
    MongoDB does not accept keys with a period.
    This function iterates a nested dict and replace all periods with unicode. 
    Making this function able to replace any character with anything.
    """
    newDict = {}
    for key,value in data.items():
        if isinstance(value, dict):
            value = replaceDictKeyCharacter(value)
        #newDict[key.replace('.', '\u2024')] = value
        newDict[key.replace(replacing, replaceWith)] = value

    return newDict

def updateLogFolder(logFolderSearchPath, removeAfterDays=5):
    """
    Update the logs folder by removing pass logs up the $removeAfterDays.
    Back up daily log files with _<timestamp>.
    
    Parameters:
       logFolderSearchPath <str>: The log folder path
       removeAfterDays <int>: The amount of days to keep past logs
        
       0 = removes all result folders starting from today
       1 = removes all result folders starting from yesterday
       never = Don't remove any
       Example=2 = Keep just the last 2 days of results and remove the rest
       
    Usage:
        logFolder = '/path/jiraServiceLogs*'    
        updateLogFolder(logFolderSearchPath=logFolder, removeAfterDays=5)
    """
    for eachLogFile in glob(logFolderSearchPath):
        currentPath = eachLogFile.split('/')[0]
        fileName = eachLogFile.split('/')[-1]
        today = datetime.datetime.now()
        
        # Get the created date/time of the log file.
        # 1651517698.3243287
        unixTimestamp = os.path.getmtime(eachLogFile)
        uniqueNumber = str(unixTimestamp).split('.')[0]
        
        # 2022-05-02 11:54:58
        unixTimestamp = datetime.datetime.fromtimestamp(int(unixTimestamp))
        
        # 05-02-22
        format = '%m-%d-%y'
        humanReadableDate = unixTimestamp.strftime(format)
        datetimeObj = datetime.datetime.strptime(humanReadableDate, format)
        daysDelta = today.date() - unixTimestamp.date()
        # 0=today, 1=yesterday
        daysRecorded = daysDelta.days

        # First, remove all unwanted past logs
        if removeAfterDays != 'never':
            if int(daysRecorded) >= int(removeAfterDays):
                try:
                    print(f'utilities: updateLogFolder: Log file set to be removed after {removeAfterDays} days. Removing {eachLogFile}.')
                    os.remove(eachLogFile)
                    continue
                except Exception as errMsg:
                    raise(f'updateLogFolder: {eachLogFile}\n{errMsg}')

        if '_' in eachLogFile:
            # Ignore backed up logs with '_<timestamp>' and any log files with _<timestam>: jiraServiceLogs_1654204608
            continue
         
        # If current log file was yesterday or beyond yesterday, append a timestamp on it
        if int(daysRecorded) > 0:
            logFolderPath = '/'.join(logFolderSearchPath.split('/')[:-1])
            copyfile(eachLogFile, f'{logFolderPath}/{fileName}_{uniqueNumber}')
            os.remove(f'{logFolderPath}/{fileName}')
        
def saveFileToBackupFile(fullPathFile, sudo=False, user=None, userGroup=None):
    """ 
    Back up a file with a unique timestamp appended to the file name
    """
    if os.path.exists(fullPathFile):
        path = '/'.join(fullPathFile.split('/')[:-1])
        fileName = fullPathFile.split('/')[-1]
        
        # 1651517698.3243287
        unixTimestamp = os.path.getmtime(fullPathFile)
        uniqueNumber = str(unixTimestamp).split('.')[0]
        backupSystemSettingsFile = f'{path}/{fileName}_{uniqueNumber}'
        
        # If current log file was yesterday or beyond yesterday, append a timestamp on it
        if sudo:
            execSubprocessInShellMode(f'sudo mv {fullPathFile} {backupSystemSettingsFile}')
        else:
            execSubprocessInShellMode(f'mv {fullPathFile} {backupSystemSettingsFile}')
            
        # TODO: chown and chmod
        return backupSystemSettingsFile
    
def sendEmail(emailTo, fromSender, subject, bodyMessage, emailAttachmentList=None):
    """
    postfix must be installed and the service must be running for emailing.
    Email generally does not work behind home internet because carriers blocks
    smtp protocol.
    """ 
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase # zip file attachment
    from email import encoders # zip file attachment
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
                
    # plain | html
    body = MIMEText(bodyMessage, 'plain')
    msg = MIMEMultipart("alternative")
    msg["From"] = fromSender
    msg["To"] = emailTo
    msg["Subject"] = subject    
    msg.attach(body)

    # fileAttachment is passed in as a list
    if emailAttachmentList:
        print(f'\nutilities:sendEmail() {emailAttachmentList}')
        for eachAttachment in emailAttachmentList:
            if eachAttachment is None:
                continue
            
            if '/' in eachAttachment:
                filename = eachAttachment.split('/')[-1]
            else:
                filename = eachAttachment
                
            if 'zip' in filename:
                # Note: Destination email server may not accept large zip file size such as 1MB
                attachment = MIMEBase("application", "zip")
                attachment.set_payload(open(eachAttachment, "rb").read())
                
                encoders.encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment', filename=f'{filename}.zip')
            else:
                attachment = MIMEApplication(open(eachAttachment, 'rb').read())
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)

            msg.attach(attachment)
            
    try:
        # Linux machine must have postgres installed and started
        p = subprocess.Popen(["sendmail", "-t"], stdin=subprocess.PIPE, universal_newlines=True)
        p.communicate(msg.as_string())
    except Exception as errMsg:
        print(f'\nkeystackCommonLib.py:sendEmail() error: {errMsg}')

def convertStrToBoolean(word):
    if word in [True, 'True', 'true', 'Yes', 'yes', 'y', 'Y', "1"]:
        return True
    
    if word in [False, 'False', 'false', 'No', 'no', 'n', 'N', "0"]:
        return False    

def convertNoneStringToNoneType(word):
    """
    yaml doesn't serialize None type. Yaml uses null as None type.
    In case a user uses "None" or "none", then return None
    Otherwise, return the original word
    """
    if word in ['None', 'none', 'null']:
        return None
    else:
        return word
    
def removeDockerImage(version, sudo=False):
    """
    Search for docker image tag. If a tag matches the keystack version,
    remove the docker image.
    """
    if sudo:
        output = execSubprocessInShellMode('sudo docker images')[1]
    else:
        output = execSubprocessInShellMode('docker images')[1]
        
    for line in output.split('\n'):
        # keystack     0.6.1o    ef935352af4d   2 hours ago   2.3GB
        match = re.search('.*keystack([^ ]+)? +([^ ]+) +([^ ]+)', line)
        if match:
            dockerTag = match.group(2)
            dockerId = match.group(3)
            if version == dockerTag:
                print(f'\nRemoving Docker image: keystack:{dockerTag} {dockerId}')
                if sudo:
                    execSubprocess2(f'sudo docker rmi -f {dockerId}')
                else:
                    execSubprocess2(f'docker rmi -f {dockerId}')
                    
def stopDockerContainer(containerName='keystack', removeContainer=True, sudo=False):
    """ 
    Check current Docker container for running Keystack. 
    Stop the Keystack container if it is running.
    If the Keystack version is the same version as the one installing,
    remove the image from docker.
    """
    tag = None
    containerIds = []
    
    print(f'\nstopDockerContainer: {containerName}')
    if sudo:
        process = subprocess.Popen('sudo docker container ps -a', stdout=subprocess.PIPE, shell=True)
    else:
        process = subprocess.Popen('docker container ps -a', stdout=subprocess.PIPE, shell=True)
    
    while True:
        process.poll()
        line = process.stdout.readline()
        if line:
            print(line.decode('utf-8'), end='')
            line = line.decode('utf-8')
            # fbfc9753002e   keystack:0.6.1o
            match = re.search(f'(^[^ ]+).*{containerName}(:[^ ]+)? +.*', line)
            if match:
                containerProcessId = match.group(1)
                tag = match.group(2)
                containerIds.append(containerProcessId)
                        
        if line == b'':
            break

    for containerId in containerIds:
        print(f'\nStopping Docker Container: {containerId} {tag}')
        if sudo:
            execSubprocess2(command=f'sudo docker container stop {containerId}')
        else:
            execSubprocess2(command=f'docker container stop {containerId}')
            
        if removeContainer:
            # Must remove the current same Keystack Docker container and image because
            # images could not be overwritten.
            if sudo:
                execSubprocess2(command=f'sudo docker container rm {containerId}')
            else:
                execSubprocess2(command=f'docker container rm {containerId}')        
        
def verifyContainer(containerName='keystack', sudo=False):
    """ 
    Check current Docker container for running Keystack. 
    Stop the Keystack container if it is running.
    If the Keystack version is the same version as the one installing,
    remove the image from docker.
    """
    if sudo:
        process = subprocess.Popen('sudo docker container ps -a', stdout=subprocess.PIPE, shell=True)
    else:
        process = subprocess.Popen('docker container ps -a', stdout=subprocess.PIPE, shell=True)
    
    while True:
        process.poll()
        line = process.stdout.readline()
        if line:
            print(line.decode('utf-8'), end='')
            line = line.decode('utf-8')
            # d07e52465893   username/keystack:0.12.0   "/opt/Keystack/start…"   10 hours ago   Up 10 hours 
            match = re.search(f'.*{containerName}.*Up.*', line)
            if match:
                print(f'\nverifyContainer: Container {containerName} is up.')
                return True
                        
        if line == b'':
            break
    
    print(f'\nverifyContainer: Container {containerName} is down.')    
    return False

def verifyContainers(containers):
    areUp = True
    for container in containers:
        if verifyContainer(container) == False:
            print(f'\nverifyContainers: {container} is down')
            areUp = False
        else:
            print(f'\nverifyContainer: {container} is up')
    
    return areUp 

def getRunningContainerTagVersion(containerName='keystack', sudo=False):
    """ 
    Check current Docker container for running Keystack. 
    Stop the Keystack container if it is running.
    If the Keystack version is the same version as the one installing,
    remove the image from docker.
    """
    if sudo:
        process = subprocess.Popen('sudo docker container ps -a', stdout=subprocess.PIPE, shell=True)
    else:
        process = subprocess.Popen('docker container ps -a', stdout=subprocess.PIPE, shell=True)
    
    allRunningKeystackContainers = []
    
    while True:
        process.poll()
        line = process.stdout.readline()
        if line:
            print(line.decode('utf-8'), end='')
            line = line.decode('utf-8')
            # d07e52465893   username/keystack:0.12.0   "/opt/Keystack/start…"   10 hours ago   Up 10 hours 
            match = re.search(f'.*{containerName}:([^ ]+).*Up.*', line)
            if match:
                allRunningKeystackContainers.append(match.group(1))
                        
        if line == b'':
            break
       
    return allRunningKeystackContainers

def getDockerNetworkServiceIpAddress(containerName):
    """
    Get the Docker container service IP address from the host server
                                                                                       
    docker network ls                                                                                                                  
    docker inspect e988c49120c7 (keystacksetup_0200_keystack-net)

    Usage:
       getDockerNetworkServiceIpAddress(containerName='mongo')  
    
        docker network ls
        NETWORK ID     NAME                                   DRIVER    SCOPE
        3e2d626719fd   bridge                                 bridge    local
        4cc51b77966f   host                                   host      local
        baf6324f9ee1   keystacksetup_04010_keystack-net       bridge    local
        127213f92e2b   keystacksetup_04020_keystack-net       bridge    local
        1fc078aab50d   keystacksetup_04030_keystack-net       bridge    local
        62b348f437e1   keystacksetup_04040_keystack-net       bridge    local
        f75d7a3499a1   keystacksetup_040040300_keystack-net   bridge    local
        f8486cc7fcdf   none                                   null      local                                             
    """
    from commonLib import showVersion
    keystackVersion, dockerContainerVersion = showVersion(stdout=False)
    keystackVersion = keystackVersion.replace('.', '')
    mongoIp = None
    keystackNetworkId = None
    
    result, output = execSubprocessInShellMode('docker network ls', showStdout=False)
    for line in output.split('\n'):
        # keystacksetup_0200_keystack-net                                                                                          
        regexMatch = re.search(f'(.+) +keystacksetup_{keystackVersion}_keystack-net', line)
        if regexMatch:
            keystackNetworkId = regexMatch.group(1)

    if keystackNetworkId:
        result, output = execSubprocessInShellMode(f'docker inspect {keystackNetworkId}', showStdout=False)
        # Convert str to dict                                                                                                          
        newOutput = json.loads(output)[0]
        for containerIdKey, value in newOutput['Containers'].items():
            if value['Name'] == containerName:
                mongoIp = value['IPv4Address'].split('/')[0]
                break

    return mongoIp

                                                   
class LockFile:
    """
    https://stackoverflow.com/questions/50485037/loading-json-from-a-locked-file

    Lock and open a file.
    If the file is opened for writing, an exclusive lock is used,
    otherwise it is a shared lock

    You want to lock the file before truncating it. You can also open the file in 'r+' mode 
    (reading and writing), at which point you need to manually truncate it after locking.

    You also will need to lock the file for reading, because you don't want your readers to 
    end up with truncated data when they try to read while another process is busy replacing 
    the contents. Use a shared lock, at which point other processes are allowed to obtain a 
    shared lock too, making it possible for many processes to read the data without having to 
    wait for one another. A process that wants to write has to grab an exclusive lock, which 
    is only going to be awarded when there are no shared locks anymore.

    This class is a context manager that handles the locking (either in exclusive mode for 
    writing, or in shared mode for reading), and only truncate the file after obtaining the 
    lock. You'll also need to account for the file not yet existing, and if you don't want to 
    wait for locks forever, you need to handle timeouts (meaning you need to use LOCK_NB in a 
    loop and test for the return value to see if the lock was acquired, until a certain amount 
    of time has passed).

    Using the os.open() low-level system call to ensure the file is created when trying to lock 
    it for exclusive access without truncating it if it already exists:

    The processes that try to read the file then use:
    with LockFile('test.json', 'r') as file:
        data = json.load(file)

    and the process that wants to write uses:
    with LockFile('test.json', 'w') as file:
        json.dump(data, file)

    If you want to allow for a timeout, add a try/except block around the with block
    and catch the Timeout exception; you'll need to decide what should happen then:
    try:
        with LockFile('test.json', 'w', timeout=10) as file:
            json.dump(data, file)
    except Timeout:
        # could not acquire an exclusive lock to write the file. What now
    """
    def __init__(self, path, mode, timeout=5, **fileopts):
        self.path = path
        self.mode = mode
        self.fileopts = fileopts
        self.timeout = timeout
        # lock in exclusive mode when writing or appending (including r+)
        self._exclusive = set('wa+').intersection(mode)
        self._lockfh = None
        self._file = None

    def _acquire(self):
        if self._exclusive:
            # open the file in write & create mode, but *without the 
            # truncate flag* to make sure it is created only if it 
            # doesn't exist yet
            lockfhmode, lockmode = os.O_WRONLY | os.O_CREAT, fcntl.LOCK_EX
        else:
            lockfhmode, lockmode = os.O_RDONLY, fcntl.LOCK_SH

        self._lockfh = os.open(self.path, lockfhmode)
        start = time.time()

        while True:
            try:
                fcntl.lockf(self._lockfh, lockmode | fcntl.LOCK_NB)
                return
            except OSError as e:
                if e.errno not in {errno.EACCES, errno.EAGAIN}:
                    raise

            if self.timeout is not None and time.time() - start > self.timeout:
                #raise LockFileTimeout()
                self._release()

            time.sleep(0.1)

    def _release(self):
        fcntl.lockf(self._lockfh, fcntl.LOCK_UN)
        os.close(self._lockfh)

    def __enter__(self):
        if self._file is not None:
            #raise Exception('Lock already taken')
            self._release()

        self._acquire()
        self._file = open(self.path, self.mode, **self.fileopts)
        return self._file

    def __exit__(self, *exc):
        if self._file is None:
            raise Exception('Not locked')
        
        self._file.close()
        self._file = None
        self._release()




