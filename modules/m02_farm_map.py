"""Module 02 — Farm Map (Geographic Intelligence)"""

from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import farms
from utils.helpers import GREEN, AMBER, page_header, card, status_badge, add_export_section, create_search_filter

def layout():
    f = farms()
    
    export_section = add_export_section({"Farms_Geographic_Data": f})
    search_bar = create_search_filter("farm-search", "Search farms by name, province, or crop...")
    
    if f.empty:
        return html.Div([
            export_section,
            search_bar,
            page_header("Farm Map", "Geographic distribution · Color-coded by profit margin · Bubble size = farm hectarage"),
            card([html.Div("⚠️ No farm data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])

    # Store full data for filtering
    full_data = f.to_dict('records')
    
    # Fix: Use correct column names (id instead of farm_id if needed)
    id_column = 'farm_id' if 'farm_id' in f.columns else 'id' if 'id' in f.columns else None
    
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=f["lat"], lon=f["lon"],
        mode="markers+text",
        marker=dict(
            size=f["size_ha"] / 60 + 12,
            color=f["profit_margin_pct"],
            colorscale=[[0, "#7f1d1d"], [0.4, "#f59e0b"], [1, "#22c55e"]],
            showscale=True,
            colorbar=dict(title=dict(text="Profit Margin %", font=dict(color="#86efac")), tickfont=dict(color="#86efac")),
            opacity=0.88,
        ),
        text=f["name"],
        textfont=dict(color="#f0fdf4", size=10),
        textposition="top center",
        customdata=f[["name", "primary_crop", "size_ha", "profit_margin_pct", "status", "owner", "irrigation_type"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>Crop: %{customdata[1]}<br>Size: %{customdata[2]:,} ha<br>"
            "Margin: %{customdata[3]:.1f}%<br>Status: %{customdata[4]}<br>Owner: %{customdata[5]}<br>Irrigation: %{customdata[6]}<extra></extra>"
        ),
    ))

    fig.update_layout(
        mapbox=dict(style="carto-darkmatter", center=dict(lat=-19.0, lon=30.5), zoom=5.8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0), height=520, font=dict(color="#86efac"), showlegend=False,
    )

    # Table placeholder (will be populated by callback)
    farm_table = html.Div(id="filtered-farm-table", children=[
        html.Div("Loading farms...", style={"color": "#86efac", "padding": "20px", "textAlign": "center"})
    ])

    return html.Div([
        html.Div([export_section], style={"display": "flex", "gap": "10px", "flexWrap": "wrap", "marginBottom": "15px"}),
        search_bar,
        page_header("Farm Map", "Geographic distribution · Color-coded by profit margin · Bubble size = farm hectarage"),
        card([dcc.Graph(figure=fig, config={"displayModeBar": True})], {"marginBottom": "16px"}),
        card([
            html.Div("📍 All Farm Locations", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
            farm_table
        ]),
        dcc.Store(id="farm-data-original", data=full_data)
    ])

def register_callbacks(app):
    @app.callback(
        Output("filtered-farm-table", "children"),
        Input("farm-search", "value"),
        State("farm-data-original", "data")
    )
    def filter_farms(search_term, farm_data):
        if not farm_data:
            return html.Div("No farm data available", style={"color": AMBER, "textAlign": "center", "padding": "20px"})
        
        # Filter data based on search term
        if search_term:
            search_lower = search_term.lower()
            filtered = [
                row for row in farm_data 
                if search_lower in str(row.get("name", "")).lower()
                or search_lower in str(row.get("province", "")).lower()
                or search_lower in str(row.get("primary_crop", "")).lower()
            ]
        else:
            filtered = farm_data
        
        if not filtered:
            return html.Div("No matching farms found", style={"color": AMBER, "textAlign": "center", "padding": "20px"})
        
        # Build table rows
        rows = []
        for row in filtered:
            profit_color = GREEN if row.get("profit_margin_pct", 0) > 30 else AMBER
            # Get ID from available column
            row_id = row.get("farm_id", row.get("id", row.get("name", "N/A")))
            rows.append(html.Tr([
                html.Td(row_id, style={"color": "#4ade80", "fontSize": "0.78rem"}),
                html.Td(str(row.get("name", "N/A"))[:25], style={"color": "#f0fdf4", "fontSize": "0.82rem", "fontWeight": "500"}),
                html.Td(row.get("province", "N/A"), style={"color": "#6b7280", "fontSize": "0.8rem"}),
                html.Td(row.get("primary_crop", "N/A"), style={"color": "#86efac", "fontSize": "0.8rem"}),
                html.Td(f"{row.get('size_ha', 0):,} ha", style={"color": "#f0fdf4", "fontSize": "0.8rem"}),
                html.Td(status_badge(row.get("status", "Unknown"))),
                html.Td(f"{row.get('profit_margin_pct', 0):.1f}%", style={"color": profit_color, "fontSize": "0.8rem", "fontWeight": "600"}),
            ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))
        
        return html.Table([
            html.Thead(html.Tr([html.Th(h, style={"color": "#4ade80", "fontSize": "0.72rem", "fontWeight": "600", "textTransform": "uppercase", "padding": "8px 10px"}) for h in ["ID", "Farm Name", "Province", "Primary Crop", "Size", "Status", "Margin"]])),
            html.Tbody(rows),
        ], style={"width": "100%", "borderCollapse": "collapse"})
