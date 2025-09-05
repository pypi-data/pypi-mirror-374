_A='menuBar'
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
from project.sparta_440f6a201b.sparta_15c403c94e import qube_d7643b4f9f as qube_d7643b4f9f
from project.sparta_440f6a201b.sparta_817694737b import qube_62229504ef as qube_62229504ef
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_a839e8520f(request):A=request;B=qube_99dd79197b.sparta_6bbe31b6fa(A);B[_A]=-1;C=qube_99dd79197b.sparta_29db575fa9(A.user);B.update(C);return render(A,'dist/project/homepage/homepage.html',B)
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_ca4b1cebeb(request,kernel_manager_uuid):
	D=kernel_manager_uuid;C=True;B=request;E=False
	if D is None:E=C
	else:
		F=qube_d7643b4f9f.sparta_7c02da572c(B.user,D)
		if F is None:E=C
	if E:return sparta_a839e8520f(B)
	def H(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=C)
	K=sparta_a4e746f060();G=os.path.join(K,'kernel');H(G);I=os.path.join(G,D);H(I);J=os.path.join(I,'main.ipynb')
	if not os.path.exists(J):
		L=qube_62229504ef.sparta_fa7ea4f2b7()
		with open(J,'w')as M:M.write(json.dumps(L))
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A['default_project_path']=G;A[_A]=-1;N=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(N);A['kernel_name']=F.name;A['kernelManagerUUID']=F.kernel_manager_uuid;A['bCodeMirror']=C;A['bPublicUser']=B.user.is_anonymous;return render(B,'dist/project/sqKernelNotebook/sqKernelNotebook.html',A)