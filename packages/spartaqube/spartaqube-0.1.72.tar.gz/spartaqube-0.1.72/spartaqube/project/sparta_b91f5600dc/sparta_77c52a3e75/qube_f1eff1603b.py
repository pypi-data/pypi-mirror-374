_P='Invalid request'
_O='Location'
_N='subscription'
_M='fingerprint'
_L='subscription_key'
_K='frequency'
_J='STRIPE_CF_TEST_ENV'
_I='yearly'
_H='monthly'
_G='is_monthly'
_F='stripe_cf_test_env'
_E='error'
_D='base_url_redirect'
_C='menuBar'
_B=True
_A=False
import json,base64,requests,uuid,hashlib
from django.http import HttpResponseRedirect,HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_561d9f653d.qube_e734fdd69c import sparta_e72f323dbf
from project.models import UserProfile,AIPlan,AIPlanSubscription,CloudPlan
from datetime import datetime
import pytz
UTC=pytz.utc
from spartaqube_app.secrets import sparta_61772791e6
@csrf_exempt
@sparta_b9ac22161e
def sparta_8d36dbee3e(request):C='CAPTCHA_SITEKEY';B=request;A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_C]=-1;D=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(D);A[C]=sparta_61772791e6()[C];return render(B,'dist/project/plans/plans.html',A)
def sparta_e7ab2007f8():A=uuid.uuid4();B=hashlib.sha256(str(A).encode());C=B.hexdigest();return C
def sparta_5ec438df57(user_obj):
	D=user_obj;E=AIPlan.objects.filter(user=D)
	if E.count()>0:
		A=E[0];B=_A
		if A.api_key_ai_plan is None:B=_B
		elif len(A.api_key_ai_plan)==0:B=_B
		if B:A.api_key_ai_plan=sparta_e7ab2007f8()
		C=_A
		if A.reset_api_key_ai_plan is None:C=_B
		elif len(A.reset_api_key_ai_plan)==0:C=_B
		if C:A.reset_api_key_ai_plan=sparta_e7ab2007f8()
		A.save();return A
	else:F=datetime.now().astimezone(UTC);A=AIPlan.objects.create(user=D,api_key_ai_plan=sparta_e7ab2007f8(),reset_api_key_ai_plan=sparta_e7ab2007f8(),last_update=F,date_created=F);return A
@csrf_exempt
@sparta_b9ac22161e
def sparta_64339e09c1(request):
	A=request
	if A.method=='POST':
		J=A.user.email;K=A.POST.get(_G);L=A.POST.get(_D)
		if str(K).lower()=='true':C=_H
		else:C=_I
		try:
			D=sparta_5ec438df57(A.user);M=D.api_key_ai_plan;N=D.reset_api_key_ai_plan;F=sparta_e7ab2007f8();G=datetime.now().astimezone(UTC);AIPlanSubscription.objects.create(ai_plan=D,subscription_key=F,billed_frequency=C,last_update=G,date_created=G);H=f"{conf_settings.SERVER_CF}/create-checkout-session-ai-test";I=_A;E=''
			if not conf_settings.IS_DEV:I=_B
			else:E=sparta_61772791e6()[_J]
			print(_F);print(E)
			if I:H=f"{conf_settings.SERVER_CF}/create-checkout-session-ai"
			B=requests.post(H,json={'email':J,_K:C,'mode':_N,'api_key':M,_L:F,'reset_api_key_ai_plan':N,_M:sparta_e72f323dbf(),_D:L,_F:E},allow_redirects=_A)
			if B.status_code==302:return HttpResponseRedirect(B.headers[_O])
			return JsonResponse({_E:B.text},status=B.status_code)
		except Exception as O:import traceback as P;print(P.format_exc());return JsonResponse({_E:str(O)},status=500)
	return HttpResponse(_P,status=405)
@csrf_exempt
@sparta_b9ac22161e
def sparta_6d916915e6(request):
	A=request;G=A.GET.get(_L);C=AIPlanSubscription.objects.filter(subscription_key=G)
	if C.count()>0:D=C[0];D.status='active';D.save()
	B=qube_99dd79197b.sparta_6bbe31b6fa(A);B[_C]=-1;H=qube_99dd79197b.sparta_29db575fa9(A.user);B.update(H);E=AIPlan.objects.filter(user=A.user)
	if E.count()>0:
		I=E[0];F=I.api_key_ai_plan
		if len(F)>0:B['api_key_ai_plan']=F;return render(A,'dist/project/plans/aiPlansSuccess.html',B)
	return sparta_75d36b41af(A)
@csrf_exempt
@sparta_b9ac22161e
def sparta_75d36b41af(request):A=request;B=qube_99dd79197b.sparta_6bbe31b6fa(A);B[_C]=-1;C=qube_99dd79197b.sparta_29db575fa9(A.user);B.update(C);return render(A,'dist/project/plans/aiPlansCancel.html',B)
@csrf_exempt
@sparta_b9ac22161e
def sparta_98883d3bf8(request):
	A=request
	if A.method=='POST':
		G=A.user.email;H=A.POST.get(_G);I=str(A.POST.get('instanceType'));J={'1':'small','2':'medium','3':'large'}[I];K=A.POST.get(_D)
		if str(H).lower()=='true':C=_H
		else:C=_I
		try:
			L=datetime.now().astimezone(UTC);D=sparta_e7ab2007f8();CloudPlan.objects.create(user=A.user,cloud_key=D,is_verified=_A,date_created=L);E=f"{conf_settings.SERVER_CF}/create-checkout-session-cloud-test";F=_A
			if not conf_settings.IS_DEV:F=_B
			else:M=sparta_61772791e6()[_J]
			if F:E=f"{conf_settings.SERVER_CF}/create-checkout-session-cloud"
			B=requests.post(E,json={'email':G,_K:C,'instance_type':J,'mode':_N,'cloud_key':D,_M:sparta_e72f323dbf(),_D:K,_F:M},allow_redirects=_A)
			if B.status_code==302:return HttpResponseRedirect(B.headers[_O])
			return JsonResponse({_E:B.text},status=B.status_code)
		except Exception as N:import traceback as O;print(O.format_exc());return JsonResponse({_E:str(N)},status=500)
	return HttpResponse(_P,status=405)
@csrf_exempt
@sparta_b9ac22161e
def sparta_131c3ab5f2(request):
	H='subscription_id';D='cloud_id';A=request;print('ENTER cloud_plans_payment_success');print('GET params:');print(A.GET);C=A.GET.get(D);E=A.GET.get(H);print(D);print(C);print(H);print(E);B=qube_99dd79197b.sparta_6bbe31b6fa(A);B[D]=C;B[_C]=-1;I=qube_99dd79197b.sparta_29db575fa9(A.user);B.update(I);F=CloudPlan.objects.filter(user=A.user,cloud_key=C)
	if F.count()>0:G=F[0];G.subscription_id=E;G.save()
	return render(A,'dist/project/plans/cloudPlansSuccess.html',B)
@csrf_exempt
@sparta_b9ac22161e
def sparta_4e0f0f8be2(request):A=request;B=qube_99dd79197b.sparta_6bbe31b6fa(A);B[_C]=-1;C=qube_99dd79197b.sparta_29db575fa9(A.user);B.update(C);return render(A,'dist/project/plans/cloudPlansCancel.html',B)