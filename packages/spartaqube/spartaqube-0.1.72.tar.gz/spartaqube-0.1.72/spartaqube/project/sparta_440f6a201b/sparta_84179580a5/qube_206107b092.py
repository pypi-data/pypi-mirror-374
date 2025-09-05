import json,base64,asyncio,subprocess,uuid,os,requests,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared
from project.models import ShareRights
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
from project.sparta_440f6a201b.sparta_cea40dd23f import qube_dc6057e018
from project.sparta_440f6a201b.sparta_aea4c35167 import qube_2fc75b9545 as qube_2fc75b9545
from project.sparta_440f6a201b.sparta_cea40dd23f.qube_1b9826e2d7 import Connector as Connector
from project.logger_config import logger
def sparta_3ae33c3386(json_data,user_obj):
	D='key';A=json_data;logger.debug('Call autocompelte api');logger.debug(A);B=A[D];E=A['api_func'];C=[]
	if E=='tv_symbols':C=sparta_944d2cbe8f(B)
	return{'res':1,'output':C,D:B}
def sparta_944d2cbe8f(key_symbol):
	F='</em>';E='<em>';B='symbol_id';G=f"https://symbol-search.tradingview.com/local_search/v3/?text={key_symbol}&hl=1&exchange=&lang=en&search_type=undefined&domain=production&sort_by_country=US";H={'http':os.environ.get('http_proxy',None),'https':os.environ.get('https_proxy',None)};C=requests.get(G,proxies=H)
	try:
		if int(C.status_code)==200:
			I=json.loads(C.text);D=I['symbols']
			for A in D:A[B]=A['symbol'].replace(E,'').replace(F,'');A['title']=A[B];A['subtitle']=A['description'].replace(E,'').replace(F,'');A['value']=A[B]
			return D
		return[]
	except:return[]