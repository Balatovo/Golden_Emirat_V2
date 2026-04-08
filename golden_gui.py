#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Emirat v2.0 - Main GUI Window
========================================
Главное окно приложения с PyQt6.
Deep Black UI Theme с поддержкой мультиязычности.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QStatusBar, QMenuBar, QMenu,
    QAction, QMessageBox, QGroupBox, QTextEdit, QGridLayout,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QLineEdit,
    QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QListWidget, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter, QPen, QBrush, QPixmap

from ..core.config import ConfigManager, t
from ..core.logger_setup import get_logger

log = get_logger(__name__)


class GoldenEmiratGUI(QMainWindow):
    """
    Главное окно приложения Golden Emirat v2.0.
    
    Features:
    - Dashboard с основной информацией
    - Панель графиков
    - Управление стратегиями
    - Мониторинг позиций
    - Бэктестинг панель
    - Настройки уведомлений
    - Синхронизация времени
    """
    
    # Signals
    signal_buy_clicked = pyqtSignal(str)  # symbol
    signal_sell_clicked = pyqtSignal(str)  # symbol
    signal_close_all_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.config
        
        # UI State
        self.current_symbol = self.config.trading.symbol
        self.is_running = False
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._apply_theme()
        
        # Status bar
        self._setup_statusbar()
        
        # Timers
        self._setup_timers()
        
        log.info("Golden Emirat GUI initialized")
    
    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle(f"🥇 {t('app.name')} {t('app.version')}")
        self.setMinimumSize(QSize(1200, 800))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        layout.addWidget(self.tabs)
        
        # Create tabs
        self._create_dashboard_tab()
        self._create_charts_tab()
        self._create_trades_tab()
        self._create_strategies_tab()
        self._create_settings_tab()
        self._create_backtest_tab()
        self._create_notifications_tab()
        
        # Menu bar
        self._create_menu_bar()
    
    def _create_menu_bar(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu(t('menu.file') if hasattr(t('menu.file'), 'Файл'))
        
        export_action = QAction(t('menu.export_report'), self)
        export_action.triggered.connect(self._on_export_report)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(t('menu.exit'), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu(t('menu.view') if hasattr(t('menu.view'), 'Вид'))
        
        dark_mode_action = QAction("🌙 Dark Mode", self, checkable=True)
        dark_mode_action.setChecked(True)
        dark_mode_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(dark_mode_action)
        
        # Help menu
        help_menu = menubar.addMenu(t('menu.help') if hasattr(t('menu.help'), 'Помощь'))
        
        about_action = QAction(t('menu.about'), self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_dashboard_tab(self):
        """Создание вкладки Dashboard"""
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        
        # Header with buttons
        header_layout = QHBoxLayout()
        title_label = QLabel(f"📊 {t('menu.dashboard')}")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Action buttons
        buy_btn = QPushButton(f"🟢 {t('action.buy')}")
        buy_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, x2:1, stop:0 #00d4aa, stop:1 #00a080);
                color: #000;
                border: none;
                padding: 10px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, x2:1, stop:0 #00ff88, stop:1 #00cc66);
            }
        """)
        buy_btn.clicked.connect(lambda: self.signal_buy_clicked.emit(self.current_symbol))
        header_layout.addWidget(buy_btn)
        
        sell_btn = QPushButton(f"🔴 {t('action.sell')}")
        sell_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, x2:1, stop:0 #ff4757, stop:1 #cc3322);
                color: #fff;
                border: none;
                padding: 10px 25px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, x2:1, stop:1 #ff6b6b, stop:1 #ee4444);
            }
        """)
        sell_btn.clicked.connect(lambda: self.signal_sell_clicked.emit(self.current_symbol))
        header_layout.addWidget(sell_btn)
        
        close_all_btn = QPushButton(f"{t('action.close_all')}")
        close_all_btn.setStyleSheet("""
            QPushButton {
                background: #111;
                color: #e8ecf1;
                border: 1px solid #222;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #222;
                border-color: #ffd700;
            }
        """)
        close_all_btn.clicked.connect(self.signal_close_all_clicked.emit)
        header_layout.addWidget(close_all_btn)
        
        layout.addLayout(header_layout)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        # Balance
        balance_card = self._create_stat_card("$10,245.50", "Balance", "#ffd700")
        stats_grid.addWidget(balance_card, 0, 0)
        
        # P&L Today
        pnl_card = self._create_stat_card("+$245.50", "P&L Today", "#00d4aa")
        stats_grid.addWidget(pnl_card, 1, 0)
        
        # Positions
        pos_card = self._create_stat_card("2", "Positions", "#3498db")
        stats_grid.addWidget(pos_card, 2, 0)
        
        # Win Rate
        winrate_card = self._create_stat_card("68.5%", "Win Rate", "#ffd700")
        stats_grid.addWidget(winrate_card, 0, 1)
        
        # Profit Factor
        pf_card = self._create_stat_card("2.14", "Profit Factor", "#3498db")
        stats_grid.addWidget(pf_card, 1, 1)
        
        # Drawdown
        dd_card = self._create_stat_card("-12.3%", "Max Drawdown", "#ff4757")
        stats_grid.addWidget(dd_card, 2, 1)
        
        layout.addLayout(stats_grid)
        
        # Open positions table
        positions_group = QGroupBox(f"📋 {t('menu.trades')}")
        positions_table = QTableWidget()
        positions_table.setColumnCount(6)
        positions_table.setHorizontalHeaderLabels([
            "Ticket", "Symbol", "Type", "Volume", "P&L", "Time"
        ])
        positions_table.horizontalHeader().setStyleSheet("color: #ffd700;")
        positions_table.setAlternatingRowColors(True)
        positions_group.setLayout(QVBoxLayout())
        positions_group.layout().addWidget(positions_table)
        layout.addWidget(positions_group)
        
        self.tabs.addTab(dashboard_widget, "📊 Dashboard")
    
    def _create_stat_card(self, value: str, label: str, color: str) -> QFrame:
        """Создание карточки статистики"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #111;
                border: 1px solid #222;
                border-radius: 10px;
                padding: 15px;
            }}
            QLabel {{ color: #8b95a5; font-size: 12px; }}
            .stat-value {{
                color: {color};
                font-size: 24px;
                font-weight: bold;
                font-family: 'Fira Code', monospace;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setObjectName("stat-value")
        label_label = QLabel(label)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return card
    
    def _create_charts_tab(self):
        """Создание вкладки графиков"""
        charts_widget = QWidget()
        layout = QVBoxLayout(charts_widget)
        
        placeholder = QLabel("📈 Interactive Chart Area\n\nPlotly/Matplotlib charts will be here")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background: #080808;
                border: 2px dashed #222;
                border-radius: 15px;
                padding: 50px;
                color: #555;
                font-size: 16px;
            }
        """)
        layout.addWidget(placeholder)
        
        self.tabs.addTab(charts_widget, "📈 Charts")
    
    def _create_trades_tab(self):
        """Создание вкладки сделок"""
        trades_widget = QWidget()
        layout = QVBoxLayout(trades_widget)
        
        placeholder = QLabel("💼 Trades History\n\nList of closed trades will be displayed here")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background: #080808;
                border: 2px dashed #222;
                border-radius: 15px;
                padding: 50px;
                color: #555;
                font-size: 16px;
            }
        """)
        layout.addWidget(placeholder)
        
        self.tabs.addTab(trades_widget, "💼 Trades")
    
    def _create_strategies_tab(self):
        """Создание вкладки стратегий"""
        strategies_widget = QWidget()
        layout = QVBoxLayout(strategies_widget)
        
        placeholder = QLabel("🎯 Strategy Configuration\n\nStrategy parameters editor will be here")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background: #080808;
                border: 2px dashed #222;
                border-radius: 15px;
                padding: 50px;
                color: #555;
                font-size: 16px;
            }
        """)
        layout.addWidget(placeholder)
        
        self.tabs.addTab(strategies_widget, "🎯 Strategies")
    
    def _create_settings_tab(self):
        """Создание вкладки настроек"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        placeholder = QLabel("⚙️ Settings\n\nApplication settings configuration")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background: #080808;
                border: 2px dashed #222;
                border-radius: 15px;
                padding: 50px;
                color: #555;
                font-size: 16px;
            }
        """)
        layout.addWidget(placeholder)
        
        self.tabs.addTab(settings_widget, "⚙️ Settings")
    
    def _create_backtest_tab(self):
        """Создание вкладки бэктестинга"""
        backtest_widget = QWidget()
        layout = QVBoxLayout(backtest_widget)
        
        placeholder = QLabel("📉 Backtesting Engine\n\nStrategy testing on historical data")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background: #080808;
                border: 2px dashed #222;
                border-radius: 15px;
                padding: 50px;
                color: #555;
                font-size: 16px;
            }
        """)
        layout.addWidget(placeholder)
        
        self.tabs.addTab(backtest_widget, "📉 Backtesting")
    
    def _create_notifications_tab(self):
        """Создание вкладки уведомлений"""
        notify_widget = QWidget()
        layout = QVBoxLayout(notify_widget)
        
        placeholder = QLabel("🔔 Notifications\n\nTelegram & Sound notifications setup")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                background: #080808;
                border: 2px dashed #222;
                border-radius: 15px;
                padding: 50px;
                color: #555;
                font-size: 16px;
            }
        """)
        layout.addWidget(placeholder)
        
        self.tabs.addTab(notify_widget, "🔔 Notifications")
    
    def _setup_statusbar(self):
        """Настройка статус-бара"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.status_label = QLabel("● Ready")
        self.status_label.setStyleSheet("color: #00d4aa; font-weight: bold;")
        self.statusBar.addWidget(self.status_label, 1)
        
        self.connection_label = QLabel("🔴 Disconnected")
        self.statusBar.addWidget(self.connection_label, 2)
        
        self.time_label = QLabel("")
        self.statusBar.addWidget(self.time_label, 3)
        
        self.statusBar.showMessage(f"🥇 {t('app.name')} {t('app.version')}", 3000)
    
    def _connect_signals(self):
        """Подключение сигналов"""
        self.signal_buy_clicked.connect(self._on_buy)
        self.signal_sell_clicked.connect(self._on_sell)
        self.signal_close_all_clicked.connect(self._on_close_all)
    
    def _apply_theme(self):
        """Применение Dark темы"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                color: #e8ecf1;
            }
            QWidget {
                background-color: #000000;
                color: #e8ecf1;
            }
            QTabWidget::pane {
                border: 1px solid #222;
                background: #0a0a0a;
            }
            QTabBar::tab {
                background: #111;
                color: #8b95a5;
                padding: 10px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #1a1a1a;
                color: #ffd700;
            }
            QGroupBox {
                border: 1px solid #222;
                border-radius: 10px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 20px;
            }
            QTableWidget {
                gridline-color: #1a1a1a;
                border: 1px solid #222;
                border-radius: 10px;
                background: #0a0a0a;
            }
            QHeaderView::section {
                background-color: #111;
                color: #ffd700;
                border: none;
                border-bottom: 1px solid #222;
                padding: 8px;
                margin: 0;
            }
            QScrollBar:vertical {
                background: #111;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #333;
                border-radius: 6px;
                min-height: 30px;
            }
            QSplitter::handle {
                background: #222;
                height: 2px;
            }
            QMenu {
                background: #111;
                border: 1px solid #222;
                border-radius: 8px;
            }
            QMenuItem {
                padding: 8px 25px;
                color: #e8ecf1;
            }
            QMenuItem:selected {
                background: #222;
                color: #ffd700;
            }
            QStatusBar {
                background: #0a0a0a0a;
                border-top: 1px solid #222;
                color: #8b95a5;
            }
            QToolTip {
                background: #222;
                color: #e8ecf1;
                border: 1px solid #333;
                padding: 8px 12px;
                border-radius: 6px;
            }
        """)
    
    def _setup_timers(self):
        """Настройка таймеров"""
        # Timer for clock updates
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)  # Update every second
    
    def _update_clock(self):
        """Обновление часов в статус-баре"""
        from datetime import datetime
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
    
    def _toggle_theme(self):
        """Перключение темы"""
        # TODO: Implement light/dark theme toggle
        pass
    
    def _on_export_report(self):
        """Экспорт отчёта"""
        from datetime import datetime
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        log.info(f"Exporting report: {filename}")
    
    def _show_about(self):
        """Показать диалог About"""
        QMessageBox.about(
            self,
            "🥇 Golden Emirat v2.0",
            f"""<h2>Golden Emirat v2.0</h2>
            <p>Professional Gold Trading Robot</p>
            <p><b>Version:</b> 2.0</p>
            <p><b>Python:</b> 3.11+</p>
            <p><b>Platform:</b> Windows/Linux/macOS</p>
            <hr>
            <p>© 2024-2026 Golden Emirat Team</p>
            <p style="color: #888;">Developed with ❤️ using PyQt6</p>"""
        )
    
    def _on_buy(self, symbol: str):
        """Обработка нажатия BUY"""
        log.info(f"BUY signal received for {symbol}")
        self.statusBar.showMessage(f"🟢 BUY {symbol}", 3000)
    
    def _on_sell(self, symbol: str):
        """Обработка нажатия SELL"""
        log.info(f"SELL signal received for {symbol}")
        self.statusBar.showMessage(f"🔴 SELL {symbol}", 3000)
    
    def _on_close_all(self):
        """Обработка закрытия всех позиций"""
        reply = QMessageBox.question(
            self,
            t('action.close_all'),
            "Are you sure you want to close ALL positions?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            log.warning("Closing all positions...")
            self.statusBar.showMessage("⏹ Closing all positions...", 3000)
    
    def update_connection_status(self, connected: bool, broker_name: str = ""):
        """Обновление статуса подключения"""
        if connected:
            self.connection_label.setText(f"✅ {t('status.connected')} | {broker_name}")
            self.connection_label.setStyleSheet("color: #00d4aa; font-weight: bold;")
        else:
            self.connection_label.setText(f"❌ {t('status.disconnected')}")
            self.connection_label.setStyleSheet("color: #ff4757; font-weight: bold;")
    
    def update_bot_status(self, running: bool):
        """Обновление статуса бота"""
        self.is_running = running
        if running:
            self.status_label.setText("● Running")
            self.status_label.setStyleSheet("color: #00d4aa; font-weight: bold;")
        else:
            self.status_label.setText("⏹ Stopped")
            self.status_label.setStyleSheet("color: #888; font-weight: bold;")
    
    def show_notification(self, title: str, message: str, level: str = "info"):
        """Показать уведомление"""
        self.statusBar.showMessage(f"{title}: {message}", 5000)
        log.log(level.upper(), f"{title}: {message}")
    
    def closeEvent(self, event):
        """Переопределение закрытия окна"""
        reply = QMessageBox.question(
            self,
            t('app.name'),
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            log.info("Application exiting...")
            super().closeEvent(event)


# Standalone launch function
def launch_gui():
    """Запуск GUI приложения"""
    app = QApplication(sys.argv)
    
    window = GoldenEmiratGUI()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    launch_gui()
