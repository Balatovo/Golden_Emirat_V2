"""Загрузчик исторических данных для бэктеста."""
import pandas as pd
import yfinance as yf

class DataLoader:
    @staticmethod
    def load(symbol: str = "GC=F", start: str = "2023-01-01", end: str = "2024-01-01") -> pd.DataFrame:
        df = yf.download(symbol, start=start, end=end, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
        df.columns = [c.lower() for c in df.columns]
        return df
