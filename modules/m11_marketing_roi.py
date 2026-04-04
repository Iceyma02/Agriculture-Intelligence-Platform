"""Module 11 — Marketing ROI"""
from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    mk = marketing()

    by_camp = mk.groupby("campaign").agg(spend=("spend_usd","sum"), lift=("revenue_lift_usd","sum"),
                                           roi=("roi_pct","mean")).reset_index().sort_values("roi", ascending=False)

    fig_roi = go.Figure()
    fig_roi.add_trace(go.Bar(name="Spend", x=by_camp["campaign"], y=by_camp["spend"], marker_color=BLUE))
    fig_roi.add_trace(go.Bar(name="Revenue Lift", x=by_camp["campaign"], y=by_camp["lift"], marker_color=GREEN))
    fig_roi.update_layout(barmode="group", xaxis_tickangle=-20)
    apply_theme(fig_roi, 300)
    fig_roi.update_layout(title=dict(text="Spend vs Revenue Lift by Campaign", font=dict(color="#86efac",size=13)))

    fig_roi_pct = go.Figure(go.Bar(
        x=by_camp["campaign"], y=by_camp["roi"],
        marker=dict(color=[GREEN if v>0 else RED for v in by_camp["roi"]]),
        text=[f"{v:.0f}%" for v in by_camp["roi"]],
        textfont=dict(color="#f0fdf4"),
    ))
    apply_theme(fig_roi_pct, 260)
    fig_roi_pct.update_layout(title=dict(text="ROI % by Campaign", font=dict(color="#86efac",size=13)), xaxis_tickangle=-20)

    return html.Div([
        page_header("Marketing ROI Tracker", "Campaign effectiveness · Revenue lift · Buyer acquisition costs"),
        html.Div([
            kpi(fmt_usd(mk["spend_usd"].sum()), "Total Marketing Spend", None, False, AMBER),
            kpi(fmt_usd(mk["revenue_lift_usd"].sum()), "Total Revenue Lift", None, True, GREEN),
            kpi(f"{mk['roi_pct'].mean():.0f}%", "Avg Campaign ROI", None, True, LIME),
            kpi(str(int(mk["new_buyers"].sum())), "New Buyers Acquired", None, True, BLUE),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"14px","marginBottom":"24px"}),
        card([dcc.Graph(figure=fig_roi, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        card([dcc.Graph(figure=fig_roi_pct, config={"displayModeBar":False})]),
    ])

def register_callbacks(app): pass
