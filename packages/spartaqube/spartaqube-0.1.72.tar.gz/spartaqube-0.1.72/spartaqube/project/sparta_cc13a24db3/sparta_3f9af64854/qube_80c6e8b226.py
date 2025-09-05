_C='isAuth'
_B='jsonData'
_A='res'
import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_440f6a201b.sparta_1b9a152d9b import qube_4f69ebe2d1 as qube_4f69ebe2d1
from project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b import sparta_7ba2aa5bc0
from project.logger_config import logger
@csrf_exempt
def sparta_544a5d44c7(request):A=json.loads(request.body);B=json.loads(A[_B]);return qube_4f69ebe2d1.sparta_544a5d44c7(B)
@csrf_exempt
def sparta_f7849928f5(request):logout(request);A={_A:1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_feadd21a0c(request):
	if request.user.is_authenticated:A=1
	else:A=0
	B={_A:1,_C:A};C=json.dumps(B);return HttpResponse(C)
def sparta_ba39e8f54c(request):
	B=request;from django.contrib.auth import authenticate as F,login;from django.contrib.auth.models import User as C;G=json.loads(B.body);D=json.loads(G[_B]);H=D['email'];I=D['password'];E=0
	try:
		A=C.objects.get(email=H);A=F(B,username=A.username,password=I)
		if A is not None:login(B,A);E=1
	except C.DoesNotExist:pass
	J={_A:1,_C:E};K=json.dumps(J);return HttpResponse(K)