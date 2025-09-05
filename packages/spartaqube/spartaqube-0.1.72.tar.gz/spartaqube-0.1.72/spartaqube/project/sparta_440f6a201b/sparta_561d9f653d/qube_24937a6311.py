_C='openai'
_B='notebook-kernel'
_A=None
import os,pandas as pd
from asgiref.sync import sync_to_async
from project.models import LLMCredentials
from project.sparta_440f6a201b.sparta_561d9f653d.qube_35ffe3dcea import sparta_e97782dba3
from project.sparta_440f6a201b.sparta_561d9f653d.sparta_1bd6503b28.qube_9eb418fd82 import OpenAIGeneratorLLM
from project.sparta_440f6a201b.sparta_561d9f653d.sparta_d05362a376.qube_1c94c35793 import ClaudeGeneratorLLM
class LLMClientCloud:
	def __init__(A,system_prompt,user_obj,mode=_B):A.user_obj=user_obj;A.system_prompt=system_prompt;A.mode=mode;A.cloud_llm_type=_A;A.generator=_A
	async def get_llm_credential_obj(B):
		A=await sync_to_async(lambda:list(LLMCredentials.objects.filter(user=B.user_obj)),thread_sensitive=False)()
		if len(A)>0:C=A[0];return C
	async def get_api_key_openai(C):
		A=_A;B=await C.get_llm_credential_obj()
		if B is not _A:A=B.openai_key
		if A is _A:A=os.environ.get('OPENAI_API_KEY',_A)
		return A
	async def get_api_key_anthropic(C):
		A=_A;B=await C.get_llm_credential_obj()
		if B is not _A:A=B.anthropic_key
		if A is _A:A=os.environ.get('ANTHROPIC_API_KEY',_A)
		return A
	async def get_api_key_gemini(C):
		A=_A;B=await C.get_llm_credential_obj()
		if B is not _A:A=B.gemini_key
		if A is _A:A=os.environ.get('GOOGLE_API_KEY',_A)
		return A
	async def set_generator(A,cloud_model,mode=_B):
		A.cloud_llm_type=sparta_e97782dba3()[cloud_model]
		if A.cloud_llm_type==_C:B=await A.get_api_key_openai();A.generator=OpenAIGeneratorLLM(A.system_prompt,B,A.user_obj,mode=mode)
		elif A.cloud_llm_type=='anthropic':B=await A.get_api_key_anthropic();A.generator=ClaudeGeneratorLLM(A.system_prompt,B,A.user_obj,mode=mode)
	def set_dataframe(A,dataframe):A.generator.set_dataframe(dataframe)
	def set_llm_settings(A,auto_execute,self_correcting,max_retry):A.generator.set_dataframe(auto_execute=auto_execute,self_correcting=self_correcting,max_retry=max_retry)
	async def init_ipython_kernel(A):print('Init python kernel');await A.generator.init_ipython_kernel();print('python kernel is init')
	async def switch_model_type(A,cloud_model):
		B=cloud_model;C=sparta_e97782dba3()[B]
		if A.cloud_llm_type!=C:A.cloud_llm_type=C;await A.set_generator(B)
	async def stream_completion(A,user_prompt,workspace_variables=_A,temperature=.2,max_tokens=512,model=_A):
		F=model;E=max_tokens;D=temperature;C=user_prompt
		if A.mode==_B:
			async for B in A.generator.stream_llm_python_code(C,workspace_variables,temperature=D,max_tokens=E,model=F):yield B
		elif A.mode=='dataframe':
			async for B in A.generator.stream_llm_coding_capabilities(C,temperature=D,max_tokens=E,model=F):yield B
	async def ipython_exec_code(A,code):
		async for B in A.generator.ipython_exec_code(code):yield B
	async def save_llm_history(A,dataframe_slug,response_list_frontend,venv=_A,llm_settings_dict=_A):return await A.generator.save_llm_history(dataframe_slug=dataframe_slug,response_list_frontend=response_list_frontend,venv=venv,llm_settings_dict=llm_settings_dict)
	async def restore_llm_chat(A,dataframe_llm_id):return await A.generator.restore_llm_chat(dataframe_llm_id=dataframe_llm_id)
	async def clear_chatbot(A):
		if A.generator is not _A:await A.generator.clear_chatbot()
	def get_conversation(A):return{'conversation':A.generator.get_conversation(),'model':_C}
	def restore_conversation(A,conversation_list):A.generator.restore_conversation(conversation_list)
	async def activate_venv(A,venv_name):await A.generator.activate_venv(venv_name)
	async def deactivate_venv(A):await A.generator.deactivate_venv()