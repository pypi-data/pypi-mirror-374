import uuid,hashlib,time
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from project.models import UserProfile
class Command(BaseCommand):
	help='Create a public user'
	def handle(I,*J,**K):
		F='utf-8';A='public@spartaqube.com';G='public'
		if not User.objects.filter(email=A).exists():B=User.objects.create_user(A,A,G)
		else:B=User.objects.filter(email=A).all()[0]
		if not UserProfile.objects.filter(user=B).exists():C=UserProfile(user=B);D=str(B.id)+'_'+str(B.email);D=D.encode(F);E=hashlib.md5(D).hexdigest()+str(datetime.now());E=E.encode(F);H=str(uuid.uuid4());C.user_profile_id=hashlib.sha256(E).hexdigest();C.email=A;C.api_key=str(uuid.uuid4());C.registration_token=H;C.save()