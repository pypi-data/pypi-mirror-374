_E='title_override'
_D='dataframe_llm_obj'
_C='has_write_rights'
_B='res'
_A='dataframe_llm_id'
import os,sys,requests,subprocess,socket
from datetime import datetime
import pytz
UTC=pytz.utc
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
from project.models import DataFrameLLM
from project.sparta_440f6a201b.sparta_561d9f653d.qube_55a93bcbe3 import LLMLauncher
from project.sparta_440f6a201b.sparta_561d9f653d.qube_35ffe3dcea import sparta_e97782dba3
def sparta_d85b1ec19a(json_data,user_obj):
	H=json_data['dataframe_slug'];D=DataFrameLLM.objects.filter(user=user_obj,dataframe_model__slug=H,is_delete=False).order_by('-last_update').all();E=[]
	if D.count()>0:
		for A in D:
			F=A.initial_prompt;G=A.llm_one_liner;B=A.title_override;C=F
			if B is not None:C=B
			elif G is not None:C=B
			E.append({'initial_prompt':F,'llm_one_liner':G,_E:B,'title_to_display':C,_A:A.dataframe_llm_id})
	return{_B:1,'dataframe_llm_history':E}
def sparta_58a5729e6e(dataframe_llm_id,user_obj):
	A=DataFrameLLM.objects.filter(dataframe_llm_id=dataframe_llm_id,user=user_obj);C=A.count()>0;B=None
	if C:B=A[0]
	return{_C:A.count()>0,_D:B}
def sparta_818624229d(json_data,user_obj):
	A=json_data;D=A[_A];B=sparta_58a5729e6e(D,user_obj)
	if B[_C]:C=B[_D];C.title_override=A[_E];C.save()
	return{_B:1}
def sparta_f71484cc3f(json_data,user_obj):
	B=json_data[_A];A=sparta_58a5729e6e(B,user_obj)
	if A[_C]:C=A[_D]
	return{_B:1}
def sparta_1e5fded66d(json_data,user_obj):
	C=json_data[_A];A=sparta_58a5729e6e(C,user_obj)
	if A[_C]:B=A[_D];B.is_delete=True;B.save()
	return{_B:1}