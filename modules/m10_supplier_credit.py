"""Module 10 — Supplier Credit & Risk"""
from dash import html, dcc
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

def layout():
    sc = sup_credit()

    high_risk = sc[sc["risk_level"]=="HIGH"]
    suspended = sc[sc["supply_status"]=="Suspended"]

    # Risk distribution per supplier
    by_sup = sc.groupby("supplier_name").agg(
        outstanding=("outstanding_usd","sum"),
        overdue=("overdue_usd","sum"),
        utilization=("credit_utilization_pct","mean"),
    ).reset_index().sort_values("outstanding", ascending=False)

    fig_outstanding = go.Figure()
    fig_outstanding.add_trace(go.Bar(name="Outstanding", x=by_sup["supplier_name"], y=by_sup["outstanding"], marker_color=AMBER))
    fig_outstanding.add_trace(go.Bar(name="Overdue", x=by_sup["supplier_name"], y=by_sup["overdue"], marker_color=RED))
    fig_outstanding.update_layout(barmode="overlay", xaxis_tickangle=-25)
    apply_theme(fig_outstanding, 300)
    fig_outstanding.update_layout(title=dict(text="Outstanding vs Overdue by Supplier", font=dict(color="#86efac",size=13)))

    # Utilization heatmap
    farms_list = sc["farm_name"].unique()[:8]
    sup_list = sc["supplier_name"].unique()
    z = []
    for fn in farms_list:
        row_vals = []
        for sn in sup_list:
            val = sc[(sc["farm_name"]==fn)&(sc["supplier_name"]==sn)]["credit_utilization_pct"].mean()
            row_vals.append(round(float(val), 1) if not (val != val) else 0)
        z.append(row_vals)

    fig_heat = go.Figure(go.Heatmap(
        z=z, x=[s[:14] for s in sup_list], y=[f[:18] for f in farms_list],
        colorscale=[[0,"#052e16"],[0.6,"#f59e0b"],[1,"#ef4444"]],
        text=z, texttemplate="%{text}%",
        textfont=dict(color="#f0fdf4", size=9),
    ))
    apply_theme(fig_heat, 320)
    fig_heat.update_layout(title=dict(text="Credit Utilization % by Farm × Supplier", font=dict(color="#86efac",size=13)))

    rows = []
    for _, row in high_risk.sort_values("overdue_usd", ascending=False).head(20).iterrows():
        rows.append(html.Tr([
            html.Td(row["farm_name"][:20], style={"color":"#f0fdf4","fontSize":"0.8rem","padding":"8px 6px"}),
            html.Td(row["supplier_name"][:22], style={"color":"#86efac","fontSize":"0.78rem","padding":"8px 6px"}),
            html.Td(row["category"], style={"color":"#6b7280","fontSize":"0.78rem","padding":"8px 6px"}),
            html.Td(fmt_usd(row["credit_limit_usd"]), style={"color":"#f0fdf4","fontSize":"0.8rem","padding":"8px 6px"}),
            html.Td(fmt_usd(row["outstanding_usd"]), style={"color":AMBER,"fontSize":"0.8rem","fontWeight":"600","padding":"8px 6px"}),
            html.Td(fmt_usd(row["overdue_usd"]), style={"color":RED,"fontSize":"0.8rem","fontWeight":"700","padding":"8px 6px"}),
            html.Td(f"{row['credit_utilization_pct']:.0f}%", style={"color":RED if row["credit_utilization_pct"]>100 else AMBER,"fontSize":"0.8rem","padding":"8px 6px"}),
            html.Td(status_badge(row["supply_status"])),
        ], style={"borderBottom":"1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color":"#4ade80","fontSize":"0.70rem","fontWeight":"600","textTransform":"uppercase","padding":"8px 6px","letterSpacing":"0.06em"})
                             for h in ["Farm","Supplier","Category","Credit Limit","Outstanding","Overdue","Utilization","Status"]])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse"})

    return html.Div([
        page_header("Supplier Credit & Risk", "Supplier payment health · Credit utilization · Supply suspension alerts"),
        html.Div([
            kpi(fmt_usd(sc["outstanding_usd"].sum()), "Total Outstanding", None, False, AMBER),
            kpi(fmt_usd(sc["overdue_usd"].sum()), "Total Overdue", "Requires payment", False, RED),
            kpi(str(len(high_risk)), "HIGH Risk Lines", None, False, RED),
            kpi(str(len(suspended)), "Suspended Suppliers", "Supply stopped", False, RED),
        ], style={"display":"grid","gridTemplateColumns":"repeat(4,1fr)","gap":"14px","marginBottom":"24px"}),
        card([dcc.Graph(figure=fig_outstanding, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        card([dcc.Graph(figure=fig_heat, config={"displayModeBar":False})], {"marginBottom":"16px"}),
        card([
            html.Div("🔴  HIGH Risk Supplier Accounts", style={"color":RED,"fontWeight":"600","marginBottom":"14px","fontSize":"0.9rem"}),
            html.Div(table, style={"overflowX":"auto","maxHeight":"380px","overflowY":"auto"}),
        ]),
    ])

def register_callbacks(app): pass
