_B='_id'
_A=False
try:from pymongo import MongoClient;from pymongo.errors import ConnectionFailure
except:pass
import pandas as pd
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe
from project.logger_config import logger
class MongoConnector(EngineBuilder):
	def __init__(self,host,port,user,password,database):port=int(port);super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='mongodb');self.database=database;self.client=None;self.connector=self.connect_db()
	def connect_db(self):self.client=self.build_mongo();return self.client[self.database]
	def test_connection(self):
		try:
			client=MongoClient(host=self.host,username=self.user,port=self.port,password=self.password,serverSelectionTimeoutMS=2000);res_ping=client.admin.command('ping');databases=client.list_database_names();res=_A
			if self.database in databases:res=True
			self.error_msg_test_connection=f"MongoDB connection is valid but database '{self.database}' does not exist. Available databases are: {', '.join(databases)}";client.close();return res
		except ConnectionFailure:self.error_msg_test_connection='MongoDB connection test failed: Unable to connect to the server';return _A
		except Exception as e:logger.debug(f"MongoDB connection test failed: {e}");self.error_msg_test_connection=str(e);return _A
	def get_available_tables(self):
		try:collections=self.connector.list_collection_names();self.client.close();return collections
		except Exception as e:self.client.close();logger.debug(f"Failed to list tables: {e}");return[]
	def get_table_columns(self,table_name):
		collection_name=table_name;sample_size=100
		try:
			db=self.connector;collection=db[collection_name];documents=collection.find().limit(sample_size);field_names=set()
			for doc in documents:field_names.update(doc.keys())
			self.client.close();return sorted(list(field_names))
		except Exception as e:self.client.close();logger.debug(f"Failed to list columns for table '{table_name}': {e}");return[]
	def get_data_table(self,table_name):
		collection_name=table_name
		try:db=self.connector;collection=db[collection_name];documents=list(collection.find({},{_B:_A}));self.client.close();return convert_to_dataframe(documents)
		except Exception as e:self.client.close();raise Exception(e)
	def get_data_table_top(self,table_name,top_limit=100):
		collection_name=table_name
		try:db=self.connector;collection=db[collection_name];documents=list(collection.find({},{_B:_A}).limit(top_limit));self.client.close();return convert_to_dataframe(documents)
		except Exception as e:self.client.close();raise Exception(e)
	def get_data_table_query(self,sql,table_name=None):
		try:exec(sql,globals(),locals());filters_to_apply=eval('filter_criteria');collection_name=table_name;db=self.connector;collection=db[collection_name];documents=list(collection.find(filters_to_apply,{_B:_A}));self.client.close();return convert_to_dataframe(documents)
		except Exception as e:self.client.close();raise Exception(e)