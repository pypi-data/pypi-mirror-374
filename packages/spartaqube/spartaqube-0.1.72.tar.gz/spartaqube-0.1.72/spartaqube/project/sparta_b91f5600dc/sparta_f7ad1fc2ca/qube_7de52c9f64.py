_P='Please send valid data'
_O='dist/project/auth/resetPasswordChange.html'
_N='captcha'
_M='cypress_tests@gmail.com'
_L='password'
_K='POST'
_J=False
_I='login'
_H='error'
_G='form'
_F='email'
_E='res'
_D='home'
_C='manifest'
_B='errorMsg'
_A=True
import json,hashlib,uuid
from datetime import datetime
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.urls import reverse
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_1b9a152d9b import qube_4f69ebe2d1 as qube_4f69ebe2d1
from project.sparta_cc13a24db3.sparta_3f9af64854 import qube_80c6e8b226 as qube_80c6e8b226
from project.models import LoginLocation,UserProfile
from project.logger_config import logger
def sparta_0f6a29b9b9():return{'bHasCompanyEE':-1}
def sparta_193aa51b4e(request):B=request;A=qube_99dd79197b.sparta_6bbe31b6fa(B);A[_C]=qube_99dd79197b.sparta_60331ef5c3();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_b9ac22161e
def sparta_c2a7c8e057(request):
	C=request;B='/';A=C.GET.get(_I)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_8bf0fa9206(C,A)
def sparta_7faa9cf9bb(request,redirectUrl):return sparta_8bf0fa9206(request,redirectUrl)
def sparta_8bf0fa9206(request,redirectUrl):
	E=redirectUrl;A=request;logger.debug('Welcome to loginRedirectFunc')
	if A.user.is_authenticated:return redirect(_D)
	G=_J;H='Email or password incorrect'
	if A.method==_K:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];F=authenticate(username=I,password=J)
			if F:
				if qube_4f69ebe2d1.sparta_a7164257a8(F):return sparta_193aa51b4e(A)
				login(A,F);K,L=qube_99dd79197b.sparta_4462a17adf();LoginLocation.objects.create(user=F,hostname=K,ip=L,date_login=datetime.now())
				if E is not None:
					D=E.split('$@$');D=[A for A in D if len(A)>0]
					if len(D)>1:M=D[0];return redirect(reverse(M,args=D[1:]))
					return redirect(E)
				return redirect(_D)
			else:G=_A
		else:G=_A
	C=ConnexionForm();B=qube_99dd79197b.sparta_6bbe31b6fa(A);B.update(qube_99dd79197b.sparta_c0f7cff7f6(A));B[_C]=qube_99dd79197b.sparta_60331ef5c3();B[_G]=C;B[_H]=G;B['redirectUrl']=E;B[_B]=H;B.update(sparta_0f6a29b9b9());return render(A,'dist/project/auth/login.html',B)
def sparta_913d8dc237(request):
	B='public@spartaqube.com';A=User.objects.filter(email=B).all()
	if A.count()>0:C=A[0];login(request,C)
	return redirect(_D)
@sparta_b9ac22161e
def sparta_40adef3ff7(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_J;F=qube_4f69ebe2d1.sparta_0697032188()
	if A.method==_K:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_4f69ebe2d1.sparta_8fce8bbde0(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_4f69ebe2d1.sparta_544a5d44c7(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_99dd79197b.sparta_6bbe31b6fa(A);C.update(qube_99dd79197b.sparta_c0f7cff7f6(A));C[_C]=qube_99dd79197b.sparta_60331ef5c3();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_0f6a29b9b9());return render(A,'dist/project/auth/registration.html',C)
def sparta_66b0bf8e78(request):A=request;B=qube_99dd79197b.sparta_6bbe31b6fa(A);B[_C]=qube_99dd79197b.sparta_60331ef5c3();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_49d15ad3b7(request,token):
	A=request;B=qube_4f69ebe2d1.sparta_688e240bd0(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_99dd79197b.sparta_6bbe31b6fa(A);D[_C]=qube_99dd79197b.sparta_60331ef5c3();return redirect(_I)
def sparta_6b547ddc99(request):logout(request);return redirect(_I)
def sparta_21a7590209():
	from project.models import PlotDBChartShared as B,PlotDBChart,DashboardShared as C,NotebookShared as D,KernelShared as E,DBConnectorUserShared as F;A=_M;print('Destroy cypress user');G=B.objects.filter(user__email=A).all()
	for H in G:H.delete()
	I=C.objects.filter(user__email=A).all()
	for J in I:J.delete()
	K=D.objects.filter(user__email=A).all()
	for L in K:L.delete()
	M=E.objects.filter(user__email=A).all()
	for N in M:N.delete()
	O=F.objects.filter(user__email=A).all()
	for P in O:P.delete()
def sparta_63a427fe83(request):
	A=request;B=_M;sparta_21a7590209();from project.sparta_440f6a201b.sparta_15c403c94e.qube_d7643b4f9f import sparta_7cb29e2780 as C;C()
	if A.user.is_authenticated:
		if A.user.email==B:A.user.delete()
	logout(A);return redirect(_I)
def sparta_0e629da837(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_97d3b2d73f(request):
	A=request;E='';F=_J
	if A.method==_K:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_N];G=qube_4f69ebe2d1.sparta_97d3b2d73f(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_99dd79197b.sparta_6bbe31b6fa(A);C.update(qube_99dd79197b.sparta_c0f7cff7f6(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_99dd79197b.sparta_60331ef5c3();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_O,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:logger.debug('exception ');logger.debug(J);E='Could not send reset email, please try again';F=_A
		else:E=_P;F=_A
	else:B=ResetPasswordForm()
	D=qube_99dd79197b.sparta_6bbe31b6fa(A);D.update(qube_99dd79197b.sparta_c0f7cff7f6(A));D[_C]=qube_99dd79197b.sparta_60331ef5c3();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_0f6a29b9b9());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_8ed79b0f8c(request):
	D=request;E='';B=_J
	if D.method==_K:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_N];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_4f69ebe2d1.sparta_8ed79b0f8c(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_P;B=_A
	else:return redirect('reset-password')
	A=qube_99dd79197b.sparta_6bbe31b6fa(D);A.update(qube_99dd79197b.sparta_c0f7cff7f6(D));A[_C]=qube_99dd79197b.sparta_60331ef5c3();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_0f6a29b9b9());return render(D,_O,A)