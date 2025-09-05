_H='list_workspace_variables'
_G='get_kernel_variable_repr'
_F='set_workspace_variable'
_E='activate_venv'
_D='ZMQ is connected'
_C='response'
_B=None
_A='service'
import os,sys,uuid,zmq,zmq.asyncio,json,base64,cloudpickle,asyncio,concurrent.futures
from project.logger_config import logger
def sparta_7a02b063ca(func):
	async def A(self,*B,**C):
		A=self;A.zmq_connect()
		try:return await func(A,*B,**C)
		finally:A.zmq_close()
	return A
def sparta_96d248094c(func):
	async def A(self,*B,**C):
		A=self;A.zmq_connect_sync()
		try:return await func(A,*B,**C)
		finally:A.zmq_close()
	return A
class SenderKernel:
	def __init__(A,websocket,port):A.websocket=websocket;A.port=port;A.zmq_context=_B;A.zmq_socket=_B
	def zmq_connect(A):
		logger.debug('ZMQ connect now')
		if A.zmq_socket is _B:B=str(uuid.uuid4());logger.debug(f"Async Identity: {B} on port {A.port}");A.zmq_context=zmq.asyncio.Context();A.zmq_socket=A.zmq_context.socket(zmq.DEALER);A.zmq_socket.setsockopt_string(zmq.IDENTITY,B);A.zmq_socket.connect(f"tcp://127.0.0.1:{A.port}")
		elif not A.zmq_socket.getsockopt(zmq.LAST_ENDPOINT):A.zmq_socket.connect(f"tcp://127.0.0.1:{A.port}")
		logger.debug(_D)
	def zmq_connect_sync(A):
		if A.zmq_socket is _B:B=str(uuid.uuid4());logger.debug(f"Sync Identity: {B} on port {A.port}");A.zmq_context=zmq.Context();A.zmq_socket=A.zmq_context.socket(zmq.DEALER);A.zmq_socket.setsockopt_string(zmq.IDENTITY,B);A.zmq_socket.connect(f"tcp://127.0.0.1:{A.port}")
		elif not A.zmq_socket.getsockopt(zmq.LAST_ENDPOINT):A.zmq_socket.connect(f"tcp://127.0.0.1:{A.port}")
		logger.debug(_D)
	def zmq_close(A):A.zmq_socket.close(linger=0);A.zmq_context.term()
	async def send_zmq_request(B,sender_dict,b_send_websocket_msg=True):
		D=sender_dict;logger.debug(f"SEND ZMQ REQ on port {B.port}");logger.debug(D);await B.zmq_socket.send_string(json.dumps(D));print('ZMQ sent...')
		while True:
			A=json.loads(await B.zmq_socket.recv_string());C=A[_A];logger.debug(f"service >>> {C}")
			if C in['exec','execute_code','execute_shell','execute',_E,'deactivate_venv','reset_kernel_workspace',_F,'set_workspace_variables','set_workspace_variable_from_datasource','set_workspace_variable_from_paste_modal']:
				if b_send_websocket_msg:await B.websocket.send(json.dumps(A))
			elif C in[_G,_H]:return A[_C]
			elif C in['get_workspace_variable']:E=base64.b64decode(A[_C]);F=cloudpickle.loads(E);return F
			if A['is_terminated']:return
	def sync_request(A,sender_dict,timeout=3000):
		C=sender_dict;A.zmq_connect_sync();A.zmq_socket.send_string(json.dumps(C));logger.debug('Sync request sent');D=zmq.Poller();D.register(A.zmq_socket,zmq.POLLIN)
		if D.poll(timeout):E=A.zmq_socket.recv_json();B=E[_C]
		else:B=-1
		logger.debug(f"SERVICE SYNC REQUEST {C[_A]}");logger.debug(B);A.zmq_close();return B
	def sync_create_kernel(A,api_key,venv):B={_A:'create_kernel','api_key':api_key,'venv':venv};return A.sync_request(B)
	def sync_list_available_kernels(A):B={_A:'list_available_kernels'};return A.sync_request(B)
	def sync_kill_kernel(A):B={_A:'kill_kernel'};return A.sync_request(B)
	def sync_get_kernel_size(A):B={_A:'get_kernel_memory_size'};return A.sync_request(B)
	def sync_get_kernel_workspace_variables(A):B={_A:_H};return A.sync_request(B)
	def sync_activate_venv(A,venv_name):B={_A:_E,'venv_name':venv_name};return A.sync_request(B)
	def sync_get_kernel_variable_repr(A,kernel_variable):B={_A:_G,'kernel_variable':kernel_variable};return A.sync_request(B)
	def sync_set_workspace_variable(A,var_name,var_value):B={_A:_F,'json_data':json.dumps({'name':var_name,'value':json.dumps(var_value)})};return A.sync_request(B)
	def sync_set_workspace_cloudpickle_variables(A,cloudpickle_kernel_variables):B={_A:'set_workspace_cloudpickle_variable','cloudpickle_kernel_variables':base64.b64encode(cloudpickle_kernel_variables).decode('utf-8')};return A.sync_request(B)
	def sync_get_cloudpickle_kernel_variables(E):
		D='unpicklable';C='picklable';F={_A:'get_cloudpickle_kernel_all_variables'};B=E.sync_request(F)
		if isinstance(B,int):return
		else:A=json.loads(B);A[C]=base64.b64decode(A[C]);A[D]=base64.b64decode(A[D]);return A