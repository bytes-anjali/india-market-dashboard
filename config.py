# Stocks to track (NSE symbols)
INDICES = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NIFTY Bank": "^NSEBANK",
    "NIFTY IT": "^CNXIT",
    "NIFTY Midcap 50": "^NSEMDCP50",
}

TOP_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS"
]

# News RSS feeds (Indian markets)
NEWS_FEEDS = [
    "https://economictimes.indiatimes.com/markets/rss.cms",
    "https://www.moneycontrol.com/rss/marketreports.xml",
    "https://feeds.feedburner.com/ndtvprofit-latest",
]

# Google Trends keywords
TREND_KEYWORDS = [
    "Nifty", "Sensex", "NSE", "IPO", "Indian stock market"
]

# Refresh interval in seconds (4 hours)
REFRESH_INTERVAL = 4 * 60 * 60

# Number of news items to show
MAX_NEWS = 20
