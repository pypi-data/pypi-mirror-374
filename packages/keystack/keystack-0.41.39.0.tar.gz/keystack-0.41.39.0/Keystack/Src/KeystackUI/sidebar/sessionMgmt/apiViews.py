
import os, sys, re

from rest_framework.views import APIView
from rest_framework.response import Response

from .views import SessionMgmt

# /Keystack/KeystackUI/sidebar/sessionMgmt
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir.replace('/KeystackUI/sidebar/sessionMgmt', ''))
from db import DB
import keystackUtilities

class Sessions(APIView):
    def get(self, request):
        """
        Get all session details
        
        GET /api/sessions
        """
        try:
            sessionsObjList = [session for session in DB.name.getDocuments(collectionName='sessions', fields={}, includeFields={'_id':0})]   
            sessionsList = []
            for session in sessionsObjList:
                testResultsPath = session['testResultsPath']
                for moduleTestResultsPath in testResultsPath:
                    status = keystackUtilities.readJson(f'{moduleTestResultsPath["path"]}/status.json')
                    sessionsList.append(status)
                    
            statusCode = 200
            message = sessionsList
        except Exception as errMsg:
            statusCode = 404
            message = 'Failed to get sessions'
            
        return Response(data={'sessions': message}, status=statusCode)

    
class SessionId(APIView):
    def get(self, request, sessionId=None):        
        # /api/sessions/id
        # Get a list of session IDs
        if sessionId is None:
            try:
                sessionsList = []
                for session in DB.name.getDocuments(collectionName='sessions', fields={}, includeFields={'_id':0}):
                    sessionsList.append(session['sessionId'])
                        
                statusCode = 200
                message = sessionsList
            except Exception as errMsg:
                statusCode = 404
                message = 'Failed to get session ID list'            
            
        # /api/sessions/<sessionID>
        # Get a specific session ID
        if sessionId:
            try:
                sessionsObjList = [session for session in DB.name.getDocuments(collectionName='sessions',
                                                                                fields={'sessionId': int(sessionId)}, 
                                                                                includeFields={'_id':0})]
                
                sessionsList = []
                for session in sessionsObjList:
                    testResultsPath = session['testResultsPath']
                    for moduleTestResultsPath in testResultsPath:
                        status = keystackUtilities.readJson(f'{moduleTestResultsPath["path"]}/status.json')
                        sessionsList.append(status)
                        
                statusCode = 200
                if sessionsList == []:
                    message = f'No such sessionId: {sessionId}'
                else:
                    message = sessionsList
                    
            except Exception as errMsg:
                statusCode = 404
                message = 'Failed to get sessions' 
    
        return Response(data={'message': message}, status=statusCode)                
    
    def delete(self, request, sessionId):
        """
        Delete a sessionId 
        
        DELETE: /api/sessionId/<sessionId>
        """
        try:
            exists = DB.name.getDocuments(collectionName='sessions', fields={'sessionId': int(sessionId)})[0]
        except Exception as errMsg:
            statusCode = 400
            message = f'Failed. No such sessionId: {sessionId}'
            return Response(data={'message': message}, status=statusCode)
            
        try:
            statusCode = SessionMgmt().deleteSession(int(sessionId))
            statusCode = 200
            message = 'Success'
        except Exception as errMsg:
            statusCode = 400
            message = f'Failed: {errMsg}: {sessionId}'
            
        return Response(data={'message': message}, status=statusCode)


    
