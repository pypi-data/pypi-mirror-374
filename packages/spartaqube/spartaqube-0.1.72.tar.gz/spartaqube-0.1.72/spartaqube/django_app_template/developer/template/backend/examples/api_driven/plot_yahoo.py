def sparta_b5b8332b5e(post_data):
    """
    This function returns an image (base64) that corresponds to a stock price from YahooFinance
    """
    import yfinance as yf
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    import base64
    ticker = post_data['ticker']
    apple_stock = yf.Ticker(ticker)
    current_price = apple_stock.history(period='1y')
    plt.figure(figsize=(10, 5))
    plt.plot(current_price.index, current_price['Close'], label=
        f'{ticker} Closing Price', color='blue')
    plt.title(f'{ticker} Stock Price (Last 1 Year)')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close()
    return {'res': 1, 'output': img_base64}

#END OF QUBE
