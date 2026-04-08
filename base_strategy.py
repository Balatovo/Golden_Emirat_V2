<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Golden Emirat - Base Strategy</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #000; color: #e8ecf1; padding: 20px; }
        pre { background: #111; padding: 20px; border-radius: 10px; overflow-x: auto; border-left: 4px solid #ffd700; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; line-height: 1.6; color: #abb2bf; }
        .keyword { color: #c678dd; } .string { color: #98c379; } .comment { color: #5c6370; font-style: italic; } .class-name { color: #e5c07b; } .function { color: #61afef; }
        h2 { color: #ffd700; margin-bottom: 15px; }
    </style>
</head>
<body>
<h2>🎯 strategies/base_strategy.py — Базовый класс стратегии</h2>
<pre><code><span class="comment"># -*- coding: utf-8 -*-
"""Golden Emirat v2.0 - Base Strategy Abstract Class
=====================================================
Абстрактный базовый класс для всех торговых стратегий.
Определяет общий интерфейс стратегий.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from ..core.config import ConfigManager, t


class SignalType(Enum):
    """Типы торговых сигналов"""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"
    HOLD = "HOLD"
    NONE = "NONE"


@dataclass
class Signal:
    """Торговый сигнал"""
    timestamp: float
    symbol: str
    signal_type: SignalType
    price: float
    volume: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 1.0  # 0.0 - 1.0
    strategy_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyConfig:
    """Конфигурация стратегии"""
    name: str
    enabled: bool = True
    symbol: str = "XAUUSD"
    timeframe: str = "H1"
    lot_size: float = 0.01
    max_risk_percent: float = 2.0
    stop_loss_pips: int = 500
    take_profit_pips: int = 1000
    max_spread_points: float = 50.0
    magic_number: int = 20240101
    
    def __post_init__(self):
        self.max_open_positions: int = 3


class BaseStrategy(ABC):
    """
    Абстрактный базовый класс торговой стратегии.
    
    Все стратегии должны наследоваться от этого класса и реализовывать
    абстрактные методы: on_tick(), on_signal(), calculate_indicators()
    """
    
    def __init__(self, config: StrategyConfig = None):
        self.config = config or StrategyConfig()
        self.is_running = False
        self.position_opened = False
        self.current_position = None
        self.signals_history: List[Signal] = []
        
        log.info(f"[{self.__class__.__name__}] Strategy initialized")
    
    @abstractmethod
    def on_tick(self, tick_data: Dict) -> Optional[Signal]:
        """
        Обработка тика данных для генерации сигнала.
        
        Args:
            tick_data: Словарь с данными тика
            
        Returns:
            Signal объект или None (если нет сигнала)
        """
        pass
    
    @abstractmethod
    def on_signal(self, signal: Signal) -> bool:
        """
        Исполнение сигнала (открытие/закрытие).
        
        Args:
            signal: Сигнал от стратегии
            
        Returns:
            True если сигнал обработан успешно
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, df) -> Dict:
        """
        Расчёт технических индикаторов.
        
        Args:
            df: DataFrame с OHLCV данными
            
        Returns:
            Словарь с индикаторами
        """
        pass
    
    def get_info(self) -> Dict:
        """Информация о стратегии"""
        return {
            "name": self.config.name,
            "type": self.__class__.__name__,
            "enabled": self.config.enabled,
            "symbol": self.config.symbol,
            "timeframe": self.config.timeframe,
            "lot_size": self.config.lot_size,
            "max_risk": f"{self.config.max_risk_percent}%",
            "sl_pips": self.config.stop_loss_pips,
            "tp_pips": self.config.take_profit_pips,
            "magic": self.config.magic_number
        }
    
    def validate_config(self) -> Tuple[bool, str]:
        """Валидация конфигурации"""
        errors = []
        
        if not self.config.symbol:
            errors.append("Symbol is required")
        
        if self.config.lot_size <= 0:
            errors.append("Lot size must be positive")
        
        if self.config.stop_loss_pips <= 0:
            errors.append("SL must be positive")
        
        if self.config.take_profit_pips <= 0:
            errors.append("TP must be positive")
        
        if self.config.max_risk_percent > 100:
            errors.append("Risk cannot exceed 100%")
        
        return len(errors) == 0, "; ".join(errors) if errors else "OK"
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name='{self.config.name}', symbol='{self.config.symbol}')>"


# ===== Factory Function =====

def create_strategy(strategy_type: str, **kwargs) -> BaseStrategy:
    """
    Фабричная функция создания стратегии.
    
    Args:
        strategy_type: Тип стратегии ('trend', 'scalping', 'breakout', 'news')
        **kwargs: Параметры стратегии
        
    Returns:
        Экземпляр BaseStrategy
    """
    from .gold_trend_strategy import GoldTrendStrategy
    from .gold_scalping_strategy import GoldScalpingStrategy
    from .gold_breakout_strategy import GoldBreakoutStrategy
    from .gold_news_strategy import GoldNewsStrategy
    
    strategies = {
        'trend': GoldTrendStrategy,
        'scalping': GoldScalpingStrategy,
        'breakout': GoldBreakoutStrategy,
        'news': GoldNewsStrategy
    }
    
    strategy_class = strategies.get(strategy_type.lower())
    if strategy_class:
        return strategy_class(**kwargs)
    
    raise ValueError(f"Unknown strategy type: {strategy_type}")


if __name__ == "__main__":
    # Тестирование базового класса
    print("✅ Base Strategy module ready")
    print("\nAvailable strategies:")
    for s in ['trend', 'scalping', 'breakout', 'news']:
        try:
            strat = create_strategy(s)
            ok, msg = strat.validate_config()
            print(f"  • {s}: {'✅' if ok else '❌'} - {msg}")
        except Exception as e:
            print(f"  • {s}: ❌ Error - {e}")
</code></pre>
</body>
</html>
