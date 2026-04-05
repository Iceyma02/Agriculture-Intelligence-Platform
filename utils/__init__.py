"""Utils package - Data loading and helper functions"""

# Import all from data_loader
from .data_loader import (
    DATA_DIR,
    load_dataset,
    load_all_datasets,
    get_cached_dataset,
    clear_cache,
    farms,
    monthly,
    pnl,
    inventory,
    movement,
    forecast,
    reorder,
    supply_chain,
    sup_credit,
    marketing,
    market_prices,
    buyer_sat,
    labour,
    losses,
    economic,
    board,
    weather,
)

# Import all from helpers
from .helpers import (
    # Colors
    GREEN,
    BLUE,
    AMBER,
    RED,
    LIME,
    PURPLE,
    PINK,
    PALETTE,
    # Formatting
    fmt_usd,
    fmt_tons,
    fmt_percent,
    fmt_number,
    # Plotly
    apply_theme,
    create_empty_chart,
    # Dash components
    page_header,
    card,
    kpi,
    status_badge,
    # Color utilities
    hex_to_rgba,
    get_color_gradient,
    # Data validation
    validate_dataframe,
    safe_merge,
)

# Define what gets exported with "from utils import *"
__all__ = [
    # Data loaders
    'DATA_DIR',
    'load_dataset',
    'load_all_datasets',
    'get_cached_dataset',
    'clear_cache',
    'farms',
    'monthly',
    'pnl',
    'inventory',
    'movement',
    'forecast',
    'reorder',
    'supply_chain',
    'sup_credit',
    'marketing',
    'market_prices',
    'buyer_sat',
    'labour',
    'losses',
    'economic',
    'board',
    'weather',
    # Colors
    'GREEN',
    'BLUE',
    'AMBER',
    'RED',
    'LIME',
    'PURPLE',
    'PINK',
    'PALETTE',
    # Formatting
    'fmt_usd',
    'fmt_tons',
    'fmt_percent',
    'fmt_number',
    # Plotly
    'apply_theme',
    'create_empty_chart',
    # Dash components
    'page_header',
    'card',
    'kpi',
    'status_badge',
    # Color utilities
    'hex_to_rgba',
    'get_color_gradient',
    # Data validation
    'validate_dataframe',
    'safe_merge',
]
