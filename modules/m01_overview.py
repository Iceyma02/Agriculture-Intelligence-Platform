"""Module 01 — Farm Operations Dashboard (CEO/National Overview)"""

from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Color definitions
GREEN = '#22c55e'
BLUE = '#3b82f6'
AMBER = '#f59e0b'
RED = '#ef4444'
LIME = '#a3e635'
PURPLE = '#a855f7'
PINK = '#ec4899'
PALETTE = [LIME, BLUE, AMBER, PURPLE, GREEN, PINK]

# Helper functions
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
    if status in ["Active", "OK", "On time", "Delivered"]:
        return html.Span("● " + status, className="badge-ok")
    elif status in ["Warning", "Low", "Delayed", "In Transit"]:
        return html.Span("⚠ " + status, className="badge-low")
    elif status in ["Suspended", "Critical", "Pending"]:
        return html.Span("● " + status, className="badge-critical")
    else:
        return html.Span(status, style={"color": "#6b7280", "fontSize": "0.72rem"})

def load_farms():
    """Load farms data"""
    data_dir = Path(__file__).parent.parent / "data" / "csv"
    farms_path = data_dir / "farms.csv"
    if farms_path.exists():
        df = pd.read_csv(farms_path)
        # Standardize column names
        if 'id' in df.columns and 'farm_id' not in df.columns:
            df = df.rename(columns={'id': 'farm_id'})
        return df
    return pd.DataFrame()

def load_monthly():
    """Load monthly performance data"""
    data_dir = Path(__file__).parent.parent / "data" / "csv"
    monthly_path = data_dir / "monthly_performance.csv"
    if monthly_path.exists():
        return pd.read_csv(monthly_path)
    return pd.DataFrame()

def load_pnl():
    """Load P&L data"""
    data_dir = Path(__file__).parent.parent / "data" / "csv"
    pnl_path = data_dir / "pnl.csv"
    if pnl_path.exists():
        df = pd.read_csv(pnl_path)
        # Standardize column names
        if 'farm_name' not in df.columns and 'Farm' in df.columns:
            df = df.rename(columns={'Farm': 'farm_name'})
        return df
    return pd.DataFrame()

def layout():
    f = load_farms()
    m = load_monthly()
    p = load_pnl()
    
    # Debug print to see actual columns (will appear in logs)
    print(f"Farms columns: {f.columns.tolist() if not f.empty else 'EMPTY'}")
    print(f"PNL columns: {p.columns.tolist() if not p.empty else 'EMPTY'}")
    print(f"Farms shape: {f.shape}")
    print(f"PNL shape: {p.shape}")
    
    # Handle empty dataframes
    if f.empty or p.empty:
        return html.Div([
            page_header("Farm Operations Dashboard", "National portfolio overview · All farms · All seasons"),
            card([html.Div("⚠️ Data not available. Please ensure datasets are generated.", 
                           style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])
    
    total_revenue = p["revenue_usd"].sum() if "revenue_usd" in p else 0
    total_profit = p["gross_profit_usd"].sum() if "gross_profit_usd" in p else 0
    avg_margin = p["profit_margin_pct"].mean() if "profit_margin_pct" in p else 0
    total_ha = f["size_ha"].sum() if "size_ha" in f else 0
    
    # Handle different column names for status
    status_col = "status" if "status" in f.columns else "Status" if "Status" in f.columns else None
    active_farms = len(f[f[status_col] == "Active"]) if status_col and not f.empty else 0
    critical_alerts = 4

    # Revenue trend (last 18 months, all farms)
    if not m.empty and "month_label" in m and "revenue_usd" in m:
        trend = m.groupby("month_label")["revenue_usd"].sum().reset_index()
        trend = trend.tail(18)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend["month_label"], y=trend["revenue_usd"],
            mode="lines", fill="tozeroy",
            line=dict(color=GREEN, width=2.5),
            fillcolor="rgba(34,197,94,0.08)",
            name="Revenue"
        ))
        apply_theme(fig_trend, 260)
        fig_trend.update_layout(title=dict(text="Portfolio Revenue Trend (18 months)", font=dict(color="#86efac", size=13)))
    else:
        fig_trend = create_empty_chart("No revenue trend data available", "Portfolio Revenue Trend (18 months)")

    # Farm profit rankings
    if not p.empty and "gross_profit_usd" in p:
        # Try to use farm_name or index if available
        if "farm_name" in p.columns:
            farm_profit = p.groupby("farm_name")["gross_profit_usd"].sum().reset_index().sort_values("gross_profit_usd", ascending=True)
            y_values = farm_profit["farm_name"]
        else:
            # Use index as farm identifier
            farm_profit = p.groupby(p.index)["gross_profit_usd"].sum().reset_index().sort_values("gross_profit_usd", ascending=True)
            y_values = [f"Farm {i+1}" for i in range(len(farm_profit))]
        
        fig_ranking = go.Figure(go.Bar(
            x=farm_profit["gross_profit_usd"],
            y=y_values,
            orientation="h",
            marker=dict(
                color=farm_profit["gross_profit_usd"],
                colorscale=[[0, "#1a2e1a"], [0.5, "#16a34a"], [1, "#22c55e"]],
            ),
            text=[fmt_usd(v) for v in farm_profit["gross_profit_usd"]],
            textfont=dict(color="#f0fdf4", size=11),
        ))
        apply_theme(fig_ranking, 340)
        fig_ranking.update_layout(title=dict(text="Profit Ranking by Farm", font=dict(color="#86efac", size=13)))
    else:
        fig_ranking = create_empty_chart("No profit data available", "Profit Ranking by Farm")

    # Crop mix - IMPROVED VERSION
    try:
        if not p.empty and not f.empty:
            # Find the correct ID column names
            p_id_col = None
            f_id_col = None
            
            # Check for ID columns in PNL
            for col in ['farm_id', 'Farm_ID', 'farmid', 'FarmId', 'id', 'ID']:
                if col in p.columns:
                    p_id_col = col
                    break
            
            # Check for ID columns in FARMS
            for col in ['farm_id', 'Farm_ID', 'farmid', 'FarmId', 'id', 'ID']:
                if col in f.columns:
                    f_id_col = col
                    break
            
            # Check for crop column in FARMS
            crop_col = None
            for col in ['primary_crop', 'crop', 'Crop', 'PrimaryCrop']:
                if col in f.columns:
                    crop_col = col
                    break
            
            if p_id_col and f_id_col and crop_col:
                # Convert to string for merging
                p[p_id_col] = p[p_id_col].astype(str)
                f[f_id_col] = f[f_id_col].astype(str)
                
                # Merge the data
                crop_rev = p.merge(f[[f_id_col, crop_col]], left_on=p_id_col, right_on=f_id_col, how='left')
                
                if crop_col in crop_rev.columns and 'revenue_usd' in crop_rev.columns:
                    crop_mix = crop_rev.groupby(crop_col)['revenue_usd'].sum().reset_index().sort_values('revenue_usd', ascending=False)
                    crop_mix = crop_mix[crop_mix[crop_col].notna()]  # Remove null crops
                    
                    if not crop_mix.empty and crop_mix['revenue_usd'].sum() > 0:
                        fig_crop = go.Figure(go.Bar(
                            x=crop_mix[crop_col], 
                            y=crop_mix['revenue_usd'],
                            marker=dict(color=PALETTE[:len(crop_mix)]),
                            text=[fmt_usd(v) for v in crop_mix['revenue_usd']],
                            textposition='outside',
                            textfont=dict(color="#f0fdf4", size=10),
                        ))
                        apply_theme(fig_crop, 300)
                        fig_crop.update_layout(
                            title=dict(text="Revenue by Primary Crop", font=dict(color="#86efac", size=13)),
                            xaxis_tickangle=-25,
                            yaxis=dict(title="Revenue (USD)", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)")
                        )
                    else:
                        fig_crop = create_empty_chart("No crop revenue data available", "Revenue by Primary Crop")
                else:
                    fig_crop = create_empty_chart("Required columns missing", "Revenue by Primary Crop")
            else:
                missing = []
                if not p_id_col: missing.append("farm_id in PNL")
                if not f_id_col: missing.append("farm_id in FARMS") 
                if not crop_col: missing.append("crop column in FARMS")
                fig_crop = create_empty_chart(f"Missing: {', '.join(missing)}", "Revenue by Primary Crop")
        else:
            fig_crop = create_empty_chart("No P&L or farm data available", "Revenue by Primary Crop")
    except Exception as e:
        print(f"Error creating crop chart: {e}")
        fig_crop = create_empty_chart(f"Error: {str(e)[:50]}", "Revenue by Primary Crop")

    # Province performance
    if not f.empty and "province" in f.columns and "profit_margin_pct" in f.columns:
        prov = f.groupby("province").agg(
            avg_margin=("profit_margin_pct", "mean")
        ).reset_index()
        fig_prov = go.Figure(go.Bar(
            x=prov["province"], y=prov["avg_margin"],
            marker=dict(color=AMBER, opacity=0.85),
            text=[f"{v:.1f}%" for v in prov["avg_margin"]],
            textfont=dict(color="#f0fdf4"),
        ))
        apply_theme(fig_prov, 260)
        fig_prov.update_layout(title=dict(text="Avg Profit Margin by Province", font=dict(color="#86efac", size=13)))
    else:
        fig_prov = create_empty_chart("No province data available", "Avg Profit Margin by Province")

    alerts = [
        ("🔴", "Mvurwi Mixed Farm", "Fertilizer stock at critical level — reorder required"),
        ("🟡", "Headlands Cotton Block", "Pest pressure HIGH — intervention recommended"),
        ("🔴", "Bindura Soya Farm", "Supplier Windmill Zimbabwe suspended — overdue $14,200"),
        ("🟡", "Karoi Maize Cooperative", "Post-harvest loss above threshold — review storage"),
    ]

    return html.Div([
        page_header("Farm Operations Dashboard", "National portfolio overview · All farms · All seasons"),

        # KPIs
        html.Div([
            kpi(fmt_usd(total_revenue), "Total Portfolio Revenue", "↑ 12.4% vs last year", True),
            kpi(fmt_usd(total_profit), "Total Gross Profit", "↑ 8.1% vs last year", True, LIME),
            kpi(f"{avg_margin:.1f}%", "Avg Profit Margin", "↑ 1.2pp vs last season", True, AMBER),
            kpi(f"{total_ha:,.0f} ha", "Hectares Under Cultivation", None),
            kpi(f"{active_farms}/{len(f)}", "Active Farms", None, True, BLUE),
            kpi(str(critical_alerts), "Critical Alerts", "Requires attention", False, RED),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(6,1fr)", "gap": "14px", "marginBottom": "24px"}),

        # Trend + Crop
        html.Div([
            card([dcc.Graph(figure=fig_trend, config={"displayModeBar": False})], {"flex": "2"}),
            card([dcc.Graph(figure=fig_crop, config={"displayModeBar": False})], {"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        # Rankings + Province
        html.Div([
            card([dcc.Graph(figure=fig_ranking, config={"displayModeBar": False})], {"flex": "1.4"}),
            card([dcc.Graph(figure=fig_prov, config={"displayModeBar": False})], {"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        # Alerts
        card([
            html.Div("⚠️  Live Alerts", style={"color": RED, "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
            *[html.Div([
                html.Span(icon, style={"marginRight": "8px"}),
                html.Span(farm + " — ", style={"color": "#f0fdf4", "fontWeight": "500", "fontSize": "0.83rem"}),
                html.Span(msg, style={"color": "#6b7280", "fontSize": "0.82rem"}),
            ], style={"padding": "10px 0", "borderBottom": "1px solid rgba(34,197,94,0.08)"})
              for icon, farm, msg in alerts]
        ]),
    ])

def register_callbacks(app):
    pass
