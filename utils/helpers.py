"""Enhanced helper functions for loading states, exports, and refresh"""

import pandas as pd
import json
from datetime import datetime
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_loading_spinner():
    """Create a loading spinner component"""
    return html.Div([
        dcc.Loading(
            id="loading-spinner",
            type="circle",
            color="#22c55e",
            children=html.Div(id="loading-output"),
            style={"position": "fixed", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)", "zIndex": 9999}
        )
    ])

def create_date_range_picker(id="date-range-picker"):
    """Create a date range picker component"""
    return html.Div([
        html.Label("Date Range:", style={"color": "#86efac", "fontSize": "0.8rem", "marginBottom": "5px"}),
        dcc.DatePickerRange(
            id=id,
            min_date_allowed=datetime(2023, 1, 1),
            max_date_allowed=datetime.now(),
            initial_visible_month=datetime.now(),
            start_date=datetime(2024, 1, 1),
            end_date=datetime.now(),
            display_format="YYYY-MM-DD",
            style={"backgroundColor": "#111811", "color": "#f0fdf4"},
            className="date-picker"
        )
    ], style={"marginBottom": "15px"})

def create_season_filter(id="season-dropdown", data=None):
    """Create a season filter dropdown"""
    if data is not None and 'season' in data.columns:
        seasons = sorted(data['season'].unique())
    else:
        seasons = ["2024 Summer", "2024 Winter", "2025 Summer", "2025 Winter"]
    
    return html.Div([
        html.Label("Season:", style={"color": "#86efac", "fontSize": "0.8rem", "marginBottom": "5px"}),
        dcc.Dropdown(
            id=id,
            options=[{"label": s, "value": s} for s in seasons],
            value=seasons[-1] if seasons else None,
            style={"backgroundColor": "#111811", "color": "#f0fdf4"},
            className="season-dropdown"
        )
    ], style={"marginBottom": "15px"})

def create_export_button(data, filename="export", button_text="📥 Export Data"):
    """Create an export button that downloads data as CSV"""
    return html.Div([
        html.Button(
            button_text,
            id={"type": "export-button", "index": filename},
            className="export-btn",
            style={
                "backgroundColor": "#22c55e",
                "color": "#0a0f0a",
                "border": "none",
                "padding": "8px 16px",
                "borderRadius": "6px",
                "cursor": "pointer",
                "fontWeight": "600",
                "fontSize": "0.8rem",
                "marginBottom": "10px"
            }
        ),
        dcc.Download(id={"type": "download", "index": filename})
    ])

def create_refresh_button():
    """Create a refresh button for real-time updates"""
    return html.Div([
        html.Button(
            "🔄 Refresh Data",
            id="refresh-button",
            style={
                "backgroundColor": "#3b82f6",
                "color": "#f0fdf4",
                "border": "none",
                "padding": "8px 16px",
                "borderRadius": "6px",
                "cursor": "pointer",
                "fontWeight": "600",
                "fontSize": "0.8rem"
            }
        ),
        dcc.Interval(
            id="refresh-interval",
            interval=300000,  # 5 minutes in milliseconds
            n_intervals=0
        )
    ])

def create_search_bar(id="search-input", placeholder="Search farms..."):
    """Create a search bar for filtering tables"""
    return html.Div([
        html.I(className="fas fa-search", style={"color": "#6b7280", "position": "absolute", "left": "12px", "top": "50%", "transform": "translateY(-50%)"}),
        dcc.Input(
            id=id,
            type="text",
            placeholder=placeholder,
            style={
                "width": "100%",
                "padding": "10px 10px 10px 35px",
                "backgroundColor": "#111811",
                "border": "1px solid rgba(34,197,94,0.15)",
                "borderRadius": "8px",
                "color": "#f0fdf4",
                "fontSize": "0.85rem"
            }
        )
    ], style={"position": "relative", "marginBottom": "15px"})

def create_compare_selector(farms_list):
    """Create a multi-select dropdown for farm comparison"""
    return html.Div([
        html.Label("Compare Farms:", style={"color": "#86efac", "fontSize": "0.8rem", "marginBottom": "5px"}),
        dcc.Dropdown(
            id="compare-farms",
            options=[{"label": farm, "value": farm} for farm in farms_list],
            multi=True,
            placeholder="Select up to 4 farms to compare",
            max=4,
            style={"backgroundColor": "#111811", "color": "#f0fdf4"}
        )
    ], style={"marginBottom": "15px"})
