_M='bPublicUser'
_L='developer_name'
_K='b_require_password'
_J='developer_obj'
_I='dist/project/homepage/homepage.html'
_H='developer_id'
_G=False
_F='default_project_path'
_E='bCodeMirror'
_D='menuBar'
_C='res'
_B=None
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve
from django.http import FileResponse,Http404
from urllib.parse import unquote
from django.conf import settings as conf_settings
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_9218ccb674 import qube_b7db7762fc as qube_b7db7762fc
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_fd5878592e(request):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_99dd79197b.sparta_6bbe31b6fa(B);return render(B,_I,A)
	qube_b7db7762fc.sparta_d91b24ac9e();A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_D]=12;E=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(E);A[_E]=_A
	def F(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	G=sparta_a4e746f060();C=os.path.join(G,'developer');F(C);A[_F]=C;D=_A
	if B.headers.get('HX-Request')=='true':D=_G
	A['bFullRender']=D;return render(B,'dist/project/developer/developer.html',A)
@csrf_exempt
def sparta_9f614817e1(request,id):
	B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_99dd79197b.sparta_6bbe31b6fa(B);return render(B,_I,A)
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=_G
	if C is _B:D=_A
	else:
		E=qube_b7db7762fc.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_fd5878592e(B)
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_D]=12;H=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(H);A[_E]=_A;F=E[_J];A[_F]=F.project_path;A[_K]=0 if E[_C]==1 else 1;A[_H]=F.developer_id;A[_L]=F.name;A[_M]=B.user.is_anonymous;return render(B,'dist/project/developer/developerRun.html',A)
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_5840a17af6(request,id):
	B=request;print('OPEN DEVELOPER DETACHED')
	if id is _B:C=B.GET.get('id')
	else:C=id
	print(_H);print(C);D=_G
	if C is _B:D=_A
	else:
		E=qube_b7db7762fc.has_developer_access(C,B.user);G=E[_C]
		if G==-1:D=_A
	print('b_redirect_developer_db');print(D)
	if D:return sparta_fd5878592e(B)
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_D]=12;H=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(H);A[_E]=_A;F=E[_J];A[_F]=F.project_path;A[_K]=0 if E[_C]==1 else 1;A[_H]=F.developer_id;A[_L]=F.name;A[_M]=B.user.is_anonymous;return render(B,'dist/project/developer/developerDetached.html',A)
def sparta_4316e873b6(request,project_path,file_name):A=project_path;A=unquote(A);return serve(request,file_name,document_root=A)