# import yfinance as yf
# import json

# def test_news():
#     ticker = "AAPL"
#     try:
#         t = yf.Ticker(ticker)
#         news = t.news
#         print(f"Raw news for {ticker}:")
#         print(json.dumps(news, indent=2))
        
#         structured_news = []
#         for item in news:
#             structured_news.append({
#                 "Title": item.get('title'),
#                 "Publisher": item.get('publisher'),
#                 "Link": item.get('link'),
#                 "RelatedTickers": item.get('relatedTickers')
#             })
#         print("\nStructured news:")
#         print(json.dumps(structured_news, indent=2))
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     test_news()
