import json
import random
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer


def sparta_5c7ff17045(service: str, post_data: dict, user
    ) ->AsyncWebsocketConsumer:
    """
    Implement your websockets here
    1. Use the service name to differentiate the websockets
    2. User's data are sent within the dictionary post_data
    3. The user variable can be used to differentiate the user who run the query
    """
    print(f'Service: {service}')
    if service == 'example_websocket_btc':
        from examples.api_driven.websocket_btc import WebsocketCore
        return WebsocketCore(post_data, user)

#END OF QUBE
