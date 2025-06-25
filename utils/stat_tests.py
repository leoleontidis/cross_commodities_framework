from statsmodels.tsa.stattools import adfuller
import numpy as np

def is_cointegrated(series1, series2, beta, max_pvalue=0.05, log_spread=True, verbose=False):
    if log_spread:
        spread = np.log(series1 + 1e-6) - beta * np.log(series2 + 1e-6)
    else:
        spread = series1 - beta * series2

    result = adfuller(spread.dropna())
    pvalue = result[1]
    if verbose:
        print(f"ADF p-value: {pvalue:.5f} for pair")
    return pvalue < max_pvalue