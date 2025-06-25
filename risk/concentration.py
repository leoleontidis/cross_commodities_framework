# risk/concentration.py

import pandas as pd
import numpy as np

def herfindahl_index(weights: pd.Series):
    return (weights ** 2).sum()

def diversification_ratio(price_data: pd.DataFrame, weights: pd.Series):
    returns = price_data.pct_change().dropna()
    stds = returns.std()
    weighted_std = (weights * stds).sum()
    portfolio_std = returns @ weights
    total_std = portfolio_std.std()
    return weighted_std / total_std
