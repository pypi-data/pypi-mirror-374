import json
import asyncio
import websockets
from channels.generic.websocket import AsyncWebsocketConsumer


class WebsocketCore(AsyncWebsocketConsumer):

    async def connect(self, user):
        self.user_obj = user
        self.keep_stream_price = True

        async def trade_stream(symbol):
            url = f'wss://stream.binance.com:9443/ws/{symbol}@trade'
            async with websockets.connect(url) as websocket:
                print(f'Connected to Binance WebSocket for {symbol} trades')
                try:
                    while True and self.keep_stream_price:
                        response = await websocket.recv()
                        print(f'Trade: {response}')
                        self.send(response)
                except websockets.ConnectionClosed as e:
                    print(f'WebSocket connection closed: {e}')
                except Exception as e:
                    print(f'Error: {e}')
        symbol = 'btcusdt'
        await asyncio.run(trade_stream(symbol))

    async def receive(self, text_data):
        pass

    async def disconnect(self, close_code):
        self.keep_stream_price = False

#END OF QUBE
