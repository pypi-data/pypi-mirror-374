_AY='figImportance64'
_AX='fig_resid64'
_AW='Feature Importance (Random Forest)'
_AV='grid_json'
_AU='fig_cv_curve'
_AT='best_depth'
_AS='RMSE vs max_depth'
_AR='Mean RMSE'
_AQ='CV RMSE vs max_depth'
_AP='Best max_depth'
_AO='neg_mean_squared_error'
_AN='full_sample_pred_json'
_AM='figPartialDeps'
_AL='figFeature64'
_AK='figTree64'
_AJ='tree_rules'
_AI='Prediction vs Actual (Test Set)'
_AH='Residual Plot (Test Set)'
_AG='Actual vs Predicted (Test Set)'
_AF='melted_json'
_AE='cluster_json'
_AD='cluster_summary'
_AC='boxplot64'
_AB='Principal Component 2'
_AA='Principal Component 1'
_A9='Principal Components'
_A8='regression_equation'
_A7='is_stationary'
_A6='adf_statistic'
_A5='Correlation Matrix Heatmap'
_A4='fig_full64'
_A3='predScatter64'
_A2='Predictions'
_A1='Actual Values'
_A0='tight'
_z='mean_test_score'
_y='param_max_depth'
_x='res64'
_w='pred64'
_v='without'
_u='with'
_t='skyblue'
_s='Value'
_r='Correlation'
_q='img64'
_p='coolwarm'
_o='utf-8'
_n='png'
_m='narrative'
_l='metrics'
_k='Predicted (Full Sample)'
_j='center'
_i='max_depth'
_h='pred_json'
_g='Residual'
_f='Residuals'
_e='right'
_d='none'
_c='gray'
_b='residuals_json'
_a='top'
_Z='R2'
_Y='orange'
_X='left'
_W='y'
_V='Predicted'
_U='MAE'
_T='x'
_S='bottom'
_R='RMSE'
_Q='Target'
_P='black'
_O='red'
_N='coerce'
_M='Importance'
_L='Cluster'
_K='res'
_J='Feature'
_I='Prediction'
_H='Index'
_G='Actual'
_F='--'
_E=None
_D='#757575'
_C='split'
_B=True
_A=False
import io,math,random,base64
from datetime import datetime
from io import BytesIO
import pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt,seaborn as sns,statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller,kpss
from project.sparta_440f6a201b.sparta_9df2ef9f24.qube_8c28039978 import sparta_1824ab1ae8
def sparta_44bf6b657a(obj):
	A=obj
	if isinstance(A,dict):return{A:sparta_44bf6b657a(B)for(A,B)in A.items()}
	elif isinstance(A,list):return[sparta_44bf6b657a(A)for A in A]
	elif isinstance(A,float):
		if math.isnan(A)or math.isinf(A):return
	return A
def sparta_c8aadd56bf(series):
	try:A=pd.to_numeric(series,errors=_N);return pd.api.types.is_numeric_dtype(A)and not A.isna().all()
	except Exception:return _A
def sparta_f5fd7d344c(series):
	A=series
	if pd.api.types.is_categorical_dtype(A):return _B
	if pd.api.types.is_object_dtype(A):B=A.nunique(dropna=_A)/max(1,len(A));return B<.1 or A.nunique(dropna=_A)<=20
	return _A
def sparta_d58ed93f34(series):
	A=series
	if pd.api.types.is_datetime64_any_dtype(A):return _B
	try:B=pd.to_datetime(A,errors=_N);return B.notna().mean()>.9
	except Exception:return _A
def sparta_0433db98e0(fig):A=BytesIO();fig.savefig(A,format=_n,bbox_inches=_A0,transparent=_B);A.seek(0);return base64.b64encode(A.read()).decode(_o)
def sparta_98cde7ff08(df,B_DARK_THEME=_A):
	C=df.select_dtypes(include='number')
	if C.shape[1]<2:return''
	E=C.corr();B,D=plt.subplots(figsize=(8,6));sns.heatmap(E,annot=_B,cmap=_p,center=0,linewidths=.5,linecolor=_c,ax=D);D.set_title(_A5);plt.tight_layout();B=sparta_1824ab1ae8(B,B_DARK_THEME);A=io.BytesIO();B.savefig(A,format=_n,bbox_inches=_A0,transparent=_B);A.seek(0);F=base64.b64encode(A.read()).decode(_o);A.close();plt.close();return F
def sparta_3c30bc6a5e(df,B_DARK_THEME=_A):
	C=df.select_dtypes(include='number')
	if C.shape[1]<2:return''
	B=sns.pairplot(C,diag_kind='hist');B.fig.suptitle('Pairplot: Distributions & Relationships',y=1.02);A=io.BytesIO();B.fig.savefig(A,format=_n,bbox_inches=_A0,transparent=_B);A.seek(0);D=base64.b64encode(A.read()).decode(_o);A.close();plt.close(B.fig);return D
def sparta_5f2014e95d(df,columns,B_DARK_THEME=_A):
	l='all';k='description';V=B_DARK_THEME;U='Summary';T='__sq_index__';P=columns;H='N/A';A=df;A[T]=A.index;P=[T]+P;J={};m=pd.DataFrame();n=dict();W=0;X=0;Y=0
	for D in P:
		if sparta_c8aadd56bf(A[D]):W+=1
		elif sparta_f5fd7d344c(A[D]):X+=1
		elif sparta_d58ed93f34(A[D]):Y+=1
	J[U]=dict();o={'num_rows':A.shape[0],'num_columns':A.shape[1],'num_numeric':W,'num_categorical':X,'num_datetime':Y};J[U]['shape_rel']=o;p={'total_cells':A.size,'non_null_cells':int(A.notnull().sum().sum()),'null_cells':int(A.isnull().sum().sum()),'null_percent':round(A.isnull().sum().sum()/A.size*100,2),'memory_usage_MB':round(A.memory_usage(deep=_B).sum()/1024**2,2),'density_percent':round(A.notnull().sum().sum()/A.size*100,2)};J[U]['dataset_summary']=p;print('df stats');print(A)
	for D in P:
		K=sparta_c8aadd56bf(A[D]);n[D]=K;L=_E
		if K:L=pd.to_numeric(A[D],errors=_N);m[D]=L
		E=A[D];B={};B['type']=E.dtype.name;B['missing']=int(E.isnull().sum());B['unique']=E.nunique();B[k]=E.describe(include=l).to_dict()
		try:C=L
		except Exception:C=pd.Series(dtype='float64')
		B[k]=sparta_44bf6b657a(E.describe(include=l).to_dict())
		if K:
			Z=C.quantile(.25);a=C.quantile(.75);q=a-Z
			try:b=float(sparta_44bf6b657a(C.min()))
			except:b=H
			try:c=float(sparta_44bf6b657a(Z))
			except:c=H
			try:M=float(sparta_44bf6b657a(C.median()))
			except:M=H
			try:d=float(sparta_44bf6b657a(a))
			except:d=H
			try:e=float(sparta_44bf6b657a(C.max()))
			except:e=H
			try:f=float(sparta_44bf6b657a(q))
			except:f=H
			try:N=float(sparta_44bf6b657a(C.mean()))
			except:N=H
			try:g=float(sparta_44bf6b657a(C.std()))
			except:g=H
			try:h=float(sparta_44bf6b657a(C.skew()))
			except:h=H
			try:i=float(sparta_44bf6b657a(C.kurt()))
			except:i=H
			B['numeric_summary']={'min':b,'Q1 (25%)':c,'median (50%)':M,'Q3 (75%)':d,'max':e,'IQR':f,'mean':N,'std':g,'skew':h,'kurtosis':i}
			try:r=sparta_f1f4774550(L.tolist());s=sparta_2f907b9f7f(L.tolist());B['adf']=r;B['kpss']=s
			except:pass
		if E.nunique(dropna=_A)<=20:B['value_counts']=sparta_44bf6b657a(E.value_counts(dropna=_A).to_dict())
		t={'missing_values':int(E.isnull().sum()),'missing_percent':round(E.isnull().mean()*100,2),'is_constant':E.nunique(dropna=_A)<=1,'duplicate_rows':int(E.duplicated().sum()),'mixed_types':E.apply(type).nunique()>1};B['data_quality']=t
		if K:
			S='No suggestions';Q=0
			if abs(C.skew())>1.5:S='Highly skewed, consider log transform.';Q=1
			if C.nunique()<5:S='Very few unique values, maybe categorical?';Q=1
			j=S;u=C.value_counts(normalize=_B,dropna=_A).values[0]
			if u>.8:j='Highly imbalanced column (most frequent > 80%).';Q=1
			B['smart_flags']=j;B['suggestion_type']=Q
		G=_D;plt.rcParams.update({'axes.edgecolor':G,'xtick.color':G,'ytick.color':G,'text.color':G,'axes.labelcolor':G,'figure.facecolor':_d,'axes.facecolor':_d,'savefig.facecolor':_d,'savefig.edgecolor':_d});I,F=plt.subplots(figsize=(8,6));O=D
		if D==T:O=_H
		if K:R=C.dropna();sns.histplot(R,kde=_B,ax=F,edgecolor=_d);F.set_title(f"Histogram: {O}");F.set_xlabel(O)
		else:E.value_counts(dropna=_A).head(10).plot(kind='bar',ax=F);F.set_title(f"Top Categories: {O}");F.set_xlabel(O)
		plt.tight_layout();I=sparta_1824ab1ae8(I,V);v=sparta_0433db98e0(I)
		if K:I,F=plt.subplots(figsize=(8,6));sns.boxplot(x=R,ax=F,whiskerprops=dict(color=G),capprops=dict(color=G),medianprops=dict(color=G),flierprops=dict(markerfacecolor=G,markeredgecolor=G));F.set_title(f"Boxplot: {D}");N=R.mean();M=R.median();F.text(N,.05,f"Mean: {N:.2f}",color=_O,ha=_j,va=_S,fontsize=10);F.text(M,-.05,f"Median: {M:.2f}",color=_O,ha=_j,va=_a,fontsize=10);F.set_yticks([]);plt.tight_layout();I=sparta_1824ab1ae8(I,V);B['boxplot_base64']=sparta_0433db98e0(I)
		B['histogram_base64']=v;J[D]=sparta_44bf6b657a(B)
	print('report keys');print(J.keys());return J
def sparta_d4b84bc707(df,columns,B_DARK_THEME=_A):
	E=B_DARK_THEME;D='_correlation_matrix';A={};B=pd.DataFrame()
	for C in columns:
		F=sparta_c8aadd56bf(df[C])
		if F:G=pd.to_numeric(df[C],errors=_N);B[C]=G
	if B.shape[1]>1:A[D]=dict();A[D]['plot_base64']=sparta_98cde7ff08(B,B_DARK_THEME=E);A[D]['pairwise_plot_base64']=sparta_3c30bc6a5e(B,B_DARK_THEME=E)
	return A
def sparta_f1f4774550(data,title=''):
	C=pd.Series(data).dropna();A=adfuller(C.dropna(),autolag='AIC');B={_A6:float(A[0]),'p_value':float(A[1]),_A7:bool(A[1]<.05)}
	for(D,E)in A[4].items():B[f"Critical Value ({D})"]=float(E)
	return B
def sparta_2f907b9f7f(data,title=''):
	C=pd.Series(data).dropna();A=kpss(C,regression='ct',nlags='auto');B={_A6:float(A[0]),'p_value':float(A[1]),_A7:bool(A[1]>.05)}
	for(D,E)in A[3].items():B[f"Critical Value ({D})"]=float(E)
	return B
def sparta_02739295ad(df,x_col,y_col,B_DARK_THEME=_A):
	E=x_col;C=y_col;G={};H=[E]
	if C not in H:H+=[C]
	df=df[H].dropna().copy();B=df[E];B=pd.to_numeric(B,errors=_N);D=df[C];D=pd.to_numeric(D,errors=_N);print('x_col >> ');print(E);print('y_col >> ');print(C);print(_W);print(D);I=B.mean();L=D.mean();M=((B-I)*(D-L)).sum();N=((B-I)**2).sum();F=M/N;J=L-F*I;O=F*B+J;K,A=plt.subplots(figsize=(8,5));sns.scatterplot(x=B,y=D,ax=A,label='Data');A.plot(B,O,color=_O,label=f"Trendline\ny = {F:.2f}x + {J:.2f}");A.set_title(f"Scatter Plot with Regression Line\n{C} vs {E}",color=_D);A.set_xlabel(E,color=_D);A.set_ylabel(C,color=_D);A.tick_params(axis=_T,colors=_D);A.tick_params(axis=_W,colors=_D)
	for P in[_X,_S,_a,_e]:A.spines[P].set_color(_D)
	A.legend();K=sparta_1824ab1ae8(K,B_DARK_THEME=B_DARK_THEME);G['scatter_plot']=sparta_0433db98e0(K);G[_A8]=f"y = {F:.4f} * x + {J:.4f}";return G
def train_test_split_custom(X,y=_E,test_size=.25,shuffle=_B,random_seed=_E):
	B=random_seed
	if B is not _E:random.seed(B)
	C=len(X);A=list(range(C))
	if shuffle:random.shuffle(A)
	D=int(C*test_size);E=A[:D];F=A[D:];G=[X[A]for A in F];H=[X[A]for A in E]
	if y is not _E:I=[y[A]for A in F];J=[y[A]for A in E];return G,H,I,J
	else:return G,H
def sparta_7f53385209():
	try:import sklearn;return _B
	except ImportError:return _A
def sparta_a7fc47c317(df,x_cols,y_col,in_sample=_B,test_size=.2,window=30,B_DARK_THEME=_A):
	A4='rolling_betas';A3='test_pred_plot';A2='OLS: Test Set Prediction';A1='Actual (Test)';A0='full_pred_plot';z='OLS: Full Sample Prediction';s=test_size;b=in_sample;X=1.;M=window;L=y_col;K=x_cols;I='Intercept';H=B_DARK_THEME;E=df;C={};Y=K.copy()
	if L not in Y:Y+=[L]
	E=E[Y].dropna().copy()
	for G in Y:E[G]=pd.to_numeric(E[G],errors=_N)
	E=E.dropna();S=E[K];D=E[L]
	if b:c,d,e,J=S,S,D,D
	else:
		t=42
		if sparta_7f53385209():from sklearn.model_selection import train_test_split as A5;c,d,e,J=A5(S,D,test_size=s,random_state=t)
		else:c,d,e,J=train_test_split_custom(S,D,test_size=s,random_state=t)
	u=c.copy();u[I]=X;A6=sm.OLS(e,u).fit();A7=A6.params;v=d.copy();v[I]=X;f=v.dot(A7);g=S.copy();g[I]=X;h=sm.OLS(D,g).fit();N=h.params;Z=g.dot(N);w=' + '.join([f"{N[A]:.4f} * {A}"for A in K]);w+=f" + {N[I]:.4f}";C[_A8]=f"y = {w}";B,A=plt.subplots(figsize=(10,5));A.plot(D.index,D.values,label=_G,color=_c);A.plot(D.index,Z.values,linestyle=_F,label=_k,color=_Y);A.set_title(z);A.set_xlabel(_H);A.set_ylabel(_Q);A.legend();B=sparta_1824ab1ae8(B,H);C[A0]=sparta_0433db98e0(B)
	if not b:O,F=plt.subplots(figsize=(10,5));F.plot(J.index,J.values,label=A1,color=_c);F.plot(J.index,f.values,linestyle=_F,label='Predicted (Test)',color='blue');F.set_title(A2);F.set_xlabel(_H);F.set_ylabel(_Q);F.legend();O=sparta_1824ab1ae8(O,H);C[A3]=sparta_0433db98e0(O)
	x=[];i=[];j=[];P=[]
	if len(E)>M:
		for T in range(M,len(E)):k=E[K].iloc[T-M:T].copy();y=E[L].iloc[T-M:T].copy();k[I]=X;A8=sm.OLS(y,k).fit();l=A8.params;A9=k.dot(l);AA=y-A9;x.append(l[K]);i.append(l[I]);j.append(AA.std());P.append(E.index[T])
		m=pd.DataFrame(x,index=P);C[A4]=dict()
		for G in K:
			B,A=plt.subplots(figsize=(8,4));A.plot(m.index,m[G],label=f"Rolling Beta: {G}");A.axhline(N[G],linestyle=_F,color=_O,label=f"Full Beta = {N[G]:.2f}");A.set_title(f"{M}-Window Rolling Beta — {G}",color=_D);A.set_ylabel(L,color=_D);A.tick_params(axis=_T,colors=_D);A.tick_params(axis=_W,colors=_D)
			for U in[_X,_S,_a,_e]:A.spines[U].set_color(_D)
			A.legend();B=sparta_1824ab1ae8(B,H);C[A4][G]={_q:sparta_0433db98e0(B),'rolling_betas_json':pd.DataFrame(m[G]).to_json(orient=_C)}
		B,A=plt.subplots(figsize=(8,4));A.plot(P,i,label='Rolling Alpha (Intercept)',color='purple');A.axhline(N[I],linestyle=_F,color=_O,label=f"Full Alpha = {N[I]:.2f}");A.set_title(f"{M}-Window Rolling Intercept (Alpha)",color=_D);A.set_ylabel(L,color=_D);A.tick_params(axis=_T,colors=_D);A.tick_params(axis=_W,colors=_D)
		for U in[_X,_S,_a,_e]:A.spines[U].set_color(_D)
		A.legend();B=sparta_1824ab1ae8(B,H);C['rolling_alpha_plot']={_q:sparta_0433db98e0(B),'rolling_alphas_json':pd.DataFrame({'Rolling alphas':i},index=P).to_json(orient=_C)};B,A=plt.subplots(figsize=(8,4));A.plot(P,j,label='Rolling Residual Std',color=_Y);A.axhline((D-Z).std(),color=_O,linestyle=_F,label='Full History Residual Std');A.set_title(f"{M}-Window Rolling Residual Std",color=_D);A.set_ylabel(L,color=_D);A.tick_params(axis=_T,colors=_D);A.tick_params(axis=_W,colors=_D)
		for U in[_X,_S,_a,_e]:A.spines[U].set_color(_D)
		A.legend();B=sparta_1824ab1ae8(B,H);C['rolling_residual_std_plot']={_q:sparta_0433db98e0(B),'rolling_residuals_json':pd.DataFrame({_f:j},index=P).to_json(orient=_C)}
	B,A=plt.subplots(figsize=(10,5));A.plot(D.index,D.values,label=_G);A.plot(D.index,Z.values,linestyle=_F,label=_k,color=_Y);A.set_title(z);A.set_xlabel(_H);A.set_ylabel(_Q);A.legend();B=sparta_1824ab1ae8(B,H);C[A0]=sparta_0433db98e0(B);Q=Z.to_frame();Q.columns=[_I];Q[_G]=D;Q=Q[[_G,_I]];C['y_pred_full_json']=Q.to_json(orient=_C);n=D-Q[_I];o=range(len(n.values));p,V=plt.subplots(figsize=(8,4));V.scatter(o,n.values,alpha=.6,color=_O);V.axhline(0,linestyle=_F,color=_P);V.set_title('Residuals (Full Set)');V.set_xlabel(_H);V.set_ylabel(_g);p=sparta_1824ab1ae8(p,H);C['full_residuals_plot']=sparta_0433db98e0(p);C['full_residuals_json']=n.to_frame().to_json(orient=_C);a=E[K].iloc[[-1]].copy();a[I]=X;a=a[h.params.index];AB=h.predict(a).iloc[0];C['last_pred_values']=f"{D.iloc[-1]:.2f}";C['last_pred_full']=f"{AB:.2f}"
	if not b:O,F=plt.subplots(figsize=(10,5));F.plot(J.values,label=A1);F.plot(f.values,linestyle=_F,label=_k,color=_Y);F.set_title(A2);F.set_xlabel(_H);F.set_ylabel(_Q);F.legend();O=sparta_1824ab1ae8(O,H);R=f.to_frame();R.columns=[_I];R[_G]=J;R=R[[_G,_I]];C[A3]=sparta_0433db98e0(O);C['test_pred_json']=R.to_json(orient=_C);q=J-R[_I];o=range(len(q.values));r,W=plt.subplots(figsize=(8,4));W.scatter(o,q.values,alpha=.6,color=_O);W.axhline(0,linestyle=_F,color=_P);W.set_title('Residuals (Test Set)');W.set_xlabel(_H);W.set_ylabel(_g);r=sparta_1824ab1ae8(r,H);C['test_residuals_plot']=sparta_0433db98e0(r);C['test_residuals_json']=q.to_frame().to_json(orient=_C)
	return C
def sparta_efb8fbf247(df,col_x,col_y,window=30,B_DARK_THEME=_A):
	E=window;D=col_y;C=col_x;B=df;F=[C]
	if D not in F:F+=[D]
	B=B[F].dropna();M=[A for A in range(len(B))];J=B[C];J=pd.to_numeric(J,errors=_N);G=B[D];G=pd.to_numeric(G,errors=_N);K=B[C].rolling(E).corr(G);H=B[C].corr(B[D]);I,A=plt.subplots(figsize=(8,4));A.plot(M,K,label=f"{E}-period Rolling Corr",color='#2196f3');A.axhline(H,color=_O,linestyle=_F,label=f"Full Corr = {H:.2f}");A.set_title(f"Rolling Correlation — {C} vs {D}",color=_D);A.set_xlabel(_H,color=_D);A.set_ylabel(_r,color=_D);A.tick_params(axis=_T,colors=_D);A.tick_params(axis=_W,colors=_D)
	for N in A.spines.values():N.set_color(_D)
	A.legend();I=sparta_1824ab1ae8(I,B_DARK_THEME=B_DARK_THEME);L=K.to_frame();L.columns=[f"Rolling Correlation {E}"];return{_q:sparta_0433db98e0(I),'rolling_corr_json':L.to_json(orient=_C),'full_corr':H}
def sparta_f5804de388(df,x_cols,y_col):
	D=x_cols;C=y_col;B=D.copy()
	if C not in B:B+=[C]
	A=df[B].dropna().copy()
	for E in B:A[E]=pd.to_numeric(A[E],errors=_N)
	A=A.dropna();F=sm.add_constant(A[D]);G=A[C];H=sm.OLS(G,F).fit();return H.summary().as_html()
def sparta_f05595937d(df,y_col,x_cols,in_sample=_B,test_size=.2,rw_beta=30,rw_corr=30,B_DARK_THEME=_A):
	H=B_DARK_THEME;G=x_cols;B=y_col;A=df;N=sparta_a7fc47c317(A,G,B,in_sample=in_sample,test_size=test_size,window=rw_beta,B_DARK_THEME=H);L={};F={};E={};I=sparta_c8aadd56bf(A[B]);C=_E
	if I:C=pd.to_numeric(A[B],errors=_N);J=sparta_f1f4774550(C.tolist());K=sparta_2f907b9f7f(C.tolist());E[B]={'adf':J,'kpss':K}
	for D in G:
		L[D]=sparta_02739295ad(A,D,B,B_DARK_THEME=H);F[D]=sparta_efb8fbf247(A,D,B,window=rw_corr,B_DARK_THEME=H);I=sparta_c8aadd56bf(A[D]);C=_E
		if I:C=pd.to_numeric(A[D],errors=_N);J=sparta_f1f4774550(C.tolist());K=sparta_2f907b9f7f(C.tolist());E[D]={'adf':J,'kpss':K}
	O={'scatter':L};F={'correlations':F};E={'stationary_tests':E};M={**N,**O,**F,**E};M['stats_models_multivariate_html']=sparta_f5804de388(A,G,B);return M
def sparta_fb9a42ae41(fig,B_DARK_THEME):
	A=fig;B='#333333'
	if B_DARK_THEME:B='white'
	for C in A.axes:
		D=C.get_title()
		if D:C.set_title(D,color=B)
	if A._suptitle:A._suptitle.set_color(B)
	return A
def sparta_b096ddf5ae(df,x_col,y_cols,B_DARK_THEME=_A,start_date=_E,end_date=_E,date_type=_E):
	q='both';p='Performances';o='YTD';n='MTD';i='errorMsg';T=y_cols;Q=x_col;M=end_date;L=start_date;F=date_type;B=B_DARK_THEME;A=df;import quantstats as D;from project.sparta_440f6a201b.sparta_ceff546bba.qube_2940d28c8f import convert_dataframe_to_json as r;print('time_series_analysis');print(A);print('x_col');print(Q);print('y_cols');print(T);print('B_DARK_THEME > '+str(B));print('start_date > '+str(L));print('end_date > '+str(M));print('date_type > '+str(F));A=A.dropna()
	try:
		if Q==_H:A.index=pd.to_datetime(A.index)
		else:A.index=pd.to_datetime(A[Q])
	except Exception:pass
	A=A.sort_index(ascending=_B)
	if A.index.tz is not _E:A.index=A.index.tz_convert(_E)
	if F is not _E:
		if F!=-1:
			if F!=7:
				from dateutil.relativedelta import relativedelta as R;I=pd.Timestamp.now().normalize();J={n:I.replace(day=1),o:I.replace(month=1,day=1),'3M':I-R(months=3),'6M':I-R(months=6),'1Y':I-R(years=1),'3Y':I-R(years=3),'5Y':I-R(years=5)}
				if F==0:A=A[A.index>=J['3M']]
				elif F==1:A=A[A.index>=J['6M']]
				elif F==2:A=A[A.index>=J['1Y']]
				elif F==3:A=A[A.index>=J['3Y']]
				elif F==4:A=A[A.index>=J['5Y']]
				elif F==5:A=A[A.index>=J[n]]
				elif F==6:A=A[A.index>=J[o]]
				elif F==7:0
		else:
			if L is not _E:
				if len(L)>0:L=pd.to_datetime(L).tz_localize(_E).normalize();A=A[A.index>=L]
			if M is not _E:
				if len(M)>0:M=pd.to_datetime(M).tz_localize(_E).normalize();A=A[A.index<=M]
	if len(A)==0:raise Exception('Empty dataframe, please control the input data and applied dates filters...This filters may not be appropriate and conduct to empty dataframe')
	s=0;U=pd.DataFrame()
	for(j,K)in enumerate(T):
		W=A[K];W.index=pd.to_datetime(W.index);k=D.reports.metrics(W,rf=s,mode='basic',display=_A,strategy_title='Returns Analysis',benchmark_title='Benchmark')
		if j==0:U=k;U.columns=[K]
		else:U[K]=k
	t=r(U);G=A[T]
	if Q==_H:G.index=pd.to_datetime(G.index)
	else:G.index=pd.to_datetime(G[Q])
	G=G.sort_index(ascending=_B);X=100*(G+1).cumprod();H,C=plt.subplots(figsize=(8,4))
	for l in X.columns:C.plot(X.index,X[l],label=l)
	C.set_title(p,fontsize=16,color=_D);C.set_xlabel('Date',color=_D);C.set_ylabel(p,color=_D);C.legend(loc='upper left');C.grid(_B,which=q,axis=q,linestyle=_F,linewidth=.5,alpha=.4,color=_c);C.tick_params(axis=_T,colors=_D);C.tick_params(axis=_W,colors=_D);C.spines[_S].set_color(_D);C.spines[_X].set_color(_D)
	for Y in[_X,_S,_a,_e]:C.spines[Y].set_color(_D)
	H.tight_layout();H=sparta_1824ab1ae8(H,B);u=sparta_0433db98e0(H);m=dict()
	for(j,K)in enumerate(T):
		E=G[K];Z=D.plots.monthly_heatmap(E,show=_A,ylabel=_A);Z=sparta_fb9a42ae41(Z,B_DARK_THEME=B);a=D.plots.yearly_returns(E,show=_A,ylabel=_A);a=sparta_fb9a42ae41(a,B_DARK_THEME=B);b=D.plots.distribution(E,show=_A,ylabel=_A);b=sparta_fb9a42ae41(b,B_DARK_THEME=B);H,C=plt.subplots(figsize=(8,4));x=_D;sns.histplot(E,kde=_B,ax=C,edgecolor=_d);C.set_title(f"Histogram: {K}");C.set_title(f"Histogram",color=_D);C.tick_params(axis=_T,colors=_D);C.tick_params(axis=_W,colors=_D);C.spines[_S].set_color(_D);C.spines[_X].set_color(_D)
		for Y in[_X,_S,_a,_e]:C.spines[Y].set_color(_D)
		plt.tight_layout();H=sparta_1824ab1ae8(H,B);V=io.BytesIO();H.savefig(V,format=_n,transparent=_B);V.seek(0);v=base64.b64encode(V.read()).decode(_o);V.close();plt.close();c=D.plots.histogram(E,show=_A,ylabel=_A);c=sparta_fb9a42ae41(sparta_1824ab1ae8(c,B_DARK_THEME=B),B_DARK_THEME=B);d=D.plots.returns(E,show=_A,ylabel=_A);d=sparta_fb9a42ae41(sparta_1824ab1ae8(d,B_DARK_THEME=B),B_DARK_THEME=B);e=D.plots.log_returns(E,show=_A,ylabel=_A);e=sparta_fb9a42ae41(sparta_1824ab1ae8(e,B_DARK_THEME=B),B_DARK_THEME=B);f=D.plots.distribution(E,show=_A,ylabel=_A);f=sparta_fb9a42ae41(sparta_1824ab1ae8(f,B_DARK_THEME=B),B_DARK_THEME=B);g=D.plots.drawdown(E,show=_A,ylabel=_A);g=sparta_fb9a42ae41(sparta_1824ab1ae8(g,B_DARK_THEME=B),B_DARK_THEME=B);h=D.plots.drawdowns_periods(E,show=_A,ylabel=_A);h=sparta_fb9a42ae41(sparta_1824ab1ae8(h,B_DARK_THEME=B),B_DARK_THEME=B)
		try:N=D.plots.rolling_volatility(E,show=_A,ylabel=_A);N=sparta_fb9a42ae41(sparta_1824ab1ae8(N,B_DARK_THEME=B),B_DARK_THEME=B);N=sparta_0433db98e0(N)
		except Exception as S:N={i:str(S)}
		try:O=D.plots.rolling_sharpe(E,show=_A,ylabel=_A);O=sparta_fb9a42ae41(sparta_1824ab1ae8(O,B_DARK_THEME=B),B_DARK_THEME=B);O=sparta_0433db98e0(O)
		except Exception as S:O={i:str(S)}
		try:P=D.plots.rolling_sortino(E,show=_A,ylabel=_A);P=sparta_fb9a42ae41(sparta_1824ab1ae8(P,B_DARK_THEME=B),B_DARK_THEME=B);P=sparta_0433db98e0(P)
		except Exception as S:P={i:str(S)}
		m[K]={'heatmap':sparta_0433db98e0(Z),'yearlyReturns':sparta_0433db98e0(a),'histogram':sparta_0433db98e0(c),'returns':sparta_0433db98e0(d),'log_returns':sparta_0433db98e0(e),'distribution':sparta_0433db98e0(f),'rolling_vol':N,'rolling_sharpe':O,'rolling_sortino':P,'quantiles':sparta_0433db98e0(b),'dd':sparta_0433db98e0(g),'dd_period':sparta_0433db98e0(h),'daily_ret_histgram':v}
	w=[A.isoformat()for A in A.index.tolist()];return{_l:t,'perf_64':u,'cols_analysis':m,'datesArr':w}
def sparta_6923b1e83b(explained_variance_ratio,cumulative_variance):C=cumulative_variance;B=explained_variance_ratio;D,A=plt.subplots(figsize=(8,4));A.bar(range(1,len(B)+1),B,alpha=.5,align=_j);A.step(range(1,len(C)+1),C,where='mid',label='Cumulative Explained Variance');A.set_ylabel('Explained Variance Ratio');A.set_xlabel(_A9);A.set_title('Explained Variance');A.legend(loc='best');A.grid(_B);return D
def sparta_108cedd50a(loadings):B,A=plt.subplots(figsize=(10,4));sns.heatmap(loadings,annot=_B,cmap=_p,ax=A);A.set_title('PCA Loadings Heatmap');A.set_xlabel(_A9);A.set_ylabel('Features');return B
def sparta_fe3b51d58a(scores_df,loadings,features):
	F='PC2';E='PC1';D=scores_df;B=loadings;G,A=plt.subplots(figsize=(8,6));A.scatter(D[E],D[F],alpha=.5)
	for(C,H)in enumerate(features):A.arrow(0,0,B.iloc[C,0],B.iloc[C,1],color='r',alpha=.5);A.text(B.iloc[C,0]*1.15,B.iloc[C,1]*1.15,H,color='g',ha=_j,va=_j)
	A.set_xlabel(E);A.set_ylabel(F);A.set_title('PCA Biplot');A.grid(_B);return G
def sparta_c1cc6a3908(scores_df):B,A=plt.subplots(figsize=(10,5));scores_df.plot(ax=A,title='Principal Component Time Series');A.set_xlabel('Time');A.set_ylabel('Score');A.grid(_B);return B
def sparta_f288e0d096(explained_variance_ratio,loadings,top_n_features=2):
	C=sum(explained_variance_ratio[:2])*100;A=f"The first 2 components explain <span class='pageNavTitle'>{C:.1f}%</span> of the variance."
	for B in range(2):A+='<li>';D=f"PC{B+1}";E=loadings[B].abs().sort_values(ascending=_A);F=E.head(top_n_features).index.tolist();G=' and '.join(F);A+=f" {D} is heavily driven by {G}.";A+='</li>'
	return A
def sparta_06c7ea30b8(df,y_cols,n_components=3,explained_variance=90,scale=_B,components_mode=1,B_DARK_THEME=_A):
	S='cumulative_variance';O=explained_variance;N='scores';M='explained_variance_ratio';F='loadings';E=B_DARK_THEME;D=components_mode;A=df;from sklearn.decomposition import PCA;from sklearn.preprocessing import StandardScaler as T;A=A.dropna();A=A[y_cols]
	try:A=A.sort_index(ascending=_B)
	except:pass
	if scale:U=T();V=U.fit_transform(A)
	D=int(D)
	if D==1:C=PCA(n_components=int(n_components))
	elif D==2:print('explained_variance >>> '+str(O));C=PCA(n_components=float(O)/100)
	else:raise ValueError('components_mode must be 1 (variance) or 2 (fixed number)')
	P=C.fit_transform(V);G=list(C.explained_variance_ratio_);W=pd.Series(G).cumsum().tolist();H=pd.DataFrame(C.components_,columns=A.columns);Q=pd.DataFrame(P,columns=[f"PC{A+1}"for A in range(P.shape[1])]);R=H.T.multiply(C.explained_variance_**.5,axis=1);B={_K:1,M:G,S:W,'components':H,N:Q,F:R};I=sparta_6923b1e83b(B[M],B[S]);I=sparta_1824ab1ae8(I,E);J=sparta_108cedd50a(B[F]);J=sparta_1824ab1ae8(J,E);K=sparta_fe3b51d58a(B[N],B[F],A.columns);K=sparta_1824ab1ae8(K,E);L=sparta_c1cc6a3908(B[N]);L=sparta_1824ab1ae8(L,E);X=sparta_0433db98e0(I);Y=sparta_0433db98e0(J);Z=sparta_0433db98e0(K);a=sparta_0433db98e0(L);b=sparta_f288e0d096(explained_variance_ratio=B[M],loadings=B[F]);c={_K:1,'scree_64':X,'loadings_heatmap64':Y,'biplot64':Z,'ts64':a,'summary_text':b,'pca_json':Q.to_json(orient=_C),'loadings_json':R.to_json(orient=_C),'variance_ratio_json':pd.DataFrame(G).to_json(orient=_C),'components_json':H.to_json(orient=_C)};return c
def sparta_b4a37f18ef(df,y_cols,n_clusters=3,B_DARK_THEME=_A):
	S=n_clusters;L=B_DARK_THEME;K=y_cols;A=df;from sklearn.cluster import KMeans as T;from sklearn.preprocessing import StandardScaler as X;from sklearn.decomposition import PCA;from sklearn.metrics import silhouette_score as Y;A=A[K].dropna();M=A[K];print('X X X');print(K);print(M);print('n_clusters >>> '+str(S))
	for C in M.columns:A[C]=pd.to_numeric(A[C],errors=_N)
	Z=X();H=Z.fit_transform(M);a=T(n_clusters=S,random_state=42);N=a.fit_predict(H);A[_L]=N;b=PCA(n_components=2);U=b.fit_transform(H);V=Y(H,N);print(f"Silhouette Score: {V:.3f}");D=A.groupby(_L).agg(['mean','std']);print('\nCluster Summary Statistics:');print(D);E,F=plt.subplots(figsize=(8,6));c=F.scatter(U[:,0],U[:,1],c=N,cmap='Set2',s=50);F.set_title('KMeans Clustering (2D PCA)');F.set_xlabel(_AA);F.set_ylabel(_AB);E.colorbar(c,ax=F,label=_L);E.tight_layout();E=sparta_1824ab1ae8(E,L);O=[];P=range(1,10)
	for d in P:W=T(n_clusters=d,random_state=42);W.fit(H);O.append(W.inertia_)
	I,G=plt.subplots(figsize=(8,6));G.plot(P,O,marker='o');G.set_title('Elbow Method for Optimal k');G.set_xlabel('Number of clusters (k)');G.set_ylabel('Inertia');G.grid(_B);I.tight_layout();I=sparta_1824ab1ae8(I,L);B=A.copy();B[_L]=B[_L].astype(str);B=B.melt(id_vars=_L,var_name=_J,value_name=_s);J,Q=plt.subplots(figsize=(12,6));sns.boxplot(x=_J,y=_s,hue=_L,data=B,ax=Q);Q.set_title('Feature Distributions by Cluster');Q.tick_params(axis=_T,rotation=45);J.tight_layout();J=sparta_1824ab1ae8(J,L);e=[f"{A[0]} ({A[1]})"for A in D.columns];R=[]
	for C in D.columns:
		if C[0]not in R:R.append(C[0])
	f={'data':D.values.tolist(),'index':D.index.tolist(),'columns':e,'columns_unique':R};g=A;h=pd.DataFrame(O,index=P);return{_K:1,'kmean64':sparta_0433db98e0(E),'elbow64':sparta_0433db98e0(I),_AC:sparta_0433db98e0(J),'sil_score':V.round(2),_AD:f,_AE:g.to_json(orient=_C),'elbow_json':h.to_json(orient=_C),_AF:B.to_json(orient=_C)}
def sparta_e6c3702b37(df,y_cols,epsilon=.5,min_samples=5,B_DARK_THEME=_A):
	K=B_DARK_THEME;J=y_cols;A=df;from sklearn.cluster import DBSCAN as P;from sklearn.preprocessing import StandardScaler as Q;from sklearn.decomposition import PCA;from sklearn.metrics import silhouette_score as R;A=A[J].dropna();S=A[J];T=Q();E=T.fit_transform(S);U=P(eps=epsilon,min_samples=min_samples);F=U.fit_predict(E);A[_L]=F;V=PCA(n_components=2);L=V.fit_transform(E);M=[A!=-1 for A in F];N=[B for(A,B)in enumerate(F)if M[A]];W=[E[A]for A in range(len(E))if M[A]]
	if len(set(N))>1:X=R(W,N)
	else:X=_E
	O=A[A[_L]!=-1];H=O.groupby(_L).agg(['mean','std']);Y=[f"{A[0]} ({A[1]})"for A in H.columns];Z={'data':H.values.tolist(),'index':H.index.tolist(),'columns':Y};C,D=plt.subplots(figsize=(8,6));a=D.scatter([A[0]for A in L],[A[1]for A in L],c=F,cmap='Set2',s=50);D.set_title('DBSCAN Clustering (2D PCA)');D.set_xlabel(_AA);D.set_ylabel(_AB);C.colorbar(a,ax=D,label=_L);C.tight_layout();C=sparta_1824ab1ae8(C,K);B=O.copy();B[_L]=B[_L].astype(str);B=B.melt(id_vars=_L,var_name=_J,value_name=_s);G,I=plt.subplots(figsize=(12,6));sns.boxplot(x=_J,y=_s,hue=_L,data=B,ax=I);I.set_title('Feature Distributions by Cluster (DBSCAN)');I.tick_params(axis=_T,rotation=45);G.tight_layout();G=sparta_1824ab1ae8(G,K);b=A;return{_K:1,'pca64':sparta_0433db98e0(C),_AC:sparta_0433db98e0(G),_AD:Z,_AE:b.to_json(orient=_C),_AF:B.to_json(orient=_C)}
def sparta_e3bfee67bd(df,y_cols,threshold=.5,B_DARK_THEME=_A):
	Q='weight';H=B_DARK_THEME;F=threshold;import networkx as G;df=df[y_cols].dropna();A=df.corr();I=[];B=list(A.columns);F=float(F)
	for J in range(len(B)):
		for R in range(J+1,len(B)):
			K=B[J];L=B[R];M=A.loc[K,L]
			if abs(M)>=F:I.append((K,L,{Q:M}))
	C=G.Graph();C.add_edges_from(I);D,N=plt.subplots(figsize=(8,6));S=G.spring_layout(C,seed=42);O=[abs(B[Q])for(A,A,B)in C.edges(data=_B)];G.draw(C,S,ax=N,with_labels=_B,width=O,edge_color=O,edge_cmap=plt.cm.viridis,node_color=_t,node_size=2000,font_size=10);N.set_title('Correlation Network (|p| > 0.5)');D.tight_layout();D=sparta_1824ab1ae8(D,H);E,P=plt.subplots(figsize=(8,6));sns.heatmap(A,annot=_B,fmt='.2f',cmap=_p,ax=P);P.set_title(_A5);E.tight_layout();E=sparta_1824ab1ae8(E,H);return{_K:1,'nx64':sparta_0433db98e0(D),'corr64':sparta_0433db98e0(E),'correlation_json':A.to_json(orient=_C)}
def sparta_6d46e6685e(df,y_cols,n_components=2,perplexity=30,B_DARK_THEME=_A):E=perplexity;D=n_components;from sklearn.preprocessing import StandardScaler as I;from sklearn.decomposition import PCA;from sklearn.manifold import TSNE;from sklearn.cluster import KMeans as J;df=df[y_cols].dropna();K=I();F=K.fit_transform(df);D=min(D,3);L=J(n_clusters=D,random_state=42);G=L.fit_predict(F);E=min(int(E),len(df)-1);M=TSNE(n_components=D,perplexity=E,n_iter=400,random_state=42);N=M.fit_transform(F);A=pd.DataFrame(N);A[_L]=G.astype(str);H=list(A.columns);B,C=plt.subplots(figsize=(8,6));O=C.scatter(A[H[0]],A[H[1]],c=G,cmap='Set2',s=50);C.set_title('t-SNE Projection (Colored by KMeans Clusters)');C.set_xlabel('Component 1');C.set_ylabel('Component 2');B.colorbar(O,ax=C,label=_L);B.tight_layout();B=sparta_1824ab1ae8(B,B_DARK_THEME);return{_K:1,'tsne64':sparta_0433db98e0(B),'tsne':A.to_json(orient=_C)}
def sparta_f16694e36f(r2,n,k):return 1-(1-r2)*((n-1)/(n-k-1))if n>k+1 else _E
def sparta_51fd438074(df,y_target,x_cols,degree=2,standardize=_B,in_sample=_B,test_size=.2,B_DARK_THEME=_A):
	o='Adjusted R2';g=in_sample;f=degree;Y=standardize;Q=B_DARK_THEME;J=x_cols;from sklearn.preprocessing import StandardScaler as h,PolynomialFeatures as p;from sklearn.linear_model import LinearRegression as q;from sklearn.metrics import r2_score,mean_squared_error as i,mean_absolute_error as r;from sklearn.model_selection import train_test_split as s;from sklearn.metrics import r2_score,mean_squared_error as i;from math import sqrt;t=df[y_target];D=t;df=df[J].dropna();E=df
	if g:
		B,C,R,A=E.astype(float),E.astype(float),D.astype(float),D.astype(float);R=R.astype(float);A=A.astype(float)
		if Y:F=h();K=F.fit_transform(B);L=F.transform(C);B=pd.DataFrame(K,columns=J,index=B.index);C=pd.DataFrame(L,columns=J,index=C.index);S=F.transform(E)
		else:B=B.astype(float);C=C.astype(float);K=B.values;L=C.values;S=E.astype(float).values
	else:
		u=42;B,C,R,A=s(E,D,test_size=test_size,random_state=u)
		if Y:F=h();K=F.fit_transform(B);L=F.transform(C);S=F.transform(E)
		else:B=B.astype(float);C=C.astype(float);K=B.values;L=C.values;S=E.astype(float).values
	T=p(degree=f,include_bias=_A);v=T.fit_transform(K);j=T.transform(L);w=T.transform(S);M=q();M.fit(v,R);G=M.predict(j);Z=M.predict(w);k=r2_score(A,G);x=sqrt(i(A,G));y=r(A,G);a=sparta_f16694e36f(k,len(A),j.shape[1]);U={_Z:round(k,4),o:round(a,4)if a is not _E else _E,_R:round(x,4),_U:round(y,4)};z=T.get_feature_names_out(J);A0=M.coef_;A1=M.intercept_
	def A2(term,coef):A=term;A=A.replace('^','<sup>')+'</sup>'if'^'in A else A;return f"{coef:.4f} × {A}"
	b=f"{A1:.4f}"
	for(l,A3)in zip(A0,z):A4=A2(A3,l);A5=' + 'if l>=0 else' - ';b+=A5+A4.lstrip('-')
	m='test'
	if g:m='full'
	A6=f"The polynomial regression model of degree <span class='whiteLabel' style='font-weight:bold'>{f}</span> using features <span class='whiteLabel' style='font-weight:bold'>{J}</span> {_u if Y else _v} standardization achieved:<br><span class='whiteLabel' style='font-weight:bold'>R2 of {U[_Z]}</span><br><span class='whiteLabel' style='font-weight:bold'>RMSE of {U[_R]}</span><br>"+(f"<span class='whiteLabel' style='font-weight:bold'>Adjusted R2 of {U[o]}</span><br>"if a is not _E else'')+f"on the <span style='text-decoration:underline'>{m} set</span>.<br><span class='whiteLabel' style='font-weight:bold'>Last value: {D.iloc[-1]:.2f}</span><br><span class='whiteLabel' style='font-weight:bold'>Next step prediction: {Z[-1]:.2f}</span><br>"+(f"<br><span class='whiteLabel' style='font-weight:bold'>The polynomial equation is:</span><br><code class='whiteLabel' style='font-weight:bold; font-family:monospace; display:inline-block; padding:7px'>{b}</code>"if b is not _E else'');V,H=plt.subplots(figsize=(8,5));H.plot(A.values,label=_G,marker='o');H.plot(G,label='Predicted (Polynomial)',linestyle=_F);H.set_title(_AG);H.set_xlabel(_H);H.set_ylabel(_Q);H.legend();V.tight_layout();V=sparta_1824ab1ae8(V,Q);c=pd.DataFrame(A.values,index=A.index,columns=[_A1]);c[_A2]=G;d=A.values-G;n=range(len(d));W,N=plt.subplots(figsize=(8,5));N.scatter(n,d,color=_O,alpha=.6);N.axhline(0,color=_P,linestyle=_F);N.set_title(_AH);N.set_xlabel(_H);N.set_ylabel(_g);W.tight_layout();W=sparta_1824ab1ae8(W,Q);A7=pd.DataFrame(d,index=n,columns=[_f]);X,O=plt.subplots(figsize=(6,6));O.scatter(A,G,alpha=.7);O.plot([min(A),max(A)],[min(A),max(A)],color=_P,linestyle=_F);O.set_title(_AI);O.set_xlabel(_G);O.set_ylabel(_V);X.tight_layout();X=sparta_1824ab1ae8(X,Q);e,I=plt.subplots(figsize=(10,5));I.plot(D.index,D.values,label=_G);I.plot(D.index,Z,linestyle=_F,label='Full Sample Prediction');I.set_title('Polynomial Regression: Full Sample Prediction');I.set_xlabel(_H);I.set_ylabel(_Q);I.legend();e=sparta_1824ab1ae8(e,Q);P=pd.DataFrame(Z);P.columns=[_I];P[_G]=D;P=P[[_G,_I]];return{_K:1,_m:A6,_l:U,_w:sparta_0433db98e0(V),_x:sparta_0433db98e0(W),_A3:sparta_0433db98e0(X),_h:c.to_json(orient=_C),_b:A7.to_json(orient=_C),_h:c.to_json(orient=_C),_A4:sparta_0433db98e0(e),'pred_full_json':P.to_json(orient=_C)}
def sparta_2a87d415df(df,y_target,x_cols,max_depth=_E,in_sample=_B,standardize=_B,test_size=.2,B_DARK_THEME=_A):
	h=in_sample;N=standardize;I=df;G=B_DARK_THEME;B=x_cols;from sklearn.preprocessing import StandardScaler as i;from sklearn.tree import DecisionTreeRegressor as s,export_text as t;from sklearn.metrics import r2_score as u,mean_squared_error as v,mean_absolute_error as w;from sklearn.model_selection import train_test_split as x;from sklearn.tree import plot_tree as y;from sklearn.inspection import PartialDependenceDisplay as z;from math import sqrt;A0=I[y_target];O=A0;I=I[B].dropna();Y=I;j=42;C,D,H,A=x(Y,O,test_size=test_size,random_state=j)
	if h:
		C,D,H,A=Y.astype(float),Y.astype(float),O.astype(float),O.astype(float);H=H.astype(float);A=A.astype(float)
		if N:J=i();Z=J.fit_transform(C);a=J.transform(D);C=pd.DataFrame(Z,columns=B,index=H.index);D=pd.DataFrame(a,columns=B,index=A.index)
		else:C=C.astype(float);D=D.astype(float);C=pd.DataFrame(C.values,columns=B,index=H.index);D=pd.DataFrame(D.values,columns=B,index=A.index)
	elif N:J=i();Z=J.fit_transform(C);a=J.transform(D);C=pd.DataFrame(Z,columns=B,index=H.index);D=pd.DataFrame(a,columns=B,index=A.index)
	else:C=C.astype(float);D=D.astype(float);C=pd.DataFrame(C.values,columns=B,index=H.index);D=pd.DataFrame(D.values,columns=B,index=A.index)
	F=s(max_depth=max_depth,random_state=j);F.fit(C,H);K=F.predict(D);A1=u(A,K);A2=sqrt(v(A,K));A3=w(A,K);T={_Z:round(A1,4),_R:round(A2,4),_U:round(A3,4)};k=I[B].iloc[[-1]].copy()
	if N:l=J.transform(k)
	else:l=k.values
	A4=F.predict(l)[0];P='test'
	if h:P='full'
	A5=f"The decision tree regression model using features {B} {_u if N else _v} standardization achieved:<br> <span class='whiteLabel' style='font-weight:bold'>R2 of {T[_Z]}</span><br><span class='whiteLabel' style='font-weight:bold'>RMSE of {T[_R]}</span><br><span class='whiteLabel' style='font-weight:bold'>MAE of {T[_U]}</span><br>on the <span style='text-decoration:underline'>{P} set</span>.<br><span class='whiteLabel' style='font-weight:bold'>Last value: {O.iloc[-1]:.2f}</span><br><span class='whiteLabel' style='font-weight:bold'>Next step prediction: {A4:.2f}</span><br>"
	if N:m=J.transform(I[B])
	else:m=I[B].astype(float).values
	n=F.predict(m);U=O;b,L=plt.subplots(figsize=(10,5));L.plot(U.index,U.values,label=_G);L.plot(U.index,n,linestyle=_F,label=_k,color=_Y);L.set_title('Decision Tree: Full Sample Prediction');L.set_xlabel(_H);L.set_ylabel(_Q);L.legend();b=sparta_1824ab1ae8(b,G);Q=U;Q=Q.to_frame();Q[_I]=n;Q.columns=[_G,_I];V,M=plt.subplots(figsize=(8,5));M.plot(A.values,label=_G,marker='o');M.plot(K,label=_V,linestyle=_F);M.set_title(f"Actual vs Predicted ({P.capitalize()} Set)");M.set_xlabel(_H);M.set_ylabel(_Q);M.legend();V.tight_layout();V=sparta_1824ab1ae8(V,G);o=pd.DataFrame(A.values,index=A.index,columns=[_A1]);o[_A2]=K;c=A.values-K;p=range(len(c));W,R=plt.subplots(figsize=(8,5));R.scatter(p,c,color=_O,alpha=.6);R.axhline(0,color=_P,linestyle=_F);R.set_title(f"Residual Plot ({P.capitalize()} Set)");R.set_xlabel(_H);R.set_ylabel(_g);W.tight_layout();W=sparta_1824ab1ae8(W,G);A6=pd.DataFrame(c,index=p,columns=[_f]);X,S=plt.subplots(figsize=(6,6));S.scatter(A,K,alpha=.7);S.plot([min(A),max(A)],[min(A),max(A)],color=_P,linestyle=_F);S.set_title(f"Prediction vs Actual ({P.capitalize()} Set)");S.set_xlabel(_G);S.set_ylabel(_V);X.tight_layout();X=sparta_1824ab1ae8(X,G);A7=t(F,feature_names=B);d,E=plt.subplots(figsize=(12,8));y(F,feature_names=B,filled=_B,rounded=_B,fontsize=10,ax=E);d=sparta_1824ab1ae8(d,G);A8=F.feature_importances_;q=pd.DataFrame({_J:B,_M:A8}).sort_values(by=_M,ascending=_A);e,E=plt.subplots(figsize=(6,4));E.barh(q[_J],q[_M]);E.set_title('Feature Importance (Decision Tree)');E.invert_yaxis();e=sparta_1824ab1ae8(e,G);f,E=plt.subplots(figsize=(12,6));z.from_estimator(F,D,features=B,ax=E);f=sparta_1824ab1ae8(f,G);r=F.predict(C);g,E=plt.subplots();E.hist(r,bins=10,color=_t);E.set_title('Distribution of Leaf Node Predictions');E.set_xlabel('Predicted Value');g=sparta_1824ab1ae8(g,G);A9=pd.DataFrame(r);return{_K:1,_m:A5,_AJ:A7,_l:T,_w:sparta_0433db98e0(V),_x:sparta_0433db98e0(W),_A3:sparta_0433db98e0(X),_AK:sparta_0433db98e0(d),_AL:sparta_0433db98e0(e),_AM:sparta_0433db98e0(f),'figLeaf':sparta_0433db98e0(g),_b:A6.to_json(orient=_C),_h:o.to_json(orient=_C),'leaf_json':A9.to_json(orient=_C),_AN:Q.to_json(orient=_C),_A4:sparta_0433db98e0(b)}
def sparta_f051b4183e(df,y_target,x_cols,max_depth=_E,in_sample=_A,standardize=_B,test_size=.2,B_DARK_THEME=_A):
	T=B_DARK_THEME;S=standardize;C=x_cols;from sklearn.preprocessing import StandardScaler as U;from sklearn.tree import DecisionTreeRegressor as W,export_text as X;from sklearn.metrics import r2_score as Y,mean_squared_error as Z,mean_absolute_error as a;from sklearn.model_selection import train_test_split as b;from sklearn.tree import plot_tree as c;from sklearn.inspection import PartialDependenceDisplay;from sklearn.model_selection import GridSearchCV as d;from math import sqrt;e=df[y_target];K=e;df=df[C].dropna();L=df;f=42;A,B,E,D=b(L,K,test_size=test_size,random_state=f)
	if in_sample:
		A,B,E,D=L.astype(float),L.astype(float),K.astype(float),K.astype(float);E=E.astype(float);D=D.astype(float)
		if S:G=U();M=G.fit_transform(A);N=G.transform(B);A=pd.DataFrame(M,columns=C,index=E.index);B=pd.DataFrame(N,columns=C,index=D.index)
		else:A=A.astype(float);B=B.astype(float);A=pd.DataFrame(A.values,columns=C,index=E.index);B=pd.DataFrame(B.values,columns=C,index=D.index)
	elif S:G=U();M=G.fit_transform(A);N=G.transform(B);A=pd.DataFrame(M,columns=C,index=E.index);B=pd.DataFrame(N,columns=C,index=D.index)
	else:A=A.astype(float);B=B.astype(float);A=pd.DataFrame(A.values,columns=C,index=E.index);B=pd.DataFrame(B.values,columns=C,index=D.index)
	g={_i:list(range(2,11))+[_E]};H=d(estimator=W(random_state=42),param_grid=g,scoring=_AO,cv=5,n_jobs=-1);H.fit(A,E);O=H.best_estimator_;V=H.best_params_[_i];P=O.predict(B);h=Y(D,P);i=sqrt(Z(D,P));j=a(D,P);l={_Z:round(h,4),_R:round(i,4),_U:round(j,4),_AP:V};I=pd.DataFrame(H.cv_results_);J,F=plt.subplots();F.plot(I[_y],-I[_z],marker='o');F.set_title(_AQ);F.set_xlabel(_i);F.set_ylabel(_AR);F.grid(_B);J.tight_layout();J=sparta_1824ab1ae8(J,T);k=X(O,feature_names=C);Q,F=plt.subplots(figsize=(12,8));c(O,feature_names=C,filled=_B,rounded=_B,fontsize=10,ax=F);Q=sparta_1824ab1ae8(Q,T);R=-I[_z].to_frame();R.index=I[_y].values;R.columns=[_AS];return{_K:1,_AT:V,_AU:sparta_0433db98e0(J),_AJ:k,_AK:sparta_0433db98e0(Q),_AV:R.to_json(orient=_C)}
def sparta_73aa49e98e(df,y_target,x_cols,n_estimators=100,max_depth=_E,in_sample=_A,standardize=_B,test_size=.2,B_DARK_THEME=_A):
	h=in_sample;g=max_depth;f=n_estimators;R=standardize;H=B_DARK_THEME;G=df;C=x_cols;from sklearn.preprocessing import StandardScaler as i;from sklearn.ensemble import RandomForestRegressor as p;from sklearn.metrics import r2_score as q,mean_squared_error as r,mean_absolute_error as s;from sklearn.model_selection import train_test_split as t;from sklearn.inspection import PartialDependenceDisplay as u;from math import sqrt;v=G[y_target];L=v;G=G[C].dropna();X=G;j=42;D,B,E,A=t(X,L,test_size=test_size,random_state=j)
	if h:
		D,B,E,A=X.astype(float),X.astype(float),L.astype(float),L.astype(float);E=E.astype(float);A=A.astype(float)
		if R:I=i();Y=I.fit_transform(D);Z=I.transform(B);D=pd.DataFrame(Y,columns=C,index=E.index);B=pd.DataFrame(Z,columns=C,index=A.index)
		else:D=D.astype(float);B=B.astype(float);D=pd.DataFrame(D.values,columns=C,index=E.index);B=pd.DataFrame(B.values,columns=C,index=A.index)
	elif R:I=i();Y=I.fit_transform(D);Z=I.transform(B);D=pd.DataFrame(Y,columns=C,index=E.index);B=pd.DataFrame(Z,columns=C,index=A.index)
	else:D=D.astype(float);B=B.astype(float);D=pd.DataFrame(D.values,columns=C,index=E.index);B=pd.DataFrame(B.values,columns=C,index=A.index)
	M=p(n_estimators=f,max_depth=g,random_state=j);M.fit(D,E);F=M.predict(B);w=q(A,F);x=sqrt(r(A,F));y=s(A,F);S={_Z:round(w,4),_R:round(x,4),_U:round(y,4)}
	if R:k=I.transform(G[C])
	else:k=G[C].astype(float).values
	a=M.predict(k);T=L;l='test'
	if h:l='full'
	z=f"The random forest regression model using features {C} {_u if R else _v} standardization and <span class='whiteLabel'>n_estimators={f}, max_depth={g}</span> achieved:<br><span class='whiteLabel' style='font-weight:bold'>R2 of {S[_Z]}</span><br><span class='whiteLabel' style='font-weight:bold'>RMSE of {S[_R]}</span><br><span class='whiteLabel' style='font-weight:bold'>MAE of {S[_U]}</span><br>on the <span style='text-decoration:underline'>{l} set</span>.<br><span class='whiteLabel' style='font-weight:bold'>Last value: {L.iloc[-1]:.2f}</span><br><span class='whiteLabel' style='font-weight:bold'>Next step prediction: {a[-1]:.2f}</span><br>";b,J=plt.subplots(figsize=(10,5));J.plot(T.index,T.values,label=_G);J.plot(T.index,a,linestyle=_F,label=_k,color=_Y);J.set_title('Random Forest Tree: Full Sample Prediction');J.set_xlabel(_H);J.set_ylabel(_Q);J.legend();b=sparta_1824ab1ae8(b,H);N=T;N=N.to_frame();N[_I]=a;N.columns=[_G,_I];U,K=plt.subplots(figsize=(8,5));K.plot(A.values,label=_G,marker='o');K.plot(F,label=_V,linestyle=_F);K.set_title(_AG);K.set_xlabel(_H);K.set_ylabel(_Q);K.legend();U.tight_layout();U=sparta_1824ab1ae8(U,H);m=pd.DataFrame(A.values,index=A.index,columns=[_A1]);m[_A2]=F;c=A.values-F;n=range(len(c));V,O=plt.subplots(figsize=(8,5));O.scatter(n,c,color=_O,alpha=.6);O.axhline(0,color=_P,linestyle=_F);O.set_title(_AH);O.set_xlabel(_H);O.set_ylabel(_g);V.tight_layout();V=sparta_1824ab1ae8(V,H);A0=pd.DataFrame(c,index=n,columns=[_f]);W,P=plt.subplots(figsize=(6,6));P.scatter(A,F,alpha=.7);P.plot([min(A),max(A)],[min(A),max(A)],color=_P,linestyle=_F);P.set_title(_AI);P.set_xlabel(_G);P.set_ylabel(_V);W.tight_layout();W=sparta_1824ab1ae8(W,H);A1=M.feature_importances_;o=pd.DataFrame({_J:C,_M:A1}).sort_values(by=_M,ascending=_A);d,Q=plt.subplots(figsize=(6,4));Q.barh(o[_J],o[_M]);Q.set_title(_AW);Q.invert_yaxis();d=sparta_1824ab1ae8(d,H);e,Q=plt.subplots(figsize=(12,6));u.from_estimator(M,B,features=C,ax=Q);e=sparta_1824ab1ae8(e,H);return{_K:1,_m:z,_l:S,_w:sparta_0433db98e0(U),_x:sparta_0433db98e0(V),_A3:sparta_0433db98e0(W),_AL:sparta_0433db98e0(d),_AM:sparta_0433db98e0(e),_b:A0.to_json(orient=_C),_h:m.to_json(orient=_C),_AN:N.to_json(orient=_C),_A4:sparta_0433db98e0(b)}
def sparta_c8a32aa802(df,y_target,x_cols,n_estimators=100,max_depth=_E,in_sample=_A,standardize=_B,test_size=.2,B_DARK_THEME=_A):
	Q=standardize;D=x_cols;from sklearn.preprocessing import StandardScaler as R;from sklearn.ensemble import RandomForestRegressor as U;from sklearn.tree import DecisionTreeRegressor,export_text;from sklearn.metrics import r2_score as V,mean_squared_error as W,mean_absolute_error as X;from sklearn.model_selection import train_test_split as Y;from sklearn.tree import plot_tree;from sklearn.inspection import PartialDependenceDisplay;from sklearn.model_selection import GridSearchCV as Z;from math import sqrt;a=df[y_target];K=a;df=df[D].dropna();L=df;S=42;A,B,E,C=Y(L,K,test_size=test_size,random_state=S)
	if in_sample:
		A,B,E,C=L.astype(float),L.astype(float),K.astype(float),K.astype(float);E=E.astype(float);C=C.astype(float)
		if Q:F=R();M=F.fit_transform(A);N=F.transform(B);A=pd.DataFrame(M,columns=D,index=E.index);B=pd.DataFrame(N,columns=D,index=C.index)
		else:A=A.astype(float);B=B.astype(float);A=pd.DataFrame(A.values,columns=D,index=E.index);B=pd.DataFrame(B.values,columns=D,index=C.index)
	elif Q:F=R();M=F.fit_transform(A);N=F.transform(B);A=pd.DataFrame(M,columns=D,index=E.index);B=pd.DataFrame(N,columns=D,index=C.index)
	else:A=A.astype(float);B=B.astype(float);A=pd.DataFrame(A.values,columns=D,index=E.index);B=pd.DataFrame(B.values,columns=D,index=C.index)
	b={_i:list(range(2,11))+[_E]};c=U(random_state=S);H=Z(c,b,cv=5,scoring=_AO,n_jobs=-1);H.fit(A,E);d=H.best_estimator_;T=H.best_params_[_i];O=d.predict(B);e=V(C,O);f=sqrt(W(C,O));g=X(C,O);h={_Z:round(e,4),_R:round(f,4),_U:round(g,4),_AP:T};I=pd.DataFrame(H.cv_results_);J,G=plt.subplots();G.plot(I[_y],-I[_z],marker='o');G.set_title(_AQ);G.set_xlabel(_i);G.set_ylabel(_AR);G.grid(_B);J.tight_layout();J=sparta_1824ab1ae8(J,B_DARK_THEME);P=-I[_z].to_frame();P.index=I[_y].values;P.columns=[_AS];return{_K:1,_AT:T,_AU:sparta_0433db98e0(J),_AV:P.to_json(orient=_C)}
def sparta_94fbcebb11(df,y_target,x_cols,quantiles,standardize=_B,in_sample=_B,test_size=.2,B_DARK_THEME=_A):
	l='const';a=B_DARK_THEME;Z=standardize;Y=y_target;K=x_cols;I=quantiles;import statsmodels.api as J;from sklearn.model_selection import train_test_split as m;from sklearn.preprocessing import StandardScaler as b;from sklearn.metrics import mean_absolute_error;from math import sqrt;import matplotlib.pyplot as c;I=[float(A)for A in I];n=df[Y];Q=n;df=df[K].dropna();R=df
	if in_sample:
		F,B,G,C=R.astype(float),R.astype(float),Q.astype(float),Q.astype(float);G=G.astype(float);C=C.astype(float)
		if Z:M=b();S=M.fit_transform(F);T=M.transform(B);F=pd.DataFrame(S,columns=K,index=F.index);B=pd.DataFrame(T,columns=K,index=B.index)
		P=J.add_constant(F).astype(float);U=J.add_constant(B).astype(float);N={A:J.QuantReg(G,P).fit(q=A)for A in I};O={A:B.predict(U)for(A,B)in N.items()}
	else:
		F,B,G,C=m(R,Q,test_size=test_size,random_state=42)
		if Z:M=b();S=M.fit_transform(F);T=M.transform(B);F=pd.DataFrame(S,columns=K,index=F.index);B=pd.DataFrame(T,columns=K,index=B.index)
		else:F=F.astype(float);B=B.astype(float);G=G.astype(float);C=C.astype(float)
		P=J.add_constant(F).astype(float);U=J.add_constant(B).astype(float);G=G.astype(float);C=C.astype(float);N={A:J.QuantReg(G,P).fit(q=A)for A in I};O={A:B.predict(U)for(A,B)in N.items()}
	V,D=c.subplots(figsize=(8,5));L=K[0];d=B[L];D.scatter(d,C,color=_c,alpha=.4,label=_G);H=pd.DataFrame({L:d,_G:C});e=dict();f=dict();g=dict()
	for A in I:
		E=O[A]
		if not isinstance(E,pd.Series):E=pd.Series(E,index=B.index)
		H[f"Quantile_{A}"]=E;o=J.QuantReg(G,P);h=o.fit(q=A);N[A]=h;e[A]=h.summary().as_html();p=round(((C-O[A])**2).mean()**.5,4);q=round((C-O[A]).abs().mean(),4);f[A]=f"<b>Quantile {A}:</b><br>RMSE = <span class='whiteLabel' style='font-weight:bold'>{p}</span><br>MAE = <span class='whiteLabel' style='font-weight:bold'>{q}</span><br><br>";r=N[A];W=r.params;s=[f"{round(W[A],4)} × {A}"for A in W.index if A!=l];t=round(W[l],4);u=f"y = {t} + "+' + '.join(s);g[A]=u
	H=H.sort_values(by=L)
	for A in I:D.plot(H[L],H[f"Quantile_{A}"],label=f"Quantile {A}",linewidth=2)
	i=sorted(I);D.set_xlabel(L);D.set_ylabel(Y);D.set_title('Quantile Regression Trendlines');D.legend();D.fill_between(H[L],H[f"Quantile_{str(i[0])}"],H[f"Quantile_{str(i[-1])}"],color='blue',alpha=.2,label='Prediction Interval (10%-90%)');V=sparta_1824ab1ae8(V,a);X,D=c.subplots(figsize=(8,5));j=pd.DataFrame()
	for A in I:
		E=O[A]
		if not isinstance(E,pd.Series):E=pd.Series(E,index=B.index)
		E=E.loc[C.index];k=C-E;j[f"Quantile {A}"]=k;print(f"len pred_q > {A}");print(len(E));D.scatter(C.index,k,label=f"Quantile {A}",alpha=.5)
	D.axhline(0,color=_P,linestyle=_F);D.set_title('Residuals by Quantile');D.set_xlabel(_H);D.set_ylabel('Residual (Actual - Predicted)');D.legend();X=sparta_1824ab1ae8(X,a);return{_K:1,'fig64':sparta_0433db98e0(V),'summaries':e,'narratives':f,_AX:sparta_0433db98e0(X),'regression_formulas':g,'quantiles_json':H.to_json(orient=_C),_b:j.to_json(orient=_C)}
def sparta_ade8cd9af4(df,y_target,x_cols,window=60,standardize=_B,test_size=.2,B_DARK_THEME=_A):
	U=y_target;M=B_DARK_THEME;L=window;K=x_cols;B=df;from statsmodels.regression.rolling import RollingOLS as c;import statsmodels.api as V,pandas as N,matplotlib.pyplot as O;from sklearn.metrics import mean_absolute_error as d,mean_squared_error;from sklearn.linear_model import LinearRegression;from math import sqrt;H=B[U].astype(float);E=B[K].astype(float)
	if standardize:from sklearn.preprocessing import StandardScaler as e;f=e();E=N.DataFrame(f.fit_transform(E),columns=K,index=E.index)
	W=V.add_constant(E);g=c(endog=H,exog=W,window=L);F=g.fit();h=W.loc[F.params.index];C=(F.params*h).sum(axis=1);A=H[C.index];X=A-C;i=sqrt(((A-C)**2).mean());j=d(A,C);k=E.iloc[[-1]];P=V.add_constant(k,has_constant='add');P=P[F.params.columns];l=F.params.iloc[-1];m=(P.iloc[0]*l).sum();Y=B.index[-1];n=B.index[-2];o=Y-n;s=[Y+o];p=f"RollingOLS (window={L}) estimates changing linear relationships between {K} and {U} over time. The model achieved:<br><span class='whiteLabel' style='font-weight:bold'>RMSE of {round(i,4)}</span><br><span class='whiteLabel' style='font-weight:bold'>MAE of {round(j,4)}</span><br> on the fitted rolling predictions.<br>It also performed a final out-of-sample forecast for the next step: {m:.2f}.";Q,I=O.subplots(figsize=(10,5));I.plot(H.index,H,label=_G);Z=C.iloc[L:];I.plot(Z.index,Z.values,linestyle=_F,label=_V);I.set_title('RollingOLS: Actual vs Predicted');I.legend();Q=sparta_1824ab1ae8(Q,M);R,S=O.subplots(figsize=(8,5));S.scatter(A.index,X,alpha=.6);S.axhline(0,color=_P,linestyle=_F);S.set_title('Residuals (RollingOLS)');R=sparta_1824ab1ae8(R,M);q=N.DataFrame({_f:X},index=A.index);r=N.DataFrame({_G:A,_V:C},index=A.index);J=F.params.copy();J.index.name=_H;a={};b={}
	for D in J.columns:T,G=O.subplots(figsize=(8,4));J[D].plot(ax=G,label=D,linewidth=2);G.set_title(f"Rolling Coefficient: {D}");G.set_xlabel(_H if B.index.name is _E else B.index.name);G.set_ylabel('Coefficient Value');G.legend();T=sparta_1824ab1ae8(T,M);a[D]=sparta_0433db98e0(T);b[D]=J[D].to_json(orient=_C)
	return{_K:1,_m:p,'fig64':sparta_0433db98e0(Q),_AX:sparta_0433db98e0(R),_h:r.to_json(orient=_C),_b:q.to_json(orient=_C),'rolling_charts':a,'rolling_coeff_dict':b}
def sparta_752f5aa77e(df,y_target,x_cols,standardize=_B,B_DARK_THEME=_A):
	X=standardize;N=B_DARK_THEME;M=y_target;F=x_cols;D=df;import pandas as E,matplotlib.pyplot as O,statsmodels.api as Y;from sklearn.preprocessing import StandardScaler as i;from sklearn.model_selection import train_test_split;from sklearn.metrics import mean_absolute_error as j,mean_squared_error as k;from math import sqrt;r={};D=D[[M]+F].dropna().copy()
	for B in[M]+F:D[B]=E.to_numeric(D[B],errors=_N)
	D=D.dropna();Z=D[F].astype(float);a=D[M].astype(float);J,P,K,C=Z.astype(float),Z.astype(float),a.astype(float),a.astype(float);K=K.astype(float);C=C.astype(float)
	if X:b=i();l=b.fit_transform(J);m=b.transform(P);J=E.DataFrame(l,columns=F,index=J.index);P=E.DataFrame(m,columns=F,index=P.index)
	H=Y.add_constant(J).astype(float);c=Y.RecursiveLS(endog=K,exog=H);d=c.fit();n=d.recursive_coefficients.filtered;Q=d.plot_recursive_coefficient(range(c.k_exog),alpha=_E,figsize=(10,6));G=E.DataFrame(n).T;G.columns=H.columns;G.index=H.index;A=K.to_frame();A.columns=[_G];A[_I]=0
	for B in H.columns:A[_I]+=(G[B]*H[B]).astype(float)
	e=A[_I];I=A[_G]-A[_I];f=I.to_frame();I.columns=[_f];o=sqrt(k(A[_G],A[_I]));p=j(A[_G],A[_I]);R={_R:round(o,4),_U:round(p,4)};q=f"Recursive Least Squares regression using features <span class='whiteLabel' style='font-weight:bold'>{F}</span> {_u if X else _v} standardization achieved:<br><span class='whiteLabel' style='font-weight:bold'>RMSE of {R[_R]}</span><br><span class='whiteLabel' style='font-weight:bold'>MAE of {R[_U]}</span><br>on the <span style='text-decoration:underline'>full set</span>.";S,L=O.subplots(figsize=(10,5));L.plot(C.index,C.values,label=_G);L.plot(C.index,e,label=_V,linestyle=_F,color=_Y);L.set_title('RecursiveLS: Actual vs Predicted');L.legend();S=sparta_1824ab1ae8(S,N);T,U=O.subplots(figsize=(8,4));U.scatter(C.index,I,alpha=.6,color=_O);U.axhline(0,linestyle=_F,color=_P);U.set_title('Residuals (RecursiveLS)');T=sparta_1824ab1ae8(T,N);g={};Q={}
	for(s,B)in enumerate(list(G.columns)):h=E.Series(G[B],index=G.index);g[B]=h.to_json(orient=_C);V,W=O.subplots(figsize=(10,4));h.plot(ax=W,label=f"{B} (Recursive)");W.set_title(f"Recursive Coefficient for {B}");W.legend();V=sparta_1824ab1ae8(V,N);Q[B]=sparta_0433db98e0(V)
	A=E.DataFrame({_G:C,_V:e},index=C.index);f=E.DataFrame({_g:I},index=C.index);return{_K:1,_m:q,_l:R,_w:sparta_0433db98e0(S),_x:sparta_0433db98e0(T),_b:I.to_json(orient=_C),_h:A.to_json(orient=_C),_b:f.to_json(orient=_C),'recursive_coeffs_json':g,'recursive_coeffs_figs':Q}
def sparta_73671afc70(importance_df,top_n=_E):
	E='Percent';B=top_n;A=importance_df
	if A.empty:return'No feature importance data is available.'
	if B is _E:B=len(A)
	B=min(B,len(A));F=A[_M].sum();A=A.copy();A[E]=A[_M]/F*100;G=A.head(B);C=[]
	for(K,D)in G.iterrows():H=D[_J];I=D[E];C.append(f"• <span class='pageNavTitle whiteLabel'>{H}</span> contributes approximately <span style='color:red'>{I:.1f}%</span> of the total importance.")
	J=f"Among all input features, the most influential {B} are:<br>"+'<br>'.join(C);return J
def sparta_3a4046558b(df,y_target,x_cols,n_estimators=100,max_depth=_E,min_samples_split=2,min_samples_leaf=1,max_features='sqrt',bootstrap=_B,B_DARK_THEME=_A):
	F=.0;E=max_depth;A=df;from sklearn.ensemble import RandomForestRegressor as I,RandomForestClassifier;from sklearn.preprocessing import StandardScaler as J;K=A[y_target];A=A[x_cols].dropna();L=J();M=L.fit_transform(A)
	if E==-1:E=_E
	G=I(n_estimators=n_estimators,criterion='squared_error',max_depth=E,min_samples_split=min_samples_split,min_samples_leaf=min_samples_leaf,min_weight_fraction_leaf=F,max_features=max_features,max_leaf_nodes=_E,min_impurity_decrease=F,bootstrap=bootstrap,oob_score=_A,n_jobs=_E,random_state=_E,verbose=0,warm_start=_A,ccp_alpha=F,max_samples=_E);G.fit(M,K);N=G.feature_importances_;O=A.columns;B=pd.DataFrame({_J:O,_M:N}).sort_values(by=_M,ascending=_A);C,D=plt.subplots(figsize=(8,6));D.barh(B[_J],B[_M],color=_t);D.set_xlabel(_M);D.set_title(_AW);D.invert_yaxis();C.tight_layout();C=sparta_1824ab1ae8(C,B_DARK_THEME);H=''
	try:H=sparta_73671afc70(B)
	except:pass
	return{_K:1,_AY:sparta_0433db98e0(C),'summary':H,'importance_json':B.to_json(orient=_C)}
def sparta_9063bce3ba(df,y_target,x_cols,B_DARK_THEME=_A):
	A=df;from sklearn.preprocessing import StandardScaler as G;from xgboost import XGBClassifier as H;I=A[y_target];A=A[x_cols].dropna();J=G();K=J.fit_transform(A);E=H(use_label_encoder=_A,eval_metric='mlogloss',random_state=42);E.fit(K,I);L=E.feature_importances_;D=pd.DataFrame({_J:A.columns,_M:L}).sort_values(by=_M,ascending=_A);B,C=plt.subplots(figsize=(8,6));C.barh(D[_J],D[_M],color='lightgreen');C.set_xlabel(_M);C.set_title('Feature Importance (XGBoost)');C.invert_yaxis();B.tight_layout();B=sparta_1824ab1ae8(B,B_DARK_THEME);F=''
	try:F=sparta_73671afc70(D)
	except:pass
	return{_K:1,_AY:sparta_0433db98e0(B),'summary':F}
def sparta_c9339c3718(df,y_target,x_cols,B_DARK_THEME=_A):
	O='Mutual Information';L=B_DARK_THEME;K=y_target;J='MI Score';C=df;B=x_cols;from sklearn.feature_selection import mutual_info_regression as P;T=C[B+[K]].corr()[K][B];U=C[K];C=C[B].dropna();V=C.astype(float);W=U.astype(float);Q=P(V,W,random_state=42);E=pd.DataFrame({_J:B,J:Q});E.sort_values(J,ascending=_B,inplace=_B);F,A=plt.subplots(figsize=(7,5));A.barh(E[_J],E[J],color='royalblue',alpha=.8);A.set_title('Mutual Information Scores',fontsize=14);A.set_xlabel(J,fontsize=12);A.set_ylabel(_J,fontsize=12);A.grid(_B,linestyle=_F,alpha=.5);F.tight_layout();F=sparta_1824ab1ae8(F,L);D=pd.DataFrame(index=B,columns=B)
	for R in B:
		for S in B:X=P(C[[R]],C[S])[0];D.loc[R,S]=X
	D=D.astype(float);M,A=plt.subplots(figsize=(8,6));sns.heatmap(D,annot=_B,cmap=_p,center=0,linewidths=.5,linecolor=_c,ax=A);A.set_title('Heatmap of Mutual Information');plt.tight_layout();M=sparta_1824ab1ae8(M,L);G=pd.DataFrame({_J:B,_r:T.values,O:Q});H,A=plt.subplots(figsize=(10,5));N=range(len(B));I=.4;A.bar([A-I/2 for A in N],G[_r],width=I,label=_r,color=_t);A.bar([A+I/2 for A in N],G[O],width=I,label=O,color=_Y);A.set_xticks(N);A.set_xticklabels(G[_J],rotation=45);A.set_title('Comparison: Correlation vs Mutual Information');A.set_ylabel('Score');A.legend();A.grid(_B,linestyle=_F,alpha=.5);H.tight_layout();H=sparta_1824ab1ae8(H,L);return{_K:1,'mi64':sparta_0433db98e0(F),'heatmap64':sparta_0433db98e0(M),'compCorre64':sparta_0433db98e0(H),'mi_json':E.to_json(orient=_C),'mi_matrix_json':D.to_json(orient=_C),'corr_comp_json':G.to_json(orient=_C)}