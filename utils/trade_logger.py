import pandas as pd

class TradeLogger:
    def __init__(self):
        self.trades = []

    def log_trade(self, dt, symbol, action, price, size, pnl=None):
        self.trades.append({
            "datetime": dt,
            "symbol": symbol,
            "action": action,
            "price": price,
            "size": size,
            "pnl": pnl
        })

    def to_dataframe(self):
        return pd.DataFrame(self.trades)

    def save_to_csv(self, path="data/processed/trade_log.csv"):
        df = self.to_dataframe()
        if not df.empty:
            df.to_csv(path, index=False)
            print(f"✅ Trade log saved to {path}")
        else:
            print("⚠️ No trades to save.")
