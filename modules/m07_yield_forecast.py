"""Module 07 — Crop Yield Forecasting"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import forecast
from utils import GREEN, AMBER, BLUE, LIME, RED, apply_theme, page_header, card, kpi

def layout():
    fc = forecast()
    
    if fc.empty:
        return html.Div([
            page_header("Crop Yield Forecasting", "ML-powered 30-90 day yield predictions · Weather integrated · Risk alerts"),
            card([html.Div("⚠️ No forecast data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])

    farm_name = "Mazowe Valley Farm"
    farm_data = fc[fc["farm_name"] == farm_name].sort_values("date") if farm_name in fc["farm_name"].values else fc.sort_values("date")

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
    if not predicted.empty:
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

    if not actual.empty and "rainfall_mm" in actual.columns:
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
    else:
        fig_rain = go.Figure()

    upcoming = fc[fc["forecast_yield_tons_ha"].notna()].groupby("farm_name").agg(
        avg_forecast=("forecast_yield_tons_ha","mean"),
        avg_confidence=("confidence_pct","mean"),
    ).reset_index().sort_values("avg_forecast", ascending=False)

    rows = []
    for _, row in upcoming.iterrows():
        rows.append(html.Tr([
            html.Td(row["farm_name"][:24], style={"color":"#f0fdf4","fontSize":"0.82rem","padding":"9px 6px"}),
            html.Td(f"{row['avg_forecast']:.2f} t/ha", style={"color":GREEN,"fontSize":"0.82rem","fontWeight":"600","padding":"9px 6px"}),
            html.Td(f"{row['avg_confidence']:.1f}%", style={"color":LIME,"fontSize":"0.82rem","padding":"9px 6px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([
            html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px 6px","letterSpacing":"0.06em"})
            for h in ["Farm","Avg Forecast Yield","Confidence"]
        ])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    avg_conf = fc[fc["confidence_pct"].notna()]["confidence_pct"].mean() if not fc[fc["confidence_pct"].notna()].empty else 0

    return html.Div([
        page_header("Crop Yield Forecasting", "ML-powered 30-90 day yield predictions · Weather integrated · Risk alerts"),
        html.Div([
            kpi(f"{fc[fc['actual_yield_tons_ha'].notna()]['actual_yield_tons_ha'].mean():.2f} t/ha", "Avg Actual Yield", None),
            kpi(f"{fc[fc['forecast_yield_tons_ha'].notna()]['forecast_yield_tons_ha'].mean():.2f} t/ha", "Avg Forecast Yield", "Next 13 weeks", True, AMBER),
            kpi(f"{avg_conf:.1f}%", "Model Confidence", None, True, LIME),
        ], style={"display":"grid","gridTemplateColumns":"repeat(3,1fr)","gap":"14px","marginBottom":"24px"}),
        card([dcc.Graph(figure=fig_forecast, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        card([dcc.Graph(figure=fig_rain, config={"displayModeBar":False})], {"marginBottom":"16px"} if fig_rain.data else {}),
        card([
            html.Div("🤖  Forecast Summary — All Farms", style={"color":"#86efac","fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            html.Div(table, style={"overflowX":"auto"}),
        ]),
    ])

def register_callbacks(app): pass
