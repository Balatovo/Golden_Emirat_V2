"""Пробой (Bollinger Bands)."""
import pandas as pd
from strategies.base_strategy import BaseStrategy

class GoldBreakoutStrategy(BaseStrategy):
    def __init__(self, config):
        super().__init__(config)
        self.name = "Breakout BB"
        self.window = 20

    def generate_signal(self, data: pd.DataFrame) -> dict:
        if len(data) < self.window or 'close' not in data.columns: return {'action': 'HOLD', 'sl': 0, 'tp': 0}
        sma = data['close'].rolling(self.window).mean()
        std = data['close'].rolling(self.window).std()
        data['upper'] = sma + (std * 2)
        data['lower'] = sma - (std * 2)
        price = data['close'].iloc[-1]
        
        if price > data['upper'].iloc[-1]: return {'action': 'BUY', 'sl': data['lower'].iloc[-1], 'tp': price + 800}
        if price < data['lower'].iloc[-1]: return {'action': 'SELL', 'sl': data['upper'].iloc[-1], 'tp': price - 800}
        return {'action': 'HOLD', 'sl': 0, 'tp': 0}
