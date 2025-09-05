_D='notebook-kernel'
_C='dataframe'
_B=True
_A=None
import os,json,traceback,platform,websocket,threading,time,asyncio,pandas as pd
from pathlib import Path
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from project.logger_config import logger
from project.sparta_31081a7413.sparta_0886d51747 import qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_ceff546bba import qube_2940d28c8f as qube_2940d28c8f
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe,convert_dataframe_to_json,sparta_a253265c85
from project.sparta_440f6a201b.sparta_561d9f653d.qube_24937a6311 import LLMClientCloud as LLMClientCloud
from project.models import LLMSettings
class ChatbotWS(AsyncWebsocketConsumer):
	channel_session=_B;http_user_and_session=_B
	async def connect(A):logger.debug('Connect Now');A.user=A.scope['user'];A.json_data_dict=dict();A.llm_mode=_A;A.llm_client_obj=_A;await A.accept()
	async def disconnect(A,close_code=_A):logger.debug('Disconnect')
	async def get_llm_settings_cloud_model(B):
		A=await sync_to_async(lambda:list(LLMSettings.objects.filter(user=B.user)),thread_sensitive=False)()
		if len(A)>0:C=A[0];return C.cloud_model
		return'gpt-3.5-turbo'
	async def set_llm_client(A,cloud_model=_A,dataframe_json=_A):
		B=cloud_model;print('Set llm client now for LLM mode >>>');print(A.llm_mode)
		if A.llm_mode==_D:await A.set_notebook_llm_client(B)
		elif A.llm_mode==_C:await A.set_dataframe_llm_client(dataframe_json,B)
	async def set_notebook_llm_client(A,cloud_model=_A):
		B=cloud_model;C=''
		if B is _A:B=await A.get_llm_settings_cloud_model()
		A.llm_client_obj=LLMClientCloud(C,A.user);await A.llm_client_obj.set_generator(B)
	async def set_dataframe_llm_client(A,dataframe_json,cloud_model=_A):
		B=cloud_model;C=json.loads(dataframe_json);D=pd.DataFrame(data=C['data'],index=C['columns'],columns=C['index']).T
		if B is _A:B=await A.get_llm_settings_cloud_model()
		E='';A.llm_client_obj=LLMClientCloud(E,A.user,mode=_C);await A.llm_client_obj.set_generator(B,mode=_C);A.llm_client_obj.set_dataframe(D);await A.llm_client_obj.init_ipython_kernel()
	async def receive(A,text_data):
		Y='conversation';X='output';W='workspaceVariables';V='query';U='model';T='errorMsg';L=text_data;K='venv';G='res';F='service'
		if len(L)>0:
			E=json.loads(L);print('Chatbot Notebook WS');B=E[F];A.llm_mode=E['mode'];M=E.get('dataframe_json',_A)
			if B=='init':
				try:await A.set_llm_client(dataframe_json=M);D={G:1,F:B}
				except Exception as I:print('Error exception init llm with traceback:');print(traceback.format_exc());D={G:-1,F:B,T:str(I)}
				C=json.dumps(D);await A.send(text_data=C);return
			elif B=='switch-model':
				N=E[U]
				if A.llm_client_obj is _A:await A.set_llm_client(cloud_model=N,dataframe_json=M)
				else:
					try:await A.llm_client_obj.switch_model_type(N)
					except Exception as I:print('Error switch model with exception:');print(I)
			elif B==V:
				Z=E[V];a=E[U];O=_A
				if A.llm_mode==_D:
					if W in E:O=json.loads(E[W])
				print('Run query now')
				try:
					async for J in A.llm_client_obj.stream_completion(Z,workspace_variables=O,model=a):D={G:1,F:B,X:J};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
				except Exception as I:print('Error exception query with traceback:');print(traceback.format_exc());D={G:-1,F:B,T:str(I)};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
			elif B=='dataframe-exec-code':
				P=E.get('code',_A)
				if P is not _A:
					async for J in A.llm_client_obj.ipython_exec_code(P):D={G:1,F:B,X:J};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
			elif B=='dataframe-save-llm-history':H=await A.llm_client_obj.save_llm_history(dataframe_slug=E['dataframe_slug'],response_list_frontend=E['responseList'],venv=E[K],llm_settings_dict=E['llm_settings']);D={G:H[G],F:B};C=json.dumps(D);await A.send(text_data=C);return
			elif B=='dataframe-restore-chat':print('Restore chat');H=await A.llm_client_obj.restore_llm_chat(dataframe_llm_id=E['dataframe_llm_id']);print('res_dict');print(H);H[F]=B;C=json.dumps(H);await A.send(text_data=C);return
			elif B=='llm-settings':await A.llm_client_obj.set_llm_settings(E.get('auto_execute',_B),E.get('self_correcting',_B),E.get('max_retry',_B));H={G:1};H[F]=B;C=json.dumps(H);await A.send(text_data=C);return
			elif B=='clear':await A.llm_client_obj.clear_chatbot();D={G:1,F:B};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
			elif B=='get-conversation':b=A.llm_client_obj.get_conversation();D={G:1,F:B,Y:b};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
			elif B=='restore-conversation':
				c=E['messages'];Q=c[Y]
				for R in Q:
					if R['role']=='user':print('/'*100);print(R['content'])
				A.llm_client_obj.restore_conversation(Q);D={G:1,F:B};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
			elif B=='activate-venv':S=E[K];await A.llm_client_obj.activate_venv(S);D={G:1,F:B,K:S};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
			elif B=='deactivate-venv':await A.llm_client_obj.deactivate_venv();D={G:1,F:B};C=json.dumps(D);await A.send(text_data=C);await asyncio.sleep(0)
			elif B=='disconnect':A.disconnect()