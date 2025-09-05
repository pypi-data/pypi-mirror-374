_A=None
import pandas as pd,pymysql,pymysql.cursors,pandas as pd
from sqlalchemy import create_engine
from project.sparta_31081a7413.sparta_7d740fe491.qube_0dc9a186ee import qube_0dc9a186ee
from project.logger_config import logger
class db_connection_mysql(db_connection_sql):
	def __init__(A):
		D='NAME';A.hostname='localhost';A.user='root';A.schemaName=_A;A.db='qbm';A.port=3306;A.path=_A;A.password='';A.connection=-1;A.bPrint=False
		try:
			from django.conf import settings as C
			if C.PLATFORM in C.USE_DEFAULT_DB_SETTINGS:B=C.DATABASES['default'];A.hostname=B['HOST'];A.user=B['USER'];A.schemaName=B[D];A.db=B[D];A.password=B['PASSWORD'];A.port=int(B['PORT'])
		except:pass
	def get_db_type(A):return 1
	def set_connection(A,hostname,username,name,password='',port=3306,schemaName=_A):
		C=schemaName;B=name;A.hostname=hostname;A.user=username;A.db=B;A.password=password
		if C is _A:A.schemaName=B
		elif len(C)>0:A.schemaName=C
		else:A.schemaName=B
		if len(str(port))>0:A.port=int(port)
	def create_connection(A):
		if A.bPrint:logger.debug('create_connection for MYSQL');logger.debug('self.hostname => '+str(A.hostname));logger.debug('self.user => '+str(A.user));logger.debug('self.password => '+str(A.password));logger.debug('self.port => '+str(A.port))
		if A.schemaName is _A:A.schemaName=A.user
		if len(str(A.port))>0:A.connection=pymysql.connect(host=A.hostname,user=A.user,password=A.password,db=A.db,port=A.port)
		else:A.connection=pymysql.connect(host=A.hostname,user=A.user,password=A.password,db=A.db)