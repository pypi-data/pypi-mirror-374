_A=None
import pandas as pd
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe
class ArcticConnector(EngineBuilder):
	def __init__(A,database_path,library_arctic):
		C=library_arctic;B=database_path;A.database_path=B;A.library_arctic=C;super().__init__(host=_A,port=_A,engine_name='arctic')
		try:A.connector=A.build_arctic(B,C)
		except:A.connector=_A
	def test_connection(A):
		D='Missing library';C='Missing path or endpoint';B=False
		if A.database_path is _A:A.error_msg_test_connection=C;return B
		if len(A.database_path)==0:A.error_msg_test_connection=C;return B
		if A.library_arctic is _A:A.error_msg_test_connection=D;return B
		if len(A.library_arctic)==0:A.error_msg_test_connection=D;return B
		try:
			E=A.connector
			if A.library_arctic in E.list_libraries():return True
			else:A.error_msg_test_connection='Invalid path folder, endpoint or library';return B
		except Exception as F:A.error_msg_test_connection=str(F);return B
	def get_available_tables(A):
		try:B=A.connector;C=B[A.library_arctic];return list(C.list_symbols())
		except Exception as D:A.error_msg_test_connection=str(D);return[]
	def get_table_columns(A,table_name):
		try:B=A.connector;C=B[A.library_arctic];D=C.read_metadata(table_name);E=D['schema']['fields'];F=[A['name']for A in E];return F
		except Exception as G:A.error_msg_test_connection=str(G);return[]
	def get_data_table(A,table_name):B=A.connector;C=B[A.library_arctic];return convert_to_dataframe(C.read(table_name).data)
	def get_data_table_top(A,table_name,top_limit=100):
		B=A.get_data_table(table_name)
		try:return B.head(top_limit)
		except:return pd.DataFrame()