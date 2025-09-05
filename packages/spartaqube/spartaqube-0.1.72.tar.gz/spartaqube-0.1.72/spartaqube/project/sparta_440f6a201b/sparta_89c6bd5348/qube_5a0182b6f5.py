_G='Path not found...'
_F='msg'
_E='folders'
_D='files'
_C='typeexplorer'
_B='currentPath'
_A='res'
import os,getpass,json,glob
from os import listdir
from os.path import isfile,join
def sparta_b9fb0acf3a(json_data,userObj):
	B=json_data[_C]
	if int(B)==1:
		C=JupyterDirectory.objects.filter(user=userObj).all()
		if C.exists():E=C[0];A=E.directory
		else:A=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	else:F=getpass.getuser();A='C:\\Users\\'+str(F)+'\\Desktop'
	try:G,H=sparta_bef842c44f(A,B);D={_A:1,_D:H,_E:G,_B:A}
	except:D={_A:-1,_F:_G}
	return D
def sparta_7d20de9315(json_data,userObj):
	A=json_data
	try:D=A[_B];E=A[_C];B=os.path.dirname(D);F,G=sparta_bef842c44f(B,E);C={_A:1,_D:G,_E:F,_B:B}
	except:C={_A:-1,_F:_G}
	return C
def sparta_6061567b86(json_data,userObj):
	A=json_data
	try:B=A[_B];D=A[_C];E,F=sparta_bef842c44f(B,D);C={_A:1,_D:F,_E:E,_B:B}
	except:C={_A:-1,_F:_G}
	return C
def sparta_bef842c44f(currentPath,typeexplorer=None):
	C=typeexplorer;A=currentPath;B=[B for B in listdir(A)if isfile(join(A,B))]
	if C is not None:
		if int(C)==2:D=['xls','xlsx','xlsm'];B=[A for A in B if A.split('.')[-1]in D]
	E=[B for B in os.listdir(A)if os.path.isdir(os.path.join(A,B))];return E,B
def sparta_534d6b0022(currentPath):
	E='___sq___files___';D='___sq___show___';C='___sq___path___';B=currentPath
	def G(starting_path):
		F=starting_path;G={'':{}}
		for(B,H,K)in os.walk(F):
			A=G;I=B;B=B[len(F):]
			for J in B.split(os.sep):
				L=A;A=A[J]
				if len(A)>0:A[C]=I;A[D]=0
			if H:
				for M in H:A[M]={}
			else:L[J]={E:K,C:I,D:0}
		return G['']
	A=G(B)
	def F(tmp_dict,tmp_path):
		B=tmp_dict;A=tmp_path;B[E]=[B for B in listdir(A)if isfile(join(A,B))];B[C]=A
		for(G,D)in B.items():
			if isinstance(D,dict):F(D,os.path.join(A,G))
	if isinstance(A,dict):F(A,B);A[E]=[A for A in listdir(B)if isfile(join(B,A))];A[C]=B;A[D]=1
	else:A={E:A,C:B,D:1}
	return A