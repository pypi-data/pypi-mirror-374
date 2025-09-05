_M='{\n        "showTicks": True,\n        "renderTicks": {\n            "showTicks": True,\n            "divisions": 10,\n        },\n    }'
_L='Example to plot a simple shaded background chart with lightweight chart'
_K='12px'
_J='center'
_I='blue'
_H='font-size'
_G='text-align'
_F='color'
_E='from spartaqube import Spartaqube as Spartaqube'
_D='code'
_C='sub_description'
_B='description'
_A='title'
import json
from django.conf import settings as conf_settings
def sparta_66fb26bc63(type='candlestick'):B='Example to plot a simple candlestick chart with lightweight chart';A=_E;C={_F:_I,_G:_J,_H:_K};D=_M;return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  ohlcv=[apple_price_df['Open'], apple_price_df['High'], apple_price_df['Low'], apple_price_df['Close']], 
  title='Example candlestick',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with volumes",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  ohlcv=[apple_price_df['Open'], apple_price_df['High'], apple_price_df['Low'], apple_price_df['Close'], apple_price_df['Volume']], 
  title='Example candlestick',
  height=500
)
plot_example"""}]
def sparta_852c623f9f(type='line2'):A=_E;B={_F:_I,_G:_J,_H:_K};C=_M;return[{_A:f"{type.capitalize()}",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
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
  height=500
)
plot_example"""},{_A:f"{type} two lines",_B:f"Example to plot multiple {type}s with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df[['Close', 'Open']], 
  title='Example {type}',
  height=500
)
plot_example"""},{_A:f"{type} two lines stacked",_B:f"Example to plot multiple {type}s with lightweight chart",_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df[['Close', 'Open']],
  stacked=True,
  title='Example {type}',
  height=500
)
plot_example"""},{_A:f"{type} with time range",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
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
def sparta_3f7542f966():return sparta_852c623f9f('ts_line')
def sparta_f61b22ca0f():return sparta_852c623f9f('ts_bar')
def sparta_157e31fc90():return sparta_852c623f9f('ts_area')
def sparta_090c017626():return sparta_852c623f9f('ts_lollipop')
def sparta_f574ec7407():B='Example to plot a simple baseline chart with lightweight chart';A=_E;D={_F:_I,_G:_J,_H:_K};C='{\n    "baseline": [\n      \t{\n          "defaultBaselinePrice": 200,\n        },\n    ]\n    }';type='ts_baseline';return[{_A:f"{type.capitalize()}",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example baseline',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom baseline",_B:B,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example baseline',
  options={C},
  height=500
)
plot_example"""}]
def sparta_fb0bfc78e9():A=_E;C={_F:_I,_G:_J,_H:_K};B='{\n        "shadedBackground": {\n            "lowColor": "rgb(50, 50, 255)",\n            "highColor": "rgb(255, 50, 50)",\n            "opacity": 0.8,\n        },\n    }';type='ts_shaded';return[{_A:f"{type.capitalize()}",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  shaded_background=apple_price_df['Close'], 
  title='Example',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom colors",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  shaded_background=apple_price_df['Close'], 
  title='Example',
  options={B},
  height=500
)
plot_example"""}]
def sparta_3ab72e240f():A=_E;B={_F:_I,_G:_J,_H:_K};C=_M;type='performance';return[{_A:f"{type.capitalize()}",_B:f"Example to plot a simple {type} chart with lightweight chart",_C:'',_D:f"""{A}
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
  height=500
)
plot_example"""}]
def sparta_c61d069173():A=_E;C={_F:_I,_G:_J,_H:_K};B='{\n        "areaBands": {\n            "fillColor": "#F5A623",\n            "color": "rgb(19, 40, 153)",\n            "lineColor": "rgb(208, 2, 27)",\n            "lineWidth": 3,\n            "custom_scale_axis": "Right",\n        },\n    }';type='ts_area_bands';return[{_A:f"{type.capitalize()}",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=[apple_price_df['Close'], apple_price_df['High'], apple_price_df['Low']], 
  title='Example',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} with custom colors",_B:_L,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=[apple_price_df['Close'], apple_price_df['High'], apple_price_df['Low']], 
  options={B},
  height=500
)
plot_example"""}]