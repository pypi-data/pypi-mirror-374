_W='%Y-%m-%d %H:%M:%S'
_V='created_time'
_U='created_time_str'
_T='workspace_variables'
_S='app.settings'
_R='venvName'
_Q='kernelType'
_P='Windows'
_O='kernel_process_obj'
_N='kernels'
_M='CommandLine'
_L='PID'
_K='spawnKernel.py'
_J='port'
_I='PPID'
_H='kernel_manager_uuid'
_G='-1'
_F=False
_E='name'
_D=True
_C='kernelManagerUUID'
_B='res'
_A=None
import os,sys,gc,socket,subprocess,threading,platform,psutil,zmq,json,base64,shutil,zipfile,io,uuid,cloudpickle
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
from pathlib import Path
from dateutil import parser
import pytz
UTC=pytz.utc
import concurrent.futures
from django.contrib.humanize.templatetags.humanize import naturalday
from project.models import KernelProcess
from project.sparta_440f6a201b.sparta_bb5bf030e1.qube_203378cc3e import sparta_08311cba71,sparta_f6bb1ee3ba,sparta_ded9e1c030
from project.sparta_440f6a201b.sparta_15c403c94e.qube_293080d79c import SenderKernel
from project.logger_config import logger
def sparta_ae569cb250():
	with socket.socket(socket.AF_INET,socket.SOCK_STREAM)as A:A.bind(('',0));return A.getsockname()[1]
class SqKernelManager:
	def __init__(A,kernel_manager_uuid,type,name,user,user_kernel=_A,project_folder=_A,notebook_exec_id=_G,dashboard_exec_id=_G,venv_name=_A):
		C=user_kernel;B=user;A.kernel_manager_uuid=kernel_manager_uuid;A.type=type;A.name=name;A.user=B;A.kernel_user_logged=B;A.project_folder=project_folder
		if C is _A:C=B
		A.user_kernel=C;A.venv_name=venv_name;A.notebook_exec_id=notebook_exec_id;A.dashboard_exec_id=dashboard_exec_id;A.is_init=_F;A.created_time=datetime.now()
	def create_kernel(A,django_settings_module=_A):
		if A.notebook_exec_id!=_G:A.user_kernel=sparta_f6bb1ee3ba(A.notebook_exec_id)
		if A.dashboard_exec_id!=_G:A.user_kernel=sparta_ded9e1c030(A.dashboard_exec_id)
		G=os.path.dirname(__file__);H=sparta_08311cba71(A.user_kernel);C=sparta_ae569cb250();I=sys.executable;J=A.venv_name if A.venv_name is not _A else _G
		def L(pipe):
			for A in iter(pipe.readline,''):logger.debug(A,end='')
			pipe.close()
		E=os.environ.copy();E['ZMQ_PROCESS']='1';logger.debug(f"SPAWN PYTHON KERNEL {C}");K=subprocess.Popen([I,_K,str(H),str(C),J],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=_D,cwd=G,env=E);F=K.pid;D=datetime.now().astimezone(UTC);B=sparta_7c02da572c(A.user,A.kernel_manager_uuid)
		if B is _A:B=KernelProcess.objects.create(kernel_manager_uuid=A.kernel_manager_uuid,port=C,pid=F,date_created=D,user=A.user,name=A.name,type=A.type,notebook_exec_id=A.notebook_exec_id,dashboard_exec_id=A.dashboard_exec_id,venv_name=A.venv_name,project_folder=A.project_folder,last_update=D)
		else:B.port=C;B.pid=F;B.name=A.name;B.type=A.type;B.notebook_exec_id=A.notebook_exec_id;B.dashboard_exec_id=A.dashboard_exec_id;B.venv_name=A.venv_name;B.project_folder=A.project_folder;B.last_update=D;B.save()
		return{_B:1,_O:B}
def sparta_46611e2f4c(kernel_process_obj):A=SenderKernel(websocket=_A,port=kernel_process_obj.port);return A.sync_get_kernel_size()
def sparta_4d4f0ad364(kernel_process_obj):A=SenderKernel(websocket=_A,port=kernel_process_obj.port);return A.sync_get_kernel_workspace_variables()
def sparta_0459def30d(kernel_process_obj,venv_name):A=SenderKernel(websocket=_A,port=kernel_process_obj.port);return A.sync_activate_venv(venv_name)
def sparta_7a57df9d31(kernel_process_obj,kernel_varname):A=SenderKernel(websocket=_A,port=kernel_process_obj.port);return A.sync_get_kernel_variable_repr(kernel_varname)
def sparta_9d598e5126(kernel_process_obj,var_name,var_value):A=SenderKernel(websocket=_A,port=kernel_process_obj.port);return A.sync_set_workspace_variable(var_name,var_value)
def set_workspace_cloudpickle_variables(kernel_process_obj,cloudpickle_kernel_variables):A=SenderKernel(websocket=_A,port=kernel_process_obj.port);return A.sync_set_workspace_cloudpickle_variables(cloudpickle_kernel_variables)
def sparta_ebe2fc55ea(kernel_process_obj):A=SenderKernel(websocket=_A,port=kernel_process_obj.port);return A.sync_get_cloudpickle_kernel_variables()
def sparta_5f69360f09(pid):
	logger.debug('Force Kill Process now from kernel manager')
	if platform.system()==_P:return sparta_92a23ebfc6(pid)
	else:return sparta_793e00ca5a(pid)
def sparta_92a23ebfc6(pid):
	try:subprocess.run(['taskkill','/F','/PID',str(pid)],check=_D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	except subprocess.CalledProcessError:logger.debug(f"Failed to kill process {pid}. It may not exist.")
def sparta_793e00ca5a(pid):
	try:subprocess.run(['kill','-9',str(pid)],check=_D,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	except subprocess.CalledProcessError:logger.debug(f"Failed to kill process {pid}. It may not exist.")
def sparta_65dfbcb099(kernel_process_obj):A=kernel_process_obj.pid;sparta_5f69360f09(A)
def sparta_7c02da572c(user_obj,kernel_manager_uuid):
	A=KernelProcess.objects.filter(user=user_obj,kernel_manager_uuid=kernel_manager_uuid,is_delete=_F)
	if A.count()>0:return A[0]
def sparta_b86cc7add4(json_data,user_obj,b_return_model=_F):
	E=user_obj;A=json_data;logger.debug('Create new kernel');logger.debug(A);H=A[_C];B=int(A[_Q]);I=A.get(_E,'undefined');C=A.get('fullpath',_A);J=A.get('notebookExecId',_G);K=A.get('dashboardExecId',_G);D=A.get(_R,'')
	if len(D)==0:D=_A
	if C is not _A:C=os.path.dirname(C)
	F=SqKernelManager(H,B,I,E,user_kernel=E,project_folder=C,notebook_exec_id=J,dashboard_exec_id=K,venv_name=D)
	if B==3 or B==4 or B==5:G=F.create_kernel(django_settings_module=_S)
	else:G=F.create_kernel()
	if b_return_model:return G
	return{_B:1}
def sparta_bbf42a8527(json_data,user_obj):
	C=user_obj;D=json_data[_C];A=sparta_7c02da572c(C,D)
	if A is not _A:
		sparta_65dfbcb099(A);B=A.type;F=A.name;G=A.project_folder;H=A.notebook_exec_id;I=A.dashboard_exec_id;J=A.user_kernel;K=A.venv_name;E=SqKernelManager(D,B,F,C,user_kernel=J,project_folder=G,notebook_exec_id=H,dashboard_exec_id=I,venv_name=K)
		if B==3 or B==4 or B==5:E.create_kernel(django_settings_module=_S)
		else:E.create_kernel()
	return{_B:1}
def sparta_95166193a9(json_data,user_obj):
	A=json_data
	if _C in A:
		C=A[_C];D=A['env_name'];B=sparta_7c02da572c(user_obj,C)
		if B is not _A:sparta_0459def30d(B,D)
	return{_B:1}
def sparta_d243bf97df(json_data,user_obj):
	B=json_data[_C];A=sparta_7c02da572c(user_obj,B)
	if A is not _A:C=sparta_46611e2f4c(A);D=sparta_4d4f0ad364(A);return{_B:1,'kernel':{_T:D,_H:B,'kernel_size':C,'type':A.type,_E:A.name,_U:str(A.date_created.strftime(_W)),_V:naturalday(parser.parse(str(A.date_created)))}}
	return{_B:-1}
def sparta_a3afa0fa20(json_data,user_obj):
	A=json_data;C=A[_C];D=A['varName'];B=sparta_7c02da572c(user_obj,C)
	if B is not _A:E=sparta_7a57df9d31(B,D);return{_B:1,'htmlReprDict':E}
	return{_B:-1}
def sparta_dd144f25cf(json_data,user_obj):
	C=json_data;D=C[_C];A=sparta_7c02da572c(user_obj,D)
	if A is not _A:
		B=C.get(_E,_A)
		if B is not _A:A.name=B;A.save();sparta_9d598e5126(A,_E,B)
	return{_B:1}
def sparta_665e27f393():
	if platform.system()==_P:return sparta_9bf7baf987()
	else:return sparta_285c083138()
def sparta_73fcdaace2(command):
	with concurrent.futures.ThreadPoolExecutor()as A:B=A.submit(subprocess.run,command,shell=_D,capture_output=_D,text=_D);C=B.result();return C.stdout.strip()
def sparta_9bf7baf987():return sparta_f13f9d51ab()
def sparta_0459db4eda():
	G='cmdline';F='ppid';E='pid';import psutil as C;D=[]
	try:
		for A in C.process_iter([E,F,_E,G]):
			try:
				if not A.info[_E]or'python'not in A.info[_E].lower():continue
				B=A.info.get(G)or[]
				if any(_K in A for A in B):H=B[3]if len(B)>3 else _A;D.append({_L:str(A.info[E]),_I:str(A.info[F]),_M:' '.join(B),_J:H})
			except(C.NoSuchProcess,C.AccessDenied):continue
	except Exception as I:logger.error(f"Unexpected error finding spawnKernel.py: {I}")
	return D
def sparta_f13f9d51ab():
	try:
		G=subprocess.check_output(['tasklist'],text=_D);D=[]
		for E in G.splitlines():
			if'python.exe'in E.lower():
				B=E.split()
				if len(B)>=2 and B[1].isdigit():D.append(int(B[1]))
		F=[]
		for H in D:
			try:
				C=psutil.Process(H);A=C.cmdline()
				if any(_K in A for A in A):I=A[3]if len(A)>3 else _A;F.append({_L:str(C.pid),_I:str(C.ppid()),_M:' '.join(A),_J:I})
			except(psutil.NoSuchProcess,psutil.AccessDenied):continue
		return F
	except Exception as J:print(f"Error: {J}");return[]
def sparta_70f0579d60():
	try:
		E='wmic process where "name=\'python.exe\'" get ProcessId,ParentProcessId,CommandLine /FORMAT:CSV';F=sparta_73fcdaace2(E);C=[];G=F.splitlines()
		for H in G[2:]:
			A=[A.strip()for A in H.split(',')]
			if len(A)<4:continue
			B=A[1];I=A[2];J=A[3]
			if _K in B:D=B.split();K=D[3]if len(D)>3 else _A;C.append({_L:I,_I:J,_M:B,_J:K})
		return C
	except Exception as L:logger.error(f"Unexpected error finding spawnKernel.py: {L}");return[]
def sparta_285c083138():
	try:
		F=sparta_73fcdaace2("ps -eo pid,ppid,command | grep '[s]pawnKernel.py'");A=[];G=F.split('\n')
		for H in G:
			B=H.strip().split(maxsplit=2)
			if len(B)<3:continue
			C,K,D=B;E=D.split();I=E[3]if len(E)>3 else _A;A.append({_L:C,_I:C,_M:D,_J:I})
		return A
	except Exception as J:logger.error(f"Unexpected error finding spawnKernel.py: {J}");return[]
def sparta_95bf147e32(json_data,user_obj):
	D=user_obj;B=json_data;I=B.get('b_require_size',_F);J=B.get('b_require_workspace_variables',_F);K=B.get('b_require_offline_kernels',_F);E=[]
	if K:from project.sparta_440f6a201b.sparta_5119509781 import qube_7009eb8c53 as L;E=L.sparta_5a76bfbe80(D)
	M=sparta_665e27f393();F=[];C=[(A[_I],A[_J])for A in M]
	if len(C)>0:
		N=KernelProcess.objects.filter(pid__in=[A[0]for A in C],port__in=[A[1]for A in C],user=D).distinct()
		for A in N:
			G=_A
			if I:G=sparta_46611e2f4c(A)
			H=[]
			if J:H=sparta_4d4f0ad364(A)
			F.append({_H:A.kernel_manager_uuid,_T:H,'type':A.type,_E:A.name,_U:str(A.date_created.strftime(_W)),_V:naturalday(parser.parse(str(A.date_created))),'size':G,'isStored':_D if A.kernel_manager_uuid in E else _F})
	return{_B:1,_N:F}
def sparta_722ba074bc(json_data,user_obj):
	B=user_obj;from project.sparta_440f6a201b.sparta_5119509781 import qube_7009eb8c53 as D;A=D.sparta_564a32970e(B);C=sparta_95bf147e32(json_data,B)
	if C[_B]==1:E=C[_N];F=[A[_H]for A in E];A=[A for A in A if A[_H]not in F];return{_B:1,'kernel_library':A}
	return{_B:-1}
def sparta_dd2c3017b5(json_data,user_obj):
	B=json_data[_C];A=sparta_7c02da572c(user_obj,B)
	if A is not _A:sparta_65dfbcb099(A)
	return{_B:1}
def sparta_c9f977a93c(json_data,user_obj):
	A=user_obj;B=sparta_95bf147e32(json_data,A)
	if B[_B]==1:
		C=B[_N]
		for D in C:E={_C:D[_H]};sparta_dd2c3017b5(E,A)
	return{_B:1}
def sparta_7cb29e2780():
	B='cypress_tests@gmail.com';C=KernelProcess.objects.filter(user__email=B,is_delete=_F)
	for A in C:print(f"Kill kernel: {A}");sparta_65dfbcb099(A)
	return{_B:1}
def sparta_3a1a5b337d(json_data,user_obj):
	C=user_obj;B=json_data;D=B[_C];from project.sparta_440f6a201b.sparta_5119509781 import qube_7009eb8c53 as I;G=I.sparta_a5b6d11e41(C,D);A=sparta_7c02da572c(C,D)
	if A is not _A:
		E=A.venv_name
		if E is _A:E=''
		B={_Q:100,_C:D,_E:A.name,_R:E};F=sparta_b86cc7add4(B,C,_D)
		if F[_B]==1:
			A=F[_O]
			if G.is_static_variables:
				H=G.kernel_variables
				if H is not _A:set_workspace_cloudpickle_variables(A,H)
		return{_B:F[_B]}
	return{_B:-1}
def sparta_752fb28461(json_data,user_obj):return{_B:1}