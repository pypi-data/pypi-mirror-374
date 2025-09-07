import os, sys, subprocess, json
from glob import glob

# /Keystack/KeystackUI/sidebar/sessionMgmt
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir.replace('/KeystackUI/sidebar/playbook', ''))

#from utilities import convertDotStringKeysToDict, getDeepDictKeys, readYaml
from utilities import readYaml
from db import DB
from sidebar.sessionMgmt.views import SessionMgmt
from django.conf import settings
#from .views import Playbook

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
    
from rest_framework.parsers import JSONParser
from rest_framework import status

from pprint import pprint
import requests


class Playbook(APIView):
    def get(self, request):
        """
        Get a list of playbooks
        
        GET /api/playbook
        """     
        try:
            playbookList = []
            playbookObj = DB.name.getDocuments(collectionName='playbooks', fields={})
            for eachPlaybook in playbookObj:
                playbookList.append(eachPlaybook['_id'])
            
            statusCode = 200
            message = playbookList
        except Exception as errMsg:
            statusCode = 404
            message = 'Failed to get playbooks'
               
        return Response(data={'playbooks': message}, status=200)
 
    @csrf_exempt
    def post(self, request, playbook=None):
        """
        Run a playbook
        
        POST: /api/playbook
        FORM-DATA: {'name': <playbook>, 'user': <user>}
        
        Examples:
            curl -d "playbook=goody&user=Hubert" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://172.16.1.16:8000/api/playbook 
            curl -d '{"user":"hubert", "playbook": "goody"}' -H "Content-Type: application/json" -X POST http://172.16.1.16:8000/api/playbook
        
        Use form-data. Don't use RAW because it requires csrf token. A hassle to insert it.
        Must do a GET to get it and then insert it as a RAW with Content-Type: application/JSON
        """
        data = request.data
        
        try:
            playbook = request.data['playbook']
        except:
            return Response(data={'message': 'Must include a playbook name'}, status=404)
        
        try:
            user = request.data['user']
        except:
            return Response(data={'message': 'Must include a user'}, status=404)
        
        try:
            # Convert the True|False string to Boolean
            runInDebugMode = request.data['runInDebugMode']
            if runInDebugMode == 'False':
                runInDebugMode = False
            else:
                runInDebugMode = True
        except:
            runInDebugMode = False
           
        playbookObj = DB.name.getDocuments(collectionName='playbooks', fields={'playbook': playbook}, 
                                           includeFields={'_id':0, 'playbook': 0})
        
        try:
            playbookObj[0]
        except:
            return Response(data={'message': f'No such playbook: {playbook}'}, status=404)
              
        # {'L3 Tests': [{'module': 'SanityScripts', 'setupFile': '', 'modulePreferences': '/Keystack/Modules/SanityScripts/ModulePreferences/modulePreferences.yml', 'testcases': ['/Keystack/Modules/SanityScripts/Testcases/bgp.py', '/Keystack/Modules/SanityScripts/Testcases/ospf.py', '/Keystack/Modules/SanityScripts/Testcases/isis.py'], 'emailResults': False, 'debugMode': False}]}

        try:
            SessionMgmt().runPlaybook(playbook=playbook, user=user, runInDebugMode=runInDebugMode)
            statusCode = 202
            message = 'Success'
        except Exception as errMsg:
            statusCode = 404
            message = f'Run playbook failed: {errMsg}'
        
        return Response(data={'message': message}, status=statusCode)
            
    def delete(self, request):
        """
        Delete a playbook
        
        DELETE: /api/playbook
        """
        playbook = request.POST['playbook']
        exists = DB.name.getDocuments(collectionName='playbooks', fields={'sessionId': playbook})

        try:
            #statusCode = SessionMgmt().deleteSession(sessionId)
            statusCode = 202
            message = 'Success'
        except Exception as errMsg:
            statusCode = 400
            message = f'Failed. No such playbook: {playbook}'
            
        return Response(data={'message': message}, status=statusCode)
