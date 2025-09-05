_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_b50ca21e3b():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_c95ddefe76(objectToCrypt):A=objectToCrypt;C=sparta_b50ca21e3b();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_1949fc122c(apiAuth):A=apiAuth;B=sparta_b50ca21e3b();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_62cecd1b65(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_299563afc3(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_62cecd1b65(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_9774e1aaa8(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_62cecd1b65(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_b419026f20(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_f95ef44661(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_b419026f20(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_0d05c7a6b6(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_b419026f20(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_1b8b0f0fb2(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_73b44614c2(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_1b8b0f0fb2(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_0b834bd855(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_1b8b0f0fb2(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_59eb86677d():A='__SQ_IPYNB_SQ_METADATA__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_b0db1cb56c(objectToCrypt):A=objectToCrypt;C=sparta_59eb86677d();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_091b9cb70f(objectToDecrypt):A=objectToDecrypt;B=sparta_59eb86677d();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)