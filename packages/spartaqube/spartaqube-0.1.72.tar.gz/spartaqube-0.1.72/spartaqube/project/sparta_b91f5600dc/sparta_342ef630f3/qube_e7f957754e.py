from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.models import UserProfile
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_b91f5600dc.sparta_f7ad1fc2ca.qube_7de52c9f64 import sparta_0f6a29b9b9
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_5ca931d59e(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	G={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_99dd79197b.sparta_6bbe31b6fa(B);A.update(qube_99dd79197b.sparta_29db575fa9(B.user));A.update(G);H='';A['accessKey']=H;A['menuBar']=4;A.update(sparta_0f6a29b9b9());F=True
	if B.headers.get('HX-Request')=='true':F=False
	A['bFullRender']=F;return render(B,'dist/project/auth/settings.html',A)