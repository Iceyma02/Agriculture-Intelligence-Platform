"""
AgriIQ — Agriculture Intelligence Platform
Main application entry point
"""

import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules
from modules import (
    m01_overview, m02_farm_map, m03_performance, m04_pnl,
    m05_inventory, m06_harvest_movement, m07_yield_forecast, m08_reorder,
    m09_supply_chain, m10_supplier_credit, m11_marketing_roi, m12_market_prices,
    m13_buyer_satisfaction, m14_labour, m15_losses, m16_economic_watch, m17_board_reports
)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="AgriIQ — Agriculture Intelligence Platform",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

# Simple CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body { background-color: #0a0f0a; color: #f0fdf4; font-family: 'DM Sans', sans-serif; margin: 0; padding: 0; }
            .sidebar { position: fixed; top: 0; left: 0; height: 100vh; width: 260px; background: #111811; border-right: 1px solid #22c55e26; padding: 20px; overflow-y: auto; }
            .main-content { margin-left: 260px; padding: 20px; min-height: 100vh; }
            .nav-item { display: block; padding: 10px; margin: 5px 0; color: #6b7280; text-decoration: none; cursor: pointer; border-radius: 8px; }
            .nav-item:hover { background: #22c55e1a; color: #22c55e; }
            .nav-item.active { background: #22c55e1a; color: #22c55e; font-weight: bold; }
            .nav-section { font-size: 0.7rem; color: #4ade80; margin-top: 15px; margin-bottom: 5px; text-transform: uppercase; }
            .kpi-card { background: #151e15; border-radius: 10px; padding: 15px; margin: 10px; border: 1px solid #22c55e26; }
            .kpi-value { font-size: 1.8rem; font-weight: bold; }
            .card { background: #111811; border-radius: 12px; padding: 20px; margin: 10px; border: 1px solid #22c55e26; }
            @media (max-width: 768px) { .sidebar { transform: translateX(-100%); } .main-content { margin-left: 0; } }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>{%config%}{%scripts%}{%renderer%}</footer>
    </body>
</html>
'''

NAV_ITEMS = [
    {"section": "Overview", "id": None},
    {"id": "overview", "label": "Farm Dashboard"},
    {"id": "farm-map", "label": "Farm Map"},
    {"section": "Performance", "id": None},
    {"id": "performance", "label": "Farm Performance"},
    {"id": "pnl", "label": "Farm P&L Engine"},
    {"section": "Operations", "id": None},
    {"id": "inventory", "label": "Inputs & Stock"},
    {"id": "harvest-movement", "label": "Harvest Movement"},
    {"section": "Forecasting", "id": None},
    {"id": "yield-forecast", "label": "Yield Forecasting"},
    {"id": "reorder", "label": "Reorder Optimizer"},
    {"section": "Supply Chain", "id": None},
    {"id": "supply-chain", "label": "Supply Chain Pipeline"},
    {"id": "supplier-credit", "label": "Supplier Credit & Risk"},
    {"section": "Market", "id": None},
    {"id": "marketing-roi", "label": "Marketing ROI"},
    {"id": "market-prices", "label": "Market Price Watch"},
    {"section": "People", "id": None},
    {"id": "buyer-sat", "label": "Buyer Satisfaction"},
    {"id": "labour", "label": "Labour Intelligence"},
    {"section": "Risk", "id": None},
    {"id": "losses", "label": "Post-Harvest Loss"},
    {"id": "economic-watch", "label": "Agri-Economic Watch"},
    {"section": "Reporting", "id": None},
    {"id": "board-reports", "label": "Board Reports"},
]

def build_sidebar(active_id="overview"):
    children = [html.Div([html.H1("AgriIQ"), html.P("Agriculture Intelligence Platform")], style={"marginBottom": "30px"})]
    for item in NAV_ITEMS:
        if "section" in item and item["id"] is None:
            children.append(html.Div(item["section"], className="nav-section"))
        elif "id" in item:
            is_active = item["id"] == active_id
            children.append(html.Div(item["label"], id={"type": "nav-btn", "index": item["id"]}, className=f"nav-item {'active' if is_active else ''}"))
    children.append(html.Div("© 2026 Anesu Manjengwa", style={"marginTop": "50px", "fontSize": "0.7rem", "color": "#374151"}))
    return html.Div(children, className="sidebar")

app.layout = html.Div([
    dcc.Store(id="active-page", data="overview"),
    html.Div(id="sidebar-container"),
    html.Div(id="page-content", className="main-content"),
])

PAGE_MODULES = {
    "overview": m01_overview, "farm-map": m02_farm_map, "performance": m03_performance,
    "pnl": m04_pnl, "inventory": m05_inventory, "harvest-movement": m06_harvest_movement,
    "yield-forecast": m07_yield_forecast, "reorder": m08_reorder, "supply-chain": m09_supply_chain,
    "supplier-credit": m10_supplier_credit, "marketing-roi": m11_marketing_roi,
    "market-prices": m12_market_prices, "buyer-sat": m13_buyer_satisfaction,
    "labour": m14_labour, "losses": m15_losses, "economic-watch": m16_economic_watch,
    "board-reports": m17_board_reports,
}

@app.callback(Output("active-page", "data"), Input({"type": "nav-btn", "index": dash.ALL}, "n_clicks"), prevent_initial_call=True)
def set_active_page(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return "overview"
    import json
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return json.loads(triggered_id)["index"]

@app.callback(Output("sidebar-container", "children"), Output("page-content", "children"), Input("active-page", "data"))
def render_page(page_id):
    sidebar = build_sidebar(page_id)
    module = PAGE_MODULES.get(page_id, m01_overview)
    try:
        content = module.layout()
    except Exception as e:
        content = html.Div([html.H3("Error", style={"color": "#ef4444"}), html.P(str(e))])
    return sidebar, content

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
