# subbooks/gas.py

GAS_CONTRACTS = ["NG", "QG","HH"]  # Natural Gas, E-mini Gas

def get_gas_assets():
    return GAS_CONTRACTS

def gas_filters(df):
    # Placeholder for filtering logic (e.g., exclude shoulder season)
    return df
