import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

MOEX_CBR_URL = "https://www.cbr.ru/"


def fetch_market_snapshot(lang="ru"):
    locale = (lang or "ru").lower()
    fallback = {
        "key_rate": 21.0,
        "usd": 90.0,
        "eur": 98.0,
    }

    try:
        response = requests.get(MOEX_CBR_URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        text = response.text
        key_match = re.search(r"ключевая ставка.*?(\d+(?:[.,]\d+)?)%?|key rate.*?(\d+(?:[.,]\d+)?)%?", text, re.I | re.S)
        if key_match:
            value = key_match.group(1) or key_match.group(2)
            fallback["key_rate"] = float(value.replace(",", "."))

        usd_match = re.search(r"USD.*?(\d+(?:[.,]\d+)?)|US Dollar.*?(\d+(?:[.,]\d+)?)", text, re.I | re.S)
        if usd_match:
            value = usd_match.group(1) or usd_match.group(2)
            fallback["usd"] = float(value.replace(",", "."))

        eur_match = re.search(r"EUR.*?(\d+(?:[.,]\d+)?)|Euro.*?(\d+(?:[.,]\d+)?)", text, re.I | re.S)
        if eur_match:
            value = eur_match.group(1) or eur_match.group(2)
            fallback["eur"] = float(value.replace(",", "."))
    except Exception:
        pass

    if locale == "ru":
        return {
            "key_rate": round(fallback["key_rate"], 2),
            "usd": round(fallback["usd"], 2),
            "eur": round(fallback["eur"], 2),
            "labels": {
                "key_rate": "Ключевая ставка",
                "usd": "USD/RUB",
                "eur": "EUR/RUB",
            },
        }

    return {
        "key_rate": round(fallback["key_rate"], 2),
        "usd": round(fallback["usd"], 2),
        "eur": round(fallback["eur"], 2),
        "labels": {
            "key_rate": "Key rate",
            "usd": "USD/RUB",
            "eur": "EUR/RUB",
        },
    }

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


def fetch_financial_news(lang="ru", limit=5):
    locale = (lang or "ru").lower()
    sources = [
        {
            "name": "banki.ru",
            "url": "https://www.banki.ru/news/lenta/",
            "selectors": [
                "a[href*=news]",
                ".news-item a",
                "article a",
                "h3 a",
                "h2 a",
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
            "url": "https://www.forbes.ru/",
            "selectors": [
                "a[href*=news]",
                "article a",
                "h2 a",
                "h3 a",
                ".news-item a",
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
            title = item["title"]
            if not title or title in seen:
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

    if not gathered:
        return [
            {"title": "Финансовые новости недоступны сейчас, но рынок и экономические события продолжают анализироваться.", "source": "insight", "url": "https://www.banki.ru/news/lenta/", "lang": locale},
            {"title": "Ключевые решения центрального банка и макроэкономические сигналы остаются важным ориентиром для портфеля.", "source": "cbr.ru", "url": "https://cbr.ru/", "lang": locale},
        ]

    return gathered[:limit]
