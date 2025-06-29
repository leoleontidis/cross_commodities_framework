# Cross-Commodities Portfolio Research Framework

<i>"A volatility-aware, subbook-balanced, mean-reverting spread trading system using dynamic z-score and rolling hedge ratios with risk monitoring, trade logging and capital tracking."</i>

This framework is a mean-reversion pair trading strategy based on z-score divergence between pairs of related commodities. It allows you to research and backtest dynamic, multi-sub-book commodity portfolios (oil, gas, grains, etc.) using futures. It supports sub-book risk control and modularity, dynamic asset selection, strategy backtesting, and risk/concentration analysis.

## Core Logic
1. Spread Trading Logic
    - Trades pairs of instruments (e.g., CL-NG, ZC-ZW) based on spread divergence from historical mean
    - Uses z-score of log-spread as the signal driver
2. Mean Reversion Hypothesis
    - Assumes that the spread between two related assets oscillates around a statistical mean
    - Entries occur at z-score ±Z_entry, exits at z-score approaching zero or Z_exit
3. Rolling Beta Hedge
    - Dynamically estimates hedge ratio (beta) using rolling linear regression
    - Accounts for changing correlation strength over time

4. Volatility Filter
    - Skips trades if the spread volatility exceeds a maximum threshold
    - Prevents entering trades in structurally unstable or noisy periods

5. Risk Management by Subbooks
    - Each subbook (e.g., oil, grains, gas) has its own starting capital
    - Positions and risk are calculated relative to the subbook’s current capital

6. Position Sizing Logic
    - Position size is proportional to:
        - 2% of current subbook capital
        - Adjusted by spread volatility (volatility-aware sizing)
    - Caps max position size for safety

7. Stop-Loss and Holding Time Limits
    - Hard stop-loss based on a multiple of spread volatility (default 3x).
    - Maximum holding period constraint to force exit if the spread doesn’t revert within a reasonable time frame.

8. Flexible Pair Selection
    - Supports:
        - Intra-subbook pairs (e.g., grains-grains).
        - Cross-subbook pairs (e.g., oil-grains).
        - Or all pairs.
    - Excludes pairs dynamically via config (excluded_pairs list).

9. Multi-Timeframe Support
    - Works with daily or 5-minute data (or other intervals) via data_interval config.

10. Full Backtest Transparency
    - Logs:
        - Spread history
        - Z-score evolution
        - Entry/exit points
        - PnL per pair and subbook
    - Each run produces a timestamped result folder with complete reports.

<br>

<b>Example:  </b><br>
<i>If the spread between CL and QM spikes (z > 1.5):
The strategy shorts CL and longs QM.
When spread reverts (z ≈ 0), it exits and logs the trade.</i>

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

**Create a virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate        # On Windows
# or
source .venv/bin/activate     # On macOS/Linux
```

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