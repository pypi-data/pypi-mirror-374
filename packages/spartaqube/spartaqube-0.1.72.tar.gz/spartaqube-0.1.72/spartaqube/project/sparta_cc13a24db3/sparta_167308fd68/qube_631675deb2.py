_A='jsonData'
import json,inspect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from project.sparta_440f6a201b.sparta_199ecf12c7 import qube_6e4f065b3d as qube_6e4f065b3d
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_2461a75d38
def sparta_a82ac5ef98(request):A={'res':1};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
@sparta_2461a75d38
def sparta_e9a56bb413(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_6e4f065b3d.sparta_e9a56bb413(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_0521503612(request):
	C='userObj';B=request;D=json.loads(B.body);E=json.loads(D[_A]);F=B.user;A=qube_6e4f065b3d.sparta_0521503612(E,F)
	if A['res']==1:
		if C in list(A.keys()):login(B,A[C]);A.pop(C,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_2461a75d38
def sparta_f7e5c6c06f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_6e4f065b3d.sparta_f7e5c6c06f(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_2461a75d38
def sparta_7116bda69f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_6e4f065b3d.sparta_7116bda69f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_2299d61603(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_6e4f065b3d.sparta_2299d61603(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_edc09b81cf(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_6e4f065b3d.sparta_edc09b81cf(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_84c476174c(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_6e4f065b3d.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_2461a75d38
def sparta_5232ab1f95(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_6e4f065b3d.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_dbb6ff0c8a(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_6e4f065b3d.sparta_dbb6ff0c8a(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_2e9b99598a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_6e4f065b3d.sparta_2e9b99598a(A,C);E=json.dumps(D);return HttpResponse(E)