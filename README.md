# Cross-Commodities Portfolio Research Framework

This framework allows you to research and backtest dynamic, multi-sub-book commodity portfolios (oil, gas, grains, etc.) using mini futures. It supports sub-book modularity, dynamic asset selection, strategy backtesting, and risk/concentration analysis.

## Futures Symbols:  
### --- Oil Sub-Book ---  
>"CL": "CL=F",  # Crude Oil Futures (NYMEX)  
"QM": "QM=F",  # E-mini Crude Oil (NYMEX)  
"MCL": "MCL=F", # Micro Crude Oil (NYMEX)  
"HO": "HO=F",  # Heating Oil Futures (NYMEX)  
"RB": "RB=F",  # RBOB Gasoline (NYMEX)

### --- Gas Sub-Book ---  
>"NG": "NG=F",  # Henry Hub Natural Gas (NYMEX)  
"QG": "QG=F",  # E-mini Natural Gas (less liquid)

### --- Grain Sub-Book ---  
>"ZC": "ZC=F",  # Corn  
"ZW": "ZW=F",  # Wheat  
"ZS": "ZS=F",  # Soybeans  
"ZL": "ZL=F",  # Soybean Oil  
"YC": "YC=F",  # Mini Corn (CBOT)  
"YK": "YK=F",  # Mini Soybeans (CBOT)  
"YW": "YW=F",  # Mini Wheat (CBOT) 

### --- Softs Sub-Book ---  
>"KC": "KC=F",  # Coffee  
"CC": "CC=F",  # Cocoa  
"SB": "SB=F",  # Sugar  
"CT": "CT=F",  # Cotton  
"OJ": "OJ=F",  # Orange Juice  

### --- Metals Sub-Book ---  
>"GC": "GC=F",  # Gold  
"SI": "SI=F",  # Silver  
"HG": "HG=F",  # Copper  
"MGC": "MGC=F",# Micro Gold  
"SIL": "SIL=F",# Micro Silver  

### --- Livestock Sub-Book ---  
>"LE": "LE=F",  # Live Cattle  
"HE": "HE=F",  # Lean Hogs  
"GF": "GF=F",  # Feeder Cattle  

## Features

- 📦 Unified day-by-day simulation across multiple subbooks (Oil, Gas, Grains, Metals, Livestock, Softs).
- 🔗 Log-spread trading with rolling beta estimation and cointegration filtering.
- 🏗️ Portfolio capital allocation by subbook.
- 📊 Full risk analytics: CVaR, Sharpe, volatility, Herfindahl index, diversification ratio.
- 🔍 Statistical filtering of pair candidates (correlation + cointegration ranking).
- 🔥 Parameter optimization for spread strategies (Z-entry, Z-exit, lookback).
- 🧠 Pairwise PnL tracking, trade logs, realized/unrealized PnL separation.
- 📈 Visualization tools for spreads, z-scores, and trading signals.

---

## 📂 Repository Structure

| Folder         | Description                                       |
|----------------|---------------------------------------------------|
| `config/`      | Config files (`config.json`, symbol maps)        |
| `data/`        | Raw and processed datasets                       |
| `portfolio/`   | Portfolio engine and allocation logic            |
| `risk/`        | Risk metrics, concentration analysis             |
| `strategies/`  | Spread trading strategy                          |
| `subbooks/`    | Asset group definitions (Oil, Gas, Grains, etc.) |
| `utils/`       | Data loader, parameter optimizer, plotters       |
| `notebooks/`   | Reporting notebook (`report.ipynb`)              |

---

## Quickstart

1️⃣ **Install dependencies:**

```bash
pip install -r requirements.txt
```

2️⃣ Configure your trading setup:

Edit config/config.json.

| Key                  | Description                                    |
| -------------------- | ---------------------------------------------- |
| `start_date`         | Start date for backtest (e.g., `"2023-01-01"`) |
| `data_interval`      | Data interval (`"1d"`, `"1h"`, `"15m"`)        |
| `capital`            | Total capital in USD                           |
| `slippage_pct`       | Slippage per trade (e.g., `0.001` = 0.1%)      |
| `capital_allocation` | Subbook budgets + contracts                    |
| `pair_mode`          | `"intra"`, `"cross"`, or `"all"`               |
| `excluded_pairs`     | List of pairs to skip (optional)               |


3️⃣ Download data:
```bash
python utils/download_all_contracts.py
```
---> Saves data to data/raw/

4️⃣ Run the backtest:
```bash
python main.py
```

6️⃣ View reports:

Open the notebook:
```bash
jupyter lab notebooks/report.ipynb
python utils/plot_spread.py
```
7️⃣ Optional Tools  
---> Optimize parameters for spreads:
```bash
python utils/optimize_spread_parameters.py
```
---> Rank spread candidates by correlation + cointegration:

```bash
python utils/rank_spread_candidates.py
```
---> Compare subbook risk:
```bash
python risk/compare_subbook_risk.py
```

8️⃣ Outputs  
✔️ Spread z-scores with trades  
✔️ Risk analysis by subbook  
✔️ Pairwise PnL breakdown  
✔️ Correlation heatmaps  
✔️ Cointegration rankings  