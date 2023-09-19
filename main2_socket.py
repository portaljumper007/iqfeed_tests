import iqfeed_downloader
#port info https://doc.stocksharp.com/topics/IQFeedConnect.html


iqfeed_downloader.historical(host="127.0.0.1", port=9100, start_date="20230601", end_date="20230917", interval="1", tickers=["AAPL","MSFT","TLRY","XGV23C1775000"])

#iqfeed_downloader.live(host="127.0.0.1", port=5009, ticker="AAPL")