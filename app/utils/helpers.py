"""Shared helper functions for all modules"""

import pandas as pd
import plotly.graph_objects as go
from dash import html

# Color definitions
GREEN = '#22c55e'
BLUE = '#3b82f6'
AMBER = '#f59e0b'
RED = '#ef4444'
LIME = '#a3e635'
PURPLE = '#a855f7'
PINK = '#ec4899'
PALETTE = [LIME, BLUE, AMBER, PURPLE, GREEN, PINK]

def fmt_usd(value):
    """Format number as USD currency"""
    if pd.isna(value):
        return "$0"
    return f"${value:,.0f}"

def fmt_tons(value):
    """Format tons with units"""
    if pd.isna(value):
        return "0 t"
    return f"{value:,.0f} t"

def apply_theme(fig, height=300):
    """Apply dark theme to plotly figures"""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#86efac", size=11),
        height=height,
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    fig.update_xaxes(gridcolor="rgba(34,197,94,0.1)", zerolinecolor="rgba(34,197,94,0.2)")
    fig.update_yaxes(gridcolor="rgba(34,197,94,0.1)", zerolinecolor="rgba(34,197,94,0.2)")
    return fig

def page_header(title, subtitle):
    """Create page header"""
    return html.Div([
        html.H1(title, className="page-title"),
        html.P(subtitle, className="page-subtitle"),
    ], className="page-header")

def card(children, style=None):
    """Create a card component"""
    card_style = {"background": "#111811", "border": "1px solid rgba(34,197,94,0.15)", 
                  "borderRadius": "12px", "padding": "20px"}
    if style:
        card_style.update(style)
    return html.Div(children, style=card_style)

def kpi(value, label, delta=None, is_up=None, color=None):
    """Create a KPI card"""
    delta_style = {"color": GREEN if is_up else RED} if delta else {}
    return html.Div([
        html.Div(value, className="kpi-value", style={"color": color} if color else {}),
        html.Div(label, className="kpi-label"),
        html.Div(delta, className="kpi-delta", style=delta_style) if delta else None,
    ], className="kpi-card")

def status_badge(status):
    """Create a status badge HTML component"""
    if status == "Active" or status == "OK" or status == "On time" or status == "Delivered":
        return html.Span("● " + status, className="badge-ok")
    elif status == "Warning" or status == "Low" or status == "Delayed" or status == "In Transit":
        return html.Span("⚠ " + status, className="badge-low")
    elif status == "Suspended" or status == "Critical" or status == "Pending":
        return html.Span("● " + status, className="badge-critical")
    else:
        return html.Span(status, style={"color": "#6b7280", "fontSize": "0.72rem"})
