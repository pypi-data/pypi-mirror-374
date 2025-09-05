_J=':memory:'
_I='influxdb_client'
_H='cassandra.auth'
_G='cassandra.cluster'
_F='questdb.ingress'
_E='clickhouse_connect'
_D='aerospike'
_C='couchdb'
_B='cx_Oracle'
_A=None
import os,time,pandas as pd,psycopg2,mysql.connector,pyodbc,duckdb,sqlite3
from pymongo import MongoClient
from sqlalchemy import create_engine,MetaData,Table,select,inspect,text
from multiprocessing import Pool
from project.logger_config import logger
libraries={_B:_B,'redis':'redis',_C:_C,_D:_D,_E:_E,_F:_F,_G:_G,_H:_H,_I:_I}
summary={}
for(lib_name,module)in libraries.items():
	try:__import__(module);summary[lib_name]='Available'
	except ImportError:summary[lib_name]='Not Installed'
class EngineBuilder:
	def __init__(A,host,port,user=_A,password=_A,database=_A,engine_name='postgresql'):C=database;B=password;A.host=host;A.port=port;A.user=user;A.password=B;A.database=C;A.url_engine=f"{engine_name}://{user}:{B}@{host}:{port}/{C}";A.error_msg_test_connection=''
	def get_error_msg_test_connection(A):return A.error_msg_test_connection
	def set_url_engine(A,url_engine):A.url_engine=url_engine
	def set_database(A,database):A.database=database
	def set_file_path(A,file_path):A.file_path=file_path
	def set_keyspace_cassandra(A,keyspace_cassandra):A.keyspace_cassandra=keyspace_cassandra
	def set_redis_db(A,redis_db):A.redis_db=redis_db
	def set_database_path(A,database_path):A.database_path=database_path
	def set_socket_url(A,socket_url):A.socket_url=socket_url
	def set_json_url(A,json_url):A.json_url=json_url
	def set_dynamic_inputs(A,dynamic_inputs):A.dynamic_inputs=dynamic_inputs
	def set_py_code_processing(A,py_code_processing):A.py_code_processing=py_code_processing
	def set_library_arctic(A,database_path,library_arctic):A.database_path=database_path;A.library_arctic=library_arctic
	def build_postgres(A):B=psycopg2.connect(user=A.user,password=A.password,host=A.host,port=A.port,database=A.database);return B
	def build_mysql(A):B=mysql.connector.connect(host=A.host,user=A.user,passwd=A.password,port=A.port,database=A.database);return B
	def build_mariadb(A):logger.debug(A.host);logger.debug(A.user);logger.debug(A.password);logger.debug(A.port);logger.debug(A.database);B=mysql.connector.connect(host=A.host,user=A.user,passwd=A.password,port=A.port,database=A.database);return B
	def build_mssql(B,trusted_connection,driver):
		D=driver;C=trusted_connection
		try:
			A=B.build_mssql_params(C,D)
			if A is not _A:return A
			else:
				try:
					A=B.build_mssql_dsn(C,D)
					if A is not _A:return A
				except:pass
		except:
			A=B.build_mssql_dsn(C,D)
			if A is not _A:return A
	def build_mssql_params(A,trusted_connection,driver):
		C=driver
		try:
			B=f"{A.host}"
			if A.port is not _A:
				if len(A.port)>0:B=f"{A.host},{A.port}"
			if trusted_connection:D=pyodbc.connect(driver=f"{C}",server=B,database=f"{A.database}",trusted_connection='yes')
			else:D=pyodbc.connect(driver=f"{C}",server=B,database=f"{A.database}",uid=f"{A.user}",pwd=f"{A.password}")
			return D
		except Exception as E:A.error_msg_test_connection=str(E)
	def build_mssql_dsn(A,trusted_connection,driver):
		B=driver
		try:
			if trusted_connection:C=pyodbc.connect(f"DRIVER={B};SERVER={A.host},{A.port};DATABASE={A.database};Trusted_Connection=yes")
			else:C=pyodbc.connect(f"DRIVER={B};SERVER={A.host},{A.port};DATABASE={A.database};UID={A.user};PWD={A.password}")
			return C
		except Exception as D:A.error_msg_test_connection=str(D)
	def build_oracle(A,lib_dir=_A,oracle_service_name='orcl'):
		C=lib_dir;import cx_Oracle as B
		if C is not _A:
			try:B.init_oracle_client(lib_dir=C)
			except:pass
		D=B.makedsn(A.host,A.port,service_name=oracle_service_name);E=B.connect(user=A.user,password=A.password,dsn=D,mode=B.SYSDBA);return E
	def build_arctic(B,database_path,library_arctic):
		A=database_path;B.set_library_arctic(A,library_arctic)
		if A is not _A:
			if len(A)>0:logger.debug('database_path > '+str(A));C=adb.Arctic(A);return C
	def build_cassandra(A,keyspace):from cassandra.cluster import Cluster as B;A.set_keyspace_cassandra(keyspace);C=[A.host];D=PlainTextAuthProvider(username=A.user,password=A.password)if A.user and A.password else _A;E=B(contact_points=C,port=A.port,auth_provider=D);return E
	def build_scylladb(A,keyspace):return A.build_cassandra(keyspace)
	def build_clickhouse(A):
		import clickhouse_connect as B
		try:C=B.get_client(host=A.host,port=A.port,user=A.user,password=A.password,database=A.database);return C
		except:pass
	def build_couchdb(A):
		import couchdb as C
		try:D=f"{A.host}:{A.port}";B=C.Server(D);B.resource.credentials=A.user,A.password;return B
		except:return
	def build_aerospike(A):
		import aerospike as C;B={'hosts':[(A.host,A.port)]}
		if A.user and A.password:
			if len(A.user)>0:B['user']=A.user
			if len(A.password)>0:B['password']=A.password
		try:D=C.client(B).connect();return D
		except:pass
	def build_redis(A,db=0):import redis;A.set_redis_db(db);B=redis.StrictRedis(host=A.host,port=A.port,password=A.password,username=A.user,db=db);return B
	def build_duckdb(B,database_path,read_only=False):
		A=database_path
		if A is _A:return
		if not os.path.exists(A)and A!=_J:return
		B.set_database_path(A);C=duckdb.connect(A,read_only=read_only);return C
	def build_parquet(B,database_path,read_only=False):
		A=database_path
		if A is _A:return
		if not os.path.exists(A)and A!=_J:return
		B.set_database_path(A);C=duckdb.connect();return C
	def build_sqlite(B,database_path):A=database_path;B.set_database_path(A);C=sqlite3.connect(A);return C
	def build_questdb(A):
		from questdb.ingress import Sender,IngressError;B=f"http::addr={A.host}:{A.port};"
		if A.user is not _A:
			if len(A.user)>0:B+=f"username={A.user};"
		if A.password is not _A:
			if len(A.password)>0:B+=f"password={A.password};"
		return B
	def build_mongo(A):B=MongoClient(host=A.host,port=A.port,username=A.user,password=A.password);return B
	def build_influxdb(D,token,organization,user,password):
		E=organization;C=user;B=token;from influxdb_client import InfluxDBClient as F;G=f"{D.host}:{D.port}";A=_A
		if B is not _A:
			if len(B)>0:A=F(url=G,token=B,org=E)
		if A is _A:
			if C is not _A:
				if len(C)>0:A=F(url=G,username=C,password=password,org=E)
		return A
	def build_csv(A,file_path):A.set_file_path(file_path);return A
	def build_xls(A,file_path):A.set_file_path(file_path);return A
	def build_json_api(A,json_url,dynamic_inputs=_A,py_code_processing=_A):A.set_json_url(json_url);A.set_dynamic_inputs(dynamic_inputs);A.set_py_code_processing(py_code_processing)
	def build_python(A,py_code_processing=_A,dynamic_inputs=_A):A.set_py_code_processing(py_code_processing);A.set_dynamic_inputs(dynamic_inputs)
	def build_wss(A,socket_url,dynamic_inputs=_A,py_code_processing=_A):A.set_socket_url(socket_url);A.set_dynamic_inputs(dynamic_inputs);A.set_py_code_processing(py_code_processing)
	def get_sqlachemy_engine(A):return create_engine(A.url_engine)
	def get_available_views(A):
		try:B=A.get_sqlachemy_engine();C=inspect(B);D=C.get_view_names();return sorted(D)
		except Exception as E:logger.debug('Exception while retrieving available views');logger.debug(E);return[]
	def get_available_tables(A):
		try:B=A.get_sqlachemy_engine();C=inspect(B);D=C.get_table_names();return sorted(D)
		except Exception as E:logger.debug('Exception get available tables metadata');logger.debug(E);return[]
	def get_table_columns(C,table_name):
		B='type'
		try:
			D=C.get_sqlachemy_engine();E=inspect(D);A=E.get_columns(table_name)
			if A:return[{'column':A['name'],B:str(A[B])}for A in A]
		except Exception as F:logger.debug('Exception get table columuns metadata');logger.debug(F)
		return[]
	def get_data_table(B,table_name):
		A=table_name
		try:
			C=B.get_sqlachemy_engine();D=text(f"SELECT * FROM {A}")
			with C.connect()as E:F=E.execute(D);G=F.fetchall();return G
		except Exception as H:logger.debug(f"Exception while loading data from table '{A}'");logger.debug(H)
		return[]
	def get_data_table_top(B,table_name,top_limit=100):
		A=table_name
		try:
			C=B.get_sqlachemy_engine();D=text(f"SELECT * FROM {A} LIMIT {top_limit}")
			with C.connect()as E:F=E.execute(D);G=F.fetchall();return G
		except Exception as H:logger.debug(f"Exception while loading data from table '{A}'");logger.debug(H)
		return[]
	def get_data_table_query(B,sql,table_name=_A):
		A=sql
		if A is not _A:
			if len(A)>0:return B.read_sql_query(A)
		return pd.DataFrame()
	def read_sql_query(A,sql,index_col=_A,coerce_float=True,params=_A,parse_dates=_A,chunksize=_A,dtype=_A):return pd.read_sql_query(sql,con=A.connector,index_col=index_col,coerce_float=coerce_float,params=params,parse_dates=parse_dates,chunksize=chunksize,dtype=dtype)