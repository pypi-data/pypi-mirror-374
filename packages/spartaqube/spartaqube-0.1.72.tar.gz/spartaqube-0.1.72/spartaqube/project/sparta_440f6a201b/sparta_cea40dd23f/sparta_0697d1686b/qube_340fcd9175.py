_D='https_proxy'
_C='http_proxy'
_B='default'
_A=None
import io,sys,os,pandas as pd,json,requests
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_b171fdba0f import EngineBuilder
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe
from project.logger_config import logger
class JsonApiConnector(EngineBuilder):
	def __init__(self,json_url,dynamic_inputs=_A,py_code_processing=_A):super().__init__(host=_A,port=_A);self.connector=self.build_json_api(json_url=json_url,dynamic_inputs=dynamic_inputs,py_code_processing=py_code_processing);self.json_url=json_url;self.dynamic_inputs=dynamic_inputs;self.py_code_processing=py_code_processing
	def test_connection(self):
		self.error_msg_test_connection=''
		if self.dynamic_inputs is not _A:
			if len(self.dynamic_inputs)>0:
				for input_dict in self.dynamic_inputs:self.json_url=self.json_url.replace('{'+str(input_dict['input'])+'}',input_dict[_B])
		proxies_dict={'http':os.environ.get(_C,_A),'https':os.environ.get(_D,_A)};response=requests.get(self.json_url,proxies=proxies_dict)
		if response.status_code==200:return True
		else:self.error_msg_test_connection=f"Could not establish connection with status code response: {response.status_code}";return False
	def preview_output_connector_bowler(self,b_get_print_buffer=True):
		self.error_msg_test_connection=''
		if self.dynamic_inputs is not _A:
			if len(self.dynamic_inputs)>0:
				for input_dict in self.dynamic_inputs:self.json_url=self.json_url.replace('{'+str(input_dict['input'])+'}',input_dict[_B])
		logger.debug('JSON URL');logger.debug(self.json_url);proxies_dict={'http':os.environ.get(_C,_A),'https':os.environ.get(_D,_A)};response=requests.get(self.json_url,proxies=proxies_dict)
		if response.status_code==200:
			resp=response.text;print_buffer_content=''
			if self.py_code_processing is not _A:
				try:
					self.py_code_processing=self.py_code_processing+'\nresp_preview = resp'
					if b_get_print_buffer:stdout_buffer=io.StringIO();sys.stdout=stdout_buffer;exec(self.py_code_processing,globals(),locals());print_buffer_content=stdout_buffer.getvalue();sys.stdout=sys.__stdout__
					else:exec(self.py_code_processing,globals(),locals())
					resp=eval('resp_preview')
				except Exception as e:raise Exception(e)
			return resp,print_buffer_content
		else:raise Exception(f"Could not establish connection with status code response: {response.status_code}")
	def get_json_api_dataframe(self):
		preview_output_list=self.preview_output_connector_bowler(b_get_print_buffer=False)
		if preview_output_list is not _A:resp,_=preview_output_list;resp=convert_to_dataframe(resp);return resp
	def get_available_tables(self):return[]