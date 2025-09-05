import zmq,zmq.asyncio,json,sys,os,sys,asyncio
current_path=os.path.dirname(__file__)
core_path=os.path.dirname(current_path)
project_path=os.path.dirname(core_path)
main_path=os.path.dirname(project_path)
sys.path.insert(0,main_path)
os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']='true'
os.chdir(main_path)
os.environ['DJANGO_SETTINGS_MODULE']='spartaqube_app.settings'
from project.sparta_440f6a201b.sparta_aac43fa003.qube_2c6fbcb282 import IPythonKernel
from project.sparta_440f6a201b.sparta_15c403c94e.qube_9d9e61f4e7 import ReceiverKernel
from project.logger_config import logger
def sparta_97fe3068bb(file_path,text):
	A=file_path
	try:
		B='a'if os.path.exists(A)and os.path.getsize(A)>0 else'w'
		with open(A,B,encoding='utf-8')as C:
			if B=='a':C.write('\n')
			C.write(text)
		logger.debug(f"Successfully wrote/appended to {A}")
	except Exception as D:logger.debug(f"Error writing to file: {D}")
async def start_worker(api_key,worker_port,venv_str):
	C=venv_str;D=zmq.asyncio.Context();A=D.socket(zmq.ROUTER);A.bind(f"tcp://127.0.0.1:{worker_port}");B=IPythonKernel(api_key);await B.initialize()
	if C!='-1':await B.activate_venv(C)
	E=ReceiverKernel(B,A)
	while True:F,G=await A.recv_multipart();H=json.loads(G);await E.process_request(F,H)
if __name__=='__main__':api_key=sys.argv[1];worker_port=sys.argv[2];venv_str=sys.argv[3];asyncio.run(start_worker(api_key,worker_port,venv_str))