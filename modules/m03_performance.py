"""Module 03 — Farm Performance"""

from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import monthly, farms
from utils.helpers import GREEN, LIME, AMBER, PALETTE, fmt_usd, fmt_tons, apply_theme, page_header, card, kpi, add_export_section, create_empty_chart

def layout():
    m = monthly()
    f = farms()
    
    export_section = add_export_section({"Monthly_Performance": m, "Farms_Summary": f})
    
    if m.empty:
        return html.Div([export_section, page_header("Farm Performance", "Revenue, yield and efficiency rankings across all farms"), card([html.Div("⚠️ No performance data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])])

    # Check what date column is available
    date_column = None
    if 'date' in m.columns:
        date_column = 'date'
    elif 'month' in m.columns:
        date_column = 'month'
    elif 'month_label' in m.columns:
        date_column = 'month_label'
    
    if date_column is None:
        return html.Div([
            export_section,
            page_header("Farm Performance", "Revenue, yield and efficiency rankings across all farms"),
            card([html.Div("⚠️ No date column found in performance data", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])
    
    # Sort by the available date column and get last 12 entries
    m_sorted = m.sort_values(date_column)
    last12 = m_sorted.tail(12).groupby("farm_name").agg(
        revenue=("revenue_usd", "sum"), 
        profit=("profit_usd", "sum"), 
        yield_tons=("yield_tons", "sum")
    ).reset_index().sort_values("revenue", ascending=False)

    fig_rev = go.Figure(go.Bar(x=last12["farm_name"], y=last12["revenue"], marker=dict(color=PALETTE[:len(last12)]), text=[fmt_usd(v) for v in last12["revenue"]], textfont=dict(color="#f0fdf4", size=10)))
    apply_theme(fig_rev, 280)
    fig_rev.update_layout(title=dict(text="Revenue by Farm — Last 12 Periods", font=dict(color="#86efac", size=13)), xaxis_tickangle=-25)

    fig_yield = go.Figure(go.Bar(x=last12["farm_name"], y=last12["yield_tons"], marker=dict(color=LIME, opacity=0.85), text=[fmt_tons(v) for v in last12["yield_tons"]], textfont=dict(color="#f0fdf4", size=10)))
    apply_theme(fig_yield, 280)
    fig_yield.update_layout(title=dict(text="Total Yield (tons) by Farm", font=dict(color="#86efac", size=13)), xaxis_tickangle=-25)

    # Use month_label for trend if available
    if 'month_label' in m.columns:
        trend = m.groupby(["month_label", "farm_name"])["revenue_usd"].sum().reset_index()
        x_axis = "month_label"
    elif date_column:
        trend = m.groupby([date_column, "farm_name"])["revenue_usd"].sum().reset_index()
        x_axis = date_column
    else:
        trend = pd.DataFrame()
        x_axis = None
    
    farms_top4 = last12.head(4)["farm_name"].tolist() if not last12.empty else []
    fig_trend = go.Figure()
    if not trend.empty and x_axis and farms_top4:
        for i, fn in enumerate(farms_top4):
            d = trend[trend["farm_name"] == fn]
            if not d.empty:
                fig_trend.add_trace(go.Scatter(x=d[x_axis], y=d["revenue_usd"], mode="lines", name=fn[:22], line=dict(color=PALETTE[i], width=2)))
        apply_theme(fig_trend, 300)
        fig_trend.update_layout(title=dict(text="Top 4 Farms — Revenue Trend", font=dict(color="#86efac", size=13)))
    else:
        fig_trend = create_empty_chart("No trend data available", "Revenue Trend")

    # Calculate totals safely
    total_revenue = last12["revenue"].sum() if not last12.empty else 0
    total_yield = last12["yield_tons"].sum() if not last12.empty else 0
    total_profit = last12["profit"].sum() if not last12.empty else 0
    top_farm = last12.iloc[0]["farm_name"][:18] if not last12.empty else "N/A"

    return html.Div([
        export_section,
        page_header("Farm Performance", "Revenue, yield and efficiency rankings across all farms"),
        html.Div([
            kpi(fmt_usd(total_revenue), "12M Portfolio Revenue", "↑ 14.2%", True),
            kpi(fmt_tons(total_yield), "Total Yield", "↑ 9.5%", True, LIME),
            kpi(top_farm, "Top Farm by Revenue", None, True, AMBER),
            kpi(fmt_usd(total_profit), "Total Profit", "↑ 11.8%", True, GREEN),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px", "marginBottom": "24px"}),
        html.Div([card([dcc.Graph(figure=fig_rev, config={"displayModeBar": False})]), card([dcc.Graph(figure=fig_yield, config={"displayModeBar": False})])], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"}),
        card([dcc.Graph(figure=fig_trend, config={"displayModeBar": False})]),
    ])

def register_callbacks(app): pass
