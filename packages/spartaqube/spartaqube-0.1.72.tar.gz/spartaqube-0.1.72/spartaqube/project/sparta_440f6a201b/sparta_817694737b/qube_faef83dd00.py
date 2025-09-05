_V='Error Final'
_U='zipName'
_T='Except2'
_S='file > '
_R='rmdir /S /Q "{}"'
_Q='folderPath2MoveArr'
_P='filesPath2MoveArr'
_O='full_path'
_N='file_name'
_M='fileName'
_L='Invalid path'
_K='You do not have the rights to perform this action'
_J='fullPath'
_I='path'
_H='pathResource'
_G=True
_F=False
_E='projectPath'
_D='errorMsg'
_C='res'
_B='ext'
_A='mode'
import os,json,base64,shutil,zipfile,io,uuid
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
from pathlib import Path
import pytz
UTC=pytz.utc
from project.models_spartaqube import Dashboard,DashboardShared,Developer,DeveloperShared,Notebook,NotebookShared
from project.models import ShareRights
from project.sparta_440f6a201b.sparta_5c1010991f import qube_2808664dfd as qube_2808664dfd
from project.sparta_440f6a201b.sparta_89c6bd5348 import qube_5a0182b6f5 as qube_5a0182b6f5
from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import sparta_a253265c85,sparta_0f6223a0af
from project.sparta_440f6a201b.sparta_817694737b import qube_62229504ef as qube_62229504ef
from project.logger_config import logger
def sparta_8bc53bda0e(user_obj):
	A=qube_2808664dfd.sparta_0a996f3465(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_377e85568b(project_path):
	A=project_path
	if not os.path.exists(A):os.makedirs(A)
	D='main_qube';B=f"{D}.ipynb";C=os.path.join(A,B);E=1
	while os.path.exists(C):B=f"{D}_{E}.ipynb";C=os.path.join(A,B);E+=1
	F="import pandas as pd\n# There is two-way binding between the notebook and your dashboard components.\n# Components linked to the notebook's variables can update their values\n# Any changes made to the variables in the notebook will be immediately reflected on the dashboard, ensuring reactivity \n\n";G=qube_62229504ef.sparta_fa7ea4f2b7(F)
	with open(C,'w',encoding='utf-8')as H:json.dump(G,H,indent=4)
	logger.debug(f"Notebook '{B}' created successfully.");return{_N:B,'file_path':A,_O:C}
def sparta_397eb9c8bd(json_data,user_obj):
	B=user_obj;A=json_data[_E];A=sparta_a253265c85(A);F=Dashboard.objects.filter(project_path=A).all()
	if F.count()>0:
		C=F[0];G=sparta_8bc53bda0e(B)
		if len(G)>0:D=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=G,dashboard__is_delete=0,dashboard=C)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=C))
		else:D=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=C)
		H=_F
		if D.count()>0:
			K=D[0];I=K.share_rights
			if I.is_admin or I.has_write_rights:H=_G
		if not H:return{_C:-1,_D:'Chose another path. A dashboard already exists at this location'}
	if not isinstance(A,str):return{_C:-1,_D:'Project path must be a string.'}
	try:A=os.path.abspath(A)
	except Exception as E:return{_C:-1,_D:f"Invalid project path: {str(E)}"}
	try:
		if not os.path.exists(A):os.makedirs(A)
		J=sparta_377e85568b(A);L=J[_N];M=J[_O];return{_C:1,'main_ipynb_filename':L,'main_ipynb_fullpath':M}
	except Exception as E:return{_C:-1,_D:f"Failed to create folder: {str(E)}"}
def sparta_02744345a6(json_data,user_obj):
	F='___sq___files___';E='___sq___folders___';B=json_data['path_to_explore'];A=dict();A={E:[],F:[],'___sq___path___':B,'___sq___show___':0}
	if os.path.exists(B):
		for C in os.listdir(B):
			D=os.path.join(B,C)
			if os.path.isdir(D):
				if not os.listdir(D):A[E].append(C)
				else:A[E].append(C)
			elif os.path.isfile(D):A[F].append(C)
	G={_C:1,'folderStructure':A};return G
def sparta_f14133ac05(user_obj,json_data):
	F='notebook_id';E='developer_id';D='dashboard_id';B=user_obj;A=json_data;logger.debug('check_perform_project_explorer_action json_data');logger.debug(A);logger.debug(A.keys());C=A[_E]
	if D in A:return check_perform_project_explorer_action_dashboard(B,A[D],C)
	if E in A:return check_perform_project_explorer_action_developer(B,A[E],C)
	if F in A:return check_perform_project_explorer_action_notebook(B,A[F],C)
	return{_C:1}
def check_perform_project_explorer_action_dashboard(user_obj,dashboard_id,project_path):
	C=dashboard_id;B=user_obj
	if len(C)>0:
		D=Dashboard.objects.filter(dashboard_id__startswith=C,is_delete=_F).all()
		if D.count()==1:
			A=D[D.count()-1];C=A.dashboard_id;F=sparta_8bc53bda0e(B)
			if len(F)>0:E=DashboardShared.objects.filter(Q(is_delete=0,user_group__in=F,dashboard__is_delete=0,dashboard=A)|Q(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A))
			else:E=DashboardShared.objects.filter(is_delete=0,user=B,dashboard__is_delete=0,dashboard=A)
			G=_F
			if E.count()>0:
				I=E[0];H=I.share_rights
				if H.is_admin or H.has_write_rights:G=_G
			if G:return{_C:1}
			else:return{_C:-1,_D:_K}
	return{_C:1}
def check_perform_project_explorer_action_developer(user_obj,developer_id,project_path):
	C=developer_id;B=user_obj
	if len(C)>0:
		D=Developer.objects.filter(developer_id__startswith=C,is_delete=_F).all()
		if D.count()==1:
			A=D[D.count()-1];C=A.developer_id;F=sparta_8bc53bda0e(B)
			if len(F)>0:E=DeveloperShared.objects.filter(Q(is_delete=0,user_group__in=F,developer__is_delete=0,developer=A)|Q(is_delete=0,user=B,developer__is_delete=0,developer=A))
			else:E=DeveloperShared.objects.filter(is_delete=0,user=B,developer__is_delete=0,developer=A)
			G=_F
			if E.count()>0:
				I=E[0];H=I.share_rights
				if H.is_admin or H.has_write_rights:G=_G
			if G:return{_C:1}
			else:return{_C:-1,_D:_K}
	return{_C:1}
def check_perform_project_explorer_action_notebook(user_obj,notebook_id,project_path):
	C=notebook_id;B=user_obj
	if len(C)>0:
		D=Notebook.objects.filter(notebook_id__startswith=C,is_delete=_F).all()
		if D.count()==1:
			A=D[D.count()-1];C=A.notebook_id;F=sparta_8bc53bda0e(B)
			if len(F)>0:E=NotebookShared.objects.filter(Q(is_delete=0,user_group__in=F,notebook__is_delete=0,notebook=A)|Q(is_delete=0,user=B,notebook__is_delete=0,notebook=A))
			else:E=NotebookShared.objects.filter(is_delete=0,user=B,notebook__is_delete=0,notebook=A)
			G=_F
			if E.count()>0:
				I=E[0];H=I.share_rights
				if H.is_admin or H.has_write_rights:G=_G
			if G:return{_C:1}
			else:return{_C:-1,_D:_K}
	return{_C:1}
def sparta_43132d82ac(main_path,test_path):B=test_path;A=main_path;A=Path(A).resolve();B=Path(B).resolve();return A in B.parents or A==B
def sparta_5a9e0aa03d(json_data,user_obj):
	A=json_data;logger.debug('Create resources');logger.debug(A);G=sparta_f14133ac05(user_obj,A)
	if G[_C]==-1:return G
	C=A[_E];C=sparta_a253265c85(C);F=A['createResourceName'];I=A['createType']
	try:
		B=os.path.join(C,F)
		if int(I)==1:
			D=A[_H];E=sparta_a253265c85(D)
			if len(D)>0:
				if not sparta_43132d82ac(C,E):return{_C:-1,_D:_L}
				B=os.path.join(E,F)
			if not os.path.exists(B):os.makedirs(B)
		else:
			D=A[_H];E=sparta_a253265c85(D)
			if len(D)>0:
				if not sparta_43132d82ac(C,E):return{_C:-1,_D:_L}
				B=os.path.join(E,F)
			if not os.path.exists(B):sparta_0f6223a0af(B)
			else:return{_C:-1,_D:'A file with this name already exists'}
	except Exception as H:logger.debug('Exception create new resource');logger.debug(H);return{_C:-1,_D:str(H)}
	return{_C:1}
def sparta_9b70057db9(json_data,user_obj):
	C=json_data;logger.debug('Rename resources');logger.debug(C);H=sparta_f14133ac05(user_obj,C)
	if H[_C]==-1:return H
	D=C[_H];I=C['editName'];E=C[_E];E=sparta_a253265c85(E);J=int(C['renameType'])
	if J==1:
		B=D;F=os.path.dirname(D);A=os.path.join(F,I);B=sparta_a253265c85(B);A=sparta_a253265c85(A)
		if E in A:
			try:os.rename(B,A)
			except Exception as G:return{_C:-1,_D:str(G)}
	else:
		B=D;F=os.path.dirname(D);A=os.path.join(F,I);B=sparta_a253265c85(B);A=sparta_a253265c85(A)
		if E in A:
			try:os.rename(B,A)
			except Exception as G:return{_C:-1,_D:str(G)}
	return{_C:1}
def sparta_9dc8136a5e(json_data,user_obj):
	A=json_data;logger.debug('*'*100);logger.debug('MOVE drag & drop resources');logger.debug(A);G=sparta_f14133ac05(user_obj,A)
	if G[_C]==-1:return G
	D=A[_E];D=sparta_a253265c85(D);B=A['folderLocation'];B=sparta_a253265c85(B);logger.debug('folder_location >>>>> ');logger.debug(B);J=A[_P];K=A[_Q]
	for H in J:
		L=H[_I];I=H[_M];E=os.path.join(L,I);C=os.path.join(B,I);E=sparta_a253265c85(E);C=sparta_a253265c85(C)
		if D in C:
			try:logger.debug(f"Move from\n{E}\nto\n{C}");shutil.move(E,C)
			except Exception as M:logger.debug('Exception move 1');logger.debug(M)
	for N in K:
		F=N[_I];F=sparta_a253265c85(F)
		if D in B:
			try:shutil.move(F,B)
			except:pass
	return{_C:1}
def sparta_2971db69bf(json_data,user_obj):
	A=json_data;logger.debug('Delete resource');logger.debug(A);E=sparta_f14133ac05(user_obj,A)
	if E[_C]==-1:return E
	C=A[_E];C=sparta_a253265c85(C);F=int(A['typeDelete']);G=A[_H];B=sparta_a253265c85(G)
	if not sparta_43132d82ac(C,B):return{_C:-1,_D:_L}
	if F==1:
		try:os.rmdir(B)
		except:
			try:os.system(_R.format(B))
			except:
				try:shutil.rmtree(B)
				except Exception as D:return{_C:-1,_D:str(D)}
	else:
		try:os.remove(B)
		except Exception as D:return{_C:-1,_D:str(D)}
	return{_C:1}
def sparta_ecd43978c8(json_data,user_obj):
	B=json_data;logger.debug('Delete multiple resources');logger.debug(B);G=sparta_f14133ac05(user_obj,B)
	if G[_C]==-1:return G
	I=B[_P];J=B[_Q];C=B[_E];C=sparta_a253265c85(C)
	for D in I:
		K=D[_M];H=D[_I];E=os.path.join(H,K);E=sparta_a253265c85(E)
		if C in H:
			try:logger.debug(f"File to delete: {E}");os.remove(E)
			except Exception as F:return{_C:-1,_D:str(F)}
	for D in J:
		A=D[_I];A=sparta_a253265c85(A)
		if C in A:
			logger.debug(f"Delete folder {A}")
			try:logger.debug(f"Folder to delete: {A}");os.system(_R.format(A))
			except:
				try:logger.debug(f"Folder to delete: {A}");shutil.rmtree(A)
				except Exception as F:return{_C:-1,_D:str(F)}
	return{_C:1}
def sparta_39c01026d6(json_data,user_obj):
	A=json_data;C=sparta_f14133ac05(user_obj,A)
	if C[_C]==-1:return C
	B=A[_E];E=A[_H];D=sparta_a253265c85(E);B=sparta_a253265c85(B)
	if B in D:return{_C:1,_J:D}
	return{_C:-1}
def sparta_13f86badf1(json_data,user_obj):
	A=json_data;logger.debug('DOWNLOAD FOLDER DEBUG');logger.debug(A);B=A[_E];E=A['folderName']
	def C(zf,folder):
		D=folder
		for E in os.listdir(D):
			logger.debug(_S+str(E));A=os.path.join(D,E)
			if os.path.isfile(A):zf.write(A,A.split(B)[1])
			elif os.path.isdir(A):
				try:C(zf,A)
				except Exception as F:logger.debug(_T);logger.debug(F)
		return zf
	try:
		D=io.BytesIO()
		with zipfile.ZipFile(D,mode='w',compression=zipfile.ZIP_DEFLATED)as F:C(F,B)
		return{_C:1,'zip':D,_U:E}
	except Exception as G:logger.debug(_V);logger.debug(G)
	return{_C:-1}
def sparta_27d69b5c57(json_data,user_obj):
	A=json_data;B=A[_E];C=sparta_f14133ac05(user_obj,A)
	if C[_C]==-1:return C
	F='app'
	def D(zf,folder):
		C=folder
		for E in os.listdir(C):
			logger.debug(_S+str(E));A=os.path.join(C,E)
			if os.path.isfile(A):zf.write(A,A.split(B)[1])
			elif os.path.isdir(A):
				try:D(zf,A)
				except Exception as F:logger.debug(_T);logger.debug(F)
		return zf
	try:
		E=io.BytesIO()
		with zipfile.ZipFile(E,mode='w',compression=zipfile.ZIP_DEFLATED)as G:D(G,B)
		return{_C:1,'zip':E,_U:F}
	except Exception as H:logger.debug(_V);logger.debug(H)
	return{_C:-1}
def sparta_9216c74746(json_data,user_obj,file_obj):
	F=file_obj;C=json_data;logger.debug('**********************************');logger.debug('upload_resource');logger.debug(C);E=C[_E];G=sparta_f14133ac05(user_obj,C)
	if G[_C]==-1:return G
	B=C[_H];E=sparta_a253265c85(E)
	if len(B)==0:B=E
	else:B=sparta_a253265c85(B)
	D=C[_I];logger.debug(f"path_folder >> {D}")
	if len(D)>0:
		A=os.path.join(B,D);A=sparta_a253265c85(A)
		if not os.path.exists(A):os.makedirs(A)
	else:
		A=os.path.join(B,D);A=sparta_a253265c85(A)
		if not os.path.exists(A):os.makedirs(A)
	H=os.path.join(A,F.name);logger.debug(f"file_path > {H}")
	with open(H,'wb')as I:I.write(F.read())
	J={_C:1};return J
def sparta_79e661945e(fileName):
	A=['pdf','png','jpg','jpeg'];B=fileName.split('.')[-1].lower()
	if B in A:return _G
	return _F
def sparta_e9b6f138cf(full_path):
	A=full_path;B=dict();C=A.split('.')[-1].lower()
	if C in['pdf','png','jpg','jpeg']:
		with open(A,'rb')as D:E=base64.b64encode(D.read()).decode();B['data']=E
	return B
def sparta_b4ffedad18(json_data,user_obj):
	A=json_data;E=A[_E];B=sparta_f14133ac05(user_obj,A)
	if B[_C]==-1:return B
	C=sparta_a253265c85(A[_J]);D=qube_62229504ef.sparta_76a219d088(C);return{_C:1,'ipynb_dict':json.dumps(D)}
def sparta_b19d171645(json_data,user_obj):
	R='cells';M='ipynb';K='file_extension';J='file_content';I='cm_mode';H='is_previewable';G='is_handled';D=json_data;S=D[_M];B=D[_J];B=sparta_a253265c85(B);N=D[_E];N=sparta_a253265c85(N);O=sparta_f14133ac05(user_obj,D)
	if O[_C]==-1:return O
	E=_F;P=_F;F='';A='';C=S.split('.')[-1].lower();T=sparta_b8bf74689b()
	for Q in T:
		try:
			if C in Q[_B]:E=_G;F=Q[_A]
		except:pass
	if E:
		try:
			with open(B)as L:A=json.dumps(L.read())
		except Exception as U:return{_C:1,G:P,H:_F,I:F,J:A,K:C,_D:str(U)}
	else:
		if sparta_79e661945e(B):C=B.split('.')[-1];V=sparta_e9b6f138cf(B);return{_C:1,G:_G,H:E,I:F,J:A,K:C,'resource':V}
		C=B.split('.')[-1]
		if C==M:
			logger.debug('JUPYTER NOTEBOOK')
			with open(B)as L:A=L.read()
			A=json.loads(A);W=A[R];X=[A['source']for A in W];return{_C:1,G:_G,H:_F,I:M,J:A,K:M,R:X}
	return{_C:1,G:P,H:E,I:F,J:A,K:C}
def sparta_2d10d36b1d(json_data,user_obj):
	A=json_data;E=A['sourceCode'];B=A[_J];B=sparta_a253265c85(B);C=A[_E];C=sparta_a253265c85(C);D=sparta_f14133ac05(user_obj,A)
	if D[_C]==-1:return D
	with open(B,'w')as F:F.write(E)
	return{_C:1}
def sparta_b8bf74689b():A5='msgenny';A4='xquery';A3='webidl';A2='textile';A1='verilog';A0='sparql';z='text';y='text/plain';x='pig';w='php';v='markdown';u='lua';t='jinja2';s='null';r='jsp';q='jade';p='pug';o='aspx';n='haxe';m='haml';l='groovy';k='forth';j='factor';i='elm';h='edn';g='ecl';f='dylan';e='dtd';d='dart';c='python';b='cypher';a='lisp';Z='coffee';Y='cmake';X='cpp';W='sig';V='apl';U='rst';T='properties';S='mbox';R='m';Q='jsx';P='jsonld';O='htmlmixed';N='mllike';M='diff';L='clojure';K='javascript';J='htmlembedded';I='mscgen';H='css';G='clike';F='sql';E='file';D='mimes';C='alias';B='mime';A='name';A6=[{A:'APL',B:'text/apl',_A:V,_B:['dyalog',V]},{A:'PGP',D:['application/pgp','application/pgp-encrypted','application/pgp-keys','application/pgp-signature'],_A:'asciiarmor',_B:['asc','pgp',W]},{A:'ASN.1',B:'text/x-ttcn-asn',_A:'asn.1',_B:['asn','asn1']},{A:'Asterisk',B:'text/x-asterisk',_A:'asterisk',E:'/^extensions\\.conf$/i'},{A:'Brainfuck',B:'text/x-brainfuck',_A:'brainfuck',_B:['b','bf']},{A:'C',B:'text/x-csrc',_A:G,_B:['c','h','ino']},{A:'C++',B:'text/x-c++src',_A:G,_B:[X,'c++','cc','cxx','hpp','h++','hh','hxx'],C:[X]},{A:'Cobol',B:'text/x-cobol',_A:'cobol',_B:['cob','cpy']},{A:'C#',B:'text/x-csharp',_A:G,_B:['cs'],C:['csharp']},{A:'Clojure',B:'text/x-clojure',_A:L,_B:['clj','cljc','cljx']},{A:'ClojureScript',B:'text/x-clojurescript',_A:L,_B:['cljs']},{A:'Closure Stylesheets (GSS)',B:'text/x-gss',_A:H,_B:['gss']},{A:'CMake',B:'text/x-cmake',_A:Y,_B:[Y,'cmake.in'],E:'/^CMakeLists.txt$/'},{A:'CoffeeScript',D:['application/vnd.coffeescript','text/coffeescript','text/x-coffeescript'],_A:'coffeescript',_B:[Z],C:[Z,'coffee-script']},{A:'Common Lisp',B:'text/x-common-lisp',_A:'commonlisp',_B:['cl',a,'el'],C:[a]},{A:'Cypher',B:'application/x-cypher-query',_A:b,_B:['cyp',b]},{A:'Cython',B:'text/x-cython',_A:c,_B:['pyx','pxd','pxi']},{A:'Crystal',B:'text/x-crystal',_A:'crystal',_B:['cr']},{A:'CSS',B:'text/css',_A:H,_B:[H]},{A:'CQL',B:'text/x-cassandra',_A:F,_B:['cql']},{A:'D',B:'text/x-d',_A:'d',_B:['d']},{A:'Dart',D:['application/dart','text/x-dart'],_A:d,_B:[d]},{A:M,B:'text/x-diff',_A:M,_B:[M,'patch']},{A:'Django',B:'text/x-django',_A:'django'},{A:'Dockerfile',B:'text/x-dockerfile',_A:'dockerfile',E:'/^Dockerfile$/'},{A:'DTD',B:'application/xml-dtd',_A:e,_B:[e]},{A:'Dylan',B:'text/x-dylan',_A:f,_B:[f,'dyl','intr']},{A:'EBNF',B:'text/x-ebnf',_A:'ebnf'},{A:'ECL',B:'text/x-ecl',_A:g,_B:[g]},{A:h,B:'application/edn',_A:L,_B:[h]},{A:'Eiffel',B:'text/x-eiffel',_A:'eiffel',_B:['e']},{A:'Elm',B:'text/x-elm',_A:i,_B:[i]},{A:'Embedded Javascript',B:'application/x-ejs',_A:J,_B:['ejs']},{A:'Embedded Ruby',B:'application/x-erb',_A:J,_B:['erb']},{A:'Erlang',B:'text/x-erlang',_A:'erlang',_B:['erl']},{A:'Esper',B:'text/x-esper',_A:F},{A:'Factor',B:'text/x-factor',_A:j,_B:[j]},{A:'FCL',B:'text/x-fcl',_A:'fcl'},{A:'Forth',B:'text/x-forth',_A:k,_B:[k,'fth','4th']},{A:'Fortran',B:'text/x-fortran',_A:'fortran',_B:['f','for','f77','f90']},{A:'F#',B:'text/x-fsharp',_A:N,_B:['fs'],C:['fsharp']},{A:'Gas',B:'text/x-gas',_A:'gas',_B:['s']},{A:'Gherkin',B:'text/x-feature',_A:'gherkin',_B:['feature']},{A:'GitHub Flavored Markdown',B:'text/x-gfm',_A:'gfm',E:'/^(readme|contributing|history).md$/i'},{A:'Go',B:'text/x-go',_A:'go',_B:['go']},{A:'Groovy',B:'text/x-groovy',_A:l,_B:[l,'gradle'],E:'/^Jenkinsfile$/'},{A:'HAML',B:'text/x-haml',_A:m,_B:[m]},{A:'Haskell',B:'text/x-haskell',_A:'haskell',_B:['hs']},{A:'Haskell (Literate)',B:'text/x-literate-haskell',_A:'haskell-literate',_B:['lhs']},{A:'Haxe',B:'text/x-haxe',_A:n,_B:['hx']},{A:'HXML',B:'text/x-hxml',_A:n,_B:['hxml']},{A:'ASP.NET',B:'application/x-aspx',_A:J,_B:[o],C:['asp',o]},{A:'HTML',B:'text/html',_A:O,_B:['html','htm','handlebars','hbs'],C:['xhtml']},{A:'HTTP',B:'message/http',_A:'http'},{A:'IDL',B:'text/x-idl',_A:'idl',_B:['pro']},{A:'Pug',B:'text/x-pug',_A:p,_B:[q,p],C:[q]},{A:'Java',B:'text/x-java',_A:G,_B:['java']},{A:'Java Server Pages',B:'application/x-jsp',_A:J,_B:[r],C:[r]},{A:'JavaScript',D:['text/javascript','text/ecmascript','application/javascript','application/x-javascript','application/ecmascript'],_A:K,_B:['js'],C:['ecmascript','js','node']},{A:'JSON',D:['application/json','application/x-json'],_A:K,_B:['json','map'],C:['json5']},{A:'JSON-LD',B:'application/ld+json',_A:K,_B:[P],C:[P]},{A:'JSX',B:'text/jsx',_A:Q,_B:[Q]},{A:'Jinja2',B:s,_A:t,_B:['j2','jinja',t]},{A:'Julia',B:'text/x-julia',_A:'julia',_B:['jl']},{A:'Kotlin',B:'text/x-kotlin',_A:G,_B:['kt']},{A:'LESS',B:'text/x-less',_A:H,_B:['less']},{A:'LiveScript',B:'text/x-livescript',_A:'livescript',_B:['ls'],C:['ls']},{A:'Lua',B:'text/x-lua',_A:u,_B:[u]},{A:'Markdown',B:'text/x-markdown',_A:v,_B:[v,'md','mkd']},{A:'mIRC',B:'text/mirc',_A:'mirc'},{A:'MariaDB SQL',B:'text/x-mariadb',_A:F},{A:'Mathematica',B:'text/x-mathematica',_A:'mathematica',_B:[R,'nb']},{A:'Modelica',B:'text/x-modelica',_A:'modelica',_B:['mo']},{A:'MUMPS',B:'text/x-mumps',_A:'mumps',_B:['mps']},{A:'MS SQL',B:'text/x-mssql',_A:F},{A:S,B:'application/mbox',_A:S,_B:[S]},{A:'MySQL',B:'text/x-mysql',_A:F},{A:'Nginx',B:'text/x-nginx-conf',_A:'nginx',E:'/nginx.*\\.conf$/i'},{A:'NSIS',B:'text/x-nsis',_A:'nsis',_B:['nsh','nsi']},{A:'NTriples',D:['application/n-triples','application/n-quads','text/n-triples'],_A:'ntriples',_B:['nt','nq']},{A:'Objective-C',B:'text/x-objectivec',_A:G,_B:[R,'mm'],C:['objective-c','objc']},{A:'OCaml',B:'text/x-ocaml',_A:N,_B:['ml','mli','mll','mly']},{A:'Octave',B:'text/x-octave',_A:'octave',_B:[R]},{A:'Oz',B:'text/x-oz',_A:'oz',_B:['oz']},{A:'Pascal',B:'text/x-pascal',_A:'pascal',_B:['p','pas']},{A:'PEG.js',B:s,_A:'pegjs',_B:[P]},{A:'Perl',B:'text/x-perl',_A:'perl',_B:['pl','pm']},{A:'PHP',D:['text/x-php','application/x-httpd-php','application/x-httpd-php-open'],_A:w,_B:[w,'php3','php4','php5','php7','phtml']},{A:'Pig',B:'text/x-pig',_A:x,_B:[x]},{A:'Plain Text',B:y,_A:O,_B:['txt',z,'conf','def','list','log']},{A:'PLSQL',B:'text/x-plsql',_A:F,_B:['pls']},{A:'PowerShell',B:'application/x-powershell',_A:'powershell',_B:['ps1','psd1','psm1']},{A:'Properties files',B:'text/x-properties',_A:T,_B:[T,'ini','in'],C:['ini',T]},{A:'ProtoBuf',B:'text/x-protobuf',_A:'protobuf',_B:['proto']},{A:'Python',B:'text/x-python',_A:c,_B:['BUILD','bzl','py','pyw'],E:'/^(BUCK|BUILD)$/'},{A:'Puppet',B:'text/x-puppet',_A:'puppet',_B:['pp']},{A:'Q',B:'text/x-q',_A:'q',_B:['q']},{A:'R',B:'text/x-rsrc',_A:'r',_B:['r','R'],C:['rscript']},{A:'reStructuredText',B:'text/x-rst',_A:U,_B:[U],C:[U]},{A:'RPM Changes',B:'text/x-rpm-changes',_A:'rpm'},{A:'RPM Spec',B:'text/x-rpm-spec',_A:'rpm',_B:['spec']},{A:'Ruby',B:'text/x-ruby',_A:'ruby',_B:['rb'],C:['jruby','macruby','rake','rb','rbx']},{A:'Rust',B:'text/x-rustsrc',_A:'rust',_B:['rs']},{A:'SAS',B:'text/x-sas',_A:'sas',_B:['sas']},{A:'Sass',B:'text/x-sass',_A:'sass',_B:['sass']},{A:'Scala',B:'text/x-scala',_A:G,_B:['scala']},{A:'Scheme',B:'text/x-scheme',_A:'scheme',_B:['scm','ss']},{A:'SCSS',B:'text/x-scss',_A:H,_B:['scss']},{A:'Shell',D:['text/x-sh','application/x-sh'],_A:'shell',_B:['sh','ksh','bash','bat'],C:['bash','sh','zsh','bat'],E:'/^PKGBUILD$/'},{A:'Sieve',B:'application/sieve',_A:'sieve',_B:['siv','sieve']},{A:'Slim',D:['text/x-slim','application/x-slim'],_A:'slim',_B:['slim']},{A:'Smalltalk',B:'text/x-stsrc',_A:'smalltalk',_B:['st']},{A:'Smarty',B:'text/x-smarty',_A:'smarty',_B:['tpl']},{A:'Solr',B:'text/x-solr',_A:'solr'},{A:'SML',B:'text/x-sml',_A:N,_B:['sml',W,'fun','smackspec']},{A:'Soy',B:'text/x-soy',_A:'soy',_B:['soy'],C:['closure template']},{A:'SPARQL',B:'application/sparql-query',_A:A0,_B:['rq',A0],C:['sparul']},{A:'Spreadsheet',B:'text/x-spreadsheet',_A:'spreadsheet',C:['excel','formula']},{A:'SQL',B:'text/x-sql',_A:F,_B:[F]},{A:'SQLite',B:'text/x-sqlite',_A:F},{A:'Squirrel',B:'text/x-squirrel',_A:G,_B:['nut']},{A:'Stylus',B:'text/x-styl',_A:'stylus',_B:['styl']},{A:'Swift',B:'text/x-swift',_A:'swift',_B:['swift']},{A:'sTeX',B:'text/x-stex',_A:'stex'},{A:'LaTeX',B:'text/x-latex',_A:'stex',_B:[z,'ltx','tex'],C:['tex']},{A:'SystemVerilog',B:'text/x-systemverilog',_A:A1,_B:['v','sv','svh']},{A:'Tcl',B:'text/x-tcl',_A:'tcl',_B:['tcl']},{A:'Textile',B:'text/x-textile',_A:A2,_B:[A2]},{A:'TiddlyWiki ',B:'text/x-tiddlywiki',_A:'tiddlywiki'},{A:'Tiki wiki',B:'text/tiki',_A:'tiki'},{A:'TOML',B:'text/x-toml',_A:'toml',_B:['toml']},{A:'Tornado',B:'text/x-tornado',_A:'tornado'},{A:'troff',B:'text/troff',_A:'troff',_B:['1','2','3','4','5','6','7','8','9']},{A:'TTCN',B:'text/x-ttcn',_A:'ttcn',_B:['ttcn','ttcn3','ttcnpp']},{A:'TTCN_CFG',B:'text/x-ttcn-cfg',_A:'ttcn-cfg',_B:['cfg']},{A:'Turtle',B:'text/turtle',_A:'turtle',_B:['ttl']},{A:'TypeScript',B:'application/typescript',_A:K,_B:['ts'],C:['ts']},{A:'TypeScript-JSX',B:'text/typescript-jsx',_A:Q,_B:['tsx'],C:['tsx']},{A:'Twig',B:'text/x-twig',_A:'twig'},{A:'Web IDL',B:'text/x-webidl',_A:A3,_B:[A3]},{A:'VB.NET',B:'text/x-vb',_A:'vb',_B:['vb']},{A:'VBScript',B:'text/vbscript',_A:'vbscript',_B:['vbs']},{A:'Velocity',B:'text/velocity',_A:'velocity',_B:['vtl']},{A:'Verilog',B:'text/x-verilog',_A:A1,_B:['v']},{A:'VHDL',B:'text/x-vhdl',_A:'vhdl',_B:['vhd','vhdl']},{A:'Vue.js Component',D:['script/x-vue','text/x-vue'],_A:'vue',_B:['vue']},{A:'XML',D:['application/xml','text/xml'],_A:'xml',_B:['xml','xsl','xsd','svg'],C:['rss','wsdl','xsd']},{A:'XQuery',B:'application/xquery',_A:A4,_B:['xy',A4]},{A:'Yacas',B:'text/x-yacas',_A:'yacas',_B:['ys']},{A:'YAML',D:['text/x-yaml','text/yaml'],_A:'yaml',_B:['yaml','yml'],C:['yml']},{A:'Z80',B:'text/x-z80',_A:'z80',_B:['z80']},{A:I,B:'text/x-mscgen',_A:I,_B:[I,'mscin','msc']},{A:'xu',B:'text/x-xu',_A:I,_B:['xu']},{A:A5,B:'text/x-msgenny',_A:I,_B:[A5]},{A:'.gitignore',B:y,_A:O,E:'/^\\.gitignore$/',_B:['gitignore']}];return A6
def sparta_8e9c973125(json_data,user_obj):
	A=json_data;B=A[_J];B=sparta_a253265c85(B);C=A[_E];C=sparta_a253265c85(C);E=A['dashboardId'];D=sparta_f14133ac05(user_obj,A)
	if D[_C]==-1:return D
	logger.debug('*='*100);logger.debug('ide_save_ipynb_resource json_data');logger.debug(A);logger.debug(A.keys());B=sparta_a253265c85(B);F=A['notebookCellsArr'];G=qube_62229504ef.save_ipnyb_from_notebook_cells(F,B,E);return G