"""Module 09 — Supply Chain Pipeline"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import supply_chain
from utils import GREEN, AMBER, BLUE, LIME, RED, PALETTE, fmt_usd, fmt_tons, apply_theme, page_header, card, kpi, status_badge

# Stage definitions
STAGE_ORDER = ["Field Harvest", "Transport", "Storage", "Processing", "Delivered", "Export Cleared"]
STAGE_COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#a855f7', '#10b981', '#ec4899']

def layout():
    sc = supply_chain()
    
    if sc.empty:
        return html.Div([
            page_header("Supply Chain Pipeline", "Field → Transport → Storage → Processing → Market · End-to-end visibility"),
            card([html.Div("⚠️ No supply chain data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])

    by_stage = sc.groupby("current_stage").agg(count=("shipment_id", "count"), value=("value_usd", "sum")).reset_index()
    by_stage["stage_order"] = by_stage["current_stage"].map({s: i for i, s in enumerate(STAGE_ORDER)})
    by_stage = by_stage.sort_values("stage_order")

    fig_funnel = go.Figure(go.Funnel(
        y=by_stage["current_stage"], x=by_stage["count"],
        textinfo="value+percent initial",
        marker=dict(color=STAGE_COLORS[:len(by_stage)]),
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_funnel, 320)
    fig_funnel.update_layout(title=dict(text="Harvest-to-Market Pipeline", font=dict(color="#86efac", size=13)))

    dest = sc.groupby("destination")["value_usd"].sum().reset_index().sort_values("value_usd", ascending=False).head(8)
    fig_dest = go.Figure(go.Bar(
        x=dest["value_usd"], y=dest["destination"],
        orientation="h", marker=dict(color=GREEN, opacity=0.8),
        text=[fmt_usd(v) for v in dest["value_usd"]],
        textfont=dict(color="#f0fdf4", size=10),
    ))
    apply_theme(fig_dest, 300)
    fig_dest.update_layout(title=dict(text="Value by Destination Market", font=dict(color="#86efac", size=13)))

    delayed = sc[sc["days_delayed"] > 0].sort_values("days_delayed", ascending=False)

    rows = []
    for _, row in sc.sort_values("start_date", ascending=False).head(25).iterrows():
        rows.append(html.Tr([
            html.Td(row["shipment_id"], style={"color": LIME, "fontSize": "0.78rem", "padding": "8px 6px", "fontFamily": "monospace"}),
            html.Td(row["farm_name"][:20], style={"color": "#f0fdf4", "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(row["crop"], style={"color": GREEN, "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(fmt_tons(row["quantity_tons"]), style={"color": "#f0fdf4", "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(row["current_stage"], style={"color": BLUE, "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(row["destination"][:22], style={"color": "#6b7280", "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(f"+{row['days_delayed']}d" if row["days_delayed"] > 0 else "On time",
                    style={"color": RED if row["days_delayed"] > 0 else GREEN, "fontSize": "0.78rem", "fontWeight": "600", "padding": "8px 6px"}),
        ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color": "#4ade80", "fontSize": "0.70rem", "fontWeight": "600", "textTransform": "uppercase", "padding": "8px 6px", "letterSpacing": "0.06em"})
                             for h in ["Shipment ID", "Farm", "Crop", "Qty", "Stage", "Destination", "Delay"]])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse"})

    return html.Div([
        page_header("Supply Chain Pipeline", "Field → Transport → Storage → Processing → Market · End-to-end visibility"),
        html.Div([
            kpi(str(len(sc)), "Total Shipments", None),
            kpi(fmt_usd(sc["value_usd"].sum()), "Pipeline Value", None, True, GREEN),
            kpi(str(len(delayed)), "Delayed", "Shipments behind schedule", False, AMBER),
            kpi(f"{sc['days_delayed'].mean():.1f}d", "Avg Delay", None, False, RED),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px", "marginBottom": "24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_funnel, config={"displayModeBar": False})]),
            card([dcc.Graph(figure=fig_dest, config={"displayModeBar": False})]),
        ], style={"display": "grid", "gridTemplateColumns": "1fr 1.2fr", "gap": "16px", "marginBottom": "16px"}),
        card([
            html.Div("🔗  Active Shipments", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
            html.Div(table, style={"overflowX": "auto", "maxHeight": "380px", "overflowY": "auto"}),
        ]),
    ])

def register_callbacks(app): 
    pass
