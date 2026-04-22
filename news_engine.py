import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
from difflib import SequenceMatcher
import re
import numpy as np
from pytrends.request import TrendReq

pytrends = TrendReq(hl="en-IN", tz=330)

NEWS_SOURCES = {
    "Business Standard": "https://www.business-standard.com/rss/markets-106.rss",
    "Mint": "https://www.livemint.com/rss/markets",
    "Economic Times": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Moneycontrol": "https://www.moneycontrol.com/rss/business.xml",
}


def normalize_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def title_similarity(a, b):
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def extract_keyword(title):
    words = normalize_text(title).split()
    return " ".join(words[:4]) if words else title


def get_trend_score(keyword):
    try:
        pytrends.build_payload([keyword], timeframe="now 1-d", geo="IN")
        data = pytrends.interest_over_time()

        if data.empty or keyword not in data.columns:
            return {"trend": "Inactive", "score": 0}

        values = data[keyword].values
        latest = values[-1]
        avg = np.mean(values) if len(values) else 0

        if avg == 0 and latest > 0:
            return {"trend": "Spike", "score": int(latest)}
        if latest > avg * 1.5:
            return {"trend": "Spike", "score": int(latest)}
        elif latest > avg:
            return {"trend": "Rising", "score": int(latest)}
        elif latest > 10:
            return {"trend": "Active", "score": int(latest)}
        else:
            return {"trend": "Inactive", "score": int(latest)}

    except Exception:
        return {"trend": "Unknown", "score": 0}


def fetch_all_news():
    articles = []

    for source, url in NEWS_SOURCES.items():
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:15]:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                published = item.findtext("pubDate", "").strip()

                if title and link:
                    articles.append({
                        "title": title,
                        "link": link,
                        "published": published,
                        "source": source
                    })
        except Exception:
            continue

    return articles


def cluster_news(articles, threshold=0.72):
    clusters = []

    for article in articles:
        matched_cluster = None

        for cluster in clusters:
            if title_similarity(article["title"], cluster["headline"]) >= threshold:
                matched_cluster = cluster
                break

        if matched_cluster:
            matched_cluster["articles"].append(article)
        else:
            clusters.append({
                "headline": article["title"],
                "articles": [article]
            })

    return clusters


def dedupe_sources_within_cluster(cluster):
    best_by_source = {}

    for article in cluster["articles"]:
        source = article["source"]

        if source not in best_by_source:
            best_by_source[source] = article
        else:
            current = best_by_source[source]
            if len(article["title"]) > len(current["title"]):
                best_by_source[source] = article

    deduped_articles = list(best_by_source.values())

    return {
        "headline": cluster["headline"],
        "sources": deduped_articles,
        "source_count": len(deduped_articles)
    }


def rank_news(clusters):
    deduped = [dedupe_sources_within_cluster(cluster) for cluster in clusters]
    enriched = []

    for cluster in deduped:
        keyword = extract_keyword(cluster["headline"])
        trend_data = get_trend_score(keyword)

        score = (
            cluster["source_count"] * 10 +
            trend_data["score"]
        )

        enriched.append({
            **cluster,
            "keyword": keyword,
            "trend": trend_data["trend"],
            "trend_score": trend_data["score"],
            "score": score
        })

    ranked = sorted(enriched, key=lambda x: x["score"], reverse=True)
    return ranked


def get_clustered_news():
    articles = fetch_all_news()
    clusters = cluster_news(articles)
    ranked = rank_news(clusters)

    top5 = ranked[:5]
    backup10 = ranked[5:15]

    return top5, backup10
