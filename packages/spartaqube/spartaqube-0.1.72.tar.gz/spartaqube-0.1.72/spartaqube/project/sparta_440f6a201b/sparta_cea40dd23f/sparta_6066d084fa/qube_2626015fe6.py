_D='columns'
_C='name'
_B='dataset'
_A='query'
try:from questdb.ingress import Sender,IngressError,TimestampNanos
except:pass
import os,time,requests,pandas as pd
from requests.auth import HTTPBasicAuth
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe
class QuestDBConnector(EngineBuilder):
	def __init__(A,host,port,user,password,database):
		B=host;A.proxies_dict={'http':os.environ.get('http_proxy',None),'https':os.environ.get('https_proxy',None)}
		if B.startswith('localhost'):B='http://localhost'
		super().__init__(host=B,port=port,user=user,password=password,database=database,engine_name='questdb');A.conf=A.build_questdb()
	def test_connection(A):
		try:
			with Sender.from_conf(A.conf)as B:B.flush()
			return True
		except IngressError as C:A.error_msg_test_connection=str(C);return False
	def get_available_tables(A):
		C=f"{A.host}:{A.port}/exec";D='SHOW TABLES'
		try:B=requests.get(C,params={_A:D},auth=HTTPBasicAuth(A.user,A.password),proxies=A.proxies_dict);B.raise_for_status();E=B.json();F=[A[0]for A in E[_B]];return sorted(F)
		except requests.RequestException as G:A.error_msg_test_connection=str(G);return[]
	def get_table_columns(A,table_name):
		C=f"{A.host}:{A.port}/exec";D=f"SHOW COLUMNS FROM {table_name}"
		try:B=requests.get(C,params={_A:D},auth=HTTPBasicAuth(A.user,A.password),proxies=A.proxies_dict);B.raise_for_status();E=B.json();F=[A['table']for A in E[_B]];return F
		except requests.RequestException as G:A.error_msg_test_connection=str(G);return[]
	def get_data_table(A,table_name):E=f"{A.host}:{A.port}/exec";F=f"SELECT * FROM {table_name}";B=requests.get(E,params={_A:F},auth=HTTPBasicAuth(A.user,A.password),proxies=A.proxies_dict);B.raise_for_status();C=B.json();G=[A[_C]for A in C[_D]];D=convert_to_dataframe(C[_B]);D.columns=G;return D
	def get_data_table_top(A,table_name,top_limit=100):E=f"{A.host}:{A.port}/exec";F=f"SELECT * FROM {table_name} LIMIT {top_limit}";B=requests.get(E,params={_A:F},auth=HTTPBasicAuth(A.user,A.password),proxies=A.proxies_dict);B.raise_for_status();C=B.json();G=[A[_C]for A in C[_D]];D=convert_to_dataframe(C[_B]);D.columns=G;return D
	def get_data_table_query(A,sql,table_name=None):E=f"{A.host}:{A.port}/exec";F=sql;B=requests.get(E,params={_A:F},auth=HTTPBasicAuth(A.user,A.password),proxies=A.proxies_dict);B.raise_for_status();C=B.json();G=[A[_C]for A in C[_D]];D=convert_to_dataframe(C[_B]);D.columns=G;return D