# utils/data_loader.py

import pandas as pd
import os
import yfinance as yf
from datetime import datetime, timedelta

def download_data(symbol, start="2022-01-01", interval="1d"):
    end = datetime.today()

    if interval.endswith("m"):
        start = end - timedelta(days=59)

    df = yf.download(
        symbol,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval=interval,
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        raise ValueError(f"[LOADER] - No data returned for {symbol} ({interval})")
    df = df.reset_index()

    if "Datetime" in df.columns:
        df = df.rename(columns={"Datetime": "Date"})

    elif "Date" not in df.columns and "index" in df.columns:
        df = df.rename(columns={"index": "Date"})

    df.columns = [col[0].capitalize() if isinstance(col, tuple) else col.capitalize() for col in df.columns]

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    return df

def save_to_csv(df, symbol, interval="1d"):
    folder = f"data/raw/{interval}"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{symbol}.csv")
    df.to_csv(path)

def load_csv(symbol, interval="1d"):
    path = f"data/raw/{interval}/{symbol}.csv"
    if not os.path.exists(path):
        raise FileNotFoundError(f"[LOADER] - No data file found for {symbol} at {path}")
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.set_index("Date")
    return df
