_N='Model not valid'
_M='ANTHROPIC_API_KEY'
_L='OPENAI_API_KEY'
_K='is_autorun'
_J='api_key_ai_plan'
_I='errorMsg'
_H='gemini'
_G='cloud_model'
_F='anthropic'
_E='openai'
_D=True
_C=False
_B=None
_A='res'
import os,sys,uuid,platform,hashlib,requests,json,base64,time,requests,subprocess,socket
from datetime import datetime
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from django.conf import settings as conf_settings
import pytz
UTC=pytz.utc
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
from project.models import LLMPort,LLMSettings,LLMCredentials,LLMTrialKey,AIPlan
from project.sparta_440f6a201b.sparta_561d9f653d.qube_55a93bcbe3 import LLMLauncher
from project.sparta_440f6a201b.sparta_561d9f653d.qube_35ffe3dcea import sparta_e97782dba3
DEFAULT_MODEL='gpt-3.5-turbo'
def sparta_ae569cb250(start_port=47832,max_port=65535):
	for A in range(start_port,max_port+1):
		with socket.socket(socket.AF_INET,socket.SOCK_STREAM)as B:
			try:B.bind(('',A));B.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);return A
			except OSError:continue
	raise RuntimeError('No free port found in range.')
def sparta_5414987a28():
	B=-1;C=LLMPort.objects.all()
	if C.count()>0:
		D=C[0];E=D.port;A=D.host
		if A is _B:A='localhost'
		try:
			F=requests.get(f"http://{A}:{E}/",timeout=2)
			if F.status_code<500:B=1
		except requests.exceptions.RequestException:pass
	return B
def sparta_c5961a02b1(json_data,user_obj):return{_A:1,'status':sparta_5414987a28()}
def sparta_511ae3e032(json_data,user_obj):
	G=_C
	if not G:return{_A:1}
	print(f"STATUS LLM: >>> {get_llm_server_status()}")
	if sparta_5414987a28()==1:return{_A:1}
	A='Phi-3-mini-4k-instruct-q4.gguf';A='mistral-7b-instruct-v0.1.Q4_K_S.gguf';A='DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf';A='Phi-3-medium-128k-instruct-Q4_K_S.gguf';A='deepseek-coder-6.7b-instruct.Q4_K_S.gguf';H='C:\\\\Users\\\\benme\\\\Desktop\\\\demo_llama_cpp\\\\llama-b5604-bin-win-cuda-12.4-x64';B='C:\\Users\\benme\\Desktop\\demo_llama_cpp';B='C:\\\\Users\\\\benme\\\\.lmstudio\\\\models\\\\TheBloke\\\\Mistral-7B-Instruct-v0.1-GGUF';B='C:\\\\Users\\\\benme\\\\.lmstudio\\\\models\\\\lmstudio-community\\\\DeepSeek-Coder-V2-Lite-Instruct-GGUF';B='C:\\\\Users\\\\benme\\\\.lmstudio\\\\models\\\\bartowski\\\\Phi-3-medium-128k-instruct-GGUF';B='C:\\\\Users\\\\benme\\\\.lmstudio\\\\models\\\\TheBloke\\\\deepseek-coder-6.7B-instruct-GGUF';I=os.path.join(H,'llama-server.exe');J=os.path.join(B,A);C=sparta_ae569cb250();print(f"server_port >>> {C}");K=os.path.dirname(__file__);L=os.path.join(K,'llm_launcher.py');M=subprocess.Popen([sys.executable,L,'--server-path',I,'--model-path',J,'--port',str(C),'--n-gpu-layers','35'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=_D,bufsize=1);print('Started launcher with PID',M.pid);E=datetime.now().astimezone(UTC);F=LLMPort.objects.all()
	if F.count()>0:D=F[0];D.port=C;D.last_update=E;D.save()
	else:LLMPort.objects.create(port=C,last_update=E)
	return{_A:1}
def sparta_ee6fcf5aee(json_data,user_obj):
	A=LLMSettings.objects.filter(user=user_obj).all()
	if A.count()>0:B=A[0];return{_A:1,_K:B.is_autorun,_G:B.cloud_model}
	return{_A:1,_K:_C,_G:DEFAULT_MODEL}
def sparta_2220ae498b(json_data,user_obj):A=json_data[_G];return{_A:1,'has_api_key_available':sparta_73c5b5b04b(user_obj,A)}
def sparta_73c5b5b04b(user_obj,cloud_model=DEFAULT_MODEL):
	A=_B;C=sparta_e97782dba3()[cloud_model];D=LLMCredentials.objects.filter(user=user_obj).all()
	if D.count()>0:
		B=D[0];A=B.openai_key
		if C==_E:
			A=B.openai_key
			if A is _B:A=os.environ.get(_L,_B)
		elif C==_F:
			A=B.anthropic_key
			if A is _B:A=os.environ.get(_M,_B)
	if A is _B:return _C
	else:return _D
def sparta_d9c34fcaa4(json_data,user_obj):
	E=user_obj;D=json_data;C=datetime.now().astimezone(UTC);A=D[_G]
	if A not in list(sparta_e97782dba3().keys()):A=DEFAULT_MODEL
	F=D[_K];G=LLMSettings.objects.filter(user=E).all()
	if G.count()>0:B=G[0];B.cloud_model=A;B.is_autorun=F;B.last_update=C;B.save()
	else:LLMSettings.objects.create(user=E,cloud_model=A,is_autorun=F,last_update=C,date_created=C)
	return{_A:1,_G:A}
def sparta_634f4bfcfe(json_data,user_obj):
	E='gemini_key';D='anthropic_key';C='openai_key';B=LLMCredentials.objects.filter(user=user_obj).all()
	if B.count()>0:A=B[0];return{_A:1,C:A.openai_key,D:A.anthropic_key,E:A.gemini_key}
	else:F=os.environ.get(_L,'');G=os.environ.get(_M,'');H=os.environ.get('GOOGLE_API_KEY','');return{_A:1,C:F,D:G,E:H}
def sparta_3f223e35e4(json_data,user_obj):
	F=user_obj;E=json_data;D=datetime.now().astimezone(UTC);A=E['model']
	if A not in[_E,_F,_H]:return{_A:-1,_I:_N}
	B=E['api_key'];G=LLMCredentials.objects.filter(user=F).all()
	if G.count()>0:
		C=G[0]
		if A==_E:C.openai_key=B
		elif A==_F:C.anthropic_key=B
		elif A==_H:C.gemini_key=B
		C.last_update=D;C.save()
	else:
		H=_B;I=_B;J=_B
		if A==_E:H=B
		elif A==_F:I=B
		elif A==_H:J=B
		LLMCredentials.objects.create(user=F,openai_key=H,anthropic_key=I,gemini_key=J,last_update=D,date_created=D)
	return{_A:1}
def sparta_e84f0301af(json_data,user_obj):
	D=datetime.now().astimezone(UTC);B=json_data['model']
	if B not in[_E,_F,_H]:return{_A:-1,_I:_N}
	C=LLMCredentials.objects.filter(user=user_obj).all()
	if C.count()>0:
		A=C[0]
		if B==_E:A.openai_key=_B
		elif B==_F:A.anthropic_key=_B
		elif B==_H:A.gemini_key=_B
		A.last_update=D;A.save()
	return{_A:1}
CLOUDFLARE_URL=f"{conf_settings.SERVER_CF}/"
CLOUDFLARE_AI_STATUS_URL=os.path.join(CLOUDFLARE_URL,'ai-status')
def sparta_ac848e8571(json_data,user_obj):
	V='trial_api_key';N='is_api_plan_verified';H=user_obj;print('CALL llm_cf_fetch_status_api');J=_C;O=_C;B=_B;C=LLMTrialKey.objects.filter().all()
	if C.count()>0:D=C[0];B=D.trial_key;O=_D
	E=_B;P=_C;F=_C;W=sparta_e72f323dbf();Q=AIPlan.objects.filter(user=H)
	if Q.count()>0:
		I=Q[0];J=I.b_use_personal_key;F=I.is_api_plan_verified;E=I.api_key_ai_plan;K=I.existing_api_key_ai_plan
		if K is not _B:
			if len(K)>0:E=K
		P=_D
	if J:return{_A:1,'b_use_personal_key':J}
	R={'fingerprint':W,'b_has_trial_key':O,V:B,'b_has_api_plan_key':P,_J:E,N:F};print('payload');print(R)
	try:
		L=requests.post(CLOUDFLARE_AI_STATUS_URL,json=R);print('response');print(L.text)
		if L.status_code==200:
			A=L.json()
			if H is _B:return A
			G=A.get('django_action',_B)
			if G is not _B:
				G=int(G)
				if G==1:
					B=A.get(V);C=LLMTrialKey.objects.filter().all();M=datetime.now().astimezone(UTC)
					if C.count()==0:LLMTrialKey.objects.create(user=H,trial_key=B,date_created=M,last_update=M)
					else:D=C[0];D.trial_key=B;D.last_update=M;D.save()
				elif G==2:
					S=AIPlan.objects.filter(user=H)
					if S.count()>0:T=S[0];T.is_api_plan_verified=_D;F=_D;T.save()
			if A[_A]==1:return{_A:1,N:F,_J:E}
			else:A[_J]=E;A[N]=F;return A
	except Exception as U:print('Failed to get API key:',U);return{_A:-1,_I:str(U)}
def sparta_e72f323dbf():A=platform.node()+str(uuid.getnode());B=hashlib.sha256(A.encode()).hexdigest();return B
def sparta_93b98a4162(user_obj):
	A=AIPlan.objects.filter(user=user_obj)
	if A.count()>0:
		B=A[0]
		if B.is_api_plan_verified:return _C
	return _D
def sparta_e7ab2007f8():A=uuid.uuid4();B=hashlib.sha256(str(A).encode());C=B.hexdigest();return C
def sparta_3cfd3cf3d3(json_data,user_obj):
	B=user_obj;C=json_data['existingApiKeyValue'];D=AIPlan.objects.filter(user=B)
	if D.count()>0:A=D[0];A.is_api_plan_verified=_D;A.existing_api_key_ai_plan=C;A.save()
	else:E=datetime.now().astimezone(UTC);A=AIPlan.objects.create(user=B,api_key_ai_plan=sparta_e7ab2007f8(),existing_api_key_ai_plan=C,is_api_plan_verified=_D,last_update=E,date_created=E)
	return{_A:1}
def sparta_aa6dd3dd2f(json_data,user_obj):
	A=AIPlan.objects.filter(user=user_obj)
	if A.count()>0:B=A[0];B.existing_api_key_ai_plan=_B;B.save()
	return{_A:1}
def sparta_7cbe92abd7(json_data,user_obj):
	D=AIPlan.objects.filter(user=user_obj)
	if D.count()>0:
		A=D[0]
		if A.is_api_plan_verified:
			F=A.api_key_ai_plan;C=A.reset_api_key_ai_plan
			if C is not _B:
				if len(C)>0:
					E=sparta_e7ab2007f8();G=f'{conf_settings.SERVER_CF}/"/reset-ai-plan-api-key';B=requests.post(G,json={_J:F,'new_api_key_ai_plan':E,'reset_api_key_ai_plan':C},allow_redirects=_C);print(f"res status code: {B.status_code}");print(B.text)
					if B.status_code==200:
						H=json.loads(B.text)
						if H[_A]==1:A.api_key_ai_plan=E;A.save();return{_A:1}
	return{_A:-1,_I:'Could not generate a new API key'}