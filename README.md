# IQFeed Downloader

Python scripts created to use with DTN IQFeed Market Data application. Connect to IQFeed socket, download historical data or start a live flow of prices for desired ticker.


## How to use?

1. Clone the repository or download both files.
2. Log into any IQFeed application and have it running in the background - make sure you've bought the data plan that contains desired ticker. 
3. Run the script.


## Running the script

There are two ways of running the script and here are the examples:
- historical data access
```
python iqfeed_downloader historical 127.0.0.1 9100 20210201 20210220 1 TLRY GME
```
- live data access
```
python iqfeed_downloader live 127.0.0.1 5009 AMC
```

### Historical access

As in example you have the specify that you want to obtain the historical data, hence "historical", after you put the ip address and port, then start and end date followed by the list of tickers (stock names) you want to download.

If you run the IQFeed app on your PC then the socket address is **localhost** on port **9100**, else you have to use the proxy address.

Date has to be in **YYYYMMDD** format.

As return the script saves CSV file with name: **TICKER_STARTDATE_ENDDATE_INTERVAL.CSV**

### Live access

You only have to feed it three things: host address, host port and ticker name. In return it prints live tick data of desired stock until interrupted.

Default port of IQFeed live data socket is **5009**.



