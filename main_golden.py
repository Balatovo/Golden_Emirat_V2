"""Главный модуль запуска приложения."""
import sys
from loguru import logger
from gui.golden_gui import GoldenEmiratApp

def start():
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{message}</level>")
    logger.info("Инициализация Golden Emirat v2.0...")
    
    app = GoldenEmiratApp(sys.argv)
    sys.exit(app.exec())

if __name__ == "__main__":
    start()
