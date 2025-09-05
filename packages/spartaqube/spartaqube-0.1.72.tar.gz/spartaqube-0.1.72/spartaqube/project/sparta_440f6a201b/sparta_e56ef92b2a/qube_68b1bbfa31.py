from datetime import datetime
import hashlib,os,sys,django
def sparta_cfecdc3157():C='/';B='\\';D=os.path.dirname(os.path.abspath(__file__)).replace(B,C);A=os.path.dirname(D).replace(B,C);A=os.path.dirname(A).replace(B,C);A=os.path.dirname(A).replace(B,C);sys.path.append(A);os.environ.setdefault('DJANGO_SETTINGS_MODULE','spartaqube_app.settings');os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']='true';django.setup()
def sparta_f803c45a23():
	H='utf-8';B='admin';from django.contrib.auth.models import User as F;from project.models import UserProfile as I
	if not F.objects.filter(username=B).exists():G='admin@spartaqube.com';A=F.objects.create_user(B,first_name=B,last_name=B,email=G,password=B);A.is_superuser=True;A.is_staff=True;A.save();C=I(user=A);D=str(A.id)+'_'+str(A.email);D=D.encode(H);E=hashlib.md5(D).hexdigest()+str(datetime.now());E=E.encode(H);C.userId=hashlib.sha256(E).hexdigest();C.email=G;C.save()
if __name__=='__main__':sparta_cfecdc3157();sparta_f803c45a23()