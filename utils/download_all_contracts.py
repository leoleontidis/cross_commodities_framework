# utils/download_all_contracts.py

import os
import json
from data_loader import download_data, save_to_csv

def load_contracts(path="config/contracts.json"):
    with open(path) as f:
        return json.load(f)

def download_all(start_date="2023-01-01", interval="1d", output_dir="data/raw"):
    contracts = load_contracts()
    os.makedirs(output_dir, exist_ok=True)

    for symbol, yf_symbol in contracts.items():
        try:
            print(f"⬇️ Downloading {symbol} ({yf_symbol})...")
            df = download_data(yf_symbol, start=start_date, interval=interval)
            if not df.empty:
                save_to_csv(df, symbol)
                print(f"✅ Saved {symbol} to {output_dir}/{symbol}.csv")
            else:
                print(f"⚠️ No data for {symbol}")
        except Exception as e:
            print(f"❌ Failed {symbol} ({yf_symbol}): {e}")

if __name__ == "__main__":
    download_all()
