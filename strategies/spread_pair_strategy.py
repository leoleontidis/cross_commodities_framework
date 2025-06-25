# strategies/spread_pair_strategy.py

import backtrader as bt
import pandas as pd
import numpy as np
import statsmodels.api as sm
import os

class SpreadPairStrategy(bt.Strategy):
    params = dict(
        asset1_name=None,
        asset2_name=None,
        spread_lookback=60,
        z_entry=2.0,
        z_exit=0.5,
        slippage_pct=0.001,
        stop_loss_multiple=2.0,
        subbook_name=None,
        subbook_start_capital=1_000_000,
        rolling_beta=True,
        beta_static=1.0,
        beta_lookback=20,
        use_log_spread=True,
        max_holding_period=5 * 24 * 4,
        volatility_filter=True,
        volatility_lookback=50,
        max_volatility=3.0
    )

    def __init__(self):
        self.spread_hist = []
        self.zscore_series = []
        self.datetime_series = []
        self.entry_timestamps = []
        self.exit_timestamps = []

        self.active_trade = None
        self.trades = []
        self.subbook_value = self.p.subbook_start_capital

        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

    def start(self):
        self.asset1 = next(d for d in self.datas if d._name == self.p.asset1_name)
        self.asset2 = next(d for d in self.datas if d._name == self.p.asset2_name)
        self.log(f"✅ Initialized spread: {self.p.asset1_name} - {self.p.asset2_name} | β₀ = {self.p.beta_static:.3f}")
        self.log(f"START | subbook={self.p.subbook_name} | capital={self.subbook_value:.2f}")

    def compute_beta(self):
        price1_hist = self.asset1.close.get(size=self.p.beta_lookback)
        price2_hist = self.asset2.close.get(size=self.p.beta_lookback)
        if self.p.rolling_beta and len(price1_hist) == self.p.beta_lookback:
            try:
                beta_est = sm.OLS(price1_hist, sm.add_constant(price2_hist)).fit().params[1]
                return beta_est if np.isfinite(beta_est) else self.p.beta_static
            except Exception:
                return self.p.beta_static
        return self.p.beta_static

    def next(self):
        beta = self.compute_beta()
        price1 = self.asset1.close[0]
        price2 = self.asset2.close[0]

        spread = (np.log(price1 + 1e-6) - beta * np.log(price2 + 1e-6)
                  if self.p.use_log_spread else price1 - beta * price2)

        self.spread_hist.append(spread)

        if len(self.spread_hist) < self.p.spread_lookback:
            return

        spread_series = pd.Series(self.spread_hist[-self.p.spread_lookback:])
        zscore = (spread - spread_series.mean()) / (spread_series.std() + 1e-6)

        self.zscore_series.append(zscore)
        self.datetime_series.append(self.datas[0].datetime.datetime(0))

        spread_vol = np.std(self.spread_hist[-self.p.volatility_lookback:]) + 1e-6

        self.log(f"[SPREAD] {spread:.4f} | Vol={spread_vol:.4f} | Z={zscore:.2f}")

        if self.p.volatility_filter and spread_vol > self.p.max_volatility:
            self.log(f"⚠️ Volatility too high ({spread_vol:.2f}), skipping trade.")
            return

        pos1 = self.getposition(self.asset1).size
        pos2 = self.getposition(self.asset2).size

        if self.active_trade:
            holding_period = len(self) - self.active_trade["entry_index"]
            if holding_period >= self.p.max_holding_period:
                self.close(self.asset1)
                self.close(self.asset2)
                self._close_trade(spread)
                self.exit_timestamps.append(self.datas[0].datetime.datetime(0))
                self.log(f"⏰ Max holding period reached ({holding_period} bars) — exiting trade.")
                self.active_trade = None
                return

            # ✅ Hard stop-loss logic
            entry_spread = self.active_trade['entry_spread']
            spread_move = spread - entry_spread if self.active_trade["side"] == "Long Spread" else entry_spread - spread
            stop_loss_threshold = self.p.stop_loss_multiple * spread_vol

            if spread_move < -stop_loss_threshold:
                self.close(self.asset1)
                self.close(self.asset2)
                self._close_trade(spread)
                self.exit_timestamps.append(self.datas[0].datetime.datetime(0))
                self.log(f"🛑 Hard stop-loss hit | Spread moved {spread_move:.2f} against position")
                self.active_trade = None
                return

        if pos1 == 0 and pos2 == 0:
            size1, size2 = self.calc_hedged_position_size(beta)
            self.log(f"Z={zscore:.2f} | Spread={spread:.2f} | pos=({pos1},{pos2}) | size=({size1},{size2}) | β={beta:.2f}")

            if zscore > self.p.z_entry:
                self.sell(self.asset1, size=size1)
                self.buy(self.asset2, size=size2)
                self.active_trade = self._create_trade_dict('Short Spread', spread, price1, price2, size1, size2)
                self.entry_timestamps.append(self.datas[0].datetime.datetime(0))
                self.log(f"📉 Short Spread entered at {spread:.2f} (z={zscore:.2f})")

            elif zscore < -self.p.z_entry:
                self.buy(self.asset1, size=size1)
                self.sell(self.asset2, size=size2)
                self.active_trade = self._create_trade_dict('Long Spread', spread, price1, price2, size1, size2)
                self.entry_timestamps.append(self.datas[0].datetime.datetime(0))
                self.log(f"📈 Long Spread entered at {spread:.2f} (z={zscore:.2f})")

        elif self.active_trade and abs(zscore) <= self.p.z_exit:
            self.close(self.asset1)
            self.close(self.asset2)
            self._close_trade(spread)
            self.exit_timestamps.append(self.datas[0].datetime.datetime(0))
            self.log(f"🎯 Target reached | Spread reverted to {spread:.2f}")
            self.active_trade = None

    def calc_hedged_position_size(self, beta):
        risk = 0.02 * self.subbook_value
        spread_vol = np.std(self.spread_hist[-self.p.spread_lookback:]) + 1e-6
        spread_vol = max(1.0, min(spread_vol, 5000.0))
        max_size = 500
        size = max(1, min(int(risk / spread_vol), max_size))
        hedge_size = max(-max_size, min(int(size * beta), max_size))
        self.log(f"[SIZE] risk={risk:.2f} | vol={spread_vol:.2f} | size1={size} | β={beta:.2f} | size2={hedge_size}")
        return size, hedge_size

    def _create_trade_dict(self, side, spread, price1, price2, size1, size2):
        return {
            'symbol': f"{self.p.asset1_name} - {self.p.asset2_name}",
            'side': side,
            'entry_date': self.datetime.date(0),
            'entry_index': len(self),
            'entry_spread': spread,
            'price1': price1,
            'price2': price2,
            'size1': size1,
            'size2': size2,
        }

    def _close_trade(self, exit_spread):
        trade = self.active_trade
        entry_spread = trade['entry_spread']
        entry_spread_safe = entry_spread if abs(entry_spread) > 1e-6 else 1e-6
        pnl = (entry_spread - exit_spread) * trade['size1']
        if trade['side'] == 'Long Spread':
            pnl *= -1
        self.subbook_value += pnl
        self.realized_pnl += pnl
        trade.update({
            'exit_date': self.datetime.date(0),
            'exit_index': len(self),
            'exit_spread': exit_spread,
            'pnl': pnl,
            'duration': len(self) - trade['entry_index'],
            'return_pct': ((exit_spread - entry_spread_safe) / abs(entry_spread_safe)) *
                        (1 if trade['side'] == 'Long Spread' else -1)
        })
        self.trades.append(trade)
        self.log(f"✅ Trade closed | {trade['side']} | Spread: {exit_spread:.2f} | PnL: {pnl:.2f} | Capital: {self.subbook_value:.2f}")

    def stop(self):
        pos1 = self.getposition(self.asset1)
        pos2 = self.getposition(self.asset2)
        unrealized = 0.0
        if pos1.size != 0:
            price_diff1 = (self.asset1.close[0] - pos1.price) * pos1.size
            unrealized += price_diff1
        if pos2.size != 0:
            price_diff2 = (self.asset2.close[0] - pos2.price) * pos2.size
            unrealized += price_diff2
        self.unrealized_pnl = unrealized

        if self.active_trade:
            beta = self.compute_beta()
            final_spread = (np.log(self.asset1.close[0]) - beta * np.log(self.asset2.close[0])
                            if self.p.use_log_spread else self.asset1.close[0] - beta * self.asset2.close[0])
            self._close_trade(final_spread)
            self.exit_timestamps.append(self.datas[0].datetime.datetime(0))
            self.log(f"⚠️ Forced exit at {final_spread:.2f}")
            self.active_trade = None

        if self.trades:
            df = pd.DataFrame(self.trades)
            df = df[['symbol', 'side', 'entry_date', 'entry_spread', 'exit_date', 'exit_spread',
                    'size1', 'size2', 'pnl', 'duration', 'return_pct']]
            file_path = 'data/processed/spread_trades.csv'
            df.to_csv(file_path, mode='a' if os.path.exists(file_path) else 'w',
                    header=not os.path.exists(file_path), index=False)

        summary_row = {
            'pair': f'{self.p.asset1_name} - {self.p.asset2_name}',
            'subbook': self.p.subbook_name,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'total_pnl': self.realized_pnl + self.unrealized_pnl
        }
        summary_path = 'data/processed/pairwise_pnl_summary.csv'
        df_row = pd.DataFrame([summary_row])
        df_row.to_csv(summary_path, mode='a' if os.path.exists(summary_path) else 'w',
                    header=not os.path.exists(summary_path), index=False)

        self.log(f"🧾 Pair PnL | Realized: {self.realized_pnl:.2f} | Unrealized: {self.unrealized_pnl:.2f}")

    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} | {self.p.asset1_name}-{self.p.asset2_name} | {txt}")
