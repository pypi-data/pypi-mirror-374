_F='bCodeMirror'
_E='menuBar'
_D=False
_C='-1'
_B=True
_A=None
import json,base64
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_aea4c35167 import qube_477699d437 as qube_477699d437
from project.sparta_440f6a201b.sparta_9df2ef9f24 import qube_7fa0ebc7a1 as qube_7fa0ebc7a1
from project.sparta_440f6a201b.sparta_c4f0fc23b4 import qube_8f617e9906 as qube_8f617e9906
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_048d1fb8eb(request):
	B=request;C=B.GET.get('edit')
	if C is _A:C=_C
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_E]=15;E=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(E);A[_F]=_B;A['edit_chart_id']=C;D=_B
	if B.headers.get('HX-Request')=='true':D=_D
	A['bFullRender']=D;return render(B,'dist/project/plot-db/plotDB.html',A)
@csrf_exempt
@sparta_b9ac22161e
def sparta_6e3246bf7f(request,id,api_token_id=_A):
	A=request
	if id is _A:B=A.GET.get('id')
	else:B=id
	return plot_widget_dataframes_func(A,B)
@csrf_exempt
@sparta_b9ac22161e
def sparta_e2b8d01a4f(request,dashboard_id,id,password):
	A=request
	if id is _A:B=A.GET.get('id')
	else:B=id
	C=base64.b64decode(password).decode();print('plot widget dadshboard');return plot_widget_dataframes_func(A,B,dashboard_id=dashboard_id,dashboard_password=C)
def plot_widget_dataframes_func(request,slug,session=_C,dashboard_id=_C,token_permission='',dashboard_password=_A):
	K='token_permission';I=dashboard_id;H=slug;G='res';E=token_permission;D=request;C=_D
	if H is _A:C=_B
	else:
		B=qube_7fa0ebc7a1.sparta_4c904163ac(H,D.user);F=B[G]
		if F==-1:C=_B
	if C:
		if I!=_C:
			B=qube_8f617e9906.has_dataframe_access(I,H,D.user,dashboard_password);F=B[G]
			if F==1:E=B[K];C=_D
	if C:
		if len(E)>0:
			B=qube_7fa0ebc7a1.sparta_e45fd842d1(E);F=B[G]
			if F==1:C=_D
	if C:return sparta_048d1fb8eb(D)
	A=qube_99dd79197b.sparta_6bbe31b6fa(D);A[_E]=15;L=qube_99dd79197b.sparta_29db575fa9(D.user);A.update(L);A[_F]=_B;J=B['dataframe_model_obj'];A['b_require_password']=0 if B[G]==1 else 1;A['slug']=J.slug;A['dataframe_model_name']=J.table_name;A['session']=str(session);A['is_dashboard_widget']=1 if I!=_C else 0;A['is_token']=1 if len(E)>0 else 0;A[K]=str(E);return render(D,'dist/project/dataframes/dataframes.html',A)
@csrf_exempt
@sparta_b9ac22161e
def sparta_dde91e7951(request,id,api_token_id=_A):
	A=request
	if id is _A:B=A.GET.get('id')
	else:B=id
	return plot_widget_dataframes_func(A,B)
@csrf_exempt
def sparta_0ce8bf553a(request,token):return plot_widget_dataframes_func(request,slug=_A,token_permission=token)
@csrf_exempt
@sparta_b9ac22161e
def sparta_3648b291f6(request):C='name';B=request;A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_E]=7;D=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(D);A[_F]=_B;A['serialized_data']=B.POST.get('data');A[C]=B.POST.get(C);return render(B,'dist/project/dataframes/plotDataFramesGUI.html',A)