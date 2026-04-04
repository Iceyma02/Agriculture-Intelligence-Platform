"""Module 08 — Reorder Optimizer"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import reorder
from utils import GREEN, AMBER, RED, LIME, BLUE, fmt_usd, apply_theme, page_header, card, kpi

def layout():
    r = reorder()
    
    if r.empty:
        return html.Div([
            page_header("Reorder Optimizer", "Smart purchasing schedule · Planting window aligned · Urgency ranked"),
            card([html.Div("⚠️ No reorder data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])
    
    critical = r[r["urgency"] == "CRITICAL"]
    high = r[r["urgency"] == "HIGH"]

    by_urgency = r.groupby("urgency")["estimated_cost_usd"].sum().reset_index()
    color_map = {"CRITICAL": RED, "HIGH": AMBER, "MEDIUM": BLUE, "LOW": GREEN}
    fig_urg = go.Figure(go.Bar(
        x=by_urgency["urgency"], y=by_urgency["estimated_cost_usd"],
        marker=dict(color=[color_map.get(u, GREEN) for u in by_urgency["urgency"]]),
        text=[fmt_usd(v) for v in by_urgency["estimated_cost_usd"]],
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_urg, 260)
    fig_urg.update_layout(title=dict(text="Reorder Value by Urgency Level", font=dict(color="#86efac", size=13)))

    rows = []
    for _, row in r.sort_values(["urgency", "days_to_planting"]).head(30).iterrows():
        urg_color = color_map.get(row["urgency"], GREEN)
        rows.append(html.Tr([
            html.Td(row["farm_name"][:20], style={"color": "#f0fdf4", "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(row["supplier_name"][:22], style={"color": "#86efac", "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(row["category"], style={"color": "#6b7280", "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(fmt_usd(row["estimated_cost_usd"]), style={"color": GREEN, "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(f"{row['days_to_planting']}d", style={"color": RED if row["days_to_planting"] < 7 else AMBER, "fontSize": "0.8rem", "padding": "8px 6px"}),
            html.Td(f"{row['supplier_lead_days']}d", style={"color": "#6b7280", "fontSize": "0.78rem", "padding": "8px 6px"}),
            html.Td(html.Span(row["urgency"], style={"background": f"{urg_color}22", "color": urg_color, "padding": "3px 10px", "borderRadius": "20px", "fontSize": "0.72rem", "fontWeight": "600"})),
            html.Td(str(row["recommended_order_date"])[:10], style={"color": LIME, "fontSize": "0.78rem", "padding": "8px 6px"}),
        ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color": "#4ade80", "fontSize": "0.70rem", "fontWeight": "600", "textTransform": "uppercase", "padding": "8px 6px", "letterSpacing": "0.06em"})
                             for h in ["Farm", "Supplier", "Category", "Est Cost", "Days to Plant", "Lead Days", "Urgency", "Order By"]])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse"})

    return html.Div([
        page_header("Reorder Optimizer", "Smart purchasing schedule · Planting window aligned · Urgency ranked"),
        html.Div([
            kpi(str(len(critical)), "CRITICAL Orders", "Order today", False, RED),
            kpi(str(len(high)), "HIGH Priority", "Order this week", False, AMBER),
            kpi(fmt_usd(r["estimated_cost_usd"].sum()), "Total Reorder Value", None, True, GREEN),
            kpi(f"{r['supplier_lead_days'].mean():.0f} days", "Avg Supplier Lead", None),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px", "marginBottom": "24px"}),
        card([dcc.Graph(figure=fig_urg, config={"displayModeBar": False})], {"marginBottom": "16px"}),
        card([
            html.Div("🔄  Reorder Queue — Prioritized", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
            html.Div(table, style={"overflowX": "auto", "maxHeight": "420px", "overflowY": "auto"}),
        ]),
    ])

def register_callbacks(app): 
    pass
