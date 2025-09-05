_E='code'
_D='sub_description'
_C='description'
_B='title'
_A='from spartaqube import Spartaqube as Spartaqube'
import json
from django.conf import settings as conf_settings
def sparta_cbaa9fd832():A=_A;type='dynamicRescale';return[{_B:f"{type.capitalize()}",_C:'An interactive chart that resizes time series from any date, comparing performance metrics in real time',_D:'',_E:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
msft = yf.Ticker('MSFT').history(period=\"24mo\")[['Close']].rename(columns={{'Close': 'MSFT'}})
aapl = yf.Ticker('AAPL').history(period=\"24mo\")[['Close']].rename(columns={{'Close': 'AAPL'}})
nvda = yf.Ticker('NVDA').history(period=\"24mo\")[['Close']].rename(columns={{'Close': 'NVDA'}})
tsla = yf.Ticker('TSLA').history(period=\"24mo\")[['Close']].rename(columns={{'Close': 'TSLA'}})

prices_df = msft
prices_df = prices_df.merge(aapl, left_index=True, right_index=True, how='inner')
prices_df = prices_df.merge(nvda, left_index=True, right_index=True, how='inner')
prices_df = prices_df.merge(tsla, left_index=True, right_index=True, how='inner')
prices_df.columns = ['MSFT', 'AAPL', 'NVDA', 'TSLA']
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  x=prices_df.index,
  y=prices_df,
  height=500
)
plot_example"""}]
def sparta_35070686da():A=_A;type='regression';return[{_B:f"{type.capitalize()}",_C:'Regression Plot: Analyzing Trends and Relationships in Data',_D:'',_E:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
msft = yf.Ticker('MSFT').history(period=\"24mo\")[['Close']].rename(columns={{'Close': 'MSFT'}})
msft_returns = msft.pct_change()
aapl = yf.Ticker('AAPL').history(period=\"24mo\")[['Close']].rename(columns={{'Close': 'AAPL'}})
aapl_returns = aapl.pct_change()
prices_df = msft
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  x=aapl_returns,
  y=msft_returns,
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_00f10e2c8c():A=_A;type='calendar';return[{_B:f"{type.capitalize()}",_C:'Weekday Calendar Heatmap: Mapping Daily Values Across Weeks and Days',_D:'',_E:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
msft = yf.Ticker('MSFT').history(period=\"24mo\")[['Close']].rename(columns={{'Close': 'MSFT'}})
prices_df = msft
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  title=['{type} example'], 
  x=prices_df.index,
  y=prices_df,
  interactive=False,
  height=500
)
plot_example"""}]
def sparta_e31d1704f0():A=_A;type='wordcloud';return[{_B:f"{type.capitalize()}",_C:'Word Cloud: Visualizing Text Data Frequency and Importance',_D:'',_E:f"""{A}
spartaqube_obj = Spartaqube()
# Plot example
import yfinance as yf
wordcloud = ['crypto', 'crypto', 'crypto', 'btc', 'btc', 'eth', 'satoshi', 'sol', 'tech', 'ia', 'ia', 'GPT']
plot_example = spartaqube_obj.plot(
  chart_type='{type}',
  x=wordcloud,
  interactive=False,
  height=500
)
plot_example"""}]