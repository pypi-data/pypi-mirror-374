from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
from project.logger_config import logger
class PostgresConnector(EngineBuilder):
	def __init__(A,host,port,user,password,database):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='postgresql');A.connector=A.connect_db()
	def connect_db(A):return A.build_postgres()
	def test_connection(A):
		B=False
		try:
			if A.connector:A.connector.close();return True
			else:return B
		except Exception as C:logger.debug(f"Error: {C}");return B