_K='output'
_J='yAxisDataArr'
_I='xAxisDataArr'
_H='Strategy'
_G='res'
_F='png'
_E='Benchmark'
_D='utf-8'
_C=True
_B=None
_A=False
import json,io,os,base64,pandas as pd,quantstats as qs,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
def sparta_f3e776cd15(df):
	A=df
	if pd.api.types.is_datetime64_any_dtype(A.index):
		if A.index.tz is not _B:A.index=A.index.tz_localize(_B)
	return A
def sparta_986e956e10(series):
	A=series
	if(A>=0).all():
		if A.max()>1.:return _A
	return _C
def sparta_b78f771df6(fig):A=io.BytesIO();fig.savefig(A,format=_F);A.seek(0);B=base64.b64encode(A.getvalue()).decode(_D);A.close();return B
def sparta_f4d4ee520b(fig):A=BytesIO();fig.savefig(A,format=_F);B=base64.b64encode(A.getvalue()).decode(_D);return B
import quantstats._plotting.core as qscore,matplotlib.pyplot as _plt
from matplotlib.ticker import FuncFormatter as _FuncFormatter
import pandas as _pd,numpy as _np
def sparta_45cd743f85(x):return(x+1).cumprod()
class _Stats:compsum=staticmethod(_compsum)
try:from quantstats import stats as _stats
except ImportError:_stats=_Stats()
def sparta_e5e3cb77df(grayscale):
	D=['#FEDD78','#348DC1','#BA516B','#4FA487','#9B59B6','#613F66','#84B082','#DC136C','#559CAD','#4A5899'];E=['#000000','#222222','#555555','#888888','#AAAAAA','#CCCCCC','#EEEEEE','#333333','#666666','#999999'];A=D;B='-';C=.8
	if grayscale:A=E;B='-';C=.5
	return A,B,C
def sparta_738329ab75(x,_):return f"{x*100:.0f}%"
def safe_plot_timeseries(returns,benchmark=_B,title='Returns',compound=_A,cumulative=_C,fill=_A,returns_label=_H,hline=_B,hlw=_B,hlcolor='red',hllabel='',percent=_C,match_volatility=_A,log_scale=_A,resample=_B,lw=1.5,figsize=(10,6),ylabel='',grayscale=_A,fontname='Arial',subtitle=_C,savefig=_B,show=_C):
	V='gray';U="%e %b '%y";T='bold';S=fontname;R=ylabel;Q=match_volatility;P=hlcolor;O='white';L=resample;K=hline;J=compound;I='black';H=savefig;G=grayscale;B=benchmark;A=returns;D,W,M=sparta_e5e3cb77df(G);A=A.copy().fillna(0)
	if isinstance(B,_pd.Series):B=B.copy().fillna(0)
	if Q and B is _B:raise ValueError('match_volatility requires passing of benchmark.')
	if Q and B is not _B:X=B.std();A=A/A.std()*X
	if J:
		if cumulative:
			A=_stats.compsum(A)
			if isinstance(B,_pd.Series):B=_stats.compsum(B)
		else:
			A=A.cumsum()
			if isinstance(B,_pd.Series):B=B.cumsum()
	if L:
		A=A.resample(L);A=A.last()if J else A.sum()
		if isinstance(B,_pd.Series):B=B.resample(L);B=B.last()if J else B.sum()
	E,C=_plt.subplots(figsize=figsize)
	for Y in C.spines.values():Y.set_visible(_A)
	E.suptitle(title,y=.94,fontweight=T,fontname=S,fontsize=14,color=I)
	if subtitle and isinstance(A.index,_pd.DatetimeIndex)and len(A.index)>=2:C.set_title('%s - %s\n'%(A.index[0].strftime(U),A.index[-1].strftime(U)),fontsize=12,color=V)
	E.set_facecolor(O);C.set_facecolor(O)
	if isinstance(B,_pd.Series):C.plot(B,lw=lw,ls=W,label=B.name or _E,color=D[0])
	M=.25 if G else 1
	if isinstance(A,_pd.Series):C.plot(A,lw=lw,label=A.name or returns_label,color=D[1],alpha=M)
	elif isinstance(A,_pd.DataFrame):
		for(N,F)in enumerate(A.columns):C.plot(A[F],lw=lw,label=F,alpha=M,color=D[N+1])
	if fill:
		if isinstance(A,_pd.Series):C.fill_between(A.index,0,A,color=D[1],alpha=.25)
		elif isinstance(A,_pd.DataFrame):
			for(N,F)in enumerate(A.columns):C.fill_between(A[F].index,0,A[F],color=D[N+1],alpha=.25)
	E.autofmt_xdate()
	if K is not _B and not isinstance(K,_pd.Series):
		if G:P=I
		C.axhline(K,ls='--',lw=hlw or 1,color=P,label=hllabel,zorder=2)
	C.axhline(0,ls='-',lw=1,color=V,zorder=1);C.axhline(0,ls='--',lw=1,color=O if G else I,zorder=2)
	try:C.legend(fontsize=11)
	except Exception:pass
	_plt.yscale('symlog'if log_scale else'linear')
	if percent:C.yaxis.set_major_formatter(_FuncFormatter(format_pct_axis))
	C.set_xlabel('')
	if R:C.set_ylabel(R,fontname=S,fontweight=T,fontsize=12,color=I)
	C.yaxis.set_label_coords(-.1,.5)
	if B is _B and len(_pd.DataFrame(A).columns)==1:
		try:C.get_legend().remove()
		except Exception:pass
	try:_plt.subplots_adjust(hspace=0,bottom=0,top=1)
	except Exception:pass
	try:E.tight_layout()
	except Exception:pass
	if H:
		if isinstance(H,dict):_plt.savefig(**H)
		else:_plt.savefig(H)
	if show:_plt.show(block=_A)
	_plt.close()
	if not show:return E
qscore.plot_timeseries=safe_plot_timeseries
def sparta_ce7f0fdddd(json_data,user_obj):
	f='basic';e='Portfolio';d='title';c='benchmark_title';b='strategyTitle';a='riskFreeRate';Z='reportType';U='split';P='date';N=json_data;A=json.loads(N['opts']);K=int(A[Z]);V=json.loads(N[_I])[0];C=json.loads(N[_J]);O=0
	if a in A:O=float(A[a])
	G=_E;E=_H
	if b in A:
		Q=A[b]
		if Q is not _B:
			if len(Q)>0:E=Q
	if c in A:
		R=A[c]
		if R is not _B:
			if len(R)>0:G=R
	W='Strategy Tearsheet'
	if d in A:
		X=A[d]
		if len(X)>0:W=X
	H=pd.DataFrame(C[0]);H[P]=pd.to_datetime(V);H.set_index(P,inplace=_C);H.columns=[e];H=sparta_f3e776cd15(H);B=H[e]
	if not sparta_986e956e10(B):B=B.pct_change().dropna()
	D=_B
	if len(C)==2:
		I=pd.DataFrame(C[1]);I[P]=pd.to_datetime(V);I.set_index(P,inplace=_C);I.columns=[_E];I=sparta_f3e776cd15(I);D=I[_E]
		if not sparta_986e956e10(D):D=D.pct_change().dropna()
	if'bHtmlReport'in list(N.keys()):
		g=os.path.dirname(os.path.abspath(__file__));S=os.path.join(g,'quantstats/quantstats-tearsheet.html')
		with open(S,mode='a')as h:h.close()
		qs.reports.html(B,benchmark=D,rf=O,mode='full',match_dates=_C,output=S,title=W,strategy_title=E,benchmark_title=G)
		with open(S,'rb')as i:j=i.read()
		return{_G:1,'file_content':j.decode(_D),'b_downloader':_C}
	if K==0:
		def L(data,benchmark=_B):
			C=benchmark;A=[];D=qs.plots.snapshot(data,show=_A,strategy_title=E,benchmark_title=G);A.append(sparta_f4d4ee520b(D));B=qs.plots.monthly_heatmap(data,show=_A,ylabel=_A,returns_label=E);A.append(sparta_f4d4ee520b(B))
			if C is not _B:B=qs.plots.monthly_heatmap(C,show=_A,ylabel=_A,returns_label=G);A.append(sparta_f4d4ee520b(B))
			return A
		if len(C)==1:F=L(B);J=F
		elif len(C)==2:F=L(B,D);J=F
	elif K==1:
		if len(C)==1:Y=qs.reports.metrics(B,rf=O,mode=f,display=_A,strategy_title=E,benchmark_title=G)
		elif len(C)==2:Y=qs.reports.metrics(B,benchmark=D,rf=O,mode=f,display=_A,strategy_title=E,benchmark_title=G)
		J=Y.to_json(orient=U)
	elif K==2:
		def L(data,benchmark=_B):
			D=benchmark;C=data;B=[]
			if A['returns']:F=qs.plots.returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(F))
			if A['logReturns']:G=qs.plots.log_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(G))
			if A['yearlyReturns']:H=qs.plots.yearly_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(H))
			if A['dailyReturns']:I=qs.plots.daily_returns(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(I))
			if A['histogram']:J=qs.plots.histogram(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(J))
			if A['rollingVol']:K=qs.plots.rolling_volatility(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(K))
			if A['rollingSharpe']:L=qs.plots.rolling_sharpe(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(L))
			if A['rollingSortino']:M=qs.plots.rolling_sortino(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(M))
			if A['rollingBeta']:
				if D is not _B:N=qs.plots.rolling_beta(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(N))
			if A['distribution']:O=qs.plots.distribution(C,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(O))
			if A['heatmap']:P=qs.plots.monthly_heatmap(C,benchmark=D,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(P))
			if A['drawdowns']:Q=qs.plots.drawdown(C,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(Q))
			if A['drawdownsPeriod']:R=qs.plots.drawdowns_periods(C,show=_A,ylabel=_A,title=E);B.append(sparta_f4d4ee520b(R))
			if A['returnQuantiles']:S=qs.plots.distribution(C,show=_A,ylabel=_A);B.append(sparta_f4d4ee520b(S))
			return B
		if len(C)==1:F=L(B);J=F
		elif len(C)==2:F=L(B,D);J=F
	elif K==3:k=[E];M=B;M.columns=k;l=qs.reports._calc_dd(M);m=qs.stats.drawdown_details(M).sort_values(by='max drawdown',ascending=_C)[:10];T=[];n=qs.plots.drawdown(M,show=_A,ylabel=_A);T.append(sparta_f4d4ee520b(n));o=qs.plots.drawdowns_periods(M,show=_A,ylabel=_A,title=E);T.append(sparta_f4d4ee520b(o));J=[l.to_json(orient=U),m.to_json(orient=U),T]
	return{_G:1,Z:K,_K:J}
def sparta_a692686563():import matplotlib,matplotlib.pyplot as A;from matplotlib.path import Path;from matplotlib.patches import PathPatch;from matplotlib.patches import Patch;import matplotlib.patches as B
def sparta_544faebbc0(json_data,user_obj):
	R='alpha';Q='sq_index';P='None';O='data_df';N='column_renamed';C=json_data;sparta_a692686563();S=json.loads(C['opts']);D=json.loads(C[_I])[0];E=json.loads(C[_J]);F=json.loads(C['chartParamsEditorDict']);print('MATPLOTIB DEBUGGER BACKJEND SERIVCE');print('x_data_arr');print(D);print(type(D));print('y_data_arr');print(E);print(type(E));print('common_props');print(S);print('chart_params_editor_dict');print(F);A=pd.DataFrame(E).T;A.index=D;H=[]
	try:H=[A[N]for A in F['yAxisArr']];A.columns=H
	except:pass
	I=[]
	try:I=[A[N]for A in F['xAxisArr']]
	except:pass
	print(O);print(A);print('user_input_x_columns');print(I);M='';J=F['typeChart'];print('LA type_chart >> '+str(J))
	if J==101:
		K=plt.figure(figsize=(12,6));B=K.add_subplot(1,1,1)
		for(T,U)in enumerate(list(A.columns)):V=E[T];B.scatter(D,V,label=U)
		B.spines['top'].set_color(P);B.spines['right'].set_color(P);B.set_xlabel('Area');B.set_ylabel('Population');B.set_xlim(-.01);B.legend(loc='upper left',fontsize=10);plt.grid()
	elif J==102:
		import seaborn as W;K,B=plt.subplots(figsize=(10,6));X=list(A.columns);A[Q]=A.index;print(O);print(A)
		for L in H:print(L);W.regplot(x=Q,y=L,data=A,label=L,scatter_kws={R:.7},line_kws={R:.7})
		plt.xlabel(I[0]);plt.ylabel('');plt.legend(title='Category');plt.grid()
	G=BytesIO();plt.savefig(G,format=_F,bbox_inches='tight')
	try:plt.close(K)
	except:pass
	G.seek(0);M=base64.b64encode(G.getvalue()).decode(_D);G.close();return{_G:1,_K:M}