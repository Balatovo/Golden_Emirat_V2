"""Движок бэктестинга."""
import pandas as pd
from loguru import logger
from strategies.base_strategy import BaseStrategy
from core.risk_manager import RiskManager

class BacktestEngine:
    def __init__(self, strategy: BaseStrategy, data: pd.DataFrame, initial_balance: float = 10000):
        self.strategy = strategy
        self.data = data
        self.risk_mgr = RiskManager(initial_balance, 2.0)
        self.balance = initial_balance
        self.equity_curve = []
        self.trades = []

    def run(self) -> dict:
        logger.info(f"Запуск бэктеста: {self.strategy.name}")
        for i in range(50, len(self.data)):
            window = self.data.iloc[i-50:i]
            signal = self.strategy.generate_signal(window)
            
            if signal['action'] != 'HOLD':
                price = self.data['close'].iloc[i]
                sl, tp = signal['sl'], signal['tp']
                
                # Симуляция (упрощенная: проверяем TP/SL на следующей свече)
                next_low = self.data['low'].iloc[i+1] if i+1 < len(self.data) else price
                next_high = self.data['high'].iloc[i+1] if i+1 < len(self.data) else price
                
                if signal['action'] == 'BUY':
                    if next_low <= sl: self.balance -= 100
                    elif next_high >= tp: self.balance += 200
                elif signal['action'] == 'SELL':
                    if next_high >= sl: self.balance -= 100
                    elif next_low <= tp: self.balance += 200
                    
            self.equity_curve.append(self.balance)
            
        return self._calculate_stats()

    def _calculate_stats(self) -> dict:
        eq = pd.Series(self.equity_curve)
        max_dd = ((eq.cummax() - eq) / eq.cummax()).max()
        total_return = ((self.balance - self.equity_curve[0]) / self.equity_curve[0]) * 100
        return {
            "Final Balance": round(self.balance, 2),
            "Total Return %": round(total_return, 2),
            "Max Drawdown %": round(max_dd * 100, 2),
            "Total Trades": len(self.trades)
        }
