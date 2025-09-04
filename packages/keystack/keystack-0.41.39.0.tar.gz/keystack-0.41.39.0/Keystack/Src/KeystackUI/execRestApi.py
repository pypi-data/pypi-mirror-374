import os, sys, time, json, traceback, httpx
from copy import deepcopy

# /Keystack/KeystackUI/restApi
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir)
try:
    from systemLogging import SystemLogsAssistant
except:
    # This file is also used in setupKeystack.py without systemLogging
    pass

from keystackUtilities import getTimestamp, writeToFile

from rest_framework.response import Response
from django.http import JsonResponse

class ExecRestApi(object):
    def __init__(self, ip, port=None, headers=None, verifySslCert=False,
                 https=False, keystackLogger:object=None):   
        """ 
        restObj = ExecRestApi(ip, port, headers, https=True)
        restObj.get(restApi)
        """ 
        self.keystackLogger = keystackLogger
   
        from requests.exceptions import ConnectionError
        
        if headers:
            self.headers = headers
        else:
            self.headers = {"content-type": "application/json"}
            
        self.verifySslCert = verifySslCert
        
        if https:
            if port is None:
                self.httpBase = f'https://{ip}'
            elif port == str(443):
                self.httpBase = f'https://{ip}'
            else:
                self.httpBase = f'https://{ip}:{port}'
        else:
            if port is None:
                self.httpBase = f'http://{ip}'
            else:
                self.httpBase = f'http://{ip}:{port}'

    def logAndPrint(self, msg):
        print(msg)
        # if self.sessionRestLogFile:
        #     writeToFile(self.sessionRestLogFile, msg=msg, mode='a+')
        if self.keystackLogger: self.keystackLogger.info(msg)
                                 
    def get(self, restApi, params={}, stream=False, showApiOnly=False, silentMode=False, ignoreError=False, timeout=10, maxRetries=10,
            user=None, webPage=None, action=None):
        """
        Description
            A HTTP GET function to send REST APIs.

        Parameters
           restApi: (str): The REST API URL.
           data: (dict): The data payload for the URL.
           silentMode: (bool):  To display on stdout: URL, data and header info.
           ignoreError: (bool): True: Don't raise an exception.  False: The response will be returned.
           maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failure.
        """
        retryInterval = 3
        restExecutionFailures = 0
        restApi = f'{self.httpBase}{restApi}'
        response = None
        
        headersWithoutAccessKey = deepcopy(self.headers)
        if 'Access-Key' in headersWithoutAccessKey:
            del headersWithoutAccessKey['Access-Key']
        if 'Authorization' in headersWithoutAccessKey:
            del headersWithoutAccessKey['Authorization']
        
        silentMode = False
                    
        while True:
            if silentMode is False:
                showRestCall = f'\nGET: {restApi}'
                if showApiOnly is False:
                    showRestCall += f'\nDATA: {params}'
                    showRestCall += f'\nHEAHDERS: {self.headers}\n'
                showRestCall = showRestCall.replace(", 'webhook': True", '')
                if self.keystackLogger:  self.keystackLogger.info(showRestCall)
                print(showRestCall)
                
            try:
                # For binary file
                if stream:
                    response = httpx.stream('GET', restApi, headers=self.headers, timeout=timeout,
                                            follow_redirects=True, verify=self.verifySslCert)
                    
                if stream == False:
                    try:
                        response = httpx.get(restApi, params=params, headers=self.headers, timeout=timeout,
                                             follow_redirects=True, verify=self.verifySslCert)
                    except Exception as errMsg:
                        errorMsg = f'GET Error: {str(errMsg)}'
                        if self.keystackLogger: self.keystackLogger.error(errorMsg)
                        print(errorMsg)
                        return response
                    
                if self.headers.get('Authorization', None):
                    del self.headers['Authorization']
                message = f'GET: {restApi}<br>HEADERS: {headersWithoutAccessKey}<br>STATUS_CODE: {response.status_code}'

                if silentMode is False:
                    for redirectStatus in response.history:
                        if '307' in str(response.history):
                            if self.keystackLogger: self.keystackLogger.info(f'\t{redirectStatus}: {response.url}')

                    statusCode = f'STATUS CODE: {response.status_code}\n'
                    if self.keystackLogger:
                        self.keystackLogger.info(statusCode)
                    print(statusCode)

                if response.status_code == 500:
                    if self.keystackLogger:
                        self.keystackLogger.error(f'Server unreachable. Status code 500.')
                    return response
                    
                if str(response.status_code).startswith('4'):
                    if restExecutionFailures < maxRetries:
                        getError = f'GET error: Retrying: {restExecutionFailures}/{maxRetries}'
                        if self.keystackLogger:
                            self.keystackLogger.warning(getError)
                            
                        restExecutionFailures += 1
                        time.sleep(retryInterval)
                        continue
                    else:
                        SystemLogsAssistant().log(user=user, webPage=webPage, action=action, msgType='Error', 
                                                  msg=response.status_code, forDetailLogs='')
                        return response
                
                if not str(response.status_code).startswith('2'):
                    msgType = 'Error'
                    if ignoreError == False:
                        if 'message' in response.json() and response.json()['messsage'] != None:
                            errorMsg = f"\nGET Error: {response.json()['message']}"
                            if self.keystackLogger: self.keystackLogger.error(errorMsg)
                            print(errorMsg)
                else:
                    msgType = 'Info'
                
                if webPage:    
                    SystemLogsAssistant().log(user=user, webPage=webPage, action=action, msgType=msgType, msg=message, forDetailLogs='')

                return response

            except (httpx.ConnectTimeout, httpx.ReadTimeout, Exception) as errMsg:
                if restExecutionFailures < maxRetries:
                    getError = f'GET error: Retrying: {restExecutionFailures}/{maxRetries}'
                    if self.keystackLogger:
                        self.keystackLogger.warning(getError)
                        
                    print(getError)
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue
                
                if restExecutionFailures == maxRetries:
                    return response
                    
          
    def post(self, restApi, params={}, headers=None, silentMode=False, showApiOnly=False, ignoreError=False, 
             timeout=10, maxRetries=10, user=None, webPage=None, action=None):
        """
        Description
           A HTTP POST function to create and start operations.

        Parameters
           restApi: (str): The REST API URL.
           data: (dict): The data payload for the URL.
           headers: (str): The special header to use for the URL.
           silentMode: (bool):  To display on stdout: URL, data and header info.
           ignoreError: (bool): True: Don't raise an exception.  False: The response will be returned.
           maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failure.
        """
        import json
                
        restApi = f'{self.httpBase}{restApi}'
        resonse = None
        
        if headers != None:
            originalJsonHeader = self.headers
            self.headers = headers
            
        headersWithoutAccessKey = deepcopy(self.headers)
        if 'Access-Key' in headersWithoutAccessKey:
            del headersWithoutAccessKey['Access-Key']
        if 'Authorization' in headersWithoutAccessKey:
            del headersWithoutAccessKey['Authorization']
         
        retryInterval = 1
        restExecutionFailures = 0
        
        # Hardcode enabling showing REST APIs for debugging
        #silentMode = False 
        
        while True:
            response = None
            
            if silentMode == False:
                params2 = deepcopy(params)
                if 'webhook' in params2:
                    del params2['webhook']
                    
                showRestCall = f'\nPOST: {restApi}'
                if showApiOnly is False:
                    showRestCall += f'\nDATA: {params}'
                    showRestCall += f'\nHEAHDERS: {self.headers}\n'
                showRestCall = showRestCall.replace(", 'webhook': True", '')
                if self.keystackLogger:
                    self.keystackLogger.info(showRestCall)
                    
                print(showRestCall)

            try:
                response = httpx.post(restApi, json=params, headers=self.headers, 
                                      timeout=timeout, follow_redirects=True,
                                      verify=self.verifySslCert)

                if self.headers.get('Authorization', None):
                    del self.headers['Authorization']
                    
                message = f'POST: {restApi}<br>HEADERS: {headersWithoutAccessKey}<br>STATUS_CODE: {response.status_code}'
   
                # 200 or 201
                if silentMode == False:
                    for redirectStatus in response.history:
                        if '307' in str(response.history):
                            if self.keystackLogger: self.keystackLogger.info(f'\t{redirectStatus}: {response.url}')
                            print(f'\t{redirectStatus}: {response.url}')
                            
                    if self.keystackLogger: self.keystackLogger.info(f'STATUS CODE: {response.status_code}')
                    print(f'STATUS CODE: {response.status_code}\n')
                    
                if response:
                    if response.status_code == 500:
                        if self.keystackLogger:
                            self.keystackLogger.error(f'Server unreachable. Status code 500.')
                        return response
                    
                    if str(response.status_code).startswith('4'):
                        msgType = 'Error'
                        if ignoreError == False:
                            if restExecutionFailures < maxRetries:
                                restExecutionFailures += 1
                                if self.keystackLogger:
                                    self.keystackLogger.warning(f'POST warning: Retrying {restExecutionFailures}/{maxRetries}\n')
                                    
                                #print(f'POST status {response.status_code} warning: Retrying {restExecutionFailures}/{maxRetries}')
                                time.sleep(retryInterval)
                                continue
                            else:
                                if 'errors' in response.json():
                                    errMsg = f'POST error: {response.json()["errors"]}\n'
                                    if self.keystackLogger:
                                        self.keystackLogger.error(errMsg)
                                        
                                    print(errMsg)

                                if self.keystackLogger:
                                    self.keystackLogger.error(f'POST error: Retried {restExecutionFailures}/{maxRetries}')
                                    
                                #print(f'POST error: {response.text}\n')
                    else:
                        msgType = 'Info'
                else:
                    raise Exception(f'Rest API got no response from the server: {restApi}')
                
                if webPage:    
                    #SystemLogsAssistant().log(user=user, webPage=webPage, action=action, msgType=msgType, msg=message, forDetailLogs='')
                    pass
                
                # Change it back to the original json header
                if headers != None:
                    self.headers = originalJsonHeader

                return response

            except (httpx.ConnectTimeout, httpx.ReadTimeout, Exception) as errMsg:
                #errorMsg = f'\nexecRestApi POST ERROR: RestAPI:{restApi}\n\n{traceback.format_exc(None, errMsg)}\n'
                #self.keystackLoggerAndPrint(errorMsg)
                
                if restExecutionFailures < maxRetries:
                    if ignoreError == False:
                        if self.keystackLogger:
                            self.keystackLogger.warning(errMsg)
                        #print(errMsg)
                        
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue
                
                if restExecutionFailures == maxRetries:
                    return response
    
    def delete(self, restApi, params={}, headers=None, maxRetries=5, user=None, webPage=None, action=None):
        """
        Description
            HTTP DELETE 

        Paramters
            restApi: (str): The REST API URL.
            data: (dict): The data payload for the URL.
            headers: (str): The headers to use for the URL.
            maxRetries: <int>: The maximum amount of GET retries before declaring as server connection failure.
        """
        restApi = f'{self.httpBase}{restApi}'
            
        if headers != None:
            originalJsonHeader = self.headers
            self.headers = headers
        
        headersWithoutAccessKey = deepcopy(self.headers)
        if 'Access-Key' in headersWithoutAccessKey:
            del headersWithoutAccessKey['Access-Key']
        if 'Authorization' in headersWithoutAccessKey:
            del headersWithoutAccessKey['Authorization']
            
        retryInterval = 3
        restExecutionFailures = 0
        
        while True:
            showRestCall = f'\nDELETE: {restApi}\n'
            showRestCall += f'DATA: {params}\n'
            showRestCall += f'HEAHDERS: {self.headers}\n'
            showRestCall = showRestCall.replace(", 'webhook': True", '')
            self.keystackLogger.info(showRestCall)
            print(showRestCall)

            try:
                response = httpx.delete(restApi, params=params, headers=self.headers, 
                                        follow_redirects=True, verify=self.verifySslCert)

                if self.headers.get('Authorization', None):
                    del self.headers['Authorization'] 
                               
                message = f'DELETE: {restApi}<br>HEADERS: {headersWithoutAccessKey}<br>STATUS_CODE: {response.status_code}'
                
                for redirectStatus in response.history:
                    if '307' in str(response.history):
                        if self.keystackLogger: self.keystackLogger.info(f'redirectStatus: {response.url}')

                self.keystackLogger.info(f'STATUS CODE: {response.status_code}')
                
                if not str(response.status_code).startswith('2'):
                    msgType = 'Error'
                    errMsg = f'DELETE Exception error: {response.text}\n'
                    if self.keystackLogger: self.keystackLogger.info(errMsg)
                    return response
                else:
                    msgType = 'Info'
                        
                if webPage:    
                    SystemLogsAssistant().log(user=user, webPage=webPage, action=action, msgType=msgType, msg=message, forDetailLogs='')
                        
                # Change it back to the original json header
                if headers != None:
                    self.headers = originalJsonHeader
                                    
                return response

            #except (requests.exceptions.RequestException, Exception) as errMsg:
            except (httpx.ConnectTimeout, httpx.ReadTimeout, Exception) as errMsg:
                errMsg = f'DELETE Exception error {restExecutionFailures}/{maxRetries} retries: {errMsg}\n'

                if restExecutionFailures < maxRetries:
                    self.keystackLogger.info(errMsg)
                    restExecutionFailures += 1
                    time.sleep(retryInterval)
                    continue
                
                if restExecutionFailures == maxRetries:
                    return response
            
