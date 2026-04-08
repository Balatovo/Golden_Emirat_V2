#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Emirat v2.0 - Data Manager Module
=============================================
Модуль управления рыночными данными:
- Загрузка исторических данных
- Хранение тиковых данных
- Обработка свечей (OHLCV)
- Экспорт/импорт данных
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from .logger_setup import get_logger

log = get_logger(__name__)


class Timeframe(Enum):
    """Таймфреймы"""
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"
    MN = "MN"


@dataclass
class Candle:
    """Свеча (бар OHLCV)"""
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str = "H1"
    
    def to_dict(self) -> dict:
        return {
            "time": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume
        }


@dataclass
class TickData:
    """Тиковые данные"""
    timestamp: float
    symbol: str
    bid: float
    ask: float
    last: float
    volume: float
    
    @property
    def mid(self) -> float:
        """Средняя цена"""
        return (self.bid + self.ask) / 2


class DataManager:
    """
    Менеджер данных для Golden Emirat v2.0
    
    Функции:
    - Загрузка исторических данных из разных источников
    - Кэширование данных в памяти
    - Сохранение/загрузка данных
    - Расчёт индикаторов
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, pd.DataFrame] = {}
        
        log.info(f"DataManager initialized. Data directory: {self.data_dir.absolute()}")
    
    def load_csv_data(
        self,
        filepath: str,
        symbol: str,
        timeframe: str = "H1",
        date_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Загрузка данных из CSV файла.
        
        Args:
            filepath: Путь к CSV файлу
            symbol: Символ инструмента
            timeframe: Таймфрейм
            date_columns: Колонки с датами для парсинга
            
        Returns:
            DataFrame с данными
        """
        try:
            df = pd.read_csv(filepath)
            
            if date_columns:
                for col in date_columns:
                    df[col] = pd.to_datetime(df[col])
            
            df.columns = [col.lower() for col in df.columns]
            
            log.info(f"Loaded {len(df)} rows from {filepath}")
            return df
            
        except Exception as e:
            log.error(f"Error loading CSV: {e}")
            return pd.DataFrame()
    
    def load_historical_data_yfinance(
        self,
        symbol: str,
        timeframe: str = "H1",
        period: str = "1y",
        interval: str = "1h"
    ) -> pd.DataFrame:
        """
        Загрузка исторических данных через yfinance.
        
        Args:
            symbol: Символ (например, 'GC=F' для золота)
            timeframe: Таймфрейм
            period: Период ('1mo', '3mo', '1y', '5y')
            interval: Интервал свечей
            
        Returns:
            DataFrame с OHLCV данными
        """
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            df = yf.download(period=period, interval=interval)
            
            df.reset_index(inplace=True)
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            log.info(f"Downloaded {len(df)} candles from Yahoo Finance ({symbol})")
            return df
            
        except ImportError:
            log.warning("yfinance not installed! Run: pip install yfinance")
            return self._generate_sample_data(symbol, timeframe)
        except Exception as e:
            log.error(f"Error downloading from yfinance: {e}")
            return self._generate_sample_data(symbol, timeframe)
    
    def load_historical_data_ccxt(
        self,
        exchange_id: str,
        symbol: str,
        timeframe: str = "1h",
        since: Optional[datetime] = None,
        limit: int = 1000
    ) -> pd.DataFrame:
        """
        Загрузка данных через CCXT.
        
        Args:
           _exchange_id: ID биржи ('bybit', 'binance', etc.)
            symbol: Пара (например, 'XAU/USD')
            timeframe: Таймфрейм
            since: Начальная дата
            limit: Количество свечей
            
        Returns:
            DataFrame с OHLCV данными
        """
        try:
            import ccxt
            
            exchange = getattr(ccxt, exchange_id)()
            
            # Конвертация таймфрейма
            tf_map = {
                "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
                "1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"
            }
            ccxt_tf = tf_map.get(timeframe, "1h")
            
            # Загрузка OHLCV
            ohlcv = exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=ccxt_tf,
                since=since,
                limit=limit
            )
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            log.info(f"Downloaded {len(df)} candles from CCXT ({exchange_id}:{symbol})")
            return df
            
        except ImportError:
            log.warning("ccxt not installed! Run: pip install ccxt")
            return self._generate_sample_data(symbol, timeframe)
        except Exception as e:
            log.error(f"Error downloading from CCXT: {e}")
            return self._generate_sample_data(symbol, timeframe)
    
    def _generate_sample_data(
        self,
        symbol: str = "XAU/USD",
        timeframe: str = "H1",
        num_candles: int = 500
    ) -> pd.DataFrame:
        """
        Генерация тестовых данных (если источники недоступны).
        """
        log.warning(f"Generating sample data for {symbol} {timeframe}")
        
        np.random.seed(42)
        
        now = datetime.now()
        timestamps = [
            (now - timedelta(hours=num_candles - i)).timestamp()
            for i in range(num_candles)
        ]
        
        base_price = 2065.0
        prices = np.cumsum(np.random.randn(num_candles) * 2) + base_price
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices + np.random.randn(num_candles) * 0.5,
            'high': prices + abs(np.random.randn(num_candles)) * 3,
            'low': prices - abs(np.random.randn(num_candles)) * 3,
            'close': prices,
            'volume': np.random.randint(100, 10000, num_candles)
        })
        
        return df
    
    def cache_data(self, key: str, data: pd.DataFrame):
        """Кэширование данных в памяти"""
        self._cache[key] = data
        log.debug(f"Cached data: {key} ({len(data)} rows)")
    
    def get_cached_data(self, key: str) -> Optional[pd.DataFrame]:
        """Получение кэшированных данных"""
        return self._cache.get(key)
    
    def save_data_to_csv(
        self,
        df: pd.DataFrame,
        filename: str,
        include_index: bool = False
    ) -> str:
        """
        Сохранение DataFrame в CSV.
        
        Returns:
        Путь к сохранённому файлу
        """
        filepath = self.data_dir / filename
        df.to_csv(filepath, index=include_index, encoding='utf-8')
        log.info(f"Saved data to {filepath}")
        return str(filepath)
    
    def calculate_indicators(
        self,
        df: pd.DataFrame,
        indicators: List[str] = None
    ) -> pd.DataFrame:
        """
        Расчёт технических индикаторов.
        
        Args:
            df: DataFrame с OHLCV данными
            indicators: Список индикаторов ['sma', 'ema', 'rsi', 'macd', 'bb', 'atr']
            
        Returns:
            DataFrame с добавленными колонками индикаторов
        """
        if indicators is None:
            indicators = ['sma_20', 'sma_50', 'ema_9', 'ema_21', 'rsi_14', 'macd', 'bb', 'atr']
        
        result = df.copy()
        
        for ind in indicators:
            ind_lower = ind.lower()
            
            if 'sma_' in ind_lower:
                period = int(ind.split('_')[-1])
                result[f'sma_{period}'] = result['close'].rolling(window=period).mean()
            
            elif 'ema_' in ind_lower:
                period = int(ind.split('_')[-1])
                result[f'ema_{period}'] = result['close'].ewm(span=period, adjust=False).mean()
            
            elif 'rsi_' in ind_lower:
                period = int(ind.split('_')[-1])
                delta = result['close'].diff()
                gain = (delta.where(delta > 0) * 1).rolling(window=period).mean()
                loss = (-delta.where(delta < 0) * 1).rolling(window=period).mean()
                rs = gain / loss
                result[f'rsi_{period} = 100 - (100 / (1 + rs))
            
            elif ind_lower == 'macd':
                ema12 = result['close'].ewm(span=12).mean()
                ema26 = result['close'].ewm(span=26).mean()
                result['macd_line'] = ema12 - ema26
                result['macd_signal'] = result['macd_line'].ewm(span=9).mean()
                result['macd_histogram'] = result['macd_line'] - result['macd_signal']
            
            elif ind_lower == 'bb':
                period = 20
                std_mult = 2.0
                sma = result['close'].rolling(window=period).mean()
                std = result['close'].rolling(window=period).std()
                result['bb_upper'] = sma + std_mult * std
                result['bb_middle'] = sma
                result['bb_lower'] = sma - std_mult * std
            
            elif ind_lower == 'atr':
                period = 14
                high_low = result['high'] - result['low']
                result['atr'] = high_low.rolling(window=period).mean()
        
        log.debug(f"Calculated indicators: {list(result.columns)}")
        return result
    
    def resample_dataframe(
        self,
        df: pd.DataFrame,
        target_timeframe: str
    ) -> pd.DataFrame:
        """
        Изменение таймфрейма DataFrame.
        
        Args:
            df: Исходной DataFrame
            target_timeframe: Целевой таймфрейм
            
        Returns:
            Resampled DataFrame
        """
        tf_map = {
            'M1': '1min', 'M5': '5min', 'M15': '15min',
            'M30': '30min', 'H1': '1h', 'H4': '4h',
            'D1': '1D', 'W1': 'W'
        }
        
        rule = tf_map.get(target_timeframe, '1h')
        
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        
        resampled = df.resample(rule).agg(ohlc_dict)
        resampled.dropna(inplace=True)
        
        return resampled
    
    def get_latest_candle(self, df: pd.DataFrame) -> Optional[Candle]:
        """Получение последней свечи из DataFrame"""
        if df.empty:
            return None
        
        last = df.iloc[-1]
        return Candle(
            timestamp=pd.Timestamp(last['timestamp']).timestamp(),
            open=last['open'],
            high=last['high'],
            low=last['low'],
            close=last['close'],
            volume=last['volume']
        )


if __name__ == "__main__":
    # Тестирование
    dm = DataManager()
    
    # Генерация тестовых данных
    df = dm._generate_sample_data("XAU/USD", "H1", 100)
    
    # Расчёт индикаторов
    df_with_indicators = dm.calculate_indicators(df)
    
    print(f"\n{'='*60}")
    print(f"📊 Data Manager Test")
    print(f"{'='*60}\n")
    
    print(f"Shape: {df_with_indicators.shape}")
    print(f"Columns: {list(df_with_indicators.columns)}")
    print(f"\nLast candle:\n{df_with_indicors.tail(1).to_string()}")
