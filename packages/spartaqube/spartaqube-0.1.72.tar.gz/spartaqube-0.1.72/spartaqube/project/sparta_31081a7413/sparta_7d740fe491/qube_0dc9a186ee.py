_S='Request could not be executed with error 2 '
_R='strReq => '
_Q=" WHERE Idx ='"
_P='DELETE FROM '
_O='SELECT count(*) FROM `'
_N="'             AND NOT EXISTS (SELECT 1 FROM information_schema.columns c WHERE c.table_name = t.table_name)"
_M="SELECT TABLE_NAME, TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES as t WHERE TABLE_SCHEMA = '"
_L="' ORDER BY table_name,ordinal_position"
_K="SELECT * FROM information_schema.columns WHERE table_schema = '"
_J='This table does not exist...'
_I='SELECT * FROM '
_H=") VALUES ('"
_G=' (Idx,'
_F='INSERT INTO '
_E='sql'
_D='`'
_C=None
_B="''"
_A="'"
import pandas as pd,pymysql,pymysql.cursors,pandas as pd,json
from sqlalchemy import create_engine
from project.logger_config import logger
class db_connection_sql:
	def __init__(A):
		D='NAME';A.hostname='localhost';A.user='root';A.schemaName=_C;A.db='qbm';A.port=3306;A.path=_C;A.password='';A.connection=-1;A.bPrint=False
		try:
			from django.conf import settings as C
			if C.PLATFORM in C.USE_DEFAULT_DB_SETTINGS:B=C.DATABASES['default'];A.hostname=B['HOST'];A.user=B['USER'];A.schemaName=B[D];A.db=B[D];A.password=B['PASSWORD'];A.port=int(B['PORT'])
		except:pass
	def getDBType(A):return 1
	def setConnection(A,hostname,username,name,password='',port=3306,schemaName=_C):
		C=schemaName;B=username;A.hostname=hostname;A.user=B;A.db=name;A.password=password
		if C is _C:A.schemaName=B
		else:A.schemaName=C
		if len(str(port))>0:A.port=int(port)
	def create_connection(A):
		if A.bPrint:logger.debug('create_connection');logger.debug('self.hostname => '+str(A.hostname));logger.debug('self.user => '+str(A.user));logger.debug('self.password => '+str(A.password));logger.debug('self.port => '+str(A.port))
		if A.schemaName is _C:A.schemaName=A.user
		if len(str(A.port))>0:A.connection=pymysql.connect(host=A.hostname,user=A.user,password=A.password,db=A.db,port=A.port)
		else:A.connection=pymysql.connect(host=A.hostname,user=A.user,password=A.password,db=A.db)
	def close_connection(A):A.close_connection()
	def pd2DB(A,tableName,thisDf):A.pd2Mysql(tableName,thisDf)
	def pd2Mysql(A,tableName,thisDf):B=create_engine('mysql://'+str(A.user)+':'+str(A.password)+'@'+str(A.hostname)+':'+str(A.port)+'/'+str(A.db));thisDf.to_sql(name=tableName,con=B,if_exists='append')
	def createBlobTable(A,tableName):B='CREATE TABLE `'+str(tableName)+'` (Id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, File LONGBLOB)';A.executeSqlRequest(B)
	def insertBLOB(A,sqlInsert,data_tuple):
		B=sqlInsert;B=B+' VALUES (%s, %s)';A.create_connection();C=A.connection.cursor();C.execute(B,data_tuple)
		try:A.connection.commit();C.close();A.close_connection()
		except Exception as D:
			if A.bPrint:logger.debug('Request could not be executed with error '+str(D))
	def getBLOB(A,tableName,dispoDate=_C):
		F='SELECT File FROM `';D=dispoDate;C=tableName
		if D is _C:E=F+C+'` ORDER BY Dispo DESC LIMIT 1'
		else:E=F+C+"` WHERE Dispo='"+str(D)+"' ORDER BY Id DESC LIMIT 1"
		A.create_connection();B=A.connection.cursor();B.execute(E);G=B.fetchone()[0];B.close();A.close_connection();return G
	def getAllDispoBLOB(A,tableName):C='SELECT * FROM `'+tableName+_D;A.create_connection();B=A.connection.cursor();B.execute(C);D=B.fetchall();B.close();A.close_connection();return D
	def set_connection_from_dbAuth(A,dbAuthObj):
		B=dbAuthObj;A.hostname=B.hostname;A.user=B.username;A.db=B.name;A.password=B.password;A.schemaName=B.schema
		if len(str(B.port))>0:A.port=int(B.port)
		else:A.port=''
	def printOutput(A,bPrint):A.bPrint=bPrint
	def close_connection(A):
		try:A.connection.close()
		except:pass
	def getAllSChemas(A):B="SELECT schema_name FROM information_schema.SCHEMATA WHERE schema_name IN ('"+A.db+"')";A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def getThisSchema(A,schemaName):B="SELECT schema_name FROM information_schema.SCHEMATA WHERE schema_name NOT IN ('information_schema', 'mysql') AND schema_name IN ('"+schemaName+"')";A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def getAllTables(A):B="SELECT table_name FROM information_schema.tables WHERE TABLE_SCHEMA IN ('"+A.schemaName+"')";A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def getAllTablesAndColumns(A):B=A.schemaName;C=_K+str(B)+_L;A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
	def getAllTablesAndColumnsRenamed(B):A=B.getAllTablesAndColumns();A=A[['TABLE_NAME','COLUMN_NAME','DATA_TYPE','COLUMN_KEY','EXTRA']];return A
	def getColumnsOfTable(A,tableName):B=A.schemaName;C=_K+str(B)+"' AND TABLE_NAME = '"+str(tableName)+_L;A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
	def getAllTablesNbRecords(A):B=A.schemaName;C=_M+str(B)+_N;A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
	def getAllTablesNbRecords(A):B=A.schemaName;C=_M+str(B)+_N;A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
	def getAllTablesNbRecords2(A,tableNameArr,websocket):
		I='table';H='recordsNb';G='res';F=websocket;A.create_connection()
		for B in tableNameArr:
			try:C=A.connection.cursor();J=_O+B.replace(_A,_B)+_D;C.execute(J);K=C.fetchone()[0];D={G:1,H:K,I:B};E=json.dumps(D);F.send(text_data=E)
			except Exception as L:D={G:-1,H:0,I:B};E=json.dumps(D);F.send(text_data=E)
		C.close();A.close_connection()
	def insertOrReplaceData(B,tableName,pandasDataframe):
		A=tableName;A=A.lower();C=pandasDataframe.copy()
		if B.checkTableExists(A):B.insertDataFuncDeleteExisting(A,C)
		else:B.createTable(A,C.columns,C.index.name);B.insertDataFuncDeleteExisting(A,C)
	def insertOrReplaceTickerDateData(B,tableName,pandasDataframe):
		A=tableName;A=A.lower();C=pandasDataframe.copy()
		if B.checkTableExists(A):B.insertDataFuncDeleteTickerDate(A,C)
		else:B.createTable(A,C.columns,C.index.name);B.insertDataFuncDeleteTickerDate(A,C)
	def insertData(B,tableName,pandasDataframe):
		A=tableName;A=A.lower();C=pandasDataframe.copy()
		if B.checkTableExists(A):B.insertDataFunc(A,C)
		else:B.createTable(A,C.columns,C.index.name);B.insertDataFunc(A,C)
	def insertDataFunc(A,tableName,pandasDataframe):
		B=pandasDataframe;B[_E]=B.apply(A.prepareData2insert,axis=1);C='';D=B.columns;D=D[:-1]
		for(H,E)in enumerate(D):
			if H==0:C=_D+E.replace(_A,_B)+_D
			else:C=C+',`'+E.replace(_A,_B)+_D
		I=B.index.tolist();A.create_connection();F=A.connection.cursor()
		for(J,K)in enumerate(B[_E]):
			L=str(I[J]).replace(_A,_B);G=_F+tableName.replace(_A,_B)+_G+C+_H+L+"',"+K+')';F.execute(G)
			if A.bPrint:logger.debug(G)
		A.connection.commit();F.close();A.close_connection()
	def insertDataFuncDeleteTickerDate(A,tableName,pandasDataframe):
		F=tableName;B=pandasDataframe;B[_E]=B.apply(A.prepareData2insert,axis=1);C='';D=B.columns;D=D[:-1]
		for(L,G)in enumerate(D):
			if L==0:C=_D+G.replace(_A,_B)+_D
			else:C=C+',`'+G.replace(_A,_B)+_D
		M=B.index.tolist();A.create_connection();E=A.connection.cursor()
		for(H,N)in enumerate(B[_E]):
			I=str(M[H]).replace(_A,_B);J=_P+F.replace(_A,_B)+_Q+I+"' AND Ticker = '"+B['Ticker'].values[H]+_A;K=_F+F.replace(_A,_B)+_G+C+_H+I+"',"+N+')';E.execute(J);E.execute(K)
			if A.bPrint:logger.debug(J);logger.debug(K)
		A.connection.commit();E.close();A.close_connection()
	def insertDataFuncDeleteExisting(A,tableName,pandasDataframe):
		F=tableName;B=pandasDataframe;B[_E]=B.apply(A.prepareData2insert,axis=1);C='';D=B.columns;D=D[:-1]
		for(K,G)in enumerate(D):
			if K==0:C=_D+G.replace(_A,_B)+_D
			else:C=C+',`'+G.replace(_A,_B)+_D
		L=B.index.tolist();A.create_connection();E=A.connection.cursor()
		for(M,N)in enumerate(B[_E]):
			H=str(L[M]).replace(_A,_B);I=_P+F.replace(_A,_B)+_Q+H+_A;J=_F+F.replace(_A,_B)+_G+C+_H+H+"',"+N+')'
			if A.bPrint:logger.debug(I);logger.debug(J)
			E.execute(I);E.execute(J)
		A.connection.commit();E.close();A.close_connection()
	def prepareData2insert(D,row):
		A=''
		for(C,B)in enumerate(row.tolist()):
			if C==0:A=_A+str(B).replace(_A,_B)+_A
			else:A=A+",'"+str(B).replace(_A,_B)+_A
		return A
	def createTable(D,tableName,columnName,idx):
		J=' varchar(64)';I=' datetime';G='Dispo';F='Date';C=tableName;C=C.replace(_A,_B);C=C.lower();A=''
		for(K,B)in enumerate(columnName):
			if K==0:
				if B==F or B==G:A=B.replace(_A,_B)+I
				else:A=B.replace(_A,_B)+J
			elif B==F or B==G:A=A+','+B.replace(_A,_B)+I
			else:A=A+','+B.replace(_A,_B)+J
		E=''
		if idx==F or idx==G:E='Idx datetime,'
		else:E='Idx varchar(64),'
		A='CREATE TABLE '+C+' (Id INT NOT NULL AUTO_INCREMENT,'+E+A+',PRIMARY KEY (Id))'
		if D.bPrint:logger.debug(A)
		D.create_connection();H=D.connection.cursor();H.execute(A);H.close();D.close_connection()
	def getCountTable(A,tableName):
		A.create_connection();B=A.connection.cursor();C=_O+tableName.replace(_A,_B)+'`;'
		if A.bPrint:logger.debug(C)
		B.execute(C);D=B.fetchone()[0];B.close();A.close_connection();return D
	def checkTableExists(A,tableName):
		A.create_connection();B=A.connection.cursor();C="SHOW TABLES LIKE '"+tableName.replace(_A,_B)+_A
		if A.bPrint:logger.debug(C)
		B.execute(C);D=B.fetchone();B.close();A.close_connection()
		if D:return True
		else:return False
	def executeSqlRequest(A,sqlReq):
		C=sqlReq;D=_C;A.create_connection();B=A.connection.cursor()
		if A.bPrint:logger.debug(C)
		try:B.execute(C);A.connection.commit();D=B.lastrowid;B.close();A.close_connection()
		except Exception as E:
			if A.bPrint:logger.debug('Request could not be executed with error 1 '+str(E))
		return D
	def executeSqlRequestArgs(A,sqlReq,sqlArgs):
		C=sqlReq;D=_C;A.create_connection();B=A.connection.cursor()
		if A.bPrint:logger.debug(C)
		try:B.execute(C,sqlArgs);A.connection.commit();D=B.lastrowid;B.close();A.close_connection()
		except Exception as E:
			if A.bPrint:logger.debug('Request could not be executed with error l0 => '+str(E))
		return D
	def getDataFrame(A,tableName):
		B=tableName
		try:
			C=_I+B
			if A.bPrint:logger.debug(_R+str(C))
			A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
		except Exception as E:
			A.close_connection()
			if not A.checkTableExists(B):
				if A.bPrint:logger.debug(_J)
			elif A.bPrint:logger.debug(_S+str(E))
			return
	def getDataFrameLimit(A,tableName,limit=100):
		B=tableName
		try:
			C=_I+B+' LIMIT '+str(limit)
			if A.bPrint:logger.debug(_R+str(C))
			A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
		except Exception as E:
			A.close_connection()
			if not A.checkTableExists(B):
				if A.bPrint:logger.debug(_J)
			elif A.bPrint:logger.debug(_S+str(E))
			return
	def getDataFrameReq(A,strReq):
		try:A.create_connection();C=pd.read_sql(strReq,con=A.connection);A.close_connection();return C
		except Exception as B:
			logger.debug('Exception sql');logger.debug(B);A.close_connection()
			if A.bPrint:logger.debug('Request could not be executed with error 3 '+str(B))
			raise Exception(str(B))
	def getData(B,tableName,flds=_C,startDate=_C,endDate=_C,orderBy=_C):
		G=orderBy;F=startDate;E=tableName;D=endDate
		try:
			A=_I+E
			if F is not _C:
				A=A+" WHERE Idx >= '"+F+_A
				if D is not _C:A=A+" AND Idx <= '"+D+_A
			elif D is not _C:A=A+" WHERE Idx <= '"+D+_A
			if G is not _C:A=A+' ORDER BY '+G
			if B.bPrint:logger.debug(A)
			B.create_connection();C=pd.read_sql(A,con=B.connection);C.set_index('Idx',inplace=True);C=C.drop(['Id'],axis=1);B.close_connection()
			if flds is not _C:return C[flds]
			else:return C
		except Exception as H:
			B.close_connection()
			if not B.checkTableExists(E):
				if B.bPrint:logger.debug(_J)
			elif B.bPrint:logger.debug('Request could not be executed with error 4 '+str(H))
	def df2Sql(A,tableName,pandasDataframe):A.insertData(tableName,pandasDataframe)
	def df2Sql_noReplace(A,tableName,pandasDataframe):A.insertData(tableName,pandasDataframe)