from loguru import logger
import os,sys
logger.remove()
LOG_FORMAT='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{level}</cyan> |\n<white>{message}</white>\n'
sq_silent=os.environ.get('SQ_SILENT','TRUE')
if sq_silent=='TRUE':logger.add(sys.stdout,format=LOG_FORMAT,level='ERROR')
else:logger.add(sys.stdout,format=LOG_FORMAT,level='DEBUG')
from django.conf import settings as conf_settings
if conf_settings.IS_DEV:logger.add(sys.stdout,format=LOG_FORMAT,level='DEBUG')