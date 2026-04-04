"""Module 02 — Farm Map (Geographic Intelligence)"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    f = farms()

    # Bubble map
    fig = go.Figure()

    # Color by profit margin
    fig.add_trace(go.Scattermapbox(
        lat=f["lat"],
        lon=f["lon"],
        mode="markers+text",
        marker=dict(
            size=f["size_ha"] / 60 + 12,
            color=f["profit_margin_pct"],
            colorscale=[[0, "#7f1d1d"], [0.4, "#f59e0b"], [1, "#22c55e"]],
            showscale=True,
            colorbar=dict(title=dict(text="Profit Margin %", font=dict(color="#86efac")),
                          tickfont=dict(color="#86efac"), bgcolor="rgba(0,0,0,0)"),
            opacity=0.88,
        ),
        text=f["name"],
        textfont=dict(color="#f0fdf4", size=10),
        textposition="top center",
        customdata=f[["name", "primary_crop", "size_ha", "profit_margin_pct", "status", "owner", "irrigation_type"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Crop: %{customdata[1]}<br>"
            "Size: %{customdata[2]:,} ha<br>"
            "Margin: %{customdata[3]:.1f}%<br>"
            "Status: %{customdata[4]}<br>"
            "Owner: %{customdata[5]}<br>"
            "Irrigation: %{customdata[6]}<extra></extra>"
        ),
        name="Farms",
    ))

    fig.update_layout(
        mapbox=dict(
            style="carto-darkmatter",
            center=dict(lat=-19.0, lon=30.5),
            zoom=5.8,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=520,
        font=dict(color="#86efac"),
        showlegend=False,
    )

    # Farm table
    rows = []
    for _, row in f.iterrows():
        rows.append(html.Tr([
            html.Td(row["id"], style={"color": "#4ade80", "fontSize": "0.78rem"}),
            html.Td(row["name"], style={"color": "#f0fdf4", "fontSize": "0.82rem", "fontWeight": "500"}),
            html.Td(row["province"], style={"color": "#6b7280", "fontSize": "0.8rem"}),
            html.Td(row["primary_crop"], style={"color": "#86efac", "fontSize": "0.8rem"}),
            html.Td(f"{row['size_ha']:,} ha", style={"color": "#f0fdf4", "fontSize": "0.8rem"}),
            html.Td(status_badge(row["status"])),
            html.Td(f"{row['profit_margin_pct']:.1f}%", style={"color": GREEN if row["profit_margin_pct"] > 30 else AMBER, "fontSize": "0.8rem", "fontWeight": "600"}),
        ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))

    farm_table = html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"color": "#4ade80", "fontSize": "0.72rem", "fontWeight": "600",
                               "textTransform": "uppercase", "padding": "8px 10px", "letterSpacing": "0.08em"})
            for h in ["ID", "Farm Name", "Province", "Primary Crop", "Size", "Status", "Margin"]
        ])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse"})

    return html.Div([
        page_header("Farm Map", "Geographic distribution · Color-coded by profit margin · Bubble size = farm hectarage"),

        card([dcc.Graph(figure=fig, config={"displayModeBar": True})], {"marginBottom": "16px"}),

        html.Div([
            card([
                html.Div("📍  All Farm Locations", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
                html.Div(farm_table, style={"overflowX": "auto"}),
            ]),
        ]),
    ])

def register_callbacks(app):
    pass
