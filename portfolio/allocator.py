# portfolio/allocator.py

import numpy as np
import pandas as pd
import riskfolio as pf

class CapitalAllocator:
    def __init__(self, price_data: pd.DataFrame):
        """
        price_data: DataFrame with asset prices (columns = tickers)
        """
        self.price_data = price_data
        self.returns = price_data.pct_change().dropna()
        self.weights = None

    def equal_weight(self):
        n = len(self.returns.columns)
        self.weights = pd.Series([1/n] * n, index=self.returns.columns)
        return self.weights

    def min_volatility(self):
        port = pf.Portfolio(returns=self.returns)
        port.assets_stats(method_mu='hist', method_cov='ledoit')
        self.weights = port.optimization(model='Classic', obj='MinVol')
        return self.weights

    def max_sharpe(self, risk_free_rate=0.01):
        port = pf.Portfolio(returns=self.returns)
        port.assets_stats(method_mu='hist', method_cov='ledoit')
        self.weights = port.optimization(model='Classic', obj='Sharpe', rf=risk_free_rate)
        return self.weights

    def get_weights(self):
        return self.weights
    
    # Add these to portfolio/allocator.py (in addition to previous ones)

    def risk_parity(self):
        port = pf.Portfolio(returns=self.returns)
        port.assets_stats(method_mu='hist', method_cov='ledoit')
        self.weights = port.rp_optimization(model='Classic', rm='MV', hist=True)
        return self.weights

    def min_cvar(self, alpha=0.05):
        port = pf.Portfolio(returns=self.returns)
        port.assets_stats(method_mu='hist', method_cov='ledoit')
        self.weights = port.optimization(model='Classic', obj='MinRisk', rm='CVaR', hist=True, alpha=alpha)
        return self.weights

