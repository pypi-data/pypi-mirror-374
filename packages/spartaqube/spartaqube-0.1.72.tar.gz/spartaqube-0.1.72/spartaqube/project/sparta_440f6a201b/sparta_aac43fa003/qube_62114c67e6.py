import ast,io,sys,contextlib
def sparta_4625672ce8(code):
	B=ast.parse(code);A=set()
	class C(ast.NodeVisitor):
		def visit_Name(B,node):A.add(node.id);B.generic_visit(node)
	D=C();D.visit(B);return list(A)
def sparta_217e4e4594(script_text):return sparta_4625672ce8(script_text)
def sparta_b0a619cf67(code):
	try:
		A=ast.parse(code)
		if A.body and isinstance(A.body[-1],ast.Expr):return ast.get_source_segment(code,A.body[-1])
	except Exception:return
def sparta_443043d676(tiny_kernel,code_str):
	L=code_str;K='result';J='stderr';I='stdout';D=tiny_kernel;B=None
	try:
		E=ast.parse(L);M=E.body[-1]if E.body else B
		if isinstance(M,ast.Expr):N=E.body[:-1];F=ast.unparse(ast.Module(body=N,type_ignores=[]))if N else'';G=ast.unparse(M.value)
		else:F=L;G=B
	except Exception as A:return{I:'',J:f"AST parsing failed: {A}",K:B}
	H=io.StringIO();C=io.StringIO()
	with contextlib.redirect_stdout(H),contextlib.redirect_stderr(C):
		try:
			if F.strip():D(F)
		except Exception as A:return{I:H.getvalue(),J:C.getvalue()+f"\nException during code execution: {A}",K:B}
		O=B
		if G:
			try:O=D(G);D('_')
			except Exception as A:C.write(f"\nException during final expression evaluation: {A}")
	return{I:H.getvalue(),J:C.getvalue(),K:O}