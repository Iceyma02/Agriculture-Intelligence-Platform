"""Module 16 — Agri-Economic Watch"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import economic, weather
from utils.helpers import GREEN, AMBER, RED, LIME, BLUE, PURPLE, apply_theme, page_header, card, kpi, add_export_section, create_empty_chart

def layout():
    ec = economic()
    wt = weather()
    
    export_section = add_export_section({
        "Economic_Data": ec,
        "Weather_Data": wt
    })
    
    if ec.empty:
        return html.Div([
            export_section,
            page_header("Agri-Economic Watch", "Rainfall · Drought index · Fuel · Electricity · Global commodity prices · FX"),
            card([html.Div("⚠️ No economic data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])

    latest = ec.iloc[-1]
    ec_sorted = ec.sort_values("date")

    # Rainfall trend
    if "month" in ec.columns and "rainfall_mm" in ec.columns:
        monthly_rain = ec.groupby("month")["rainfall_mm"].mean().reset_index()
        fig_rain = go.Figure()
        fig_rain.add_trace(go.Bar(x=monthly_rain["month"], y=monthly_rain["rainfall_mm"], marker=dict(color=monthly_rain["rainfall_mm"], colorscale=[[0, "#7f1d1d"], [0.3, "#f59e0b"], [1, "#1d4ed8"]]), name="Rainfall"))
        fig_rain.add_hline(y=60, line=dict(color=AMBER, dash="dot", width=1.5), annotation_text="Minimum threshold")
        apply_theme(fig_rain, 260)
        fig_rain.update_layout(title=dict(text="Average Monthly Rainfall (mm)", font=dict(color="#86efac", size=13)), xaxis_tickangle=-30)
    else:
        fig_rain = create_empty_chart("No rainfall data available", "Monthly Rainfall")

    # Fuel price trend
    if "fuel_price_usd_l" in ec.columns:
        fig_fuel = go.Figure(go.Scatter(x=ec_sorted["date"], y=ec_sorted["fuel_price_usd_l"], mode="lines", line=dict(color=AMBER, width=2), fill="tozeroy", fillcolor="rgba(245,158,11,0.07)"))
        apply_theme(fig_fuel, 240)
        fig_fuel.update_layout(title=dict(text="Fuel Price Trend (USD/litre)", font=dict(color="#86efac", size=13)), yaxis=dict(title="USD/L"))
    else:
        fig_fuel = create_empty_chart("No fuel price data", "Fuel Price Trend")

    # Global commodity prices
    fig_global = go.Figure()
    for col, label, color in [("global_maize_usd_ton", "Maize", GREEN), ("global_wheat_usd_ton", "Wheat", AMBER), ("global_soya_usd_ton", "Soya", BLUE)]:
        if col in ec.columns:
            fig_global.add_trace(go.Scatter(x=ec_sorted["date"], y=ec_sorted[col], mode="lines", name=label, line=dict(color=color, width=2)))
    apply_theme(fig_global, 280)
    fig_global.update_layout(title=dict(text="Global Commodity Prices (USD/ton)", font=dict(color="#86efac", size=13)))

    # Electricity availability
    if "month" in ec.columns and "electricity_availability_pct" in ec.columns:
        monthly_ec = ec.groupby("month").agg(electricity=("electricity_availability_pct", "mean"), drought=("drought_index", "mean") if "drought_index" in ec.columns else ("electricity_availability_pct", "mean")).reset_index()
        fig_elec = go.Figure()
        fig_elec.add_trace(go.Scatter(x=monthly_ec["month"], y=monthly_ec["electricity"], mode="lines+markers", name="Electricity %", line=dict(color=LIME, width=2), marker=dict(size=6)))
        fig_elec.add_hline(y=70, line=dict(color=RED, dash="dot", width=1.5), annotation_text="Min for irrigation pumps")
        apply_theme(fig_elec, 240)
        fig_elec.update_layout(title=dict(text="Electricity Grid Availability % (irrigation impact)", font=dict(color="#86efac", size=13)), xaxis_tickangle=-30)
    else:
        fig_elec = create_empty_chart("No electricity data", "Grid Availability")

    # Drought index
    if "month" in ec.columns and "drought_index" in ec.columns:
        monthly_ec = ec.groupby("month")["drought_index"].mean().reset_index()
        fig_drought = go.Figure(go.Bar(x=monthly_ec["month"], y=monthly_ec["drought_index"], marker=dict(color=monthly_ec["drought_index"], colorscale=[[0, "#052e16"], [0.5, "#f59e0b"], [1, "#ef4444"]])))
        apply_theme(fig_drought, 240)
        fig_drought.update_layout(title=dict(text="Drought Index by Month (higher = drier)", font=dict(color="#86efac", size=13)), xaxis_tickangle=-30)
    else:
        fig_drought = create_empty_chart("No drought data", "Drought Index")

    # Exchange rate
    if "usd_zwg_rate" in ec.columns:
        fig_fx = go.Figure(go.Scatter(x=ec_sorted["date"], y=ec_sorted["usd_zwg_rate"], mode="lines", line=dict(color=PURPLE, width=2), fill="tozeroy", fillcolor="rgba(139,92,246,0.07)"))
        apply_theme(fig_fx, 240)
        fig_fx.update_layout(title=dict(text="USD/ZWG Exchange Rate", font=dict(color="#86efac", size=13)))
    else:
        fig_fx = create_empty_chart("No FX data", "Exchange Rate")

    # El Nino alerts
    el_nino_months = ec[ec["el_nino_alert"] == True] if "el_nino_alert" in ec.columns else pd.DataFrame()
    el_nino_count = len(el_nino_months["month"].unique()) if not el_nino_months.empty and "month" in el_nino_months.columns else 0

    # Weather station table
    if not wt.empty and "date" in wt.columns:
        latest_weather = wt[wt["date"] == wt["date"].max()]
        rows = []
        for _, row in latest_weather.iterrows():
            rows.append(html.Tr([
                html.Td(row["station"], style={"color": "#f0fdf4", "fontSize": "0.82rem", "fontWeight": "500", "padding": "9px 6px"}),
                html.Td(row["province"], style={"color": "#6b7280", "fontSize": "0.78rem", "padding": "9px 6px"}),
                html.Td(f"{row['rainfall_mm']} mm", style={"color": BLUE, "fontSize": "0.8rem", "padding": "9px 6px"}),
                html.Td(f"{row['max_temp_c']}°C / {row['min_temp_c']}°C", style={"color": AMBER, "fontSize": "0.8rem", "padding": "9px 6px"}),
                html.Td(f"{row['humidity_pct']:.0f}%", style={"color": "#86efac", "fontSize": "0.8rem", "padding": "9px 6px"}),
                html.Td(f"{row['wind_speed_kmh']:.0f} km/h", style={"color": "#6b7280", "fontSize": "0.78rem", "padding": "9px 6px"}),
            ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))

        weather_table = html.Table([
            html.Thead(html.Tr([html.Th(h, style={"color": "#4ade80", "fontSize": "0.70rem", "fontWeight": "600", "textTransform": "uppercase", "padding": "8px 6px"}) for h in ["Weather Station", "Province", "Rainfall", "Temp (Max/Min)", "Humidity", "Wind"]])),
            html.Tbody(rows),
        ], style={"width": "100%", "borderCollapse": "collapse"})
    else:
        weather_table = html.Div("No weather data available")

    return html.Div([
        export_section,
        page_header("Agri-Economic Watch", "Rainfall · Drought index · Fuel · Electricity · Global commodity prices · FX"),
        html.Div([
            kpi(f"{latest.get('rainfall_mm', 0):.0f} mm", "Latest Rainfall", "Today's reading", True, BLUE),
            kpi(f"{latest.get('drought_index', 0):.0f}", "Drought Index", "Higher = drier", latest.get('drought_index', 0) < 40, RED if latest.get('drought_index', 0) > 60 else AMBER),
            kpi(f"${latest.get('fuel_price_usd_l', 0):.3f}/L", "Fuel Price", None, False, AMBER),
            kpi(f"{latest.get('electricity_availability_pct', 0):.0f}%", "Grid Availability", "Irrigation impact", latest.get('electricity_availability_pct', 0) > 70, LIME),
            kpi(f"{latest.get('usd_zwg_rate', 0):.2f}", "USD/ZWG Rate", None, False, PURPLE),
            kpi(str(el_nino_count), "El Niño Alert Months", "Low rainfall months", False, RED),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(6,1fr)", "gap": "14px", "marginBottom": "24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_rain, config={"displayModeBar": False})], {"flex": "1"}),
            card([dcc.Graph(figure=fig_drought, config={"displayModeBar": False})], {"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),
        card([dcc.Graph(figure=fig_global, config={"displayModeBar": False})], {"marginBottom": "16px"}),
        html.Div([
            card([dcc.Graph(figure=fig_fuel, config={"displayModeBar": False})], {"flex": "1"}),
            card([dcc.Graph(figure=fig_elec, config={"displayModeBar": False})], {"flex": "1"}),
            card([dcc.Graph(figure=fig_fx, config={"displayModeBar": False})], {"flex": "1"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),
        card([html.Div("🌧️ Live Weather Station Data", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}), html.Div(weather_table, style={"overflowX": "auto"})]),
    ])

def register_callbacks(app): pass
