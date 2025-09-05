_l='self_correcting'
_k='code_results'
_j='output'
_i='chart_type'
_h='params'
_g='choices'
_f='executing_code'
_e='terminate'
_d='assistant'
_c='prompt_params'
_b='stream'
_a='fingerprint'
_Z='messages'
_Y='system_prompt'
_X='is_local_system_prompt'
_W='system'
_V='buffer'
_U='current_tag'
_T='yield'
_S='```'
_R='responding_text'
_Q='```python'
_P='errorMsg'
_O='b_require_api'
_N='-1'
_M='user'
_L='max_tokens'
_K='temperature'
_J='model'
_I='generating_code'
_H='is_partial'
_G='res'
_F='role'
_E=False
_D=True
_C='mode'
_B='content'
_A=None
import json,cloudpickle,base64,os,io,uuid,re,requests,tinykernel,pandas as pd
from asgiref.sync import sync_to_async
from typing import Optional,Generator,AsyncGenerator
from django.conf import settings as conf_settings
from project.sparta_440f6a201b.sparta_561d9f653d.qube_35ffe3dcea import sparta_09baf7c669,sparta_3a0befdabf
from project.models import DataFrameLLM,DataFrameModel,AIPlan
from datetime import datetime
import pytz
UTC=pytz.utc
class MockDelta:
	def __init__(A,content):A.content=content
class MockChoice:
	def __init__(A,delta):A.delta=delta
class MockChunk:
	def __init__(A,content):A.choices=[MockChoice(MockDelta(content))]
class WorkerStreamWrapper:
	def __init__(A,url,payload):B=payload;A.url=url;A.payload=B;A.response=requests.post(url,stream=_D,json=B);A.lines=A.response.iter_lines();A._validate_response()
	def _validate_response(A):
		if A.response.status_code!=200:raise RuntimeError(f"Worker stream failed: {A.response.status_code} - {A.response.text}")
	def __iter__(A):return A
	def __next__(D):
		C='data: '
		while _D:
			A=next(D.lines).decode('utf-8').strip()
			if not A or not A.startswith(C):continue
			B=A[len(C):].strip()
			if B=='[DONE]':raise StopIteration
			try:E=json.loads(B);F=E.get(_g,[{}])[0].get('delta',{}).get(_B,'');return MockChunk(F)
			except Exception as G:print('Failed to parse chunk:',G);continue
def sparta_0f95ff768b(url,payload):
	class B:
		def __init__(A,json_response):A.choices=[A.Choice(B)for B in json_response.get(_g,[])]
		class Choice:
			def __init__(A,choice_dict):A.message=A.Message(choice_dict.get('message',{}))
			class Message:
				def __init__(A,msg_dict):A.content=msg_dict.get(_B,'')
	A=requests.post(url,json=payload)
	if A.status_code!=200:raise Exception(f"LLM request failed: {A.status_code} - {A.text}")
	C=B(A.json());return C
def sparta_f21e68f7fb():from project.sparta_440f6a201b.sparta_561d9f653d.qube_e734fdd69c import sparta_e72f323dbf as A;return A()
class LLMGenerator:
	def __init__(A,system_prompt,api_key,user_obj,model='gpt-3.5-turbo',mode='notebook-kernel'):B=f"{conf_settings.SERVER_CF}/";A.streaming_llm_url=os.path.join(B,'stream-llm');A.no_stream_llm_url=os.path.join(B,'nostream-llm');A.cf_stream=_D;A.dataframe_llm_id=_A;A.is_local_system_prompt=_E;A.api_key=api_key;A.system_prompt=system_prompt;A.model=model;A.mode=mode;A.user_obj=user_obj;A.is_trial_mode=_A;A.api_key_ai_plan=_A;A.self_correcting=_D;A.max_retry=5;A.ini_msg=[{_F:_W,_B:A.system_prompt}];A.messages=A.ini_msg.copy();A.ipython_kernel=_A;A.tiny_kernel_obj=_A;A.llm_summarizer_generator=_A;A.llm_generator_spartaqube_api=_A
	def set_llm_settings(A,self_correcting,max_retry):A.self_correcting=self_correcting;A.max_retry=max_retry
	async def fetch_is_trial(B):
		A=AIPlan.objects.filter(user=B.user_obj);C=await sync_to_async(A.count)()
		if C>0:
			D=await sync_to_async(lambda:A.first())()
			if D.is_api_plan_verified:return _E
		return _D
	async def fetch_ai_plan_api_key(D):
		B=AIPlan.objects.filter(user=D.user_obj);E=await sync_to_async(B.count)()
		if E>0:
			C=await sync_to_async(lambda:B.first())();A=C.existing_api_key_ai_plan
			if A is not _A:
				if len(A)>0:return A
			return C.api_key_ai_plan
		return''
	async def get_is_trial_mode(A):
		if A.is_trial_mode is _A:A.is_trial_mode=await A.fetch_is_trial()
		return A.is_trial_mode
	async def get_ai_plan_api_key(A):
		if A.api_key_ai_plan is _A:A.api_key_ai_plan=await A.fetch_ai_plan_api_key()
		return A.api_key_ai_plan
	async def get_payload_params(A):return{'is_trial':await A.get_is_trial_mode(),'api_key_ai_plan':await A.get_ai_plan_api_key()}
	async def stream_spartaqube_api_context(A,prompt,temperature=.7,max_tokens=512,model=_A):
		F=prompt;E=model;D=max_tokens;C=temperature
		if E is not _A:
			if E in A.available_models:A.model=E
		print('LLM SPARTAQUBE API CONTEXT RAG: user prompt query:');print(F);A.messages.append({_F:_M,_B:F});print('MESSAGE DISCUSSION RAG LENGTH:');print(len(A.messages))
		try:
			if A.cf_stream:from project.sparta_440f6a201b.sparta_ceff546bba.qube_a44c916988 import sparta_8922cae1b3 as I;G={_X:A.is_local_system_prompt,_Y:{_C:'spartaqube_api_context',_h:{'available_components_system_prompt':json.dumps(I())}},_J:A.model,_Z:A.messages,_K:C,_L:D,_a:sparta_f21e68f7fb(),_b:_E};G.update(await A.get_payload_params());H=sparta_0f95ff768b(A.no_stream_llm_url,G)
			else:H=A.client.chat.completions.create(model=A.model,messages=A.messages,temperature=C,max_tokens=D,stream=_E)
			B=str(H.choices[0].message.content);J={_J:A.model,_K:C,_L:D};A.messages.append({_F:_d,_B:B,_c:J})
			def K(output):
				C='`';B=output
				if not isinstance(B,str):B=str(B)
				A=B.strip();A=re.sub('[^\\w\\-]','',A)
				for D in[C,'"',"'",'*',C,' ']:A=A.replace(D,'')
				if A==_N:return _N
				for D in[C,'"',"'",'-','*',C,' ']:A=A.replace(D,'')
				return A
			B=K(B);print(f"chart_type found >> {B}")
			if B==_N:return{_G:1,_O:_E}
			else:return{_G:1,_O:_D,_i:B}
		except Exception as L:return{_G:-1,_O:_E,_P:str(L)}
	def handle_stream_chunk_notebook(J,delta,buffer,current_tag=_A):
		D=delta;B=current_tag;A=buffer;C=_A;A+=D;print(f"current_tag > {B}")
		if B is _A:
			if _Q in A:print('DEBUG DEBUG DEBUG buffer');print(A);B=_I;F=A.split(_Q,1);G=F[0];A=F[1];C={_C:_R,_B:G,_H:_E}
			else:C={_C:_R,_B:D,_H:_D}
		elif B==_I:
			if _S in A:E,H=A.split(_S,1);E=E.strip();I=E;C={_C:_I,_B:I,_H:_E};A=H;B=_A
			else:C={_C:_I,_B:D,_H:_D}
		return{_T:C,_U:B,_V:A}
	async def stream_llm_python_code(A,prompt,workspace_variables,temperature=.7,max_tokens=512,model=_A):
		G=model;F=max_tokens;E=temperature;D=workspace_variables;B=prompt;U=B
		if G is not _A:
			if G in A.available_models:A.model=G
		if D is not _A:
			if len(D)>0:B=f"{generate_workspace_variable_context(D)}\n\n{B}"
		print('LLM PYTHON CODE: user prompt query:');print(B)
		if A.is_local_system_prompt:
			try:from project.sparta_440f6a201b.sparta_561d9f653d.sq_prompt import get_notebook_system_prompt_notebook_cloud as Q;R=Q();A.messages[0]={_F:_W,_B:R}
			except:pass
		A.messages.append({_F:_M,_B:B})
		try:
			if A.cf_stream:L={_X:A.is_local_system_prompt,_Y:{_C:'notebook_system_prompt'},_J:A.model,_Z:A.messages,_K:E,_L:F,_a:sparta_f21e68f7fb(),_b:_D};L.update(await A.get_payload_params());M=WorkerStreamWrapper(url=A.streaming_llm_url,payload=L)
			else:M=A.client.chat.completions.create(model=A.model,messages=A.messages,temperature=E,max_tokens=F,stream=_D)
			C='';N='';H=_A;O=_A;print('Iterating chunk over stream')
			for S in M:
				I=S.choices[0].delta.content or''
				if I is not _A:
					C+=I;J=A.handle_stream_chunk_notebook(I,N,H);K=J[_T]
					if K is not _A:O=K;yield K
					N=J[_V];H=J[_U]
			if H is _A:yield{_C:_R,_B:C,_H:_E}
			yield{_C:_e};print('Final last_yield_dict');print(O);print('Last content');print(C)
			if C!=_N:T={_J:A.model,_K:E,_L:F};A.messages.append({_F:_d,_B:C,_c:T})
		except Exception as P:print(f"An error occurred with msg: {str(P)}");raise Exception(f"Streaming error (OpenAI v1+): {str(P)}")
	def set_dataframe(A,dataframe):A.dataframe=dataframe
	async def init_ipython_kernel(A):
		from project.sparta_440f6a201b.sparta_aac43fa003.qube_2c6fbcb282 import IPythonKernel as B;from project.sparta_440f6a201b.sparta_bb5bf030e1.qube_203378cc3e import get_api_key_async as C
		if A.ipython_kernel is _A:D=await C(A.user_obj);A.ipython_kernel=B(D);await A.ipython_kernel.initialize();await A.ipython_kernel.load_spartaqube_api()
	def handle_stream_chunk_coding_capabilities(G,delta,buffer,current_tag=_A):
		D=delta;B=current_tag;A=buffer;C=_A;A+=D
		if B is _A:
			if _Q in A:B=_I;A=A.split(_Q,1)[1]
			else:C={_C:_R,_B:D,_H:_D}
		elif B==_I:
			if _S in A:E,F=A.split(_S,1);E=E.strip();C={_C:_f,_B:E,_H:_E};A=F;B=_A
			else:C={_C:_I,_B:D,_H:_D}
		return{_T:C,_U:B,_V:A}
	async def stream_llm_coding_capabilities(A,prompt,temperature=.7,max_tokens=512,model=_A,retry=0):
		M=retry;L=prompt;D=max_tokens;C=temperature
		if A.tiny_kernel_obj is _A:A.tiny_kernel_obj=tinykernel.TinyKernel();W=f"\nimport pandas as pd\nimport numpy as np\nimport sys, os\n";await A.ipython_kernel.execute(W);await A.ipython_kernel.set_workspace_variables({'df':A.dataframe})
		if A.dataframe_llm_id is _A:A.dataframe_llm_id=str(uuid.uuid4());yield{_C:'setter_dataframe_llm_id','dataframe_llm_id':A.dataframe_llm_id}
		G=await A.spartaqube_api_context_rag(L);E=_A;H=_A
		if G[_G]==1:
			if G[_O]:
				E=G[_i];from project.sparta_440f6a201b.sparta_ceff546bba.qube_a44c916988 import sparta_3f5006b529 as X;Y=X();H=Y[E]
				if A.is_local_system_prompt:
					try:from project.sparta_440f6a201b.sparta_561d9f653d.sq_prompt import get_system_prompt_coding_agent_dataframe as Z;a=Z(A.dataframe,E,H);A.messages[0]={_F:_W,_B:a}
					except:pass
		A.messages.append({_F:_M,_B:L})
		try:
			if A.cf_stream:N={_X:A.is_local_system_prompt,_Y:{_C:'dataframe_system_prompt',_h:{'df_schema':A.dataframe.dtypes.astype(str).to_dict(),'df_sample_rows':A.dataframe.head(5).to_markdown(),'df_summary':A.dataframe.describe().to_markdown(),'spartaqube_chart_type':E,'spartaqube_options_dict':H}},_J:A.model,_Z:A.messages,_K:C,_L:D,_a:sparta_f21e68f7fb(),_b:_D};N.update(await A.get_payload_params());O=WorkerStreamWrapper(url=A.streaming_llm_url,payload=N)
			else:O=A.client.chat.completions.create(model=A.model,messages=A.messages,temperature=C,max_tokens=D,stream=_D)
			P='';Q='';R=_A;h=_A;F=_A
			for b in O:
				I=b.choices[0].delta.content or''
				if I is not _A:
					P+=I;J=A.handle_stream_chunk_coding_capabilities(I,Q,R);B=J[_T];Q=J[_V];R=J[_U]
					if B is not _A:
						if B[_C]==_f:S=B.copy();S[_B]='';yield S
						else:yield B
						if B[_C]==_f:
							from project.sparta_440f6a201b.sparta_aac43fa003.qube_62114c67e6 import sparta_443043d676;T=B[_B];print('Executing code into ipython kernel:');print(T);await A.ipython_kernel.execute(T);c=A.ipython_kernel.get_output_queue();K=A.ipython_kernel.get_error_queue()
							if len(K)>0:F=K[0]
							yield{_C:_k,_H:_D,_j:c,'error':K};A.ipython_kernel.clear_output_queue();A.ipython_kernel.clear_error_queue()
			d={_J:A.model,_K:C,_L:D};A.messages.append({_F:_d,_B:P,_c:d});U=_E
			if A.self_correcting:
				if F is not _A:
					if M<A.max_retry:U=_D
			if U:
				print('error_for_self_correction_dict');print(F);e=f"\nGetting the following error: {F[_P]}\n\nPlease fix it\n";yield{_C:_l}
				async for f in A.stream_llm_coding_capabilities(prompt=e,temperature=C,max_tokens=D,model=model,retry=M+1):yield f
			else:yield{_G:1,_C:_e}
		except Exception as V:print(f"Error exception llm capabilities: {str(V)}");import traceback as g;print(g.format_exc());yield{_G:-1,_P:str(V)}
	async def ipython_exec_code(A,code):
		if A.ipython_kernel is not _A:await A.ipython_kernel.execute(code);B=A.ipython_kernel.get_output_queue();C=A.ipython_kernel.get_error_queue();yield{_C:_k,_j:B,'error':C};A.ipython_kernel.clear_output_queue();A.ipython_kernel.clear_error_queue();yield{_C:_e}
	async def save_llm_history(A,dataframe_slug,response_list_frontend,venv=_A,llm_settings_dict=_A):
		E=response_list_frontend;C=llm_settings_dict;D=datetime.now().astimezone(UTC);F=DataFrameModel.objects.filter(slug=dataframe_slug).all();K=await sync_to_async(F.count)()
		if K>0:
			G=await sync_to_async(lambda:F.first())();print('len(self.messages)');print(len(A.messages))
			if len(A.messages)>1:
				H=A.messages[1]
				if H[_F]==_M:
					L,N=await A.ipython_kernel.cloudpickle_kernel_variables();M=H[_B];I=await sync_to_async(lambda:list(DataFrameLLM.objects.filter(dataframe_llm_id=A.dataframe_llm_id,user=A.user_obj)))();J=base64.b64encode(cloudpickle.dumps(L))
					if C is not _A:A.self_correcting=C.get('bSelfCorrecting',_D);A.max_retry=C.get('maxRetry',5)
					if len(I)==0:await sync_to_async(DataFrameLLM.objects.create)(dataframe_llm_id=A.dataframe_llm_id,dataframe_model=G,initial_prompt=M,venv=venv,self_correcting=A.self_correcting,max_retry=A.max_retry,response_list_frontend=json.dumps(E),llm_conversation_list_backend=json.dumps(A.messages),llm_conversation_spartaqube_api_rag=json.dumps(A.llm_generator_spartaqube_api.messages),kernel_variables=J,date_created=D,last_update=D,user=A.user_obj)
					else:B=I[0];B.dataframe_model=G;B.kernel_variables=J;B.venv=venv;B.self_correcting=A.self_correcting;B.max_retry=A.max_retry;B.response_list_frontend=json.dumps(E);B.llm_conversation_list_backend=json.dumps(A.messages);B.llm_conversation_spartaqube_api_rag=json.dumps(A.llm_generator_spartaqube_api.messages);B.last_update=D;await sync_to_async(B.save)()
		return{_G:1}
	async def restore_llm_chat(B,dataframe_llm_id):
		try:
			D=await sync_to_async(lambda:list(DataFrameLLM.objects.filter(dataframe_llm_id=dataframe_llm_id,user=B.user_obj)))()
			if len(D)>0:
				A=D[0];G=cloudpickle.loads(base64.b64decode(A.kernel_variables))
				for(H,I)in G.items():
					J=io.BytesIO(I)
					try:E=cloudpickle.load(J);await B.ipython_kernel._method_set_workspace_variable(H,E)
					except Exception as F:print(f"Exception restore variable from cloudpickle: {E}")
				C=A.venv
				if C is not _A:
					if len(C)>0:await B.activate_venv(C)
				B.messages=json.loads(A.llm_conversation_list_backend);B.dataframe_llm_id=A.dataframe_llm_id;B.restore_llm_spartaqube_api(json.loads(A.llm_conversation_spartaqube_api_rag));B.set_llm_settings(self_correcting=A.self_correcting,max_retry=A.max_retry);return{_G:1,'response_list_frontend':A.response_list_frontend,'venv':C,'llm_settings_dict':{_l:A.self_correcting,'max_retry':A.max_retry}}
			return{_G:-1}
		except Exception as F:import traceback as K;print(K.format_exc());return{_G:-1,_P:str(F)}
	async def clear_chatbot(A):A.messages=A.ini_msg.copy();A.dataframe_llm_id=_A;A.clear_chatbot_spartaqube_api_rag_context();await A.deactivate_venv()
	def get_conversation(A):return A.messages
	def restore_conversation(A,conversation_list):A.messages=conversation_list
	async def activate_venv(A,venv_name):
		if A.ipython_kernel is not _A:await A.ipython_kernel.activate_venv(venv_name)
	async def deactivate_venv(A):
		if A.ipython_kernel is not _A:await A.ipython_kernel.deactivate_venv()