import json, time
from random import randint
from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer, AsyncConsumer

# websocket references: https://earthly.dev/blog/build-real-time-comm-app/

# Channels docs: https://channels.readthedocs.io/en/latest/topics/consumers.html

# Real-Time App with WebSocket Django Channels: https://michaelsusanto81.medium.com/real-time-app-with-websocket-through-django-channels-adb436e9a17a

# tail -f streaming: https://amittallapragada.github.io/docker/fastapi/python/2020/12/23/server-side-events.html
#                    https://h3xagn.com/create-a-streaming-log-viewer-using-fastapi/

# Configure Docker/Apache/Daphne/Channels:
#      https://medium.com/@ahmedhosnycs/django-channels-deployment-with-docker-apache-7520163773c9

class LogsConsumer_backup(AsyncJsonWebsocketConsumer):
    async def websocket_application(scope, receive, send):
        while True:
            event = await receive()
            print('\n--- event:', event)
            
            if event['type'] == 'websocket.connect':
                print('\n--- connect ----')
                await send(text_data=json.dumps({
                    'type': 'websocket.accept',
                    'data': 'ack!'
                }))

            if event['type'] == 'websocket.disconnect':
                print('\n--- disconnect ---')
                break

            if event['type'] == 'websocket.receive':
                print('\n---- received ----')
                if event['text'] == 'ping':
                    await send(text_data=json.dumps({
                        'type': 'websocket.send',
                        'data': 'pong!'
                    }))   
                else:
                    await send(text_data=json.dumps({
                        'type': 'websocket.send',
                        'data': 'pong!'
                    }))  
                  
                                        
class LogsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print('\n---- logConsumers.py connect ---', self.scope)
        print('\n---- channelName:', self.channel_name)
         
        # {'type': 'websocket', 'path': '/ws/room/wsPipelineRoom', 'raw_path': b'/ws/room/wsPipelineRoom', 'headers': [(b'host', b'192.168.28.10:28028'), (b'connection', b'Upgrade'), (b'pragma', b'no-cache'), (b'cache-control', b'no-cache'), (b'user-agent', b'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'), (b'upgrade', b'websocket'), (b'origin', b'http://192.168.28.10:28028'), (b'sec-websocket-version', b'13'), (b'accept-encoding', b'gzip, deflate'), (b'accept-language', b'en-US,en;q=0.9'), (b'cookie', b'csrftoken=ZP7KTmr4NctMzUwNcoAt4pQ3NFI8O1hr; sessionid=ytucsy931zhxmp7c0x03uoqqbrh0nz5w'), (b'sec-websocket-key', b'TLB1YhYMl0SOi8m3nF4vIg=='), (b'sec-websocket-extensions', b'permessage-deflate; client_max_window_bits')], 'query_string': b'', 'client': ['192.168.28.1', 64915], 'server': ['192.168.28.10', 28028], 'subprotocols': [], 'asgi': {'version': '3.0'}, 'path_remaining': '', 'url_route': {'args': (), 'kwargs': {}}} 
        
        #self.roomName = self.scope['url_route']['kwargs']['roomName']
        self.roomName = 'pipeline'
        self.groupName = 'testcaseLogs'
        
        # The AuthMiddlewareStack you added earlier will populate the scope with the current user which you can then retrieve in the consumer.
        # This line in the connect method of the JoinAndLeave consumer retrieves the current user:
        #self.user = self.scope["user"]
        
        # Create new group and Join to group
        # channel_name -> specific..inmemory!SZVdBoZTyfhA
        await self.channel_layer.group_add(
            self.groupName,
            self.channel_name
        )

        # Accept the message first before sending a message
        await self.accept()
        
        await self.channel_layer.group_send(
            self.groupName,
            {
                'type': 'tester_message',
                'tester': 'Hello world',
            }    
        )
        
        #self.send(text_data=json.dumps({'type':'connect_established', 'message': "You are connected to the server!"}))
            
    async def disconnect(self, closeCode):
        # closeCode -> 1001
        print('\n---- logConsumers.py disconnect ---', closeCode)
        # Leave group        
        await self.channel_layer.group_discard(
            self.groupName,
            self.channel_name
        )
        
    async def tester_message(self, event):
        tester = event['tester']
        await self.send(text_data=json.dumps({
            'tester': tester,
        }))
        
    async def log_reader(self, n=5):
        log_lines = []
        readPath = "/opt/Keystack/websocketLogs.txt"
        
        with open(readPath, "r") as file:
            for line in file.readlines()[-n:]:
                log_lines.append(line)
                
                if line.__contains__("Failed"):
                    log_lines.append(f'<span class="text-red-400">{line}</span><br/>')
                elif line.__contains__("Warning"):
                    log_lines.append(f'<span class="text-orange-300">{line}</span><br/>')
                else:
                    log_lines.append(f"{line}<br/>")
                
            return log_lines
                    
    async def receive(self, text_data):
        print('\n--- receive: text_data:', text_data)
        textDataJson = json.loads(text_data)
        
        # 'message' is the html javascript passed in keyword
        message = textDataJson.get('messageFromTemplateJS', None)
        
        print('\n--- 1:Msg received from templateJS:', textDataJson, type(textDataJson))
        print('---- 2: ---', message)

        # send a message back to the client
        #await self.send(text_data=json.dumps({'type': 'chat', 'message': 'ACK from server!'}))
        # type: send_message

        await self.channel_layer.group_send(
            self.groupName,
            {
                'type': "send_message", 
                'message': message,
                'event': 'gotcha'
            }
        )
        
        '''
        import asyncio
        try:
            counter = 0
            stopCounter = 0
            while True:
                await asyncio.sleep(3)
                
                logs = await self.log_reader(60)
                print('\n--- logs:', logs)
                #await websocket.send_text(logs)
                
                await self.channel_layer.group_send(
                    self.groupName, {
                        'type': "send_message", 
                        'message': logs,
                        'event': 'gotcha'
                    })
                
                if counter == stopCounter:
                    break
                
                counter += 1
                
        except Exception as e:
            print(e)
        finally:
            # Uncomment this is you want to leave the group
            await self.disconnect('123')
        '''    

    async def send_message(self, event):
        """ 
        Receive message from room group
        """
        print('\n--- send_message:', event, type(event))
        message = event['message']        
        await self.send(text_data=json.dumps({"message": message}))
        
                           
'''
import asyncio
import json
from channels.consumer import AsyncConsumer
from random import randint
from time import sleep

class PracticeConsumer(AsyncConsumer):
    async def websocket_connect(self,event):
        # when websocket connects
        print("Connected:", event)

        await self.send({"type": "websocket.accept",})
        await self.send({"type":"websocket.send", "text":0})

    async def websocket_receive(self,event):
        # when messages is received from websocket
        print("Received:", event)
        sleep(1)

        await self.send({"type": "websocket.send",
                         "text":str(randint(0,100))})

    async def websocket_disconnect(self, event):
        # when websocket disconnects
        print("Disconnected:", event)
'''
