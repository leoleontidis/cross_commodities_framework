# subbooks/grains.py

GRAINS_CONTRACTS = ["ZC", "ZW", "ZS"]  # Corn, Wheat, Soybeans

def get_grains_assets():
    return GRAINS_CONTRACTS

def grains_filters(df):
    # Placeholder for filtering logic (e.g., only front month)
    return df
