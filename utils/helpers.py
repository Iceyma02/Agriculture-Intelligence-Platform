import pandas as pd
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "csv"

def load_dataset(filename):
    """Load a CSV dataset from the data/csv directory"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        return pd.read_csv(filepath)
    else:
        print(f"Warning: {filename} not found at {filepath}")
        return pd.DataFrame()

def format_currency(value):
    """Format number as currency"""
    if pd.isna(value):
        return "$0"
    return f"${value:,.2f}"

def format_percentage(value):
    """Format number as percentage"""
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"

def format_number(value):
    """Format large numbers with K/M/B suffixes"""
    if pd.isna(value):
        return "0"
    if value >= 1e9:
        return f"{value/1e9:.1f}B"
    elif value >= 1e6:
        return f"{value/1e6:.1f}M"
    elif value >= 1e3:
        return f"{value/1e3:.1f}K"
    else:
        return f"{value:.0f}"
