_A=True
from distutils.spawn import spawn
import json,platform,subprocess,os
from project.logger_config import logger
IS_WINDOWS=False
if platform.system()=='Windows':IS_WINDOWS=_A
from project.models import UserProfile
from channels.generic.websocket import WebsocketConsumer
class XtermGitWS(WebsocketConsumer):
	channel_session=_A;http_user_and_session=_A
	def connect(A):A.accept();A.user=A.scope['user'];A.json_data_dict=dict()
	def disconnect(A,close_code):
		B=None;A.process=B;A.master,A.slave=B,B
		try:A.close()
		except:pass
	def receive(E,text_data):
		O='git_cmd_err';N='git_cmd_output';M='err';L='output';K='res';H=text_data;logger.debug('RECEIVE GIT XTERMS')
		if len(H)>0:
			C=json.loads(H);D=C['cmd'];logger.debug('json_data');logger.debug(C)
			if not D.startswith('git'):F={K:1,L:'',M:['Invalid git command...','Enter command git --help to get the list of available commands']};G=json.dumps(F);E.send(text_data=G);return
			E.json_data_dict=C;logger.debug('cmd > '+str(D));P=C['projectPath']
			if IS_WINDOWS:I=f'"%ProgramFiles%\\Git\\bin\\bash.exe" -c "{D}"'
			else:I=D
			J=subprocess.Popen(I,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=_A,cwd=P);A=J.stdout.readlines();logger.debug(N);logger.debug(A)
			if len(A)>0:A=[A.decode()for A in A];logger.debug(N);logger.debug(A)
			B=J.stderr.readlines();logger.debug(O);logger.debug(B)
			if len(B)>0:B=[A.decode()for A in B];logger.debug(O);logger.debug(B)
			logger.debug(C);F={K:1,L:A,M:B};G=json.dumps(F);E.send(text_data=G)