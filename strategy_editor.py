<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Golden Emirat - Strategy Editor Module</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #000; color: #e8ecf1; padding: 20px; }
        pre { background: #111; padding: 20px; border-radius: 10px; overflow-x: auto; border-left: 4px solid #ffd700; }
        code { font-family: 'Fira Code', monospace; font-size: 14px; line-height: 1.6; color: #abb2bf; }
        .keyword { color: #c678dd; } .string { color: #98c379; } .comment { color: #5c6370; font-style: italic; } .class-name { color: #e5c07b; } .function { color: #61afef; }
        h2 { color: #ffd700; margin-bottom: 15px; }
    </style>
</head>
<body>
<h2>📝 gui/strategy_editor.py — Редактор стратегий</h2>
<pre><code><span class="comment"># -*- coding: utf-8 -*-
"""Golden Emirat v2.0 - Strategy Editor Widget
==========================================
Виджет для редактирования параметров торговых стратегий.
Поддержка 4 стратегий: Trend, Scalping, Breakout, News.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox, QPushButton,
    QFormLayout, QScrollArea, QFrame, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..core.config import ConfigManager, t


class StrategyEditorWidget(QWidget):
    """
    Виджет редактора стратегий.
    
    Сигналы:
    - strategy_params_changed(dict) — при изменении параметров стратегии
    """
    
    strategy_params_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager().config
        self._setup_ui()
        
    def _setup_ui(self):
        """Настройка UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("🎯 Strategy Configuration")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        layout.addWidget(title)
        
        # Scroll area for all strategy groups
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidgetResizable(True)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # === Trend Strategy Settings ===
        trend_group = self._create_trend_group()
        content_layout.addWidget(trend_group)
        
        # === Scalping Strategy Settings ===
        scalping_group = _create_scalping_group()
        content_layout.addWidget(scalping_group)
        
        # === Breakout Strategy Settings ===
        breakout_group = _create_breakout_group()
        content_layout(breakout_group)
        
        # === News Trading Settings ===
        news_group = _create_news_group()
        content_layout.addWidget(news_group)
        
        # Save button
        save_btn = QPushButton("💾 Save All Parameters")
        save_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, x2:1, stop:0 #ffd700, stop:1: #b8960f);
                color: #000;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, x2:1, stop:1: #ffe066, stop:1: #ffd700);
            }
        """)
        save_btn.clicked.connect(self._on_save)
        content_layout.addWidget(save_btn)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
    
    def _create_trend_group(self) -> QGroupBox:
        """Группа настроек трендовой стратегии"""
        group = QGroupBox("📈 Trend Strategy (EMA + RSI)")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 12px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 20px;
            }
        """)
        form = QFormLayout()
        
        # EMA Fast
        ema_fast_spin = QSpinBox()
        ema_fast_spin.setRange(3, 50)
        ema_fast_spin.setValue(self.config.strategy.trend_ema_fast)
        ema_fast_spin.setSuffix(" periods")
        form.addRow("EMA Fast Period:", ema_fast_spin)
        self.trend_ema_fast = ema_fast_spin
        
        # EMA Slow
        ema_slow_spin = QSpinBox()
        ema_slow_spin.setRange(10, 200)
        ema_slow_spin.setValue(self.config.strategy.trend_ema_slow)
        ema_slow_spin.setSuffix(" periods")
        form.addRow("EMA Slow Period:", ema_slow_spin)
        self.trend_ema_slow = ema_slow_spin
        
        # RSI Period
        rsi_spin = QSpinBox()
        rsi_spin.setRange(5, 30)
        rsi_spin.setValue(self.config.strategy.trend_rsi_period)
        rsi_spin.setSuffix(" periods")
        form.addRow("RSI Period:", rsi_spin)
        self.trend_rsi_period = rsi_spin
        
        # Enable checkbox
        enable_cb = QCheckBox("Enable Trend Strategy")
        enable_cb.setChecked(self.config.strategy.trend_enabled)
        form.addRow("", enable_cb)
        self.trend_enabled = enable_cb
        
        group.setLayout(form)
        return group
    
    def _create_scalping_group(self) -> QGroupBox:
        """Группа настроек скальпинг стратегии"""
        group = QGroupBox("⚡ Scalping Strategy (Bollinger Bands)")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 12px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 20px;
            }
        """)
        form = QFormLayout()
        
        # BB Period
        bb_period = QSpinBox()
        bb_period.setRange(10, 50)
        bb_period.setValue(self.config.strategy.scalping_bb_period)
        bb_period.setSuffix(" periods")
        form.addRow("BB Period:", bb_period)
        self.scalping_bb_period = bb_period
        
        # BB Std Deviation
        bb_std = QDoubleSpinBox()
        bb_std.setRange(0.5, 4.0)
        bb_std.setValue(self.config.strategy.scalping_bb_std)
        bb_std.setDecimals(1)
        bb_std.setSingleStep(0.1)
        form.addRow("BB Std Deviation:", bb_std)
        self.scalping_bb_std = bb_std
        
        # RSI Oversold
        rsi_oversold = QSpinBox()
        rsi_oversold.setRange(10, 40)
        rsi_oversold.setValue(self.config.strategy.scalping_rsi_oversold)
        form.addRow("RSI Oversold Level:", rsi_oversold)
        self.scalping_rsi_oversold = rsi_oversold
        
        # RSI Overbought
        rsi_overbought = QSpinBox()
        rsi_overbought.setRange(60, 90)
        rsi_overbought.setValue(self.config.strategy.scalping_rsi_overbought)
        form.addRow("RSI Overbought Level:", rsi_overbought)
        self.scalping_rsi_overbought = rsi_overbought
        
        enable_cb = QCheckBox("Enable Scalping Strategy")
        enable_cb.setChecked(self.config.strategy.scalping_enabled)
        form.addRow("", enable_cb)
        self.scalping_enabled = enable_cb
        
        group.setLayout(form)
        return group
    
    def _create_breakout_group(self) -> QGroupBox:
        """Группа настроек стратегии пробоя"""
        group = QGroupBox("💥 Breakout Strategy (ATR Channels)")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 12px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 20px;
            }
        """)
        form = QFormLayout()
        
        # ATR Period
        atr_period = QSpinBox()
        atr_period.setRange(7, 30)
        atr_period.setValue(self.config.strategy.breakout_atr_period)
        atr_period.setSuffix(" periods")
        form.addRow("ATR Period:", atr_period)
        self.breakout_atr_period = atr_period
        
        # ATR Multiplier
        atr_mult = QDoubleSpinBox()
        atr_mult.setRange(0.5, 5.0)
        atr_mult.setValue(self.config.strategy.breakout_atr_multiplier)
        atr_mult.setDecimals(1)
        atr_mult.setSingleStep(0.1)
        form.addRow("ATR Multiplier:", atr_mult)
        self.breakout_atr_multiplier = atr_mult
        
        # Lookback period
        lookback = QSpinBox()
        lookback.setRange(10, 50)
        lookback.setValue(self.config.strategy.breakout_lookback)
        lookback.setSuffix(" bars")
        form.addRow("Lookback Period:", lookback)
        self.breakout_lookback = lookback
        
        enable_cb = QCheckBox("Enable Breakout Strategy")
        enable_cb.setChecked(self.config.strategy.breakout_enabled)
        form.addRow("", enable_cb)
        self.breakout_enabled = enable_cb
        
        group.setLayout(form)
        return group
    
    def _create_news_group(self) -> QGroupBox:
        """Группа настроек новостной торговли"""
        group = QGroupBox("📰 News Trading Strategy ⭐")
        group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 12px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 20px;
            }
        """)
        form = QFormLayout()
        
        # Impact filter
        impact_edit = QLineEdit(", ".join(self.config.strategy.news_impact_filter))
        impact_edit.setPlaceholder("high, medium, low")
        form.addRow("Impact Filter (comma-separated):", impact_edit)
        self.news_impact_filter = impact_edit
        
        # Pause before news (minutes)
        pause_before = QSpinBox()
        pause_before.setRange(5, 60)
        pause_before.setValue(self.config.strategy.news_pause_before_min)
        pause_before.setSuffix(" min before")
        form.addRow("Pause Before News:", pause_before)
        self.news_pause_before = pause_before
        
        # Resume after news (minutes)
        resume_after = QSpinBox()
        resume_after.setRange(10, 120)
        resume_after.setValue(self.config.strategy.news_resume_after_min)
        resume_after.setSuffix(" min after")
        form.addRow("Resume After News:", resume_after)
        self.news_resume_after = resume_after
        
        enable_cb = QCheckBox("Enable News Trading Strategy")
        enable_cb.setChecked(self.config.strategy.news_trading_enabled)
        form.addRow("", enable_cb)
        self.news_enabled = enable_cb
        
        group.setLayout(form)
        return group
    
    def get_trend_params(self) -> dict:
        """Получить параметры трендовой стратегии"""
        return {
            "ema_fast": self.trend_ema_fast.value(),
            "ema_slow": self.trend_ema_slow.value(),
            "rsi_period": self.trend_rsi_period.value(),
            "enabled": self.trend_enabled.isChecked()
        }
    
    def get_scalping_params(self) -> dict:
        """Получить параметры скальпинга"""
        return {
            "bb_period": self.scalping_bb_period.value(),
            "bb_std": self.scalping_bb_std.value(),
            "rsi_oversold": self.scalping_rsi_oversold.value(),
            "rsi_overbought": self.scalping_rsi_overbought.value(),
            "enabled": self.scalping_enabled.isChecked()
        }
    
    def get_breakout_params(self) -> dict:
        """Получить параметры пробоя"""
        return {
            "atr_period": self.breakout_atr_period.value(),
            "atr_multiplier": self.breakout_atr_multiplier.value(),
            "lookback": self.breakout_lookback.value(),
            "enabled": self.breakout_enabled.isChecked()
        }
    
    def get_news_params(self) -> dict:
        """Получить параметры новостной торговли"""
        return {
            "impact_filter": [x.strip() for x in self.news_impact_filter.text().split(',') if x.strip()],
            "pause_before": self.news_pause_before.value(),
            "resume_after": self.news_resume_after.value(),
            "enabled": self.news_enabled.isChecked()
        }
    
    def get_all_params(self) -> dict:
        """Получить ВСЕ параметры стратегий"""
        return {
            "trend": self.get_trend_params(),
            "scalping": self.get_scalping_params(),
            "breakout": self.get_breakout_params(),
            "news": self.get_news_params()
        }
    
    @staticmethod
    def _create_scalping_group() -> QGroupBox:
        """Статический метод для создания группы скальпинга"""
        pass  # Используется в _setup_ui
    
    @staticmethod
    def _create_breakout_group() -> QGroupBox:
        """Статический метод для создания группы пробоя"""
        pass  # Используется в _setup_ui
    
    @staticmethod
    def _create_news_group() -> QGroupBox:
        """Статический метод для создания группы новостей"""
        pass  # Используется в _setup_ui
    
    def _on_save(self):
        """Сохранение параметров и отправка сигнала"""
        params = self.get_all_params()
        self.strategy_params_changed.emit(params)
        
        print(f"[Strategy Editor] Params saved: {params}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    widget = StrategyEditorWidget()
    widget.show()
    
    print("✅ Strategy Editor module ready")
    sys.exit(app.exec_())
</code></pre>
</body>
</html>
