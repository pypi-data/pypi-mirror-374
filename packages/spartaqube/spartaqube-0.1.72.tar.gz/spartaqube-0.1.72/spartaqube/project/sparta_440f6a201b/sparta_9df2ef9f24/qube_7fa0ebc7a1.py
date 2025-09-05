_AD='this_traceback quantile reg'
_AC='perplexity'
_AB='__sq_index__'
_AA='bFirstColIndex'
_A9='bFirstRowHeader'
_A8='delimiters'
_A7='clipboardData'
_A6='You do not have access to this dataframe...'
_A5='You do not have the rights to edit this dataframe'
_A4='encoded_blob'
_A3='data_preview_df'
_A2='%Y-%m-%d %H:%M:%S'
_A1='last_update'
_A0='date_created'
_z='You do not have the rights to drop this dataframe'
_y='If you want to use a list of dispo, it must have the same length at the dataframe'
_x='keras'
_w='prophet'
_v='wavelet'
_u='arch'
_t='max_depth'
_s='scikit-learn'
_r='this_traceback'
_q='analysis'
_p='df_blob'
_o='is_dataframe_connector'
_n='previewTopMod'
_m='has_widget_password'
_l='is_public_widget'
_k='is_expose_widget'
_j='description'
_i='ruptures'
_h='bNormalizeDecisionTree'
_g='this_traceback clustering'
_f='nbComponents'
_e='is_installed'
_d='Invalid password'
_c='-1'
_b='has_access'
_a='password'
_Z='dataframe_model_name'
_Y='name'
_X='%Y-%m-%d'
_W='Missing slug'
_V='table_name'
_U='dataset'
_T='columns'
_S='replace'
_R='this_traceback polynomial reg'
_Q='bInSample'
_P='utf-8'
_O='trainTest'
_N='selectedX'
_M='dispo'
_L='dataframe_model_obj'
_K='target'
_J='index'
_I='slug'
_H='data'
_G='colDataset'
_F='B_DARK_THEME'
_E='errorMsg'
_D=True
_C=False
_B='res'
_A=None
import traceback,subprocess,sys,json,math,pickle,base64,pandas as pd
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from django.db.models import Q
from django.utils.text import slugify
from project.models_spartaqube import DataFrameHistory,DataFrameShared,DataFrameModel,DataFramePermission
from project.models import ShareRights
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
from project.sparta_440f6a201b.sparta_aea4c35167 import qube_2fc75b9545 as qube_2fc75b9545
from project.logger_config import logger
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import process_dataframe_components
def sparta_8bc53bda0e(user_obj):
	A=qube_2808664dfd.sparta_0a996f3465(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_fbd037e548(dispo):return pickle.loads(base64.b64decode(dispo.encode(_P)))
def sparta_27b5de16e0(json_data,user_obj):
	I=json_data;F=user_obj;S=I['df'];K=base64.b64decode(S.encode(_P));G=I[_V];A=I.get(_M,_A)
	if A is not _A:A=sparta_fbd037e548(A)
	L=I.get('mode','append');C=datetime.now().astimezone(UTC);B=_A;J=sparta_8bc53bda0e(F)
	if len(J)>0:E=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=J,dataframe_model__table_name=G)|Q(is_delete=0,user=F,dataframe_model__table_name=G))
	else:E=DataFrameShared.objects.filter(is_delete=0,user=F,dataframe_model__table_name=G)
	M=E.count()
	if M==0:
		N=slugify(G);D=N;O=1
		while DataFrameModel.objects.filter(slug=D).exists():D=f"{N}-{O}";O+=1
		T=DataFrameModel.objects.create(table_name=G,slug=D,date_created=C,last_update=C);H=ShareRights.objects.create(is_admin=_D,has_write_rights=_D,has_reshare_rights=_D,last_update=C);B=DataFrameShared.objects.create(dataframe_model=T,user=F,date_created=C,share_rights=H,is_owner=_D)
	elif M==1:B=E[0];D=B.dataframe_model.slug
	else:
		if D is _A:return{_B:-1,_E:_W}
		if len(J)>0:E=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=J,dataframe_model__slug=D)|Q(is_delete=0,user=F,dataframe_model__slug=D))
		else:E=DataFrameShared.objects.filter(is_delete=0,user=F,dataframe_model__slug=D)
		if E.count()==1:B=E[0]
		else:return{_B:-1,_E:'Invalid slug'}
	if B is not _A:
		if A is _A:A=C.strftime(_X)
		if isinstance(A,list):
			P=pickle.loads(K)
			if len(A)==len(P):
				if L==_S:
					H=B.share_rights
					if H.is_admin:DataFrameHistory.objects.filter(dataframe_model=B.dataframe_model,dispo__in=A).delete()
				R=[]
				for(U,V)in enumerate(A):W=pickle.dumps(P.iloc[U].to_frame().T);R.append(DataFrameHistory(dataframe_model=B.dataframe_model,df_blob=W,dispo=V,date_created=C,last_update=C))
				DataFrameHistory.objects.bulk_create(R,batch_size=500)
			else:return{_B:-1,_E:_y}
		else:
			if L==_S:
				H=B.share_rights
				if H.is_admin:
					X=DataFrameHistory.objects.filter(dataframe_model=B.dataframe_model,dispo=A)
					for Y in X:Y.delete()
			DataFrameHistory.objects.create(dataframe_model=B.dataframe_model,df_blob=K,dispo=A,date_created=C,last_update=C)
		return{_B:1,_I:D}
	return{_B:-1}
def sparta_8aad5190e6(json_data,user_obj):
	C=json_data;print('DEBUG put_df_from_gui');A=json.loads(C[_H]);B=A[_T]
	if isinstance(B[0],list)or isinstance(B[0],tuple):E=[tuple(A)for A in B];D=pd.DataFrame(data=A[_H],index=pd.MultiIndex.from_tuples(E),columns=A[_J]).T
	else:D=pd.DataFrame(data=A[_H],index=B,columns=A[_J]).T
	F=D;G=pickle.dumps(F);H=base64.b64encode(G).decode(_P);C['df']=H;I=sparta_27b5de16e0(C,user_obj);return I
def sparta_ff546ed8a8(json_data,user_obj):
	H=json_data;B=user_obj;F=H[_V];D=H.get(_I,_A);E=sparta_8bc53bda0e(B)
	if len(E)>0:A=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=E,dataframe_model__table_name=F)|Q(is_delete=0,user=B,dataframe_model__table_name=F))
	else:A=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model__table_name=F)
	if A.count()==0:return{_B:-1,_E:_z}
	elif A.count()==1:
		C=A[0];G=C.share_rights
		if G.is_admin:C.delete()
	elif D is _A:return{_B:-1,_E:_W}
	else:
		if len(E)>0:A=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=E,dataframe_model__slug=D)|Q(is_delete=0,user=B,dataframe_model__slug=D))
		else:A=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model__slug=D)
		if A.count()==1:
			C=A[0];G=C.share_rights
			if G.is_admin:C.delete()
	return{_B:1}
def sparta_9543b3cc6a(json_data,user_obj):
	G=json_data;B=user_obj;C=G[_M]
	if C is not _A:C=sparta_fbd037e548(C)
	H=G[_V];E=G.get(_I,_A);F=sparta_8bc53bda0e(B)
	if len(F)>0:A=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=F,dataframe_model__table_name=H)|Q(is_delete=0,user=B,dataframe_model__table_name=H))
	else:A=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model__table_name=H)
	if A.count()==0:return{_B:-1,_E:_z}
	elif A.count()==1:
		D=A[0];I=D.share_rights
		if I.is_admin:
			J=DataFrameHistory.objects.filter(dataframe_model=D.dataframe_model,dispo=C)
			for K in J:K.delete()
	elif E is _A:return{_B:-1,_E:_W}
	else:
		if len(F)>0:A=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=F,dataframe_model__slug=E)|Q(is_delete=0,user=B,dataframe_model__slug=E))
		else:A=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model__slug=E)
		if A.count()==1:
			D=A[0];I=D.share_rights
			if I.is_admin:
				J=DataFrameHistory.objects.filter(dataframe_model=D.dataframe_model,dispo=C)
				for K in J:K.delete()
	return{_B:1}
def sparta_e38fbf3333(json_data,user_obj):
	B=user_obj;D=DataFrameModel.objects.filter(id=json_data['id'])
	if D.count()>0:
		A=D[0];E=sparta_8bc53bda0e(B)
		if len(E)>0:C=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=E,dataframe_model=A)|Q(is_delete=0,user=B,dataframe_model=A))
		else:C=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model=A)
		if C.count()==1:
			F=C[0];G=F.share_rights
			if G.is_admin:A.delete();return{_B:1}
			return{_B:-1,_E:"You don't have sufficient rights to drop this object"}
		return{_B:-1,_E:"You don't have the rights to drop this object"}
	return{_B:-1,_E:'Object not found...'}
def sparta_0839dbe1a8(json_data,user_obj):
	C=user_obj;D=sparta_8bc53bda0e(C)
	if len(D)>0:E=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=D)|Q(is_delete=0,user=C))
	else:E=DataFrameShared.objects.filter(is_delete=0,user=C)
	B=[]
	for F in E:G=F.share_rights;A=F.dataframe_model;B.append({_Y:A.table_name,_I:A.slug,_j:A.description,_k:A.is_expose_widget,_l:A.is_public_widget,_m:A.has_widget_password,_A0:str(A.date_created.strftime(_X)),_A1:str(A.last_update.strftime(_A2)),'is_admin':G.is_admin,'has_write_rights':G.has_write_rights,'id':A.id})
	if len(B)>0:B=sorted(B,key=lambda x:x['id'],reverse=_D)
	return{_B:1,'available_df':B}
def sparta_911c15915b(json_data,user_obj):
	N='is_encoded_blob';I=json_data;D=user_obj;E=I.get(_V,_A);G=I.get(_I,_A);C=I.get(_M,_A)
	if C is not _A:C=sparta_fbd037e548(C)
	H=sparta_8bc53bda0e(D)
	if E is not _A:
		if len(H)>0:B=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=H,dataframe_model__table_name=E)|Q(is_delete=0,user=D,dataframe_model__table_name=E))
		else:B=DataFrameShared.objects.filter(is_delete=0,user=D,dataframe_model__table_name=E)
		if B.count()==0:return{_B:-1,_E:'You do not have the rights to get this dataframe'}
	A=_A
	if E is not _A:
		if B.count()==1:A=B[0]
	if A is _A:
		if G is _A:return{_B:-1,_E:_W}
		else:
			if len(H)>0:B=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=H,dataframe_model__slug=G)|Q(is_delete=0,user=D,dataframe_model__slug=G))
			else:B=DataFrameShared.objects.filter(is_delete=0,user=D,dataframe_model__slug=G)
			if B.count()==1:A=B[0]
	if A is not _A:
		if A.dataframe_model.is_dataframe_connector:K=json.loads(A.dataframe_model.connector_config);K[_n]=1;from project.sparta_440f6a201b.sparta_aea4c35167 import qube_477699d437 as O;F=O.sparta_eadb378663(K,D);F=json.loads(F[_H]);P=pd.DataFrame(F[_H],index=F[_J],columns=F[_T]);return{_B:1,_o:_D,_A3:P,_Z:A.dataframe_model.table_name,N:_C}
		else:
			if C is _A:J=DataFrameHistory.objects.filter(dataframe_model=A.dataframe_model)
			elif isinstance(C,list):J=DataFrameHistory.objects.filter(dataframe_model=A.dataframe_model,dispo__in=C)
			else:J=DataFrameHistory.objects.filter(dataframe_model=A.dataframe_model,dispo=C)
			L=[]
			for M in J:L.append({_p:M.df_blob,_M:M.dispo})
			R=pickle.dumps(L);S=base64.b64encode(R).decode(_P);return{_B:1,_A4:S,_Z:A.dataframe_model.table_name,_o:_C,N:_C}
	return{_B:1,'df':[]}
def sparta_6e66dcb290(json_data,user_obj):
	G=user_obj;E=json_data;K=E[_I];L=E[_a];A=E.get(_M,_A)
	if A is not _A:A=sparta_fbd037e548(A)
	C=sparta_4c904163ac(K,G,L)
	if C[_B]==1:
		B=C[_L]
		if B.dataframe_model.is_dataframe_connector:H=json.loads(B.connector_config);H[_n]=1;from project.sparta_440f6a201b.sparta_aea4c35167 import qube_477699d437 as M;D=M.sparta_eadb378663(H,G);D=json.loads(D[_H]);N=pd.DataFrame(D[_H],index=D[_J],columns=D[_T]);return{_B:1,_o:_D,_A3:N,_Z:B.table_name}
		else:
			if A is _A:F=DataFrameHistory.objects.filter(dataframe_model=B)
			elif isinstance(A,list):F=DataFrameHistory.objects.filter(dataframe_model=B,dispo__in=A)
			else:F=DataFrameHistory.objects.filter(dataframe_model=B,dispo=A)
			I=[]
			for J in F:I.append({_p:J.df_blob,_M:J.dispo})
			O=pickle.dumps(I);P=base64.b64encode(O).decode(_P);C[_A4]=P;C[_Z]=B.table_name,
	return C
def sparta_68a1257cc0(slug,user_obj,dispo):
	C=user_obj;B=slug;A=dispo
	if A is not _A:A=sparta_fbd037e548(A)
	G=sparta_8bc53bda0e(C)
	if len(G)>0:D=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=G,dataframe_model__slug=B)|Q(is_delete=0,user=C,dataframe_model__slug=B))
	else:D=DataFrameShared.objects.filter(is_delete=0,user=C,dataframe_model__slug=B)
	if D.count()==1:
		E=D[0]
		if A is _A:F=DataFrameHistory.objects.filter(dataframe_model=E.dataframe_model)
		elif isinstance(A,list):F=DataFrameHistory.objects.filter(dataframe_model=E.dataframe_model,dispo__in=A)
		else:F=DataFrameHistory.objects.filter(dataframe_model=E.dataframe_model,dispo=A)
		return[pickle.loads(A.df_blob).assign(dispo=A.dispo)for A in F]
	return[]
def sparta_78119e24e6(dataframe_model,dispo):
	B=dataframe_model;A=dispo
	if A is not _A:A=sparta_fbd037e548(A)
	if A is _A:C=DataFrameHistory.objects.filter(dataframe_model=B)
	elif isinstance(A,list):C=DataFrameHistory.objects.filter(dataframe_model=B,dispo__in=A)
	else:C=DataFrameHistory.objects.filter(dataframe_model=B,dispo=A)
	return[pickle.loads(A.df_blob).assign(dispo=A.dispo)for A in C]
def sparta_681e3260f2(json_data,user_obj):
	C=user_obj;B=json_data;I=B.get(_Y,'');D=B.get(_I,_A);J=B.get(_j,'');F=sparta_8bc53bda0e(C)
	if len(F)>0:E=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=F,dataframe_model__slug=D)|Q(is_delete=0,user=C,dataframe_model__slug=D))
	else:E=DataFrameShared.objects.filter(is_delete=0,user=C,dataframe_model__slug=D)
	if E.count()==0:return{_B:-1,_E:_A5}
	K=datetime.now().astimezone(UTC);L=E[0];A=L.dataframe_model;A.table_name=I;A.description=J;G=_A;H=B[_m]
	if H:M=B['widget_password'];G=qube_2fc75b9545.sparta_cba0981627(M)
	A.is_expose_widget=B[_k];A.is_public_widget=B[_l];A.has_widget_password=H;A.widget_password_e=G;A.last_update=K;A.save();return{_B:1}
def sparta_f913ef822e(json_data,user_obj):
	A=user_obj;B=json_data.get(_I,_A);D=sparta_8bc53bda0e(A)
	if len(D)>0:C=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=D,dataframe_model__slug=B)|Q(is_delete=0,user=A,dataframe_model__slug=B))
	else:C=DataFrameShared.objects.filter(is_delete=0,user=A,dataframe_model__slug=B)
	if C.count()==1:E=C[0];F=E.dataframe_model;return F
def sparta_3bfecc12de(json_data,user_obj):
	A=sparta_f913ef822e(json_data,user_obj)
	if A is not _A:return{_B:1,'config':A.dataframe_config}
	return{_B:-1,_E:_A6}
def sparta_ca1b6cb709(json_data,user_obj):
	try:A=sparta_58d86dc18c(json_data[_I],user_obj);B=A[_b];return{_B:1,_b:B}
	except:pass
	return{_B:-1}
def sparta_01be4c7361(json_data,user_obj):
	J='plot_chart_id';C=user_obj;A=json_data;E=A[_I];G=sparta_8bc53bda0e(C)
	if len(G)>0:F=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=G,dataframe_model__slug=E)|Q(is_delete=0,user=C,dataframe_model__slug=E))
	else:F=DataFrameShared.objects.filter(is_delete=0,user=C,dataframe_model__slug=E)
	if F.count()==0:return{_B:-1,_E:_A5}
	K=datetime.now().astimezone(UTC);L=F[0];B=L.dataframe_model;B.dataframe_config=A['config'];B.last_update=K;B.save();M=A.get('plotDBConfig',_A);print('save_config_dataframe json_data');print(A);print(A.keys())
	if M is not _A:
		from project.sparta_440f6a201b.sparta_aea4c35167 import qube_477699d437 as H;A['plotName']=B.table_name;A['is_created_from_dataframe']=_D
		if str(A.get(J,_c))==_c:
			N=_D;D=H.sparta_915988ea54(A,C,N);print('res_dict create save plot');print(D)
			if D[_B]==1:I=D['plot_db_chart_obj'];B.plot_db_chart=I;B.save();return{_B:1,J:I.plot_chart_id}
		else:D=H.sparta_9ea4182302(A,C);print('res_dict update plot');print(D)
	return{_B:1}
def sparta_b34d5da82a(json_data,user_obj):
	B=json_data;print('json_data create_dataframe_from_connector');print(B);B[_n]=1;D=B['connector_name'];C=datetime.now().astimezone(UTC);E=slugify(D);A=E;F=1
	while DataFrameModel.objects.filter(slug=A).exists():A=f"{E}-{F}";F+=1
	A=A.lower();G=DataFrameModel.objects.create(table_name=D,slug=A,date_created=C,is_dataframe_connector=_D,connector_config=json.dumps(B),last_update=C);H=ShareRights.objects.create(is_admin=_D,has_write_rights=_D,has_reshare_rights=_D,last_update=C);I=DataFrameShared.objects.create(dataframe_model=G,user=user_obj,date_created=C,share_rights=H,is_owner=_D);return{_B:1,_I:A}
def sparta_3e95bf1734(json_data,user_obj):
	B=json_data;A=pd.DataFrame(B[_A7]);C=B[_A8]
	if C is not _A:
		if len(C)>0:D=A.columns;A=A[D[0]].str.split(C,expand=_D)
	if B[_A9]:A.columns=A.iloc[0];A=A[1:].reset_index(drop=_D)
	if B[_AA]:A=A.set_index(A.columns[0])
	E=A.to_html();return{_B:1,'table':E}
def sparta_8865623e21(json_data,user_obj):
	F=json_data;I=_S;J=F[_Y];C=F.get(_M,_A);B=datetime.now().astimezone(UTC);A=pd.DataFrame(F[_A7]);H=F[_A8]
	if H is not _A:
		if len(H)>0:N=A.columns;A=A[N[0]].str.split(H,expand=_D)
	if F[_A9]:A.columns=A.iloc[0];A=A[1:].reset_index(drop=_D)
	if F[_AA]:A=A.set_index(A.columns[0])
	K=slugify(J);D=K;L=1
	while DataFrameModel.objects.filter(slug=D).exists():D=f"{K}-{L}";L+=1
	D=D.lower();O=DataFrameModel.objects.create(table_name=J,slug=D,date_created=B,last_update=B);G=ShareRights.objects.create(is_admin=_D,has_write_rights=_D,has_reshare_rights=_D,last_update=B);E=DataFrameShared.objects.create(dataframe_model=O,user=user_obj,date_created=B,share_rights=G,is_owner=_D)
	if E is not _A:
		if C is _A:C=B.strftime(_X)
		if isinstance(C,list):
			if len(C)==len(A):
				if I==_S:
					G=E.share_rights
					if G.is_admin:DataFrameHistory.objects.filter(dataframe_model=E.dataframe_model,dispo__in=C).delete()
				M=[]
				for(P,Q)in enumerate(C):R=pickle.dumps(A.iloc[P].to_frame().T);M.append(DataFrameHistory(dataframe_model=E.dataframe_model,df_blob=R,dispo=Q,date_created=B,last_update=B))
				DataFrameHistory.objects.bulk_create(M,batch_size=500)
			else:return{_B:-1,_E:_y}
		else:
			if I==_S:
				G=E.share_rights
				if G.is_admin:
					S=DataFrameHistory.objects.filter(dataframe_model=E.dataframe_model,dispo=C)
					for T in S:T.delete()
			U=pickle.dumps(A);DataFrameHistory.objects.create(dataframe_model=E.dataframe_model,df_blob=U,dispo=C,date_created=B,last_update=B)
		return{_B:1,_I:D}
	return{_B:1,_I:D}
def sparta_99146e8742(json_data,user_obj):
	C=user_obj;A=json_data;D=A.get(_M,_A);E=A[_I]
	if A.get(_a,_A)is not _A:
		F=sparta_4c904163ac(E,C,A[_a])
		if F[_B]==1:H=F[_L];G=sparta_78119e24e6(H,D)
		else:return{_B:-1,_a:_d,_E:_d}
	else:G=sparta_68a1257cc0(E,C,D)
	try:B=pd.concat(G);B=process_dataframe_components(B);I=B.describe();return{_B:1,_H:I.to_json(orient='split')}
	except Exception as J:return{_B:-1,_E:'Cannot compute the statistics for this object. Make sure all dataframes are stored with the same data/columns structure','errorMsg2':str(J)}
def sparta_4240097500(json_data,user_obj):
	A=json.loads(json_data[_H]);B=A[_T]
	if isinstance(B[0],list)or isinstance(B[0],tuple):D=[tuple(A)for A in B];C=pd.DataFrame(data=A[_H],index=pd.MultiIndex.from_tuples(D),columns=A[_J]).T
	elif len(A[_H])==len(A[_J]):C=pd.DataFrame(data=A[_H],columns=B,index=A[_J])
	else:C=pd.DataFrame(data=A[_H],index=B,columns=A[_J]).T
	try:E=C.describe();return{_B:1,_H:E.to_json(orient='split')}
	except Exception as F:G=traceback.format_exc();print('this_traceback Get statistics from GUI dataframe');print(G);return{_B:-1,_E:str(F)}
def sparta_8e2c9a3ca3(data_df,json_data):
	G='differencingDict';C=json_data;B=data_df
	for(A,D)in C['logTransformationDict'].items():
		if D:B[A]=B[A].apply(lambda x:math.log(x))
	for(A,D)in C[G].items():
		if D:
			E=C.get(G,_A)
			if E is not _A:
				F=E.get(A,0)
				if F!=0:B[A]=B[A]-B[A].shift(F)
	return B
def sparta_cabc527dee(json_data):
	E=json_data;F=E.get('isFilterDispo',_C);A=json.loads(E[_H]);B=A[_T]
	if F:
		if isinstance(B[0],list)or isinstance(B[0],tuple):D=[tuple(A)for A in B];C=pd.DataFrame(data=A[_H],columns=pd.MultiIndex.from_tuples(D),index=A[_J])
		else:C=pd.DataFrame(data=A[_H],index=A[_J],columns=B)
	elif isinstance(B[0],list)or isinstance(B[0],tuple):D=[tuple(A)for A in B];C=pd.DataFrame(data=A[_H],index=pd.MultiIndex.from_tuples(D),columns=A[_J]).T
	else:C=pd.DataFrame(data=A[_H],index=B,columns=A[_J]).T
	C[_AB]=C.index;return C
def sparta_27b9007db3(json_data,user_obj):
	B=json_data;from.qube_6bb6acd30c import analyze_columns;A=sparta_cabc527dee(B);C=list(A.columns)
	try:A=sparta_8e2c9a3ca3(A,B);D=sparta_5f2014e95d(A,C,B_DARK_THEME=B.get(_F,_C));return{_B:1,_q:json.dumps(D,allow_nan=_C)}
	except Exception as E:F=traceback.format_exc();print('this_traceback > ');print(F);return{_B:-1,_E:str(E)}
def sparta_069abb2a3b(json_data,user_obj):
	B=json_data;from.qube_6bb6acd30c import analyze_columns_corr;A=sparta_cabc527dee(B);C=list(A.columns);C=[A for A in C if A!=_AB]
	try:A=sparta_8e2c9a3ca3(A,B);D=sparta_d4b84bc707(A,C,B_DARK_THEME=B.get(_F,_C));return{_B:1,_q:json.dumps(D,allow_nan=_C)}
	except Exception as E:F=traceback.format_exc();print(_r);print(F);return{_B:-1,_E:str(E)}
def sparta_3b0fd4fb91(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import time_series_analysis;B=sparta_cabc527dee(A)
	try:C=A['datesCol'];D=A['returnsCols'];E=sparta_b096ddf5ae(B,C,D,B_DARK_THEME=A.get(_F,_C),start_date=A.get('startDate',_A),end_date=A.get('endDate',_A),date_type=A.get('horizonType',_A));return{_B:1,_q:json.dumps(E,allow_nan=_C)}
	except Exception as F:G=traceback.format_exc();print(_r);print(G);return{_B:-1,_E:str(F)}
def sparta_ef0c5fb143(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import relationship_explorer;B=sparta_cabc527dee(A)
	try:B=sparta_8e2c9a3ca3(B,A);C=sparta_f05595937d(B,A['selectedY'],A[_N],in_sample=A.get(_Q,_C),test_size=1-float(A.get(_O,80))/100,rw_beta=int(A['rw_beta']),rw_corr=int(A['rw_corr']),B_DARK_THEME=A.get(_F,_C));return{_B:1,'relationship_explorer':json.dumps(C)}
	except Exception as D:E=traceback.format_exc();print(_r);print(E);return{_B:-1,_E:str(D)}
def sparta_b5bf3ee9ea(json_data,user_obj):
	D=user_obj;E=json_data.get(_I,_A);G=sparta_8bc53bda0e(D)
	if len(G)>0:F=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=G,dataframe_model__slug=E)|Q(is_delete=0,user=D,dataframe_model__slug=E))
	else:F=DataFrameShared.objects.filter(is_delete=0,user=D,dataframe_model__slug=E)
	if F.count()==1:
		K=F[0];A=K.dataframe_model;L=DataFrameHistory.objects.filter(dataframe_model=A);H=[];B=0
		for I in L:
			C=I.df_blob;J=I.dispo;H.append({_p:C,_M:J})
			if isinstance(C,bytes):B+=len(C)
			else:B+=len(str(C).encode(_P))
			B+=len(str(J).encode(_P))
		M=str(A.date_created.strftime(_X));N=str(A.last_update.strftime(_A2));return{_B:1,'infos':{'row_nb':len(H),'size':B,_A1:N,_A0:M,_Y:A.table_name,_I:A.slug,_j:A.description,_k:A.is_expose_widget,_l:A.is_public_widget,_m:A.has_widget_password}}
	return{_B:-1,_E:_A6}
def sparta_cf6da542e2(json_data,user_obj):
	def A():
		try:import sklearn;return _D
		except ImportError:return _C
	return{_B:1,'is_sklearn_installed':A()}
def sparta_097b2a36e1(package_name):
	F='output';E='success';C=package_name;print(f"install package: {C}");B=subprocess.Popen([sys.executable,'-m','pip','install',C],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=_D,bufsize=1);A=''
	for D in B.stdout:print(D,end='');A+=D
	B.wait()
	if B.returncode==0:return{_B:1,E:_D,F:A,_e:_D}
	else:return{_B:-1,E:_C,F:A,_e:_C,_E:A}
def sparta_fdb5759b10(json_data,user_obj):A=sparta_097b2a36e1(_s);return A
def sparta_84396d334b(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_pca;B=sparta_cabc527dee(A)
	try:C=sparta_06c7ea30b8(B,y_cols=A['pcaDataset'],n_components=A[_f],explained_variance=A['nbComponentsVariance'],scale=A['bScalePCA'],components_mode=A['pcaComponentsMode'],B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print('this_traceback PCA');print(E);return{_B:-1,_E:str(D)}
def sparta_e86279a988(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_clustering_kmeans,run_clustering_dbscan;B=sparta_cabc527dee(A)
	try:
		if A['clusteringModel']=='Kmean':C=sparta_b4a37f18ef(B,y_cols=A[_G],n_clusters=A[_f],B_DARK_THEME=A.get(_F,_C))
		else:C=sparta_e6c3702b37(B,y_cols=A[_G],min_samples=A['minSamples'],epsilon=A['epsilon'],B_DARK_THEME=A.get(_F,_C))
		return C
	except Exception as D:E=traceback.format_exc();print(_g);print(E);return{_B:-1,_E:str(D)}
def sparta_e3bfee67bd(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_correlation_network;B=sparta_cabc527dee(A)
	try:C=sparta_e3bfee67bd(B,y_cols=A[_U],threshold=A['threshold'],B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_g);print(E);return{_B:-1,_E:str(D)}
def sparta_6d46e6685e(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_tsne;B=sparta_cabc527dee(A)
	try:C=sparta_6d46e6685e(B,y_cols=A[_U],n_components=A[_f],perplexity=A[_AC],B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_g);print(E);return{_B:-1,_E:str(D)}
def sparta_51fd438074(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_polynomial_regression;B=sparta_cabc527dee(A)
	try:C=sparta_51fd438074(B,y_target=A[_K],x_cols=A[_N],degree=int(A.get('degree',2)),in_sample=A.get(_Q,_D),standardize=A.get('bNormalizePolyReg',_D),test_size=1-float(A.get(_O,80))/100,B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_R);print(E);return{_B:-1,_E:str(D)}
def sparta_2a87d415df(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_decision_tree_regression;C=sparta_cabc527dee(A)
	try:
		B=A['maxDepth']
		if str(B)==_c:B=_A
		else:B=int(B)
		D=sparta_2a87d415df(C,y_target=A[_K],x_cols=A[_N],max_depth=B,in_sample=A.get(_Q,_C),standardize=A.get(_h,_D),test_size=1-float(A.get(_O,80))/100,B_DARK_THEME=A.get(_F,_C));return D
	except Exception as E:F=traceback.format_exc();print(_R);print(F);return{_B:-1,_E:str(E)}
def sparta_f051b4183e(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_decision_tree_regression_grid_search;C=sparta_cabc527dee(A)
	try:
		B=A['maxDepth']
		if str(B)==_c:B=_A
		else:B=int(B)
		D=sparta_f051b4183e(C,y_target=A[_K],x_cols=A[_N],max_depth=B,in_sample=A.get(_Q,_C),standardize=A.get(_h,_D),test_size=1-float(A.get(_O,80))/100,B_DARK_THEME=A.get(_F,_C));return D
	except Exception as E:F=traceback.format_exc();print(_R);print(F);return{_B:-1,_E:str(E)}
def sparta_73aa49e98e(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_random_forest_regression;B=sparta_cabc527dee(A)
	try:C=sparta_73aa49e98e(B,y_target=A[_K],x_cols=A[_N],standardize=A.get(_h,_D),max_depth=A.get(_t,_A),in_sample=A.get(_Q,_C),test_size=1-float(A.get(_O,80))/100,B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_R);print(E);return{_B:-1,_E:str(D)}
def sparta_c8a32aa802(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_random_forest_regression_grid_search;B=sparta_cabc527dee(A)
	try:C=sparta_c8a32aa802(B,y_target=A[_K],x_cols=A[_N],max_depth=A.get(_t,_A),in_sample=A.get(_Q,_C),standardize=A.get(_h,_D),test_size=1-float(A.get(_O,80))/100,B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_R);print(E);return{_B:-1,_E:str(D)}
def sparta_94fbcebb11(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_quantile_regression;B=sparta_cabc527dee(A)
	try:C=sparta_94fbcebb11(B,y_target=A[_K],x_cols=A[_N],quantiles=A.get('selectedQuantiles',[.1,.5,.9]),standardize=A.get('bNormalizeQuantileReg',_D),in_sample=A.get(_Q,_D),test_size=1-float(A.get(_O,80))/100,B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_AD);print(E);return{_B:-1,_E:str(D)}
def sparta_ade8cd9af4(json_data,user_obj):
	A=json_data;print('RUN ROLLING REGRESSION NOW');from.qube_6bb6acd30c import run_rolling_regression;B=sparta_cabc527dee(A)
	try:C=sparta_ade8cd9af4(B,y_target=A[_K],x_cols=A[_N],window=int(A.get('window',20)),standardize=A.get('bNormalizeRollingReg',_D),test_size=1-float(A.get(_O,80))/100,B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print('this_traceback rolling reg');print(E);return{_B:-1,_E:str(D)}
def sparta_752f5aa77e(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_recursive_regression;B=sparta_cabc527dee(A)
	try:C=sparta_752f5aa77e(B,y_target=A[_K],x_cols=A[_N],standardize=A.get('bNormalizeRecursiveReg',_D),B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_AD);print(E);return{_B:-1,_E:str(D)}
def sparta_7406d842a2(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_features_importance_randomforest,run_features_importance_xgboost;B=sparta_cabc527dee(A)
	try:
		if A['model']=='Random Forest':C=sparta_3a4046558b(B,y_target=A[_K],x_cols=A[_U],n_estimators=A.get('n_estimators',100),max_depth=A.get(_t,_A),min_samples_split=A.get('min_samples_split',1),min_samples_leaf=A.get('min_samples_leaf',1),max_features=A.get('max_features','sqrt'),bootstrap=A.get('bootstrap',_D),B_DARK_THEME=A.get(_F,_C))
		else:C=sparta_9063bce3ba(B,y_cols=A[_U],n_components=A[_f],perplexity=A[_AC],B_DARK_THEME=A.get(_F,_C))
		return C
	except Exception as D:E=traceback.format_exc();print(_g);print(E);return{_B:-1,_E:str(D)}
def sparta_c9339c3718(json_data,user_obj):
	A=json_data;from.qube_6bb6acd30c import run_mutual_information;B=sparta_cabc527dee(A)
	try:C=sparta_c9339c3718(B,y_target=A[_K],x_cols=A[_U],B_DARK_THEME=A.get(_F,_C));return C
	except Exception as D:E=traceback.format_exc();print(_R);print(E);return{_B:-1,_E:str(D)}
def sparta_89738e918d(json_data,user_obj):
	B=json_data['lib'];D=_A;A=_C
	if B==_u:
		try:import arch;A=_D
		except ImportError:A=_C
	elif B==_v:
		try:
			import pywt;A=_D;E=[]
			if A:import pywt;E=pywt.wavelist()
			return{_B:1,_e:A,'families':E}
		except ImportError:A=_C
	elif B==_i:
		try:import ruptures as F;A=_D
		except ImportError:A=_C
	elif B=='sklearn':
		try:import sklearn;A=_D
		except ImportError:A=_C
	elif B==_w:
		try:from prophet import Prophet;A=_D
		except ImportError:A=_C
	elif B==_x:
		try:import keras;A=_D
		except ModuleNotFoundError as C:print(f"module not found: {C}");A=_C
		except Exception as C:print(f"Exception found: {C}");A=_C;D=str(C)
	return{_B:1,_e:A,'install_but_import_errors':D}
def sparta_1a807770cf(json_data,user_obj):
	B=json_data['lib']
	if B==_u:A=sparta_097b2a36e1(_u)
	elif B==_v:A=sparta_097b2a36e1('PyWavelets')
	elif B==_i:A=sparta_097b2a36e1(_i)
	elif B=='sklearn':A=sparta_097b2a36e1(_s)
	elif B==_w:A=sparta_097b2a36e1(_w)
	elif B==_x:
		A=sparta_097b2a36e1(_s)
		if A[_B]==-1:return A
		print('res_dict scikit learn');print(A);A=sparta_097b2a36e1(_x)
		if A[_B]==-1:return A
		print('res_dict KERAS');print(A);A=sparta_097b2a36e1('tensorflow')
		if A[_B]==-1:return A
		print('res_dict TF');print(A)
	return A
def sparta_55dfa6cea5(json_data,user_obj):
	I='dateCol';H='params';A=json_data;import project.sparta_440f6a201b.sparta_9df2ef9f24.qube_2e71f05b54 as F;B=sparta_cabc527dee(A);G=A['tsaModel']
	try:
		if G=='adf':E=A[_G];B=B[E];return F.sparta_4734dcf418(B,A.get(H,_A))
		elif G=='kpss':E=A[_G];B=B[E];return F.sparta_d4b6694972(B,A.get(H,_A))
		elif G=='perron':E=A[_G];B=B[E];return F.sparta_db645b5576(B,A.get(H,_A))
		elif G=='za':E=A[_G];C=A.get(I,_A);D=B[C];B=B[E];return F.sparta_5b69d18710(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='stl':
			E=A[_G];C=A[I];D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_263a48339d(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G==_v:
			E=A[_G];C=A[I];D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_e66c6d99f0(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='hmm':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_dbb470d4cf(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G==_i:
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_597c7a97bf(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='cusum':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_056f487687(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='zscore':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_8d534897e7(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='isolationForest':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_2b48b8254d(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='madMedian':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_21748c5273(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='prophetOutlier':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_71e3d0075f(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='granger':E=A[_G];J=A[_K];K=B[J];B=B[E];return F.sparta_275cc59a5d(B,K,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='cointegration':E=A[_G];J=A[_K];K=B[J];B=B[E];return F.sparta_24b24d296c(B,K,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='canonical_corr':L=A['colDataset1'];M=A['colDataset2'];N=B[L];O=B[M];return F.sparta_76d708a65e(N,O,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='sarima':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_4e55148a12(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='ets':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_2459ee69cc(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='prophetForecast':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_fdc10abe0b(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='lstm':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_5c7e79c879(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
		elif G=='var':
			E=A[_G];C=A.get(I,_A);D=_A
			if C is not _A:
				if len(C)>0:
					try:D=B[C]
					except:D=_A
			B=B[E];return F.sparta_4fe76207b6(B,D,A.get(H,_A),B_DARK_THEME=A.get(_F,_C))
	except Exception as P:Q=traceback.format_exc();print('this_traceback TSA');print(Q);return{_B:-1,_E:str(P)}
def sparta_e45fd842d1(token_permission):
	A=DataFramePermission.objects.filter(token=token_permission);B=A.count()
	if B>0:C=A[B-1];return{_B:1,_L:C.dataframe_model}
	return{_B:-1}
def has_permission_widget_or_shared_rights(dataframe_model_obj,user_obj,password_widget=_A):
	B=user_obj;A=dataframe_model_obj;F=A.has_widget_password;C=_C
	if B.is_authenticated:
		D=sparta_8bc53bda0e(B)
		if len(D)>0:E=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=D,dataframe_model__is_delete=0,dataframe_model=A)|Q(is_delete=0,user=B,dataframe_model__is_delete=0,dataframe_model=A))
		else:E=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model__is_delete=0,dataframe_model=A)
		if E.count()>0:C=_D
	if C:return _D
	if A.is_expose_widget:
		if A.is_public_widget:
			if not F:return _D
			else:
				try:
					if qube_2fc75b9545.sparta_117adcad9c(A.widget_password_e)==password_widget:return _D
					else:return _C
				except:return _C
		else:return _C
	return _C
def sparta_4c904163ac(slug,user_obj,password_widget=_A):
	G=password_widget;F=slug;B=user_obj;logger.debug(f"CHECK NOW has_widget_access: {F}");C=DataFrameModel.objects.filter(slug=F,is_delete=_C).all();D=_C;E=C.count()
	if E==1:D=_D
	if not D:
		C=DataFrameModel.objects.filter(slug__startswith=F,is_delete=_C).all();E=C.count()
		if E==1:D=_D
	if D:
		A=C[E-1];J=A.has_widget_password
		if A.is_expose_widget:
			if A.is_public_widget:
				if not J:return{_B:1,_L:A}
				elif G is _A:return{_B:2,_E:'Require password',_L:A}
				else:
					try:
						if qube_2fc75b9545.sparta_117adcad9c(A.widget_password_e)==G:return{_B:1,_L:A}
						else:return{_B:3,_E:_d,_L:A}
					except:return{_B:3,_E:_d,_L:A}
			elif B.is_authenticated:
				H=sparta_8bc53bda0e(B)
				if len(H)>0:I=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=H,dataframe_model__is_delete=0,dataframe_model=A)|Q(is_delete=0,user=B,dataframe_model__is_delete=0,dataframe_model=A))
				else:I=DataFrameShared.objects.filter(is_delete=0,user=B,dataframe_model__is_delete=0,dataframe_model=A)
				if I.count()>0:return{_B:1,_L:A}
			else:return{_B:-1}
	return{_B:-1}
def sparta_58d86dc18c(slug,user_obj):
	D=user_obj;B=DataFrameModel.objects.filter(slug=slug,is_delete=_C).all();C=_C;E=B.count()
	if E==1:C=_D
	if not C:
		B=DataFrameModel.objects.filter(slug__startswith=slug,is_delete=_C).all();E=B.count()
		if E==1:C=_D
	if C:
		A=B[0];G=sparta_8bc53bda0e(D)
		if len(G)>0:F=DataFrameShared.objects.filter(Q(is_delete=0,user_group__in=G,dataframe_model__is_delete=0,dataframe_model=A)|Q(is_delete=0,user=D,dataframe_model__is_delete=0,dataframe_model=A))
		else:F=DataFrameShared.objects.filter(is_delete=0,user=D,dataframe_model__is_delete=0,dataframe_model=A)
		if F.count()>0:H=F[0];A=H.dataframe_model;return{_B:1,_b:_D,_L:A}
	return{_B:1,_b:_C}