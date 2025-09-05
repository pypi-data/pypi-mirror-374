_F='Example to run a simple linear regression'
_E='code'
_D='sub_description'
_C='description'
_B='title'
_A='from spartaqube import Spartaqube as Spartaqube'
def sparta_40c6c82cb2():A=_A;type='OLS';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='OLS',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_e87feee6a5():A=_A;type='Polynomial Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='PolynomialRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_1974263480():A=_A;type='Decision Tree Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='DecisionTreeRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_6e7906655d():A=_A;type='Random Forest Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='RandomForestRegression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_184005f72b():A=_A;type='Clustering';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='clustering',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_56d259ab97():A=_A;type='Correlation Network';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='correlation_network',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_fce56c39ac():A=_A;type='PCA';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='pca',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_dda1de25f1():A=_A;type='TSNE';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='tsne',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_5ab27b7b0f():A=_A;type='Features importance';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='features_importance',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7cda8d4bcb():A=_A;type='Mutual Information';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='mutual_information',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_61b0c8e93c():A=_A;type='Quantile Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='quantile_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_cb849309b5():A=_A;type='Rolling Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='rolling_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_13484911eb():A=_A;type='Recursive Regression';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for SPX (ticker symbol: ^SPX)
spx_price_df = yf.Ticker(\"^SPX\").history(period=\"1y\")[['Close']]
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")[['Close']]
apple_price_df = apple_price_df.reindex(spx_price_df.index)
data_df = pd.concat([spx_price_df, apple_price_df], axis=1).pct_change().dropna()
data_df.columns = ['SPX', 'AAPL']

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='recursive_regression',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]