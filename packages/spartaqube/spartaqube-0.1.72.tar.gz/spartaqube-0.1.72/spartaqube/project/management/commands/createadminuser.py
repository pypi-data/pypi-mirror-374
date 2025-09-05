import uuid,hashlib
from datetime import datetime
from django.conf import settings as conf_settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from project.models import UserProfile
class Command(BaseCommand):
	help='Create an admin user'
	def handle(J,*K,**L):
		G='utf-8';C=conf_settings.ADMIN_DEFAULT_USER;F=conf_settings.ADMIN_DEFAULT_EMAIL;H=conf_settings.ADMIN_DEFAULT_PWD
		if not User.objects.filter(username=C).exists():A=User.objects.create_user(username=C,email=F,password=H,is_superuser=True)
		else:A=User.objects.filter(username=C).all()[0]
		if not UserProfile.objects.filter(user=A).exists():B=UserProfile(user=A);D=str(A.id)+'_'+str(A.email);D=D.encode(G);E=hashlib.md5(D).hexdigest()+str(datetime.now());E=E.encode(G);I=str(uuid.uuid4());B.user_profile_id=hashlib.sha256(E).hexdigest();B.email=F;B.api_key=str(uuid.uuid4());B.registration_token=I;B.save()