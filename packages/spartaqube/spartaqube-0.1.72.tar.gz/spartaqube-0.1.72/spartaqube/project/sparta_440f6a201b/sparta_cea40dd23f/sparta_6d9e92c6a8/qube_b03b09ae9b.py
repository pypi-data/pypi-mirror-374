_A=None
import pandas as pd
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
class MssqlConnector(EngineBuilder):
	def __init__(A,host,port,trusted_connection,driver,user,password,database):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='mssql+pyodbc');A.trusted_connection=trusted_connection;A.driver=driver;A.connector=A.connect_db()
	def connect_db(A):return A.build_mssql(A.trusted_connection,A.driver)
	def test_connection(A):
		F=False;A.connector=A.connect_db()
		if A.connector is _A:return F
		D=F
		try:
			B=A.connector;C=B.cursor();G='SELECT @@VERSION';C.execute(G);E=C.fetchone()
			while E:E=C.fetchone()
			D=True
		except Exception as H:A.error_msg_test_connection=str(H)
		try:
			if B:B.close()
		except:pass
		return D
	def get_available_tables(A):
		A.connector=A.connect_db()
		if A.connector is _A:return[]
		B=[]
		try:C=A.connector;D="SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'";E=pd.read_sql(D,C);B=sorted(list(E['TABLE_NAME'].values))
		except Exception as F:A.error_msg_test_connection=str(F);B=[]
		finally:
			if C:C.close()
		return B
	def get_table_columns(A,table_name):
		A.connector=A.connect_db()
		if A.connector is _A:return[]
		B=[]
		try:C=A.connector;D=f"\n                SELECT COLUMN_NAME\n                FROM INFORMATION_SCHEMA.COLUMNS\n                WHERE TABLE_NAME = '{table_name}'\n                ";E=pd.read_sql(D,C);B=sorted(list(E['COLUMN_NAME'].values))
		except Exception as F:A.error_msg_test_connection=str(F);B=[]
		finally:
			if C:C.close()
		return B
	def get_data_table(A,table_name):
		A.connector=A.connect_db()
		if A.connector is _A:return pd.DataFrame()
		try:B=A.connector;C=f"SELECT * FROM {table_name}";D=pd.read_sql(C,B);return D
		except Exception as E:A.error_msg_test_connection=str(E);return pd.DataFrame()
		finally:
			if B:B.close()
	def get_data_table_top(A,table_name,top_limit=100):
		A.connector=A.connect_db()
		if A.connector is _A:return pd.DataFrame()
		try:B=A.connector;C=f"SELECT TOP {top_limit} * FROM {table_name}";D=pd.read_sql(C,B);return D
		except Exception as E:A.error_msg_test_connection=str(E);return pd.DataFrame()
		finally:
			if B:B.close()
	def get_data_table_query(A,sql,table_name=_A):
		A.connector=A.connect_db()
		if A.connector is _A:return pd.DataFrame()
		try:B=A.connector;C=sql;D=pd.read_sql(C,B);return D
		except Exception as E:A.error_msg_test_connection=str(E);return pd.DataFrame()
		finally:
			if B:B.close()
	def get_available_views(A):
		A.connector=A.connect_db()
		if A.connector is _A:return[]
		B=[]
		try:C=A.connector;D='SELECT name FROM sys.views ORDER BY name';E=pd.read_sql(D,C);B=sorted(list(E['name'].values))
		except Exception as F:A.error_msg_test_connection=str(F);B=[]
		finally:
			if C:C.close()
		return B