"""Торговля на новостях (Фильтрация по календарю)."""
import pandas as pd
from strategies.base_strategy import BaseStrategy
from news.economic_calendar import EconomicCalendar

class GoldNewsStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "News Trading ⭐"
        self.calendar = EconomicCalendar()

    def generate_signal(self, data: pd.DataFrame) -> dict:
        # Проверяет, есть ли важные новости прямо сейчас
        if not self.calendar.is_high_impact_news_now():
            return {'action': 'HOLD', 'sl': 0, 'tp': 0}
        
        # Логика пробоя волатильности после новости
        price = data['close'].iloc[-1]
        prev_close = data['close'].iloc[-2]
        change = abs(price - prev_close)
        
        if change > 500: # Сильное движение
            action = 'BUY' if price > prev_close else 'SELL'
            return {'action': action, 'sl': price + (-500 if action == 'BUY' else 500), 'tp': price + (1000 if action == 'BUY' else -1000)}
        return {'action': 'HOLD', 'sl': 0, 'tp': 0}
