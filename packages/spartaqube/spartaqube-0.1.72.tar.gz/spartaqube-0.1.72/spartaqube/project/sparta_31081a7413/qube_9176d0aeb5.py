import os
class writeLog:
	def __init__(A):0
	def write(C,thisText):A=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))));A=A+str('/log/log.txt');B=open(A,'a');B.write(thisText);B.writelines('\n');B.close()