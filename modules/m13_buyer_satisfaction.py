"""Module 13 — Buyer Satisfaction"""

from dash import html, dcc
import plotly.graph_objects as go
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import buyer_sat
from utils.helpers import GREEN, AMBER, RED, LIME, BLUE, PALETTE, fmt_usd, fmt_tons, apply_theme, page_header, card, kpi, add_export_section, create_empty_chart, hex_to_rgba

def layout():
    bs = buyer_sat()
    
    export_section = add_export_section({
        "Buyer_Satisfaction_Complete": bs,
        "Buyer_Ratings_Summary": bs.groupby("buyer").agg(overall=("overall_score", "mean")).reset_index() if not bs.empty else None
    })
    
    if bs.empty:
        return html.Div([
            export_section,
            page_header("Buyer Satisfaction", "Customer feedback · Quality ratings · Complaint tracking · Repeat orders"),
            card([html.Div("⚠️ No buyer satisfaction data available", style={"color": AMBER, "textAlign": "center", "padding": "40px"})])
        ])

    by_buyer = bs.groupby("buyer").agg(
        overall=("overall_score", "mean"),
        quality=("quality_score", "mean"),
        delivery=("delivery_score", "mean"),
        payment=("payment_score", "mean"),
        complaints=("complaints", "sum"),
        revenue=("revenue_usd", "sum"),
        volume=("volume_tons", "sum"),
    ).reset_index().sort_values("overall", ascending=False)

    # ============================================================================
    # RADAR CHART - FIXED with better spacing and no text clash
    # ============================================================================
    categories = ["Overall", "Quality", "Delivery", "Payment"]
    fig_radar = go.Figure()
    top4 = by_buyer.head(4)
    
    for i, (_, row) in enumerate(top4.iterrows()):
        vals = [row["overall"], row["quality"], row["delivery"], row["payment"]]
        vals += vals[:1]  # Close the loop
        
        hex_color = PALETTE[i % len(PALETTE)]
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        
        fig_radar.add_trace(go.Scatterpolar(
            r=vals,
            theta=categories + [categories[0]],
            fill="toself",
            name=row["buyer"][:20],
            line=dict(color=hex_color, width=2),
            fillcolor=f"rgba({r}, {g}, {b}, 0.15)",
            hovertemplate="<b>%{theta}</b><br>Score: %{r:.1f}/5<br>Buyer: " + row["buyer"][:20] + "<extra></extra>"
        ))
    
    # Improved radar chart layout with better text positioning
    fig_radar.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 5.5],
                tickfont=dict(color="#6b7280", size=10),
                gridcolor="rgba(34,197,94,0.15)",
                linecolor="rgba(34,197,94,0.3)",
                tickvals=[0, 1, 2, 3, 4, 5],
                ticktext=["0", "1", "2", "3", "4", "5"]
            ),
            angularaxis=dict(
                tickfont=dict(color="#86efac", size=11, weight="bold"),
                gridcolor="rgba(34,197,94,0.15)",
                linecolor="rgba(34,197,94,0.3)",
                rotation=90,
                direction="clockwise"
            ),
        ),
        title=dict(
            text="Buyer Satisfaction Radar — Top 4 Buyers",
            font=dict(color="#86efac", size=14),
            x=0.5,
            xanchor="center"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="#86efac", size=10),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(l=60, r=60, t=80, b=80),
        height=450,
        width=550,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    # Score bar chart
    fig_scores = go.Figure()
    fig_scores.add_trace(go.Bar(name="Overall", x=by_buyer["buyer"], y=by_buyer["overall"], marker_color=GREEN, text=by_buyer["overall"].round(1), textposition="outside", textfont=dict(color="#f0fdf4", size=10)))
    fig_scores.add_trace(go.Bar(name="Quality", x=by_buyer["buyer"], y=by_buyer["quality"], marker_color=LIME, text=by_buyer["quality"].round(1), textposition="outside", textfont=dict(color="#f0fdf4", size=10)))
    fig_scores.add_trace(go.Bar(name="Delivery", x=by_buyer["buyer"], y=by_buyer["delivery"], marker_color=BLUE, text=by_buyer["delivery"].round(1), textposition="outside", textfont=dict(color="#f0fdf4", size=10)))
    fig_scores.update_layout(barmode="group", xaxis_tickangle=-25)
    apply_theme(fig_scores, 320)
    fig_scores.update_layout(
        title=dict(text="Satisfaction Scores by Buyer", font=dict(color="#86efac", size=13)),
        yaxis=dict(title="Score (1-5)", range=[0, 5.5], tickvals=[0, 1, 2, 3, 4, 5]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    # Revenue vs satisfaction scatter
    fig_scatter = go.Figure(go.Scatter(
        x=by_buyer["revenue"], y=by_buyer["overall"],
        mode="markers+text",
        marker=dict(size=18, color=by_buyer["overall"], colorscale=[[0, "#7f1d1d"], [0.5, "#f59e0b"], [1, "#22c55e"]], showscale=True, colorbar=dict(title="Score", tickfont=dict(color="#86efac"))),
        text=by_buyer["buyer"].str[:12],
        textposition="top center",
        textfont=dict(color="#f0fdf4", size=9),
        hovertemplate="<b>%{text}</b><br>Revenue: $%{x:,.0f}<br>Satisfaction: %{y:.1f}/5<extra></extra>"
    ))
    apply_theme(fig_scatter, 300)
    fig_scatter.update_layout(
        title=dict(text="Revenue vs Satisfaction Score", font=dict(color="#86efac", size=13)),
        xaxis=dict(title="Revenue (USD)", tickformat="$,.0f", tickfont=dict(color="#6b7280")),
        yaxis=dict(title="Satisfaction Score /5", range=[0, 5.5], tickvals=[0, 1, 2, 3, 4, 5], tickfont=dict(color="#6b7280")),
    )

    # Complaints trend
    if "month_label" in bs.columns:
        trend = bs.groupby("month_label")["complaints"].sum().reset_index()
        fig_complaints = go.Figure(go.Bar(
            x=trend["month_label"], y=trend["complaints"],
            marker=dict(color=[RED if v > 20 else AMBER if v > 10 else GREEN for v in trend["complaints"]]),
            text=trend["complaints"], textposition="outside", textfont=dict(color="#f0fdf4", size=9)
        ))
        apply_theme(fig_complaints, 260)
        fig_complaints.update_layout(
            title=dict(text="Monthly Complaints Across All Buyers", font=dict(color="#86efac", size=13)),
            xaxis_tickangle=-45,
            yaxis=dict(title="Number of Complaints", tickfont=dict(color="#6b7280"))
        )
    else:
        fig_complaints = create_empty_chart("No complaint data available", "Monthly Complaints")

    # Summary table
    rows = []
    for _, row in by_buyer.iterrows():
        score_color = GREEN if row["overall"] >= 4.2 else AMBER if row["overall"] >= 3.5 else RED
        rows.append(html.Tr([
            html.Td(row["buyer"][:25], style={"color": "#f0fdf4", "fontSize": "0.82rem", "fontWeight": "500", "padding": "9px 6px"}),
            html.Td(f"{row['overall']:.1f} / 5", style={"color": score_color, "fontSize": "0.82rem", "fontWeight": "700", "padding": "9px 6px"}),
            html.Td(f"{row['quality']:.1f}", style={"color": "#86efac", "fontSize": "0.8rem", "padding": "9px 6px"}),
            html.Td(f"{row['delivery']:.1f}", style={"color": "#86efac", "fontSize": "0.8rem", "padding": "9px 6px"}),
            html.Td(str(int(row["complaints"])), style={"color": RED if row["complaints"] > 15 else "#f0fdf4", "fontSize": "0.8rem", "fontWeight": "600", "padding": "9px 6px"}),
            html.Td(fmt_usd(row["revenue"]), style={"color": GREEN, "fontSize": "0.8rem", "padding": "9px 6px"}),
            html.Td(fmt_tons(row["volume"]), style={"color": "#6b7280", "fontSize": "0.8rem", "padding": "9px 6px"}),
        ], style={"borderBottom": "1px solid rgba(34,197,94,0.07)"}))

    table = html.Table([
        html.Thead(html.Tr([html.Th(h, style={"color": "#4ade80", "fontSize": "0.70rem", "fontWeight": "600", "textTransform": "uppercase", "padding": "8px 6px"}) for h in ["Buyer", "Overall Score", "Quality", "Delivery", "Complaints", "Revenue", "Volume"]])),
        html.Tbody(rows),
    ], style={"width": "100%", "borderCollapse": "collapse"})

    return html.Div([
        export_section,
        page_header("Buyer Satisfaction", "Customer feedback · Quality ratings · Complaint tracking · Repeat orders"),
        html.Div([
            kpi(f"{bs['overall_score'].mean():.1f} / 5", "Portfolio Avg Score", None, True, GREEN),
            kpi(str(int(bs["complaints"].sum())), "Total Complaints", "All buyers, all months", False, RED),
            kpi(fmt_usd(bs["revenue_usd"].sum()), "Total Buyer Revenue", None, True, LIME),
            kpi(by_buyer.iloc[0]["buyer"][:16], "Highest Rated Buyer", f"{by_buyer.iloc[0]['overall']:.1f}/5", True, AMBER),
        ], style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "14px", "marginBottom": "24px"}),
        html.Div([
            card([dcc.Graph(figure=fig_radar, config={"displayModeBar": False})], {"flex": "1"}),
            card([dcc.Graph(figure=fig_scores, config={"displayModeBar": False})], {"flex": "1.2"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px", "flexWrap": "wrap"}),
        html.Div([
            card([dcc.Graph(figure=fig_scatter, config={"displayModeBar": False})], {"flex": "1"}),
            card([dcc.Graph(figure=fig_complaints, config={"displayModeBar": False})], {"flex": "1"}) if fig_complaints.data else None,
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px", "flexWrap": "wrap"}),
        card([
            html.Div("⭐ Buyer Satisfaction Summary", style={"color": "#86efac", "fontWeight": "600", "marginBottom": "14px", "fontSize": "0.9rem"}),
            html.Div(table, style={"overflowX": "auto", "maxHeight": "400px", "overflowY": "auto"}),
        ]),
    ])

def register_callbacks(app): 
    pass
