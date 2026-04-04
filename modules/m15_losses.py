"""Module 15 — Post-Harvest Loss Tracker"""
from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    ls = losses()

    total_loss_val = ls["loss_value_usd"].sum()
    total_loss_tons = ls["loss_tons"].sum()
    avg_loss_pct = ls["loss_pct"].mean()
    recoverable_val = ls[ls["recoverable"]==True]["loss_value_usd"].sum()

    # Loss by cause — treemap
    by_cause = ls.groupby("loss_cause").agg(
        total_tons=("loss_tons","sum"),
        total_value=("loss_value_usd","sum"),
        avg_pct=("loss_pct","mean"),
    ).reset_index().sort_values("total_value", ascending=False)

    fig_treemap = go.Figure(go.Treemap(
        labels=by_cause["loss_cause"],
        parents=[""] * len(by_cause),
        values=by_cause["total_value"],
        customdata=by_cause[["avg_pct","total_tons"]].values,
        hovertemplate="<b>%{label}</b><br>Value Lost: $%{value:,.0f}<br>Avg Loss: %{customdata[0]:.1f}%<br>Tons: %{customdata[1]:.0f}<extra></extra>",
        marker=dict(
            colorscale=[[0,"#052e16"],[0.4,"#f59e0b"],[1,"#ef4444"]],
            colors=by_cause["total_value"],
            showscale=False,
        ),
        texttemplate="<b>%{label}</b><br>$%{value:,.0f}",
        textfont=dict(color="#f0fdf4", size=12),
    ))
    apply_theme(fig_treemap, 320)
    fig_treemap.update_layout(
        title=dict(text="Loss Value by Cause — Treemap", font=dict(color="#86efac",size=13)),
        margin=dict(l=0,r=0,t=40,b=0),
    )

    # Loss by crop
    by_crop = ls.groupby("crop")["loss_value_usd"].sum().reset_index().sort_values("loss_value_usd", ascending=True)
    fig_crop = go.Figure(go.Bar(
        x=by_crop["loss_value_usd"], y=by_crop["crop"],
        orientation="h",
        marker=dict(color=by_crop["loss_value_usd"], colorscale=[[0,"#1a2e1a"],[1,"#ef4444"]]),
        text=[fmt_usd(v) for v in by_crop["loss_value_usd"]],
        textfont=dict(color="#f0fdf4", size=10),
    ))
    apply_theme(fig_crop, 280)
    fig_crop.update_layout(title=dict(text="Loss Value by Crop", font=dict(color="#86efac",size=13)))

    # Loss by farm (top worst)
    by_farm = ls.groupby("farm_name").agg(
        total_loss=("loss_value_usd","sum"),
        avg_pct=("loss_pct","mean"),
        worst_cause=("loss_cause", lambda x: x.mode()[0] if len(x) > 0 else "N/A"),
    ).reset_index().sort_values("total_loss", ascending=False)

    fig_farm = go.Figure(go.Bar(
        x=by_farm["farm_name"], y=by_farm["total_loss"],
        marker=dict(color=RED, opacity=0.8),
        text=[fmt_usd(v) for v in by_farm["total_loss"]],
        textfont=dict(color="#f0fdf4", size=10),
    ))
    apply_theme(fig_farm, 260)
    fig_farm.update_layout(title=dict(text="Total Post-Harvest Loss by Farm", font=dict(color="#86efac",size=13)), xaxis_tickangle=-25)

    # Season trend
    by_season = ls.groupby("season")["loss_value_usd"].sum().reset_index()
    fig_season = go.Figure(go.Bar(
        x=by_season["season"], y=by_season["loss_value_usd"],
        marker=dict(color=[AMBER, RED, AMBER]),
        text=[fmt_usd(v) for v in by_season["loss_value_usd"]],
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_season, 240)
    fig_season.update_layout(title=dict(text="Loss by Season", font=dict(color="#86efac",size=13)))

    # Intervention recommendations table
    rows = []
    for _, row in by_farm.head(12).iterrows():
        rows.append(html.Tr([
            html.Td(row["farm_name"][:22], style={"color":"#f0fdf4","fontSize":"0.82rem","fontWeight":"500","padding":"9px 6px"}),
            html.Td(fmt_usd(row["total_loss"]), style={"color":RED,"fontSize":"0.82rem","fontWeight":"700","padding":"9px 6px"}),
            html.Td(f"{row['avg_pct']:.1f}%", style={"color":RED if row["avg_pct"]>8 else AMBER,"fontSize":"0.82rem","fontWeight":"600","padding":"9px 6px"}),
            html.Td(row["worst_cause"], style={"color":AMBER,"fontSize":"0.8rem","padding":"9px 6px"}),
            html.Td("Cold storage upgrade / Fumigation" if "Storage" in row["worst_cause"] else
                    "Pest control programme" if "Pest" in row["worst_cause"] else
                    "Improved packaging" if "Transport" in row["worst_cause"] else
                    "Security enhancement" if "Theft" in row["worst_cause"] else
                    "Re-grading protocol review",
                    style={"color":"#6b7280","fontSize":"0.78rem","padding":"9px 6px"}),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px 6px","letterSpacing":"0.06em"})
                             for h in ["Farm","Total Loss Value","Avg Loss %","Primary Cause","Recommended Intervention"]])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    return html.Div([
        page_header("Post-Harvest Loss Tracker", "Spoilage · Theft · Pest damage · Transport loss · Grading downgrades"),
        html.Div([
            kpi(fmt_usd(total_loss_val), "Total Loss Value", "All farms, all seasons", False, RED),
            kpi(fmt_tons(total_loss_tons), "Total Tons Lost", None, False, AMBER),
            kpi(f"{avg_loss_pct:.1f}%", "Avg Loss Rate", "Below 5% is target", False, RED),
            kpi(fmt_usd(recoverable_val), "Recoverable Losses", "With intervention", True, GREEN),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"14px","marginBottom":"24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_treemap, config={"displayModeBar":False})], {"flex":"1.3"}),
            card([dcc.Graph(figure=fig_crop, config={"displayModeBar":False})], {"flex":"1"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
        html.Div([
            card([dcc.Graph(figure=fig_farm, config={"displayModeBar":False})], {"flex":"1.5"}),
            card([dcc.Graph(figure=fig_season, config={"displayModeBar":False})], {"flex":"1"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),
        card([
            html.Div("💔  Loss Analysis & Intervention Recommendations", style={"color":RED,"fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            html.Div(table, style={"overflowX":"auto"}),
        ]),
    ])

def register_callbacks(app): pass
