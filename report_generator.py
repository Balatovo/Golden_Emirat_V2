"""Генератор отчетов."""
import json
from pathlib import Path

class ReportGenerator:
    @staticmethod
    def save_json(stats: dict, path: Path = Path("backtest_report.json")):
        with open(path, 'w') as f:
            json.dump(stats, f, indent=4)
