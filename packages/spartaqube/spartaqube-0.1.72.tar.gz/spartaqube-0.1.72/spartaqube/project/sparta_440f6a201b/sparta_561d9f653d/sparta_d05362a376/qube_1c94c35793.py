_B='claude-3-sonnet-20240229'
_A=None
from anthropic import AsyncAnthropic
from anthropic.types import MessageStreamEvent
from typing import Optional,AsyncGenerator
from project.sparta_440f6a201b.sparta_561d9f653d.qube_ca95e52015 import LLMGenerator
from project.sparta_440f6a201b.sparta_561d9f653d.qube_35ffe3dcea import sparta_09baf7c669,sparta_3a0befdabf
class ClaudeGeneratorLLM(LLMGenerator):
	def __init__(A,system_prompt,api_key,user_obj,model=_B,mode='notebook-kernel'):
		B=api_key;super().__init__(system_prompt,B,user_obj,model,mode);A.available_models=['claude-3-opus-20240229',_B,'claude-3-haiku-20240307']
		if not B:raise ValueError('Anthropic API key is required.')
		A.client=AsyncAnthropic(api_key=B);A.ini_msg=[];A.messages=A.ini_msg.copy()
	def construct_generator(A,system_prompt):A.llm_generator_spartaqube_api=ClaudeGeneratorLLM(system_prompt,api_key=A.api_key,user_obj=A.user_obj,model=A.model,mode='spartaqube-api-context')
	def clear_chatbot_spartaqube_api_rag_context(A):
		if A.is_local_system_prompt:
			try:from project.sparta_440f6a201b.sparta_561d9f653d.sq_prompt import get_spartaqube_api_context_rag as B;C=B()
			except:pass
		A.construct_generator(C)
	async def stream_llm_python_code(A,prompt,workspace_variables,temperature=.7,max_tokens=512,model=_A):
		P='content';O='role';I=max_tokens;H=temperature;D=model;C=workspace_variables;B=prompt
		if D is not _A and D in A.available_models:A.model=D
		if C is not _A:
			if len(C)>0:B=f"{generate_workspace_variable_context(C)}\n\n{B}"
		print('User prompt query:');print(B);A.messages.append({O:'user',P:B});print('self.system_prompt');print(A.system_prompt)
		try:
			Q=await A.client.messages.create(model=A.model,max_tokens=I,system=A.system_prompt,temperature=H,messages=A.messages,stream=True);E='';J=_A
			async for F in Q:
				print('event');print(F);K=getattr(F,'type',_A)
				if K=='message_stop':break
				if K=='content_block_delta':
					R=F.delta.text;G=A.handle_stream_chunk_python_code(R,E,J);L=G['yield']
					if L is not _A:yield L
					E=G['buffer'];J=G['current_tag']
			M=E.strip()
			if M!='-1':S={'model':A.model,'temperature':H,'max_tokens':I};A.messages.append({O:'assistant',P:M,'prompt_params':S})
		except Exception as N:print(f"Error during streaming: {N}");yield{'error':str(N)}
	async def spartaqube_api_context_rag(A,prompt):
		if A.llm_generator_spartaqube_api is _A:B=get_spartaqube_api_context_rag();A.construct_generator(B)
		return await A.llm_generator_spartaqube_api.stream_spartaqube_api_context(prompt)
	def restore_llm_spartaqube_api(A,messages):B=get_spartaqube_api_context_rag();A.construct_generator(B);A.llm_generator_spartaqube_api.messages=messages