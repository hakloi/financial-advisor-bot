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
            "key_rate": payload["key_rate"],
            "usd": payload["usd"],
            "eur": payload["eur"],
            "labels": {
                "key_rate": "Key rate",
                "usd": "USD/RUB",
                "eur": "EUR/RUB",
            },
        }

    fallback = {"key_rate": 18.5, "usd": 89.6, "eur": 97.4}

    try:
        xml_response = requests.get("https://www.cbr.ru/scripts/XML_daily.asp", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        xml_response.raise_for_status()
        xml_text = xml_response.text
        for code in ("USD", "EUR"):
            match = re.search(rf"<Valute\s+ID=\"[^\"]+\"[\s\S]*?<CharCode>{code}</CharCode>[\s\S]*?<Value>([0-9,\.]+)</Value>", xml_text)
            if match:
                fallback[code.lower()] = _safe_float(match.group(1)) or fallback[code.lower()]
    except Exception:
        pass

    try:
        rate_response = requests.get("https://www.cbr.ru/hd_base/keyrate/", timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        rate_response.raise_for_status()
        text = rate_response.text
        matches = re.findall(r"(?:ключевая ставка|key rate).*?(\d+(?:[.,]\d+)?)\s*%?", text, flags=re.I | re.S)
        if matches:
            fallback["key_rate"] = _safe_float(matches[0]) or fallback["key_rate"]
    except Exception:
        pass

    payload = {
        "key_rate": round(float(fallback["key_rate"]), 2),
        "usd": round(float(fallback["usd"]), 2),
        "eur": round(float(fallback["eur"]), 2),
        "labels": {
            "key_rate": "Ключевая ставка" if locale == "ru" else "Key rate",
            "usd": "USD/RUB",
            "eur": "EUR/RUB",
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
    seen = set()
    for source in sources:
        try:
            response = requests.get(source["url"], timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            links = _extract_links_from_html(response.text, source["selectors"], source["url"])
        except Exception:
            links = []

        for item in links:
            title = _clean_title(item["title"])
            if not title or len(title) < 18 or title.lower() in {"главная", "все новости", "новости", "о нас"}:
                continue
            if title in seen:
                continue
            seen.add(title)
            gathered.append({
                "title": title,
                "source": source["name"],
                "url": item["url"],
                "lang": locale,
            })
            if len(gathered) >= limit:
                break
        if len(gathered) >= limit:
            break

    if not gathered:
        payload = [
            {"title": "Финансовые новости недоступны сейчас, но рынок и экономические события продолжают анализироваться.", "source": "banki.ru", "url": "https://www.banki.ru/news/lenta/", "lang": locale},
            {"title": "Ключевые решения центрального банка и макроэкономические сигналы остаются важным ориентиром для портфеля.", "source": "cbr.ru", "url": "https://cbr.ru/", "lang": locale},
            {"title": "Финансовые индикаторы и политика монетарных органов влияют на выбор активов и капитала.", "source": "forbes.ru", "url": "https://www.forbes.ru/", "lang": locale},
        ]
    else:
        payload = gathered[:limit]

    _NEWS_CACHE["news"] = {"ts": now, "data": payload}
    return payload
