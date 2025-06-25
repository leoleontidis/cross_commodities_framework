# utils/rank_spread_candidates.py

import os
import json
import pandas as pd
import numpy as np
from itertools import combinations
from statsmodels.tsa.stattools import adfuller
import seaborn as sns
import matplotlib.pyplot as plt

from data_loader import load_csv

def load_contract_symbols(path="config/contracts.json"):
    with open(path) as f:
        contracts = json.load(f)
    return list(set(contracts.keys()))

def compute_metrics(symbols, data_dir="data/raw"):
    pairs = list(combinations(symbols, 2))
    results = []

    for sym1, sym2 in pairs:
        try:
            df1 = load_csv(sym1)
            df2 = load_csv(sym2)
            df = pd.DataFrame({
                sym1: df1["Close"],
                sym2: df2["Close"]
            }).dropna()

            if len(df) < 100:
                continue

            returns = df.pct_change().dropna()
            corr = returns[sym1].corr(returns[sym2])

            # Cointegration test
            spread = df[sym1] - df[sym2]
            coint_pval = adfuller(spread.dropna())[1]

            results.append({
                "pair": f"{sym1}-{sym2}",
                "symbol1": sym1,
                "symbol2": sym2,
                "correlation": corr,
                "cointegration_pval": coint_pval
            })

        except Exception as e:
            print(f"[RANKER] - Failed {sym1}-{sym2}: {e}")

    return pd.DataFrame(results)

def rank_pairs(df, top_n=10):
    df["cointegration_score"] = 1 - df["cointegration_pval"]
    df["combined_score"] = df["correlation"].abs() * df["cointegration_score"]
    ranked = df.sort_values("combined_score", ascending=False).reset_index(drop=True)
    return ranked.head(top_n)

def plot_heatmap(df, symbols, output="data/processed/correlation_heatmap.png"):
    matrix = pd.DataFrame(index=symbols, columns=symbols, dtype=float)
    for _, row in df.iterrows():
        s1, s2 = row["symbol1"], row["symbol2"]
        matrix.loc[s1, s2] = row["correlation"]
        matrix.loc[s2, s1] = row["correlation"]
    matrix.fillna(1.0, inplace=True)

    plt.figure(figsize=(12, 10))
    sns.heatmap(matrix.astype(float), annot=False, cmap="coolwarm", fmt=".2f")
    plt.title("Pairwise Correlation Heatmap (All Contracts)")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output), exist_ok=True)
    plt.savefig(output)
    print(f"[RANKER] - Correlation heatmap saved to {output}")

if __name__ == "__main__":
    symbols = load_contract_symbols()
    df = compute_metrics(symbols)
    ranked = rank_pairs(df, top_n=10)
    ranked.to_csv("data/processed/top_spread_candidates.csv", index=False)
    print("\n[RANKER] - Top spread candidates saved to data/processed/top_spread_candidates.csv")
    print(ranked[["pair", "correlation", "cointegration_pval", "combined_score"]])

    plot_heatmap(df, symbols)
