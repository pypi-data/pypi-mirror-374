_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_440f6a201b.sparta_d534fc8e38 import qube_17d1d6d19a as qube_17d1d6d19a
from project.sparta_440f6a201b.sparta_5d8d67cf28 import qube_14a60390f9 as qube_14a60390f9
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_2461a75d38
@csrf_exempt
@sparta_2461a75d38
def sparta_7266693c6f(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_14a60390f9.sparta_dd6e069988(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_17d1d6d19a.sparta_7266693c6f(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_2461a75d38
def sparta_73ebfed9dc(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_17d1d6d19a.sparta_2588c0f40f(C,A.user);E=json.dumps(D);return HttpResponse(E)