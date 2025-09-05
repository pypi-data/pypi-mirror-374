import json
from channels.generic.websocket import AsyncWebsocketConsumer


class WebsocketCore(AsyncWebsocketConsumer):

    async def connect(self, user):
        self.user_obj = user

    async def receive(self, text_data: dict):
        pass

    async def disconnect(self, close_code: int):
        pass

#END OF QUBE
