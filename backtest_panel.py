<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Golden Emirat - Backtest Panel</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #000; color: #e8ecf1; padding: 20px; }
        pre { background: #111; padding: 20px; border-radius: 10px; overflow-x: auto; border-left: 4px solid #ffd700; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; line-height: 1.5; color: #abb2bf; }
        .keyword { color: #c678dd; } .string { color: #98c379; } .comment { color: #5c6370; font-style: italic; } .class-name { color: #e5c07b; } .function { color: #61afef; }
        h2 { color: #ffd700; margin-bottom: 15px; }
    </style>
</head>
<body>
<h2>📉 gui/backtest_panel.py — Панель бэктестинга</h2>
<pre><code><span class="comment"># -*- coding: utf-8 -*-
"""Golden Emirat v2.0 - Backtest Panel Widget
=====================================================
Панель для запуска и отображения результатов бэктестинга.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QPushButton, QDateEdit, QComboBox,
    QSpinBox, QDoubleSpinBox, QProgressBar, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGridLayout, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTime
from PyQt6.QtGui import QFont, QColor, QPixmap

from ..core.config import ConfigManager, t


@dataclass
class BacktestConfig:
    """Конфигурация бэктестинга"""
    symbol: str = "XAUUSD"
    strategy: str = "trend"  # trend, scalping, breakout, news
    start_date: QDate.currentDate().addMonths(-12)
    end_date: = QDate.current_date()
    initial_deposit: float = 10000.0
    risk_percent: float = 2.0
    leverage: int = 100
    spread: float = 3.0
    commission: float = 0.05
    
    def __post_init__(self):
        self.start_date = QDate.currentDate().addMonths(-12)
        self.end_date = QDate.current_date()


@dataclass
class BacktestResult:
    """Результаты бэктестинга"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    net_profit: float = 0.0
    final_balance: float = 0.0
    duration_days: int = 0
    equity_curve: List[float] = field(default_factory=list)
    
    def calculate_stats(self):
        """Расчёт метрик из сырых данных"""
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
            if self.losing_trades > 0:
                self.profit_factor = (self.winning_trades / max(self.losing_trades, 1))
        
        return {
            "total_trades": self.total_trades,
            "win_rate": round(self.win_rate, 2),
            "profit_factor": round(self.profit_factor, 2),
            "max_drawdown": f"{abs(self.max_drawdown):.2f}%",
            "sharpe": round(self.sharpe_ratio, 2),
            "net_profit": f"${self.net_profit:.2f}",
            "final_balance": f"${self.final_balance:.2f}"
        }


class BacktestPanelWidget(QWidget):
    """
    Панель управления бэктестингом стратегий.
    
    Features:
    - Выбор стратегии и параметров
    - Настройка диапазона дат
    - Запуск и отмена бэктестинга
    - Отображение результатов в реальном времени
    - Экспорт отчётов в PDF/Excel
    """
    
    # Signals
    start_backtest = pyqtSignal(dict)  # config
    stop_backtest = pyqtSignal()
    backtest_completed = pyqtSignal(object)  # BacktestResult
    progress_updated = pyqtSignal(int)  # percentage
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = BacktestConfig()
        self._is_running = False
        self._backtest_thread: Optional[QThread] = None
        self._results: Optional[BacktestResult] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        title = QLabel("📉 Backtesting Engine")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("⭐ NEW"))
        layout.addWidget(header)
        
        # Settings grid
        settings_group = QGroupBox("⚙️ Backtest Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 14px;
                margin-top: 20px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 25px;
            }
        """)
        settings_form = QFormLayout()
        
        # Strategy selector
        strategy_combo = QComboBox()
        strategy_combo.addItems(["Trend", "Scalping", "Breakout", "News Trading"])
        strategy_combo.setCurrentText(self.config.strategy)
        settings_form.addRow("Strategy:", strategy_combo)
        self.strategy_combo = strategy_combo
        
        # Date range
        date_layout = QHBoxLayout()
        
        start_edit = QDateEdit()
        start_edit.setDate(self.config.start_date)
        start_edit.setCalendarPopup(True)
        start_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(QLabel("Start:"), start_edit)
        
        end_edit = QDateEdit()
        end_edit.setDate(self.config.end_date)
        end_edit.setCalendarPopup(True)
        end_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(QLabel("End:"), end_edit)
        
        settings_form.addRow("Date Range:", date_layout)
        
        # Initial deposit
        deposit_spin = QDoubleSpinBox()
        deposit_spin.setRange(1000, 10000000)
        deposit_spin.setValue(self.config.initial_deposit)
        deposit_spin.setPrefix("$")
        deposit_spin.setDecimals(2)
        settings_form.addRow("Initial Deposit:", deposit_spin)
        self.deposit_spin = deposit_spin
        
        # Risk %
        risk_spin = QDoubleSpinBox()
        risk_spin.setRange(0.5, 10.0)
        risk_spin.setValue(self.config.risk_percent)
        risk_spin.setSuffix("%")
        risk_spin.setSingleStep(0.5)
        settings_form.addRow("Risk per Trade (%):", risk_spin)
        self.risk_spin = risk_spin
        
        settings_group.setLayout(settings_form)
        layout.addWidget(settings_group)
        
        # Run button
        run_btn = QPushButton("▶️ RUN BACKTEST")
        run_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, x2:1, stop:0 #00d4aa, stop:1: #00a080);
                color: #fff;
                border: none;
                padding: 16px;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, x2:1, stop:0: #00ff88, stop:1: #00cc66);
                transform: translateY(-2px);
            }
        """)
        run_btn.clicked.connect(self._on_run_clicked)
        self.run_btn = run_btn
        
        # Stop button
        stop_btn = QPushButton("⏹ STOP")
        stop_btn.setStyleSheet("""
            QPushButton {
                background: #333;
                color: #e8ecf1;
                border: 1px solid #444;
                padding: 14px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #ff4757;
                color: #fff;
            }
        """)
        stop_btn.clicked.connect(self._on_stop_clicked)
        stop_btn.setEnabled(False)
        self.stop_btn = stop_btn
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(run_btn)
        buttons_layout.addWidget(stop_btn)
        layout.addLayout(buttons_layout)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setTextVisible(True)
        progress_bar.setFormat("{value}%")
        progress_bar.setStyleSheet("""
            QProgressBar {
                background: #111;
                border: 1px solid #222;
                border-radius: 8px;
                height: 28px;
                text-align: center;
                font-size: 13px;
                color: #888;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, x2:1, stop:0 #00d4aa, stop:1: #ffd700);
                border-radius: 8px;
            }
        """)
        self.progress_bar = progress_bar
        layout.addWidget(progress_bar)
        
        # Results area
        results_group = QGroupBox("📊 Results")
        results_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 14px;
                margin-top: 25px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 25px;
            }
        """)
        
        results_table = QTableWidget()
        results_table.setColumnCount(7)
        results_table.setHorizontalHeaderLabels([
            "Metric", "Value", "Change", "", "", "", ""
        ])
        results_table.horizontalHeader().setStyleSheet("color: #ffd700;")
        results_group.setLayout(QVBoxLayout())
        results_group.layout().addWidget(results_table)
        self.results_table = results_table
        layout.addWidget(results_group)
        
        self.setLayout(layout)
    
    def _on_run_clicked(self):
        """Обработка нажатия RUN"""
        self.config.strategy = self.strategy_combo.currentText()
        self.config.start_date = self.deposit_spin.value() * 100  # Convert to cents
        self.config.end_date = self.end_edit.date().toPyDate()
        self.config.initial_deposit = self.deposit_spin.value()
        self.config.risk_percent = self.risk_spin.value()
        
        self.start_backtest.emit({
            "symbol": self.config.symbol,
            "strategy": self.config.strategy,
            "start_date": self.config.start_date.strftime('%Y-%m-%d'),
            "end_date": self.config.end_date.strftime('%Y-%m-%d'),
            "initial_deposit": self.config.initial_deposit,
            "risk_percent": self.config.risk_percent
        })
        
        self._is_running = True
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Start backtest in thread
        self._start_backtest_thread()
    
    def _on_stop_clicked(self):
        """Остановка бэктестинга"""
        self._is_running = False
        self.stop_backtest.emit()
        
        if self._backtest_thread and self._backtest_thread.isRunning():
            self._backtest_thread.requestInterruption()
        
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def _start_backtest_thread(self):
        """Запуск бэктестинга в отдельном потоке"""
        from .backtest.backtest_engine import BacktestEngine
        
        self._backtest_thread = BacktestThread(
            self.config,
            self
        )
        self._backtest_thread.finished.connect(self._on_backtest_finished)
        self._backtest_thread.start()
    
    def _on_backtest_finished(self, result: dict):
        """Обработка завершения бэктестинга"""
        self._is_running = False
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setValue(100)
        
        # Parse result
        self._results = BacktestResult(**result)
        stats = self._results.calculate_stats()
        
        # Update table
        self._update_results_table(stats)
        
        self.backtest_completed.emit(self._results)
        
        log.info(f"Backtest completed! Win Rate: {stats['win_rate']}%")
    
    def _update_progress(self, value: int):
        """Обновление прогресс-бара"""
        self.progress_bar.setValue(value)
        self.progress_updated.emit(value)
    
    def _update_results_table(self, stats: dict):
        """Обновление таблицы результатов"""
        self.results_table.setRowCount(0)
        
        metrics = [
            ("Total Trades", str(stats.get('total_trades', 0)), "#e8ecf1"),
            ("Win Rate", f"{stats.get('win_rate', 0)}%", "#00d4aa"),
            ("Profit Factor", str(stats.get('profit_factor', '0')), "#3498db"),
            ("Max Drawdown", stats.get('max_drawdown', '0%'), "#ff4757"),
            ("Sharpe Ratio", str(stats.get('sharpe', '0')), "#9b59b6"),
            ("Net Profit", stats.get('net_profit', '$0'), "#00d4aa"),
            ("Final Balance", stats.get('final_balance', '$0'), "#ffd700"),
        ]
        
        for i, (metric, value, color) in enumerate(metrics):
            item_0 = QTableWidgetItem(metric)
            item_1 = QTableWidgetItem(value)
            item_1.setTextAlignment(Qt.AlignCenter)
            item_1.setForeground(QColor(color))
            
            item_2 = QTableWidgetItem("")
            item_3 = QTableWidgetItem("")
            item_4 = QTableWidgetItem("")
            item_5 = QTableWidgetItem("")
            
            self.results_table.setItem(i, 0, item_0)
            self.results_table.setItem(i, 1, item_1)
            self.results_table.setItem(i, 2, item_2)
            self.results_table.setItem(i, 3, item_3)
            self.results_table.setItem(i, 4, item_4)
            self.results_table.setItem(i, 5, item_5)


class BacktestThread(QThread):
    """Поток для выполнения бэктестинга"""
    
    finished = pyqtSignal(object)
    progress = pyqtSignal(int)
    
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self._cancelled = False
    
    def run(self):
        """Выполнение бэктеста"""
        try:
            from .backtest.backtest_engine import BacktestEngine
            
            engine = BacktestEngine(self.config)
            
            for progress in engine.run():
                if self._cancelled:
                    break
                
                self.progress.emit(progress)
                
            result = engine.get_results()
            self.finished.emit(result)
            
        except Exception as e:
            self.finished.emit({"error": str(e)})
    
    def cancel(self):
        """Остановка потока"""
        self._cancelled = True
        self.wait()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = BacktestPanelWidget()
    widget.show()
    
    print("✅ Backtest Panel ready")
    sys.exit(app.exec_())
</code></pre>
</body>
</html>
