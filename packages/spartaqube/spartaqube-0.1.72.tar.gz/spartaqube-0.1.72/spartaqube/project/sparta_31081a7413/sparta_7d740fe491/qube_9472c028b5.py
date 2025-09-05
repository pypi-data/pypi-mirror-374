_F='Request could not be executed with error l1 => '
_E='Request could not be executed with error l0 => '
_D='This table does not exist...'
_C='SELECT * FROM '
_B=True
_A=None
import pandas as pd,sqlite3,os
from project.logger_config import logger
class db_connection_sqlite:
	def __init__(A,hostname='',schemaName=_A,user='',db='db',password='',port='',path=''):
		A.hostname=hostname;A.schemaName=schemaName;A.user=user;A.db=db;A.password=password;A.port=port;A.bPrint=False;A.path=path
		if os.environ['DJANGO_SETTINGS_MODULE']=='spartaqube.project.settings':A.db='db'
		A.create_connection()
	def getDBType(A):return 0
	def setBPrint(A,bPrint):A.bPrint=bPrint
	def setPath(A,thisPath):A.path=thisPath
	def setDbName(A,db_):A.db=db_
	def setConnection(A,hostname='',username='',name=''):A.hostname=hostname;A.user=username;A.db=name
	def create_connection(A):A.connection=sqlite3.connect(A.path+'/'+str(A.db)+'.sqlite3')
	def printOutput(A,bPrint):A.bPrint=bPrint
	def close_connection(A):A.connection.close()
	def pd2DB(A,tableName,thisDf):A.df2Sql(tableName,thisDf)
	def getAllSChemas(A):B="SELECT name FROM sqlite_master WHERE type='table'";A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def df2Sql(A,tableName,pandasDataframe):A.create_connection();B=pandasDataframe.copy();B.to_sql(name=tableName,con=A.connection,if_exists='replace',index=_B);A.close_connection()
	def df2Sql_noReplace(A,tableName,pandasDataframe):A.create_connection();B=pandasDataframe.copy();B.to_sql(name=tableName,con=A.connection,if_exists='append',index=_B);A.close_connection()
	def getCountTable(A,tableName):
		A.create_connection();B=A.connection.cursor();C="SELECT count(*) FROM '"+tableName.replace("'","''")+"';"
		if A.bPrint:logger.debug(C)
		B.execute(C);D=B.fetchone()[0];B.close();A.close_connection();return D
	def checkTableExists(A,tableName):
		A.create_connection();B=A.connection.cursor();C="SELECT count(*) FROM sqlite_master WHERE type='table' AND name='"+tableName.replace("'","''")+"';"
		if A.bPrint:logger.debug(C)
		B.execute(C);D=B.fetchone()[0];B.close();A.close_connection()
		if D>0:return _B
		else:return False
	def createBlobTable(A,tableName):B='CREATE TABLE `'+str(tableName)+'` (Id INT(11) PRIMARY KEY, File LONGBLOB)';A.executeSqlRequest(B)
	def insertBLOB(A,sqlInsert,data_tuple):
		B=sqlInsert;B=B+' VALUES (?, ?)';A.create_connection();C=A.connection.cursor();C.execute(B,data_tuple)
		try:A.connection.commit();C.close();A.close_connection()
		except Exception as D:
			if A.bPrint:logger.debug('Request could not be executed with error l10 '+str(D))
	def getBLOB(B,tableName,dispoDate=_A):
		G='SELECT File FROM `';E=dispoDate;D=tableName
		if E is _A:F=G+D+'` ORDER BY Dispo DESC LIMIT 1'
		else:F=G+D+"` WHERE Dispo='"+str(E)+"' ORDER BY Id DESC LIMIT 1"
		B.create_connection();C=B.connection.cursor();C.execute(F);A=C.fetchone()
		if A is not _A:
			if len(A)==1:A=A[0]
		C.close();B.close_connection();return A
	def get_blob(A,tableName):C='SELECT * FROM `'+tableName+'`';A.create_connection();B=A.connection.cursor();B.execute(C);D=B.fetchall();B.close();A.close_connection();return D
	def executeSqlRequest(A,sqlReq):
		C=sqlReq;D=_A;A.create_connection();B=A.connection.cursor()
		if A.bPrint:logger.debug(C)
		try:B.execute(C);A.connection.commit();D=B.lastrowid;B.close();A.close_connection()
		except Exception as E:
			if A.bPrint:logger.debug(_E+str(E))
		return D
	def executeSqlRequestArgs(A,sqlReq,sqlArgs):
		C=sqlReq;D=_A;A.create_connection();B=A.connection.cursor()
		if A.bPrint:logger.debug(C)
		try:B.execute(C,sqlArgs);A.connection.commit();D=B.lastrowid;B.close();A.close_connection()
		except Exception as E:
			A.bPrint=_B
			if A.bPrint:logger.debug(_E+str(E))
		return D
	def getDataFrame(A,tableName):
		B=tableName
		try:C=_C+B;A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
		except Exception as E:
			A.close_connection()
			if not A.checkTableExists(B):
				if A.bPrint:logger.debug(_D)
			elif A.bPrint:logger.debug(_F+str(E))
			return
	def getDataFrameLimit(A,tableName,limit=100):
		B=tableName
		try:C=_C+B+' LIMIT '+str(limit);A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
		except Exception as E:
			A.close_connection()
			if not A.checkTableExists(B):
				if A.bPrint:logger.debug(_D)
			elif A.bPrint:logger.debug(_F+str(E))
			return
	def getDataFrameReq(A,strReq):
		try:A.create_connection();B=pd.read_sql(strReq,con=A.connection);A.close_connection();return B
		except Exception as C:
			A.close_connection()
			if A.bPrint:logger.debug('Request could not be executed with error l2 => '+str(C))
			return
	def getData(B,tableName,flds=_A,startDate=_A,endDate=_A,orderBy=_A):
		G=orderBy;F=startDate;E=tableName;D=endDate
		try:
			A=_C+E
			if F is not _A:
				A=A+" WHERE Idx >= '"+F+"'"
				if D is not _A:A=A+" AND Idx <= '"+D+"'"
			elif D is not _A:A=A+" WHERE Idx <= '"+D+"'"
			if G is not _A:A=A+' ORDER BY '+G
			if B.bPrint:logger.debug(A)
			B.create_connection();C=pd.read_sql(A,con=B.connection);C.set_index('Idx',inplace=_B);C=C.drop(['Id'],axis=1);B.close_connection()
			if flds is not _A:return C[flds]
			else:return C
		except Exception as H:
			B.close_connection()
			if not B.checkTableExists(E):
				if B.bPrint:logger.debug(_D)
			elif B.bPrint:logger.debug('Request could not be executed with error l3 => '+str(H))