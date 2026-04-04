"""Module 01 — Farm Operations Dashboard (CEO/National Overview)"""

from dash import html, dcc, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    f = farms()
    m = monthly()
    p = pnl()

    total_revenue = p["revenue_usd"].sum()
    total_profit = p["gross_profit_usd"].sum()
    avg_margin = p["profit_margin_pct"].mean()
    total_ha = f["size_ha"].sum()
    active_farms = len(f[f["status"] == "Active"])
    critical_alerts = 4

    # Revenue trend (last 18 months, all farms)
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

    # Farm profit rankings
    farm_profit = p.groupby("farm_name")["gross_profit_usd"].sum().reset_index().sort_values("gross_profit_usd", ascending=True)
    fig_ranking = go.Figure(go.Bar(
        x=farm_profit["gross_profit_usd"],
        y=farm_profit["farm_name"],
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

    # Crop mix donut
    crop_rev = p.merge(farms()[["farm_id", "primary_crop"]], on="farm_id", how="left")
    crop_mix = crop_rev.groupby("primary_crop")["revenue_usd"].sum().reset_index()
    fig_donut = go.Figure(go.Pie(
        labels=crop_mix["primary_crop"], values=crop_mix["revenue_usd"],
        hole=0.6, marker=dict(colors=PALETTE),
        textinfo="label+percent", textfont=dict(color="#f0fdf4", size=11),
    ))
    apply_theme(fig_donut, 300)
    fig_donut.update_layout(title=dict(text="Revenue by Primary Crop", font=dict(color="#86efac", size=13)),
                             showlegend=False)

    # Province performance
    prov = f.groupby("province").agg(farms_count=("id","count"), total_ha=("size_ha","sum"),
                                      avg_margin=("profit_margin_pct","mean")).reset_index()
    fig_prov = go.Figure(go.Bar(
        x=prov["province"], y=prov["avg_margin"],
        marker=dict(color=AMBER, opacity=0.85),
        text=[f"{v:.1f}%" for v in prov["avg_margin"]],
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_prov, 260)
    fig_prov.update_layout(title=dict(text="Avg Profit Margin by Province", font=dict(color="#86efac", size=13)))

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
            kpi(f"{total_ha:,} ha", "Hectares Under Cultivation", None),
            kpi(f"{active_farms}/{len(f)}", "Active Farms", None, True, BLUE),
            kpi(str(critical_alerts), "Critical Alerts", "Requires attention", False, RED),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(6,1fr)", "gap": "14px", "marginBottom": "24px"}),

        # Trend + Donut
        html.Div([
            card([dcc.Graph(figure=fig_trend, config={"displayModeBar": False})], {"flex": "2"}),
            card([dcc.Graph(figure=fig_donut, config={"displayModeBar": False})], {"flex": "1"}),
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
