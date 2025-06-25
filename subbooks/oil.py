# subbooks/oil.py

OIL_CONTRACTS = ["CL", "QM", "HO", "RB", "BZ"]  # Crude, E-mini Crude, Micro Crude, Heating Oil, Gasoline

def get_oil_assets():
    return OIL_CONTRACTS

def oil_filters(df):
    # Placeholder for filtering logic (e.g., front-month, volume filter)
    return df
