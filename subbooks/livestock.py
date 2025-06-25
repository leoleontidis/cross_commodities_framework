# subbooks/livestock.py

LIVESTOCK_CONTRACTS = ["LE", "HE", "GF"]  # Live Cattle, Lean Hogs, Feeder Cattle

def get_livestock_assets():
    return LIVESTOCK_CONTRACTS

def livestock_filters(df):
    # Placeholder for filtering logic (e.g., avoid summer contracts)
    return df
