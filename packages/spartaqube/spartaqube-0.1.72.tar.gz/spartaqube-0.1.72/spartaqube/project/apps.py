import os,sys
from django.apps import AppConfig
class ProjectConfig(AppConfig):
	default_auto_field='django.db.models.BigAutoField';name='project'
	def ready(B):
		from django.conf import settings as A
		if not hasattr(A,'GLOBAL_KERNEL_MANAGER'):A.GLOBAL_KERNEL_MANAGER={}