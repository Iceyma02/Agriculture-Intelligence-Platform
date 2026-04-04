"""Module 14 — Farm Labour Intelligence"""
from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    lb = labour()

    total_perm = lb["permanent_workers"].sum()
    total_seasonal = lb["seasonal_workers"].sum()
    total_cost = lb["labour_cost_usd"].sum()
    avg_productivity = lb["productivity_score"].mean()

    # Workforce composition over time (stacked area)
    monthly_totals = lb.groupby("month_label").agg(
        permanent=("permanent_workers","mean"),
        seasonal=("seasonal_workers","mean"),
    ).reset_index()

    fig_workforce = go.Figure()
    fig_workforce.add_trace(go.Scatter(
        x=monthly_totals["month_label"], y=monthly_totals["permanent"],
        mode="lines", fill="tozeroy", name="Permanent",
        line=dict(color=GREEN, width=2), fillcolor="rgba(34,197,94,0.15)",
    ))
    fig_workforce.add_trace(go.Scatter(
        x=monthly_totals["month_label"], y=monthly_totals["seasonal"],
        mode="lines", fill="tonexty", name="Seasonal",
        line=dict(color=AMBER, width=2), fillcolor="rgba(245,158,11,0.12)",
    ))
    apply_theme(fig_workforce, 280)
    fig_workforce.update_layout(title=dict(text="Workforce Composition — Permanent vs Seasonal", font=dict(color="#86efac",size=13)))

    # Labour cost by farm
    by_farm = lb.groupby("farm_name").agg(
        cost=("labour_cost_usd","sum"),
        cost_ha=("cost_per_ha","mean"),
        productivity=("productivity_score","mean"),
        overtime=("overtime_hours","sum"),
    ).reset_index().sort_values("cost", ascending=False)

    fig_cost = go.Figure(go.Bar(
        x=by_farm["farm_name"], y=by_farm["cost"],
        marker=dict(color=by_farm["cost"], colorscale=[[0,"#1a2e1a"],[1,"#22c55e"]]),
        text=[fmt_usd(v) for v in by_farm["cost"]],
        textfont=dict(color="#f0fdf4", size=10),
    ))
    apply_theme(fig_cost, 280)
    fig_cost.update_layout(title=dict(text="Total Labour Cost by Farm (12 months)", font=dict(color="#86efac",size=13)), xaxis_tickangle=-25)

    # Productivity vs cost per ha scatter
    fig_prod = go.Figure(go.Scatter(
        x=by_farm["cost_ha"], y=by_farm["productivity"],
        mode="markers+text",
        marker=dict(size=15, color=by_farm["productivity"], colorscale=[[0,"#7f1d1d"],[1,"#22c55e"]], showscale=False),
        text=by_farm["farm_name"].str[:12],
        textposition="top center",
        textfont=dict(color="#86efac", size=9),
    ))
    apply_theme(fig_prod, 280)
    fig_prod.update_layout(
        title=dict(text="Labour Cost/ha vs Productivity Score", font=dict(color="#86efac",size=13)),
        xaxis=dict(title="Cost per Ha (USD)", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)"),
        yaxis=dict(title="Productivity Score", tickfont=dict(color="#6b7280"), gridcolor="rgba(34,197,94,0.07)"),
    )

    # Overtime heatmap by farm and season
    peak_data = lb.groupby(["farm_name","season_type"])["overtime_hours"].mean().reset_index()
    farms_list = lb["farm_name"].unique()[:8]
    seasons = ["Peak","Off-Peak"]
    z = []
    for fn in farms_list:
        row_vals = []
        for s in seasons:
            val = peak_data[(peak_data["farm_name"]==fn)&(peak_data["season_type"]==s)]["overtime_hours"].mean()
            row_vals.append(round(float(val), 0) if val == val else 0)
        z.append(row_vals)

    fig_overtime = go.Figure(go.Heatmap(
        z=z, x=seasons, y=[f[:20] for f in farms_list],
        colorscale=[[0,"#052e16"],[0.5,"#f59e0b"],[1,"#ef4444"]],
        text=z, texttemplate="%{text:.0f}h",
        textfont=dict(color="#f0fdf4", size=11),
    ))
    apply_theme(fig_overtime, 300)
    fig_overtime.update_layout(title=dict(text="Avg Overtime Hours by Farm & Season", font=dict(color="#86efac",size=13)))

    # Summary table
    rows = []
    for _, row in by_farm.iterrows():
        prod_color = GREEN if row["productivity"] >= 85 else AMBER if row["productivity"] >= 70 else RED
        rows.append(html.Tr([
            html.Td(row["farm_name"][:22], style={"color":"#f0fdf4","fontSize":"0.82rem","fontWeight":"500","padding":"9px 6px"}),
            html.Td(fmt_usd(row["cost"]), style={"color":AMBER,"fontSize":"0.8rem","padding":"9px 6px"}),
            html.Td(f"${row['cost_ha']:.0f}/ha", style={"color":"#86efac","fontSize":"0.8rem","padding":"9px 6px"}),
            html.Td(f"{row['productivity']:.1f}", style={"color":prod_color,"fontSize":"0.8rem","fontWeight":"700","padding":"9px 6px"}),
            html.Td(f"{row['overtime']:.0f}h", style={"color":RED if row["overtime"]>1000 else "#f0fdf4","fontSize":"0.8rem","padding":"9px 6px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px 6px","letterSpacing":"0.06em"})
                             for h in ["Farm","Total Labour Cost","Cost / Ha","Productivity","Overtime Hours"]])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    return html.Div([
        page_header("Farm Labour Intelligence", "Workforce composition · Labour costs · Productivity · Seasonal tracking"),
        html.Div([
            kpi(f"{int(total_perm):,}", "Avg Permanent Workers", "Across all farms", True, GREEN),
            kpi(f"{int(total_seasonal):,}", "Avg Seasonal Workers", "Peak season", True, AMBER),
            kpi(fmt_usd(total_cost), "Total Labour Cost", "12-month rolling", False, RED),
            kpi(f"{avg_productivity:.1f}", "Avg Productivity Score", "Out of 100", True, LIME),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"14px","marginBottom":"24px"}),
        card([dcc.Graph(figure=fig_workforce, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        html.Div([
            card([dcc.Graph(figure=fig_cost, config={"displayModeBar":False})]),
            card([dcc.Graph(figure=fig_prod, config={"displayModeBar":False})]),
        ], style={"display":"grid","gridTemplateColumns":"1.2fr 1fr","gap":"16px","marginBottom":"16px"}),
        html.Div([
            card([dcc.Graph(figure=fig_overtime, config={"displayModeBar":False})], {"flex":"1"}),
            card([
                html.Div("👨‍🌾  Labour Summary by Farm", style={"color":"#86efac","fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
                html.Div(table, style={"overflowX":"auto"}),
            ], {"flex":"1.2"}),
        ], style={"display":"flex","gap":"16px"}),
    ])

def register_callbacks(app): pass
