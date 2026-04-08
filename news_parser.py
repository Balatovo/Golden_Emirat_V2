"""Парсер новостей (Requests + BeautifulSoup)."""
import requests
from bs4 import BeautifulSoup
from loguru import logger
from news.news_sources import SOURCES

class NewsParser:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def fetch_latest(self) -> list:
        news_list = []
        for source in SOURCES[:2]: # Берем топ-2 для скорости
            try:
                resp = requests.get(source.url, headers=self.headers, timeout=5)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    news_list.append({"source": source.name, "title": soup.title.string if soup.title else "No title"})
            except Exception as e:
                logger.error(f"Ошибка парсинга {source.name}: {e}")
        return news_list
