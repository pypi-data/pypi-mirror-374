import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_440f6a201b.sparta_84179580a5 import qube_206107b092 as qube_206107b092
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_2461a75d38
@csrf_exempt
@sparta_2461a75d38
def sparta_3ae33c3386(request):G='api_func';F='key';E='utf-8';A=request;C=A.body.decode(E);C=A.POST.get(F);D=A.body.decode(E);D=A.POST.get(G);B=dict();B[F]=C;B[G]=D;H=qube_206107b092.sparta_3ae33c3386(B,A.user);I=json.dumps(H);return HttpResponse(I)