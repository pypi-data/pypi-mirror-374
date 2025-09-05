_AR='plot_residuals_base64'
_AQ='model_summary'
_AP='residuals'
_AO='Residuals Histogram'
_AN='prophet_dict'
_AM='holidays_prior_scale'
_AL='multiplicative'
_AK='n_changepoints'
_AJ='interval_width'
_AI='height_ratios'
_AH='Changepoint'
_AG='params_dict'
_AF='Original Series'
_AE='Weak evidence against the null hypothesis. The series is likely **non-stationary**.'
_AD='Strong evidence against the null hypothesis. The series is likely **stationary**.'
_AC='yearly_seasonality'
_AB='weekly_seasonality'
_AA='daily_seasonality'
_A9='additive'
_A8='seasonality_mode'
_A7='changepoint_prior_scale'
_A6='Signal'
_A5='changepoint_dates'
_A4='threshold'
_A3='seasonal'
_A2='Number of Observations Used'
_A1='maxlag'
_A0='yhat'
_z='logistic'
_y='linear'
_x='floor'
_w='cap'
_v='outlier_dates'
_u='Outliers'
_t='errorMsg'
_s='window'
_r='Observed'
_q='results'
_p='p-val'
_o='stat'
_n='critical_dict'
_m='out'
_l='res_text'
_k='is_stationary'
_j='#Lags Used'
_i='modelReg'
_h='differencing'
_g='bDiffTransformation'
_f='bLogTransformation'
_e='plot_forecast_base64'
_d='forecast_json'
_c='forecast_steps'
_b='yhat_upper'
_a='yhat_lower'
_Z='trend'
_Y='p-value'
_X='ct'
_W='Forecast'
_V='y'
_U='ds'
_T='IsOutlier'
_S='orange'
_R='blue'
_Q='red'
_P='-1'
_O='data_json'
_N='plot_base64'
_M='--'
_L='Date'
_K='Value'
_J='auto'
_I='coerce'
_H='black'
_G=True
_F='split'
_E='#343434'
_D='res'
_C=False
_B='white'
_A=None
import io,math,base64
from datetime import datetime
from io import BytesIO
import pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt,seaborn as sns,statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller,kpss
from project.sparta_440f6a201b.sparta_9df2ef9f24.qube_8c28039978 import sparta_1824ab1ae8,sparta_0433db98e0,sparta_fed6a98499
def sparta_4734dcf418(df,params_dict=_A):
	D=params_dict;B=df
	if D is _A:D=dict()
	P=D.get(_f,_C)
	if P:
		for A in B.columns:B[A]=B[A].apply(lambda x:math.log(x))
	Q=D.get(_g,_C)
	if Q:
		H=D.get(_h,0)
		if H>0:
			for A in B.columns:B[A]=B[A]-B[A].shift(H)
	C=int(D.get(_i,0))
	if C==0:C='c'
	elif C==1:C=_X
	elif C==2:C='ctt'
	elif C==3:C='n'
	F=D.get(_A1,_A)
	if F is not _A:
		if str(F)==_P:F=_A
	if F is _A:
		E=int(D.get('autolag',0))
		if E==0:E='AIC'
		elif E==1:E='BIC'
		elif E==2:E='t-stat'
	I=dict()
	for A in B.columns:
		T=A;R=B[A];G=adfuller(R.dropna(),maxlag=F,regression=C,autolag=E,store=_C,regresults=_G);S=['ADF Test Statistic',_Y,_j,_A2];J=pd.Series(G[0:4],index=S);K=dict()
		for(L,M)in G[2].items():J[f"Critical Value ({L})"]=M;K[L]=M
		N=0
		if G[1]<=.05:N=1;O=_AD
		else:O=_AE
		I[A]={_k:N,_l:O,_m:J.to_frame().to_json(orient=_F),_n:K,_o:float(G[0]),_p:float(G[1])}
	return{_D:1,_q:I}
def sparta_d4b6694972(df,params_dict=_A):
	C=params_dict;B=df
	if C is _A:C=dict()
	O=C.get(_f,_C)
	if O:
		for A in B.columns:B[A]=B[A].apply(lambda x:math.log(x))
	P=C.get(_g,_C)
	if P:
		G=C.get(_h,0)
		if G>0:
			for A in B.columns:B[A]=B[A]-B[A].shift(G)
	E=int(C.get(_i,0))
	if E==0:E='c'
	elif E==1:E=_X
	F=C.get('nlags',_J)
	if F!=_J:
		if str(F)==_P:F=_J
	H=dict()
	for A in B.columns:
		S=A;Q=B[A];D=kpss(Q.dropna(),nlags=F,regression=E);R=['KPSS Test Statistic',_Y,_j,_A2];I=pd.Series(D[0:4],index=R);J=dict()
		for(K,L)in D[3].items():I[f"Critical Value ({K})"]=L;J[K]=L
		M=0
		if D[1]>.05:M=1;N='Weak evidence against the null hypothesis. The series is likely **stationary**.'
		else:N='Strong evidence against the null hypothesis. The series is likely **non-stationary**.'
		H[A]={_k:M,_l:N,_m:I.to_frame().to_json(orient=_F),_n:J,_o:float(D[0]),_p:float(D[1]),'lags':D[2]}
	return{_D:1,_q:H}
def sparta_db645b5576(df,params_dict=_A):
	Q='PP Test Statistic';D=params_dict;C=df;import arch;from arch.unitroot import PhillipsPerron as R
	if D is _A:D=dict()
	S=D.get(_f,_C)
	if S:
		for A in C.columns:C[A]=C[A].apply(lambda x:math.log(x))
	T=D.get(_g,_C)
	if T:
		H=D.get(_h,0)
		if H>0:
			for A in C.columns:C[A]=C[A]-C[A].shift(H)
	E=int(D.get(_i,0))
	if E==0:E='c'
	elif E==1:E=_X
	elif E==1:E='n'
	G=int(D.get('testType',0))
	if G==0:G='tau'
	elif G==1:G='rho'
	F=D.get('nlags',_A)
	if F is not _A:
		if str(F)==_P:F=_A
		else:F=int(F)
	print('test_type >>> '+str(G));print('model_reg >>> '+str(E));print('nlags >>> '+str(F));I=dict()
	for A in C.columns:
		U=A;J=C[A];J=pd.to_numeric(C[A],errors=_I).dropna().astype(float);B=R(J,lags=F,trend=E,test_type=G);print('result');print(B);V=[Q,_Y,_j,_A2];K=pd.Series({Q:B.stat,_Y:B.pvalue,_j:B.lags,'Trend':B.trend,'Test Type':B.test_type});L=dict()
		for(M,N)in B.critical_values.items():K[f"Critical Value ({M})"]=N;L[M]=N
		O=0
		if B.pvalue<=.05:O=1;P=_AD
		else:P=_AE
		I[A]={_k:O,_l:P,_m:K.to_frame().to_json(orient=_F),_n:L,_o:float(B.stat),_p:float(B.pvalue),'lags':B.lags}
	print('Perron test executed!');return{_D:1,_q:I}
def plot_zivot_andrews_break(series,breakpoint_index,title='Zivot-Andrews Structural Break',B_DARK_THEME=_C):F=series;B=breakpoint_index;C=pd.to_datetime(F.index);E=F.values.astype(float);D,A=plt.subplots(figsize=(8,5));A.plot(C,E,color=_H,label='Time Series');H=C[B];A.axvline(H,color=_Q,linestyle=_M,label='Detected Breakpoint');A.fill_between(C[:B],E[:B],color=_R,alpha=.1,label='Regime 1');A.fill_between(C[B:],E[B:],color='green',alpha=.1,label='Regime 2');A.set_title(title);A.set_xlabel(_L);A.set_ylabel(_K);A.legend();G=BytesIO();plt.tight_layout();plt.savefig(G,format='png');plt.close(D);D.tight_layout();D=sparta_1824ab1ae8(D,B_DARK_THEME);I=base64.b64encode(G.getvalue()).decode('utf-8');return I
def sparta_5b69d18710(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	K=dates_series;C=params_dict;B=df;from statsmodels.tsa.stattools import zivot_andrews as T
	if C is _A:C=dict()
	U=C.get(_f,_C)
	if U:
		for A in B.columns:B[A]=B[A].apply(lambda x:math.log(x))
	V=C.get(_g,_C)
	if V:
		L=C.get(_h,0)
		if L>0:
			for A in B.columns:B[A]=B[A]-B[A].shift(L)
	E=int(C.get(_i,0))
	if E==0:E='c'
	elif E==1:E=_X
	elif E==1:E='n'
	G=int(C.get('testType',0))
	if G==0:G='tau'
	elif G==1:G='rho'
	F=C.get(_A1,_A)
	if F is not _A:
		if str(F)==_P:F=_A
		else:F=int(F)
	D='AIC'
	if F is _A:
		D=int(C.get('autolag',0))
		if D==0:D='AIC'
		elif D==1:D='BIC'
		elif D==2:D='t-stat'
	W=float(C.get('trim',.15));M=dict()
	for A in B.columns:
		b=A;N=B[A];N=pd.to_numeric(B[A],errors=_I).dropna().astype(float);H=T(N,regression=E,maxlag=F,autolag=D,trim=W);O=H[0];I=H[1];P=H[2];J=H[4];X=K.iloc[J];Q=int(I<.05);Y='Strong evidence against the null hypothesis. The series is likely **stationary with a structural break**.'if Q else'Weak evidence against the null hypothesis. The series is likely **non-stationary**, even accounting for a break.';R=pd.Series({'ZA Test Statistic':O,_Y:I,'Breakpoint (Index)':breakpoint})
		for(Z,a)in P.items():R[f"Critical Value ({Z})"]=a
		S=B[A];S.index=K.values;M[A]={_k:Q,_l:Y,_m:R.to_frame().to_json(orient=_F),_n:P,_o:float(O),_p:float(I),'breakpoint':int(J),'breakpoint_dt':str(X),'img64':plot_zivot_andrews_break(S,J,title=f"Zivot-Andrews Structural Break for {A}",B_DARK_THEME=B_DARK_THEME)}
	return{_D:1,_q:M}
def sparta_263a48339d(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	P='zscore';O='observed';K=B_DARK_THEME;H=dates_series;E=params_dict;D='resid';from statsmodels.tsa.seasonal import STL
	if E is _A:E={}
	L=dict()
	for M in df.columns:
		C=df[M]
		if H is _A:I=range(0,len(df))
		else:
			try:I=pd.to_datetime(H.values)
			except:I=H.values
		C.index=I;C=pd.to_numeric(C,errors=_I).dropna();Q=int(E.get('period',7));R=E.get('bRobust',_G);S=STL(C,period=Q,robust=R);F=S.fit();A=pd.DataFrame({O:F.observed,_Z:F.trend,_A3:F.seasonal,D:F.resid},index=C.index);T=A[D].mean();U=A[D].std();A[P]=(A[D]-T)/U;G=A[A[P].abs()>2.5];J,B=plt.subplots(4,1,figsize=(10,8),sharex=_G);N=_H
		if K:N=_B
		A[O].plot(ax=B[0],color=N,title=_r);A[_Z].plot(ax=B[1],color=_R,title='Trend');A[_A3].plot(ax=B[2],color='green',title='Seasonal');A[D].plot(ax=B[3],color=_Q,title='Residual')
		for V in B:V.grid(_G)
		B[-1].set_xlabel(_L);plt.tight_layout();J=sparta_1824ab1ae8(J,K);A=sparta_fed6a98499(A);G=sparta_fed6a98499(G);L[M]={_N:sparta_0433db98e0(J),_O:A.to_json(orient=_F),'outliers':G.to_json(orient=_F),'num_outliers':len(G)}
	return{_D:1,'stl_dict':L}
def sparta_e66c6d99f0(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	Z='approximation';S=B_DARK_THEME;I=params_dict;E=df;D=dates_series;import pywt as F
	if I is _A:I={}
	M=D
	if D is not _A:M=list(D.values)
	T=dict()
	for N in E.columns:
		A=E[N];J=range(0,len(E))
		if D is _A:J=range(0,len(E))
		else:
			try:J=pd.to_datetime(D.values)
			except:J=D.values
		A.index=J;A=pd.to_numeric(A,errors=_I).dropna();G=I.get('wavelet','db4');H=int(I.get('level',2));U=F.wavedec(A,G,level=H);V=U[0];W=U[1:];O=F.upcoef('a',V,G,level=H,take=len(A));X={Z:pd.Series(O,index=A.index)}
		for(B,P)in enumerate(W[::-1],start=1):Q=F.upcoef('d',P,G,level=B,take=len(A));X[f"detail_level_{B}"]=pd.Series(Q,index=A.index)
		c=pd.Series(O,index=A.index);R,C=plt.subplots(H+2,1,figsize=(12,8),sharex=_G);Y=_H
		if S:Y=_B
		C[0].plot(A.index,A,color=Y,label='Original');C[0].set_title(_AF);C[0].legend();C[1].plot(A.index,O,color=_R,label='Approximation (Trend)');C[1].set_title('Approximation Component');C[1].legend()
		for B in range(H):a=X[f"detail_level_{B+1}"];C[B+2].plot(A.index,a,label=f"Detail Level {B+1}");C[B+2].set_title(f"Detail Component Level {B+1}");C[B+2].legend()
		for b in C:b.grid(_G)
		plt.tight_layout();R=sparta_1824ab1ae8(R,S);K={};K['original']=E[N];K[Z]=pd.Series(F.upcoef('a',V,G,level=H,take=len(A)),index=A.index)
		for(B,P)in enumerate(W[::-1],start=1):Q=F.upcoef('d',P,G,level=B,take=len(A));K[f"detail_level_{B}"]=pd.Series(Q,index=A.index)
		L=pd.DataFrame(K)
		if M is not _A:L.index=M
		L=sparta_fed6a98499(L);T[N]={_N:sparta_0433db98e0(R),_O:L.to_json(orient=_F)}
	return{_D:1,'wavelet_dict':T}
def sparta_dbb470d4cf(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	J=B_DARK_THEME;E=params_dict;D=dates_series;from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression as S
	if E is _A:E={}
	T=D
	if D is not _A:T=list(D.values)
	U=int(E.get('k_regimes',2));print(_AG);A=E.get(_Z,0);print(_Z);print(A)
	if A is _A:A=0
	else:A=int(A)
	if A==0:A='c'
	elif A==1:A='t'
	elif A==2:A=_X
	else:A='nc'
	V=bool(E.get('switching_variance',_C));K=dict()
	for L in df.columns:
		B=df[L];H=range(0,len(df))
		if D is _A:H=range(0,len(df))
		else:
			try:H=pd.to_datetime(D.values)
			except:H=D.values
		B.index=H;B=pd.to_numeric(B,errors=_I).dropna();W=S(B,k_regimes=U,trend=A,switching_variance=V);M=W.fit(disp=_C);F=M.smoothed_marginal_probabilities;N=F.idxmax(axis=1);G=pd.DataFrame({'Original':B,'PredictedState':N},index=B.index);G=pd.concat([G,F],axis=1);I,C=plt.subplots(3,1,figsize=(12,8),sharex=_G)
		if J:O=_B
		else:O=_B
		C[0].plot(B.index,B.values,color=O,label='Return');C[0].set_title(_AF);C[0].legend()
		for P in sorted(F.columns):Q=N==P;C[1].plot(B.index[Q],B[Q],linestyle='None',marker='o',label=f"Regime {P}",alpha=.6)
		C[1].set_title('Series by Regime');C[1].legend()
		for R in F.columns:C[2].plot(B.index,F[R],label=f"Regime {R} Prob")
		C[2].set_title('Smoothed Regime Probabilities');C[2].legend();plt.tight_layout();I=sparta_1824ab1ae8(I,J);G=sparta_fed6a98499(G);K[L]={'summary':M.summary().as_html(),_N:sparta_0433db98e0(I),_O:G.to_json(orient=_F)}
	return{_D:1,'hmm_dict':K}
def sparta_597c7a97bf(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	f='#121212';e='pelt';V='dynp';U='bottomup';O=dates_series;N='binseg';H=params_dict;import ruptures as I
	if H is _A:H={}
	W=H.get('model','l2');C=H.get('algo',N);E=H.get('pen',10)
	if E is not _A:
		if str(E)==_P:E=_A
		else:E=int(E)
	F=H.get('n_bkps',4)
	if F is not _A:
		if str(F)==_P:F=_A
	if C in[N,U,V]:
		if F is not _A:E=_A
	else:F=_A
	X=dict()
	for Y in df.columns:
		A=df[Y];K=range(0,len(df))
		if O is _A:K=range(0,len(df))
		else:
			try:K=pd.to_datetime(O.values)
			except:K=O.values
		A.index=K;A=pd.to_numeric(A,errors=_I).dropna();Z={e:I.Pelt,N:I.Binseg,_s:I.Window,V:I.Dynp,U:I.BottomUp}
		if C not in Z:return{_D:-1,_t:f"Unsupported algo '{C}'"}
		J=Z[C](model=W).fit(A.values)
		try:
			if C==e:G=J.predict(pen=float(E))
			elif C==N:G=J.predict(n_bkps=int(F))
			elif C==_s:G=J.predict(pen=float(E))
			elif C==V:G=J.predict(n_bkps=int(F))
			elif C==U:G=J.predict(n_bkps=int(F))
		except Exception as g:return{_D:-1,_t:str(g)}
		P=[]
		for L in G:
			if L==0 or L>len(A):continue
			h=L-1 if L<len(A)else-1;P.append(A.index[h])
		Q=pd.Series(index=A.index,dtype=int);R=0
		for(a,D)in enumerate(G):
			if D>=len(A):break
			Q.iloc[R:D]=a;R=D
		Q.iloc[R:]=a+1;S=pd.DataFrame({_K:A,'Segment':Q});b,B=plt.subplots(figsize=(12,6));c=_H
		if B_DARK_THEME:b.patch.set_facecolor(f);B.set_facecolor(f);B.tick_params(colors=_B);B.title.set_color(_B);B.yaxis.label.set_color(_B);B.xaxis.label.set_color(_B);B.set_facecolor(_E);c=_B
		B.plot(A.index,A.values,label='Series',color=c);M=0;d=['#1f77b4','#ff7f0e']
		for(T,D)in enumerate(G):
			if D>=len(A):break
			i=A.index[D-1];B.axvspan(A.index[M],i,alpha=.1,color=d[T%2]);M=D
		if M<len(A):B.axvspan(A.index[M],A.index[-1],alpha=.1,color=d[len(G)%2])
		for(T,D)in enumerate(P):B.axvline(D,color=_Q,linestyle=_M,label='Breakpoint'if T==0 else'')
		B.set_title(f"Ruptures Detection ({C.upper()} + {W.upper()})");B.legend();plt.tight_layout();S=sparta_fed6a98499(S);X[Y]={_N:sparta_0433db98e0(b),'breakpoints':[str(A)for A in P],_O:S.to_json(orient=_F)}
	return{_D:1,'ruptures_dict':X}
def sparta_056f487687(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	d='down';U='both';O=B_DARK_THEME;J=dates_series;F=.0;D=params_dict
	if D is _A:D={}
	V=float(D.get(_A4,1.5));W=float(D.get('limit',5));C=int(D.get('direction','2'));X=int(D.get(_s,20));print(_AG);print(D);print('dates_series');print(J);print('threshold_scale_vol > '+str(V));print('limit_scale_threshold > '+str(W))
	if C==0:C='up'
	elif C==1:C=d
	else:C=U
	print('direction >> '+str(C));Y=dict()
	for Z in df.columns:
		A=df[Z];K=range(0,len(df))
		if J is _A:K=range(0,len(df))
		else:
			try:K=pd.to_datetime(J.values)
			except:K=J.values
		A.index=K;A=pd.to_numeric(A,errors=_I).dropna();a=A.rolling(window=X,min_periods=1).mean();P=[];Q=[];E=[];G=F;H=F;e=(A-a).rolling(X).std().dropna();L=V*e.mean();M=W*L;print('threshold COMPUTED');print(L);print('limit COMPUTED');print(M)
		for(R,f)in enumerate(A):
			b=f-a.iloc[R];G=max(F,G+b-L);H=max(F,H-b-L);P.append(G);Q.append(H)
			if C in(U,'up')and G>M:E.append(A.index[R]);G=F
			if C in(U,d)and H>M:E.append(A.index[R]);H=F
		S=pd.DataFrame({_K:A,'CUSUM_Pos':P,'CUSUM_Neg':Q,'IsChangepoint':[A in E for A in A.index]});N,B=plt.subplots(figsize=(12,4));c=_H
		if O:N.patch.set_facecolor(_E);B.set_facecolor(_E);B.tick_params(colors=_B);B.title.set_color(_B);B.xaxis.label.set_color(_B);B.yaxis.label.set_color(_B);c=_B
		print('changepoints');print(len(E));B.plot(A.index,A.values,label='Series',color=c)
		for(g,h)in enumerate(E):B.axvline(h,color=_Q,linestyle=_M,label=_AH if g==0 else'')
		B.set_title('CUSUM Detection');B.legend();plt.tight_layout();N=sparta_1824ab1ae8(N,O);T,I=plt.subplots(figsize=(12,4));I.plot(A.index,P,label='CUSUM +',color=_R);I.plot(A.index,Q,label='CUSUM -',color=_S);I.axhline(M,color='gray',linestyle=_M,label='CUSUM Limit');I.set_title('Cumulative Sums (CUSUM)');I.legend();T=sparta_1824ab1ae8(T,O);S=sparta_fed6a98499(S);Y[Z]={_D:1,_N:sparta_0433db98e0(N),'plot2_base64':sparta_0433db98e0(T),_A5:[str(A)for A in E],_O:S.to_json(orient=_F)}
	return{_D:1,'cusum_dict':Y}
def sparta_8d534897e7(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	M=B_DARK_THEME;J=params_dict;I=dates_series
	if J is _A:J={}
	E=float(J.get(_A4,2.));N=dict()
	for O in df.columns:
		A=df[O];F=range(0,len(df))
		if I is _A:F=range(0,len(df))
		else:
			try:F=pd.to_datetime(I.values)
			except:F=I.values
		A.index=F;A=pd.to_numeric(A,errors=_I).dropna();Q=A.mean();R=A.std();K=(A-Q)/R;G=K.abs()>E;S=A.index[G].tolist();L=pd.DataFrame({_K:A,'Z_score':K,_T:G});H,(C,B)=plt.subplots(2,1,figsize=(14,6),sharex=_G,gridspec_kw={_AI:[2,1]})
		if M:
			for D in[C,B]:D.set_facecolor(_E);D.tick_params(colors=_B);D.title.set_color(_B);D.xaxis.label.set_color(_B);D.yaxis.label.set_color(_B)
			H.patch.set_facecolor(_E);P=_B
		else:P=_H
		C.plot(A.index,A.values,label=_A6,color=P);C.scatter(A.index[G],A[G],color=_Q,label=_u,zorder=3);C.set_title(f"Signal with Z-score Outliers (Threshold = {E})");C.legend();B.plot(A.index,K,label='Z-score',color=_R);B.axhline(E,linestyle=_M,color='gray',label='Threshold');B.axhline(-E,linestyle=_M,color='gray');B.set_title('Z-score Diagnostic Plot');B.legend();plt.tight_layout();H=sparta_1824ab1ae8(H,M);L=sparta_fed6a98499(L);N[O]={_D:1,_N:sparta_0433db98e0(H),_v:[str(A)for A in S],_O:L.to_json(orient=_F)}
	return{_D:1,'zscore_dict':N}
def sparta_2b48b8254d(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	M=B_DARK_THEME;I=dates_series;D=params_dict;from sklearn.ensemble import IsolationForest as S
	if D is _A:D={}
	N=dict()
	for O in df.columns:
		A=df[O];E=range(0,len(df))
		if I is _A:E=range(0,len(df))
		else:
			try:E=pd.to_datetime(I.values)
			except:E=I.values
		A.index=E;A=pd.to_numeric(A,errors=_I).dropna();P=float(D.get('contamination',.05));T=D.get('max_samples',_J);J=A.values.reshape(-1,1);K=S(contamination=P,max_samples=T,random_state=42);K.fit(J);U=K.predict(J);Q=K.decision_function(J);F=U==-1;V=A.index[F].tolist();L=pd.DataFrame({_K:A,'AnomalyScore':Q,_T:F});G,(B,H)=plt.subplots(2,1,figsize=(14,6),sharex=_G,gridspec_kw={_AI:[2,1]})
		if M:
			for C in[B,H]:C.set_facecolor(_E);C.tick_params(colors=_B);C.title.set_color(_B);C.xaxis.label.set_color(_B);C.yaxis.label.set_color(_B)
			G.patch.set_facecolor(_E);R=_B
		else:R=_H
		B.plot(A.index,A.values,label=_A6,color=R);B.scatter(A.index[F],A[F],color=_Q,label=_u,zorder=3);B.set_title(f"Isolation Forest Anomaly Detection (contamination={P})");B.legend();H.plot(A.index,Q,label='Anomaly Score',color=_R);H.set_title('Isolation Forest Score');H.legend();plt.tight_layout();G=sparta_1824ab1ae8(G,M);L=sparta_fed6a98499(L);N[O]={_D:1,_N:sparta_0433db98e0(G),_v:[str(A)for A in V],_O:L.to_json(orient=_F)}
	return{_D:1,'isolation_forest_dict':N}
def sparta_21748c5273(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	J=B_DARK_THEME;G=dates_series;C=params_dict
	if C is _A:C={}
	H=int(C.get(_s,15));K=float(C.get(_A4,3.));L=dict()
	for M in df.columns:
		A=df[M];D=range(0,len(df))
		if G is _A:D=range(0,len(df))
		else:
			try:D=pd.to_datetime(G.values)
			except:D=G.values
		A.index=D;A=pd.to_numeric(A,errors=_I).dropna();I=A.rolling(window=H,center=_G).median();P=lambda x:(x-x.median()).abs().median();N=A.rolling(window=H,center=_G).apply(P,raw=_C);Q=(A-I).abs();E=Q>K*N;R=A.index[E].tolist();S=pd.DataFrame({_K:A,'RollingMedian':I,'RollingMAD':N,_T:E});F,B=plt.subplots(figsize=(14,4))
		if J:F.patch.set_facecolor(_E);B.set_facecolor(_E);B.tick_params(colors=_B);B.title.set_color(_B);B.xaxis.label.set_color(_B);B.yaxis.label.set_color(_B);O=_B
		else:O=_H
		B.plot(A.index,A.values,label=_A6,color=O);B.plot(A.index,I,label='Rolling Median',color=_S);B.scatter(A.index[E],A[E],color=_Q,label=_u,zorder=3);B.set_title(f"Rolling MAD Outlier Detection (window={H}, threshold={K})");B.legend();plt.tight_layout();F=sparta_1824ab1ae8(F,J);L[M]={_D:1,_N:sparta_0433db98e0(F),_v:[str(A)for A in R],_O:S.to_json(orient=_F)}
	return{_D:1,'mad_median_dict':L}
def sparta_71e3d0075f(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	R=B_DARK_THEME;P=dates_series;B=params_dict;from prophet import Prophet as S
	if B is _A:B={}
	T=dict()
	for U in df.columns:
		D=df[U];M=range(0,len(df))
		if P is _A:M=range(0,len(df))
		else:
			try:M=pd.to_datetime(P.values)
			except:M=P.values
		D.index=M;D=pd.to_numeric(D,errors=_I).dropna()
		try:D.index=D.index.tz_localize(_A)
		except:pass
		N=pd.DataFrame({_U:D.index,_V:D.values});V=float(B.get(_AJ,.95));W=float(B.get(_A7,.2));J=int(B.get(_A8,0));X=int(B.get(_AK,25));H=int(B.get('growth',0));K=B.get(_w,_A);c=B.get(_x,0);Y=_C
		if H==0:H=_y
		else:H=_z
		if K is _A:H=_y
		elif str(K)!=_P:
			if H==_z:K=float(K);Y=_G
		if J==0:J=_A9
		else:J=_AL
		Z=float(B.get(_AM,1e1));E=int(B.get(_AA,0))
		if E==0:E=_J
		elif E==1:E=_G
		else:E=_C
		F=int(B.get(_AB,0))
		if F==0:F=_J
		elif F==1:F=_G
		else:F=_C
		G=int(B.get(_AC,0))
		if G==0:G=_J
		elif G==1:G=_G
		else:G=_C
		if Y:N[_w]=K;N[_x]=c;I=S(interval_width=V,changepoint_prior_scale=W,holidays_prior_scale=Z,seasonality_mode=J,daily_seasonality=E,weekly_seasonality=F,yearly_seasonality=G,n_changepoints=X,growth=H)
		else:I=S(interval_width=V,changepoint_prior_scale=W,holidays_prior_scale=Z,seasonality_mode=J,daily_seasonality=E,weekly_seasonality=F,yearly_seasonality=G,n_changepoints=X)
		I.fit(N);d=I.make_future_dataframe(periods=0);e=I.predict(d);A=N.set_index(_U).join(e.set_index(_U)[[_A0,_a,_b]]);A[_T]=(A[_V]<A[_a])|(A[_V]>A[_b]);f=[str(A.date())for A in I.changepoints];g=[str(A.date())for A in A[A[_T]].index];O,C=plt.subplots(figsize=(14,5))
		if R:O.patch.set_facecolor(_E);C.set_facecolor(_E);C.tick_params(colors=_B);C.title.set_color(_B);C.xaxis.label.set_color(_B);C.yaxis.label.set_color(_B);a=_B
		else:a=_H
		Q=A.index.to_numpy();h=A[_V].astype(float).to_numpy();i=A[_A0].astype(float).to_numpy();j=A[_a].astype(float).to_numpy();k=A[_b].astype(float).to_numpy();C.plot(Q,h,label='Actual',color=a);C.plot(Q,i,label=_W,color=_R);C.fill_between(Q,j,k,color=_R,alpha=.2,label='Confidence Interval')
		for(l,m)in enumerate(I.changepoints):C.axvline(m,color=_S,linestyle=_M,alpha=.6,label=_AH if l==0 else'')
		b=A[A[_T]];C.scatter(b.index,b[_V].astype(float),color=_Q,label=_u,zorder=3);C.set_title('Prophet Changepoint & Outlier Detection');C.legend();plt.tight_layout();O=sparta_1824ab1ae8(O,R);L=A.reset_index();L[_L]=L[_U];L[_K]=L[_V];T[U]={_D:1,_N:sparta_0433db98e0(O),_A5:f,_v:g,_O:L[[_L,_K,_A0,_a,_b,_T]].to_json(orient=_F)}
	return{_D:1,_AN:T}
def sparta_275cc59a5d(df,target,params_dict=_A,B_DARK_THEME=_C):
	H='error';C=params_dict;from statsmodels.tsa.stattools import grangercausalitytests as L
	if C is _A:C={}
	D='target';M=pd.DataFrame({D:target});E=int(C.get(_A1,5));B=dict()
	for A in df.columns:
		if A==D:continue
		try:I=pd.concat([M,df[[A]]],axis=1).dropna()
		except Exception as F:B[A]={H:f"Failed to merge data: {str(F)}"};continue
		if I.shape[0]<E+1:B[A]={H:f"Not enough observations for lag {E}."};continue
		try:N=L(I,maxlag=E,verbose=_C)
		except Exception as F:B[A]={H:f"Granger test failed: {str(F)}"};continue
		J=[]
		for(O,P)in N.items():
			Q,G=P[0]['ssr_ftest'][:2]
			if G<.05:K=1
			else:K=0
			R='Reject Null (X Granger-causes Y)'if G<.05 else'Fail to Reject Null';J.append({'Lag':int(O),'F-statistic':round(float(Q),4),_Y:round(float(G),4),'Conclusion':R,'res_test':K})
		B[A]={'x_column':A,'y_column':D,'summary':J}
	return{_D:1,'granger_dict':B}
def sparta_24b24d296c(df,target,params_dict=_A,B_DARK_THEME=_C):
	H='cointegration_dict';E=params_dict;D=target;from statsmodels.tsa.stattools import coint
	if E is _A:E={}
	C=D.name or'target';I=pd.DataFrame({C:D});B={}
	for A in df.columns:
		if A==C:continue
		try:F=pd.concat([I,df[[A]]],axis=1).dropna();J=F.iloc[:,0];K=F.iloc[:,1];L,G,M=coint(J,K);N=G<.05;B[A]={_D:1,'x_column':A,'y_column':C,'t_stat':round(float(L),4),'p_value':round(float(G),4),'critical_values':{str(A):round(float(B),4)for(A,B)in zip(['1%','5%','10%'],M)},'is_cointegrated':bool(N)};print(H);print(B)
		except Exception as O:B[A]={_t:str(O),_D:-1}
	return{_D:1,H:B}
def sparta_76d708a65e(df_X,df_Y,params_dict=_A,B_DARK_THEME=_C):
	U='Weight';G=params_dict;F=df_Y;E=df_X;C=B_DARK_THEME;from sklearn.cross_decomposition import CCA;from sklearn.preprocessing import StandardScaler as O
	if G is _A:G={}
	P=O().fit_transform(E);Q=O().fit_transform(F);R=int(G.get('n_components',min(P.shape[1],Q.shape[1])));A=CCA(n_components=R);S,T=A.fit_transform(P,Q);H=[float(round(pd.Series(S[:,A]).corr(pd.Series(T[:,A])),4))for A in range(R)];I,B=plt.subplots();B.bar(range(1,len(H)+1),H);B.set_title('Canonical Correlations');B.set_xlabel('Canonical Component');B.set_ylabel('Correlation');B.set_ylim(0,1);I=sparta_1824ab1ae8(I,C);J,D=plt.subplots();D.scatter(S[:,0],T[:,0],alpha=.7);D.set_title('Canonical Variables U1 vs V1');D.set_xlabel('U1 (from X)');D.set_ylabel('V1 (from Y)');J=sparta_1824ab1ae8(J,C);K,L=plt.subplots();L.bar(E.columns,A.x_weights_[:,0]);L.set_title('Canonical Weights for X (Component 1)');L.set_ylabel(U);K=sparta_1824ab1ae8(K,C);M,N=plt.subplots();N.bar(F.columns,A.y_weights_[:,0]);N.set_title('Canonical Weights for Y (Component 1)');N.set_ylabel(U);M=sparta_1824ab1ae8(M,C);return{_D:1,'canonical_correlations':H,'x_weights':A.x_weights_[:,0].tolist(),'y_weights':A.y_weights_[:,0].tolist(),'x_columns':E.columns.tolist(),'y_columns':F.columns.tolist(),'plot_correlation_bar':sparta_0433db98e0(I),'plot_uv_scatter':sparta_0433db98e0(J),'plot_x_weights':sparta_0433db98e0(K),'plot_y_weights':sparta_0433db98e0(M)}
def sparta_4e55148a12(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	K=B_DARK_THEME;J=dates_series;A=params_dict;import statsmodels.api as L,matplotlib.pyplot as R,pandas as F
	if A is _A:A={}
	Y=int(A.get('order_p',1));Z=int(A.get('order_d',1));a=int(A.get('order_q',1));b=int(A.get('seasonal_p',1));c=int(A.get('seasonal_d',1));d=int(A.get('seasonal_q',1));e=int(A.get('season_length',12));f=A.get('order',(Y,Z,a));g=A.get('seasonal_order',(b,c,d,e));S=int(A.get(_c,20));T=dict()
	for U in df.columns:
		C=df[U]
		if J is _A:M=range(0,len(df))
		else:
			try:M=F.to_datetime(J.values)
			except:M=J.values
		C.index=M;C=F.to_numeric(C,errors=_I).dropna();h=L.tsa.statespace.SARIMAX(C,order=f,seasonal_order=g,enforce_stationarity=_C,enforce_invertibility=_C);N=h.fit(disp=_C);V=N.get_forecast(steps=S);B=V.predicted_mean;O=V.conf_int();P,G=R.subplots(figsize=(10,4));C.plot(ax=G,label=_r)
		try:B.index=F.date_range(start=C.index[-1]+F.Timedelta(days=1),periods=S,freq='D')
		except:pass
		B.plot(ax=G,label=_W,color=_S);G.fill_between(B.index,O.iloc[:,0].astype(float).to_numpy(),O.iloc[:,1].astype(float).to_numpy(),color=_S,alpha=.3);G.set_title('SARIMA Forecast with Confidence Intervals');G.legend();P=sparta_1824ab1ae8(P,K);H=N.resid;Q,W=R.subplots(figsize=(6,3));W.hist(H.dropna(),bins=20,edgecolor=_H);W.set_title(_AO);Q=sparta_1824ab1ae8(Q,K);I=L.graphics.tsa.plot_acf(H.dropna(),lags=20);I.suptitle('Autocorrelation of Residuals');I=sparta_1824ab1ae8(I,K);D=O.copy();D['forecast']=B;D=sparta_fed6a98499(D);E=H.to_frame().copy();E.columns=[_AP];E=sparta_fed6a98499(E);X=L.tsa.acf(H.dropna(),nlags=20);i=F.DataFrame({'Lag':list(range(len(X))),'Autocorrelation':X});B=sparta_fed6a98499(B);D=sparta_fed6a98499(D);E=sparta_fed6a98499(E);T[U]={'acf_json':i.to_json(orient=_F),_d:B.to_json(orient=_F),'conf_int_json':D.to_json(orient=_F),'residuals_json':E.to_json(orient=_F),_AQ:N.summary().as_html(),_e:sparta_0433db98e0(P),_AR:sparta_0433db98e0(Q),'plot_acf_base64':sparta_0433db98e0(I)}
	return{_D:1,'sarima_dict':T}
def sparta_2459ee69cc(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	a='Residuals';Z='Fitted';Y='mul';X='add';O=dates_series;F=B_DARK_THEME;C=params_dict;from statsmodels.tsa.holtwinters import ExponentialSmoothing as b
	if C is _A:C={}
	G=int(C.get(_Z,0))
	if G==0:G=X
	elif G==1:G=Y
	else:G=_A
	H=int(C.get(_A3,0))
	if H==0:H=X
	elif H==1:H=Y
	else:H=_A
	c=int(C.get('seasonal_periods',7));d=bool(C.get('damped_trend',_C));T=int(C.get(_c,20));U=dict()
	for V in df.columns:
		D=df[V]
		if O is _A:P=range(0,len(df))
		else:
			try:P=pd.to_datetime(O.values)
			except:P=O.values
		D.index=P;D=pd.to_numeric(D,errors=_I).dropna();e=b(D,trend=G,seasonal=H,seasonal_periods=c,damped_trend=d);Q=e.fit();R=Q.forecast(T)
		try:f=pd.date_range(start=D.index[-1]+pd.Timedelta(days=1),periods=T,freq='D');R.index=f
		except:pass
		I,A=plt.subplots(figsize=(10,4));D.plot(ax=A,label=_r);R.plot(ax=A,label=_W,color=_S);A.set_title('ETS Forecast');A.legend()
		if F:I.patch.set_facecolor(_E);A.set_facecolor(_E);A.tick_params(colors=_B);A.title.set_color(_B);A.yaxis.label.set_color(_B);A.xaxis.label.set_color(_B)
		I=sparta_1824ab1ae8(I,F);W=Q.resid;J,E=plt.subplots(figsize=(6,3));E.hist(W.dropna(),bins=20,edgecolor=_H);E.set_title(_AO)
		if F:J.patch.set_facecolor(_E);E.set_facecolor(_E);E.tick_params(colors=_B);E.title.set_color(_B);E.yaxis.label.set_color(_B);E.xaxis.label.set_color(_B)
		J=sparta_1824ab1ae8(J,F);S=Q.fittedvalues;K,B=plt.subplots(figsize=(10,3));S.plot(ax=B,label=Z);(D-S).plot(ax=B,label=a,alpha=.5);B.set_title('Fitted Values and Residuals');B.legend()
		if F:K.patch.set_facecolor(_E);B.set_facecolor(_E);B.tick_params(colors=_B);B.title.set_color(_B);B.yaxis.label.set_color(_B);B.xaxis.label.set_color(_B)
		K=sparta_1824ab1ae8(K,F);L=R.to_frame().copy();L.columns=[_W];L=sparta_fed6a98499(L);M=W.to_frame().copy();M.columns=[a];M=sparta_fed6a98499(M);N=S.to_frame().copy();N.columns=[Z];N=sparta_fed6a98499(N);U[V]={'forecast':L.to_json(orient=_F),_AP:M.to_json(orient=_F),'fitted':N.to_json(orient=_F),_e:sparta_0433db98e0(I),_AR:sparta_0433db98e0(J),'plot_fitted_residuals_base64':sparta_0433db98e0(K)}
	return{_D:1,'ets_dict':U}
def sparta_fdc10abe0b(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	c='Prophet Forecast';P=dates_series;O=B_DARK_THEME;A=params_dict;from prophet import Prophet as U
	if A is _A:A={}
	d=A.get(_c,30);G=A.get(_A8,_A9);Q=float(A.get(_A7,.05));g=A.get(_AC,_J);h=A.get(_AB,_J);i=A.get(_AA,_J);V=float(A.get(_AJ,.95));Q=float(A.get(_A7,.2));G=int(A.get(_A8,0));W=int(A.get(_AK,25));H=int(A.get('growth',0));L=A.get(_w,_A);e=A.get(_x,0);X=_C
	if H==0:H=_y
	else:H=_z
	if L is _A:H=_y
	elif str(L)!=_P:
		if H==_z:L=float(L);X=_G
	if G==0:G=_A9
	else:G=_AL
	Y=float(A.get(_AM,1e1));B=int(A.get(_AA,0))
	if B==0:B=_J
	elif B==1:B=_G
	else:B=_C
	C=int(A.get(_AB,0))
	if C==0:C=_J
	elif C==1:C=_G
	else:C=_C
	D=int(A.get(_AC,0))
	if D==0:D=_J
	elif D==1:D=_G
	else:D=_C
	Z=dict()
	for a in df.columns:
		E=df[a]
		if P is _A:R=range(0,len(df))
		else:
			try:R=pd.to_datetime(P.values)
			except:R=P.values
		E.index=R;E=pd.to_numeric(E,errors=_I).dropna()
		try:E.index=E.index.tz_localize(_A)
		except:pass
		S=pd.DataFrame({_U:E.index,_V:E.values})
		if X:S[_w]=L;S[_x]=e;F=U(interval_width=V,changepoint_prior_scale=Q,holidays_prior_scale=Y,seasonality_mode=G,daily_seasonality=B,weekly_seasonality=C,yearly_seasonality=D,n_changepoints=W,growth=H)
		else:F=U(interval_width=V,changepoint_prior_scale=Q,holidays_prior_scale=Y,seasonality_mode=G,daily_seasonality=B,weekly_seasonality=C,yearly_seasonality=D,n_changepoints=W)
		F.fit(S);f=F.make_future_dataframe(periods=d);T=F.predict(f);I=F.plot(T);I.suptitle(c,fontsize=14)
		if O:
			I.patch.set_facecolor(_E);J=I.axes[0];J.set_facecolor(_E);J.tick_params(colors=_B);J.yaxis.label.set_color(_B);J.xaxis.label.set_color(_B);J.set_title(c,fontsize=14,color=_B);b=J.get_lines()
			if len(b)>0:b[0].set_color(_B)
		I=sparta_1824ab1ae8(I,O);M=F.plot_components(T)
		if O:
			for N in M.axes:N.set_facecolor(_E);N.tick_params(colors=_B);N.title.set_color(_B);N.yaxis.label.set_color(_B);N.xaxis.label.set_color(_B)
			M.patch.set_facecolor(_E)
		M=sparta_1824ab1ae8(M,O);K=T[[_U,_A0,_a,_b]].copy();K[_L]=K[_U].dt.strftime('%Y-%m-%d');K.set_index(_L,inplace=_G);K=sparta_fed6a98499(K);Z[a]={_D:1,_e:sparta_0433db98e0(I),'plot_components_base64':sparta_0433db98e0(M),_d:K.to_json(orient=_F),_A5:[str(A.date())for A in F.changepoints]}
	return{_D:1,_AN:Z}
def sparta_5c7e79c879(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	L=dates_series;E=B_DARK_THEME;D=params_dict;from sklearn.preprocessing import MinMaxScaler as Y;import tensorflow as C;from tensorflow.keras.models import Sequential as Z;from tensorflow.keras.layers import LSTM,Dense,Dropout as a
	if D is _A:D={}
	M=int(D.get('seq_len',20));b=int(D.get('epochs',30));N=int(D.get(_c,30));O={}
	for P in df.columns:
		G=df[P].dropna().reset_index(drop=_G)
		if L is not _A:H=pd.to_datetime(L.values)
		else:H=pd.date_range(start='2000-01-01',periods=len(G),freq='D')
		G.index=H;F=pd.DataFrame({_L:H,_K:G}).dropna();Q=Y();c=Q.fit_transform(F[[_K]]);d=[float(A[0])for A in c]
		def e(data_list,length):
			B=length;A=data_list;D,E=[],[]
			for C in range(len(A)-B):D.append([[A]for A in A[C:C+B]]);E.append([A[C+B]])
			return D,E
		I,f=e(d,M)
		if len(I)<10:return{_D:-1,_t:'Not enough data for LSTM sequence modeling.'}
		g=C.convert_to_tensor(I,dtype=C.float32);h=C.convert_to_tensor(f,dtype=C.float32);J=Z([LSTM(50,return_sequences=_C,input_shape=(M,1)),a(.2),Dense(1)]);J.compile(optimizer='adam',loss='mse');R=J.fit(g,h,epochs=b,batch_size=16,validation_split=.1,verbose=0);K=I[-1];S=[]
		for k in range(N):T=J.predict(C.convert_to_tensor([K],dtype=C.float32),verbose=0)[0][0];S.append(T);K=K[1:]+[[T]]
		i=pd.DataFrame(S,columns=['Forecast_Scaled']);U=[A[0]for A in Q.inverse_transform(i)];V=pd.date_range(F[_L].iloc[-1]+pd.Timedelta(days=1),periods=N);W,A=plt.subplots(figsize=(12,4));A.plot(F[_L],F[_K],label='Actual',color=_B if E else _H);A.plot(V,U,label=_W,color=_S);A.set_title('LSTM Forecast',color=_B if E else _H);A.legend()
		if E:W.patch.set_facecolor(_E);A.set_facecolor(_E);A.tick_params(colors=_B);A.yaxis.label.set_color(_B);A.xaxis.label.set_color(_B)
		X,B=plt.subplots(figsize=(6,3));B.plot(R.history['loss'],label='Train Loss');B.plot(R.history['val_loss'],label='Val Loss');B.set_title('Training Loss',color=_B if E else _H);B.legend()
		if E:X.patch.set_facecolor(_E);B.set_facecolor(_E);B.tick_params(colors=_B);B.yaxis.label.set_color(_B);B.xaxis.label.set_color(_B)
		j=pd.DataFrame({_L:V.strftime('%Y-%m-%d'),_W:U});O[P]={_D:1,_d:j.to_json(orient=_F),_e:sparta_0433db98e0(W),'plot_loss_base64':sparta_0433db98e0(X)}
	return{_D:1,'lstm_dict':O}
def sparta_4fe76207b6(df,dates_series,params_dict=_A,B_DARK_THEME=_C):
	P=dates_series;J=params_dict;C=B_DARK_THEME;A=df;from statsmodels.tsa.api import VAR;from statsmodels.tsa.stattools import acf
	if J is _A:J={}
	Y=int(J.get('maxlags',5));Z=int(J.get('irf_steps',10));T=int(J.get(_c,10));D=int(J.get(_Z,0))
	if D==0:D='c'
	elif D==1:D=_X
	elif D==2:D='ctt'
	elif D==3:D='n'
	if P is _A:Q=range(0,len(A))
	else:
		try:Q=pd.to_datetime(P.values)
		except:Q=P.values
	A.index=Q;A=A.astype(float);print('df');print(A);a=VAR(A);G=a.fit(maxlags=Y,ic='aic',trend=D);K=G.irf(Z);L=K.plot(orth=_C)
	if C:
		for I in L.axes:I.set_facecolor(_E);I.tick_params(colors=_B);I.title.set_color(_B)
	L=sparta_1824ab1ae8(L,C);M=G.plot_acorr()
	if C:
		for I in M.axes:I.set_facecolor(_E);I.tick_params(colors=_B);I.title.set_color(_B)
	M=sparta_1824ab1ae8(M,C);b=G.forecast(A.values[-G.k_ar:],steps=T);c=A.index[-1];R=pd.infer_freq(A.index)
	if R is _A:R='D'
	d=pd.date_range(start=c,periods=T+1,freq=R)[1:];H=pd.DataFrame(b,index=d,columns=A.columns);N,E=plt.subplots(figsize=(10,4))
	for B in A.columns:E.plot(A.index,A[B],label=f"{B} (Observed)");E.plot(H.index,H[B],linestyle=_M,label=f"{B} (Forecast)")
	E.set_title('VAR Forecast');E.legend();e=pd.DataFrame(K.irfs.reshape(K.irfs.shape[0],-1),index=range(K.irfs.shape[0]),columns=[f"{A}->{B}"for A in G.names for B in G.names])
	if C:N.patch.set_facecolor(_E);E.set_facecolor(_E);E.tick_params(colors=_B);E.title.set_color(_B);E.yaxis.label.set_color(_B);E.xaxis.label.set_color(_B)
	N=sparta_1824ab1ae8(N,C);U={}
	for B in A.columns:
		O,F=plt.subplots(figsize=(10,4));F.plot(A.index,A[B],label=_r,color=_B if C else _H);F.plot(H.index,H[B],linestyle=_M,label=_W,color=_S);F.set_title(f"VAR Forecast – {B}");F.legend()
		if C:O.patch.set_facecolor(_E);F.set_facecolor(_E);F.tick_params(colors=_B);F.title.set_color(_B);F.yaxis.label.set_color(_B);F.xaxis.label.set_color(_B)
		O=sparta_1824ab1ae8(O,C);S=H[[B]];S=sparta_fed6a98499(S);U[B]={'img64':sparta_0433db98e0(O),_d:S.to_json(orient=_F)}
	H=sparta_fed6a98499(H);V=[]
	for B in A.columns:f=G.resid[B].dropna();W,X=acf(f,nlags=20,alpha=.05);g=pd.DataFrame({'Variable':B,'Lag':list(range(len(W))),'ACF':W,'CI Lower':X[:,0],'CI Upper':X[:,1]});V.append(g)
	h=pd.concat(V,ignore_index=_G);return{_D:1,_AQ:f"<pre>{str(G.summary())}</pre>",'plot_irf_base64':sparta_0433db98e0(L),'plot_resid_acf_base64':sparta_0433db98e0(M),_e:sparta_0433db98e0(N),_d:H.to_json(orient=_F),'irf_json':e.to_json(orient=_F),'acf_json':h.to_json(orient=_F),'forecast_plots':U}