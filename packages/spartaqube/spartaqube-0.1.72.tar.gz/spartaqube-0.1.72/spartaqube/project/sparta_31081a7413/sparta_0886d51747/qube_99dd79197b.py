_D='manifest'
_C=None
_B=False
_A=True
import os,socket,json,requests
from datetime import date,datetime
from project.models import UserProfile,AppVersioning
from django.conf import settings as conf_settings
from spartaqube_app.secrets import sparta_61772791e6
from spartaqube_app.path_mapper_obf import sparta_fc868586da
from project.sparta_440f6a201b.sparta_8ade4c4917.qube_b559aa4222 import sparta_ac6c5f1fe5
import pytz
UTC=pytz.utc
class dotdict(dict):__getattr__=dict.get;__setattr__=dict.__setitem__;__delattr__=dict.__delitem__
def sparta_dea94aa96c(appViewsModels):
	A=appViewsModels
	if isinstance(A,list):
		for C in A:
			for B in list(C.keys()):
				if isinstance(C[B],date):C[B]=str(C[B])
	else:
		for B in list(A.keys()):
			if isinstance(A[B],date):A[B]=str(A[B])
	return A
def sparta_c216d94b94(thisText):A=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));A=A+str('/log/log.txt');B=open(A,'a');B.write(thisText);B.writelines('\n');B.close()
def sparta_c0f7cff7f6(request):A=request;return{'appName':'Project','user':A.user,'ip_address':A.META['REMOTE_ADDR']}
def sparta_7be7b58bc3():return conf_settings.PLATFORM
def sparta_60331ef5c3():
	A=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));A=os.path.dirname(os.path.dirname(A))
	if conf_settings.DEBUG:C='static'
	else:C='staticfiles'
	E=A+f"/{C}/dist/manifest.json";F=open(E);B=json.load(F)
	if conf_settings.B_TOOLBAR:
		G=list(B.keys())
		for D in G:B[D]=A+f"/{C}"+B[D]
	return B
def sparta_6bbe31b6fa(request):
	K='CYPRESS_TEST_APP';B='';C=''
	if len(B)>0:B='/'+str(B)
	if len(C)>0:C='/'+str(C)
	H=sparta_ac6c5f1fe5()
	try:
		A=_B;I=AppVersioning.objects.all();E=datetime.now().astimezone(UTC)
		if I.count()==0:AppVersioning.objects.create(last_check_date=E);A=_A
		else:
			D=I[0];L=D.last_check_date;M=E-L;N=D.last_available_version_pip
			if not H==N:A=_A
			elif M.seconds>60*10:A=_A;D.last_check_date=E;D.save()
	except:A=_A
	try:
		O=sparta_fc868586da()['api']
		with open(os.path.join(O,'app_data_asgi.json'),'r')as P:Q=json.load(P)
		J=int(Q['default_port'])
	except:J=5664
	F=-1
	if os.environ.get(K,'0')=='1':F=1
	R=conf_settings.HOST_WS_PREFIX;S=conf_settings.WEBSOCKET_PREFIX;G=conf_settings.IS_VITE
	if G:
		if F==1:G=_B
	T={'PROJECT_NAME':conf_settings.PROJECT_NAME,'IS_DEV_VIEW_ENABLED':conf_settings.IS_DEV_VIEW_ENABLED,'CAPTCHA_SITEKEY':conf_settings.CAPTCHA_SITEKEY,'WEBSOCKET_PREFIX':S,'URL_PREFIX':B,'URL_WS_PREFIX':C,'ASGI_PORT':J,'HOST_WS_PREFIX':R,'CHECK_VERSIONING':A,'CURRENT_VERSION':H,'IS_VITE':G,'IS_DEV':conf_settings.IS_DEV,'IS_LLM':conf_settings.IS_LLM,'IS_DOCKER':os.getenv('IS_REMOTE_SPARTAQUBE_CONTAINER','False')=='True',K:F};return T
def sparta_7ba2aa5bc0(captcha):
	D='errorMsg';B='res';A=captcha
	try:
		if A is not _C:
			if len(A)>0:
				E=sparta_61772791e6()['CAPTCHA_SECRET_KEY'];F=f"https://www.google.com/recaptcha/api/siteverify?secret={E}&response={A}";C=requests.get(F)
				if int(C.status_code)==200:
					G=json.loads(C.text)
					if G['success']:return{B:1}
	except Exception as H:return{B:-1,D:str(H)}
	return{B:-1,D:'Invalid captcha'}
def sparta_e78623b340(password):
	A=password;B=UserProfile.objects.filter(email=conf_settings.ADMIN_DEFAULT_EMAIL).all()
	if B.count()==0:return conf_settings.ADMIN_DEFAULT==A
	else:C=B[0];D=C.user;return D.check_password(A)
def sparta_60b27d02a9(code):
	A=code
	try:
		if A is not _C:
			if len(A)>0:
				B=os.getenv('SPARTAQUBE_PASSWORD','admin')
				if B==A:return _A
	except:return _B
	return _B
def sparta_29db575fa9(user):
	F='default';A=dict()
	if not user.is_anonymous:
		E=UserProfile.objects.filter(user=user)
		if E.count()>0:
			B=E[0];D=B.avatar
			if D is not _C:D=B.avatar.avatar
			A['avatar']=D;A['userProfile']=B;C=B.editor_theme
			if C is _C:C=F
			elif len(C)==0:C=F
			else:C=B.editor_theme
			A['theme']=C;A['font_size']=B.font_size;A['B_DARK_THEME']=B.is_dark_theme;A['is_size_reduced_plot_db']=B.is_size_reduced_plot_db;A['is_size_reduced_api']=B.is_size_reduced_api
	A[_D]=sparta_60331ef5c3();return A
def sparta_ba95ac950e(user):A=dict();A[_D]=sparta_60331ef5c3();return A
def sparta_d34ac6fcaf():
	try:socket.create_connection(('1.1.1.1',53));return _A
	except OSError:pass
	return _B
def sparta_4462a17adf():A=socket.gethostname();B=socket.gethostbyname(A);return A,B