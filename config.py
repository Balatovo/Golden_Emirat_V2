#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Emirat v2.0 - Configuration Module
=========================================
Централизованная конфигурация с поддержкой мультиязычности (RU/EN).
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class Language(Enum):
    """Поддерживаемые языки"""
    RUSSIAN = "ru"
    ENGLISH = "en"


class DisplayUnits(Enum):
    """Единицы отображения"""
    USD_DOLLARS = "$"
    POINTS = "pt"
    PIPS = "pip"


# ===== I18N Translations =====
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    Language.RUSSIAN.value: {
        # App
        "app.name": "Golden Emirat",
        "app.version": "v2.0",
        "app.subtitle": "Торговый робот для золота XAU/USD",
        
        # Menu
        "menu.dashboard": "📊 Панель управления",
        "menu.strategies": "🎯 Стратегии",
        "menu.settings": "⚙️ Настройки",
        "menu.charts": "📈 Графики",
        "menu.trades": "💼 Сделки",
        "menu.risks": "🛡️ Риски",
        "menu.news": "📰 Новости",
        "menu.notifications": "🔔 Уведомления",
        "menu.backtest": "📉 Бэктестинг",
        "menu.time_sync": "⏰ Синхронизация времени",
        "menu.sounds": "🔊 Звуки",
        
        # Actions
        "action.buy": "BUY",
        "action.sell": "SELL",
        "action.close_all": "Закрыть все",
        "action.start": "▶️ ЗАПУСТИТЬ",
        "action.stop": "⏹ ОСТАНОВИТЬ",
        
        # Status
        "status.connected": "✅ Подключено",
        "status.disconnected": "❌ Отключено",
        "status.running": "● Активен",
        "status.stopped": "⏹ Остановлен",
        
        # Errors
        "error.connection": "Ошибка подключения к брокеру",
        "error.order": "Ошибка отправки ордера",
        "error.auth": "Ошибка аутентификации",
        
        # Time Sync
        "time.gmt": "GMT (UTC)",
        "time.broker": "Время Брокера",
        "time.local": "Локальное время",
        "time.synced": "✅ СИНХРОНИЗИРОВАНО",
        
        # Notifications
        "notif.trade_opened": "🟢 СДЕЛКА ОТКРЫТА",
        "notif.trade_closed": "✅ СДЕЛКА ЗАКРЫТА",
        "notif.stop_loss": "❌ СТОП-ЛОСС СРАБОТАЛ",
        "notif.news_signal": "📰 НОВОСТНОЙ СИГНАЛ",
    },
    
    Language.ENGLISH.value: {
        # App
        "app.name": "Golden Emirat",
        "app.version": "v2.0",
        "app.subtitle": "Trading Bot for Gold XAU/USD",
        
        # Menu
        "menu.dashboard": "📊 Dashboard",
        "menu.strategies": "🎯 Strategies",
        "menu.settings": "⚙️ Settings",
        "menu.charts": "📈 Charts",
        "menu.trades": "💼 Trades",
        "menu.risks": "🛡️ Risks",
        "menu.news": "📰 News",
        "menu.notifications": "🔔 Notifications",
        "menu.backtest": "📉 Backtesting",
        "menu.time_sync": "⏰ Time Sync",
        "menu.sounds": "🔊 Sounds",
        
        # Actions
        "action.buy": "BUY",
        "action.sell": "SELL",
        "action.close_all": "Close All",
        "action.start": "▶️ START",
        "action.stop": "⏹ STOP",
        
        # Status
        "status.connected": "✅ Connected",
        "status.disconnected": "❌ Disconnected",
        "status.running": "● Active",
        "status.stopped": "⏹ Stopped",
        
        # Errors
        "error.connection": "Broker connection error",
        "error.order": "Order execution error",
        "error.auth": "Authentication error",
        
        # Time Sync
        "time.gmt": "GMT (UTC)",
        "time.broker": "Broker Time",
        "time.local": "Local Time",
        "time.synced": "✅ SYNCED",
        
        # Notifications
        "notif.trade_opened": "🟢 TRADE OPENED",
        "notif.trade_closed": "✅ TRADE CLOSED",
        "notif.stop_loss": "❌ STOP LOSS TRIGGERED",
        "notif.news_signal": "📰 NEWS SIGNAL",
    }
}


@dataclass
class BrokerConfig:
    """Конфигурация брокера"""
    type: str = "mt5"  # mt4, mt5
    server: str = ""
    login: int = 0
    password: str = ""
    path: str = ""  # Путь к терминалу MT4/MT5
    timezone: str = "Europe/Helsinki"  # Часовой пояс сервера


@dataclass
class TradingConfig:
    """Торговая конфигурация"""
    symbol: str = "XAUUSD"
    lot_size: float = 0.01
    max_risk_percent: float = 2.0
    stop_loss_pips: int = 500
    take_profit_pips: int = 1000
    max_spread: float = 50.0
    slippage: int = 10
    magic_number: int = 20240101


@dataclass
class StrategyConfig:
    """Конфигурация стратегий"""
    trend_enabled: bool = True
    scalping_enabled: bool = True
    breakout_enabled: bool = True
    news_trading_enabled: bool = True
    
    # Параметры трендовой стратегии
    trend_ema_fast: int = 9
    trend_ema_slow: int = 21
    trend_rsi_period: int = 14
    
    # Параметры скальпинга
    scalping_bb_period: int = 20
    scalping_bb_std: float = 2.0
    scalping_rsi_oversold: int = 30
    scalping_rsi_overbought: int = 70
    
    # Параметры пробоя
    breakout_atr_period: int = 14
    breakout_atr_multiplier: float = 2.0
    breakout_lookback: int = 20
    
    # Параметры новостной торговли
    news_impact_filter: list = field(default_factory=lambda: ["high", "medium"])
    news_pause_before_min: int = 15
    news_resume_after_min: int = 30


@dataclass
class NotificationConfig:
    """Конфигурация уведомлений"""
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    sound_enabled: bool = True
    sound_volume: float = 0.7


@dataclass
class DisplayConfig:
    """Конфигурация отображения"""
    language: str = Language.RUSSIAN.value
    units: str = DisplayUnits.USD_DOLLARS.value
    theme: str = "dark"  # dark, light
    chart_type: str = "candles"  # candles, line, area
    timeframe: str = "H1"  # M5, M15, M30, H1, H4, D1


@dataclass
class TimeSyncConfig:
    """Конфигурация синхронизации времени"""
    ntp_server: str = "pool.ntp.org"
    auto_dst: bool = True
    update_interval_sec: int = 1


@dataclass
class AppConfig:
    """Главная конфигурация приложения"""
    broker: BrokerConfig = field(default_factory=BrokerConfig)
    trading: TradingConfig = field(default_factory=TradingConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
    time_sync: TimeSyncConfig = field(default_factory=TimeSyncConfig)
    
    # Пути к директориям
    logs_dir: str = "logs"
    data_dir: str = "data"
    reports_dir: str = "reports"
    sounds_dir: str = "sounds"
    screenshots_dir: str = "screenshots"
    backtest_dir: str = "backtest"


class ConfigManager:
    """Менеджер конфигурации"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path(__file__).parent.parent / "config" / "config.json"
        self._config: Optional[AppConfig] = None
        self._language: str = Language.RUSSIAN.value
    
    def load(self) -> AppConfig:
        """Загрузка конфигурации из JSON файла"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self._config = self._parse_config(data)
                print(f"✅ Конфигурация загружена: {self.config_path}")
                
            except Exception as e:
                print(f"⚠️  Ошибка загрузки конфигурации: {e}")
                self._config = AppConfig()
        else:
            print(f"⚠️  Конфигурационный файл не найден, используем значения по умолчанию")
            self._config = AppConfig()
        
        return self._config
    
    def save(self) -> bool:
        """Сохранение конфигурации в JSON файл"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "broker": self._to_dict(self._config.broker),
                "trading": self._to_dict(self._config.trading),
                "strategy": self._to_dict(self._config.strategy),
                "notifications": self._to_dict(self._config.notifications),
                "display": self._to_dict(self._config.display),
                "time_sync": self._to_dict(self._config.time_sync)
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Конфигурация сохранена: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
    
    @property
    def config(self) -> AppConfig:
        """Текущая конфигурация"""
        if self._config is None:
            self.load()
        return self._config
    
    @property
    def language(self) -> str:
        """Текущий язык"""
        return self._language
    
    def set_language(self, lang: str):
        """Установка языка"""
        if lang in [Language.RUSSIAN.value, Language.ENGLISH.value]:
            self._language = lang
            self._config.display.language = lang
    
    def t(self, key: str) -> str:
        """Получение перевода по ключу"""
        translations = TRANSLATIONS.get(self._language, TRANSLATIONS[Language.ENGLISH.value])
        return translations.get(key, key)
    
    def _parse_config(self, data: Dict[str, Any]) -> AppConfig:
        """Парсинг словаря в AppConfig"""
        config = AppConfig()
        
        # Broker
        if "broker" in data:
            for k, v in data["broker"].items():
                if hasattr(config.broker, k):
                    setattr(config.broker, k, v)
        
        # Trading
        if "trading" in data:
            for k, v in data["trading"].items():
                if hasattr(config.trading, k):
                    setattr(config.trading, k, v)
        
        # Strategy
        if "strategy" in data:
            for k, v in data["strategy"].items():
                if hasattr(config.strategy, k):
                    setattr(config.strategy, k, v)
        
        # Notifications
        if "notifications" in data:
            for k, v in data["notifications"].items():
                if hasattr(config.notifications, k):
                    setattr(config.notifications, k, v)
        
        # Display
        if "display" in data:
            for k, v in data["display"].items():
                if hasattr(config.display, k):
                    setattr(config.display, k, v)
            self._language = config.display.language
        
        # Time Sync
        if "time_sync" in data:
            for k, v in data["time_sync"].items():
                if hasattr(config.time_sync, k):
                    setattr(config.time_sync, k, v)
        
        return config
    
    def _to_dict(self, obj) -> Dict[str, Any]:
        """Конвертация dataclass в словарь"""
        if hasattr(obj, '__dataclass_fields__'):
            import dataclasses
            return dataclasses.asdict(obj)
        return obj.__dict__


# Глобальный экземпляр менеджера конфигурации
config_manager = ConfigManager()


def get_config() -> AppConfig:
    """Получение текущей конфигурации (глобальная функция)"""
    return config_manager.config


def t(key: str) -> str:
    """Получение перевода (глобальная функция)"""
    return config_manager.t(key)


if __name__ == "__main__":
    # Тестирование
    cm = ConfigManager()
    cfg = cm.load()
    
    print(f"\n{'='*60}")
    print(f"🥇 Golden Emirat v2.0 - Configuration Test")
    print(f"{'='*60}\n")
    
    print(f"Language: {cm.language}")
    print(f"Symbol: {cfg.trading.symbol}")
    print(f"Lot Size: {cfg.trading.lot_size}")
    print(f"Risk: {cfg.trading.max_risk_percent}%")
    print(f"\nTranslation test: {t('app.name')} - {t('app.subtitle')}")
