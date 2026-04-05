"""Farm comparison component for side-by-side analysis"""

from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import apply_theme, fmt_usd, GREEN, BLUE, AMBER

def create_comparison_chart(data, selected_farms, metric='gross_profit_usd'):
    """Create a comparison chart for selected farms"""
    
    if not selected_farms:
        return go.Figure()
    
    fig = go.Figure()
    colors = [GREEN, BLUE, AMBER, '#a855f7']
    
    for i, farm in enumerate(selected_farms):
        farm_data = data[data['farm_name'] == farm]
        
        fig.add_trace(go.Bar(
            name=farm,
            x=farm_data['season'],
            y=farm_data[metric],
            marker_color=colors[i % len(colors)],
            text=[fmt_usd(v) for v in farm_data[metric]],
            textposition='outside'
        ))
    
    fig.update_layout(
        barmode='group',
        title=f"Farm Comparison: {metric.replace('_', ' ').title()}",
        xaxis_title="Season",
        yaxis_title="Value (USD)",
        hovermode='x unified'
    )
    
    apply_theme(fig, 400)
    return fig

def create_comparison_metrics_table(data, selected_farms):
    """Create a metrics comparison table"""
    
    if not selected_farms:
        return html.Div("Select farms to compare", style={"color": "#6b7280", "padding": "20px", "textAlign": "center"})
    
    metrics = ['revenue_usd', 'gross_profit_usd', 'profit_margin_pct', 'profit_per_ha']
    metric_labels = ['Revenue', 'Gross Profit', 'Profit Margin', 'Profit/Ha']
    
    rows = []
    for metric, label in zip(metrics, metric_labels):
        row_cells = [html.Td(label, style={"fontWeight": "600", "color": "#86efac"})]
        
        for farm in selected_farms:
            farm_data = data[data['farm_name'] == farm]
            if not farm_data.empty:
                if metric == 'profit_margin_pct':
                    value = f"{farm_data[metric].mean():.1f}%"
                else:
                    value = fmt_usd(farm_data[metric].mean())
            else:
                value = "N/A"
            row_cells.append(html.Td(value, style={"color": "#f0fdf4"}))
        
        rows.append(html.Tr(row_cells))
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Metric", style={"color": "#4ade80"}),
            *[html.Th(farm, style={"color": "#4ade80"}) for farm in selected_farms]
        ])),
        html.Tbody(rows)
    ], style={"width": "100%", "borderCollapse": "collapse"})

def create_comparison_radar(data, selected_farms):
    """Create a radar chart for farm comparison"""
    
    if not selected_farms:
        return go.Figure()
    
    categories = ['Revenue', 'Profit', 'Margin', 'Efficiency', 'Yield', 'Satisfaction']
    
    fig = go.Figure()
    colors = [GREEN, BLUE, AMBER, '#a855f7']
    
    for i, farm in enumerate(selected_farms):
        farm_data = data[data['farm_name'] == farm]
        if not farm_data.empty:
            values = [
                farm_data['revenue_usd'].mean() / 1000000,  # Normalize to millions
                farm_data['gross_profit_usd'].mean() / 1000000,
                farm_data['profit_margin_pct'].mean(),
                farm_data.get('profit_per_ha', pd.Series([100])).mean() / 100,
                farm_data.get('yield_tons_ha', pd.Series([5])).mean(),
                farm_data.get('satisfaction_score', pd.Series([4])).mean()
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=farm,
                line=dict(color=colors[i % len(colors)], width=2),
                fillcolor=f"rgba({int(colors[i % len(colors)][1:3], 16)}, {int(colors[i % len(colors)][3:5], 16)}, {int(colors[i % len(colors)][5:7], 16)}, 0.2)"
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max(values) if 'values' in locals() else 10])
        ),
        showlegend=True,
        title="Farm Performance Radar"
    )
    
    apply_theme(fig, 400)
    return fig
