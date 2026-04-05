"""
AgriIQ — Agriculture Intelligence Platform
Main application entry point
"""

import dash
from dash import dcc, html, Input, Output, State, callback_context  # ← Added State here
import dash_bootstrap_components as dbc
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all modules
from modules import (
    m01_overview, m02_farm_map, m03_performance, m04_pnl,
    m05_inventory, m06_harvest_movement, m07_yield_forecast, m08_reorder,
    m09_supply_chain, m10_supplier_credit, m11_marketing_roi, m12_market_prices,
    m13_buyer_satisfaction, m14_labour, m15_losses, m16_economic_watch, m17_board_reports
)

# Create Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap",
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    title="AgriIQ — Agriculture Intelligence Platform",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1, maximum-scale=1, user-scalable=yes"},
        {"name": "description", "content": "Agriculture Intelligence Platform - Farm Management Dashboard"}
    ],
    use_pages=False
)

server = app.server

# ── Design tokens ─────────────────────────────────────────────────────────────
CUSTOM_CSS = """
:root {
    --bg-primary: #0a0f0a;
    --bg-card: #111811;
    --bg-card2: #151e15;
    --accent-green: #22c55e;
    --accent-lime: #a3e635;
    --accent-amber: #f59e0b;
    --accent-red: #ef4444;
    --accent-blue: #38bdf8;
    --text-primary: #f0fdf4;
    --text-secondary: #86efac;
    --text-muted: #4ade80;
    --border: rgba(34,197,94,0.15);
    --border-strong: rgba(34,197,94,0.35);
    --font-display: 'Playfair Display', serif;
    --font-body: 'DM Sans', sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg-primary); color: var(--text-primary); font-family: var(--font-body); overflow-x: hidden; }

/* Sidebar */
.sidebar {
    position: fixed; top: 0; left: 0; height: 100vh; width: 260px;
    background: var(--bg-card); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; z-index: 1000;
    overflow-y: auto; overflow-x: hidden;
    transition: transform 0.3s ease;
}
.sidebar-logo {
    padding: 24px 20px 16px;
    border-bottom: 1px solid var(--border);
}
.sidebar-logo h1 {
    font-family: var(--font-display); color: var(--accent-green);
    font-size: 1.6rem; font-weight: 800; line-height: 1;
}
.sidebar-logo p { color: var(--text-muted); font-size: 0.72rem; margin-top: 4px; letter-spacing: 0.08em; text-transform: uppercase; }

.nav-section { padding: 12px 0; }
.nav-section-label {
    color: var(--text-muted); font-size: 0.65rem; font-weight: 600;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 6px 20px; margin-bottom: 2px;
}
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 20px; cursor: pointer; border: none; background: none;
    color: #6b7280; font-family: var(--font-body); font-size: 0.82rem;
    width: 100%; text-align: left; transition: all 0.2s;
    border-left: 3px solid transparent;
}
.nav-item:hover { color: var(--text-primary); background: rgba(34,197,94,0.06); }
.nav-item.active { color: var(--accent-green); background: rgba(34,197,94,0.1); border-left-color: var(--accent-green); }
.nav-item i { width: 20px; text-align: center; font-size: 0.9rem; }

/* Main content */
.main-content { margin-left: 260px; min-height: 100vh; padding: 28px 32px; transition: margin-left 0.3s ease; }

/* KPI cards */
.kpi-card {
    background: var(--bg-card2); border: 1px solid var(--border);
    border-radius: 10px; padding: 18px 20px;
    transition: all 0.3s ease;
}
.kpi-card:hover { transform: translateY(-2px); border-color: var(--border-strong); }
.kpi-value { font-family: var(--font-display); font-size: 1.9rem; font-weight: 700; color: var(--text-primary); line-height: 1; }
.kpi-label { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 6px; }
.kpi-delta { font-size: 0.78rem; margin-top: 6px; }
.kpi-delta.up { color: var(--accent-green); }
.kpi-delta.down { color: var(--accent-red); }

/* Page headers */
.page-header { margin-bottom: 28px; }
.page-title { font-family: var(--font-display); font-size: 2rem; font-weight: 700; color: var(--text-primary); }
.page-subtitle { color: var(--text-muted); font-size: 0.85rem; margin-top: 4px; }

/* Status badges */
.badge-ok { background: rgba(34,197,94,0.15); color: #22c55e; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-low { background: rgba(245,158,11,0.15); color: #f59e0b; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }
.badge-critical { background: rgba(239,68,68,0.15); color: #ef4444; padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 600; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #22c55e40; border-radius: 3px; }

/* Plotly charts dark override */
.js-plotly-plot .plotly .bg { fill: transparent !important; }
.modebar { display: none !important; }

/* Mobile responsive */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
    }
    .sidebar.open {
        transform: translateX(0);
    }
    .main-content {
        margin-left: 0 !important;
        padding: 15px !important;
    }
    .kpi-card {
        padding: 12px;
    }
    .kpi-value {
        font-size: 1.3rem;
    }
    .page-title {
        font-size: 1.5rem;
    }
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.fade-in {
    animation: fadeIn 0.5s ease;
}
"""

# Inject CSS into the app's HTML head
app.index_string = f'''
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
            {CUSTOM_CSS}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
'''

# ── Nav structure ─────────────────────────────────────────────────────────────
NAV_ITEMS = [
    {"section": "Overview"},
    {"id": "overview",        "label": "Farm Dashboard",         "icon": "fa-gauge-high"},
    {"id": "farm-map",        "label": "Farm Map",               "icon": "fa-map-location-dot"},
    {"section": "Performance"},
    {"id": "performance",     "label": "Farm Performance",       "icon": "fa-chart-line"},
    {"id": "pnl",             "label": "Farm P&L Engine",        "icon": "fa-coins"},
    {"section": "Operations"},
    {"id": "inventory",       "label": "Inputs & Stock",         "icon": "fa-boxes-stacked"},
    {"id": "harvest-movement","label": "Harvest Movement",       "icon": "fa-truck-moving"},
    {"section": "Forecasting"},
    {"id": "yield-forecast",  "label": "Yield Forecasting",      "icon": "fa-seedling"},
    {"id": "reorder",         "label": "Reorder Optimizer",      "icon": "fa-rotate"},
    {"section": "Supply Chain"},
    {"id": "supply-chain",    "label": "Supply Chain Pipeline",  "icon": "fa-link"},
    {"id": "supplier-credit", "label": "Supplier Credit & Risk", "icon": "fa-credit-card"},
    {"section": "Market"},
    {"id": "marketing-roi",   "label": "Marketing ROI",          "icon": "fa-bullhorn"},
    {"id": "market-prices",   "label": "Market Price Watch",     "icon": "fa-chart-bar"},
    {"section": "People"},
    {"id": "buyer-sat",       "label": "Buyer Satisfaction",     "icon": "fa-star"},
    {"id": "labour",          "label": "Labour Intelligence",    "icon": "fa-users"},
    {"section": "Risk"},
    {"id": "losses",          "label": "Post-Harvest Loss",      "icon": "fa-triangle-exclamation"},
    {"id": "economic-watch",  "label": "Agri-Economic Watch",    "icon": "fa-earth-africa"},
    {"section": "Reporting"},
    {"id": "board-reports",   "label": "Board Reports",          "icon": "fa-file-lines"},
]

def build_sidebar(active_id="overview"):
    children = [
        html.Div([
            html.H1("AgriIQ"),
            html.P("Agriculture Intelligence Platform"),
        ], className="sidebar-logo")
    ]
    nav_children = []
    for item in NAV_ITEMS:
        if "section" in item:
            nav_children.append(html.Div(item["section"], className="nav-section-label"))
        else:
            is_active = item["id"] == active_id
            nav_children.append(
                html.Button(
                    [html.I(className=f"fas {item['icon']}"), item["label"]],
                    id={"type": "nav-btn", "index": item["id"]},
                    className=f"nav-item {'active' if is_active else ''}",
                    n_clicks=0,
                )
            )
    children.append(html.Div(nav_children, className="nav-section"))

    # Footer with version
    children.append(html.Div([
        html.P("© 2026 Anesu Manjengwa", style={"color": "#374151", "fontSize": "0.68rem"}),
        html.P("Version 2.0 | Enterprise", style={"color": "#374151", "fontSize": "0.6rem", "marginTop": "5px"})
    ], style={"marginTop": "auto", "padding": "16px 20px"}))

    return html.Div(children, className="sidebar")

# ── App layout ────────────────────────────────────────────────────────────────
app.layout = html.Div([
    dcc.Store(id="active-page", data="overview"),
    html.Div(id="sidebar-container"),
    html.Div(id="page-content", className="main-content"),
])

# ── Callbacks ─────────────────────────────────────────────────────────────────
PAGE_MODULES = {
    "overview":        m01_overview,
    "farm-map":        m02_farm_map,
    "performance":     m03_performance,
    "pnl":             m04_pnl,
    "inventory":       m05_inventory,
    "harvest-movement":m06_harvest_movement,
    "yield-forecast":  m07_yield_forecast,
    "reorder":         m08_reorder,
    "supply-chain":    m09_supply_chain,
    "supplier-credit": m10_supplier_credit,
    "marketing-roi":   m11_marketing_roi,
    "market-prices":   m12_market_prices,
    "buyer-sat":       m13_buyer_satisfaction,
    "labour":          m14_labour,
    "losses":          m15_losses,
    "economic-watch":  m16_economic_watch,
    "board-reports":   m17_board_reports,
}

@app.callback(
    Output("active-page", "data"),
    Input({"type": "nav-btn", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def set_active_page(n_clicks_list):
    ctx = callback_context
    if not ctx.triggered:
        return "overview"
    triggered_id = ctx.triggered[0]["prop_id"]
    import json as _json
    id_dict = _json.loads(triggered_id.split(".")[0])
    return id_dict["index"]

@app.callback(
    Output("sidebar-container", "children"),
    Output("page-content", "children"),
    Input("active-page", "data"),
)
def render_page(page_id):
    sidebar = build_sidebar(page_id)
    module = PAGE_MODULES.get(page_id, m01_overview)
    try:
        content = module.layout()
    except Exception as e:
        content = html.Div([
            html.H3("Error Loading Page", style={"color": "#ef4444"}),
            html.P(f"Error: {str(e)}", style={"color": "#86efac"}),
        ], className="fade-in")
    return sidebar, content

# Register all module callbacks
for module in PAGE_MODULES.values():
    if hasattr(module, "register_callbacks"):
        try:
            module.register_callbacks(app)
        except Exception as e:
            print(f"Error registering callbacks for module: {e}")

# Run the app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
