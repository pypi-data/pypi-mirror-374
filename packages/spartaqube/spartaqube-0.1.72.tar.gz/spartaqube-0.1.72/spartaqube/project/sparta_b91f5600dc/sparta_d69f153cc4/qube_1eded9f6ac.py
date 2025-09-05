import os,json,getpass,platform
from pathlib import Path
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_aea4c35167 import qube_477699d437 as qube_477699d437
from project.sparta_440f6a201b.sparta_c4f0fc23b4 import qube_8f617e9906 as qube_8f617e9906
def sparta_69df759d09():
	A=platform.system()
	if A=='Windows':return'windows'
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
@csrf_exempt
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_a57453f727(request):
	E='template';D='developer';B=request
	if not conf_settings.IS_DEV_VIEW_ENABLED:A=qube_99dd79197b.sparta_6bbe31b6fa(B);return render(B,'dist/project/homepage/homepage.html',A)
	A=qube_99dd79197b.sparta_6bbe31b6fa(B);A['menuBar']=12;F=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(F);A['bCodeMirror']=True;G=os.path.dirname(__file__);C=os.path.dirname(os.path.dirname(G));H=os.path.join(C,'static');I=os.path.join(H,'js',D,E,'frontend');A['frontend_path']=I;J=os.path.dirname(C);K=os.path.join(J,'django_app_template',D,E,'backend');A['backend_path']=K;return render(B,'dist/project/developer/developerExamples.html',A)