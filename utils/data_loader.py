"""Shared data loading utilities for all modules"""

import pandas as pd
from pathlib import Path

# Get the data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "csv"

def load_dataset(filename):
    """Load a CSV dataset from the data/csv directory"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        return pd.read_csv(filepath)
    return pd.DataFrame()

def farms():
    """Load farms data"""
    return load_dataset("farms.csv")

def monthly():
    """Load monthly performance data"""
    return load_dataset("monthly_performance.csv")

def pnl():
    """Load P&L data"""
    return load_dataset("pnl.csv")

def inventory():
    """Load inventory data"""
    return load_dataset("inventory.csv")

def movement():
    """Load harvest movement data"""
    return load_dataset("harvest_movement.csv")

def forecast():
    """Load yield forecast data"""
    return load_dataset("yield_forecast.csv")

def reorder():
    """Load reorder optimizer data"""
    return load_dataset("reorder_optimizer.csv")

def supply_chain():
    """Load supply chain data"""
    return load_dataset("supply_chain.csv")

def sup_credit():
    """Load supplier credit data"""
    return load_dataset("supplier_credit.csv")

def marketing():
    """Load marketing ROI data"""
    return load_dataset("marketing_roi.csv")

def market_prices():
    """Load market prices data"""
    return load_dataset("market_prices.csv")

def buyer_sat():
    """Load buyer satisfaction data"""
    return load_dataset("buyer_satisfaction.csv")

def labour():
    """Load labour data"""
    return load_dataset("labour.csv")

def losses():
    """Load losses data"""
    return load_dataset("losses.csv")

def economic():
    """Load economic watch data"""
    return load_dataset("economic_watch.csv")

def board():
    """Load board summary data"""
    return load_dataset("board_summary.csv")

def weather():
    """Load weather data"""
    return load_dataset("weather.csv")
