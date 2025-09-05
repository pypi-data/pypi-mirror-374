_A=None
from email.utils import make_msgid
from django.contrib.auth.models import User
from project.sparta_440f6a201b.sparta_804dd6b985 import qube_03613a31ee as qube_03613a31ee
from spartaqube_app.secrets import sparta_61772791e6
from project.logger_config import logger
def send(emailObj,USERNAME_SMTP=_A,PASSWORD_SMTP=_A,EMAIL_SMTP=_A,HOST=_A,PORT=25,SENDERNAME=_A):return sendEmailFunc(emailObj,USERNAME_SMTP,PASSWORD_SMTP,EMAIL_SMTP,HOST,PORT,SENDERNAME)
def sendEmailFunc(emailObj,USERNAME_SMTP=_A,PASSWORD_SMTP=_A,EMAIL_SMTP=_A,HOST=_A,PORT=25,SENDERNAME=_A):
	T='attachment; filename="%s"';S='Content-Disposition';R='base64';Q='Content-Transfer-Encoding';P='errorMsg';O='res';K=PASSWORD_SMTP;H=EMAIL_SMTP;G=SENDERNAME;F=USERNAME_SMTP;C=emailObj;import smtplib as U,email.utils;from email.mime.multipart import MIMEMultipart as V;from email.mime.text import MIMEText as W;from email.mime.image import MIMEImage;from email.mime.base import MIMEBase as L;I=','.join(C.getRecipients())
	if G is _A:G='My Project'
	if F is _A:D=sparta_61772791e6();HOST=D['EMAIL_HOST_SMTP'];F=D['EMAIL_USERNAME_SMTP'];H=D['EMAIL_RECIPIENT'];K=D['EMAIL_PASSWORD_SMTP'];PORT=D['EMAIL_PORT_SMTP'];G=D['EMAIL_SENDERNAME']
	if F is _A:return{O:-1,P:'You need to configure an email sender service in your profile view'}
	X=C.getEmailTitle();Y=C.getHTML();B=V('related');B['Subject']=X;B['From']=email.utils.formataddr((G,H));B['To']=I;B['Message-ID']=make_msgid();logger.debug('RECIPIENT');logger.debug(I);Z=C.getEmailB64ImgList();a=C.getEmailImgNameArr()
	for(J,b)in enumerate(Z):A=L('image','png');A.set_payload(b);A.add_header(Q,R);c=a[J];A[S]=T%c;B.attach(A)
	d=C.getFilesArr();e=C.getFilesNameArr()
	for(J,f)in enumerate(d):A=L('application','octet-stream');A.set_payload(f);A.add_header(Q,R);M=e[J];logger.debug('fileName > '+str(M));A[S]=T%M;B.attach(A)
	g=W(Y,'html');B.attach(g);logger.debug('SEND EMAIL NOW')
	try:E=U.SMTP(HOST,PORT);E.ehlo();E.starttls();E.ehlo();E.login(F,K);E.sendmail(H,I,B.as_string());E.close()
	except Exception as N:print('Error: ',N);return{O:-1,P:str(N)}
	else:return'Email sent!'