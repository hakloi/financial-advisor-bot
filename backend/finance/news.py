import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

MOEX_CBR_URL = "https://www.cbr.ru/"

_MARKET_CACHE = {}


def _safe_float(value):
    try:
        return float(str(value).replace(",", ".").replace("%", ""))
    except Exception:
        return None


def fetch_market_snapshot(lang="ru"):
    locale = (lang or "ru").lower()
    now = int(time.time())
    cached = _MARKET_CACHE.get("market")
    if cached and now - cached["ts"] < 86400:
        payload = cached["data"]
        return payload if locale == "ru" else {
            "usd": payload["usd"],
            "eur": payload["eur"],
            "cny": payload["cny"],
            "inr": payload["inr"],
            "labels": {
                "usd": "USD/RUB",
                "eur": "EUR/RUB",
                "cny": "CNY/RUB",
                "inr": "INR/RUB",
            },
        }

    fallback = {"usd": 89.6, "eur": 97.4, "cny": 12.1, "inr": 1.05}

    try:
        xml_response = requests.get("https://www.cbr.ru/scripts/XML_daily.asp", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        xml_response.raise_for_status()
        xml_text = xml_response.text
        for code in ("USD", "EUR", "CNY", "INR"):
            match = re.search(rf"<Valute\s+ID=\"[^\"]+\"[\s\S]*?<CharCode>{code}</CharCode>[\s\S]*?<Value>([0-9,\.]+)</Value>", xml_text)
            if match:
                fallback[code.lower()] = _safe_float(match.group(1)) or fallback[code.lower()]
    except Exception:
        pass

    payload = {
        "usd": round(float(fallback["usd"]), 2),
        "eur": round(float(fallback["eur"]), 2),
        "cny": round(float(fallback["cny"]), 2),
        "inr": round(float(fallback["inr"]), 2),
        "labels": {
            "usd": "USD/RUB",
            "eur": "EUR/RUB",
            "cny": "CNY/RUB",
            "inr": "INR/RUB",
        },
    }
    _MARKET_CACHE["market"] = {"ts": now, "data": payload}
    return payload

DEFAULT_NEWS = [
    {
        "title": "Финансовые новости: рынок и макроэкономика",
        "source": "banki.ru",
        "url": "https://www.banki.ru/news/lenta/",
    },
    {
        "title": "Центральный банк России: актуальные решения",
        "source": "cbr.ru",
        "url": "https://cbr.ru/",
    },
    {
        "title": "Forbes: экономика и финансы",
        "source": "forbes.ru",
        "url": "https://www.forbes.ru/",
    },
]

_NEWS_CACHE = {}


def _clean_title(raw_text):
    text = re.sub(r"\s+", " ", raw_text or "").strip()
    return text[:180]


def _extract_links_from_html(html_text, selectors, base_url):
    soup = BeautifulSoup(html_text, "html.parser")
    links = []
    for selector in selectors:
        for element in soup.select(selector):
            href = element.get("href")
            if not href:
                continue
            text = _clean_title(element.get_text(" ", strip=True))
            if not text:
                continue
            links.append({"title": text, "url": urljoin(base_url, href)})
    return links


def fetch_financial_news(lang="ru", limit=3):
    locale = (lang or "ru").lower()
    now = int(time.time())
    cached = _NEWS_CACHE.get("news")
    if cached and now - cached["ts"] < 86400:
        return cached["data"][:limit]

    sources = [
        {
            "name": "banki.ru",
            "url": "https://www.banki.ru/news/lenta/",
            "selectors": [
                ".news-item a",
                "article a",
                "h3 a",
                "h2 a",
                "a[href*=news]",
            ],
        },
        {
            "name": "cbr.ru",
            "url": "https://cbr.ru/",
            "selectors": [
                "a[href*=press]",
                "a[href*=news]",
                "a[href*=analytics]",
                ".news a",
                "li a",
            ],
        },
        {
            "name": "forbes.ru",
            "url": "https://www.forbes.ru/finansy",
            "selectors": [
                "article a",
                "h2 a",
                "h3 a",
                ".news-item a",
                "a[href*=finansy]",
                "a[href*=finance]",
            ],
        },
    ]

    gathered = []
    seen_titles = set()
    for source in sources:
        if len(gathered) >= limit:
            break
        try:
            response = requests.get(source["url"], timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            links = _extract_links_from_html(response.text, source["selectors"], source["url"])
        except Exception:
            links = []

        chosen = None
        for item in links:
            title = _clean_title(item["title"])
            if not title or len(title) < 18 or title.lower() in {"главная", "все новости", "новости", "о нас"}:
                continue
            if title in seen_titles:
                continue
            seen_titles.add(title)
            chosen = {
                "title": title,
                "source": source["name"],
                "url": item["url"],
                "lang": locale,
            }
            break

        if chosen:
            gathered.append(chosen)

    if not gathered:
        payload = [
            {"title": "Финансовые новости недоступны сейчас, но рынок и экономические события продолжают анализироваться.", "source": "banki.ru", "url": "https://www.banki.ru/news/lenta/", "lang": locale},
            {"title": "Ключевые решения центрального банка и макроэкономические сигналы остаются важным ориентиром для портфеля.", "source": "cbr.ru", "url": "https://cbr.ru/", "lang": locale},
            {"title": "Финансовые индикаторы и политика монетарных органов влияют на выбор активов и капитала.", "source": "forbes.ru", "url": "https://www.forbes.ru/finansy", "lang": locale},
        ]
    else:
        payload = gathered[:limit]

    _NEWS_CACHE["news"] = {"ts": now, "data": payload}
    return payload
