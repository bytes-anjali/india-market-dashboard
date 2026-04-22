import yfinance as yf
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
import config


@st.cache_data(ttl=300)
def get_indices():
    """Fetch current index values and % change."""
    results = []
    for name, symbol in config.INDICES.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                curr_close = hist["Close"].iloc[-1]
                change_pct = ((curr_close - prev_close) / prev_close) * 100
                results.append({
                    "Index": name,
                    "Value": round(curr_close, 2),
                    "Change %": round(change_pct, 2),
                })
        except Exception:
            results.append({
                "Index": name,
                "Value": "N/A",
                "Change %": 0
            })
    return pd.DataFrame(results)


@st.cache_data(ttl=300)
def get_top_stocks():
    """Fetch top stocks with price and % change."""
    results = []
    for symbol in config.TOP_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                curr_close = hist["Close"].iloc[-1]
                change_pct = ((curr_close - prev_close) / prev_close) * 100
                results.append({
                    "Stock": symbol.replace(".NS", ""),
                    "Price (₹)": round(curr_close, 2),
                    "Change %": round(change_pct, 2),
                })
        except Exception:
            results.append({
                "Stock": symbol.replace(".NS", ""),
                "Price (₹)": "N/A",
                "Change %": 0
            })
    return pd.DataFrame(results)


@st.cache_data(ttl=300)
def get_news():
    """Fetch news from RSS feeds."""
    articles = []
    for url in config.NEWS_FEEDS:
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:10]:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                pub_date = item.findtext("pubDate", "").strip()

                if title and link:
                    articles.append({
                        "Title": title,
                        "Link": link,
                        "Published": pub_date,
                        "Source": url.split("/")[2].replace("www.", "")
                    })
        except Exception:
            continue

    return articles[:config.MAX_NEWS]


@st.cache_data(ttl=300)
def get_ipo_data():
    """Fetch IPO data from NSE."""
    ipos = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://www.nseindia.com/api/ipo-current-allotment"
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        for item in data.get("data", []):
            ipos.append({
                "Company": item.get("companyName", ""),
                "Open": item.get("ipoOpenDate", ""),
                "Close": item.get("ipoCloseDate", ""),
                "Price Band": item.get("priceBand", ""),
                "Status": item.get("status", ""),
            })
    except Exception:
        ipos = [{
            "Company": "Data unavailable - NSE may require login",
            "Open": "",
            "Close": "",
            "Price Band": "",
            "Status": ""
        }]

    return pd.DataFrame(ipos)


def get_last_updated():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")
