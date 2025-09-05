import os
from project.sparta_31081a7413.sparta_7d740fe491.qube_8308a65ca6 import qube_8308a65ca6
from project.sparta_31081a7413.sparta_7d740fe491.qube_9472c028b5 import qube_9472c028b5
from project.logger_config import logger
class db_custom_connection:
	def __init__(A):A.dbCon=None;A.dbIdManager='';A.spartAppId=''
	def setSettingsSqlite(B,dbId,dbLocalPath,dbFileNameWithExtension):G='spartApp';E=dbLocalPath;C=dbId;from bqm import settings as F,settingsLocalDesktop as H;B.dbType=0;B.spartAppId=C;A={};A['id']=C;A['ENGINE']='django.db.backends.sqlite3';A['NAME']=str(E)+'/'+str(dbFileNameWithExtension);A['USER']='';A['PASSWORD']='2change';A['HOST']='';A['PORT']='';F.DATABASES[C]=A;H.DATABASES[C]=A;D=qube_9472c028b5();D.setPath(E);D.setDbName(G);B.dbCon=D;B.dbIdManager=G;logger.debug(F.DATABASES)
	def getConnection(A):return A.dbCon
	def setAuthDB(A,authDB):A.dbType=authDB.dbType