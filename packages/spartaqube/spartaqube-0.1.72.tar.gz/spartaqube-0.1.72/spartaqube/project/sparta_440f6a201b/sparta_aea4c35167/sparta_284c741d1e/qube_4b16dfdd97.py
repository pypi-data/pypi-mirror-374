_F='from spartaqube import Spartaqube as Spartaqube'
_E='Example to display a quant report using QuantStats'
_D='code'
_C='sub_description'
_B='description'
_A='title'
import json
from django.conf import settings as conf_settings
def sparta_2cde16b54a():A=_F;type='notebook';return[{_A:f"{type.capitalize()}",_B:'Example to display a python Notebook',_C:'',_D:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  height=500
)
plot_example"""}]
def sparta_8c3f7829e5():A=_F;B="{'reportType': 1}";C="{'reportType': 2}";D="{'reportType': 3}";type='quantstats';return[{_A:f"{type.capitalize()} basic report",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} metrics report",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  options={B},
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} plots report",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  options={C},
  height=500
)
plot_example"""},{_A:f"{type.capitalize()} drawdowns report",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  y=apple_price_df['Close'], 
  title='Example',
  options={D},
  height=500
)
plot_example"""}]
def sparta_190adb9465():A=_F;type='dataframe';return[{_A:f"{type.capitalize()}",_B:_E,_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=apple_price_df.index,
  dataframe=apple_price_df, 
  title='Example',
  height=500
)
plot_example"""}]
def sparta_7ca95b66b0():A=_F;type='summary_statistics';return[{_A:f"{type.capitalize()}",_B:'Summary Statistics Example',_C:'',_D:f"""{A}
import yfinance as yf
spartaqube_obj = Spartaqube()
# Fetch the data for Apple (ticker symbol: AAPL)
apple_price_df = yf.Ticker(\"AAPL\").history(period=\"1y\")
# Plot example
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  y=[apple_price_df['Close'], apple_price_df['Volume']], 
  title='Example',
  height=500
)
plot_example"""}]