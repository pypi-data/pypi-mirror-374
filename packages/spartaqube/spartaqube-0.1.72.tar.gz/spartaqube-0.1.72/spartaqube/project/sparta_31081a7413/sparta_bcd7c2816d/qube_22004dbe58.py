import json
from channels.generic.websocket import WebsocketConsumer
from project.logger_config import logger
class StatusWS(WebsocketConsumer):
	channel_session=True;http_user_and_session=True
	def connect(A):logger.debug('Connect Now');A.accept();A.json_data_dict=dict()
	def disconnect(A,close_code=None):
		logger.debug('Disconnect')
		try:A.close()
		except:pass
	def receive(A,text_data):B={'res':1};C=json.dumps(B);A.send(text_data=C)