<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Golden Emirat - Charts Widget</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #000; color: #e8ecf1; padding: 20px; }
        pre { background: #111; padding: 20px; border-radius: 10px; overflow-x: auto; border-left: 4px solid #ffd700; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; line-height: 1.5; color: #abb2bf; }
        .keyword { color: #c678dd; } .string { color: #98c379; } .comment { color: #5c6370; font-style: italic; } .class-name { color: #e5c07b; } .function { color: #61afef; }
        h2 { color: #ffd700; margin-bottom: 15px; }
    </style>
</head>
<body>
<h2>📈 gui/charts_widget.py — Виджет графиков</h2>
<pre><code><span class="comment"># -*- coding: utf-8 -*-
"""Golden Emirat v2.0 - Charts Widget Module
==========================================
Виджет отображения графиков цен с индикаторами.
Поддержка Plotly и Matplotlib для визуализации.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QCheckBox, QGroupBox,
    QGridLayout, QFrame, QLabel as QLabelNew
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ..core.config import ConfigManager, t


@dataclass
class ChartConfig:
    """Конфигурация графика"""
    symbol: str = "XAUUSD"
    timeframe: str = "H1"
    show_volume: bool = True
    show_indicators: bool = True
    indicators_list: List[str] = None
    
    def __post_init__(self):
        if self.indicators_list is None:
            self.indicators_list = ["sma_20", "sma_50", "ema_9", "ema_21", 
                                "rsi_14", "macd", "bb_upper", "bb_lower", "atr"]


class ChartsWidget(QWidget):
    """
    Виджет отображения графиков с индикаторами.
    
    Features:
    - Интерактивные свечи (свечи)
    - Технические индикаторы (SMA, EMA, RSI, MACD, BB, ATR)
    - Мультитаймфреймы (M1, M5, M15, H1, H4, D1)
    - Экспорт графика в изображение
    """
    
    # Signals
    chart_timeframe_changed = pyqtSignal(str)  # new timeframe
    indicator_added = pyqtSignal(str)  # indicator name
    candle_clicked = pyqtSignal(dict)  # candle data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ChartConfig()
        self._current_data: Optional[pd.DataFrame] = None
        self._indicators_data: Dict[str, pd.Series] = {}
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header with controls
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("📈 Price Chart")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffd700;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Timeframe selector
        tf_combo = QComboBox()
        tf_combo.addItems(["M1", "M5", "M15", "M30", "H1", "H4", "D1"])
        tf_combo.setCurrentText(self.config.timeframe)
        tf_combo.currentTextChanged.connect(self._on_timeframe_changed)
        header_layout.addWidget(QLabel(t('gui.timeframe') if hasattr(t('gui.timeframe'), 'Timeframe:')))
        header_layout.addWidget(tf_combo)
        
        # Indicators toggle
        ind_btn = QPushButton("📊 Indicators")
        ind_btn.setCheckable(True)
        ind_btn.setChecked(True)
        ind_btn.clicked.connect(self._toggle_indicators)
        header_layout.addWidget(ind_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #222;
                color: #e8ecf1;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #333;
                color: #ffd700;
            }
        """)
        refresh_btn.clicked.connect(self._refresh_chart)
        header_layout.addWidget(refresh_btn)
        
        layout.addWidget(header)
        
        # Chart placeholder (real chart would be here)
        self.chart_frame = QFrame()
        self.chart_frame.setMinimumHeight(400)
        self.chart_frame.setStyleSheet("""
            QFrame {
                background: #080808;
                border: 2px dashed #222;
                border-radius: 12px;
            }
        """)
        
        chart_placeholder = QLabel("""
            <div style="text-align:center; padding: 80px 20px;">
                <h3 style="color:#555;">📈 Interactive Chart Area</h3>
                <p style="color:#666; font-size:14px;">
                    Plotly/Matplotlib charts will be rendered here<br>
                    • Candlestick charts<br>
                    • Line charts<br>
                    • Technical indicators overlay<br>
                    • Real-time price updates
                </p>
            </div>
        """)
        chart_placeholder.setAlignment(Qt.AlignCenter)
        self.chart_frame.setLayout(chart_placeholder)
        layout.addWidget(self.chart_frame)
        
        # Stats below chart
        stats_layout = QGridLayout()
        stats_layout.setSpacing(10)
        
        stats = [
            ("Current:", "$2,065.40", "#ffd700"),
            ("Open:", "$2,064.80", "#00d4aa"),
            ("High:", "$2,071.25", "#00d4aa"),
            ("Low:", "$2,062.30", "#ff4757"),
            ("Spread:", "3.0 pts", "#888")
        ]
        
        for i, (label_text, value, color) in enumerate(stats):
            lbl = QLabel(label_text)
            val = QLabel(value)
            val.setStyleSheet(f"font-family: 'Fira Code', monospace; font-size: 18px; font-weight: bold; color: {color};")
            stats_layout.addWidget(lbl, 0, i)
            stats_layout.addWidget(val, 1, i)
        
        layout.addLayout(stats_layout)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(10000)  # Every 10 seconds
    
    def _on_timeframe_changed(self, text: str):
        """Обработка смены таймфрейма"""
        self.config.timeframe = text
        self.chart_timeframe_changed.emit(text)
        log.debug(f"Timeframe changed to {text}")
    
    def _toggle_indicators(self):
        """Переключение отображения индикаторов"""
        self.config.show_indicators = not self.config.show_indicators
        status = "ON" if self.config.show_indicators else "OFF"
        self.sender().statusBar.showMessage(f"Indicators: {status}", 2000)
    
    def _refresh_chart(self):
        """Обновление данных графика"""
        self.sender().show_notification(
            "Chart", "Refreshing data...", "info"
        )
        # TODO: Load real data from DataManager and update chart
    
    def _auto_refresh(self):
        """Автоматическое обновление"""
        self._refresh_chart()
    
    def load_data(self, df: pd.DataFrame):
        """Загрузка данных в график"""
        self._current_data = df
        
        if not df.empty:
            # Calculate indicators if enabled
            if self.config.show_indicators:
                from ..core.data_manager import DataManager
                dm = DataManager()
                df_with_ind = dm.calculate_indicators(df, self.config.indicators_list)
                
                for col in df_with_ind.columns:
                    if col.startswith(('sma_', 'ema_', 'rsi_', 'macd', 'bb_', 'atr')):
                        if col in df_with_ind.columns:
                            self._indicators_data[col] = df_with_ind[col]
            
            self._update_stats_from_data(df)
    
    def _update_stats_from_data(self, df: pd.DataFrame):
        """Обновление статистики из DataFrame"""
        if df.empty:
            return
        
        last = df.iloc[-1]
        
        stats = [
            ("Current:", f"${last['close']:.2f}", "#ffd700"),
            ("Open:", f"${last['open']:.2f}", "#00d4aa"),
            ("High:", f"${last['high']:.2f}", "#00d4aa"),
            ("Low:", f"${last['low']:.2f}", "#ff4757"),
            ("Spread:", f"{abs(last['close'] - last['open']):.2f} pts", "#888"),
        ]
        
        # Update labels in grid layout
        grid = self.findChild(QGridLayout)
        if grid:
            for i in range(grid.count() // 2):  # Each stat is 2 items (label + value)
                val_item = grid.itemAt(1, i)  # Value column
                if val_item:
                    old_text = val_item.text()
                    _, value, color = next((s for s in stats if s[0] == old_text), (None, None))
                    if value:
                        val_item.setText(value)
                        val_item.setStyleSheet(f"font-family: 'Fries', monospace; font-size: 18px; font-weight: bold; color: {color};")
    
    def get_current_candle(self) -> Optional[Dict]:
        """Получение последней свечи"""
        if self._current_data is not None and len(self._current_data) > 0:
            last = self._current_data.iloc[-1]
            return {
                "time": last.get("timestamp", 0),
                "open": last.get("open", 0),
                "high": last.get("high", 0),
                "low": last.get("low", 0),
                "close": last.get("close", 0),
                "volume": last.get("volume", 0)
            }
        return None
    
    def export_chart_image(self, filepath: str) -> bool:
        """Экспорт графика в изображение"""
        try:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(12, 6), facecolor='#0a0a0a')
            
            if self._current_data is not None:
                ax.plot(self._current_data['timestamp'], 
                        self._current_data['close'], 
                        color='#ffd700', linewidth=1.5)
                
                if 'sma_20' in self._indicators_data:
                    ax.plot(self._current_data['timestamp'], 
                           self._indicators_data['sma_20'], 
                           color='#3498db', linewidth=1, alpha=0.7, label='SMA 20')
                
                if 'bb_upper' in self._indicators_data:
                    ax.plot(self._current_data['timestamp'], 
                           self._indicators_data['bb_upper'], 
                           color='#ff9800', linewidth=1, alpha=0.5, linestyle='--',
                           label='BB Upper')
                    ax.plot(self._current_data['timestamp'], 
                           self._indicators_data['bb_lower'], 
                           color='#ff9800', linewidth=1, alpha=0.5, linestyle='--',
                           label='BB Lower')
                
                ax.fill_between(self._current_data['timestamp'],
                                 self._indicators_data.get('bb_lower', pd.Series()),
                                 self._indicators_data.get('bb_upper', pd.Series()),
                                 alpha=0.05, color='#ff9800'
                )
            
            ax.set_facecolor('#0a0a0a')
            ax.figure.set_facecolor('#0a0a0a')
            ax.set_title(f"XAU/USD - {self.config.timeframe} Chart", color='#ffd700', fontsize=14)
            ax.grid(True, alpha=0.1, color='#333')
            ax.tick_params(colors='#666')
            
            fig.savefig(filepath, dpi=150, facecolor='#0a0a0a', edgecolor='none',
                       bbox_inches='tight', pad_inches=0.1)
            plt.close()
            
            return True
        except Exception as e:
            print(f"Error exporting chart: {e}")
            return False


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = ChartsWidget()
    widget.show()
    
    print("✅ Charts Widget ready")
    sys.exit(app.exec_())
</code></pre>
</body>
</html>
