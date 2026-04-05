"""Shared data loading utilities for all modules"""

import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the data directory - handles both local and container paths
def get_data_dir():
    """Get the correct data directory path"""
    # Try multiple possible paths
    possible_paths = [
        Path(__file__).parent.parent / "data" / "csv",  # /app/utils/../data/csv
        Path.cwd() / "data" / "csv",                     # /app/data/csv
        Path("/app/data/csv"),                           # Absolute path in container
    ]
    
    for path in possible_paths:
        if path.exists():
            logger.info(f"Found data directory: {path}")
            return path
    
    logger.warning(f"No data directory found. Tried: {possible_paths}")
    return possible_paths[0]  # Return the first path as default

DATA_DIR = get_data_dir()

def load_dataset(filename, required=True):
    """
    Load a CSV dataset from the data/csv directory
    
    Args:
        filename: Name of the CSV file
        required: If True, log error when file not found
    
    Returns:
        DataFrame with data or empty DataFrame if not found
    """
    filepath = DATA_DIR / filename
    
    if filepath.exists():
        try:
            df = pd.read_csv(filepath)
            logger.debug(f"Loaded {filename}: {len(df)} rows, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            return pd.DataFrame()
    else:
        if required:
            logger.warning(f"File not found: {filepath}")
        return pd.DataFrame()

def load_all_datasets():
    """Load all datasets at once for debugging"""
    datasets = {
        'farms': load_dataset("farms.csv"),
        'monthly': load_dataset("monthly_performance.csv"),
        'pnl': load_dataset("pnl.csv"),
        'inventory': load_dataset("inventory.csv"),
        'harvest_movement': load_dataset("harvest_movement.csv"),
        'yield_forecast': load_dataset("yield_forecast.csv"),
        'reorder_optimizer': load_dataset("reorder_optimizer.csv"),
        'supply_chain': load_dataset("supply_chain.csv"),
        'supplier_credit': load_dataset("supplier_credit.csv"),
        'marketing_roi': load_dataset("marketing_roi.csv"),
        'market_prices': load_dataset("market_prices.csv"),
        'buyer_satisfaction': load_dataset("buyer_satisfaction.csv"),
        'labour': load_dataset("labour.csv"),
        'losses': load_dataset("losses.csv"),
        'economic_watch': load_dataset("economic_watch.csv"),
        'board_summary': load_dataset("board_summary.csv"),
        'weather': load_dataset("weather.csv"),
    }
    
    # Log summary
    for name, df in datasets.items():
        logger.info(f"{name}: {len(df)} rows")
    
    return datasets

# ============================================================================
# INDIVIDUAL DATASET LOADERS
# ============================================================================

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

# ============================================================================
# CACHED LOADERS (for performance)
# ============================================================================

_cache = {}

def get_cached_dataset(filename, force_reload=False):
    """Get cached dataset to avoid repeated file reads"""
    if force_reload or filename not in _cache:
        _cache[filename] = load_dataset(filename)
    return _cache[filename].copy() if not _cache[filename].empty else _cache[filename]

def clear_cache():
    """Clear all cached datasets"""
    _cache.clear()
    logger.info("Cache cleared")
