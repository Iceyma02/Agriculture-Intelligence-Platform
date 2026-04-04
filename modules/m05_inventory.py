"""Module 05 — Inputs & Stock Monitor"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    inv = inventory()

    total_items = len(inv)
    critical_count = len(inv[inv["status"] == "Critical"])
    low_count = len(inv[inv["status"] == "Low"])
    ok_count = len(inv[inv["status"] == "OK"])

    # Status donut
    fig_status = go.Figure(go.Pie(
        labels=["OK", "Low", "Critical"],
        values=[ok_count, low_count, critical_count],
        hole=0.62,
        marker=dict(colors=[GREEN, AMBER, RED]),
        textinfo="label+value",
        textfont=dict(color="#f0fdf4", size=12),
    ))
    apply_theme(fig_status, 280)
    fig_status.update_layout(title=dict(text="Stock Health Overview", font=dict(color="#86efac", size=13)), showlegend=False)

    # By category
    cat_status = inv.groupby(["category","status"]).size().reset_index(name="count")
    categories = inv["category"].unique()
    fig_cat = go.Figure()
    for status, color in [("OK", GREEN), ("Low", AMBER), ("Critical", RED)]:
        sub = cat_status[cat_status["status"] == status]
        fig_cat.add_trace(go.Bar(name=status, x=sub["category"], y=sub["count"], marker_color=color))
    fig_cat.update_layout(barmode="stack")
    apply_theme(fig_cat, 280)
    fig_cat.update_layout(title=dict(text="Stock Status by Category", font=dict(color="#86efac", size=13)))

    # Stock level gauge per item (top 8 critical)
    critical_items = inv[inv["status"] == "Critical"].head(8)
    fig_bars = go.Figure()
    for i, (_, row) in enumerate(critical_items.iterrows()):
        pct = row["qty_current"] / row["qty_max"] * 100
        fig_bars.add_trace(go.Bar(
            name=row["item_name"][:25],
            x=[pct], y=[row["item_name"][:25]],
            orientation="h",
            marker=dict(color=RED if pct < 20 else AMBER),
            text=[f"{pct:.0f}% — {row['farm_name'][:15]}"],
            textfont=dict(color="#f0fdf4", size=10),
        ))
    apply_theme(fig_bars, 300)
    fig_bars.update_layout(
        title=dict(text="Critical Stock Items — % of Capacity", font=dict(color="#86efac", size=13)),
        showlegend=False, xaxis=dict(range=[0,100]),
    )

    # Table — all critical items
    rows = []
    for _, row in inv[inv["status"] != "OK"].sort_values("status").head(30).iterrows():
        rows.append(html.Tr([
            html.Td(row["farm_name"][:20], style={"color":"#f0fdf4","fontSize":"0.8rem","padding":"8px 6px"}),
            html.Td(row["item_name"][:28], style={"color":"#86efac","fontSize":"0.8rem","padding":"8px 6px"}),
            html.Td(row["category"], style={"color":"#6b7280","fontSize":"0.78rem","padding":"8px 6px"}),
            html.Td(f"{row['qty_current']}/{row['qty_max']}", style={"color":"#f0fdf4","fontSize":"0.8rem","padding":"8px 6px"}),
            html.Td(row["unit"], style={"color":"#6b7280","fontSize":"0.78rem","padding":"8px 6px"}),
            html.Td(status_badge(row["status"])),
            html.Td(row["supplier"][:20], style={"color":"#6b7280","fontSize":"0.78rem","padding":"8px 6px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px 6px","letterSpacing":"0.06em"})
            for h in ["Farm","Item","Category","Qty / Max","Unit","Status","Supplier"]
        ])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    return html.Div([
        page_header("Inputs & Stock Monitor", "Real-time input tracking across all farms · Alerts on critical levels"),
        html.Div([
            kpi(str(total_items), "Total Stock Lines", None),
            kpi(str(ok_count), "Items OK", None, True, GREEN),
            kpi(str(low_count), "Items Low", "Reorder soon", False, AMBER),
            kpi(str(critical_count), "Items Critical", "Immediate action", False, RED),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"14px","marginBottom":"24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_status, config={"displayModeBar":False})]),
            card([dcc.Graph(figure=fig_cat, config={"displayModeBar":False})]),
            card([dcc.Graph(figure=fig_bars, config={"displayModeBar":False})]),
        ], style={"display":"grid","gridTemplateColumns":"1fr 1fr 1.2fr","gap":"16px","marginBottom":"16px"}),
        card([
            html.Div("⚠️  Low & Critical Stock Items", style={"color":AMBER,"fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            html.Div(table, style={"overflowX":"auto","maxHeight":"400px","overflowY":"auto"}),
        ]),
    ])

def register_callbacks(app): pass
