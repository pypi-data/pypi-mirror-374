import os,threading
from threading import Thread
import sys,queue,signal,traceback
from project.logger_config import logger
import ctypes
def sparta_1b94351f5d(thread):
	A=thread
	if not A.isAlive():return
	C=ctypes.py_object(SystemExit);B=ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(A.ident),C)
	if B==0:raise ValueError('nonexistent thread id')
	elif B>1:ctypes.pythonapi.PyThreadState_SetAsyncExc(A.ident,None);raise SystemError('PyThreadState_SetAsyncExc failed')
class TimeoutError(Exception):0
class FailedProcess:
	def __init__(A,exceptionMsg,exceptionType):A.exceptionMsg=exceptionMsg;A.exceptionType=exceptionType
class InterruptableThread(threading.Thread):
	def __init__(A,func,*B,**C):threading.Thread.__init__(A,daemon=True);A._func=func;A._args=B;A._kwargs=C;A._result=None
	def run(A):
		C='*******************************************************************'
		try:A._result=A._func(*A._args,**A._kwargs)
		except Exception as B:logger.debug(C);logger.debug('Traceback timeout');logger.debug(traceback.format_exc());logger.debug('error > ');logger.debug(str(B));logger.debug(C);A._result=FailedProcess(str(B),B.__class__.__name__)
	@property
	def result(self):return self._result
class timeout:
	def __init__(A,sec):A._sec=sec
	def __call__(B,f):
		def A(*C,**D):
			A=InterruptableThread(f,*C,**D);A.daemon=True;A.start();A.join(B._sec)
			if not A.is_alive():logger.debug('XXXXXXXXXXXXXXX RETURN NOW XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX');logger.debug(A.result);return A.result
			sparta_1b94351f5d(A);raise TimeoutError(f"Timeout exception (you code cannot run more than {B._sec} seconds, please contact us if you require more computation power)")
		return A