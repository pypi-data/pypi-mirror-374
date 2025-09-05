_U='projectPath'
_T='kernelSize'
_S='kernelVenv'
_R='kernel_size'
_Q='main_ipynb_fullpath'
_P='kernel_manager_uuid'
_O='main.ipynb'
_N='-kernel__last_update'
_M='kernel_cpkl_unpicklable'
_L='kernel'
_K='luminoLayout'
_J='description'
_I='slug'
_H='is_static_variables'
_G=False
_F='unpicklable'
_E='name'
_D='kernelManagerUUID'
_C='res'
_B=True
_A=None
import os,sys,gc,json,base64,shutil,zipfile,io,uuid,subprocess,cloudpickle,platform,getpass
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
from pathlib import Path
from dateutil import parser
import pytz
UTC=pytz.utc
from django.contrib.humanize.templatetags.humanize import naturalday
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
from project.models_spartaqube import Kernel,KernelShared,ShareRights
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import sparta_a253265c85,sparta_0f6223a0af
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
from project.sparta_440f6a201b.sparta_bb5bf030e1.qube_203378cc3e import sparta_8b9995568a,sparta_08311cba71,sparta_f6bb1ee3ba,sparta_ded9e1c030
from project.sparta_440f6a201b.sparta_ceff546bba.qube_467225df75 import sparta_9f1de43185,sparta_46a11b5877
from project.sparta_440f6a201b.sparta_8ade4c4917.qube_b559aa4222 import sparta_ac6c5f1fe5
from project.logger_config import logger
def sparta_446aaafbc7():A=sparta_a4e746f060();B=os.path.join(A,_L);return B
def sparta_8bc53bda0e(user_obj):
	A=qube_2808664dfd.sparta_0a996f3465(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_9f1d797e74(user_obj,kernel_manager_uuid):from project.sparta_440f6a201b.sparta_15c403c94e import qube_d7643b4f9f as B;E=B.sparta_7c02da572c(user_obj,kernel_manager_uuid);A=B.sparta_ebe2fc55ea(E);logger.debug('get_cloudpickle_kernel_variables res_dict');logger.debug(A);C=A['picklable'];logger.debug('kernel_cpkl_picklable');logger.debug(type(C));logger.debug("res_dict['unpicklable']");logger.debug(type(A[_F]));D=cloudpickle.loads(A[_F]);logger.debug(_M);logger.debug(type(D));return C,D
def sparta_564a32970e(user_obj):
	I='%Y-%m-%d';C=user_obj;J=sparta_446aaafbc7();D=sparta_8bc53bda0e(C)
	if len(D)>0:B=KernelShared.objects.filter(Q(is_delete=0,user_group__in=D,kernel__is_delete=0)|Q(is_delete=0,user=C,kernel__is_delete=0))
	else:B=KernelShared.objects.filter(Q(is_delete=0,user=C,kernel__is_delete=0))
	if B.count()>0:B=B.order_by(_N)
	E=[]
	for F in B:
		A=F.kernel;K=F.share_rights;G=_A
		try:G=str(A.last_update.strftime(I))
		except:pass
		H=_A
		try:H=str(A.date_created.strftime(I))
		except Exception as L:logger.debug(L)
		M=os.path.join(J,A.kernel_manager_uuid,_O);E.append({_P:A.kernel_manager_uuid,_E:A.name,_I:A.slug,_J:A.description,_Q:M,_R:A.kernel_size,'has_write_rights':K.has_write_rights,'last_update':G,'date_created':H})
	return E
def sparta_5a76bfbe80(user_obj):
	B=user_obj;C=sparta_8bc53bda0e(B)
	if len(C)>0:A=KernelShared.objects.filter(Q(is_delete=0,user_group__in=C,kernel__is_delete=0)|Q(is_delete=0,user=B,kernel__is_delete=0))
	else:A=KernelShared.objects.filter(Q(is_delete=0,user=B,kernel__is_delete=0))
	if A.count()>0:A=A.order_by(_N);return[A.kernel.kernel_manager_uuid for A in A]
	return[]
def sparta_a5b6d11e41(user_obj,kernel_manager_uuid):
	B=user_obj;D=Kernel.objects.filter(kernel_manager_uuid=kernel_manager_uuid).all()
	if D.count()>0:
		A=D[0];E=sparta_8bc53bda0e(B)
		if len(E)>0:C=KernelShared.objects.filter(Q(is_delete=0,user_group__in=E,kernel__is_delete=0,kernel=A)|Q(is_delete=0,user=B,kernel__is_delete=0,kernel=A))
		else:C=KernelShared.objects.filter(is_delete=0,user=B,kernel__is_delete=0,kernel=A)
		F=_G
		if C.count()>0:
			H=C[0];G=H.share_rights
			if G.is_admin or G.has_write_rights:F=_B
		if F:return A
def sparta_0463d3d862(json_data,user_obj):
	D=user_obj;from project.sparta_440f6a201b.sparta_15c403c94e import qube_d7643b4f9f as I;A=json_data[_D];B=I.sparta_7c02da572c(D,A)
	if B is _A:return{_C:-1,'errorMsg':'Kernel not found'}
	E=sparta_446aaafbc7();J=os.path.join(E,A,_O);K=B.venv_name;F=_A;G=_G;H=_G;C=sparta_a5b6d11e41(D,A)
	if C is not _A:G=_B;F=C.lumino_layout;H=C.is_static_variables
	return{_C:1,_L:{'basic':{'is_kernel_saved':G,_H:H,_P:A,_E:B.name,'kernel_venv':K,'kernel_type':B.type,'project_path':E,_Q:J},'lumino':{'lumino_layout':F}}}
def sparta_ce8fd59797(json_data,user_obj):
	D=user_obj;A=json_data;logger.debug('Save notebook');logger.debug(A);logger.debug(A.keys());L=A['isKernelSaved']
	if L:return sparta_231f23fd97(A,D)
	C=datetime.now().astimezone(UTC);G=A[_D];M=A[_K];N=A[_E];O=A[_J];E=sparta_446aaafbc7();E=sparta_a253265c85(E);H=A[_H];P=A.get(_S,_A);Q=A.get(_T,0);B=A.get(_I,'')
	if len(B)==0:B=A[_E]
	I=slugify(B);B=I;J=1
	while Kernel.objects.filter(slug=B).exists():B=f"{I}-{J}";J+=1
	K=_A;F=[]
	if H:K,F=sparta_9f1d797e74(D,G)
	R=Kernel.objects.create(kernel_manager_uuid=G,name=N,slug=B,description=O,is_static_variables=H,lumino_layout=M,project_path=E,kernel_venv=P,kernel_variables=K,kernel_size=Q,date_created=C,last_update=C,last_date_used=C,spartaqube_version=sparta_ac6c5f1fe5());S=ShareRights.objects.create(is_admin=_B,has_write_rights=_B,has_reshare_rights=_B,last_update=C);KernelShared.objects.create(kernel=R,user=D,share_rights=S,is_owner=_B,date_created=C);logger.debug(_M);logger.debug(F);return{_C:1,_F:F}
def sparta_231f23fd97(json_data,user_obj):
	F=user_obj;A=json_data;logger.debug('update_kernel_notebook');logger.debug(A);D=A[_D];B=sparta_a5b6d11e41(F,D)
	if B is not _A:
		K=datetime.now().astimezone(UTC);D=A[_D];L=A[_K];M=A[_E];N=A[_J];E=A[_H];O=A.get(_S,_A);P=A.get(_T,0);C=A.get(_I,'')
		if len(C)==0:C=A[_E]
		G=slugify(C);C=G;H=1
		while Kernel.objects.filter(slug=C).exists():C=f"{G}-{H}";H+=1
		E=A[_H];I=_A;J=[]
		if E:I,J=sparta_9f1d797e74(F,D)
		B.name=M;B.description=N;B.slug=C;B.kernel_venv=O;B.kernel_size=P;B.is_static_variables=E;B.kernel_variables=I;B.lumino_layout=L;B.last_update=K;B.save()
	return{_C:1,_F:J}
def sparta_16e816c2d0(json_data,user_obj):0
def sparta_c7a9ad1a11(json_data,user_obj):A=sparta_a253265c85(json_data[_U]);return sparta_9f1de43185(A)
def sparta_50b25cf92d(json_data,user_obj):A=sparta_a253265c85(json_data[_U]);return sparta_46a11b5877(A)
def sparta_d1daba2722(json_data,user_obj):
	C=user_obj;B=json_data;logger.debug('SAVE LYUMINO LAYOUT KERNEL NOTEBOOK');logger.debug('json_data');logger.debug(B);I=B[_D];E=Kernel.objects.filter(kernel_manager_uuid=I).all()
	if E.count()>0:
		A=E[0];F=sparta_8bc53bda0e(C)
		if len(F)>0:D=KernelShared.objects.filter(Q(is_delete=0,user_group__in=F,kernel__is_delete=0,kernel=A)|Q(is_delete=0,user=C,kernel__is_delete=0,kernel=A))
		else:D=KernelShared.objects.filter(is_delete=0,user=C,kernel__is_delete=0,kernel=A)
		G=_G
		if D.count()>0:
			J=D[0];H=J.share_rights
			if H.is_admin or H.has_write_rights:G=_B
		if G:K=B[_K];A.lumino_layout=K;A.save()
	return{_C:1}
def sparta_b10c133001(json_data,user_obj):
	from project.sparta_440f6a201b.sparta_15c403c94e import qube_d7643b4f9f as A;C=json_data[_D];B=A.sparta_7c02da572c(user_obj,C)
	if B is not _A:D=A.sparta_46611e2f4c(B);return{_C:1,_R:D}
	return{_C:-1}
def sparta_abda948269(json_data,user_obj):
	B=json_data[_D];A=sparta_a5b6d11e41(user_obj,B)
	if A is not _A:A.is_delete=_B;A.save()
	return{_C:1}