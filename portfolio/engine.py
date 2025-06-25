# portfolio/engine.py

from subbooks.oil import get_oil_assets
from subbooks.gas import get_gas_assets
from subbooks.grains import get_grains_assets

class PortfolioEngine:
    def __init__(self):
        self.subbooks = {
            "oil": get_oil_assets(),
            "gas": get_gas_assets(),
            "grains": get_grains_assets(),
        }
        self.active_assets = []

    def load_all_assets(self):
        """Flatten all sub-books into a single asset list."""
        self.active_assets = [
            asset for subbook_assets in self.subbooks.values()
            for asset in subbook_assets
        ]
        return self.active_assets

    def activate_subbooks(self, active_list):
        """Activate only specific sub-books (e.g., ['oil', 'grains'])"""
        self.active_assets = [
            asset for name, assets in self.subbooks.items()
            if name in active_list
            for asset in assets
        ]
        return self.active_assets

    def print_summary(self):
        print("Loaded Subbooks:")
        for name, assets in self.subbooks.items():
            print(f"  {name.capitalize()}: {assets}")
        print("\nActive Assets:", self.active_assets)
