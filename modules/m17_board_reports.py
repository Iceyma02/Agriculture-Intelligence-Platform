"""Module 17 — Board Reports (Executive Summaries)"""
from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    br = board()
    p = pnl()
    f = farms()
    ls = losses()
    mk = marketing()

    latest_season = "2025 Summer"
    latest = br[br["season"] == latest_season].iloc[0]
    prev = br[br["season"] == "2024 Summer"].iloc[0]

    rev_growth = (latest["total_revenue_usd"] - prev["total_revenue_usd"]) / prev["total_revenue_usd"] * 100
    profit_growth = (latest["total_profit_usd"] - prev["total_profit_usd"]) / prev["total_profit_usd"] * 100

    # Revenue vs profit all seasons
    fig_seasons = go.Figure()
    fig_seasons.add_trace(go.Bar(name="Revenue", x=br["season"], y=br["total_revenue_usd"], marker_color=GREEN))
    fig_seasons.add_trace(go.Bar(name="Profit", x=br["season"], y=br["total_profit_usd"], marker_color=LIME))
    fig_seasons.add_trace(go.Bar(name="Loss Value", x=br["season"], y=br["total_loss_value_usd"], marker_color=RED, opacity=0.7))
    fig_seasons.update_layout(barmode="group")
    apply_theme(fig_seasons, 280)
    fig_seasons.update_layout(title=dict(text="Season-on-Season Financial Performance", font=dict(color="#86efac",size=13)))

    # Margin trend
    fig_margin = go.Figure(go.Scatter(
        x=br["season"], y=br["avg_profit_margin_pct"],
        mode="lines+markers+text",
        line=dict(color=LIME, width=3),
        marker=dict(size=12, color=LIME),
        text=[f"{v:.1f}%" for v in br["avg_profit_margin_pct"]],
        textposition="top center",
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_margin, 220)
    fig_margin.update_layout(title=dict(text="Portfolio Profit Margin Trend", font=dict(color="#86efac",size=13)))

    # Top 5 farms by profit
    top5 = p[p["season"]==latest_season].sort_values("gross_profit_usd", ascending=False).head(5)
    fig_top5 = go.Figure(go.Bar(
        x=top5["farm_name"], y=top5["gross_profit_usd"],
        marker=dict(color=PALETTE[:5]),
        text=[fmt_usd(v) for v in top5["gross_profit_usd"]],
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_top5, 260)
    fig_top5.update_layout(title=dict(text="Top 5 Farms by Profit — 2025 Summer", font=dict(color="#86efac",size=13)), xaxis_tickangle=-15)

    # Risk matrix
    risk_items = [
        ("Post-Harvest Losses", "HIGH", fmt_usd(ls["loss_value_usd"].sum()), "Upgrade cold storage; deploy fumigation"),
        ("Supplier Credit Overdue", "HIGH", "Multiple accounts", "Priority payment queue activation"),
        ("El Niño Rainfall Risk", "MEDIUM", "6 alert months", "Expand irrigation coverage"),
        ("Labour Cost Escalation", "MEDIUM", "↑ 8.2% YoY", "Mechanisation feasibility study"),
        ("Fertilizer Price Volatility", "MEDIUM", "Index at 118", "Pre-season bulk procurement contract"),
        ("Currency Depreciation", "LOW", "ZWG 15.8/USD", "USD-denominated export contract hedging"),
    ]

    risk_rows = []
    for risk, level, impact, action in risk_items:
        level_color = RED if level=="HIGH" else AMBER if level=="MEDIUM" else GREEN
        risk_rows.append(html.Tr([
            html.Td(risk, style={"color":"#f0fdf4","fontSize":"0.82rem","fontWeight":"500","padding":"10px 8px"}),
            html.Td(html.Span(level, style={"background":f"{level_color}22","color":level_color,"padding":"3px 10px","borderRadius":"20px","fontSize":"0.72rem","fontWeight":"600"})),
            html.Td(impact, style={"color":AMBER,"fontSize":"0.8rem","padding":"10px 8px"}),
            html.Td(action, style={"color":"#6b7280","fontSize":"0.78rem","padding":"10px 8px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    risk_table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px","letterSpacing":"0.06em"})
                             for h in ["Risk Item","Level","Current Impact","Recommended Action"]])),
        html.Tbody(risk_rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    # Executive summary card
    exec_summary = html.Div([
        html.Div("📋  BOARD EXECUTIVE SUMMARY — 2025 SUMMER SEASON", style={
            "fontFamily":"'Playfair Display',serif","fontSize":"1.0rem","fontWeight":"700",
            "color":GREEN,"marginBottom":"20px","letterSpacing":"0.04em",
        }),
        html.Div([
            html.Div([
                html.P("FINANCIAL PERFORMANCE", style={"color":"#4ade80","fontSize":"0.68rem","fontWeight":"600","letterSpacing":"0.1em","textTransform":"uppercase","marginBottom":"10px"}),
                html.P(f"Portfolio revenue reached {fmt_usd(latest['total_revenue_usd'])} for the 2025 Summer season, representing a {rev_growth:.1f}% increase year-on-year from the 2024 Summer season. Gross profit of {fmt_usd(latest['total_profit_usd'])} was achieved at an average margin of {latest['avg_profit_margin_pct']:.1f}% across {latest['farms_active']} active farms covering {latest['total_hectares']:,} hectares.", style={"color":"#86efac","fontSize":"0.83rem","lineHeight":"1.75","marginBottom":"12px"}),
                html.P(f"Top performing farm: {latest['top_farm']}. Primary revenue crop: {latest['top_crop']}.", style={"color":"#f0fdf4","fontSize":"0.83rem","lineHeight":"1.75"}),
            ], style={"flex":"1","paddingRight":"24px","borderRight":"1px solid rgba(34,197,94,0.12)"}),
            html.Div([
                html.P("OPERATIONAL HIGHLIGHTS", style={"color":"#4ade80","fontSize":"0.68rem","fontWeight":"600","letterSpacing":"0.1em","textTransform":"uppercase","marginBottom":"10px"}),
                *[html.P(f"• {rec}", style={"color":"#86efac","fontSize":"0.82rem","lineHeight":"1.7","marginBottom":"6px"})
                  for rec in latest["recommendations"].split("; ")],
                html.P(f"• {latest['risk_alerts']} active risk alerts require board attention this quarter.", style={"color":AMBER,"fontSize":"0.82rem","lineHeight":"1.7","marginTop":"8px"}),
            ], style={"flex":"1","paddingLeft":"24px"}),
        ], style={"display":"flex"}),
    ], style={"background":"rgba(34,197,94,0.04)","border":"1px solid rgba(34,197,94,0.2)","borderRadius":"12px","padding":"24px","marginBottom":"20px"})

    return html.Div([
        page_header("Board Reports", "Executive summaries · Investor-ready · Season overview · Risk assessment"),
        html.Div([
            kpi(fmt_usd(latest["total_revenue_usd"]), "Season Revenue", f"↑ {rev_growth:.1f}% YoY", True, GREEN),
            kpi(fmt_usd(latest["total_profit_usd"]), "Season Profit", f"↑ {profit_growth:.1f}% YoY", True, LIME),
            kpi(f"{latest['avg_profit_margin_pct']:.1f}%", "Avg Margin", None, True, AMBER),
            kpi(f"{latest['total_hectares']:,} ha", "Total Hectares", f"{latest['farms_active']} active farms", True, BLUE),
            kpi(fmt_usd(latest["total_loss_value_usd"]), "Loss Value", "Post-harvest losses", False, RED),
            kpi(str(latest["risk_alerts"]), "Risk Alerts", "Active this season", False, RED),
        ], style={"display":"grid","gridTemplateColumns":"repeat(6,1fr)","gap":"14px","marginBottom":"24px"}),

        card([exec_summary], {"marginBottom":"16px"}),

        html.Div([
            card([dcc.Graph(figure=fig_seasons, config={"displayModeBar":False})], {"flex":"1.3"}),
            card([dcc.Graph(figure=fig_margin, config={"displayModeBar":False})], {"flex":"1"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

        card([dcc.Graph(figure=fig_top5, config={"displayModeBar":False})], {"marginBottom":"16px"}),

        card([
            html.Div("⚠️  Risk Register — Current Season", style={"color":RED,"fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            risk_table,
        ]),
    ])

def register_callbacks(app): pass
