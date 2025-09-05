_E='service'
_D='is_terminated'
_C='utf-8'
_B='response'
_A='res'
import json,io,base64,os,sys,cloudpickle,pandas as pd
from project.logger_config import logger
from project.sparta_440f6a201b.sparta_aac43fa003.qube_2c6fbcb282 import IPythonKernel
def sparta_97fe3068bb(file_path,text):
	A=file_path
	try:
		B='a'if os.path.exists(A)and os.path.getsize(A)>0 else'w'
		with open(A,B,encoding=_C)as C:
			if B=='a':C.write('\n')
			C.write(text)
		logger.debug(f"Successfully wrote/appended to {A}")
	except Exception as D:logger.debug(f"Error writing to file: {D}")
class ReceiverKernel:
	def __init__(A,ipython_kernel,socket_zmq):A.ipython_kernel=ipython_kernel;A.socket_zmq=socket_zmq
	async def send_response(C,identity,response_dict,request_dict=None):
		B=request_dict;A=response_dict
		if B is not None:A.update(B)
		A[_D]=True;await C.socket_zmq.send_multipart([identity,json.dumps(A).encode()])
	async def terminate(A,identity):B={_A:1,_E:'break-loop',_D:True,_B:1};await A.send_response(identity,B)
	async def create_new_ipython_kernel(B,api_key,venv):
		A=IPythonKernel(api_key);await A.initialize()
		if venv!='-1':await A.activate_venv(venv)
		B.ipython_kernel=A
	async def process_request(C,identity,request_dict):
		S='value';R='kernel_variable';Q='cellId';P='name';O='cmd';J='json_data';E=identity;A=request_dict;D=A[_E];B=C.ipython_kernel;B.set_zmq_identity(E);B.set_zmq_request(A)
		if D=='execute_code':H=A[O];await B.execute_code(H,websocket=C.socket_zmq)
		elif D=='execute_shell':H=A[O];F=json.loads(A[J]);await B.execute_shell(H,websocket=C.socket_zmq,cell_id=F[Q])
		elif D=='execute':H=A[O];F=json.loads(A[J]);await B.execute(H,websocket=C.socket_zmq,cell_id=F[Q])
		elif D=='activate_venv':T=A['venv_name'];await B.activate_venv(T);await C.terminate(E)
		elif D=='deactivate_venv':await B.deactivate_venv();await C.terminate(E)
		elif D=='get_kernel_variable_repr':K=A[R];U=B._method_get_kernel_variable_repr(kernel_variable=K);G={_A:1,_B:U};await C.send_response(E,G,A)
		elif D=='get_workspace_variable':K=A[R];V=await B._method_get_workspace_variable(kernel_variable=K);W=base64.b64encode(cloudpickle.dumps(V)).decode(_C);G={_A:1,_B:W};await C.send_response(E,G,A)
		elif D=='reset_kernel_workspace':B.reset_kernel_workspace();await C.terminate(E)
		elif D=='list_workspace_variables':X=await B.list_workspace_variables();G={_A:1,_B:X};await C.send_response(E,G,A)
		elif D=='set_workspace_variable':F=json.loads(A[J]);await B._method_set_workspace_variable(name=F[P],value=json.loads(F[S]));await C.terminate(E)
		elif D=='set_workspace_variables':
			I=cloudpickle.loads(base64.b64decode(A['encoded_dict']))
			for(L,M)in I.items():await B._method_set_workspace_variable(L,M)
			await C.terminate(E)
		elif D=='set_workspace_variable_from_datasource':F=json.loads(A[J]);I=json.loads(F[S]);Y=pd.DataFrame(I['data'],columns=I['columns'],index=I['index']);await B._method_set_workspace_variable(name=F[P],value=Y);await C.terminate(E)
		elif D=='get_kernel_memory_size':Z=await B.get_kernel_memory_size();G={_A:1,_B:Z};await C.send_response(E,G,A)
		elif D=='set_workspace_cloudpickle_variable':
			N=base64.b64decode(A['cloudpickle_kernel_variables']);N=cloudpickle.loads(N)
			for(L,M)in N.items():a=io.BytesIO(M);b=cloudpickle.load(a);await B._method_set_workspace_variable(L,b)
			await C.terminate(E)
		elif D=='set_workspace_variable_from_paste_modal':F=json.loads(A[J]);await B._method_set_workspace_variable_from_paste_modal(name=F[P],value=F['df_json']);await C.terminate(E)
		elif D=='get_cloudpickle_kernel_all_variables':c,d=await B.cloudpickle_kernel_variables();G={_A:1,_B:json.dumps({'picklable':base64.b64encode(cloudpickle.dumps(c)).decode(_C),'unpicklable':base64.b64encode(cloudpickle.dumps(d)).decode(_C)})};await C.send_response(E,G,A)