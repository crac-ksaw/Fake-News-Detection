import re
from typing import Any
from urllib.parse import quote_plus
from xml.etree import ElementTree

import requests

from backend.core.logger import logger


GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
GOOGLE_NEWS_RSS_API = "https://news.google.com/rss/search"
REQUEST_TIMEOUT_SECONDS = 15
DEFAULT_MAX_RECORDS = 5

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "will",
    "with",
}


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z0-9\s'-]", " ", text)).strip()


def _extract_keywords(text: str, limit: int = 8) -> list[str]:
    words: list[str] = []
    for token in _clean_text(text).lower().split():
        if len(token) < 3 or token in STOPWORDS:
            continue
        if token not in words:
            words.append(token)
        if len(words) >= limit:
            break
    return words


def _build_queries(text: str) -> list[str]:
    cleaned = _clean_text(text)
    if not cleaned:
        return []

    queries = [f'"{cleaned[:180]}"']

    keywords = _extract_keywords(cleaned)
    if keywords:
        queries.append(" ".join(keywords))

    shorter_phrase = " ".join(cleaned.split()[:12])
    if shorter_phrase and shorter_phrase not in queries:
        queries.append(f'"{shorter_phrase}"')

    seen: set[str] = set()
    deduped: list[str] = []
    for query in queries:
        if query and query not in seen:
            deduped.append(query)
            seen.add(query)
    return deduped


def _fetch_articles(query: str, max_records: int) -> list[dict[str, Any]]:
    url = (
        f"{GDELT_DOC_API}?query={quote_plus(query)}&mode=artlist"
        f"&maxrecords={max_records}&format=json&sort=datedesc&timespan=30d"
    )
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    payload = response.json()
    articles = payload.get("articles", [])
    return articles if isinstance(articles, list) else []


def _fetch_google_news_rss(query: str, max_records: int) -> list[dict[str, Any]]:
    url = (
        f"{GOOGLE_NEWS_RSS_API}?q={quote_plus(query)}"
        "&hl=en-US&gl=US&ceid=US:en"
    )
    response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    root = ElementTree.fromstring(response.content)
    articles: list[dict[str, Any]] = []

    for item in root.findall("./channel/item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        pub_date = item.findtext("pubDate", default="").strip()
        source = item.findtext("source", default="").strip()

        if not title:
            continue

        articles.append(
            {
                "title": title,
                "url": link,
                "domain": source or "Google News",
                "seendate": pub_date,
            }
        )

        if len(articles) >= max_records:
            break

    return articles


def _format_article(article: dict[str, Any]) -> str:
    title = str(article.get("title", "")).strip() or "Untitled"
    domain = str(article.get("domain", "")).strip() or "unknown source"
    date = str(article.get("seendate", "")).strip() or "unknown date"
    url = str(article.get("url", "")).strip()
    return f"{title} | Source: {domain} | Seen: {date} | URL: {url}"


def retrieve_context(text: str, max_records: int = DEFAULT_MAX_RECORDS) -> list[str]:
    logger.info("Retrieving live context for text: %s", text[:80])

    queries = _build_queries(text)
    if not queries:
        return []

    collected: list[str] = []
    seen_urls: set[str] = set()

    for query in queries:
        articles: list[dict[str, Any]] = []
        retrieval_errors: list[str] = []

        for fetcher_name, fetcher in (
            ("GDELT", _fetch_articles),
            ("Google News RSS", _fetch_google_news_rss),
        ):
            try:
                articles = fetcher(query, max_records=max_records)
            except Exception as exc:
                retrieval_errors.append(f"{fetcher_name}: {exc}")
                continue

            if articles:
                break

        if not articles:
            logger.warning(
                "Live retrieval failed for query '%s': %s",
                query,
                " | ".join(retrieval_errors) or "no articles found",
            )
            continue

        for article in articles:
            url = str(article.get("url", "")).strip()
            if url and url in seen_urls:
                continue

            if url:
                seen_urls.add(url)
            collected.append(_format_article(article))

            if len(collected) >= max_records:
                return collected

    return collected
