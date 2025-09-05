_M='An error occurred, please try again'
_L='password_confirmation'
_K='password'
_J='jsonData'
_I='api_token_id'
_H='Invalid captcha'
_G='is_created'
_F='utf-8'
_E=None
_D='errorMsg'
_C=False
_B=True
_A='res'
import hashlib,re,uuid,json,requests,socket,base64,traceback,os
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout,login,authenticate
from django.http import HttpResponseRedirect,HttpResponse
from django.conf import settings as conf_settings
from django.urls import reverse
from project.models import UserProfile,GuestCode,GuestCodeGlobal,LocalApp,SpartaQubeCode
from project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b import sparta_7ba2aa5bc0
from project.sparta_440f6a201b.sparta_804dd6b985 import qube_03613a31ee as qube_03613a31ee
from project.sparta_440f6a201b.sparta_bb5bf030e1 import qube_203378cc3e as qube_203378cc3e
from project.sparta_440f6a201b.sparta_6750f6ff8a.qube_d4bc28ec7a import Email as Email
from project.logger_config import logger
def sparta_b9ac22161e(function):
	def A(request,*E,**D):
		A=request;B=_B
		if not A.user.is_active:B=_C;logout(A)
		if not A.user.is_authenticated:B=_C;logout(A)
		try:C=D.get(_I,_E)
		except:C=_E
		if not B:
			if C is not _E:F=qube_203378cc3e.sparta_8246bbabca(C);login(A,F)
		else:0
		return function(A,*E,**D)
	return A
def sparta_2461a75d38(function):
	def A(request,*C,**D):
		B='notLoggerAPI';A=request
		if not A.user.is_active:return HttpResponseRedirect(reverse(B))
		if A.user.is_authenticated:return function(A,*C,**D)
		else:return HttpResponseRedirect(reverse(B))
	return A
def sparta_62e9a93c09(function):
	def A(request,*B,**C):
		try:return function(request,*B,**C)
		except Exception as A:
			if conf_settings.DEBUG:logger.debug('Try catch exception with error:');logger.debug(A);logger.debug('traceback:');logger.debug(traceback.format_exc())
			D={_A:-1,_D:str(A)};E=json.dumps(D);return HttpResponse(E)
	return A
def sparta_6dea471c4e(function):
	C=function
	def A(request,*D,**E):
		A=request;F=_C
		try:
			G=json.loads(A.body);H=json.loads(G[_J]);I=H[_I];B=qube_203378cc3e.sparta_8246bbabca(I)
			if B is not _E:F=_B;A.user=B
		except Exception as J:logger.debug('exception pip auth');logger.debug(J)
		if F:return C(A,*D,**E)
		else:K='public@spartaqube.com';B=User.objects.filter(email=K).all()[0];A.user=B;return C(A,*D,**E)
	return A
def sparta_4d7cb32d4a(code):
	try:
		B=SpartaQubeCode.objects.all()
		if B.count()==0:return code=='admin'
		else:C=B[0].spartaqube_code;A=hashlib.md5(code.encode(_F)).hexdigest();A=base64.b64encode(A.encode(_F));A=A.decode(_F);return A==C
	except Exception as D:pass
	return _C
def sparta_16b67ffe79():
	A=LocalApp.objects.all()
	if A.count()==0:B=str(uuid.uuid4());LocalApp.objects.create(app_id=B,date_created=datetime.now());return B
	else:return A[0].app_id
def sparta_620a7bfce8():A=socket.gethostname();B=socket.gethostbyname(A);return B
def sparta_e20e6c3a73(json_data):
	D='ip_addr';A=json_data;del A[_K];del A[_L]
	try:A[D]=sparta_620a7bfce8()
	except:A[D]=-1
	C=dict();C[_J]=json.dumps(A);E={'http':os.environ.get('http_proxy',_E),'https':os.environ.get('https_proxy',_E)};B=requests.post(f"{conf_settings.SPARTAQUBE_WEBSITE}/create-user",data=json.dumps(C),proxies=E)
	if B.status_code==200:
		try:
			A=json.loads(B.text)
			if A[_A]==1:return{_A:1,_G:_B}
			else:A[_G]=_C;return A
		except Exception as F:return{_A:-1,_G:_C,_D:str(F)}
	return{_A:1,_G:_C,_D:f"status code: {B.status_code}. Please check your internet connection"}
def sparta_97fe3068bb(file_path,text):
	A=file_path
	try:
		B='a'if os.path.exists(A)and os.path.getsize(A)>0 else'w'
		with open(A,B,encoding=_F)as C:
			if B=='a':C.write('\n')
			C.write(text)
		logger.debug(f"Successfully wrote/appended to {A}")
	except Exception as D:logger.debug(f"Error writing to file: {D}")
def sparta_544a5d44c7(json_data,hostname_url):
	P='emailExist';O='passwordConfirm';K='email';B=json_data;F={O:'The two passwords must be the same...',K:'Email address is not valid...','form':'The form you sent is not valid...',P:'This email is already registered...'};E=_C;Q=B['firstName'].capitalize();R=B['lastName'].capitalize();C=B[K].lower();L=B[_K];S=B[_L];T=B['code'];M=B['captcha'];B['app_id']=sparta_16b67ffe79()
	if M=='cypress'and C=='cypress_tests@gmail.com':
		if int(os.environ.get('CYPRESS_TEST_APP','0'))==1:
			try:from project.sparta_b91f5600dc.sparta_f7ad1fc2ca.qube_7de52c9f64 import sparta_21a7590209 as U;U()
			except Exception as V:W='C:\\Users\\benme\\Desktop\\LOG_DEBUG_CYPRESS.txt';sparta_97fe3068bb(W,str(V))
	else:
		X=sparta_7ba2aa5bc0(M)
		if X[_A]!=1:return{_A:-1,_D:_H}
	if not sparta_4d7cb32d4a(T):return{_A:-1,_D:'Invalid spartaqube code, please contact your administrator'}
	if L!=S:E=_B;G=F[O]
	if not re.match('[^@]+@[^@]+\\.[^@]+',C):E=_B;G=F[K]
	if User.objects.filter(username=C).exists():E=_B;G=F[P]
	if not E:
		Y=sparta_e20e6c3a73(B);N=_B;Z=Y[_G]
		if not Z:N=_C
		A=User.objects.create_user(C,C,L);A.is_staff=_C;A.username=C;A.first_name=Q;A.last_name=R;A.is_active=_B;A.save();D=UserProfile(user=A);H=str(A.id)+'_'+str(A.email);H=H.encode(_F);I=hashlib.md5(H).hexdigest()+str(datetime.now());I=I.encode(_F);a=str(uuid.uuid4());D.user_profile_id=hashlib.sha256(I).hexdigest();D.email=C;D.api_key=str(uuid.uuid4());D.registration_token=a;D.b_created_website=N;D.save();J={_A:1,'userObj':A};return J
	J={_A:-1,_D:G};return J
def sparta_c12ad92c26(user_obj,hostname_url,registration_token):C='Validate your account';B=user_obj;A=Email(B.username,[B.email],f"Welcome to {conf_settings.PROJECT_NAME}",C);A.addOneRow(C);A.addSpaceSeparator();A.addOneRow('Click on the link below to validate your account');D=f"{hostname_url.rstrip('/')}/registration-validation/{registration_token}";A.addOneCenteredButton('Validate',D);A.send()
def sparta_688e240bd0(token):
	C=UserProfile.objects.filter(registration_token=token)
	if C.count()>0:A=C[0];A.registration_token='';A.is_account_validated=_B;A.save();B=A.user;B.is_active=_B;B.save();return{_A:1,'user':B}
	return{_A:-1,_D:'Invalid registration token'}
def sparta_0697032188():return conf_settings.IS_GUEST_CODE_REQUIRED
def sparta_8fce8bbde0(guest_code):
	if GuestCodeGlobal.objects.filter(guest_id=guest_code,is_active=_B).count()>0:return _B
	return _C
def sparta_072593f3f9(guest_code,user_obj):
	D=user_obj;C=guest_code
	if GuestCodeGlobal.objects.filter(guest_id=C,is_active=_B).count()>0:return _B
	A=GuestCode.objects.filter(user=D)
	if A.count()>0:return _B
	else:
		A=GuestCode.objects.filter(guest_id=C,is_used=_C)
		if A.count()>0:B=A[0];B.user=D;B.is_used=_B;B.save();return _B
	return _C
def sparta_a7164257a8(user):
	A=UserProfile.objects.filter(user=user)
	if A.count()==1:return A[0].is_banned
	else:return _C
def sparta_97d3b2d73f(email,captcha):
	D=sparta_7ba2aa5bc0(captcha)
	if D[_A]!=1:return{_A:-1,_D:_H}
	B=UserProfile.objects.filter(user__username=email)
	if B.count()==0:return{_A:-1,_D:_M}
	A=B[0];C=str(uuid.uuid4());A.token_reset_password=C;A.save();sparta_e84262bd81(A.user,C);return{_A:1}
def sparta_e84262bd81(user_obj,token_reset_password):B=user_obj;A=Email(B.username,[B.email],'Reset Password','Reset Password Message');A.addOneRow('Reset code','Copy the following code to reset your password');A.addSpaceSeparator();A.addOneRow(token_reset_password);A.send()
def sparta_8ed79b0f8c(captcha,token,email,password):
	D=sparta_7ba2aa5bc0(captcha)
	if D[_A]!=1:return{_A:-1,_D:_H}
	B=UserProfile.objects.filter(user__username=email)
	if B.count()==0:return{_A:-1,_D:_M}
	A=B[0]
	if not token==A.token_reset_password:return{_A:-1,_D:'Invalid token..., please try again'}
	A.token_reset_password='';A.save();C=A.user;C.set_password(password);C.save();return{_A:1}