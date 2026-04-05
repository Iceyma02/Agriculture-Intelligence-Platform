"""Real-time alerts system for critical conditions"""

from dash import html, dcc
import pandas as pd
from datetime import datetime, timedelta

class AlertSystem:
    def __init__(self):
        self.alerts = []
    
    def check_inventory_alerts(self, inventory_df):
        """Check for critical inventory levels"""
        alerts = []
        if not inventory_df.empty:
            critical_items = inventory_df[inventory_df['status'] == 'Critical']
            for _, item in critical_items.iterrows():
                alerts.append({
                    'type': 'critical',
                    'title': f"Critical Stock Alert: {item['item_name']}",
                    'message': f"{item['farm_name']} - {item['item_name']} is at {item['qty_current']}/{item['qty_max']} units. Immediate reorder required!",
                    'farm': item['farm_name'],
                    'timestamp': datetime.now()
                })
        return alerts
    
    def check_financial_alerts(self, pnl_df):
        """Check for financial anomalies"""
        alerts = []
        if not pnl_df.empty:
            # Check for negative profit margins
            negative_margins = pnl_df[pnl_df['profit_margin_pct'] < 0]
            for _, farm in negative_margins.iterrows():
                alerts.append({
                    'type': 'warning',
                    'title': f"Negative Profit Margin: {farm['farm_name']}",
                    'message': f"{farm['farm_name']} has a negative profit margin of {farm['profit_margin_pct']:.1f}%",
                    'farm': farm['farm_name'],
                    'timestamp': datetime.now()
                })
        return alerts
    
    def check_supply_chain_alerts(self, sc_df):
        """Check for supply chain delays"""
        alerts = []
        if not sc_df.empty and 'days_delayed' in sc_df.columns:
            delayed = sc_df[sc_df['days_delayed'] > 5]
            for _, shipment in delayed.iterrows():
                alerts.append({
                    'type': 'warning',
                    'title': f"Shipment Delay Alert",
                    'message': f"Shipment {shipment['shipment_id']} to {shipment['destination']} is delayed by {shipment['days_delayed']} days",
                    'farm': shipment.get('farm_name', 'Unknown'),
                    'timestamp': datetime.now()
                })
        return alerts
    
    def get_active_alerts(self):
        """Get all active alerts (last 24 hours)"""
        cutoff = datetime.now() - timedelta(hours=24)
        return [a for a in self.alerts if a['timestamp'] > cutoff]

def create_alerts_panel(alert_system):
    """Create an alerts panel component"""
    active_alerts = alert_system.get_active_alerts()
    
    if not active_alerts:
        return html.Div([
            html.Div("✅ No Active Alerts", style={"color": "#22c55e", "textAlign": "center", "padding": "20px"})
        ])
    
    alert_elements = []
    for alert in active_alerts:
        color = "#ef4444" if alert['type'] == 'critical' else "#f59e0b"
        icon = "🔴" if alert['type'] == 'critical' else "⚠️"
        
        alert_elements.append(html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "1.2rem", "marginRight": "10px"}),
                html.Span(alert['title'], style={"fontWeight": "600", "color": color})
            ]),
            html.P(alert['message'], style={"margin": "8px 0", "color": "#86efac", "fontSize": "0.85rem"}),
            html.Small(f"Farm: {alert['farm']} | {alert['timestamp'].strftime('%H:%M')}", 
                      style={"color": "#6b7280", "fontSize": "0.7rem"})
        ], style={
            "padding": "12px",
            "marginBottom": "10px",
            "borderLeft": f"3px solid {color}",
            "backgroundColor": "rgba(239,68,68,0.05)" if alert['type'] == 'critical' else "rgba(245,158,11,0.05)",
            "borderRadius": "8px"
        }))
    
    return html.Div([
        html.Div(f"🚨 {len(active_alerts)} Active Alerts", 
                style={"fontWeight": "600", "marginBottom": "15px", "color": "#ef4444"}),
        *alert_elements
    ])
