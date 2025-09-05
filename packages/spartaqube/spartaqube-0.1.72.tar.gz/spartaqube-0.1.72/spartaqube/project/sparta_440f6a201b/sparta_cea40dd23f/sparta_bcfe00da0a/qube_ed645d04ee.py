_A='get available tables error'
import sqlite3
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
from project.logger_config import logger
class SqliteConnector(EngineBuilder):
	def __init__(A,database_path):super().__init__(host=None,port=None,engine_name='sqlite');A.database_path=database_path;A.set_url_engine(f"sqlite:///{A.database_path}");A.connector=A.connect_db()
	def connect_db(A):return A.build_sqlite(database_path=A.database_path)
	def test_connection(A):
		B=False
		try:
			if A.connector:A.connector.close();return True
			else:return B
		except Exception as C:A.error_msg_test_connection=str(C);return B
	def get_available_tables(C):
		try:A=C.connector;B=A.cursor();B.execute("SELECT name FROM sqlite_master WHERE type='table';");D=B.fetchall();A.close();return sorted([A[0]for A in D])
		except Exception as E:logger.debug(_A);logger.debug(E)
		try:A.close()
		except:pass
		return[]
	def get_table_columns(C,table_name):
		try:A=C.connector;B=A.cursor();B.execute(f"PRAGMA table_info({table_name});");D=B.fetchall();E=[{'column':A[1],'type':A[2]}for A in D];A.close();return E
		except Exception as F:logger.debug(_A);logger.debug(F)
		try:A.close()
		except:pass
		return[]