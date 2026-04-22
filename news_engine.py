import requests
import xml.etree.ElementTree as ET
from collections import defaultdict
from difflib import SequenceMatcher
import re


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
    ranked = sorted(
        deduped,
        key=lambda x: (x["source_count"], len(x["headline"])),
        reverse=True
    )
    return ranked


def get_clustered_news():
    articles = fetch_all_news()
    clusters = cluster_news(articles)
    ranked = rank_news(clusters)
    return ranked[:10]
