_L='bPublicUser'
_K='notebook_name'
_J='notebook_id'
_I='b_require_password'
_H='notebook_obj'
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
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_0972eac5cf import qube_57c026f3db as qube_57c026f3db
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_cf9da279c3(request):
	B=request;A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_D]=13;E=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(E);A[_E]=_A
	def F(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	G=sparta_a4e746f060();C=os.path.join(G,'notebook');F(C);A[_F]=C;D=_A
	if B.headers.get('HX-Request')=='true':D=_G
	A['bFullRender']=D;return render(B,'dist/project/notebook/notebook.html',A)
@csrf_exempt
def sparta_cfb785a97d(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=_G
	if C is _B:D=_A
	else:
		E=qube_57c026f3db.sparta_7dacc199b9(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_cf9da279c3(B)
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_D]=12;H=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(H);A[_E]=_A;F=E[_H];A[_F]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.notebook_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookRun.html',A)
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_155dabd20a(request,id):
	B=request
	if id is _B:C=B.GET.get('id')
	else:C=id
	D=_G
	if C is _B:D=_A
	else:
		E=qube_57c026f3db.sparta_7dacc199b9(C,B.user);G=E[_C]
		if G==-1:D=_A
	if D:return sparta_cf9da279c3(B)
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_D]=12;H=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(H);A[_E]=_A;F=E[_H];A[_F]=F.project_path;A[_I]=0 if E[_C]==1 else 1;A[_J]=F.notebook_id;A[_K]=F.name;A[_L]=B.user.is_anonymous;return render(B,'dist/project/notebook/notebookDetached.html',A)