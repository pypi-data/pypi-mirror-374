try:import clickhouse_connect
except:pass
import pandas as pd
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe
class ClickhouseConnector(EngineBuilder):
	def __init__(A,host,port,database,user='default',password=''):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='clickhouse');A.connector=A.build_clickhouse()
	def test_connection(A):
		C=False
		try:
			B=clickhouse_connect.get_client(host=A.host,port=A.port,user=A.user,password=A.password,database=A.database);D=f"SELECT name FROM system.databases WHERE name = '{A.database}'";E=B.query(D)
			if E.result_rows:C=True
			else:A.error_msg_test_connection='Invalid database'
		except Exception as F:A.error_msg_test_connection=str(F)
		finally:
			if B:B.close()
		return C
	def get_available_tables(A):
		B=[]
		try:C=A.connector;D=f"SHOW TABLES FROM {A.database}";E=C.query(D);B=[A[0]for A in E.result_rows]
		except Exception as F:A.error_msg_test_connection=str(F);B=[]
		finally:
			if C:C.close()
		return B
	def get_table_columns(A,table_name):
		B=[]
		try:C=A.connector;D=f"\n                SELECT name, type FROM system.columns \n                WHERE database = '{A.database}' AND table = '{table_name}'\n                ";E=C.query(D);B=[A[1]for A in E.result_rows]
		except Exception as F:A.error_msg_test_connection=str(F);B=[]
		finally:
			if C:C.close()
		return B
	def get_data_table(E,table_name):
		try:
			A=E.connector;C=f"SELECT * FROM {table_name}";B=A.query(C);D=B.result_columns;B=A.query(C);D=B.column_names;F=B.result_rows;G=convert_to_dataframe(pd.DataFrame(F,columns=D))
			if A:A.close()
			return G
		except Exception as H:
			if A:A.close()
			raise Exception(H)
	def get_data_table_top(E,table_name,top_limit=100):
		try:
			A=E.connector;C=f"SELECT * FROM {table_name} LIMIT {top_limit}";B=A.query(C);D=B.result_columns;B=A.query(C);D=B.column_names;F=B.result_rows;G=convert_to_dataframe(pd.DataFrame(F,columns=D))
			if A:A.close()
			return G
		except Exception as H:
			if A:A.close()
			raise Exception(H)
	def get_data_table_query(E,sql,table_name=None):
		try:
			A=E.connector;C=sql;B=A.query(C);D=B.result_columns;B=A.query(C);D=B.column_names;F=B.result_rows;G=convert_to_dataframe(pd.DataFrame(F,columns=D))
			if A:A.close()
			return G
		except Exception as H:
			if A:A.close()
			raise Exception(H)