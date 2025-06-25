# main.py — Unified day-by-day simulation with pair filtering

import os
import json
import pandas as pd
import backtrader as bt
from itertools import combinations
from utils.data_loader import load_csv, download_data, save_to_csv
from strategies.spread_pair_strategy import SpreadPairStrategy
from risk.risk_metrics import compute_risk_metrics
from risk.concentration import herfindahl_index, diversification_ratio
import statsmodels.api as sm

# Load config
with open("config/config.json") as f:
    config = json.load(f)

symbol_map_path = config.get("symbol_map_path", "config/contracts.json")
with open(symbol_map_path) as f:
    symbol_map = json.load(f)

start_date = config.get("start_date", "2023-01-01")
initial_capital = config.get("capital", 10_000_000)
slippage_pct = config.get("slippage_pct", 0.001)
excluded_pairs = set(config.get("excluded_pairs", []))

capital_allocation = config["capital_allocation"]
symbols = sum([entry["contracts"] for entry in capital_allocation.values()], [])
data_interval = config.get("data_interval", "1d")

log_path = "data/processed/failed_spreads.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/processed/zscore", exist_ok=True)

def get_data(symbol):
    try:
        return load_csv(symbol, interval=data_interval)
    except FileNotFoundError:
        yf_symbol = symbol_map.get(symbol)
        print(f"Downloading {symbol} ({yf_symbol}) with interval '{data_interval}'...")
        df = download_data(yf_symbol, start=start_date, interval=data_interval)
        save_to_csv(df, symbol, interval=data_interval)
        return df

def estimate_beta(asset1_series, asset2_series):
    model = sm.OLS(asset1_series, sm.add_constant(asset2_series)).fit()
    return model.params.iloc[1]

def find_subbook(symbol):
    for book, info in capital_allocation.items():
        if symbol in info["contracts"]:
            return book
    print(f"⚠️ Symbol {symbol} not found in any subbook.")
    return None

def run_portfolio():
    for file in [
        'data/processed/spread_trades.csv',
        'data/processed/portfolio_risk_metrics.csv',
        'data/processed/portfolio_summary.csv',
        'data/processed/pairwise_pnl_summary.csv'
    ]:
        if os.path.exists(file):
            os.remove(file)

    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(initial_capital)

    print("\n🧾 Initial Capital Allocation per Subbook:")
    for book, info in capital_allocation.items():
        print(f"  📘 {book.capitalize()}: {info['budget']:,.2f}")

    symbol_data = {}
    for symbol in set(symbols):
        df = get_data(symbol)
        feed = bt.feeds.PandasData(dataname=df, name=symbol)
        cerebro.adddata(feed)
        symbol_data[symbol] = df

    pairs = list(combinations(set(symbols), 2))
    pair_mode = config.get("pair_mode", "intra")

    for s1, s2 in pairs:
        book1 = find_subbook(s1)
        book2 = find_subbook(s2)

        pair_name = f"{s1} - {s2}"
        reverse_pair = f"{s2} - {s1}"

        if pair_name in excluded_pairs or reverse_pair in excluded_pairs:
            print(f"🚫 Skipping excluded pair: {pair_name}")
            continue

        if book1 is None or book2 is None:
            print(f"⛔ Skipping pair {s1}-{s2} | book1={book1}, book2={book2}")
            continue

        if pair_mode == "intra" and book1 != book2:
            continue
        elif pair_mode == "cross" and book1 == book2:
            continue
        elif pair_mode not in ["intra", "cross", "all"]:
            print(f"⚠️ Invalid pair_mode '{pair_mode}' in config. Skipping pair {s1}-{s2}.")
            continue

        try:
            df1 = symbol_data[s1]
            df2 = symbol_data[s2]
            common_idx = df1.index.intersection(df2.index)
            beta = estimate_beta(df1.loc[common_idx, "Close"], df2.loc[common_idx, "Close"])

            subbook_budget = capital_allocation.get(book1, {}).get("budget", initial_capital)
            cerebro.addstrategy(
                SpreadPairStrategy,
                asset1_name=s1,
                asset2_name=s2,
                spread_lookback=60,
                z_entry=2.0,
                z_exit=0.5,
                slippage_pct=slippage_pct,
                stop_loss_multiple=3.0,
                subbook_name=book1,
                subbook_start_capital=subbook_budget,
                rolling_beta=True,
                beta_static=1.0,
                beta_lookback=20,
                use_log_spread=True,
                max_holding_period=5 * 24 * 4,  # ~5 days at 15-min bars
                volatility_filter=True,
                volatility_lookback=50,
                max_volatility=5.0
            )

        except Exception as e:
            with open(log_path, "a") as f:
                f.write(f"Failed pair {s1}-{s2}: {str(e)}\n")

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")

    results = cerebro.run()
    strat = results[0]

    if os.path.exists("data/processed/spread_trades.csv"):
        df_trades = pd.read_csv("data/processed/spread_trades.csv")
        subbook_pnls = {book: 0.0 for book in capital_allocation}

        for _, row in df_trades.iterrows():
            symbol_pair = row['symbol']
            s1, s2 = symbol_pair.split(" - ")
            book = find_subbook(s1)
            if book:
                subbook_pnls[book] += row["pnl"]

        print("\n💰 Final Subbook Results:")
        final_total = 0.0
        for book, pnl in subbook_pnls.items():
            start_cap = capital_allocation[book]["budget"]
            final_cap = start_cap + pnl
            final_total += final_cap
            print(f"  📘 {book.capitalize()}: Start = {start_cap:,.2f}, PnL = {pnl:,.2f}, Final = {final_cap:,.2f}")

        print(f"\n📦 Portfolio Final Value: {final_total:,.2f}")

        if not df_trades.empty and "pnl" in df_trades.columns:
            sharpe = strat.analyzers.sharpe.get_analysis().get("sharperatio", None)
            drawdown = strat.analyzers.drawdown.get_analysis()["max"]["drawdown"]
            ret = strat.analyzers.returns.get_analysis().get("rtot", None)
            final_value = cerebro.broker.getvalue()

            wins = (df_trades["pnl"] > 0).sum()
            losses = (df_trades["pnl"] <= 0).sum()
            total = wins + losses
            win_rate = wins / total if total else 0
            loss_rate = losses / total if total else 0

            summary_df = pd.DataFrame([{
                "portfolio_value": final_value,
                "sharpe": sharpe,
                "drawdown": drawdown,
                "return_pct": ret,
                "total_trades": total,
                "wins": wins,
                "losses": losses,
                "win_rate": win_rate,
                "loss_rate": loss_rate
            }])
            summary_df.to_csv("data/processed/portfolio_summary.csv", index=False)
            print("\n📊 Portfolio Summary saved to data/processed/portfolio_summary.csv")

    price_data = pd.DataFrame({s: symbol_data[s]["Close"] for s in symbol_data}).dropna()
    returns = price_data.pct_change().dropna()

    from portfolio.allocator import CapitalAllocator
    allocator = CapitalAllocator(price_data)
    weights = allocator.equal_weight()

    risk = compute_risk_metrics(price_data, weights)
    risk["Herfindahl Index"] = herfindahl_index(weights)
    risk["Diversification Ratio"] = diversification_ratio(price_data, weights)
    risk.to_csv("data/processed/portfolio_risk_metrics.csv")

    print("\n✅ Backtest completed and metrics saved.")
    print('Final Portfolio Value: {:,.2f}'.format(cerebro.broker.getvalue()))

if __name__ == "__main__":
    run_portfolio()
