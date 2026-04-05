"""Module 01 — Farm Operations Dashboard (CEO/National Overview)"""

from dash import html, dcc
import plotly.graph_objects as go
import pandas as pd
import sys, os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import farms, monthly, pnl
from utils.helpers import (
    GREEN, BLUE, AMBER, RED, LIME, PALETTE, 
    fmt_usd, fmt_tons, apply_theme, page_header, card, kpi, 
    add_export_section, create_empty_chart
)

def load_farms():
    return farms()

def load_monthly():
    return monthly()

def load_pnl():
    return pnl()

def layout():
    f = load_farms()
    m = load_monthly()
    p = load_pnl()
    
    if f.empty or p.empty:
        return html.Div([
            page_header("Farm Operations Dashboard", "National portfolio overview · All farms · All seasons"),
            card([html.Div("⚠️ Data not available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])
    
    # Export section
    export_section = add_export_section({
        "Farms_Data": f,
        "PNL_Data": p,
        "Monthly_Performance": m
    })
    
    total_revenue = p["revenue_usd"].sum() if "revenue_usd" in p else 0
    total_profit = p["gross_profit_usd"].sum() if "gross_profit_usd" in p else 0
    avg_margin = p["profit_margin_pct"].mean() if "profit_margin_pct" in p else 0
    total_ha = f["size_ha"].sum() if "size_ha" in f else 0
    active_farms = len(f[f["status"] == "Active"]) if "status" in f else 0
    critical_alerts = 4

    # Revenue trend
    if not m.empty and "month_label" in m and "revenue_usd" in m:
        trend = m.groupby("month_label")["revenue_usd"].sum().reset_index().tail(18)
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
        fig_trend = create_empty_chart("No revenue trend data", "Portfolio Revenue Trend")

    # Farm profit rankings
    if not p.empty and "gross_profit_usd" in p and "farm_name" in p:
        farm_profit = p.groupby("farm_name")["gross_profit_usd"].sum().reset_index().sort_values("gross_profit_usd", ascending=True)
        fig_ranking = go.Figure(go.Bar(
            x=farm_profit["gross_profit_usd"], y=farm_profit["farm_name"],
            orientation="h",
            marker=dict(color=farm_profit["gross_profit_usd"], colorscale=[[0, "#1a2e1a"], [0.5, "#16a34a"], [1, "#22c55e"]]),
            text=[fmt_usd(v) for v in farm_profit["gross_profit_usd"]],
            textfont=dict(color="#f0fdf4", size=11),
        ))
        apply_theme(fig_ranking, 340)
        fig_ranking.update_layout(title=dict(text="Profit Ranking by Farm", font=dict(color="#86efac", size=13)))
    else:
        fig_ranking = create_empty_chart("No profit data", "Profit Ranking by Farm")

    # Crop mix
    try:
        if not p.empty and not f.empty and 'farm_id' in p.columns and 'farm_id' in f.columns and 'primary_crop' in f.columns:
            p['farm_id'] = p['farm_id'].astype(str)
            f['farm_id'] = f['farm_id'].astype(str)
            crop_rev = p.merge(f[['farm_id', 'primary_crop']], on='farm_id', how='left')
            crop_mix = crop_rev.groupby('primary_crop')['revenue_usd'].sum().reset_index().sort_values('revenue_usd', ascending=False)
            
            if not crop_mix.empty and crop_mix['revenue_usd'].sum() > 0:
                fig_crop = go.Figure(go.Bar(
                    x=crop_mix['primary_crop'], y=crop_mix['revenue_usd'],
                    marker=dict(color=PALETTE[:len(crop_mix)]),
                    text=[fmt_usd(v) for v in crop_mix['revenue_usd']],
                    textposition='outside',
                    textfont=dict(color="#f0fdf4", size=10),
                ))
                apply_theme(fig_crop, 300)
                fig_crop.update_layout(
                    title=dict(text="Revenue by Primary Crop", font=dict(color="#86efac", size=13)),
                    xaxis_tickangle=-25,
                    yaxis=dict(title="Revenue (USD)")
                )
            else:
                fig_crop = create_empty_chart("No crop revenue data", "Revenue by Primary Crop")
        else:
            fig_crop = create_empty_chart("Crop data not available", "Revenue by Primary Crop")
    except Exception:
        fig_crop = create_empty_chart("Error loading crop data", "Revenue by Primary Crop")

    # Province performance
    if not f.empty and "province" in f.columns and "profit_margin_pct" in f.columns:
        prov = f.groupby("province")["profit_margin_pct"].mean().reset_index()
        fig_prov = go.Figure(go.Bar(
            x=prov["province"], y=prov["profit_margin_pct"],
            marker=dict(color=AMBER, opacity=0.85),
            text=[f"{v:.1f}%" for v in prov["profit_margin_pct"]],
            textfont=dict(color="#f0fdf4"),
        ))
        apply_theme(fig_prov, 260)
        fig_prov.update_layout(title=dict(text="Avg Profit Margin by Province", font=dict(color="#86efac", size=13)))
    else:
        fig_prov = create_empty_chart("No province data", "Avg Profit Margin by Province")

    alerts = [
        ("🔴", "Mvurwi Mixed Farm", "Fertilizer stock at critical level — reorder required"),
        ("🟡", "Headlands Cotton Block", "Pest pressure HIGH — intervention recommended"),
        ("🔴", "Bindura Soya Farm", "Supplier Windmill Zimbabwe suspended — overdue $14,200"),
        ("🟡", "Karoi Maize Cooperative", "Post-harvest loss above threshold — review storage"),
    ]

    return html.Div([
        export_section,
        page_header("Farm Operations Dashboard", "National portfolio overview · All farms · All seasons"),
        html.Div([
            kpi(fmt_usd(total_revenue), "Total Portfolio Revenue", "↑ 12.4% vs last year", True),
            kpi(fmt_usd(total_profit), "Total Gross Profit", "↑ 8.1% vs last year", True, LIME),
            kpi(f"{avg_margin:.1f}%", "Avg Profit Margin", "↑ 1.2pp vs last season", True, AMBER),
            kpi(f"{total_ha:,.0f} ha", "Hectares Under Cultivation", None),
            kpi(f"{active_farms}/{len(f)}", "Active Farms", None, True, BLUE),
            kpi(str(critical_alerts), "Critical Alerts", "Requires attention", False, RED),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(6,1fr)", "gap": "14px", "marginBottom": "24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_trend, config={"displayModeBar": False})], {"flex": "2"}),
            card([dcc.Graph(figure=fig_crop, config={"displayModeBar": False})], {"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),
        html.Div([
            card([dcc.Graph(figure=fig_ranking, config={"displayModeBar": False})], {"flex": "1.4"}),
            card([dcc.Graph(figure=fig_prov, config={"displayModeBar": False})], {"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),
        card([
            html.Div("⚠️ Live Alerts", style={"color": RED, "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
            *[html.Div([
                html.Span(icon, style={"marginRight": "8px"}),
                html.Span(farm + " — ", style={"color": "#f0fdf4", "fontWeight": "500", "fontSize": "0.83rem"}),
                html.Span(msg, style={"color": "#6b7280", "fontSize": "0.82rem"}),
            ], style={"padding": "10px 0", "borderBottom": "1px solid rgba(34,197,94,0.08)"}) for icon, farm, msg in alerts]
        ]),
    ])

def register_callbacks(app):
    pass
