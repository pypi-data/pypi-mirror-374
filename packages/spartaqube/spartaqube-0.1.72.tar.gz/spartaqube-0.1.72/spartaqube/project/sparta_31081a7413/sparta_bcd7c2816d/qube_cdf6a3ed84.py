_E='execute_code'
_D='backend'
_C=False
_B=None
_A='service'
import os,sys,json,base64,cloudpickle,importlib,traceback,asyncio,subprocess,platform
from django.conf import settings
from pathlib import Path
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from spartaqube_app.path_mapper_obf import sparta_fc868586da
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import sparta_a253265c85
from project.sparta_440f6a201b.sparta_15c403c94e.qube_293080d79c import SenderKernel
from project.sparta_440f6a201b.sparta_bb5bf030e1.qube_203378cc3e import sparta_8b9995568a,sparta_08311cba71
from project.logger_config import logger
class OutputRedirector:
	def __init__(A,websocket):A.websocket=websocket;A.original_stdout=sys.stdout;A.original_stderr=sys.stderr
	def __enter__(A):
		class B:
			def __init__(A,websocket):A.websocket=websocket
			def write(A,message):
				if A.websocket:
					try:A.websocket.send(json.dumps({'res':1000,'msg':message}))
					except Exception as B:logger.debug(f"WebSocket send error: {B}")
		A.custom_stream=B(A.websocket);sys.stdout=A.custom_stream;sys.stderr=A.custom_stream
	def __exit__(A,exc_type,exc_val,exc_tb):sys.stdout=A.original_stdout;sys.stderr=A.original_stderr
class ApiWebserviceWS(AsyncWebsocketConsumer):
	async def prepare_sender_kernel(A,kernel_manager_uuid):
		from project.models import KernelProcess as C;B=await sync_to_async(lambda:list(C.objects.filter(kernel_manager_uuid=kernel_manager_uuid)),thread_sensitive=_C)()
		if len(B)>0:
			D=B[0];E=D.port
			if A.sender_kernel_obj is _B:A.sender_kernel_obj=SenderKernel(A,E)
			A.sender_kernel_obj.zmq_connect()
	async def connect(A):await A.accept();A.user=A.scope['user'];A.sender_kernel_obj=_B
	async def disconnect(A,close_code=_B):
		logger.debug('Disconnect')
		try:await A.close()
		except:pass
	async def init_kernel_import_models(B,user_project_path):C=os.path.join(os.path.dirname(user_project_path),_D);A=os.path.join(C,'app');D=f'''
%load_ext autoreload
%autoreload 2    
import os, sys
import django
# Set the Django settings module
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
sys.path.insert(0, r"{A}")
os.chdir(r"{A}")
os.environ[\'DJANGO_SETTINGS_MODULE\'] = \'app.settings\'
# Initialize Django
django.setup()
''';await B.sender_kernel_obj.send_zmq_request({_A:_E,'cmd':D})
	async def init_kernel(A,kernel_manager_uuid,user_project_path):await A.prepare_sender_kernel(kernel_manager_uuid);await A.init_kernel_import_models(user_project_path)
	async def receive(A,text_data):
		E=text_data
		if len(E)>0:
			B=json.loads(E);G=B['kernelManagerUUID'];N=B.get('isRunMode',_C);H=B.get('initOnly',_C);F=sparta_a253265c85(B['baseProjectPath']);I=os.path.join(os.path.dirname(F),_D);J=B[_A];K=B.copy();await A.init_kernel(G,F)
			if H:await A.send(json.dumps({'res':1}));return
			C='import os, sys, importlib\n';C+=f'sys.path.insert(0, r"{I}")\n';C+=f"import webservices\n";C+=f"importlib.reload(webservices)\n";C+=f"webservice_res_dict = webservices.sparta_d4219a0df1(service_name, post_data)\n";L={'service_name':J,'post_data':K};M=base64.b64encode(cloudpickle.dumps(L)).decode('utf-8');await A.sender_kernel_obj.send_zmq_request({_A:'set_workspace_variables','encoded_dict':M});await A.sender_kernel_obj.send_zmq_request({_A:_E,'cmd':C});D=await A.sender_kernel_obj.send_zmq_request({_A:'get_workspace_variable','kernel_variable':'webservice_res_dict'})
			if D is not _B:D['webservice_resolve']=1;await A.send(json.dumps(D))