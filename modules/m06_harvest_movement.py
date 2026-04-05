"""Module 06 — Harvest Movement"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import movement
from utils.helpers import GREEN, AMBER, BLUE, LIME, RED, PALETTE, fmt_usd, fmt_tons, apply_theme, page_header, card, kpi, status_badge, add_export_section, create_empty_chart

def layout():
    mv = movement()
    
    export_section = add_export_section({"Harvest_Movement_Complete": mv})
    
    if mv.empty:
        return html.Div([
            export_section,
            page_header("Harvest Movement", "Crop flow from field to market · Transport, storage and delivery tracking"),
            card([html.Div("⚠️ No movement data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])

    by_type = mv.groupby("movement_type")["quantity_tons"].sum().reset_index().sort_values("quantity_tons", ascending=False)
    fig_type = go.Figure(go.Bar(
        x=by_type["movement_type"], y=by_type["quantity_tons"],
        marker=dict(color=PALETTE[:len(by_type)]), text=[fmt_tons(v) for v in by_type["quantity_tons"]],
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_type, 280)
    fig_type.update_layout(title=dict(text="Volume by Movement Type", font=dict(color="#86efac", size=13)), xaxis_tickangle=-15)

    by_crop = mv.groupby("crop")["value_usd"].sum().reset_index().sort_values("value_usd", ascending=False)
    fig_crop = go.Figure(go.Pie(
        labels=by_crop["crop"], values=by_crop["value_usd"],
        hole=0.55, marker=dict(colors=PALETTE),
        textinfo="label+percent", textfont=dict(color="#f0fdf4", size=11),
    ))
    apply_theme(fig_crop, 280)
    fig_crop.update_layout(title=dict(text="Value by Crop", font=dict(color="#86efac", size=13)), showlegend=False)

    mv["date"] = mv["date"].astype(str)
    daily = mv.groupby("date")["quantity_tons"].sum().reset_index().sort_values("date")
    fig_time = go.Figure(go.Scatter(
        x=daily["date"], y=daily["quantity_tons"],
        mode="lines", fill="tozeroy",
        line=dict(color=BLUE, width=2), fillcolor="rgba(56,189,248,0.08)",
    ))
    apply_theme(fig_time, 260)
    fig_time.update_layout(title=dict(text="Daily Movement Volume (tons)", font=dict(color="#86efac", size=13)))

    recent = mv.sort_values("date", ascending=False).head(25)
    rows = []
    for _, row in recent.iterrows():
        rows.append(html.Tr([
            html.Td(str(row["date"])[:10], style={"color": "#6b7280", "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(row["farm_name"][:20], style={"color": "#f0fdf4", "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(row["crop"], style={"color": GREEN, "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(row["movement_type"], style={"color": "#86efac", "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(fmt_tons(row["quantity_tons"]), style={"color": "#f0fdf4", "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(row["destination"][:22], style={"color": "#6b7280", "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(status_badge(row["status"])),
        ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color": "#4ade80", "fontSize": "0.70rem", "fontWeight": "600", "textTransform": "uppercase", "padding": "8px 6px"}) for h in ["Date", "Farm", "Crop", "Movement Type", "Qty", "Destination", "Status"]])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse"})

    return html.Div([
        export_section,
        page_header("Harvest Movement", "Crop flow from field to market · Transport, storage and delivery tracking"),
        html.Div([
            kpi(fmt_tons(mv["quantity_tons"].sum()), "Total Moved", None),
            kpi(fmt_usd(mv["value_usd"].sum()), "Total Value", None, True, GREEN),
            kpi(str(len(mv[mv["status"] == "In Transit"])), "In Transit Now", None, True, BLUE),
            kpi(str(len(mv[mv["status"] == "Pending"])), "Pending", None, False, AMBER),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px", "marginBottom": "24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_type, config={"displayModeBar": False})]),
            card([dcc.Graph(figure=fig_crop, config={"displayModeBar": False})]),
        ], style={"display": "grid", "gridTemplateColumns": "1.5fr 1fr", "gap": "16px", "marginBottom": "16px"}),
        card([dcc.Graph(figure=fig_time, config={"displayModeBar": False})], {"marginBottom": "16px"}),
        card([html.Div("🚚 Recent Movements", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}), html.Div(table, style={"overflowX": "auto", "maxHeight": "380px", "overflowY": "auto"})]),
    ])

def register_callbacks(app): pass
