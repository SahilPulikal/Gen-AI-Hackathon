import yfinance as yf
import pandas as pd

def get_market_data(tickers):
    """
    Fetches real-time market data for a list of tickers.
    Returns a DataFrame with 'Close', 'Change', 'PctChange'.
    """
    if not tickers:
        return pd.DataFrame()
    
    # yfinance expects space-separated string
    tickers_str = " ".join(tickers)
    data = yf.download(tickers_str, period="5d", group_by='ticker', progress=False, auto_adjust=True)
    
    market_summary = []
    
    # Handle single ticker case vs multiple
    if len(tickers) == 1:
        ticker = tickers[0]
        # yf.download for single ticker returns DataFrame with columns like 'Close', 'Open' directly
        # But sometimes it has MultiIndex if group_by='ticker' is used? 
        # Let's use Ticker object for safety or handle the DF structure carefully.
        # Actually, let's just use Ticker object for current price to be safe and fast.
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="5d")
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = current - prev
                pct_change = (change / prev) * 100
                market_summary.append({
                    "Ticker": ticker,
                    "Price": round(current, 2),
                    "Change": round(change, 2),
                    "PctChange": round(pct_change, 2)
                })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            
    else:
        for ticker in tickers:
            try:
                # data[ticker] is a DataFrame
                if ticker in data.columns.levels[0]:
                    df_ticker = data[ticker]
                    if len(df_ticker) >= 2:
                        current = df_ticker['Close'].iloc[-1]
                        prev = df_ticker['Close'].iloc[-2]
                        change = current - prev
                        pct_change = (change / prev) * 100
                        market_summary.append({
                            "Ticker": ticker,
                            "Price": round(current, 2),
                            "Change": round(change, 2),
                            "PctChange": round(pct_change, 2)
                        })
            except Exception as e:
                print(f"Error processing {ticker}: {e}")

    return pd.DataFrame(market_summary)

def get_market_news(ticker):
    """
    Fetches news for a specific ticker.
    """
    try:
        t = yf.Ticker(ticker)
        return t.news
    except:
        return []
