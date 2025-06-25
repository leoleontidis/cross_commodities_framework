# subbooks/metals.py

METALS_CONTRACTS = ["GC", "SI", "HG", "MGC", "SIL"]  # Gold, Silver, Copper, Micro Gold, Micro Silver

def get_metals_assets():
    return METALS_CONTRACTS

def metals_filters(df):
    # Placeholder for filtering logic (e.g., high open interest)
    return df
