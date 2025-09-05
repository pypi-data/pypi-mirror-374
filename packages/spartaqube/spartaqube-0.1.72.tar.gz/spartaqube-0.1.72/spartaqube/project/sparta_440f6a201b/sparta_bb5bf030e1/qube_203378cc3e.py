_F='output'
_E=False
_D=None
_C='res'
_B='utf-8'
_A='name'
import os,sys,json,ast,re,base64,uuid,hashlib,socket,cloudpickle,websocket,subprocess,threading
from random import randint
import pandas as pd
from pathlib import Path
from cryptography.fernet import Fernet
from subprocess import PIPE
from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.cache import cache
from django.conf import settings as conf_settings
from asgiref.sync import sync_to_async
import pytz
UTC=pytz.utc
from spartaqube_app.path_mapper_obf import sparta_fc868586da
from project.models import UserProfile,NewPlotApiVariables,NotebookShared,DashboardShared
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
from project.sparta_440f6a201b.sparta_aea4c35167 import qube_477699d437 as qube_477699d437
from project.sparta_440f6a201b.sparta_9df2ef9f24 import qube_7fa0ebc7a1 as qube_7fa0ebc7a1
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_to_dataframe,convert_dataframe_to_json,sparta_a253265c85
from project.sparta_440f6a201b.sparta_ceff546bba.qube_a44c916988 import sparta_12b87f0842,sparta_d3a3936389
from project.logger_config import logger
def sparta_97fe3068bb(file_path=_D,text=_D,b_log=True):
	if text is _D:return
	if file_path is _D:file_path='C:\\Users\\benme\\Desktop\\LOG_DEBUG.txt'
	try:
		mode='a'if os.path.exists(file_path)and os.path.getsize(file_path)>0 else'w'
		with open(file_path,mode,encoding=_B)as file:
			if mode=='a':file.write('\n')
			file.write(text)
		if b_log:logger.debug(f"Successfully wrote/appended to {file_path}")
	except Exception as e:
		if b_log:logger.debug(f"Error writing to file: {e}")
def sparta_35ac6c1a32():keygen_fernet='spartaqube-api-key';key=keygen_fernet.encode(_B);key=hashlib.md5(key).hexdigest();key=base64.b64encode(key.encode(_B));return key.decode(_B)
def sparta_417db7b20b():keygen_fernet='spartaqube-internal-decoder-api-key';key=keygen_fernet.encode(_B);key=hashlib.md5(key).hexdigest();key=base64.b64encode(key.encode(_B));return key.decode(_B)
def sparta_b20b0146ba(f,str_to_encrypt):data_to_encrypt=str_to_encrypt.encode(_B);token=f.encrypt(data_to_encrypt).decode(_B);token=base64.b64encode(token.encode(_B)).decode(_B);return token
def sparta_8246bbabca(api_token_id):
	if api_token_id=='public':
		try:return User.objects.filter(email='public@spartaqube.com').all()[0]
		except:return
	try:
		f_private=Fernet(sparta_417db7b20b().encode(_B));api_key=f_private.decrypt(base64.b64decode(api_token_id)).decode(_B).split('@')[1];user_profile_set=UserProfile.objects.filter(api_key=api_key,is_banned=_E).all()
		if user_profile_set.count()==1:return user_profile_set[0].user
		return
	except Exception as e:logger.debug('Could not authenticate api with error msg:');logger.debug(e);return
def sparta_08311cba71(user_obj):
	userprofile_obj=UserProfile.objects.get(user=user_obj);api_key=userprofile_obj.api_key
	if api_key is _D:api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;userprofile_obj.save()
	return api_key
async def get_api_key_async_DEPREC(user_obj):
	userprofile_obj=await UserProfile.objects.aget(user=user_obj);api_key=userprofile_obj.api_key
	if api_key is _D:api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;await userprofile_obj.asave()
	return api_key
async def get_api_key_async(user_obj):
	userprofile_obj=await sync_to_async(lambda:UserProfile.objects.get(user=user_obj),thread_sensitive=_E)()
	if userprofile_obj.api_key is _D:userprofile_obj.api_key=str(uuid.uuid4());await sync_to_async(userprofile_obj.save,thread_sensitive=_E)()
	return userprofile_obj.api_key
def sparta_8b9995568a(user_obj,domain_name):api_key=sparta_08311cba71(user_obj);random_nb=str(randint(0,1000));data_to_encrypt=f"apikey@{api_key}@{random_nb}";f_private=Fernet(sparta_417db7b20b().encode(_B));private_encryption=sparta_b20b0146ba(f_private,data_to_encrypt);data_to_encrypt=f"apikey@{domain_name}@{private_encryption}";f_public=Fernet(sparta_35ac6c1a32().encode(_B));public_encryption=sparta_b20b0146ba(f_public,data_to_encrypt);return public_encryption
def sparta_39dad58f81(json_data,user_obj):api_key=sparta_08311cba71(user_obj);domain_name=json_data['domain'];public_encryption=sparta_8b9995568a(user_obj,domain_name);return{_C:1,'token':public_encryption}
def sparta_76b0888e16(json_data,user_obj):userprofile_obj=UserProfile.objects.get(user=user_obj);api_key=str(uuid.uuid4());userprofile_obj.api_key=api_key;userprofile_obj.save();return{_C:1}
def sparta_adc9455792():plot_types=sparta_12b87f0842();plot_types=sorted(plot_types,key=lambda x:x['Library'].lower(),reverse=_E);return{_C:1,'plot_types':plot_types}
def sparta_0e96fd0c0d(json_data):logger.debug('DEBUG get_plot_options json_data');logger.debug(json_data);plot_type=json_data['plot_type'];plot_input_options_dict=sparta_d3a3936389(plot_type);plot_input_options_dict[_C]=1;return plot_input_options_dict
def sparta_1ccc9615eb(code):
	tree=ast.parse(code)
	if isinstance(tree.body[-1],ast.Expr):last_expr_node=tree.body[-1].value;last_expr_code=ast.unparse(last_expr_node);return last_expr_code
	else:return
def sparta_38156b0b87(json_data,user_obj):
	A='errorMsg';user_code_example=json_data['userCode'];resp=_D;error_msg=''
	try:
		logger.debug('EXECUTE API EXAMPLE DEBUG DEBUG DEBUG');api_key=sparta_08311cba71(user_obj);core_api_path=sparta_fc868586da()['project/core/api'];ini_code='import os, sys\n';ini_code+=f'sys.path.insert(0, r"{str(core_api_path)}")\n';ini_code+='from spartaqube import Spartaqube as Spartaqube\n';ini_code+=f"Spartaqube('{api_key}')\n";user_code_example=ini_code+'\n'+user_code_example;exec(user_code_example,globals());last_expression_str=sparta_1ccc9615eb(user_code_example)
		if last_expression_str is not _D:
			last_expression_output=eval(last_expression_str)
			if last_expression_output.__class__.__name__=='HTML':resp=last_expression_output.data
			else:resp=last_expression_output
			resp=json.dumps(resp);return{_C:1,'resp':resp,A:error_msg}
		return{_C:-1,A:'No output to display. You should put the variable to display as the last line of the code'}
	except Exception as e:return{_C:-1,A:str(e)}
def sparta_9260c9bc07(json_data,user_obj):
	session_id=json_data['session'];new_plot_api_variables_set=NewPlotApiVariables.objects.filter(session_id=session_id).all();logger.debug(f"gui_plot_api_variables with session_id {session_id}");logger.debug(new_plot_api_variables_set)
	if new_plot_api_variables_set.count()>0:
		new_plot_api_variables_obj=new_plot_api_variables_set[0];pickled_variables=new_plot_api_variables_obj.pickled_variables;unpickled_data=cloudpickle.loads(pickled_variables.encode('latin1'));notebook_variables=[]
		for notebook_variable in unpickled_data:
			notebook_variables_df=convert_to_dataframe(notebook_variable)
			if notebook_variables_df is not _D:0
			else:notebook_variables_df=pd.DataFrame()
			notebook_variables.append(convert_dataframe_to_json(notebook_variables_df))
		logger.debug(notebook_variables);return{_C:1,'notebook_variables':notebook_variables}
	return{_C:-1}
def sparta_ec424d956b(json_data,user_obj):widget_id=json_data['widgetId'];return qube_477699d437.sparta_ec424d956b(user_obj,widget_id)
def sparta_b63c468bde(json_data,user_obj):
	A='api_service';api_service=json_data[A];print(A);print(api_service)
	if api_service=='get_status':output=sparta_96983a6d60()
	elif api_service=='get_status_ws':return sparta_fbeb1c346c()
	elif api_service=='get_connectors':return sparta_3d7e8fe1c2(json_data,user_obj)
	elif api_service=='get_connector_tables':return sparta_019f3de200(json_data,user_obj)
	elif api_service=='get_data_from_connector':return sparta_b2ad36f3c5(json_data,user_obj)
	elif api_service=='get_widgets':output=sparta_e8710bfdf3(user_obj)
	elif api_service=='has_widget_id':return sparta_9531d03838(json_data,user_obj)
	elif api_service=='get_widget_data':return sparta_657ef01579(json_data,user_obj)
	elif api_service=='get_plot_types':return sparta_12b87f0842()
	elif api_service=='put_df':return sparta_b0e34ba084(json_data,user_obj)
	elif api_service=='drop_df':return sparta_8b98764768(json_data,user_obj)
	elif api_service=='drop_dispo_df':return sparta_b2cc4498e8(json_data,user_obj)
	elif api_service=='get_available_df':return sparta_a3cacd55a9(json_data,user_obj)
	elif api_service=='get_df':return sparta_d4f5785b5a(json_data,user_obj)
	elif api_service=='has_dataframe_slug':return sparta_bf6e4e189e(json_data,user_obj)
	return{_C:1,_F:output}
def sparta_96983a6d60():return 1
def sparta_3d7e8fe1c2(json_data,user_obj):
	A='db_connectors';keys_to_retain=['connector_id',_A,'db_engine'];res_dict=qube_477699d437.sparta_34b93e99ae(json_data,user_obj)
	if res_dict[_C]==1:res_dict[A]=[{k:d[k]for k in keys_to_retain if k in d}for d in res_dict[A]]
	return res_dict
def sparta_019f3de200(json_data,user_obj):res_dict=qube_477699d437.sparta_222396bfd6(json_data,user_obj);return res_dict
def sparta_b2ad36f3c5(json_data,user_obj):res_dict=qube_477699d437.sparta_eadb378663(json_data,user_obj);return res_dict
def sparta_e8710bfdf3(user_obj):return qube_477699d437.sparta_41e19b7ef4(user_obj)
def sparta_9531d03838(json_data,user_obj):return qube_477699d437.sparta_e82e236f3b(json_data,user_obj)
def sparta_657ef01579(json_data,user_obj):return qube_477699d437.sparta_ae8689d9ca(json_data,user_obj)
def sparta_b0e34ba084(json_data,user_obj):return qube_7fa0ebc7a1.sparta_27b5de16e0(json_data,user_obj)
def sparta_8b98764768(json_data,user_obj):return qube_7fa0ebc7a1.sparta_ff546ed8a8(json_data,user_obj)
def sparta_b2cc4498e8(json_data,user_obj):return qube_7fa0ebc7a1.sparta_9543b3cc6a(json_data,user_obj)
def sparta_a3cacd55a9(json_data,user_obj):return qube_7fa0ebc7a1.sparta_0839dbe1a8(json_data,user_obj)
def sparta_d4f5785b5a(json_data,user_obj):return qube_7fa0ebc7a1.sparta_911c15915b(json_data,user_obj)
def sparta_bf6e4e189e(json_data,user_obj):return qube_7fa0ebc7a1.sparta_ca1b6cb709(json_data,user_obj)
def sparta_3a0c331276(json_data,user_obj):date_now=datetime.now().astimezone(UTC);session_id=str(uuid.uuid4());pickled_data=json_data['data'];NewPlotApiVariables.objects.create(user=user_obj,session_id=session_id,pickled_variables=pickled_data,date_created=date_now,last_update=date_now);return{_C:1,'session_id':session_id}
def sparta_ad444d97a9():return sparta_12b87f0842()
def sparta_d657bfd518():cache.clear();return{_C:1}
def sparta_fbeb1c346c():
	global is_wss_valid;is_wss_valid=_E
	try:
		api_path=sparta_fc868586da()['api']
		with open(os.path.join(api_path,'app_data_asgi.json'),'r')as json_file:loaded_data_dict=json.load(json_file)
		ASGI_PORT=int(loaded_data_dict['default_port'])
	except:ASGI_PORT=5664
	logger.debug('ASGI_PORT');logger.debug(ASGI_PORT)
	def on_open(ws):global is_wss_valid;is_wss_valid=True;ws.close()
	def on_error(ws,error):global is_wss_valid;is_wss_valid=_E;ws.close()
	def on_close(ws,close_status_code,close_msg):
		try:logger.debug(f"Connection closed with code: {close_status_code}, message: {close_msg}");ws.close()
		except Exception as e:logger.debug(f"Except: {e}")
	ws=websocket.WebSocketApp(f"ws://127.0.0.1:{ASGI_PORT}/ws/statusWS",on_open=on_open,on_close=on_close);ws.run_forever()
	if ws.sock and ws.sock.connected:logger.debug('WebSocket is still connected. Attempting to close again.');ws.close()
	else:logger.debug('WebSocket is properly closed.')
	return{_C:1,_F:is_wss_valid}
def sparta_97a1ed0876(json_data,user_obj):
	I='displayText';H='Plot';G='-1';F='dict';E='popTitle';D='other';C='preview';B='popType';A='type';api_methods=[{_A:'Spartaqube().get_connectors()',A:1,B:F,C:'',D:'',E:'Get Connectors'},{_A:'Spartaqube().get_connector_tables("connector_id")',A:1,B:F,C:'',D:'',E:'Get Connector Tables'},{_A:'Spartaqube().get_data_from_connector("connector_id", table=None, sql_query=None, output_format=None)',A:1,B:F,C:'',D:'',E:'Get Connector Data'},{_A:'Spartaqube().get_plot_types()',A:1,B:'list',C:'',D:'',E:'Get Plot Type'},{_A:'Spartaqube().get_widgets()',A:1,B:F,C:'',D:'',E:'Get Widgets list'},{_A:'Spartaqube().iplot([var1, var2], width="100%", height=750)',A:1,B:H,C:'',D:G,E:'Interactive plot'},{_A:'Spartaqube().plot(\n    x:list=None, y:list=None, r:list=None, legend:list=None, labels:list=None, ohlcv:list=None, shaded_background:list=None, \n    datalabels:list=None, border:list=None, background:list=None, border_style:list=None, tooltips_title:list=None, tooltips_label:list=None,\n    chart_type="line", interactive=True, widget_id=None, title=None, title_css:dict=None, stacked:bool=False, date_format:str=None, time_range:bool=False,\n    gauge:dict=None, gauge_zones:list=None, gauge_zones_labels:list=None, gauge_zones_height:list=None,\n    dataframe:pd.DataFrame=None, dates:list=None, returns:list=None, returns_bmk:list=None,\n    options:dict=None, width=\'100%\', height=750\n)',A:1,B:H,C:'',D:G,I:'Spartaqube().plot(...)',E:'Programmatic plot'},{_A:'Spartaqube().get_available_df()',A:1,B:'List',C:'',D:G,E:'Get available dataframes'},{_A:'Spartaqube().get_df(table_name, dispo=None, slug=None)',A:1,B:'pd.DataFrame',C:'',D:G,E:'Get dataframe'},{_A:'Spartaqube().put_df(df:pd.DataFrame, table_name:str, dispo=None, mode="append")',A:1,B:F,C:'',D:G,E:'Insert a dataframe'},{_A:'Spartaqube().drop_df(table_name, slug=None)',A:1,B:F,C:'',D:G,E:'Drop dataframe'},{_A:'Spartaqube().drop_df_by_id(id=id)',A:1,B:F,C:'',D:G,E:'Drop dataframe (by id)'},{_A:'Spartaqube().drop_dispo_df(table_name, dispo, slug=None)',A:1,B:F,C:'',D:G,E:'Drop dataframe for dispo date'}];api_widgets_suggestions=[]
	if not user_obj.is_anonymous:
		api_get_widgets=sparta_e8710bfdf3(user_obj)
		for widget_dict in api_get_widgets:widget_id_with_quote="'"+str(widget_dict['id'])+"'";widget_cmd=f"Spartaqube().get_widget({widget_id_with_quote})";api_widgets_suggestions.append({_A:widget_cmd,I:widget_dict[_A],E:widget_dict[_A],A:2,B:'Widget',C:widget_cmd,D:widget_dict['id']})
	autocomplete_suggestions_arr=api_methods+api_widgets_suggestions;return{_C:1,'suggestions':autocomplete_suggestions_arr}
def sparta_f6bb1ee3ba(notebook_id):
	notebook_shared_set=NotebookShared.objects.filter(is_delete=0,notebook__is_delete=0,notebook__notebook_id=notebook_id)
	if notebook_shared_set.count()>0:return notebook_shared_set[0].user
def sparta_ded9e1c030(dashboard_id):
	dashboard_shared_set=DashboardShared.objects.filter(is_delete=0,dashboard__is_delete=0,dashboard__dashboard_id=dashboard_id)
	if dashboard_shared_set.count()>0:return dashboard_shared_set[0].user