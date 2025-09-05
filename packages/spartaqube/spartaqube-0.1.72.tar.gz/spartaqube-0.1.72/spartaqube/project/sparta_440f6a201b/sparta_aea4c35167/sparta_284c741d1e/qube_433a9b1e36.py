_F='Example to run a simple linear regression'
_E='code'
_D='sub_description'
_C='description'
_B='title'
_A='from spartaqube import Spartaqube as Spartaqube'
def sparta_3fb8863cc0():A=_A;type='STL';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='stl',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_8088e5545f():A=_A;type='Wavelet';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='wavelet',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_ecc98e4425():A=_A;type='HMM';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='hmm',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_1ca7258d04():A=_A;type='CUSUM';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='cusum',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_72252ef1f8():A=_A;type='Ruptures';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='ruptures',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_23257d06b8():A=_A;type='Z-score';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='zscore',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_a8e1b55e83():A=_A;type='Prophet Outlier';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='prophet_outlier',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_788ac72c91():A=_A;type='Isolation Forest';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='isolation_forest',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_b69772cb21():A=_A;type='MAD';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='mad',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7239689627():A=_A;type='SARIMA';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='sarima',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_35bc9f367e():A=_A;type='ETS';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='ets',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_ee64011eb1():A=_A;type='Prophet Forecast';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='prophet_forecast',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_bb7090b182():A=_A;type='VAR';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
data_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='var',
  x=data_df.index,
  y=[data_df['Close'], data_df['Volume']],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_c65f9f8821():A=_A;type='ADF Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='adf_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_046f6d49e3():A=_A;type='KPSS Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='kpss_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_6ba7954175():A=_A;type='Perron Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='perron_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_8ecefb32a8():A=_A;type='Zivot-Andrews Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='zivot_andrews_test',
  x=apple_price_df.index,
  y=apple_price_df['Close'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_173e9e189b():A=_A;type='Granger Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='granger_test',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_dbc248f7d3():A=_A;type='Cointegration Test';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
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
  chart_type='cointegration_test',
  x=data_df['SPX'],
  y=data_df['AAPL'],
  title='Example',
  height=500
)
plot_example"""}]
def sparta_78d1dc6bd0():A=_A;type='Canonical Correlation';return[{_B:f"{type.capitalize()}",_C:_F,_D:'',_E:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
data_df = yf.Ticker(\"AAPL\").history(period=\"1y\")

# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='canonical_corr',
  x=[data_df['Close'], data_df['Open']],
  y=[data_df['High'], data_df['Volume']],
  title='Example',
  height=500
)
plot_example"""}]