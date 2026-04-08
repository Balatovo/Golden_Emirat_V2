"""Экономический календарь (Mock)."""
from datetime import datetime
from loguru import logger

class EconomicCalendar:
    def get_events(self) -> list:
        # В реальности тут парсинг Investing.com или FX Street API
        return [
            {"time": datetime.now(), "event": "FOMC Decision", "impact": "HIGH"},
            {"time": datetime.now(), "event": "NFP", "impact": "HIGH"}
        ]

    def is_high_impact_news_now(self) -> bool:
        """Проверка, идет ли сейчас важная новость (в пределах 15 мин)."""
        # Заглушка для безопасности бэктестов
        return False
