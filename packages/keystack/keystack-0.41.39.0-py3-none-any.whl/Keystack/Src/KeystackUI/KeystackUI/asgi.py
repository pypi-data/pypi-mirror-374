import os

# Details about what this is and why this file is needed -
# https://channels.readthedocs.io/en/latest/asgi.html
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path 

#from sidebar.sessionMgmt.routing import websocket_urlPatterns as sessionMgmt_ws
#from sidebar.testResults.routing import websocket_urlPatterns as testResults_ws

from sidebar.sessionMgmt import logConsumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "KeystackUI.settings")

application = ProtocolTypeRouter (
    {
        # handle http/https requests
        "http": get_asgi_application(),
        
        # handle ws/wss requests
        # To associate the user with a websocket connection, you can wrap the URLRouter class with the AuthMiddlewareStack provided by channels.
        # This will populate the metadata about the connection with the user instance.
        # The Metadata can be accessed from the self.scope attribute in the consumer class. The scope is similar to the request.META in Django.
        
        # For security purposes, you will add the AllowedHostsOriginValidator that validates the origin of the websocket connection.  Also, for security purposes, you will add the AllowedHostsOriginValidator that validates the origin of the websocket connection.
        
        # "websocket": 
        #     AllowedHostsOriginValidator(
        #         AuthMiddlewareStack(
        #             #URLRouter(websocket_urlPatterns,),
                    
        #             # re_path(r'ws/testcaseLogs/$', logConsumers.LogsConsumer.as_asgi())
        #             URLRouter(sessionMgmt_ws,),
        #             #URLRouter(sessionMgmt_ws + testResults_ws,),
        #         )
        # )
            
        "websocket":
            AllowedHostsOriginValidator(
                AuthMiddlewareStack( 
            URLRouter([
                # Uncomment this when using this. Turning this off for debugging purpose.
                re_path(r'ws/room/pipelineId', logConsumers.LogsConsumer.as_asgi())
            ])
            )
            )
    }
)
    
