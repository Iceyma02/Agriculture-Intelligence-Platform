"""Module 04 — Farm P&L Engine"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import pnl
from utils import GREEN, RED, LIME, AMBER, BLUE, PALETTE, fmt_usd, apply_theme, page_header, card, kpi

def layout():
    p = pnl()
    
    if p.empty:
        return html.Div([
            page_header("Farm P&L Engine", "True profitability per farm · Season: 2025 Summer"),
            card([html.Div("⚠️ No P&L data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])
    
    latest = p[p["season"] == "2025 Summer"]
    
    if latest.empty:
        latest = p

    first = latest.iloc[0]
    fig_waterfall = go.Figure(go.Waterfall(
        name="P&L",
        orientation="v",
        measure=["absolute","relative","relative","relative","relative","relative","relative","relative","relative","total"],
        x=["Revenue","Seeds","Fertilizer","Labour","Irrigation","Equipment","Transport","Chemicals","Storage","Net Profit"],
        y=[first["revenue_usd"],
           -first["seeds_usd"], -first["fertilizer_usd"], -first["labour_usd"],
           -first["irrigation_usd"], -first["equipment_usd"], -first["transport_usd"],
           -first["chemicals_usd"], -first["storage_usd"],
           first["gross_profit_usd"]],
        connector=dict(line=dict(color="rgba(34,197,94,0.2)")),
        increasing=dict(marker=dict(color=GREEN)),
        decreasing=dict(marker=dict(color=RED)),
        totals=dict(marker=dict(color=LIME)),
        text=[fmt_usd(abs(v)) for v in [first["revenue_usd"], first["seeds_usd"], first["fertilizer_usd"],
              first["labour_usd"], first["irrigation_usd"], first["equipment_usd"],
              first["transport_usd"], first["chemicals_usd"], first["storage_usd"], first["gross_profit_usd"]]],
        textfont=dict(color="#f0fdf4", size=10),
    ))
    apply_theme(fig_waterfall, 320)
    fig_waterfall.update_layout(title=dict(text=f"P&L Waterfall — {first['farm_name']} · 2025 Summer", font=dict(color="#86efac", size=13)))

    cost_cols = ["seeds_usd","fertilizer_usd","labour_usd","irrigation_usd","equipment_usd","transport_usd","chemicals_usd","storage_usd"]
    cost_labels = ["Seeds","Fertilizer","Labour","Irrigation","Equipment","Transport","Chemicals","Storage"]
    fig_costs = go.Figure()
    for col, label, color in zip(cost_cols, cost_labels, PALETTE):
        fig_costs.add_trace(go.Bar(name=label, x=latest["farm_name"], y=latest[col], marker_color=color))
    fig_costs.update_layout(barmode="stack", xaxis_tickangle=-25)
    apply_theme(fig_costs, 320)
    fig_costs.update_layout(title=dict(text="Cost Breakdown by Farm — 2025 Summer", font=dict(color="#86efac", size=13)))

    fig_margin = go.Figure(go.Scatter(
        x=latest["revenue_usd"], y=latest["profit_margin_pct"],
        mode="markers+text",
        marker=dict(size=14, color=latest["profit_margin_pct"], colorscale=[[0,"#7f1d1d"],[1,"#22c55e"]], showscale=False),
        text=latest["farm_name"].str[:12],
        textposition="top center",
        textfont=dict(color="#86efac", size=9),
    ))
    apply_theme(fig_margin, 300)
    fig_margin.update_layout(
        title=dict(text="Revenue vs Profit Margin", font=dict(color="#86efac", size=13)),
        xaxis=dict(title="Revenue (USD)", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)"),
        yaxis=dict(title="Margin %", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)"),
    )

    rows = []
    for _, row in latest.sort_values("gross_profit_usd", ascending=False).iterrows():
        rows.append(html.Tr([
            html.Td(row["farm_name"], style={"color":"#f0fdf4","fontSize":"0.82rem","fontWeight":"500","padding":"9px 8px"}),
            html.Td(fmt_usd(row["revenue_usd"]), style={"color":GREEN,"fontSize":"0.82rem","padding":"9px 8px"}),
            html.Td(fmt_usd(row["total_cost_usd"]), style={"color":RED,"fontSize":"0.82rem","padding":"9px 8px"}),
            html.Td(fmt_usd(row["gross_profit_usd"]), style={"color":LIME,"fontSize":"0.82rem","fontWeight":"700","padding":"9px 8px"}),
            html.Td(f"{row['profit_margin_pct']:.1f}%", style={"color":GREEN if row["profit_margin_pct"]>30 else AMBER,"fontSize":"0.82rem","fontWeight":"600","padding":"9px 8px"}),
            html.Td(fmt_usd(row["profit_per_ha"]), style={"color":"#86efac","fontSize":"0.82rem","padding":"9px 8px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"color":"#4ade80","fontSize":"0.72rem","fontWeight":"600","textTransform":"uppercase","padding":"8px","letterSpacing":"0.08em"})
            for h in ["Farm","Revenue","Total Cost","Gross Profit","Margin %","Profit/ha"]
        ])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    return html.Div([
        page_header("Farm P&L Engine", "True profitability per farm · Season: 2025 Summer"),
        html.Div([
            kpi(fmt_usd(latest["revenue_usd"].sum()), "Season Revenue", "2025 Summer", True),
            kpi(fmt_usd(latest["total_cost_usd"].sum()), "Total Costs", None, False, RED),
            kpi(fmt_usd(latest["gross_profit_usd"].sum()), "Gross Profit", "↑ 9.3% vs 2024", True, LIME),
            kpi(f"{latest['profit_margin_pct'].mean():.1f}%", "Avg Margin", None, True, AMBER),
            kpi(fmt_usd(latest["profit_per_ha"].mean()), "Avg Profit / Ha", None, True, BLUE),
        ], style={"display":"grid","gridTemplateColumns":"repeat(5,1fr)","gap":"14px","marginBottom":"24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_waterfall, config={"displayModeBar":False})]),
            card([dcc.Graph(figure=fig_margin, config={"displayModeBar":False})]),
        ], style={"display":"grid","gridTemplateColumns":"1.4fr 1fr","gap":"16px","marginBottom":"16px"}),
        card([dcc.Graph(figure=fig_costs, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        card([
            html.Div("📊  P&L Summary Table — All Farms · 2025 Summer", style={"color":"#86efac","fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            html.Div(table, style={"overflowX":"auto"}),
        ]),
    ])

def register_callbacks(app): pass
