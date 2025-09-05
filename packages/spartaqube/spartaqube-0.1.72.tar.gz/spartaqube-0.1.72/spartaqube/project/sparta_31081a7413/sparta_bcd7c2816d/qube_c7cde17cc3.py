_D='Monitoring task cancelled.'
_C='stderr'
_B='res'
_A=True
import os,json,asyncio,subprocess,platform
from pathlib import Path
from channels.generic.websocket import AsyncWebsocketConsumer
from spartaqube_app.path_mapper_obf import sparta_fc868586da
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import sparta_a253265c85
from project.logger_config import logger
class HotReloadLivePreviewWS(AsyncWebsocketConsumer):
	async def connect(A):logger.debug('Connect Now');A.isSocketKilled=False;A.monitor_task=None;A.user=A.scope['user'];await A.accept()
	async def disconnect(A,close_code=None):
		logger.debug('Disconnect');A.isSocketKilled=_A
		try:await A.close()
		except:pass
		if A.monitor_task and not A.monitor_task.done():
			A.monitor_task.cancel()
			try:await A.monitor_task
			except asyncio.CancelledError:logger.debug(_D)
	def build_dist(D):
		J='main.js';I='frontend';H='Darwin';G='x86_64';B=platform.system();C=platform.machine();K=sparta_fc868586da()['project/core/developer'];L=os.path.join(K,'esbuild')
		if B=='Linux'and C in[G]:A='esbuild-linux-x64'
		elif B==H and C in[G]:A='esbuild-darwin-x64'
		elif B==H and C in['arm64']:A='esbuild-darwin-arm64'
		elif B in['Windows']and C in['AMD64']:A='esbuild-windows-x64.exe'
		else:raise RuntimeError(f"Unsupported platform: {B} {C}")
		A=os.path.join(L,A);M=os.path.join(D.project_path,I,J);N=os.path.join(D.project_path,I,'dist',J)
		try:E=subprocess.run([A,M,'--bundle','--minify',f"--outfile={N}"],check=_A,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=_A,encoding='utf-8');logger.debug('Build successful:');logger.debug(E.stdout);return{_B:1,'stdout':E.stdout}
		except Exception as F:logger.debug('Error occurred:');logger.debug(F);O=str(F);return{_B:-1,_C:O}
	async def monitor_folder(C,path_to_watch,excluded_subfolders):
		A=dict()
		while not C.isSocketKilled:
			try:
				D=False;H=[]
				for(E,Q,L)in os.walk(path_to_watch):
					M=sparta_a253265c85(E)
					if any(M.startswith(A)for A in excluded_subfolders):continue
					for F in L:
						if F.split('.')[-1]=='pyc':continue
						B=os.path.join(E,F);H.append(B);I=os.stat(B).st_mtime
						if B not in A or A[B]!=I:A[B]=I;D=_A;logger.debug(f"Changes hot reload1 due to {F} where root {E}")
				N=list(A.keys())
				for G in N:
					if G not in H:del A[G];D=_A;logger.debug(f"Changes hot reload2 due to {G}")
				if D:
					J=C.build_dist()
					if J[_B]==1:K={_B:1,'triggerChanges':1}
					else:K={_B:-1,_C:J[_C]}
					O=json.dumps(K);await C.send(text_data=O)
				await asyncio.sleep(.5)
			except asyncio.CancelledError:logger.debug(_D);break
			except Exception as P:logger.debug(f"Error monitoring folder: {P}");break
	async def receive(A,text_data):
		D=text_data
		if len(D)>0:
			E=json.loads(D);B=sparta_a253265c85(E['projectPath']);A.project_path=B;C=[os.path.join(B,'backend/logs'),os.path.join(B,'frontend/dist')];C=[sparta_a253265c85(A)for A in C]
			if A.monitor_task and not A.monitor_task.done():
				A.monitor_task.cancel()
				try:await A.monitor_task
				except asyncio.CancelledError:logger.debug('Previous monitoring task cancelled.')
			A.monitor_task=asyncio.create_task(A.monitor_folder(B,C))