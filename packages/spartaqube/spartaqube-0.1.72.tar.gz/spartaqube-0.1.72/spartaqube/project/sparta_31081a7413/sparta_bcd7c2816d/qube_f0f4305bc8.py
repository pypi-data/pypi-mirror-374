_C=True
_B=False
_A=None
import os,json,platform,websocket,threading,time,pandas as pd
from pathlib import Path
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from project.logger_config import logger
from project.sparta_31081a7413.sparta_0886d51747 import qube_99dd79197b as qube_99dd79197b
from project.sparta_440f6a201b.sparta_ceff546bba import qube_2940d28c8f as qube_2940d28c8f
from project.sparta_440f6a201b.sparta_aac43fa003.qube_62114c67e6 import sparta_217e4e4594
from project.sparta_440f6a201b.sparta_aac43fa003.qube_1151abe53c import sparta_63ad2e7e4a
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe,convert_dataframe_to_json,sparta_a253265c85
from project.sparta_440f6a201b.sparta_15c403c94e.qube_293080d79c import SenderKernel
from project.sparta_440f6a201b.sparta_bb5bf030e1.qube_203378cc3e import sparta_8b9995568a,sparta_08311cba71,get_api_key_async
class NotebookWS(AsyncWebsocketConsumer):
	channel_session=_C;http_user_and_session=_C
	async def connect(A):logger.debug('Connect Now');await A.accept();A.user=A.scope['user'];A.json_data_dict=dict();A.sender_kernel_obj=_A
	async def disconnect(A,close_code=_A):
		logger.debug('Disconnect')
		if A.sender_kernel_obj is not _A:A.sender_kernel_obj.zmq_close()
		try:await A.close()
		except:pass
	async def notebook_permission_code_exec(A,json_data):from project.sparta_440f6a201b.sparta_0972eac5cf import qube_57c026f3db as B;return await coreNotebook.notebook_permission_code_exec(json_data)
	async def prepare_sender_kernel(A,kernel_manager_uuid):
		from project.models import KernelProcess as C;B=await sync_to_async(lambda:list(C.objects.filter(kernel_manager_uuid=kernel_manager_uuid)),thread_sensitive=_B)()
		if len(B)>0:
			D=B[0];E=D.port
			if A.sender_kernel_obj is _A:A.sender_kernel_obj=SenderKernel(A,E)
			A.sender_kernel_obj.zmq_connect()
	async def get_kernel_type(D,kernel_manager_uuid):
		from project.models import KernelProcess as B;A=await sync_to_async(lambda:list(B.objects.filter(kernel_manager_uuid=kernel_manager_uuid)),thread_sensitive=_B)()
		if len(A)>0:C=A[0];return C.type
		return 1
	async def receive(B,text_data):
		AQ='kernel_variable_arr';AP='workspace_variables_to_update';AO='repr_data';AN='raw_data';AM='cellTitleVarName';AL='execCodeTitle';AK='cellId';AJ='cell_id';AI='execute';AH='execute_shell';AG='activate_venv';AF='venv_name';AE='import json\n';y=text_data;x='updated_variables';w='output';v='cellCode';u='=';t='defaultDashboardVars';m='assignGuiComponentVariable';l='variable';k='get_workspace_variable';j='value';d='get_kernel_variable_repr';c='code';W='errorMsg';V='json_data';T='dashboardVenv';Q='\n';P='';O='execute_code';N='kernel_variable';K='cmd';F='res';C='service'
		if len(y)>0:
			A=json.loads(y);E=A[C];z=A['kernelManagerUUID'];await B.prepare_sender_kernel(z);AR=await B.get_kernel_type(z)
			def Z(code_to_exec,json_data):
				D=json_data;B=code_to_exec;A=AE
				if t in D:
					E=D[t]
					for(C,F)in E.items():
						if len(C)>0:G=F['outputDefaultValue'];A+=f'if "{C}" in globals():\n    pass\nelse:\n    {C} = {repr(G)}\n'
				H=json.dumps({j:_A,'col':-1,'row':-1});A+=f"if \"last_action_state\" in globals():\n    pass\nelse:\n    last_action_state = json.loads('{H}')\n"
				if len(A)>0:B=f"{A}\n{B}"
				return B
			async def R(json_data):
				E='projectSysPath';D=json_data
				if E in D:
					if len(D[E])>0:A=sparta_a253265c85(D[E]);A=Path(A).resolve();F=f'import sys, os\nsys.path.insert(0, r"{str(A)}")\nos.chdir(r"{str(A)}")\n';await B.sender_kernel_obj.send_zmq_request({C:O,K:F})
			async def e(json_data):
				A=json_data
				if T in A:
					if A[T]is not _A:
						if len(A[T])>0:D=A[T];await B.sender_kernel_obj.send_zmq_request({C:AG,AF:D})
			if E=='init-socket'or E=='reconnect-kernel'or E=='reconnect-kernel-run-all':
				G={F:1,C:E}
				if t in A:I=Z(P,A);await B.sender_kernel_obj.send_zmq_request({C:O,K:I})
				await R(A);await e(A);D=json.dumps(G);await B.send(text_data=D);return
			elif E=='disconnect':B.disconnect()
			elif E=='exec':
				await R(A);A0=time.time();logger.debug(u*50);J=A[v];I=J
				if AR==5:logger.debug('Execute for the notebook Execution Exec case');logger.debug(A);I=await B.notebook_permission_code_exec(A)
				I=Z(I,A);a=_B;print('BEFORE CRASH input_cmd');print(J);print(type(J))
				if J is not _A:
					if len(J)>0:
						if J[0]=='!':a=_C
				if a:await B.sender_kernel_obj.send_zmq_request({C:AH,K:I,V:json.dumps(A)})
				else:await B.sender_kernel_obj.send_zmq_request({C:AI,K:I,V:json.dumps(A)})
				try:A1=sparta_217e4e4594(A[v])
				except:A1=[]
				logger.debug(u*50);AS=time.time()-A0;D=json.dumps({F:2,C:E,'elapsed_time':round(AS,2),AJ:A[AK],'updated_plot_variables':A1,'input':json.dumps(A)});await B.send(text_data=D)
			elif E=='exec-llm':
				await R(A);A0=time.time();logger.debug(u*50);J=A[v];I=J;a=_B
				if J is not _A:
					print('Before crash input_cmd 1');print(J);print(type(J));print('json_data DEBUG');print(A);print(A.keys())
					if len(J)>0:
						if J[0]=='!':a=_C
				if a:await B.sender_kernel_obj.send_zmq_request({C:AH,K:I,V:json.dumps(A)})
				else:await B.sender_kernel_obj.send_zmq_request({C:AI,K:I,V:json.dumps(A)})
			elif E=='trigger-code-gui-component-input':
				R(A)
				try:
					try:n=json.loads(A[AL]);L=Q.join([A[c]for A in n])
					except:L=P
					AT=json.loads(A['execCodeInput']);A2=Q.join([A[c]for A in AT]);X=Z(A2,A);X+=Q+L;await B.sender_kernel_obj.send_zmq_request(sender_dict={C:O,K:X},b_send_websocket_msg=_B);Y=sparta_217e4e4594(A2);A3=A['guiInputVarName'];AU=A['guiOutputVarName'];AV=A[AM];o=[A3,AU,AV];b=[]
					for U in o:
						try:S=await B.sender_kernel_obj.send_zmq_request({C:d,N:U})
						except:S=json.dumps({F:1,w:P})
						p=convert_dataframe_to_json(convert_to_dataframe(await B.sender_kernel_obj.send_zmq_request({C:k,N:U}),A3));b.append({l:U,AN:p,AO:S})
				except Exception as H:D=json.dumps({F:-1,C:E,W:str(H)});logger.debug('Error',D);await B.send(text_data=D);return
				D=json.dumps({F:1,C:E,x:Y,AP:b});await B.send(text_data=D)
			elif E=='trigger-code-gui-component-output':
				R(A)
				try:
					A4=P;f=P
					if m in A:g=A[m];A5=sparta_63ad2e7e4a(g);A4=A5['assign_state_variable'];f=A5['assign_code']
					AW=json.loads(A['execCodeOutput']);A6=Q.join([A[c]for A in AW]);X=f+Q;X+=A4+Q;X+=A6;await B.sender_kernel_obj.send_zmq_request(sender_dict={C:O,K:X},b_send_websocket_msg=_B);Y=sparta_217e4e4594(A6)
					try:Y.append(A[m][l])
					except Exception as H:pass
				except Exception as H:D=json.dumps({F:-1,C:E,W:str(H)});await B.send(text_data=D);return
				D=json.dumps({F:1,C:E,x:Y});logger.debug(f"return final here {D}");await B.send(text_data=D)
			elif E=='assign-kernel-variable-from-gui':
				try:g=A[m];AX=g[j];f=f"{g[l]} = {AX}";await B.sender_kernel_obj.send_zmq_request({C:O,K:f})
				except Exception as H:D=json.dumps({F:-1,C:E,W:str(H)});await B.send(text_data=D);return
				D=json.dumps({F:1,C:E});await B.send(text_data=D)
			elif E=='exec-main-dashboard-notebook-init':
				await R(A);await e(A);I=A['dashboardFullCode'];I=Z(I,A)
				try:await B.sender_kernel_obj.send_zmq_request({C:O,K:I},b_send_websocket_msg=_B)
				except Exception as H:D=json.dumps({F:-1,C:E,W:str(H)});await B.send(text_data=D);return
				A7=A['plotDBRawVariablesList'];AY=A7;A8=[];A9=[]
				for q in A7:
					try:A8.append(convert_dataframe_to_json(convert_to_dataframe(await B.sender_kernel_obj.send_zmq_request({C:k,N:q}),q)));A9.append(await B.sender_kernel_obj.send_zmq_request({C:d,N:q}))
					except Exception as H:logger.debug('Except get var');logger.debug(H)
				D=json.dumps({F:1,C:E,'variables_names':AY,'variables_raw':A8,'variables_repr':A9});await B.send(text_data=D)
			elif E=='trigger-action-plot-db':
				logger.debug('TRIGGER CODE ACTION PLOTDB');logger.debug(A)
				try:
					h=AE;h+=f"last_action_state = json.loads('{A['actionDict']}')\n"
					try:AZ=json.loads(A['triggerCode']);r=Q.join([A[c]for A in AZ])
					except:r=P
					h+=Q+r;logger.debug('cmd to execute');logger.debug('cmd_to_exec');logger.debug(h);await B.sender_kernel_obj.send_zmq_request({C:O,K:h});Y=sparta_217e4e4594(r)
				except Exception as H:D=json.dumps({F:-1,C:E,W:str(H)});await B.send(text_data=D);return
				D=json.dumps({F:1,C:E,x:Y});await B.send(text_data=D)
			elif E=='dynamic-title':
				try:n=json.loads(A[AL]);L=Q.join([A[c]for A in n])
				except:L=P
				if len(L)>0:
					L=Z(L,A);await R(A);await e(A)
					try:
						await B.sender_kernel_obj.send_zmq_request({C:O,K:L});AA=A[AM];o=[AA];b=[]
						for U in o:
							try:S=await B.sender_kernel_obj.send_zmq_request({C:d,N:U})
							except:S=json.dumps({F:1,w:P})
							p=convert_dataframe_to_json(convert_to_dataframe(await B.sender_kernel_obj.send_zmq_request({C:k,N:U}),AA));b.append({l:U,AN:p,AO:S})
						D=json.dumps({F:1,C:E,AP:b});await B.send(text_data=D)
					except Exception as H:D=json.dumps({F:-1,C:E,W:str(H)});logger.debug('Error',D);logger.debug(L);await B.send(text_data=D);return
			elif E=='dashboard-map-dataframe-python':Aa=A['notebookVar'];Ab=A['jsonDataFrame'];L=f"jsonDataFrameDictTmp = json.loads('{Ab}')\n";L+=f"{Aa} = pd.DataFrame(index=jsonDataFrameDictTmp['index'], columns=jsonDataFrameDictTmp['columns'], data=jsonDataFrameDictTmp['data'])";await B.sender_kernel_obj.send_zmq_request({C:O,K:L});D=json.dumps({F:1,C:E});await B.send(text_data=D)
			elif E=='reset':await B.sender_kernel_obj.send_zmq_request({C:'reset_kernel_workspace'});await e(A);G={F:1,C:E};D=json.dumps(G);await B.send(text_data=D)
			elif E=='workspace-list':Ac=await B.sender_kernel_obj.send_zmq_request({C:'list_workspace_variables'});G={F:1,C:E,'workspace_variables':Ac};G.update(A);D=json.dumps(G);await B.send(text_data=D)
			elif E=='workspace-get-variable-as-df':
				AB=[];AC=[];AD=[]
				for i in A[AQ]:
					Ad=await B.sender_kernel_obj.send_zmq_request({C:k,N:i});Ae=convert_to_dataframe(Ad,variable_name=i)
					try:AB.append(convert_dataframe_to_json(Ae));AC.append(i)
					except:pass
					try:S=await B.sender_kernel_obj.send_zmq_request({C:d,N:i})
					except:S=json.dumps({F:1,w:P})
					AD.append(S)
				G={F:1,C:E,AQ:AC,'workspace_variable_arr':AB,'kernel_variable_repr_arr':AD};D=json.dumps(G);await B.send(text_data=D)
			elif E=='workspace-get-variable'or E=='workspace-get-variable-preview':Af=await B.sender_kernel_obj.send_zmq_request({C:d,N:A[N]});G={F:1,C:E,AJ:A.get(AK,_A),'workspace_variable':Af};D=json.dumps(G);await B.send(text_data=D)
			elif E=='workspace-set-variable-from-datasource':
				if j in list(A.keys()):await B.sender_kernel_obj.send_zmq_request({C:'set_workspace_variable_from_datasource',V:json.dumps(A)});G={F:1,C:E};D=json.dumps(G);await B.send(text_data=D)
			elif E=='workspace-set-variable':
				if j in list(A.keys()):await B.sender_kernel_obj.send_zmq_request({C:'set_workspace_variable',V:json.dumps(A)});G={F:1,C:E};D=json.dumps(G);await B.send(text_data=D)
			elif E=='workspace-set-variable-from-paste-modal':
				M=pd.DataFrame(A['clipboardData']);s=A['delimiters']
				if s is not _A:
					if len(s)>0:Ag=M.columns;M=M[Ag[0]].str.split(s,expand=_C)
				if A['bFirstRowHeader']:M.columns=M.iloc[0];M=M[1:].reset_index(drop=_C)
				if A['bFirstColIndex']:M=M.set_index(M.columns[0])
				Ah={'name':A['name'],'df_json':M.to_json(orient='split')};await B.sender_kernel_obj.send_zmq_request({C:'set_workspace_variable_from_paste_modal',V:json.dumps(Ah)});G={F:1,C:E};D=json.dumps(G);await B.send(text_data=D)
			elif E=='set-sys-path-import':
				if'projectPath'in A:await R(A)
				G={F:1,C:E};D=json.dumps(G);await B.send(text_data=D)
			elif E=='set-kernel-venv':
				if T in A:
					if A[T]is not _A:
						if len(A[T])>0:Ai=A[T];await B.sender_kernel_obj.send_zmq_request({C:AG,AF:Ai})
				G={F:1,C:E};D=json.dumps(G);await B.send(text_data=D)
			elif E=='deactivate-venv':await B.sender_kernel_obj.send_zmq_request({C:'deactivate_venv'});G={F:1,C:E};D=json.dumps(G);await B.send(text_data=D)
			elif E=='get-widget-iframe':
				logger.debug('Deal with iframe here');from IPython.core.display import display,HTML;import warnings as Aj;Aj.filterwarnings('ignore',message='Consider using IPython.display.IFrame instead',category=UserWarning)
				try:Ak=A['widget_id'];Al=await get_api_key_async(B.user);Am=await sync_to_async(lambda:HTML(f'<iframe src="/plot-widget/{Ak}/{Al}" width="100%" height="500" frameborder="0" allow="clipboard-write"></iframe>').data)();G={F:1,C:E,'widget_iframe':Am};D=json.dumps(G);await B.send(text_data=D)
				except Exception as H:G={F:-1,W:str(H)};D=json.dumps(G);await B.send(text_data=D)