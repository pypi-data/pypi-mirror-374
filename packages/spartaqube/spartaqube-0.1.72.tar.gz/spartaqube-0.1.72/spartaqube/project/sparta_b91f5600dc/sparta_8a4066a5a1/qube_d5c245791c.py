_D='bFullRender'
_C='bCodeMirror'
_B='menuBar'
_A=True
import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_aea4c35167 import qube_477699d437 as qube_477699d437
from project.sparta_440f6a201b.sparta_c4f0fc23b4 import qube_8f617e9906 as qube_8f617e9906
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_6f644e6cf4(request):
	B=request;C=B.GET.get('edit')
	if C is None:C='-1'
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_B]=9;F=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(F);A[_C]=_A;A['edit_chart_id']=C
	def G(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=_A)
	H=sparta_a4e746f060();D=os.path.join(H,'dashboard');G(D);A['default_project_path']=D;E=_A
	if B.headers.get('HX-Request')=='true':E=False
	A[_D]=E;return render(B,'dist/project/dashboard/dashboard.html',A)
@csrf_exempt
def sparta_4f0a3d34b6(request,id):
	A=request
	if id is None:B=A.GET.get('id')
	else:B=id
	return sparta_51b5c93938(A,B)
def sparta_51b5c93938(request,dashboard_id,session='-1'):
	G='res';E=dashboard_id;B=request;C=False
	if E is None:C=_A
	else:
		D=qube_8f617e9906.has_dashboard_access(E,B.user);H=D[G]
		if H==-1:C=_A
	if C:return sparta_6f644e6cf4(B)
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_B]=9;I=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(I);A[_C]=_A;F=D['dashboard_obj'];A['b_require_password']=0 if D[G]==1 else 1;A['dashboard_id']=F.dashboard_id;A['dashboard_name']=F.name;A['bPublicUser']=B.user.is_anonymous;A['session']=str(session);A[_D]=_A;return render(B,'dist/project/dashboard/dashboardRun.html',A)