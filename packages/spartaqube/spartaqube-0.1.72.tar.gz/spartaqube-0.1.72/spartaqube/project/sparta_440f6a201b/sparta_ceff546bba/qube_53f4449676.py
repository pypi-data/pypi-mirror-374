_A='windows'
import os,platform,getpass
def sparta_19f1944ceb():
	try:A=str(os.environ.get('IS_REMOTE_SPARTAQUBE_CONTAINER','False'))=='True'
	except:A=False
	return A
def sparta_69df759d09():
	A=platform.system()
	if A=='Windows':return _A
	elif A=='Linux':return'linux'
	elif A=='Darwin':return'mac'
	else:return
def sparta_a4e746f060():
	if sparta_19f1944ceb():return'/spartaqube'
	A=sparta_69df759d09()
	if A==_A:B=f"C:\\Users\\{getpass.getuser()}\\SpartaQube"
	elif A=='linux':B=os.path.expanduser('~/SpartaQube')
	elif A=='mac':B=os.path.expanduser('~/Library/Application Support\\SpartaQube')
	return B