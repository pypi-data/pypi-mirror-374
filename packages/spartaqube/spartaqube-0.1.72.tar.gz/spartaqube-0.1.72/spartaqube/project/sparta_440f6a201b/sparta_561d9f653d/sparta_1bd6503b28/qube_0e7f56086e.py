_A=None
import os,asyncio,json
from urllib.parse import urlparse
from project.sparta_440f6a201b.sparta_561d9f653d.sparta_1bd6503b28.qube_9eb418fd82 import OpenAIGeneratorLLM
from project.models import LLMCredentials
from asgiref.sync import sync_to_async
def sparta_5bcf8d4aba(host):
	A=host;B=urlparse(A)
	if not B.scheme:return f"http://{A}"
	return A
class NotebookLLMClientOpenAI:
	def __init__(A):0
	async def create(C,system_prompt,user_obj):
		A=_A;B=await sync_to_async(lambda:list(LLMCredentials.objects.filter(user=user_obj)),thread_sensitive=False)()
		if len(B)>0:D=B[0];A=D.openai_key
		if A is _A:A=os.environ.get('OPENAI_API_KEY',_A)
		C.generator=OpenAIGeneratorLLM(system_prompt,A)
	async def stream_completion(A,user_prompt,workspace_variables,temperature=.2,max_tokens=512,model=_A):
		async for B in A.generator.stream_llm_python_code(user_prompt,workspace_variables,temperature=temperature,max_tokens=max_tokens,model=model):yield B
	def clear_chatbot(A):A.generator.clear_chatbot()
	def get_conversation(A):return{'conversation':A.generator.get_conversation(),'model':'openai'}
	def restore_conversation(A,conversation_list):A.generator.restore_conversation(conversation_list)