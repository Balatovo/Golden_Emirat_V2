#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Emirat v2.0 - Trade Executor Module
==================================================
Модуль исполнения ордеров через MetaTrader 4/5 API.
Поддержка MT5 (официальный API) и MT4 (через ZeroMQ мост).
"""

import time
import threading
from dataclasses import dataclass
from typing import Optional, List, Dict, Callable, Any
from enum import Enum
from abc import ABC, abstractmethod

from .logger_setup import get_logger

log = get_logger(__name__)


class OrderType(Enum):
    """Типы ордеров"""
    BUY = "BUY"
    SELL = "SELL"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"


class OrderStatus(Enum):
    """Статусы ордеров"""
    PENDING = "pending"
    OPENED = "opened"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    PARTIAL = "partial"


class PositionType(Enum):
    """Типы позиций"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Order:
    """Торговый ордер"""
    order_id: int
    symbol: str
    order_type: OrderType
    volume: float
    price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    comment: str
    status: OrderStatus = OrderStatus.PENDING
    ticket: Optional[int] = None
    open_time: Optional[float] = None
    close_time: Optional[float] = None
    close_price: Optional[float] = None
    commission: float = 0.0
    swap: float = 0.0
    profit: float = 0.0


@dataclass
class Position:
    """Открытая позиция"""
    ticket: int
    symbol: str
    position_type: PositionType
    volume: float
    price_open: float
    price_current: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    profit: float = 0.0
    comment: str = ""
    open_time: float = 0.0


@dataclass
class TradeResult:
    """Результат торговой операции"""
    success: bool
    order: Optional[Order] = None
    position: Optional[Position] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


class BaseTradeExecutor(ABC):
    """
    Абстрактный базовый класс исполнителя торговых операций.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """Подключение к торговому терминалу"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Отключение от терминала"""
        pass
    
    @abstractmethod
    def send_order(self, order: Order) -> TradeResult:
        """Отправка ордера"""
        pass
    
    @abstractmethod
    def close_order(self, ticket: int, volume: Optional[float] = None) -> TradeResult:
        """Закрытие ордера/позиции"""
        pass
    
    @abstractmethod
    def close_all(self, symbol: Optional[str] = None) -> List[TradeResult]:
        """Закрытие всех позиций"""
        pass
    
    @abstractmethod
    def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Получение списка открытых позиций"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """Получение информации о счёте"""
        pass
    
    @abstractmethod
    def get_server_time(self) -> Optional[float]:
        """Получение времени сервера"""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Проверка соединения"""
        pass


class MT5TradeExecutor(BaseTradeExecutor):
    """
    Исполнитель торговых операций для MetaTrader 5.
    Использует официальное Python API MetaTrader5.
    """
    
    def __init__(self, path: str, login: int, password: str, server: str):
        self.path = path
        self.login = login
        self.password = password
        self.server = server
        self._connected = False
        self._mt5 = None
        self._order_counter = 100000
    
    def connect(self) -> bool:
        """Подключение к MT5 терминалу"""
        try:
            import MetaTrader5 as mt5
            
            if not mt5.initialize(path=self.path):
                log.error(f"initialize() failed, error code: {mt5.last_error()}")
                return False
            
            if not mt5.login(login=self.login, password=self.password, server=self.server):
                log.error(f"login() failed, error code: {mt5.last_error()}")
                mt5.shutdown()
                return False
            
            self._mt5 = mt5
            self._connected = True
            log.success(f"Connected to MT5 | Server: {server} | Login: {login}")
            return True
            
        except ImportError:
            log.error("MetaTrader5 package not installed! Run: pip install MetaTrader5")
            return False
        except Exception as e:
            log.error(f"Connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Отключение от MT5"""
        try:
            if self._mt5:
                self._mt5.shutdown()
            self._connected = False
            log.info("Disconnected from MT5")
            return True
        except Exception as e:
            log.error(f"Disconnect error: {e}")
            return False
    
    def is_connected(self) -> bool:
        return self._connected and (self._mt5 is not None) if self._mt5 else False
    
    def send_order(self, order: Order) -> TradeResult:
        """Отправка ордера в MT5"""
        start_time = time.time()
        
        if not self.is_connected():
            return TradeResult(success=False, error="Not connected to MT5")
        
        try:
            symbol_info = mt5.symbol_info(order.symbol)
            if symbol_info is None:
                return TradeResult(success=False, error=f"Symbol {order.symbol} not found")
            
            # Определение типа ордера
            if order.order_type in [OrderType.BUY, OrderType.SELL]:
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": order.symbol,
                    "volume": order.volume,
                    "type": mt5.ORDER_TYPE_BUY if order.order_type == OrderType.BUY else mt5.ORDER_TYPE_SELL,
                    "price": order.price or symbol_info.bid,
                    "sl": order.stop_loss,
                    "tp": order.take_profit,
                    "comment": order.comment,
                    "deviation": 10,
                    "magic": 20240101,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,
                }
            else:
                # Limit/Stop orders
                order_type_map = {
                    OrderType.BUY_LIMIT: mt5.ORDER_TYPE_BUY_LIMIT,
                    OrderType.SELL_LIMIT: mt5.ORDER_TYPE_SELL_LIMIT,
                    OrderType.BUY_STOP: mt5.ORDER_TYPE_BUY_STOP,
                    OrderType.SELL_STOP: mt5.ORDER_TYPE_SELL_STOP,
                }
                request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": order.symbol,
                    "volume": order.volume,
                    "type": order_type_map.get(order.order_type, mt5.ORDER_TYPE_BUY),
                    "price": order.price,
                    "sl": order.stop_loss,
                    "tp": order.take_profit,
                    "comment": order.comment,
                    "deviation": 10,
                    "magic": 20240101,
                }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.RET_CODE_OK:
                return TradeResult(
                    success=False,
                    error=f"Order failed: {result.retcode} - {result.comment}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            
            order.ticket = result.order
            order.status = OrderStatus.FILLED
            order.open_time = time.time()
            
            return TradeResult(
                success=True,
                order=order,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            log.error(f"Send order error: {e}")
            return TradeResult(success=False, error=str(e))
    
    def close_order(self, ticket: int, volume: Optional[float] = None) -> TradeResult:
        """Закрытие позиции по билету"""
        start_time = time.time()
        
        if not self.is_connected():
            return TradeResult(success=False, error="Not connected")
        
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                return TradeResult(success=False, error=f"Position {ticket} not found")
            
            close_volume = volume or position[0].volume
            
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position[0].symbol,
                "volume": close_volume,
                "type": mt5.ORDER_TYPE_BUY if position[0].type == mt5.POSITION_TYPE_SELL else mt5.ORDER_TYPE_SELL,
                "position": ticket,
                "price": position[0].price_current,
                "deviation": 10,
                "magic": 20240101,
            }
            
            result = mt5.order_send(request)
            
            if result.retcode != mt5.RET_CODE_OK:
                return TradeResult(success=False, error=f"Close failed: {result.comment}")
            
            return TradeResult(
                success=True,
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            log.error(f"Close order error: {e}")
            return TradeResult(success=False, error=str(e))
    
    def close_all(self, symbol: Optional[str] = None) -> List[TradeResult]:
        """Закрытие всех позиций"""
        results = []
        
        if not self.is_connected():
            return [TradeResult(success=False, error="Not connected")]
        
        positions = self.get_positions(symbol)
        
        for pos in positions:
            result = self.close_order(pos.ticket)
            results.append(result)
        
        return results
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Получение открытых позиций"""
        positions = []
        
        if not self.is_connected():
            return positions
        
        try:
            if symbol:
                positions_mt5 = mt5.positions_get(symbol=symbol)
            else:
                positions_mt5 = mt5.positions_get()
            
            for pos in positions_mt5:
                position = Position(
                    ticket=pos.ticket,
                    symbol=pos.symbol,
                    position_type=PositionType.LONG if pos.type == mt5.POSITION_TYPE_BUY else PositionType.SHORT,
                    volume=pos.volume,
                    price_open=pos.price_open,
                    price_current=pos.price_current,
                    stop_loss=pos.sl,
                    take_profit=pos.tp,
                    profit=pos.profit,
                    comment=pos.comment,
                    open_time=pos.time
                )
                positions.append(position)
                
        except Exception as e:
            log.error(f"Get positions error: {e}")
        
        return positions
    
    def get_account_info(self) -> Dict[str, Any]:
        """Получение информации о счёте"""
        if not self.is_connected():
            return {}
        
        try:
            account_info = mt5.account_info()
            return {
                "balance": account_info.balance,
                "equity": account_info.equity,
                "margin": account_info.margin,
                "free_margin": account_info.margin_free,
                "profit": account_info.profit,
                "currency": account_info.currency,
                "leverage": account_info.leverage,
            }
        except Exception as e:
            log.error(f"Get account info error: {e}")
            return {}
    
    def get_server_time(self) -> Optional[float]:
        """Получение времени сервера MT5"""
        if not self.is_connected():
            return None
        
        try:
            tick = mt5.symbol_info_tick("EURUSD")  # Любой символ для получения времени
            if tick:
                return tick[0].time
        except:
            pass
        return None


class MT4TradeExecutor(BaseTradeExecutor):
    """
    Исполнитель торговых операций для MetaTrader 4.
    Использует ZeroMQ мост для связи с MT4.
    """
    
    def __init__(self, zmq_host: str = "tcp://127.0.0.1:5555"):
        self.zmq_host = zmq_host
        self._socket = None
        self._context = None
        self._connected = False
        self._order_counter = 200000
    
    def connect(self) -> bool:
        """Подключение к MT4 через ZeroMQ"""
        try:
            import zmq
            
            self._context = zmq.Context()
            self._socket = self._context.socket(zmq.REQ)
            self._socket.setsockopt(zmq.RCVTIMEO, 5000)  # 5 сек таймаут
            self._socket.connect(self.zmq_host)
            
            # Тестовое сообщение
            self._socket.send_string(b"PING")
            response = self._socket.recv_string()
            
            if response == "PONG":
                self._connected = True
                log.success(f"Connected to MT4 via ZMQ at {zmq_host}")
                return True
            else:
                log.error(f"Invalid response: {response}")
                return False
                
        except ImportError:
            log.error("pyzmq not installed! Run: pip install pyzmq")
            return False
        except Exception as e:
            log.error(f"ZMQ connection error: {e}")
            return False
    
    def disconnect(self) -> bool:
        """Отключение от MT4"""
        try:
            if self._socket:
                self._socket.close()
            if self._context:
                self._context.term()
            self._connected = False
            log.info("Disconnected from MT4")
            return True
        except Exception as e:
            log.error(f"Disconnect error: {e}")
            return False
    
    def is_connected(self) -> bool:
        return self._connected
    
    def send_order(self, order: Order) -> TradeResult:
        """Отправка ордера в MT4 через ZMQ"""
        start_time = time.time()
        
        if not self.is_connected():
            return TradeResult(success=False, error="Not connected to MT4")
        
        try:
            import json
            
            request_data = {
                "action": "ORDER",
                "id": self._order_counter,
                "symbol": order.symbol,
                "volume": order.volume,
                "type": order.order_type.value,
                "price": order.price,
                "sl": order.stop_loss,
                "tp": order.take_profit,
                "comment": order.comment,
            }
            
            self._socket.send_json(request_data)
            response = self._socket.recv_json()
            
            self._order_counter += 1
            
            if response.get("success"):
                order.ticket = response.get("ticket")
                order.status = OrderStatus.FILLED
                return TradeResult(
                    success=True,
                    order=order,
                    execution_time_ms=(time.time() - start_time) * 1000
                )
            else:
                return TradeResult(
                    success=False,
                    error=response.get("error", "Unknown error"),
                    execution_time_ms=(time.time() - start_time) * 1000
                )
                
        except Exception as e:
            log.error(f"MT4 send order error: {e}")
            return TradeResult(success=False, error=str(e))
    
    def close_order(self, ticket: int, volume: Optional[float] = None) -> TradeResult:
        """Закрытие позиции MT4"""
        start_time = time.time()
        
        if not self.is_connected():
            return TradeResult(success=False, error="Not connected")
        
        try:
            request_data = {
                "action": "CLOSE",
                "ticket": ticket,
                "volume": volume,
            }
            
            self._socket.send_json(request_data)
            response = self._socket.recv_json()
            
            return TradeResult(
                success=response.get("success", False),
                error=response.get("error"),
                execution_time_ms=(time.time() - start_time) * 1000
            )
            
        except Exception as e:
            log.error(f"MT4 close error: {e}")
            return TradeResult(success=False, error=str(e))
    
    def close_all(self, symbol: Optional[str] = None) -> List[TradeResult]:
        """Закрытие всех позиций MT4"""
        results = []
        
        if not self.is_connected():
            return [TradeResult(success=False, error="Not connected")]
        
        try:
            self._socket.send_json({"action": "GET_POSITIONS", "symbol": symbol})
            positions = self._socket.recv_json().get("positions", [])
            
            for pos in positions:
                result = self.close_order(pos["ticket"])
                results.append(result)
                
        except Exception as e:
            log.error(f"MT4 close all error: {e}")
            results.append(TradeResult(success=False, error=str(e)))
        
        return results
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Position]:
        """Получение позиций MT4"""
        positions = []
        
        if not self.is_connected():
            return positions
        
        try:
            self._socket.send_json({"action": "GET_POSITIONS", "symbol": symbol})
            response = self._socket.recv_json()
            
            for pos_data in response.get("positions", []):
                pos = Position(
                    ticket=pos_data["ticket"],
                    symbol=pos_data["symbol"],
                    position_type=PositionType.LONG if pos_data["type"] == "buy" else PositionType.SHORT,
                    volume=pos_data["volume"],
                    price_open=pos_data["price_open"],
                    price_current=pos_data["price_current"],
                    profit=pos_data.get("profit", 0),
                    comment=pos_data.get("comment", "")
                )
                positions.append(pos)
                
        except Exception as e:
            log.error(f"MT4 get positions error: {e}")
        
        return positions
    
    def get_account_info(self) -> Dict[str, Any]:
        """Получение информации о счёте MT4"""
        if not self.is_connected():
            return {}
        
        try:
            self._socket.send_json({"action": "ACCOUNT_INFO"})
            return self._socket.recv_json()
        except Exception as e:
            log.error(f"MT4 account info error: {e}")
            return {}
    
    def get_server_time(self) -> Optional[float]:
        """Получение времени MT4"""
        if not self.is_connected():
            return None
        
        try:
            self._socket.send_json({"action": "SERVER_TIME"})
            response = self._socket.recv_json()
            return response.get("time")
        except:
            return None


# Factory function
def create_executor(broker_type: str, **kwargs) -> BaseTradeExecutor:
    """
    Фабричная функция создания исполнителя.
    
    Args:
        broker_type: Тип брокера ('mt5' или 'mt4')
        **kwargs: Параметры подключения
        
    Returns:
        Экземпляр BaseTradeExecutor
    """
    if broker_type.lower() == 'mt5':
        return MT5TradeExecutor(**kwargs)
    elif broker_type.lower() == 'mt4':
        return MT4TradeExecutor(**kwargs)
    else:
        raise ValueError(f"Unsupported broker type: {broker_type}")


if __name__ == "__main__":
    # Тестирование MT5 (закомментировано, требует запущенного MT5)
    # executor = MT5TradeExecutor(
    #     path=r"C:\Program Files\MetaTrader 5\terminal64.exe",
    #     login=12345678,
    #     password="password",
    #     server="ICMarkets-Demo"
    # )
    
    print("✅ Trade Executor module loaded successfully")
    print("Supported brokers: MT5 (official API), MT4 (via ZeroMQ)")
