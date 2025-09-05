from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from django.utils import timezone
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from project.models import User,UserProfile,UserGroup,notificationShare,notificationGroup,notificationShare
from project.sparta_31081a7413.sparta_0886d51747.qube_99dd79197b import sparta_dea94aa96c
def sparta_7266693c6f(json_data,user_obj):
	O='humanDate';N='userFromName';M=False;I=True;D=user_obj;J=datetime.now().astimezone(UTC)-timedelta(days=3);F=0;K=list(notificationShare.objects.filter(user=D,is_delete=0,is_seen=M));K+=list(notificationShare.objects.filter(user=D,is_delete=0,is_seen=I,date_seen__gt=J));E=[];P=['id','user','user_group','is_delete','date_seen']
	for A in K:
		B=sparta_dea94aa96c(model_to_dict(A));Q=int(A.typeObject)
		if not A.is_seen:F+=1
		for R in P:B.pop(R,None)
		C=User.objects.get(id=A.user_from.id);G=C.first_name+' '+C.last_name;H=A.date_created.astimezone(UTC);B[N]=G;B[O]=sparta_52178c3817(H)
		if Q==0:0
	L=list(notificationGroup.objects.filter(user=D,is_delete=0,is_seen=M));L+=list(notificationGroup.objects.filter(user=D,is_delete=0,is_seen=I,date_seen__gt=J))
	for A in L:
		if not A.is_seen:F+=1
		B=sparta_dea94aa96c(model_to_dict(A));C=User.objects.get(id=A.user_from.id);G=C.first_name+' '+C.last_name;H=A.dateCreated.astimezone(UTC);B[N]=G;B['type_object']=-2;B[O]=sparta_52178c3817(H);E.append(B)
	E=sorted(E,key=lambda obj:obj['dateCreated'],reverse=I);return{'res':1,'resNotifications':E,'nbNotificationNotSeen':F}
def sparta_52178c3817(dateCreated):
	A=dateCreated;B=datetime.now().astimezone(UTC)
	if A.day==B.day:
		if int(B.hour-A.hour)==0:return'A moment ago'
		elif int(B.hour-A.hour)==1:return'1 hour ago'
		return str(B.hour-A.hour)+' hours ago'
	elif A.month==B.month:
		if int(B.day-A.day)==1:return'Yesterday'
		return str(B.day-A.day)+' days ago'
	elif A.year==B.year:
		if int(B.month-A.month)==1:return'Last month'
		return str(B.month-A.month)+' months ago'
	return str(A)
def sparta_2588c0f40f(json_data,user_obj):
	B=user_obj;print('JUST BEFORE WARNING');C=datetime.now().astimezone(UTC);D=notificationShare.objects.filter(user=B,is_delete=0,is_seen=0)
	for A in D:
		if A.dateSeen is not None:
			if abs(A.date_seen.day-A.date_created.day)>2:A.is_delete=1
		A.is_seen=1;A.date_seen=C;A.save()
	E=notificationGroup.objects.filter(user=B,is_delete=0,is_seen=0)
	for A in E:
		if A.date_seen is not None:
			if abs(A.date_seen.day-A.date_created.day)>2:A.is_delete=1
		A.is_seen=1;A.date_seen=C;A.save()
	return{'res':1}