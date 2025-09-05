from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_440f6a201b.sparta_1b9a152d9b.qube_4f69ebe2d1 import sparta_b9ac22161e
from project.sparta_440f6a201b.sparta_5d8d67cf28 import qube_14a60390f9 as qube_14a60390f9
from project.models import UserProfile
import project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b as qube_99dd79197b
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_91965f9c22(request):
	E='avatarImg';B=request;A=qube_99dd79197b.sparta_6bbe31b6fa(B);A['menuBar']=-1;F=qube_99dd79197b.sparta_29db575fa9(B.user);A.update(F);A[E]='';C=UserProfile.objects.filter(user=B.user)
	if C.count()>0:
		D=C[0];G=D.avatar
		if G is not None:H=D.avatar.image64;A[E]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_b9ac22161e
@login_required(redirect_field_name='login')
def sparta_f72cc0edcd(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_91965f9c22(A)