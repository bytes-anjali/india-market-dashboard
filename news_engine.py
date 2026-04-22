import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
import re


NEWS_SOURCES = {
    "Business Standard": "https://www.business-standard.com/rss/markets-106.rss",
    "Mint": "https://www.livemint.com/rss/markets",
    "Economic Times": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Moneycontrol": "https://www.moneycontrol.com/rss/business.xml",
}


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return text


def fetch_all_news():
    articles = []

    for source, url in NEWS_SOURCES.items():
        try:
            resp = requests.get(url, timeout=10)
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:15]:
                articles.append({
                    "title": item.findtext("title", "").strip(),
                    "link": item.findtext("link", "").strip(),
                    "published": item.findtext("pubDate", ""),
                    "source": source
                })
        except Exception:
            continue

    return articles


def cluster_news(articles):
    clusters = defaultdict(list)

    for article in articles:
        key = normalize(article["title"])[:60]  # simple grouping
        clusters[key].append(article)

    results = []

    for group in clusters.values():
        if not group:
            continue

        results.append({
            "headline": group[0]["title"],
            "sources": group
        })

    return results


def rank_news(clusters):
    # simple ranking for now
    return sorted(clusters, key=lambda x: len(x["sources"]), reverse=True)


def get_clustered_news():
    articles = fetch_all_news()
    clusters = cluster_news(articles)
    ranked = rank_news(clusters)

    return ranked[:10]
