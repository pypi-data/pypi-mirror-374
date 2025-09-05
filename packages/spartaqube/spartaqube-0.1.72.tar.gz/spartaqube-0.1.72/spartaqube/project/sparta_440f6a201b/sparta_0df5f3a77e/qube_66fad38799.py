_E='subscription_key'
_D=True
_C='errorMsg'
_B=False
_A='res'
import requests
from datetime import datetime
from django.conf import settings as conf_settings
from project.models import AIPlan,AIPlanSubscription,CloudPlan
def sparta_fe7768e55b(json_data,user_obj):
	F='captcha';B=json_data;A=user_obj.email;G='Contact US - New Message';C=B['message'];D=f"<h3>Message:{C}</h3>";D+=f"<hr><div>Sender:{A}</div>";H=B[F];I=f"*ContactUS Message:* {C}\n*From Sender:* {A}\n",;E=requests.post(f"{conf_settings.SERVER_CF}/contact-us",json={'recipient':A,'subject':G,'email_msg':D,'slack_msg':I,F:H},allow_redirects=_B)
	try:
		if E.status_code==400:return{_A:-1,_C:E.text}
		return{_A:1}
	except Exception as J:return{_A:-1,_C:str(J)}
def sparta_c666e3ad57(json_data,user_obj):from project.sparta_440f6a201b.sparta_0416b94add import qube_aac7a3218f as A;B=json_data['cloud_id'];C=A.sparta_ba7bc02e18(B);return C
def sparta_888840f8cb(json_data,user_obj):
	M='%Y-%m-%d';B=user_obj;C=_B;D=[];E=AIPlanSubscription.objects.filter(ai_plan__user=B,status='active')
	if E.count()>0:
		C=_D
		for A in E:D.append({_E:A.subscription_key,'billed_frequency':A.billed_frequency,'date_created':datetime.strftime(A.date_created,M),'last_update':datetime.strftime(A.last_update,M)})
	F='';G='';H=AIPlan.objects.filter(user=B)
	if H.count()>0:I=H[0];G=I.api_key_ai_plan;F=I.existing_api_key_ai_plan
	J=_B;K=[];L=CloudPlan.objects.filter(user=B,is_destroyed=_B,is_verified=_D)
	if len(L)>0:
		J=_D
		for N in L:K.append(N.ipv4)
	return{_A:1,'has_ai_plan':C,'has_cloud_plan':J,'cloud_plans_ip':K,'ai_plan_subs':D,'ai_api_key':G,'existing_api_key_ai_plan':F}
def sparta_1fac2407c0(json_data,user_obj):
	B=user_obj;C=json_data[_E];D=AIPlan.objects.filter(user=B)
	if D.count()>0:
		I=D[0];J=I.api_key_ai_plan;E=f"{conf_settings.SERVER_CF}/unsubscribe-ai-test";F=_B
		if not conf_settings.IS_DEV:F=_D
		if F:E=f"{conf_settings.SERVER_CF}/unsubscribe-ai"
		A=requests.post(E,json={_E:C,'api_key':J},allow_redirects=_B);print('response');print(A);print(A.status_code);print(A.text)
		if A.status_code==200:
			G=AIPlanSubscription.objects.filter(ai_plan__user=B,subscription_key=C)
			if G.count()>0:H=G[0];H.status='revoked';H.save()
			return{_A:1}
		else:
			try:return{_A:-1,_C:str(A.text)}
			except:pass
	return{_A:-1,_C:'An unexpected error occurred, could not process the query'}