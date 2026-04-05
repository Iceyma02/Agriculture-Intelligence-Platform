"""Shared helper functions for all modules"""

import pandas as pd
import plotly.graph_objects as go
from dash import html

# ============================================================================
# COLOR DEFINITIONS
# ============================================================================

GREEN = '#22c55e'
BLUE = '#3b82f6'
AMBER = '#f59e0b'
RED = '#ef4444'
LIME = '#a3e635'
PURPLE = '#a855f7'
PINK = '#ec4899'

# Color palette for charts
PALETTE = [LIME, BLUE, AMBER, PURPLE, GREEN, PINK]

# ============================================================================
# FORMATTING FUNCTIONS
# ============================================================================

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

def fmt_percent(value):
    """Format as percentage"""
    if pd.isna(value):
        return "0%"
    return f"{value:.1f}%"

def fmt_number(value):
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

# ============================================================================
# PLOTLY THEME FUNCTIONS
# ============================================================================

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
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#86efac", size=10),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(
        gridcolor="rgba(34,197,94,0.1)", 
        zerolinecolor="rgba(34,197,94,0.2)",
        tickfont=dict(color="#6b7280")
    )
    fig.update_yaxes(
        gridcolor="rgba(34,197,94,0.1)", 
        zerolinecolor="rgba(34,197,94,0.2)",
        tickfont=dict(color="#6b7280")
    )
    return fig

def create_empty_chart(message="No data available", title="Data Not Available"):
    """Create an empty chart with a message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(color="#86efac", size=14)
    )
    apply_theme(fig, 300)
    fig.update_layout(
        title=dict(text=title, font=dict(color="#86efac", size=13)),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )
    return fig

# ============================================================================
# DASH COMPONENT FUNCTIONS
# ============================================================================

def page_header(title, subtitle):
    """Create page header"""
    return html.Div([
        html.H1(title, className="page-title"),
        html.P(subtitle, className="page-subtitle"),
    ], className="page-header")

def card(children, style=None):
    """Create a card component"""
    card_style = {
        "background": "#111811", 
        "border": "1px solid rgba(34,197,94,0.15)", 
        "borderRadius": "12px", 
        "padding": "20px",
        "transition": "all 0.3s ease"
    }
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
    status_map = {
        "Active": ("● Active", "badge-ok"),
        "OK": ("● OK", "badge-ok"),
        "On time": ("● On time", "badge-ok"),
        "Delivered": ("● Delivered", "badge-ok"),
        "Warning": ("⚠ Warning", "badge-low"),
        "Low": ("⚠ Low", "badge-low"),
        "Delayed": ("⚠ Delayed", "badge-low"),
        "In Transit": ("⚠ In Transit", "badge-low"),
        "Suspended": ("● Suspended", "badge-critical"),
        "Critical": ("● Critical", "badge-critical"),
        "Pending": ("● Pending", "badge-critical"),
    }
    
    if status in status_map:
        text, class_name = status_map[status]
        return html.Span(text, className=class_name)
    else:
        return html.Span(status, style={"color": "#6b7280", "fontSize": "0.72rem"})

# ============================================================================
# COLOR UTILITIES
# ============================================================================

def hex_to_rgba(hex_color, opacity=0.1):
    """Convert hex color to rgba with opacity"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {opacity})"

def get_color_gradient(value, min_val=0, max_val=100):
    """Get color based on value (green to red gradient)"""
    if value <= min_val:
        return GREEN
    elif value >= max_val:
        return RED
    else:
        # Interpolate between green and red
        ratio = (value - min_val) / (max_val - min_val)
        r = int(34 + (239 - 34) * ratio)  # 34->239
        g = int(197 + (68 - 197) * ratio)  # 197->68
        b = int(94 + (68 - 94) * ratio)    # 94->68
        return f"rgb({r}, {g}, {b})"

# ============================================================================
# DATA VALIDATION FUNCTIONS
# ============================================================================

def validate_dataframe(df, required_columns, df_name="DataFrame"):
    """Validate that a DataFrame has required columns"""
    if df.empty:
        return False, f"{df_name} is empty"
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"{df_name} missing columns: {missing_cols}"
    
    return True, "Valid"
    def create_export_button(data, filename="export", button_text="📥 Export to CSV"):
    """Create a working export button"""
    import base64
    import io
    
    if data is None or data.empty:
        return html.Div("No data to export", style={"color": "#6b7280"})
    
    # Convert dataframe to CSV
    csv_buffer = io.StringIO()
    data.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()
    csv_base64 = base64.b64encode(csv_string.encode()).decode()
    
    return html.Div([
        html.A(
            button_text,
            href=f"data:text/csv;base64,{csv_base64}",
            download=f"{filename}.csv",
            style={
                "backgroundColor": "#22c55e",
                "color": "#0a0f0a",
                "border": "none",
                "padding": "8px 16px",
                "borderRadius": "6px",
                "cursor": "pointer",
                "fontWeight": "600",
                "fontSize": "0.8rem",
                "textDecoration": "none",
                "display": "inline-block"
            }
        )
    ])

def safe_merge(df1, df2, on, how='left'):
    """Safely merge two dataframes with type conversion"""
    try:
        # Convert join keys to string to avoid type mismatches
        if on in df1.columns:
            df1[on] = df1[on].astype(str)
        if on in df2.columns:
            df2[on] = df2[on].astype(str)
        
        return df1.merge(df2, on=on, how=how)
    except Exception as e:
        print(f"Error merging dataframes: {e}")
        return pd.DataFrame()
