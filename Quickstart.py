#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Emirat v2.0 - Quick Start Script
=====================================
Точка входа с автоустановкой зависимостей и проверкой окружения.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path


def check_python_version():
    """Проверка версии Python (требуется 3.11+)"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ Требуется Python 3.11 или выше!")
        print(f"   Ваша версия: {sys.version}")
        sys.exit(1)
    
    print("✅ Версия Python соответствует требованиям")
    return True


def check_virtual_env():
    """Проверка виртуального окружения"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Виртуальное окружение активно")
        return True
    
    print("⚠️  Виртуальное окружение НЕ активно!")
    print("   Рекомендуется создать: python -m venv venv")
    return False


def install_dependencies():
    """Установка зависимостей из requirements.txt"""
    req_file = Path(__file__).parent / "requirements.txt"
    
    if not req_file.exists():
        print("❌ Файл requirements.txt не найден!")
        return False
    
    print("\n📦 Установка зависимостей...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", str(req_file), "--upgrade"
        ])
        print("✅ Все зависимости успешно установлены!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки: {e}")
        return False


def create_config_template():
    """Создание шаблона конфигурации, если отсутствует"""
    config_dir = Path(__file__).parent / "config"
    config_file = config_dir / "config.json"
    
    if not config_file.exists():
        config_dir.mkdir(exist_ok=True)
        
        template = {
            "broker": {
                "type": "mt5",
                "server": "ICMarkets-Demo",
                "login": "",
                "password": "",
                "path": r"C:\Program Files\MetaTrader 5\terminal64.exe",
                "timezone": "Europe/Helsinki"
            },
            "trading": {
                "symbol": "XAUUSD",
                "lot_size": 0.01,
                "max_risk_percent": 2.0,
                "stop_loss_pips": 500,
                "take_profit_pips": 1000,
                "max_spread": 50
            },
            "strategies": {
                "trend_enabled": True,
                "scalping_enabled": True,
                "breakout_enabled": True,
                "news_trading_enabled": True
            },
            "notifications": {
                "telegram_enabled": False,
                "telegram_bot_token": "",
                "telegram_chat_id": ""
            },
            "display": {
                "language": "ru",
                "units": "$",
                "theme": "dark"
            },
            "time_sync": {
                "ntp_server": "pool.ntp.org",
                "auto_dst": True
            }
        }
        
        import json
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Создан шаблон конфигурации: {config_file}")
        return True
    
    return True


def create_directories():
    """Создание необходимых директорий"""
    dirs = [
        "logs", "data", "reports", "sounds", "screenshots",
        "backtest/results", "backtest/data"
    ]
    
    base_path = Path(__file__).parent
    
    for dir_name in dirs:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Директории созданы")


def run_main():
    """Запуск главного модуля"""
    print("\n" + "="*60)
    print("🥇 Запуск Golden Emirat v2.0...")
    print("="*60 + "\n")
    
    try:
        from main_golden import GoldenEmiratApp
        
        app = GoldenEmiratApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("\n💡 Попробуйте:")
        print("   1. pip install -r requirements.txt")
        print("   2. python Quickstart.py --install")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Главная функция"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🥇  GOLDEN EMIRAT v2.0 - Trading Bot for XAU/USD      ║
║      Professional Gold Trading Robot | MT4/MT5 Support     ║
║                                                           ║
║   Version: 2.0 | Python 3.11+ | Deep Black UI         ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Проверка аргументов командной строки
    if "--install" in sys.argv:
        install_dependencies()
        return
    
    if "--check" in sys.argv:
        check_python_version()
        check_virtual_env()
        return
    
    # Проверки перед запуском
    check_python_version()
    check_virtual_env()
    
    # Инициализация
    create_directories()
    create_config_template()
    
    # Запуск
    run_main()


if __name__ == "__main__":
    main()
