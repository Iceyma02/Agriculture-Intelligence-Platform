"""Module 12 — Market Price Watch"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import market_prices
from utils import GREEN, AMBER, BLUE, LIME, RED, PURPLE, fmt_usd, apply_theme, page_header, card, kpi

def layout():
    mp = market_prices()
    
    if mp.empty:
        return html.Div([
            page_header("Market Price Watch", "Real-time price comparison · GMB · TIMB · COTTCO · Private · Export"),
            card([html.Div("⚠️ No market price data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])

    latest_date = mp["date"].max()
    latest = mp[mp["date"] == latest_date]

    fig_prices = go.Figure()
    for channel, color in [("gmb_price", GREEN), ("private_buyer_price", AMBER), ("export_price_usd", BLUE)]:
        sub = latest.dropna(subset=[channel])
        fig_prices.add_trace(go.Bar(
            name=channel.replace("_", " ").title(),
            x=sub["crop"], y=sub[channel],
            marker_color=color,
        ))
    fig_prices.update_layout(barmode="group", xaxis_tickangle=-15)
    apply_theme(fig_prices, 300)
    fig_prices.update_layout(title=dict(text="Current Prices: GMB vs Private vs Export (USD/ton)", font=dict(color="#86efac", size=13)))

    maize = mp[mp["crop"] == "Maize"].sort_values("date").tail(90) if "Maize" in mp["crop"].values else mp.sort_values("date").tail(90)
    fig_maize = go.Figure()
    if "gmb_price" in maize.columns:
        fig_maize.add_trace(go.Scatter(x=maize["date"], y=maize["gmb_price"], name="GMB", line=dict(color=GREEN, width=2)))
    if "private_buyer_price" in maize.columns:
        fig_maize.add_trace(go.Scatter(x=maize["date"], y=maize["private_buyer_price"], name="Private Buyer", line=dict(color=AMBER, width=2)))
    if "export_price_usd" in maize.columns:
        fig_maize.add_trace(go.Scatter(x=maize["date"], y=maize["export_price_usd"], name="Export", line=dict(color=BLUE, width=2, dash="dot")))
    apply_theme(fig_maize, 280)
    fig_maize.update_layout(title=dict(text="Maize Price Trend — 90 days", font=dict(color="#86efac", size=13)))

    rows = []
    for _, row in latest.iterrows():
        prices = {"GMB": row.get("gmb_price", 0) or 0, 
                  "Private": row.get("private_buyer_price", 0) or 0, 
                  "Export": row.get("export_price_usd", 0) or 0}
        best = max(prices, key=prices.get)
        rows.append(html.Tr([
            html.Td(row["crop"], style={"color": "#f0fdf4", "fontSize": "0.82rem", "fontWeight": "500", "padding": "9px 6px"}),
            html.Td(f"${row.get('gmb_price', 0):.0f}" if row.get("gmb_price") else "—", style={"color": GREEN, "fontSize": "0.8rem", "padding": "9px 6px"}),
            html.Td(f"${row.get('private_buyer_price', 0):.0f}" if row.get("private_buyer_price") else "—", style={"color": AMBER, "fontSize": "0.8rem", "padding": "9px 6px"}),
            html.Td(f"${row.get('export_price_usd', 0):.0f}" if row.get("export_price_usd") else "—", style={"color": BLUE, "fontSize": "0.8rem", "padding": "9px 6px"}),
            html.Td(html.Span(f"✅ {best}", style={"color": GREEN, "fontWeight": "600", "fontSize": "0.8rem"})),
        ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color": "#4ade80", "fontSize": "0.70rem", "fontWeight": "600", "textTransform": "uppercase", "padding": "8px 6px", "letterSpacing": "0.06em"})
                             for h in ["Crop", "GMB ($/ton)", "Private ($/ton)", "Export ($/ton)", "Recommended Channel"]])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse"})

    return html.Div([
        page_header("Market Price Watch", "Real-time price comparison · GMB · TIMB · COTTCO · Private · Export"),
        html.Div([
            kpi("$285", "Maize — GMB Price", "Per ton today", True, GREEN),
            kpi("$3,200", "Tobacco — TIMB", "Per ton today", True, PURPLE),
            kpi("$680", "Cotton — COTTCO", "Per ton today", True, AMBER),
            kpi("$1,200", "Horticulture Export", "Per ton today", True, BLUE),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px", "marginBottom": "24px"}),
        card([dcc.Graph(figure=fig_prices, config={"displayModeBar": False})], {"marginBottom": "16px"}),
        card([dcc.Graph(figure=fig_maize, config={"displayModeBar": False})], {"marginBottom": "16px"}),
        card([
            html.Div("📊  Sell Channel Recommendations — Today's Prices", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
            html.Div(table, style={"overflowX": "auto"}),
        ]),
    ])

def register_callbacks(app): 
    pass
