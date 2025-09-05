_A=False
import re,os,json,requests
from datetime import datetime
from packaging.version import parse
from project.models import AppVersioning
from project.logger_config import logger
import pytz
UTC=pytz.utc
proxies_dict={'http':os.environ.get('http_proxy',None),'https':os.environ.get('https_proxy',None)}
def sparta_26b41b508a():0
def sparta_e890945f62():A='name';B='https://api.github.com/repos/SpartaQube/spartaqube-version/tags';C=requests.get(B,proxies=proxies_dict,verify=_A);D=json.loads(C.text);E=max(D,key=lambda t:parse(t[A]));return E[A]
def sparta_3433e3b6c1():A='https://spartaqube-version.pages.dev/latest_version.txt';B=requests.get(A,proxies=proxies_dict,verify=_A,timeout=1);return B.text.split('\n')[0]
def sparta_41d86bcc09():A='https://spartaqube-version.pages.dev/latest_features.json';B=requests.get(A,proxies=proxies_dict,verify=_A,timeout=1);return json.loads(B.text)
def sparta_251b2648da():
	try:A='https://pypi.org/project/spartaqube/';B=requests.get(A,proxies=proxies_dict,verify=_A).text;C=re.search('<h1 class="package-header__name">(.*?)</h1>',B,re.DOTALL);D=C.group(1);E=D.strip().split('spartaqube ')[1];return E
	except:pass
def sparta_ac6c5f1fe5():
	B=os.path.dirname(__file__);C=os.path.dirname(B);D=os.path.dirname(C);E=os.path.dirname(D)
	try:
		with open(os.path.join(E,'app_version.json'),'r')as F:G=json.load(F);A=G['version']
	except:A='0.1.1'
	return A
def sparta_ca595f17e9():
	I='res'
	try:
		C=sparta_ac6c5f1fe5();A=sparta_3433e3b6c1();D=AppVersioning.objects.all();E=datetime.now().astimezone(UTC)
		if D.count()==0:AppVersioning.objects.create(last_available_version_pip=A,last_check_date=E)
		else:B=D[0];B.last_available_version_pip=A;B.last_check_date=E;B.save()
		F=not C==A;G=[]
		if F:J=sparta_41d86bcc09();G=J['features']
		return{'current_version':C,'latest_version':A,'latest_features_list':G,'b_update':F,'humanDate':'A moment ago',I:1}
	except Exception as H:logger.debug('Exception versioning update');logger.debug(H);return{I:-1,'errorMsg':str(H)}