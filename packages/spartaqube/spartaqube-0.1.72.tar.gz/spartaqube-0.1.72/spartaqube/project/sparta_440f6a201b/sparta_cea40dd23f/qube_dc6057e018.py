_A='utf-8'
import base64,hashlib
from cryptography.fernet import Fernet
def sparta_e82c330585():B='db-conn';A=B.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A.decode(_A)
def sparta_5952741046(password_to_encrypt):A=password_to_encrypt;A=A.encode(_A);C=Fernet(sparta_e82c330585().encode(_A));B=C.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_318a4d7bee(password_e):B=Fernet(sparta_e82c330585().encode(_A));A=base64.b64decode(password_e);A=B.decrypt(A).decode(_A);return A
def sparta_872ba2a643():
	R='influxdb';Q='cassandra';P='questdb';O='clickhouse';N='oracle';M=True;L=False;K='is_available';J='is_default';I='aerospike';H='couchdb';G='redis';E='name';B='lib';A='pip';F={N:{B:'cx_Oracle',A:['cx_Oracle==8.3.1']},G:{B:G,A:['redis==5.0.1']},H:{B:H,A:['CouchDB==1.2']},I:{B:I,A:['aerospike==15.0.0']},O:{B:'clickhouse_connect',A:['clickhouse-connect==0.7.16']},P:{B:'questdb.ingress',A:['questdb==1.2.0']},Q:{B:'cassandra.cluster',A:['cassandra-driver==3.29.0']},R:{B:'influxdb_client',A:['influxdb-client==1.44.0','influxdb==5.3.2']}};S=sorted([I,Q,O,H,'csv','duckdb',R,'json_api','mariadb','mongo','mssql','mysql',N,'parquet','postgres','python',P,G,'scylladb','sqlite','wss']);D=[]
	for C in S:
		if C in F:
			T=F[C][B]
			try:__import__(T);D.append({E:C,J:L,K:M})
			except ImportError:D.append({E:C,J:L,K:L,A:F[C][A]})
		else:D.append({E:C,J:M,K:M})
	U=sorted(D,key=lambda x:x[E]);return U