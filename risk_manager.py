#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Emirat v2.0 - Risk Manager Module
==========================================
Модуль управления рисками: расчёт позиции, стоп-лосс, тейк-профит.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum
import math


class RiskLevel(Enum):
    """Уровни риска"""
    CONSERVATIVE = "conservative"  # 1% на сделку
    MODERATE = "moderate"          # 2% на сделку
    AGGRESSIVE = "aggressive"        # 3% на сделку


@dataclass
class PositionSize:
    """Информация о размере позиции"""
    lots: float
    volume: float  # Объём в единицах базового актива
    risk_amount: float  # Риск в валюте депозита
    stop_loss_price: float
    take_profit_price: float
    reward_to_risk: float  # Соотношение риск/прибыль


@dataclass
class RiskParameters:
    """Параметры риска"""
    account_balance: float
    risk_per_trade_percent: float  # % от баланса на сделку
    max_daily_loss_percent: float   # Макс. дневная потеря %
    max_open_positions: int          # Макс. открытых позиций
    current_open_positions: int = 0
    today_pnl: float = 0.0
    max_spread_points: float = 50.0  # Макс. допустимый спред


class RiskManager:
    """
    Менеджер рисков для Golden Emirat v2.0
    
    Функции:
    - Расчёт размера позиции по риску
    - Расчёт Stop Loss и Take Profit
    - Проверка допустимости сделки
    - Контроль дневных убытков
    """
    
    def __init__(self, params: RiskParameters):
        self.params = params
        self.initial_balance = params.account_balance
        self.daily_loss_limit = params.account_balance * (params.max_daily_loss_percent / 100)
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_distance_points: float,
        point_value: float = 0.01  # Стоимость пункта для XAU/USD
    ) -> PositionSize:
        """
        Расчёт размера позиции на основе риска.
        
        Args:
            entry_price: Цена входа
            stop_loss_distance_points: Расстояние до SL в пунктах
            point_value: Стоимость одного пункта
            
        Returns:
            PositionSize с деталями
        """
        # Риск в валюте депозита
        risk_amount = self.params.account_balance * (self.params.risk_per_trade_percent / 100)
        
        # Расстояние до SL в цене
        sl_distance_price = stop_loss_distance_points * point_value
        
        # Объём в единицах актива (для XAU/USD - это лоты)
        volume = risk_amount / sl_distance_price if sl_distance_price > 0 else 0
        
        # Округление лотов (стандартные размеры для золота)
        lots = self._round_lot_size(volume)
        
        # Пересчёт реального риска
        actual_risk = lots * sl_distance_price
        
        # Расчёт цен SL и TP
        stop_loss_price = entry_price - (stop_loss_distance_points * point_value)
        take_profit_price = entry_price + (stop_loss_distance_points * point_value * 2)  # R:R = 1:2
        
        # Reward to Risk ratio
        rr_ratio = stop_loss_distance_points * 2 / stop_loss_distance_points if stop_loss_distance_points > 0 else 0
        
        return PositionSize(
            lots=lots,
            volume=volume,
            risk_amount=actual_risk,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price,
            reward_to_risk=rr_ratio
        )
    
    def calculate_position_size_by_amount(
        self,
        entry_price: float,
        risk_amount: float,
        stop_loss_distance_points: float,
        point_value: float = 0.01
    ) -> PositionSize:
        """
        Расчёт позиции по фиксированной сумме риска.
        """
        sl_distance_price = stop_loss_distance_points * point_value
        volume = risk_amount / sl_distance_price if sl_distance_price > 0 else 0
        lots = self._round_lot_size(volume)
        
        return PositionSize(
            lots=lots,
            volume=volume,
            risk_amount=risk_amount,
            stop_loss_price=entry_price - (stop_loss_distance_points * point_value),
            take_profit_price=entry_price + (stop_loss_distance_points * point_value * 2),
            reward_to_risk=2.0
        )
    
    def is_trade_allowed(
        self,
        spread_points: float,
        entry_price: Optional[float] = None
    ) -> Tuple[bool, str]:
        """
        Проверка разрешения на открытие сделки.
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Проверка спреда
        if spread_points > self.params.max_spread_points:
            return False, f"Слишком большой спред: {spread_points} > {self.params.max_spread_points}"
        
        # Проверка количества открытых позиций
        if self.params.current_open_positions >= self.params.max_open_positions:
            return False, f"Достигнут лимит открытых позиций: {self.params.current_open_positions}"
        
        # Проверка дневного убытка
        if abs(self.params.today_pnl) >= self.daily_loss_limit:
            return False, f"Достигнут дневной лимит потерь: ${abs(self.params.today_pnl):.2f}"
        
        return True, "Разрешено"
    
    def calculate_max_drawdown(self, equity_curve: list) -> dict:
        """
        Расчёт максимальной просадки.
        
        Args:
            equity_curve: Список значений equity
            
        Returns:
            Словарь с метриками просадки
        """
        if not equity_curve or len(equity_curve) < 2:
            return {"max_drawdown": 0, "max_drawdown_percent": 0, "peak": 0, "trough": 0}
        
        peak = equity_curve[0]
        max_dd = 0
        max_dd_pct = 0
        trough = peak
        
        for value in equity_curve:
            if value > peak:
                peak = value
            
            drawdown = peak - value
            drawdown_pct = (drawdown / peak * 100) if peak > 0 else 0
            
            if drawdown > max_dd:
                max_dd = drawdown
                max_dd_pct = drawdown_pct
                trough = value
        
        return {
            "max_drawdown": round(max_dd, 2),
            "max_drawdown_percent": round(max_dd_pct, 2),
            "peak": round(peak, 2),
            "trough": round(trough, 2)
        }
    
    def calculate_position_risk(
        self,
        entry_price: float,
        current_price: float,
        lot_size: float,
        direction: str  # "buy" or "sell"
    ) -> dict:
        """
        Расчёт текущего риска позиции.
        
        Returns:
            Словарь с метриками риска
        """
        if direction.lower() == "buy":
            pnl = (current_price - entry_price) * lot_size * 100  # Для XAU/USD
            unrealized_loss = min(0, (current_price - entry_price) * lot_size * 100)
        else:
            pnl = (entry_price - current_price) * lot_size * 100
            unrealized_loss = min(0, (entry_price - current_price) * lot_size * 100)
        
        risk_percent = (unrealized_loss / self.params.account_balance * 100) if self.params.account_balance > 0 else 0
        
        return {
            "pnl": round(pnl, 2),
            "unrealized_loss": round(unrealized_loss, 2),
            "risk_percent": round(risk_percent, 2),
            "is_acceptable": risk_percent < self.params.risk_per_trade_percent * 2  # 2x риск допустим
        }
    
    def _round_lot_size(self, lots: float) -> float:
        """
        Округление размера лота до стандартного значения.
        
        Стандартные размеры для золота:
        0.01, 0.02, 0.05, 0.1, 0.5, 1.0, etc.
        """
        if lots <= 0.01:
            return 0.01
        elif lots <= 0.05:
            return round(lots * 20) / 20  # До 0.01
        elif lots <= 0.1:
            return round(lots * 10) / 10  # До 0.02
        elif lots <= 1.0:
            return round(lots * 2) / 2  # До 0.05
        else:
            return round(lots)  # До 0.1
    
    def get_risk_summary(self) -> dict:
        """
        Получение сводки по рискам.
        """
        daily_loss_used = abs(self.params.today_pnl) if self.params.today_pnl < 0 else 0
        daily_loss_remaining = self.daily_loss_limit - daily_loss_used
        
        return {
            "account_balance": self.params.account_balance,
            "risk_per_trade": f"{self.params.risk_per_trade_percent}%",
            "daily_loss_limit": f"${self.daily_loss_limit:.2f}",
            "daily_loss_used": f"${daily_loss_used:.2f}",
            "daily_loss_remaining": f"${daily_loss_remaining:.2f}",
            "open_positions": self.params.current_open_positions,
            "max_positions": self.params.max_open_positions,
            "initial_balance": self.initial_balance
        }


if __name__ == "__main__":
    # Тестирование
    params = RiskParameters(
        account_balance=10000,
        risk_per_trade_percent=2.0,
        max_daily_loss_percent=5.0,
        max_open_positions=3,
        max_spread_points=50
    )
    
    rm = RiskManager(params)
    
    pos = rm.calculate_position_size(
        entry_price=2065.50,
        stop_loss_distance_points=500
    )
    
    print(f"\n{'='*60}")
    print(f"🛡️ Risk Manager Test")
    print(f"{'='*60}\n")
    
    print(f"Lots: {pos.lots}")
    print(f"Risk Amount: ${pos.risk_amount:.2f}")
    print(f"SL Price: ${pos.stop_loss_price:.2f}")
    print(f"TP Price: ${pos.take_profit_price:.2f}")
    print(f"R:R Ratio: {pos.reward_to_risk}:1")
    
    allowed, reason = rm.is_trade_allowed(spread_points=30)
    print(f"\nTrade Allowed: {allowed} - {reason}")
