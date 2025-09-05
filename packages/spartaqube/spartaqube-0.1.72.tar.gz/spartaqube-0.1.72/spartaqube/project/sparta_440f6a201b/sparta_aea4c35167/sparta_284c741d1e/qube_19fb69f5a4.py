_R='year: y, month: M, day: d, quarter: QQQ, week: w, hour: HH, minute: MM, seconds: SS, millisecond: ms'
_Q='Example to plot a simple time series with datalabels using chartJS'
_P='Example to plot a simple time series with custom title using chartJS'
_O='f"label-{round(price,2)}"'
_N='f"title-{round(price,2)}"'
_M='12px'
_L='center'
_K='blue'
_J='font-size'
_I='text-align'
_H='color'
_G='Example to plot a two time series using chartJS'
_F='from spartaqube import Spartaqube as Spartaqube'
_E='Example to plot a simple time series using chartJS'
_D='code'
_C='sub_description'
_B='description'
_A='title'
import json
from django.conf import settings as conf_settings
def sparta_852c623f9f(type='line'):A=_F;B={_H:_K,_I:_L,_J:_M};C=_N;D=_O;return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Two {type}s with legend",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""},{_A:f"Two stacked {type}s",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""},{_A:f"Simple {type} with title",_B:_P,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(B)},
  height=500
)
plot_example"""},{_A:f"Simple {type} with datalabels",_B:_Q,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with conditional colors",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
apple_price_df['vol_colors'] = 'red'
apple_price_df.loc[apple_price_df['Volume'] > apple_price_df['Volume'].mean(), 'vol_colors'] = 'green'
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  border=apple_price_df['vol_colors'].tolist(), 
  background=apple_price_df['vol_colors'],
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with tooltips",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  tooltips_title=[{C} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{D} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with date formatting",_B:_E,_C:_R,_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  date_format='yyyy-MM-dd',
  labels=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with time range",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""}]
def sparta_e2465e6cec():return sparta_852c623f9f(type='line')
def sparta_d26b3a4d02():return sparta_852c623f9f(type='bar')
def sparta_df6b06092e():return sparta_852c623f9f(type='scatter')
def sparta_7093349ed4():A=_F;type='area';B={_H:_K,_I:_L,_J:_M};C=_N;D=_O;return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Two {type}s with legend",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""},{_A:f"Two stacked {type}s",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""},{_A:f"Simple {type} with title",_B:_P,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(B)},
  height=500
)
plot_example"""},{_A:f"Simple {type} with datalabels",_B:_Q,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with tooltips",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  tooltips_title=[{C} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{D} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with date formatting",_B:_E,_C:_R,_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  date_format='yyyy-MM-dd',
  labels=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with time range",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""}]
def sparta_fd86b4f2c5(type='pie'):A=_F;D={_H:_K,_I:_L,_J:_M};B='{\n    "datasets": [\n        {\n            "datalabels": {\n                "display": True,\n                "color": "red",\n                "font": {\n                    "family": "Azonix",\n                    "size": 20,\n                }\n            },\n        }\n    ]\n  }';C='{\n    "datasets": [\n        {\n            "backgroundColor": [\'red\', \'blue\', \'green\'],\n            "borderColor": [\'red\', \'blue\', \'green\'],\n        }\n    ]\n  }';return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with labels",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20],
  datalabels=['group 1', 'group 2', 'group 3'],
  height=500
)
plot_example"""},{_A:f"Simple {type} with custom labels",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20],
  options={B},
  height=500
)
plot_example"""},{_A:f"Simple {type} with custom colors",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=[1,2,3], 
  y=[20,60,20],
  options={C},
  height=500
)
plot_example"""}]
def sparta_a902341768():return sparta_fd86b4f2c5(type='donut')
def sparta_db0528be8f():return sparta_fd86b4f2c5(type='polar')
def sparta_066d132343():type='bubble';A=_F;B={_H:_K,_I:_L,_J:_M};C=_N;D=_O;return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with radius",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  r=apple_price_df['Volume'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Two {type}s with legend",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""},{_A:f"Two stacked {type}s",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""},{_A:f"Simple {type} with title",_B:_P,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(B)},
  height=500
)
plot_example"""},{_A:f"Simple {type} with datalabels",_B:_Q,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with conditional colors",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
apple_price_df['vol_colors'] = 'red'
apple_price_df.loc[apple_price_df['Volume'] > apple_price_df['Volume'].mean(), 'vol_colors'] = 'green'
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  r=apple_price_df['Volume'], 
  border=apple_price_df['vol_colors'].tolist(), 
  background=apple_price_df['vol_colors'],
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with tooltips",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  r=apple_price_df['Volume'], 
  tooltips_title=[{C} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{D} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple {type} with date formatting",_B:_E,_C:_R,_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  r=apple_price_df['Volume'], 
  date_format='yyyy-MM-dd',
  labels=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with time range",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  r=apple_price_df['Volume'], 
  title='Example {type}',
  time_range=True,
  height=500
)
plot_example"""}]
def sparta_ea26775560():A=_F;B={_H:_K,_I:_L,_J:_M};C=_N;D=_O;type='barH';return[{_A:f"Simple horizontal bar",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Two horizontal bars with legend",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  legend=['High', 'Low'], 
  height=500
)
plot_example"""},{_A:f"Two stacked horizontal bars",_B:_G,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=[
      apple_price_df['High'], 
      apple_price_df['Low']
  ], 
  stacked=True,
  height=500
)
plot_example"""},{_A:f"Simple horizontal bar with title",_B:_P,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  legend=['AAPL'], 
  title='Apple Close Prices', 
  title_css={json.dumps(B)},
  height=500
)
plot_example"""},{_A:f"Simple horizontal bar with datalabels",_B:_Q,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'], 
  datalabels=apple_price_df['Close'],
  legend=['AAPL'], 
  height=500
)
plot_example"""},{_A:f"Simple horizontal bar with tooltips",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}', 
  x=apple_price_df.index, 
  y=apple_price_df['Close'],
  tooltips_title=[{C} for price in apple_price_df['Close'].tolist()],
  tooltips_label=[{D} for price in apple_price_df['Close'].tolist()],
  labels=['AAPL'], 
  height=500
)
plot_example"""}]
def sparta_3238ce7b7e():A=_F;type='radar';C={_H:_K,_I:_L,_J:_M};D=_N;E=_O;B='{\n    "datasets": [\n        {\n            "tension": 0\n        }\n    ]\n  }';return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f'''{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type=\'{type}\',
  x=["A", "B", "C", "D", "E", "F", "G"], 
  y=[65, 59, 90, 81, 56, 55, 40], 
  height=500
)
plot_example'''},{_A:f"Simple {type} with custom tension",_B:_E,_C:'',_D:f'''{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type=\'{type}\',
  x=["A", "B", "C", "D", "E", "F", "G"], 
  y=[65, 59, 90, 81, 56, 55, 40], 
  options={B},
  height=500
)
plot_example'''}]
def sparta_fc4e87d276():A=_F;type='mixed';B='{\n    "datasets": [\n        {\n            "type": \'bar\',\n        },\n        {\n            "type": \'line\',\n        }\n    ]\n  }';return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index, 
  y=[apple_price_df['Close'], apple_price_df['High']], 
  option={B}, 
  height=500
)
plot_example"""}]
def sparta_2b956b8309():A=_F;type='histogram';return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
apple_ret_df = apple_price_df[['Close']].pct_change().dropna()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  y=apple_ret_df['Close'], 
  height=500
)
plot_example"""}]
def sparta_11569e12d1():A=_F;type='matrix';B="{'AAPL': apple_ret_df['Close'], 'NVDA': nvda_ret_df['Close'], 'TSLA': tsla_ret_df['Close']}";C='{\n    \'options\': {\n        "gradientColors": {\n            "bGradientMatrix": True,\n            "gradientStart": "#20ff86ff",\n            "gradientMiddle": "#f8e61cff",\n            "gradientEnd": "#ff0000ff",\n            "gradientFixedBorderColor": False,\n            "gradientBorderColor": "#ffffffff",\n            "gradientBorderWidth": 1,\n            "bDisplayHeatbar": True,\n            "heatBarPosition": "Right",\n            "bMiddleColor": True,\n        },\n    }\n  }';return[{_A:f"Simple {type}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
apple_ret_df = apple_price_df.pct_change().iloc[-10:]
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_ret_df.index, 
  y=apple_ret_df['Close'],
  date_format='yyyy-MM-dd',
  height=500
)
plot_example"""},{_A:f"Correlation matrix example",_B:'Example to plot a simple correlation matrix using chartJS',_C:'',_D:f'''{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker("AAPL").history(period="1y")
apple_ret_df = apple_price_df.pct_change()
nvda_price_df = yf.Ticker("NVDA").history(period="1y")
nvda_ret_df = nvda_price_df.pct_change()
tsla_price_df = yf.Ticker("TSLA").history(period="1y")
tsla_ret_df = tsla_price_df.pct_change()
df = pd.DataFrame({B})
# Compute the correlation matrix
correlation_matrix = df.corr()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type=\'{type}\',
  x=correlation_matrix.index, 
  y=[correlation_matrix[\'AAPL\'], correlation_matrix[\'NVDA\'], correlation_matrix[\'TSLA\']],
  options={C},
  height=500
)
plot_example'''}]