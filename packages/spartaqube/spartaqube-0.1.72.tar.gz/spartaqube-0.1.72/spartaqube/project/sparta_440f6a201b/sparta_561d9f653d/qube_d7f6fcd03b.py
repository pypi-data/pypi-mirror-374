_N='assistant'
_M='choices'
_L='[DONE]'
_K='stream'
_J='max_tokens'
_I='temperature'
_H='messages'
_G='is_partial'
_F='mode'
_E='data: '
_D=True
_C='role'
_B=None
_A='content'
import httpx,asyncio,json
from urllib.parse import urlparse
def sparta_5bcf8d4aba(host):
	A=host;B=urlparse(A)
	if not B.scheme:return f"http://{A}"
	return A
class NotebookLLMClient:
	def __init__(A,port=47832,host='http://localhost',system_prompt_reasoning=_B,system_prompt_coding=_B):B='system';A.host=host;A.port=port;C=sparta_5bcf8d4aba(f"{A.host}:{A.port}");A.url=f"{C}/v1/chat/completions";A.system_prompt_reasoning=system_prompt_reasoning or'';A.last_reasoning_output=_B;A.messages_reasoning=[{_C:B,_A:A.system_prompt_reasoning}];A.system_prompt_coding=system_prompt_coding or'';A.last_coding_output=_B;A.messages_coding=[{_C:B,_A:A.system_prompt_coding}]
	async def stream_completion(A,user_prompt,temperature=.2,max_tokens=512):
		D=max_tokens;C=temperature;B=user_prompt
		async for E in A.stream_completion_reasoning(B,coding_prompt_output=A.last_coding_output,temperature=C,max_tokens=D):yield E
		async for F in A.stream_completion_coding(B,A.last_reasoning_output,temperature=C,max_tokens=D):yield F
	async def stream_completion_reasoning(A,user_prompt,coding_prompt_output=_B,temperature=.2,max_tokens=512):
		I='reasoning';F=coding_prompt_output;B=user_prompt
		if F is _B:B=f"\nUser question: {B}\n"
		else:B=f"""
User question: {B}
Coding context to improve:

 
{F}
"""
		A.messages_reasoning.append({_C:'user',_A:B});J={_H:A.messages_reasoning,_I:temperature,_J:max_tokens,_K:_D};print('self.messages_reasoning');print(A.messages_reasoning);K='';G=''
		async with httpx.AsyncClient(timeout=_B)as L:
			async with L.stream('POST',A.url,json=J)as C:
				if C.status_code!=200:print(f"Error: {C.status_code}");print(await C.aread());return
				async for D in C.aiter_lines():
					if not D.strip():continue
					print(f"debug line: {D}")
					if D.startswith(_E):
						H=D[len(_E):].strip()
						if H==_L:break
						M=json.loads(H);E=M.get(_M,[{}])[0].get('delta',{}).get(_A,'')
						if not E:continue
						K+=E;G+=E;yield{_F:I,_G:_D,_A:E}
		N=G.strip();A.last_reasoning_output=N;yield{_F:I,_G:False,_A:A.last_reasoning_output};A.messages_reasoning.append({_C:_N,_A:A.last_reasoning_output})
	async def stream_completion_coding(A,user_prompt,reasoning_prompt_output,temperature=.2,max_tokens=512):
		I='coding';F=reasoning_prompt_output;B=user_prompt
		if A.last_coding_output is _B:B=f"""
User question: {B}
Reasoning context to help:

 
{F}
"""
		else:B=f"""
User question: {B}
New Reasoning context to help:

 
{F}
Previous code to improve:


{A.last_coding_output}
"""
		A.messages_coding.append({_C:'user',_A:B});J={_H:A.messages_coding,_I:temperature,_J:max_tokens,_K:_D};print('self.messages_coding');print(A.messages_coding);K='';G=''
		async with httpx.AsyncClient(timeout=_B)as L:
			async with L.stream('POST',A.url,json=J)as C:
				if C.status_code!=200:print(f"Error: {C.status_code}");print(await C.aread());return
				async for D in C.aiter_lines():
					if not D.strip():continue
					print(f"debug line: {D}")
					if D.startswith(_E):
						H=D[len(_E):].strip()
						if H==_L:break
						M=json.loads(H);E=M.get(_M,[{}])[0].get('delta',{}).get(_A,'')
						if not E:continue
						K+=E;G+=E;yield{_F:I,_G:_D,_A:E}
		A.last_coding_output=G.strip();yield{_F:I,_G:False,_A:A.last_coding_output};A.messages_coding.append({_C:_N,_A:A.last_coding_output})