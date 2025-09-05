import re,os,json,stat,importlib,io,sys,subprocess,platform,base64,traceback,uuid,shutil
from pathlib import Path
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from spartaqube_app.path_mapper_obf import sparta_fc868586da
from project.models import ShareRights
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
from project.sparta_440f6a201b.sparta_aea4c35167 import qube_2fc75b9545 as qube_2fc75b9545
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_1b9826e2d7 import Connector as Connector
from project.sparta_440f6a201b.sparta_89c6bd5348 import qube_5a0182b6f5 as qube_5a0182b6f5
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import sparta_a253265c85
from project.sparta_440f6a201b.sparta_817694737b import qube_62229504ef as qube_62229504ef
from project.sparta_440f6a201b.sparta_817694737b import qube_ec67714d19 as qube_ec67714d19
from project.sparta_440f6a201b.sparta_8ade4c4917.qube_b559aa4222 import sparta_ac6c5f1fe5
from project.sparta_440f6a201b.sparta_ceff546bba.qube_467225df75 import sparta_9f1de43185,sparta_46a11b5877
from project.logger_config import logger
from project.sparta_440f6a201b.sparta_ceff546bba.qube_53f4449676 import sparta_a4e746f060
from project.sparta_440f6a201b.sparta_9218ccb674 import qube_b7db7762fc as qube_b7db7762fc
def sparta_8bc53bda0e(user_obj):
	A=qube_2808664dfd.sparta_0a996f3465(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_028a4f4c45(json_data,user_obj):A=json_data;A['is_plot_db']=True;return qube_b7db7762fc.sparta_bb1d6cee63(A,user_obj)
def sparta_a176dcab01():
	B=sparta_a4e746f060();A=os.path.join(B,'plot_db_developer')
	def C(path):
		A=Path(path)
		if not A.exists():A.mkdir(parents=True)
	C(A);return{'res':1,'path':A}