import os,json,base64,subprocess,pandas as pd
from datetime import datetime,timedelta
from dateutil import parser
import pytz
UTC=pytz.utc
from django.db.models import Q
from django.conf import settings as conf_settings
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.text import Truncator
from django.db.models import CharField,TextField
from django.db.models.functions import Lower
CharField.register_lookup(Lower)
TextField.register_lookup(Lower)
from project.models import User,UserProfile,PlotDBChart,PlotDBChartShared,DashboardShared,Notebook,NotebookShared,DataFrameShared
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
from project.sparta_440f6a201b.sparta_ded1362815 import qube_bdfd9ffb24 as qube_bdfd9ffb24
def sparta_8bc53bda0e(user_obj):
	A=qube_2808664dfd.sparta_0a996f3465(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_51bbba07af(json_data,user_obj):
	n='dataframes';m='notebooks';l='dashboards';k='widgets';j='plot_chart_id';X=False;N=True;M='description_trunc';L='description';K='name_trunc';J='name';B=user_obj;A=json_data['keyword'].lower();D=120;E=sparta_8bc53bda0e(B)
	if len(E)>0:O=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=E,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=A)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=A))
	else:O=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=A)
	o=O.count();P=[]
	for p in O[:5]:H=p.plot_db_chart;P.append({j:H.plot_chart_id,'type_chart':H.type_chart,J:H.name,K:Truncator(H.name).chars(D),L:H.description,M:Truncator(H.description).chars(D)})
	q=sorted(set([A[j]for A in P]));Y=[];Z=[];a=0
	if len(E)>0:R=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=E,dashboard__is_delete=0)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard__name__lower__icontains=A))
	else:R=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard__name__lower__icontains=A)
	a=R.count()
	for r in R[:5]:
		S=X;C=r.dashboard
		if A in C.name.lower():S=N
		else:
			I=C.plot_db_dependencies
			if I is not None:
				I=json.loads(I)
				for s in I:
					if s in q:S=N;break
		if S:
			if C.dashboard_id not in Z:Z.append(C.dashboard_id);Y.append({'dashboard_id':C.dashboard_id,J:C.name,K:Truncator(C.name).chars(D),L:C.description,M:Truncator(C.description).chars(D)})
	T=[];b=[];c=0
	if len(E)>0:U=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=E,notebook__is_delete=0)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook__name__lower__icontains=A))
	else:U=NotebookShared.objects.filter(is_delete=0,user=B,notebook__is_delete=0,notebook__name__lower__icontains=A)
	c=U.count()
	for t in U:
		if len(T)>=5:break
		d=X;F=t.notebook
		if A in F.name.lower():d=N
		if d:
			if F.notebook_id not in b:b.append(F.notebook_id);T.append({'notebook_id':F.notebook_id,J:F.name,K:Truncator(F.name).chars(D),L:F.description,M:Truncator(F.description).chars(D)})
	V=[];e=[];f=0
	if len(E)>0:W=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=E,dataframe_model__is_delete=0)|Q(is_delete=0,user=B,dataframe_model__is_delete=0,dataframe_model__table_name__lower__icontains=A))
	else:W=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model__is_delete=0,dataframe_model__table_name__lower__icontains=A)
	f=W.count()
	for u in W:
		if len(V)>=5:break
		g=X;G=u.dataframe_model
		if A in G.table_name.lower():g=N
		if g:
			if G.slug not in e:e.append(G.slug);V.append({'dataframe_id':G.slug,J:G.table_name,K:Truncator(G.table_name).chars(D),L:G.description,M:Truncator(G.description).chars(D)})
	h=0;i={k:o,l:a,m:c,n:f}
	for(w,v)in i.items():h+=v
	return{'res':1,k:P,l:Y,m:T,n:V,'cntTotal':h,'counter_dict':i}