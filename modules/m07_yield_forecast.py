"""Module 07 — Crop Yield Forecasting"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    fc = forecast()

    # Select one farm for deep forecast view
    farm_name = "Mazowe Valley Farm"
    farm_data = fc[fc["farm_name"] == farm_name].sort_values("date")

    actual = farm_data[farm_data["actual_yield_tons_ha"].notna()]
    predicted = farm_data[farm_data["forecast_yield_tons_ha"].notna()]

    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(
        x=actual["date"], y=actual["actual_yield_tons_ha"],
        mode="lines", name="Actual Yield",
        line=dict(color=GREEN, width=2.5),
    ))
    fig_forecast.add_trace(go.Scatter(
        x=predicted["date"], y=predicted["forecast_yield_tons_ha"],
        mode="lines", name="Forecast",
        line=dict(color=AMBER, width=2, dash="dot"),
    ))
    # Confidence band
    upper = predicted["forecast_yield_tons_ha"] * 1.08
    lower = predicted["forecast_yield_tons_ha"] * 0.92
    fig_forecast.add_trace(go.Scatter(
        x=list(predicted["date"]) + list(predicted["date"])[::-1],
        y=list(upper) + list(lower)[::-1],
        fill="toself", fillcolor="rgba(245,158,11,0.08)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence Band",
    ))
    apply_theme(fig_forecast, 320)
    fig_forecast.update_layout(title=dict(text=f"Yield Forecast — {farm_name}", font=dict(color="#86efac",size=13)))

    # Rainfall vs yield correlation scatter
    fig_rain = go.Figure(go.Scatter(
        x=actual["rainfall_mm"], y=actual["actual_yield_tons_ha"],
        mode="markers",
        marker=dict(color=BLUE, size=7, opacity=0.7),
    ))
    apply_theme(fig_rain, 280)
    fig_rain.update_layout(
        title=dict(text="Rainfall vs Yield (Correlation)", font=dict(color="#86efac",size=13)),
        xaxis=dict(title="Rainfall (mm)", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)"),
        yaxis=dict(title="Yield (t/ha)", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)"),
    )

    # Pest pressure heatmap
    pest = fc.groupby(["farm_name","pest_pressure"]).size().reset_index(name="weeks")
    farms_list = fc["farm_name"].unique()[:8]
    pressure_levels = ["Low","Medium","High"]
    z_data = []
    y_labels = []
    for fn in farms_list:
        row = []
        for pl in pressure_levels:
            val = pest[(pest["farm_name"]==fn) & (pest["pest_pressure"]==pl)]["weeks"].sum()
            row.append(int(val))
        z_data.append(row)
        y_labels.append(fn[:20])

    fig_pest = go.Figure(go.Heatmap(
        z=z_data, x=pressure_levels, y=y_labels,
        colorscale=[[0,"#052e16"],[0.5,"#f59e0b"],[1,"#ef4444"]],
        text=z_data, texttemplate="%{text}wks",
        textfont=dict(color="#f0fdf4", size=10),
    ))
    apply_theme(fig_pest, 300)
    fig_pest.update_layout(title=dict(text="Pest Pressure by Farm (weeks per level)", font=dict(color="#86efac",size=13)))

    # Summary table: upcoming forecasts
    upcoming = fc[fc["forecast_yield_tons_ha"].notna()].groupby("farm_name").agg(
        avg_forecast=("forecast_yield_tons_ha","mean"),
        avg_confidence=("confidence_pct","mean"),
        high_pest_weeks=("pest_pressure", lambda x: (x=="High").sum()),
    ).reset_index().sort_values("avg_forecast", ascending=False)

    rows = []
    for _, row in upcoming.iterrows():
        rows.append(html.Tr([
            html.Td(row["farm_name"][:24], style={"color":"#f0fdf4","fontSize":"0.82rem","padding":"9px 6px"}),
            html.Td(f"{row['avg_forecast']:.2f} t/ha", style={"color":GREEN,"fontSize":"0.82rem","fontWeight":"600","padding":"9px 6px"}),
            html.Td(f"{row['avg_confidence']:.1f}%", style={"color":LIME,"fontSize":"0.82rem","padding":"9px 6px"}),
            html.Td(str(int(row["high_pest_weeks"])),
                    style={"color":RED if row["high_pest_weeks"]>2 else GREEN,"fontSize":"0.82rem","fontWeight":"600","padding":"9px 6px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px 6px","letterSpacing":"0.06em"})
            for h in ["Farm","Avg Forecast Yield","Confidence","High-Pest Weeks"]
        ])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    avg_conf = fc[fc["confidence_pct"].notna()]["confidence_pct"].mean()

    return html.Div([
        page_header("Crop Yield Forecasting", "ML-powered 30-90 day yield predictions · Weather integrated · Risk alerts"),
        html.Div([
            kpi(f"{fc[fc['actual_yield_tons_ha'].notna()]['actual_yield_tons_ha'].mean():.2f} t/ha", "Avg Actual Yield", None),
            kpi(f"{fc[fc['forecast_yield_tons_ha'].notna()]['forecast_yield_tons_ha'].mean():.2f} t/ha", "Avg Forecast Yield", "Next 13 weeks", True, AMBER),
            kpi(f"{avg_conf:.1f}%", "Model Confidence", None, True, LIME),
            kpi(str(int((fc["pest_pressure"]=="High").sum())), "High Pest Weeks", "Across all farms", False, RED),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"14px","marginBottom":"24px"}),
        card([dcc.Graph(figure=fig_forecast, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        html.Div([
            card([dcc.Graph(figure=fig_rain, config={"displayModeBar":False})]),
            card([dcc.Graph(figure=fig_pest, config={"displayModeBar":False})]),
        ], style={"display":"grid","gridTemplateColumns":"1fr 1.2fr","gap":"16px","marginBottom":"16px"}),
        card([
            html.Div("🤖  Forecast Summary — All Farms", style={"color":"#86efac","fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            html.Div(table, style={"overflowX":"auto"}),
        ]),
    ])

def register_callbacks(app): pass
