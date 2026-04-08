<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Golden Emirat - Trend Strategy</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #000; color: #e8ecf1; padding: 20px; }
        pre { background: #111; padding: 20px; border-radius: 10px; overflow-x: auto; border-left: 4px solid #ffd700; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; line-height: 1.6; color: #abb2bf; }
        .keyword { color: #c678dd; } .string { color: #98c379; } .comment { color: #5c6370; font-style: italic; } .class-name { color: #e5c07b; } .function { color: #61afef; }
        h2 { color: #ffd700; margin-bottom: 15px; }
    </style>
</head>
<body>
<h2>📈 strategies/gold_trend_strategy.py — Трендовая стратегия</h2>
<pre><code><span class="comment"># -*- coding: utf-8 -*-
"""Golden Emirat v2.0 - Trend Following Strategy
=====================================================
Трендследующая стратегия на основе EMA + RSI.
Оптимальна для трендовых движений золота.
"""

import numpy as np
import pandas as pd
from datetime import datetime

from .base_strategy import (
    BaseStrategy, StrategyConfig, Signal, SignalType,
    get_logger
)

log = get_logger(__name__)


@dataclass
class TrendConfig(StrategyConfig):
    """Конфигурация трендовой стратегии"""
    ema_fast_period: int = 9
    ema_slow_period: int = 21
    rsi_period: int = 14
    rsi_overbought: float = 70.0
    rsi_oversold: float = 30.0
    
    def __post_init__(self):
        self.name = "Trend"
        self.timeframe = "H1"
        self.max_risk_percent = 1.5


class GoldTrendStrategy(BaseStrategy):
    """
    Трендовая стратегия Golden Emirat.
    
    Логика:
    - Покупает при восходящем тренде (EMA9 > EMA21)
    - Продает при нисходящем тренде (EMA9 < EMA21)
    - Использует RSI для подтверждения силы тренда
    - Фильтрует слабые сигналы (RSI < 40 или > 80)
    
    Индикаторы:
    - EMA Fast (9) — быстрая скользяющая средняя
    - EMA Slow (21) — медленная скользяющая средняя
    - RSI (14) — индекс относительной силы
    """
    
    def __init__(self, config: TrendConfig = None):
        super().__init__(config or TrendConfig())
        
        # Дополнительные параметры
        self.min_rsi = 40.0
        self.max_rsi = 80.0
        self.trend_strength = 0.5  # Минимальная сила тренда
        
        log.info("Trend Strategy initialized")
    
    def on_tick(self, tick_data: Dict) -> Optional[Signal]:
        """
        Анализ тика и генерация сигнала.
        
        Args:
            tick_data: Словарь с данными тика {
                'timestamp': float,
                'open': float,
                'high': float,
                'low': float,
                'close': float,
                'volume': float
            }
            
        Returns:
            Signal объект или None
        """
        try:
            df = pd.DataFrame([tick_data])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('timestamp')
            
            # Расчёт индикаторов
            indicators = self.calculate_indicators(df)
            
            if indicators.empty():
                return None
            
            ema_fast = indicators.get('ema_9', pd.Series())
            ema_slow = indicators.get('ema_21', pd.Series())
            rsi = indicators.get('rsi_14', pd.Series())
            
            # Проверяем наличие данных
            if len(ema_fast) < 20 or len(ema_slow) < 50:
                return None
            
            # ===== Основная логика стратегии =====
            signal_type = None
            current_close = df['close'].iloc[-1]
            
            # 1. Определяем направление тренда
            is_bullish = ema_fast.iloc[-1] > ema_slow.iloc[-1]
            
            # 2. RSI фильтр
            rsi_current = rsi.iloc[-1]
            if rsi_current > self.max_rsi or rsi_current < self.min_rsi:
                return None  # Перекупленность или перепродан
            
            # 3. Сила тренда
            trend_strength = self._calculate_trend_strength(
                ema_fast, ema_slow, 
                current_close, df['high'].iloc[-1], 
                df['low'].iloc[-1]
            )
            
            if trend_strength < self.trend_strength:
                return None  # Слабый тренд
            
            # 4. Генерируем сигнал
            if is_bullish:
                signal_type = SignalType.BUY
                price = current_close
                confidence = min(1.0, trend_strength * 1.5)
            else:
                signal_type = SignalType.SELL
                price = current_close
                confidence = min(1.0, (1 - trend_strength) * 1.5)
            
            # 5. Создаём объект сигнала
            signal = Signal(
                timestamp=df['timestamp'].iloc[-1],
                symbol=self.config.symbol,
                signal_type=signal_type,
                price=price,
                volume=self._calculate_position_size(),
                stop_loss=self._calculate_sl(price),
                take_profit=self._calculate_tp(price),
                confidence=confidence,
                strategy_name=self.name,
                metadata={
                    "ema_fast": round(ema_fast.iloc[-1], 2),
                    "ema_slow": round(ema_slow.iloc[-1], 2),
                    "rsi": round(rsi_current, 2),
                    "trend_strength": round(trend_strength, 3),
                    "close_price": round(price, 2)
                }
            )
            
            log.debug(f"Trend Signal: {signal_type.value} @ {price} | Confidence: {confidence:.2f}")
            return signal
            
        except Exception as e:
            log.error(f"Error in trend strategy: {e}")
            return None
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Расчёт индикаторы для трендовой стратегии.
        
        Returns:
            Словарь с индикаторами
        """
        indicators = {}
        
        try:
            # EMA Fast
            ema_fast = df['close'].ewm(span=self.config.ema_fast_period, adjust=False).mean()
            indicators['ema_9'] = ema_fast.round(2)
            
            # EMA Slow
            ema_slow = df['close'].ewm(span=self.config.ema_slow_period, adjust=False).mean()
            indicators['ema_21'] = ema_slow.round(2)
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0) * 1).rolling(window=self.config.rsi_period).mean()
            loss = (-delta.where(delta < 0) * 1).rolling(window=self.config.rsi_period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi_14'] = rsi.round(2)
            
            # ATR (Average True Range)
            tr = df['high'] - df['low']
            atr = tr.rolling(window=14).mean()
            indicators['atr'] = atr.round(2)
            
            # ADX (Average Directional Index)
            up = (df['close'] > df['open']).astype(int)
            down = (df['close'] < df['open']).astype(int)
            adx = up.ewm(span=10).mean() - down.ewm(span=10).mean()
            indicators['adx'] = adx.round(2)
            
            log.debug(f"Indicators calculated: {list(indicators.keys())}")
            
        except Exception as e:
            log.error(f"Error calculating indicators: {e}")
            return {}
    
    def _calculate_trend_strength(self, ema_fast, ema_slow, close, high, low) -> float:
        """
        Расчёт силы текущего тренда.
        
        Returns:
            Значение от 0 до 1 (чем выше, тем сильнее тренд)
        """
        try:
            # Угол наклона EMA
            ema_angle = np.arctan2(
                (ema_fast - ema_slow) / (abs(ema_slow) + 0.001), 1
            ) * (180 / np.pi)
            
            # Позиция цены относительно EMA
            price_pos = (close - ema_slow) / (close * 0.01)  # В процентах от EMA
            
            # Нормализация
            strength = np.clip((price_pos + 1) / 2, 0, 1)
            
            return round(strength, 3)
            
        except Exception as e:
            log.warning(f"Error calculating trend strength: {e}")
            return 0.5
    
    def _calculate_position_size(self) -> float:
        """Расчёт размера позиции"""
        # Риск 1.5% от баланса
        balance = 10000  # TODO: Получить из config
        risk_amount = balance * (self.config.max_risk_percent / 100)
        
        # SL в пунктах (для золота ~$0.01 за пункт)
        sl_distance = self.config.stop_loss_pips
        sl_cost = sl_distance * 0.01
        
        # Объём позиции
        position_size = risk_amount / sl_cost
        position_size = max(0.01, round(position_size, 2))  # Минимум 0.01 лота
        
        return position_size
    
    def _calculate_sl(self, entry_price: float) -> float:
        """Расчёт Stop Loss цены"""
        return entry_price - (self.config.stop_loss_pips * 0.01)
    
    def _calculate_tp(self, entry_price: float) -> float:
        """Расчёт Take Profit цены (R:R = 1:2)"""
        return entry_price + (self.config.take_profit_pips * 0.01)


if __name__ == "__main__":
    # Тестирование
    strat = GoldTrendStrategy()
    
    print(f"\n{'='*60}")
    print(f"{'🥇 GOLDEN EMIRAT - TREND STRATEGY'}")
    print(f"{'='*60}\n")
    
    print(f"Strategy: {strat.name}")
    print(f"Symbol: {strat.symbol}")
    print(f"Timeframe: {strat.timeframe}")
    print(f"Lot Size: {strat.lot_size}")
    print(f"Max Risk: {strat.max_risk_percent}%")
    print(f"SL/TP: {strat.stop_loss_pips}/{strat.take_profit_pips} pips")
    
    print("\n✅ Trend Strategy ready!")
</code></pre>
</body>
</html>
