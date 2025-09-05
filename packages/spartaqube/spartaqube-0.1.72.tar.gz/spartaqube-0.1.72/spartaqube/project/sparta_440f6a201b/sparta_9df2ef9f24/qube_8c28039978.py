_C='coerce'
_B=True
_A=False
import io,math,base64
from datetime import datetime
from io import BytesIO
import pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt,seaborn as sns
def sparta_44bf6b657a(obj):
	A=obj
	if isinstance(A,dict):return{A:sparta_44bf6b657a(B)for(A,B)in A.items()}
	elif isinstance(A,list):return[sparta_44bf6b657a(A)for A in A]
	elif isinstance(A,float):
		if math.isnan(A)or math.isinf(A):return
	return A
def sparta_c8aadd56bf(series):
	try:A=pd.to_numeric(series,errors=_C);return pd.api.types.is_numeric_dtype(A)and not A.isna().all()
	except Exception:return _A
def sparta_f5fd7d344c(series):
	A=series
	if pd.api.types.is_categorical_dtype(A):return _B
	if pd.api.types.is_object_dtype(A):B=A.nunique(dropna=_A)/max(1,len(A));return B<.1 or A.nunique(dropna=_A)<=20
	return _A
def sparta_d58ed93f34(series):
	A=series
	if pd.api.types.is_datetime64_any_dtype(A):return _B
	try:B=pd.to_datetime(A,errors=_C);return B.notna().mean()>.9
	except Exception:return _A
def sparta_0433db98e0(fig):A=BytesIO();fig.savefig(A,format='png',bbox_inches='tight',transparent=_B);A.seek(0);return base64.b64encode(A.read()).decode('utf-8')
def sparta_1824ab1ae8(fig,B_DARK_THEME=_A):
	T='Arial';S='#dddddd';R='black';Q='#333333';P='#dcdcdc';O='#757575';F=B_DARK_THEME;C='white';B=fig;U=1.1;G=O;H=C;I='#343434';J=P;K=O;E=Q;L=R;V=R
	if F:I=S;E=C;K='#c1c1c1';J=S;G=Q;H=C;L=C;V=C
	for M in B.findobj(match=lambda x:hasattr(x,'set_fontsize')):W=M.get_fontsize();M.set_fontsize(W*U)
	for A in B.axes:
		A.set_facecolor(C);A.grid(_B,color=I,linewidth=.25,linestyle=':');A.tick_params(colors=J)
		if A.title:A.set_title(A.get_title(),fontsize=16,color=E,fontname=T)
		if A.xaxis.label:A.xaxis.label.set_color(E)
		if A.yaxis.label:A.yaxis.label.set_color(E)
		for X in A.get_xticklabels()+A.get_yticklabels():X.set_color(K)
		for Y in A.get_lines():Y.set_linewidth(1.5)
		for Z in A.spines.values():Z.set_visible(_A)
		D=A.get_legend()
		if D:
			D.get_frame().set_facecolor(H)
			if F:D.get_frame().set_edgecolor('none')
			else:D.get_frame().set_edgecolor(P);D.get_frame().set_linewidth(1.)
			for N in D.get_texts():N.set_fontname(T);N.set_color(G)
	if hasattr(B,'_suptitle')and B._suptitle is not None:B._suptitle.set_color(L)
	B.patch.set_facecolor(C);B.set_size_inches(10,6);return B
def sparta_fed6a98499(data_df):A=data_df;A.index=A.index.astype(str);return A