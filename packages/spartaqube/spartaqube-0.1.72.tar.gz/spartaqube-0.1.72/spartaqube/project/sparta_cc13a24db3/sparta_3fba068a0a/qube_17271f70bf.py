_I='error.txt'
_H='zipName'
_G='utf-8'
_F='attachment; filename={0}'
_E='appId'
_D='res'
_C='Content-Disposition'
_B='projectPath'
_A='jsonData'
import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_440f6a201b.sparta_850eb1704d import qube_8d8966264e as qube_8d8966264e
from project.sparta_440f6a201b.sparta_850eb1704d import qube_0ef6dace14 as qube_0ef6dace14
from project.sparta_440f6a201b.sparta_ceff546bba import qube_2940d28c8f as qube_2940d28c8f
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_2461a75d38
@csrf_exempt
@sparta_2461a75d38
def sparta_b652ea2e2f(request):
	D='files[]';A=request;E=A.POST.dict();B=A.FILES
	if D in B:C=qube_8d8966264e.sparta_dbbcfaeed4(E,A.user,B[D])
	else:C={_D:1}
	F=json.dumps(C);return HttpResponse(F)
@csrf_exempt
@sparta_2461a75d38
def sparta_4c2f3de0a8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8d8966264e.sparta_ab3e8c2986(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_99b8018663(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8d8966264e.sparta_3e5942b27b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_cb6d13d031(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8d8966264e.sparta_e1629eaf4a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_25ed5d357a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_0ef6dace14.sparta_4536b162ea(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_b7be0b71bb(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8d8966264e.sparta_5934e69cde(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_d12017e233(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8d8966264e.sparta_1ffd0c7c22(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_3653cd407b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8d8966264e.sparta_a28c498592(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_4125eb2a1b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_8d8966264e.sparta_fe4aecf85c(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_8623926f49(request):
	F='filePath';E='fileName';A=request;B=A.GET[E];G=A.GET[F];H=A.GET[_B];I=A.GET[_E];J={E:B,F:G,_E:I,_B:base64.b64decode(H).decode(_G)};C=qube_8d8966264e.sparta_39c01026d6(J,A.user)
	if C[_D]==1:
		try:
			with open(C['fullPath'],'rb')as K:D=HttpResponse(K.read(),content_type='application/force-download');D[_C]='attachment; filename='+str(B);return D
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_2461a75d38
def sparta_ec206ced98(request):
	E='folderName';B=request;F=B.GET[_B];D=B.GET[E];G={_B:base64.b64decode(F).decode(_G),E:D};C=qube_8d8966264e.sparta_13f86badf1(G,B.user)
	if C[_D]==1:H=C['zip'];I=C[_H];A=HttpResponse();A.write(H.getvalue());A[_C]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {D}, please try again";K=_I;A.write(J);A[_C]=_F.format(K)
	return A
@csrf_exempt
@sparta_2461a75d38
def sparta_d71e326212(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_8d8966264e.sparta_27d69b5c57(F,B.user)
	if C[_D]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_C]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_C]=_F.format(J)
	return A