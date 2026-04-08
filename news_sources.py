"""Источники новостей (8 сайтов)."""
from dataclasses import dataclass

@dataclass
class NewsSource:
    name: str
    url: str
    importance: str # HIGH, MEDIUM, LOW

SOURCES = [
    NewsSource("Forex Factory", "https://forexfactory.com/calendar", "HIGH"),
    NewsSource("Investing.com", "https://investing.com/economic-calendar/", "HIGH"),
    NewsSource("DailyFX", "https://www.dailyfx.com/gold-price", "MEDIUM"),
    NewsSource("Reuters", "https://www.reuters.com/commodities/gold", "HIGH"),
    NewsSource("Bloomberg", "https://www.bloomberg.com/markets/commodities", "HIGH"),
    NewsSource("Kitco News", "https://www.kitco.com/news/gold", "MEDIUM"),
    NewsSource("Trading Economics", "https://tradingeconomics.com/calendar", "MEDIUM"),
    NewsSource("CoinTelegraph", "https://cointelegraph.com/tags/gold", "LOW")
]
