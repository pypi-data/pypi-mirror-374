from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings as conf_settings
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
import hashlib,project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
@csrf_exempt
def sparta_16b7821e9c(request):
	B=request;A=qube_99dd79197b.sparta_6bbe31b6fa(B);A['menuBar']=8;A['bCodeMirror']=True;D=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(D);C=True
	if B.headers.get('HX-Request')=='true':C=False
	A['bFullRender']=C;return render(B,'dist/project/api/api.html',A)