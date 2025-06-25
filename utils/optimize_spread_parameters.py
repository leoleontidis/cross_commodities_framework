# optimize_spread_parameters.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# optimize_spread_parameters.py

import os
import json
import pandas as pd
import backtrader as bt
from itertools import product, combinations
from utils.data_loader import load_csv
from strategies.spread_pair_strategy import SpreadPairStrategy
import statsmodels.api as sm

# Load config
with open("config/config.json") as f:
    config = json.load(f)

symbol_map_path = config.get("symbol_map_path", "config/contracts.json")
with open(symbol_map_path) as f:
    symbol_map = json.load(f)

capital_allocation = config["capital_allocation"]
symbols_by_subbook = {book: info["contracts"] for book, info in capital_allocation.items()}
all_symbols = sum([v for v in symbols_by_subbook.values()], [])
start_date = config.get("start_date", "2023-01-01")
initial_capital = config.get("capital", 10_000_000)
slippage_pct = config.get("slippage_pct", 0.001)

def find_subbook(symbol):
    for book, contracts in symbols_by_subbook.items():
        if symbol in contracts:
            return book
    return None

def estimate_beta(asset1_series, asset2_series):
    model = sm.OLS(asset1_series, sm.add_constant(asset2_series)).fit()
    return model.params.iloc[1]

# Parameter grid
z_entries = [0.5, 1.0, 1.5]
z_exits = [0.1, 0.25, 0.5]
lookbacks = [10, 20, 30]
param_grid = list(product(z_entries, z_exits, lookbacks))

results = []

# Build intra + cross subbook pairs
pairs = []
for a, b in combinations(set(all_symbols), 2):
    book1 = find_subbook(a)
    book2 = find_subbook(b)
    if not book1 or not book2:
        continue
    tag = book1 if book1 == book2 else "cross"
    pairs.append((a, b, tag))

print(f"\n🔍 Total Pairs to Optimize: {len(pairs)}")

for s1, s2, book in pairs:
    print(f"\n🔍 Optimizing {s1}-{s2} ({book})")
    subbook_budget = capital_allocation.get(book, {}).get("budget", initial_capital)
    best_result = None

    try:
        df1 = load_csv(s1)
        df2 = load_csv(s2)
        common_idx = df1.index.intersection(df2.index)
        df1 = df1.loc[common_idx]
        df2 = df2.loc[common_idx]
        if len(common_idx) < 50:
            print(f"⚠️ Not enough data overlap for {s1}-{s2}")
            continue

        beta = estimate_beta(df1["Close"], df2["Close"])

        for z_entry, z_exit, lookback in param_grid:
            cerebro = bt.Cerebro()
            cerebro.broker.set_cash(subbook_budget)

            data1 = bt.feeds.PandasData(dataname=df1, name=s1)
            data2 = bt.feeds.PandasData(dataname=df2, name=s2)
            cerebro.adddata(data1)
            cerebro.adddata(data2)

            cerebro.addstrategy(
                SpreadPairStrategy,
                asset1_name=s1,
                asset2_name=s2,
                beta=beta,
                spread_lookback=lookback,
                z_entry=z_entry,
                z_exit=z_exit,
                slippage_pct=slippage_pct,
                subbook_name=book,
                subbook_start_capital=subbook_budget
            )

            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
            cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")

            results_bt = cerebro.run()
            strat = results_bt[0]

            sharpe = strat.analyzers.sharpe.get_analysis().get("sharperatio", 0.0)
            drawdown = strat.analyzers.drawdown.get_analysis().get("max", {}).get("drawdown", 1e6)
            total_return = strat.analyzers.returns.get_analysis().get("rtot", 0.0)

            result = {
                "pair": f"{s1}-{s2}",
                "subbook": book,
                "z_entry": z_entry,
                "z_exit": z_exit,
                "lookback": lookback,
                "sharpe": sharpe,
                "drawdown": drawdown,
                "return_pct": total_return
            }
            print(result)
            results.append(result)


    except Exception as e:
        print(f"❌ Skipping {s1}-{s2}: {e}")
        continue


# Save results
os.makedirs("data/processed", exist_ok=True)
df = pd.DataFrame(results)
df.to_csv("data/processed/best_pair_parameters.csv", index=False)
print("\n✅ Optimization completed and saved to data/processed/best_pair_parameters.csv")
