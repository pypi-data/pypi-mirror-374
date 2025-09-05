import os
from project.sparta_31081a7413.sparta_7d740fe491.qube_9472c028b5 import qube_9472c028b5
from project.sparta_31081a7413.sparta_7d740fe491.qube_8308a65ca6 import qube_8308a65ca6
from project.sparta_31081a7413.sparta_7d740fe491.qube_2cddb6e3a2 import qube_2cddb6e3a2
from project.sparta_31081a7413.sparta_7d740fe491.qube_f230496dc7 import qube_f230496dc7
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_9472c028b5()
		elif A.dbType==1:A.dbCon=qube_8308a65ca6()
		elif A.dbType==2:A.dbCon=qube_2cddb6e3a2()
		elif A.dbType==4:A.dbCon=qube_f230496dc7()
		return A.dbCon