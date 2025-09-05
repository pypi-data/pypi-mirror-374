import os,zipfile,pytz
UTC=pytz.utc
from django.conf import settings as conf_settings
def sparta_35544f8a64():
	B='APPDATA'
	if conf_settings.PLATFORMS_NFS:
		A='/var/nfs/notebooks/'
		if not os.path.exists(A):os.makedirs(A)
		return A
	if conf_settings.PLATFORM=='LOCAL_DESKTOP'or conf_settings.IS_LOCAL_PLATFORM:
		if conf_settings.PLATFORM_DEBUG=='DEBUG-CLIENT-2':return os.path.join(os.environ[B],'SpartaQuantNB/CLIENT2')
		return os.path.join(os.environ[B],'SpartaQuantNB')
	if conf_settings.PLATFORM=='LOCAL_CE':return'/app/notebooks/'
def sparta_4ea80e5d70(userId):A=sparta_35544f8a64();B=os.path.join(A,userId);return B
def sparta_de0667fa7f(notebookProjectId,userId):A=sparta_4ea80e5d70(userId);B=os.path.join(A,notebookProjectId);return B
def sparta_af2a57f22b(notebookProjectId,userId):A=sparta_4ea80e5d70(userId);B=os.path.join(A,notebookProjectId);return os.path.exists(B)
def sparta_27deda74d5(notebookProjectId,userId,ipynbFileName):A=sparta_4ea80e5d70(userId);B=os.path.join(A,notebookProjectId);return os.path.isfile(os.path.join(B,ipynbFileName))
def sparta_ec5d39ab0a(notebookProjectId,userId):
	C=userId;B=notebookProjectId;D=sparta_de0667fa7f(B,C);G=sparta_4ea80e5d70(C);A=f"{G}/zipTmp/"
	if not os.path.exists(A):os.makedirs(A)
	H=f"{A}/{B}.zip";E=zipfile.ZipFile(H,'w',zipfile.ZIP_DEFLATED);I=len(D)+1
	for(J,M,K)in os.walk(D):
		for L in K:F=os.path.join(J,L);E.write(F,F[I:])
	return E
def sparta_55d5957d67(notebookProjectId,userId):B=userId;A=notebookProjectId;sparta_ec5d39ab0a(A,B);C=f"{A}.zip";D=sparta_4ea80e5d70(B);E=f"{D}/zipTmp/{A}.zip";F=open(E,'rb');return{'zipName':C,'zipObj':F}