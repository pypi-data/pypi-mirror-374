_E='Content-Disposition'
_D='utf-8'
_C='dashboardId'
_B='projectPath'
_A='jsonData'
import os,json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_440f6a201b.sparta_817694737b import qube_faef83dd00 as qube_faef83dd00
from project.sparta_440f6a201b.sparta_817694737b import qube_4f7256eedf as qube_4f7256eedf
from project.sparta_440f6a201b.sparta_c4f0fc23b4 import qube_8f617e9906 as qube_8f617e9906
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_2461a75d38,sparta_62e9a93c09
@csrf_exempt
def sparta_b4ffedad18(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_b4ffedad18(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_b19d171645(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_b19d171645(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_2d10d36b1d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_2d10d36b1d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_8e9c973125(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_8e9c973125(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_397eb9c8bd(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_397eb9c8bd(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_02744345a6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_02744345a6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_5a9e0aa03d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_5a9e0aa03d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_9b70057db9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_9b70057db9(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_9dc8136a5e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_9dc8136a5e(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_2971db69bf(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.sparta_2971db69bf(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_ecd43978c8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_faef83dd00.dashboard_project_explorer_delete_multiple_resources(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
def sparta_9216c74746(request):A=request;B=A.POST.dict();C=A.FILES;D=qube_faef83dd00.sparta_9216c74746(B,A.user,C['files[]']);E=json.dumps(D);return HttpResponse(E)
def sparta_15a9e6859b(path):
	A=path;A=os.path.normpath(A)
	if os.path.isfile(A):A=os.path.dirname(A)
	return os.path.basename(A)
def sparta_6af3d80a3a(path):A=path;A=os.path.normpath(A);return os.path.basename(A)
@csrf_exempt
@sparta_2461a75d38
def sparta_6d7eb23b08(request):
	E='pathResource';A=request;B=A.GET[E];B=base64.b64decode(B).decode(_D);F=A.GET[_B];G=A.GET[_C];H=sparta_6af3d80a3a(B);I={E:B,_C:G,_B:base64.b64decode(F).decode(_D)};C=qube_faef83dd00.sparta_39c01026d6(I,A.user)
	if C['res']==1:
		try:
			with open(C['fullPath'],'rb')as J:D=HttpResponse(J.read(),content_type='application/force-download');D[_E]='attachment; filename='+str(H);return D
		except Exception as K:pass
	raise Http404
@csrf_exempt
@sparta_2461a75d38
def sparta_19699c6dd6(request):
	D='attachment; filename={0}';B=request;E=B.GET[_C];F=B.GET[_B];G={_C:E,_B:base64.b64decode(F).decode(_D)};C=qube_faef83dd00.sparta_27d69b5c57(G,B.user)
	if C['res']==1:H=C['zip'];I=C['zipName'];A=HttpResponse();A.write(H.getvalue());A[_E]=D.format(f"{I}.zip")
	else:A=HttpResponse();J='Could not download the application, please try again';K='error.txt';A.write(J);A[_E]=D.format(K)
	return A
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_3a99af326a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_3a99af326a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_0a93d8a8e9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_0a93d8a8e9(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_3a80d6982b(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_3a80d6982b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_6d5f724127(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_6d5f724127(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_5826c8b96d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_5826c8b96d(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_d4a4b84713(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_d4a4b84713(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_487092c61f(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_487092c61f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_662bb1af0a(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_662bb1af0a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_10a84bbf14(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_10a84bbf14(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_d4f9bcfd12(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_d4f9bcfd12(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_52428630da(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_52428630da(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_23769a60eb(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_23769a60eb(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_74437f31a7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_74437f31a7(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_2461a75d38
@sparta_62e9a93c09
def sparta_ac81614ea7(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_4f7256eedf.sparta_ac81614ea7(C,A.user);E=json.dumps(D);return HttpResponse(E)