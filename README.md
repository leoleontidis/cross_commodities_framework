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


Example Output:

|pair|subbook|realized_pnl|unrealized_pnl|total_pnl|
|--------------------|--------------------|--------------------|--------------------|--------------------|
|CL - ZW|oil|-14.371165684351261|9909.99984741211|9895.628681727758|
|CL - BZ|oil|7.737114435950154|-17090.00015258789|-17082.26303815194|
|CL - HH|oil|26.031535647400794|-16977.499723434452|-16951.46818778705|
|CL - HO|oil|4.447366048735857|-17288.80000114441|-17284.352635095674|
|CL - ZS|oil|-3.6914391186075868|-15215.00015258789|-15218.691591706498|
|CL - QG|oil|-11.075863053104706|-17290.000200271606|-17301.076063324712|
|CL - ZC|oil|-12.576028996933886|-13715.00015258789|-13727.576181584824|
|CL - NG|oil|-18.871804524039028|-15470.000267028809|-15488.872071552847|
|ZW - BZ|grains|-18.4701013687234|27000.0|26981.529898631277|
|ZW - HH|grains|37.50117304884526|27112.50042915344|27150.001602202283|
|ZW - HO|grains|7.720179986301812|26801.20015144348|26808.920331429785|
|ZW - ZS|grains|1.6428326194177778|28875.0|28876.64283261942|
|ZW - QG|grains|-0.9302854313895104|26799.999952316284|26799.069666884894|
|ZW - ZC|grains|6.144836652674179|30375.0|30381.144836652675|
|BZ - HH|oil|74.82905538547003|112.50042915344038|187.3294845389104|
|BZ - HO|oil|0.8572296683286851|-198.799848556519|-197.94261888819034|
|BZ - ZS|oil|9.852270289355758|1875.0|1884.8522702893558|
|BZ - QG|oil|15.780613573418423|-200.00004768371582|-184.21943411029739|
|BZ - ZC|oil|276.41006239922297|3375.0|3651.410062399223|
|HH - HO|gas|11.23601781132544|-86.29941940307863|-75.06340159175319|
|HH - ZS|gas|0.0|1987.5004291534403|1987.5004291534403|
|HH - QG|gas|14.49856221428869|-87.49961853027544|-73.00105631598674|
|HH - ZC|gas|22.973083886907997|3487.5004291534406|3510.4735130403487|
|HH - NG|gas|0.0|1732.5003147125224|1732.5003147125224|
|HO - ZS|oil|0.0|1676.200151443481|1676.200151443481|
|HO - QG|oil|-17.78143735859439|-398.79989624023483|-416.58133359882925|
|HO - ZC|oil|6.668955979332036|3176.200151443481|3182.869107422813|
|ZS - QG|grains|-0.5372066454962798|1674.9999523162842|1674.4627456707879|
|ZS - ZC|grains|1.324047611625634|5250.0|5251.324047611625|
|ZS - NG|grains|-13.605460474177988|3494.999885559082|3481.394425084904|
|QG - ZC|gas|2.471110824608047|3174.999952316284|3177.471063140892|
|QG - NG|gas|0.0|1419.9998378753662|1419.9998378753662|
|ZC - NG|grains|-15.966434010771913|4994.999885559082|4979.03345154831|