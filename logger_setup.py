#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Golden Emirat v2.0 - Logger Setup Module
============================================
Настройка логирования с ротацией файлов и цветным выводом.
"""

import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime


def setup_logger(
    log_level: str = "DEBUG",
    log_dir: str = "logs",
    rotation: str = "10 MB",
    retention: str = "30 days",
    compression: str = "zip"
) -> None:
    """
    Настройка системы логирования.
    
    Args:
        log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
        log_dir: Директория для лог-файлов
        rotation: Размер файла для ротации
        retention: Период хранения логов
        compression: Метод сжатия старых логов
    """
    # Создание директории логов
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Удаление стандартного обработчика
    logger.remove()
    
    # Добавление консольного вывода (цветной)
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Добавление файлового вывода с ротацией
    log_file = log_path / f"golden_emirat_{datetime.now().strftime('%Y%m%d')}.log"
    
    logger.add(
        str(log_file),
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        rotation=rotation,
        retention=retention,
        compression=compression,
        encoding="utf-8"
    )
    
    # Отдельный файл для ошибок
    error_log = log_path / "errors.log"
    
    logger.add(
        str(error_log),
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        rotation="50 MB",
        retention="90 days",
        compression=compression,
        encoding="utf-8"
    )
    
    logger.success("Logger initialized successfully")
    logger.debug(f"Log file: {log_file.absolute()}")


def get_logger(name: str):
    """
    Получение логгера для конкретного модуля.
    
    Args:
        name: Имя модуля (обычно __name__)
    
    Returns:
        Логгер loguru
    """
    return logger.bind(name=name)


# Автоматическая настройка при импорте
setup_logger()

if __name__ == "__main__":
    # Тестирование
    setup_logger()
    
    log = get_logger("test")
    
    log.debug("Debug message")
    log.info("Info message")
    log.warning("Warning message")
    log.error("Error message")
    log.success("Success message")
