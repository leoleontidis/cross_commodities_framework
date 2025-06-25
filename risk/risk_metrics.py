# risk/risk_metrics.py

import pandas as pd
from riskfolio import Portfolio

def compute_risk_metrics(price_data: pd.DataFrame, weights: pd.Series, alpha=0.05):
    returns = price_data.pct_change().dropna()
    returns.columns = returns.columns.astype(str)
    weights.index = weights.index.astype(str)

    port = Portfolio(returns=returns)
    port.assets_stats(method_mu='hist', method_cov='ledoit')

    mu = port.mu.iloc[0]  # Get first row as Series
    cov = port.cov

    # Align symbols
    common_assets = list(set(weights.index) & set(mu.index) & set(cov.index))
    if len(common_assets) == 0:
        raise ValueError("No common assets between weights, mu, and cov.")

    weights = weights[common_assets]
    mu = mu[common_assets]
    cov = cov.loc[common_assets, common_assets]

    expected_return = weights.dot(mu)
    volatility = (weights.T @ cov @ weights) ** 0.5

    # ✅ Portfolio-level CVaR (manual)
    portfolio_returns = returns[common_assets] @ weights
    cvar = portfolio_returns[portfolio_returns <= portfolio_returns.quantile(alpha)].mean()

    metrics = {
        "Expected Return": expected_return,
        "Volatility": volatility,
        f"CVaR ({int((1-alpha)*100)}%)": cvar
    }

    return pd.Series(metrics)

def risk_contributions(price_data: pd.DataFrame, weights: pd.Series):
    returns = price_data.pct_change().dropna()
    weights = weights[price_data.columns]  # Ensure alignment

    cov = returns.cov()
    portfolio_vol = (weights.T @ cov @ weights) ** 0.5

    # Marginal contribution: ∂σ/∂w = (Σw) / σ
    marginal_contrib = cov @ weights
    risk_contrib = weights * marginal_contrib
    pct_risk_contrib = (risk_contrib / portfolio_vol**2) * 100

    return pd.DataFrame({
        "Marginal": marginal_contrib,
        "Abs Contribution": risk_contrib,
        "Percent Contribution": pct_risk_contrib
    }).T

