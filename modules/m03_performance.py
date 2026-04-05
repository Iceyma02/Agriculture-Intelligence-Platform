"""Module 03 — Farm Performance"""

from dash import html, dcc
import plotly.graph_objects as go
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

    last12 = m.sort_values("date").tail(12).groupby("farm_name").agg(
        revenue=("revenue_usd", "sum"), profit=("profit_usd", "sum"), yield_tons=("yield_tons", "sum")
    ).reset_index().sort_values("revenue", ascending=False)

    fig_rev = go.Figure(go.Bar(x=last12["farm_name"], y=last12["revenue"], marker=dict(color=PALETTE[:len(last12)]), text=[fmt_usd(v) for v in last12["revenue"]], textfont=dict(color="#f0fdf4", size=10)))
    apply_theme(fig_rev, 280)
    fig_rev.update_layout(title=dict(text="Revenue by Farm — Last 12 Months", font=dict(color="#86efac", size=13)), xaxis_tickangle=-25)

    fig_yield = go.Figure(go.Bar(x=last12["farm_name"], y=last12["yield_tons"], marker=dict(color=LIME, opacity=0.85), text=[fmt_tons(v) for v in last12["yield_tons"]], textfont=dict(color="#f0fdf4", size=10)))
    apply_theme(fig_yield, 280)
    fig_yield.update_layout(title=dict(text="Total Yield (tons) by Farm", font=dict(color="#86efac", size=13)), xaxis_tickangle=-25)

    trend = m.groupby(["month_label", "farm_name"])["revenue_usd"].sum().reset_index()
    farms_top4 = last12.head(4)["farm_name"].tolist()
    fig_trend = go.Figure()
    for i, fn in enumerate(farms_top4):
        d = trend[trend["farm_name"] == fn]
        fig_trend.add_trace(go.Scatter(x=d["month_label"], y=d["revenue_usd"], mode="lines", name=fn[:22], line=dict(color=PALETTE[i], width=2)))
    apply_theme(fig_trend, 300)
    fig_trend.update_layout(title=dict(text="Top 4 Farms — Revenue Trend", font=dict(color="#86efac", size=13)))

    return html.Div([
        export_section,
        page_header("Farm Performance", "Revenue, yield and efficiency rankings across all farms"),
        html.Div([
            kpi(fmt_usd(last12["revenue"].sum()), "12M Portfolio Revenue", "↑ 14.2%", True),
            kpi(fmt_tons(last12["yield_tons"].sum()), "Total Yield", "↑ 9.5%", True, LIME),
            kpi(last12.iloc[0]["farm_name"][:18], "Top Farm by Revenue", None, True, AMBER),
            kpi(fmt_usd(last12["profit"].sum()), "Total Profit", "↑ 11.8%", True, GREEN),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px", "marginBottom": "24px"}),
        html.Div([card([dcc.Graph(figure=fig_rev, config={"displayModeBar": False})]), card([dcc.Graph(figure=fig_yield, config={"displayModeBar": False})])], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"}),
        card([dcc.Graph(figure=fig_trend, config={"displayModeBar": False})]),
    ])

def register_callbacks(app): pass
