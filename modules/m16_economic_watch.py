"""Module 16 — Agri-Economic Watch"""
from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    ec = economic()
    wt = weather()

    # Latest values
    latest = ec.iloc[-1]
    latest_date = ec["date"].max()

    # Rainfall trend
    monthly_rain = ec.groupby("month")["rainfall_mm"].mean().reset_index()
    fig_rain = go.Figure()
    fig_rain.add_trace(go.Bar(
        x=monthly_rain["month"], y=monthly_rain["rainfall_mm"],
        marker=dict(
            color=monthly_rain["rainfall_mm"],
            colorscale=[[0,"#7f1d1d"],[0.3,"#f59e0b"],[1,"#1d4ed8"]],
        ),
        name="Rainfall",
    ))
    fig_rain.add_hline(y=60, line=dict(color=AMBER, dash="dot", width=1.5), annotation_text="Minimum threshold")
    apply_theme(fig_rain, 260)
    fig_rain.update_layout(title=dict(text="Average Monthly Rainfall (mm)", font=dict(color="#86efac",size=13)), xaxis_tickangle=-30)

    # Fuel price trend
    ec_sorted = ec.sort_values("date")
    fig_fuel = go.Figure(go.Scatter(
        x=ec_sorted["date"], y=ec_sorted["fuel_price_usd_l"],
        mode="lines", line=dict(color=AMBER, width=2),
        fill="tozeroy", fillcolor="rgba(245,158,11,0.07)",
    ))
    apply_theme(fig_fuel, 240)
    fig_fuel.update_layout(title=dict(text="Fuel Price Trend (USD/litre)", font=dict(color="#86efac",size=13)),
                            yaxis=dict(title="USD/L", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)"))

    # Global commodity prices
    fig_global = go.Figure()
    for col, label, color in [("global_maize_usd_ton","Maize",GREEN),("global_wheat_usd_ton","Wheat",AMBER),("global_soya_usd_ton","Soya",BLUE)]:
        fig_global.add_trace(go.Scatter(
            x=ec_sorted["date"], y=ec_sorted[col],
            mode="lines", name=label, line=dict(color=color, width=2),
        ))
    apply_theme(fig_global, 280)
    fig_global.update_layout(title=dict(text="Global Commodity Prices (USD/ton)", font=dict(color="#86efac",size=13)))

    # Electricity availability
    monthly_ec = ec.groupby("month").agg(
        electricity=("electricity_availability_pct","mean"),
        drought=("drought_index","mean"),
    ).reset_index()

    fig_elec = go.Figure()
    fig_elec.add_trace(go.Scatter(
        x=monthly_ec["month"], y=monthly_ec["electricity"],
        mode="lines+markers", name="Electricity %",
        line=dict(color=LIME, width=2),
        marker=dict(size=6),
    ))
    fig_elec.add_hline(y=70, line=dict(color=RED, dash="dot", width=1.5), annotation_text="Min for irrigation pumps")
    apply_theme(fig_elec, 240)
    fig_elec.update_layout(title=dict(text="Electricity Grid Availability % (irrigation impact)", font=dict(color="#86efac",size=13)), xaxis_tickangle=-30)

    # Drought index
    fig_drought = go.Figure(go.Bar(
        x=monthly_ec["month"], y=monthly_ec["drought"],
        marker=dict(color=monthly_ec["drought"], colorscale=[[0,"#052e16"],[0.5,"#f59e0b"],[1,"#ef4444"]]),
    ))
    apply_theme(fig_drought, 240)
    fig_drought.update_layout(title=dict(text="Drought Index by Month (higher = drier)", font=dict(color="#86efac",size=13)), xaxis_tickangle=-30)

    # El Nino alerts
    el_nino_months = ec[ec["el_nino_alert"]==True]
    el_nino_count = len(el_nino_months["month"].unique())

    # ZWG exchange rate
    fig_fx = go.Figure(go.Scatter(
        x=ec_sorted["date"], y=ec_sorted["usd_zwg_rate"],
        mode="lines", line=dict(color=PURPLE, width=2),
        fill="tozeroy", fillcolor="rgba(139,92,246,0.07)",
    ))
    apply_theme(fig_fx, 240)
    fig_fx.update_layout(title=dict(text="USD/ZWG Exchange Rate", font=dict(color="#86efac",size=13)))

    # Weather station table
    latest_weather = wt[wt["date"] == wt["date"].max()]
    rows = []
    for _, row in latest_weather.iterrows():
        rows.append(html.Tr([
            html.Td(row["station"], style={"color":"#f0fdf4","fontSize":"0.82rem","fontWeight":"500","padding":"9px 6px"}),
            html.Td(row["province"], style={"color":"#6b7280","fontSize":"0.78rem","padding":"9px 6px"}),
            html.Td(f"{row['rainfall_mm']} mm", style={"color":BLUE,"fontSize":"0.8rem","padding":"9px 6px"}),
            html.Td(f"{row['max_temp_c']}°C / {row['min_temp_c']}°C", style={"color":AMBER,"fontSize":"0.8rem","padding":"9px 6px"}),
            html.Td(f"{row['humidity_pct']:.0f}%", style={"color":"#86efac","fontSize":"0.8rem","padding":"9px 6px"}),
            html.Td(f"{row['wind_speed_kmh']:.0f} km/h", style={"color":"#6b7280","fontSize":"0.78rem","padding":"9px 6px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px 6px","letterSpacing":"0.06em"})
                             for h in ["Weather Station","Province","Rainfall","Temp (Max/Min)","Humidity","Wind"]])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    return html.Div([
        page_header("Agri-Economic Watch", "Rainfall · Drought index · Fuel · Electricity · Global commodity prices · FX"),
        html.Div([
            kpi(f"{latest['rainfall_mm']:.0f} mm", "Latest Rainfall", "Today's reading", True, BLUE),
            kpi(f"{latest['drought_index']:.0f}", "Drought Index", "Higher = drier", latest["drought_index"] < 40, RED if latest["drought_index"] > 60 else AMBER),
            kpi(f"${latest['fuel_price_usd_l']:.3f}/L", "Fuel Price", None, False, AMBER),
            kpi(f"{latest['electricity_availability_pct']:.0f}%", "Grid Availability", "Irrigation impact", latest["electricity_availability_pct"] > 70, LIME),
            kpi(f"{latest['usd_zwg_rate']:.2f}", "USD/ZWG Rate", None, False, PURPLE),
            kpi(str(el_nino_count), "El Niño Alert Months", "Low rainfall months", False, RED),
        ], style={"display":"grid","gridTemplateColumns":"repeat(6,1fr)","gap":"14px","marginBottom":"24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_rain, config={"displayModeBar":False})], {"flex":"1"}),
            card([dcc.Graph(figure=fig_drought, config={"displayModeBar":False})], {"flex":"1"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
        card([dcc.Graph(figure=fig_global, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        html.Div([
            card([dcc.Graph(figure=fig_fuel, config={"displayModeBar":False})], {"flex":"1"}),
            card([dcc.Graph(figure=fig_elec, config={"displayModeBar":False})], {"flex":"1"}),
            card([dcc.Graph(figure=fig_fx, config={"displayModeBar":False})], {"flex":"1"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
        card([
            html.Div("🌧️  Live Weather Station Data", style={"color":"#86efac","fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            html.Div(table, style={"overflowX":"auto"}),
        ]),
    ])

def register_callbacks(app): pass
