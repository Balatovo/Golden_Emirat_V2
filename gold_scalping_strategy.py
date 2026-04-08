"""Скальпинг (RSI)."""
import pandas as pd
from strategies.base_strategy import BaseStrategy

class GoldScalpingStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Scalper RSI"
        self.period = 14

    def generate_signal(self, data: pd.DataFrame) -> dict:
        if len(data) < self.period or 'close' not in data.columns: return {'action': 'HOLD', 'sl': 0, 'tp': 0}
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(self.period).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        rsi = data['rsi'].iloc[-1]
        price = data['close'].iloc[-1]
        
        if rsi < 30: return {'action': 'BUY', 'sl': price - 200, 'tp': price + 400}
        if rsi > 70: return {'action': 'SELL', 'sl': price + 200, 'tp': price - 400}
        return {'action': 'HOLD', 'sl': 0, 'tp': 0}
