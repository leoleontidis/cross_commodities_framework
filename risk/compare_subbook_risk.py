import pandas as pd
import os
from risk.risk_metrics import compute_risk_metrics
from risk.concentration import diversification_ratio

def compare_subbook_risks(subbooks, price_data_dir="data/raw"):
    results = []
    for subbook, symbols in subbooks.items():
        dfs = []
        for sym in symbols:
            path = os.path.join(price_data_dir, f"{sym}.csv")
            df = pd.read_csv(path, index_col=0, parse_dates=True)
            # Clean and enforce numeric
            df = df.loc[:, df.columns.str.lower().str.contains("close")]
            df.columns = [sym]  # Rename for merging
            df[sym] = pd.to_numeric(df[sym], errors="coerce")
            dfs.append(df)

        # Merge and drop NAs
        price_df = pd.concat(dfs, axis=1).dropna()
        returns = price_df.pct_change().dropna()

        weights = [1 / len(symbols)] * len(symbols)
        risk = compute_risk_metrics(price_df, weights)
        div_ratio = diversification_ratio(price_df, weights)
        risk["Diversification Ratio"] = div_ratio
        risk["Subbook"] = subbook
        results.append(risk)

    df_results = pd.DataFrame(results).set_index("Subbook")
    df_results.to_csv("data/processed/subbook_risk_comparison.csv")
    print("📊 Subbook risk comparison saved to data/processed/subbook_risk_comparison.csv")
