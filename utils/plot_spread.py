import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_spread_zscore_with_trades(pair_id: str, z_entry=1.0, z_exit=0.25):
    """
    Plot z-score and spread with trade entry/exit markers for a given pair.

    Args:
        pair_id (str): e.g., "CL_NG"
        z_entry (float): z-score entry threshold
        z_exit (float): z-score exit threshold
    """
    base_path = "data/processed/zscore/"
    z_path = os.path.join(base_path, f"zscore_series_{pair_id}.csv")
    e_path = os.path.join(base_path, f"entries_{pair_id}.csv")
    x_path = os.path.join(base_path, f"exits_{pair_id}.csv")

    if not all(map(os.path.exists, [z_path, e_path, x_path])):
        print(f"⛔ Missing data files for {pair_id}.")
        return

    # Load data
    df = pd.read_csv(z_path, parse_dates=["datetime"])
    entries = pd.read_csv(e_path, parse_dates=["entry"])["entry"]
    exits = pd.read_csv(x_path, parse_dates=["exit"])["exit"]

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    # ax1: z-score with entry/exit markers
    # ax2: spread

    ax1.plot(df["datetime"], df["zscore"], label="Z-Score", color="blue")
    ax1.axhline(z_entry, color="red", linestyle="--", label=f"+Z Entry ({z_entry})")
    ax1.axhline(-z_entry, color="green", linestyle="--", label=f"-Z Entry ({-z_entry})")
    ax1.axhline(z_exit, color="gray", linestyle="--", label=f"+Z Exit ({z_exit})")
    ax1.axhline(-z_exit, color="gray", linestyle="--", label=f"-Z Exit ({-z_exit})")

    for t in entries:
        ax1.axvline(t, color="blue", linestyle=":", alpha=0.4)
    for t in exits:
        ax1.axvline(t, color="orange", linestyle=":", alpha=0.4)


    ax1.set_title(f"Z-Score and Trades for {pair_id}")
    ax1.set_ylabel("Z-Score")
    ax1.legend()
    ax1.grid(True)
    
    ax2.plot(df["datetime"], df["spread"], color="black")
    ax2.set_title("Spread Series")
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

plot_spread_zscore_with_trades("CL_NG", z_entry=1.5, z_exit=0.25)
