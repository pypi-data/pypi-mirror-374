import time
from project.logger_config import logger
def sparta_62908189fa():
	B=0;A=time.time()
	while True:B=A;A=time.time();yield A-B
TicToc=sparta_62908189fa()
def sparta_2abea5514e(tempBool=True):
	A=next(TicToc)
	if tempBool:logger.debug('Elapsed time: %f seconds.\n'%A);return A
def sparta_8bfdcf7313():sparta_2abea5514e(False)