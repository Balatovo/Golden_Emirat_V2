<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Golden Emirat - Notifications Panel</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #000; color: #e8ecf1; padding: 20px; }
        pre { background: #111; padding: 20px; border-radius: 10px; overflow-x: auto; border-left: 4px solid #ffd700; }
        code { font-family: 'Fira Code', monospace; font-size: 13px; line-height: 1.5; color: #abb2bf; }
        .keyword { color: #c678dd; } .string { color: #98c379; } .comment { color: #5c6370; font-style: italic; } .class-name { color: #e5c07b; } .function { color: #61afef; }
        h2 { color: #ffd700; margin-bottom: 15px; }
    </style>
</head>
<body>
<h2>🔔 gui/notifications_panel.py — Панель уведомлений</h2>
<pre><code><span class="comment"># -*- coding: utf-8 -*-
"""Golden Emirat v2.0 - Notifications Panel Widget
=====================================================
Панель управления уведомлениями (Telegram, звуковые).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QPushButton, QCheckBox, QLineEdit,
    QTextEdit, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPixmap

from ..core.config import ConfigManager, t


class NotificationsPanelWidget(QWidget):
    """
    Виджет панели уведомлений.
    
    Features:
    - Настройка Telegram бота
    - Включение/выключение каналов
    - Просмотр истории уведомлений
    - Тестирование соединения
    """
    
    telegram_test_clicked = pyqtSignal()
    notification_received = pyqtSignal(dict)  # {type, message, time}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager().config.notifications
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        title = QLabel("🔔 Notifications Center")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addWidget(header)
        
        # Telegram Section
        tg_group = QGroupBox("📱 Telegram Bot")
        tg_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 14px;
                margin-top: 20px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 25px;
            }
        """)
        tg_form = QGridLayout()
        
        self.tg_enabled_cb = QCheckBox("Enable Telegram Notifications")
        self.tg_enabled_cb.setChecked(self.config.telegram_enabled)
        tg_form.addRow(self.tg_enabled_cb)
        
        token_label = QLabel("Bot Token:")
        self.token_edit = QLineEdit()
        self.token_edit.setPlaceholder("123456789:ABCdefGHI...")
        self.token_edit.setText(self.config.telegram_bot_token)
        self.token_edit.setEchoMode(QLineEdit.Password)
        tg_form.addRow(token_label, self.token_edit)
        
        chat_id_label = QLabel("Chat ID:")
        self.chat_id_edit = QLineEdit()
        self.chat_id_edit.setPlaceholder("@username (или числовой)")
        self.chat_id_edit.setText(self.config.telegram_chat_id)
        tg_form.addRow(chat_id_label, self.chat_id_edit)
        
        test_tg_btn = QPushButton("🧪 Test Connection")
        test_tg_btn.setStyleSheet("""
            QPushButton {
                background: #0088cc;
                color: #fff;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #00a0d0;
            }
        """)
        test_tg_btn.clicked.connect(self.telegram_test_clicked)
        tg_form.addRow("", test_tg_btn)
        
        tg_group.setLayout(tg_form)
        layout.addWidget(tg_group)
        
        # Sound Section
        sound_group = QGroupBox("🔊 Sound Alerts")
        sound_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 14px;
                margin-top: 20px;
                font-weight: bold;
                font font-size: 14px;
                padding-top: 25px;
            }
        """)
        sound_form = QVBoxLayout()
        
        self.sound_enabled_cb = QCheckBox("Enable Sound Alerts")
        self.sound_enabled_cb.setChecked(self.config.sound_enabled)
        sound_form.addWidget(self.sound_enabled_cb)
        
        volume_label = QLabel("Volume:")
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(int(self.config.sound_volume * 100))
        volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_row = QHBoxLayout()
        volume_row.addWidget(volume_label)
        volume_row.addWidget(volume_slider)
        self.volume_value_lbl = QLabel(f"{int(self.config.sound_volume * 100)}%")
        volume_row.addWidget(self.volume_value_lbl)
        sound_form.addRow(volume_row)
        
        sound_group.setLayout(sound_form)
        layout.addWidget(sound_group)
        
        # Log area
        log_group = QGroupBox("📜 Notification Log")
        log_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #222;
                border-radius: 14px;
                margin-top: 20px;
                font-weight: bold;
                font-size: 14px;
                padding-top: 25px;
            }
        """)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumBlockCount(200)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #080808;
                border: 1px solid #222;
                border-radius: 10px;
                font-family: 'Fira Code', monospace;
                font-size: 12px;
                line-height: 1.5;
                color: #888;
            }
        """)
        log_group.setLayout(QVBoxLayout())
        log_group.layout().addWidget(self.log_text)
        layout.addWidget(log_group)
        
        self.setLayout(layout)
    
    @property
    def telegram_enabled(self) -> bool:
        return self.tg_enabled_cb.isChecked()
    
    @property
    def sound_enabled(self) -> bool:
        return self.sound_enabled_cb.isChecked()
    
    @property
    def telegram_token(self) -> str:
        return self.token_edit.text()
    
    @property
    def chat_id(self) -> str:
        return self.chat_id_edit.text()
    
    def _on_volume_changed(self, value: int):
        """Изменение громкости"""
        self.volume_value_lbl.setText(f"{value}%")
        self.config.sound_volume = value / 100
    
    def telegram_test_clicked(self):
        """Тестирование Telegram соединения"""
        self.telegram_test_clicked.emit()
        
    def add_log_entry(self, message: str, level: str = "info"):
        """Добавление записи в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        colors = {
            "info": "#00d4aa",
            "success": "#00d4aa",
            "warning": "#ffd700",
            "error": "#ff4757"
        }
        color = colors.get(level, "#888")
        
        formatted = f"[{timestamp}] [{level.upper()}] {message}\n"
        self.log_text.append(formatted)
        
        # Auto-scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        self.notification_received.emit({
            "type": "log",
            "message": message,
            "time": timestamp
        })


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    widget = NotificationsPanelWidget()
    widget.show()
    
    print("✅ Notifications Panel ready")
    sys.exit(app.exec_())


from PyQt6.QtWidgets import QSlider
</code></pre>
</body>
</html>
