"""Enhanced callbacks for loading states, exports, refresh, and compare"""

import pandas as pd
import base64
from datetime import datetime
from dash import callback, Input, Output, State, html, dcc
import dash_bootstrap_components as dbc

def register_enhanced_callbacks(app):
    
    @callback(
        Output("refresh-interval", "disabled"),
        Input("refresh-button", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_auto_refresh(n_clicks):
        """Toggle auto-refresh on/off"""
        # This just returns False to keep it running
        # You could add state to track if it's enabled
        return False
    
    @callback(
        Output({"type": "download", "index": "farm-data"}, "data"),
        Input({"type": "export-button", "index": "farm-data"}, "n_clicks"),
        prevent_initial_call=True
    )
    def export_farm_data(n_clicks):
        """Export farm data as CSV"""
        from utils.data_loader import farms
        df = farms()
        return dcc.send_data_frame(df.to_csv, "farms_export.csv", index=False)
    
    @callback(
        Output({"type": "download", "index": "pnl-data"}, "data"),
        Input({"type": "export-button", "index": "pnl-data"}, "n_clicks"),
        prevent_initial_call=True
    )
    def export_pnl_data(n_clicks):
        """Export P&L data as CSV"""
        from utils.data_loader import pnl
        df = pnl()
        return dcc.send_data_frame(df.to_csv, "pnl_export.csv", index=False)
    
    @callback(
        Output("search-results", "children"),
        Input("search-input", "value"),
        State("farm-table-data", "data")
    )
    def filter_farms(search_term, farm_data):
        """Filter farms based on search term"""
        if not search_term:
            return farm_data
        
        filtered = [farm for farm in farm_data 
                   if search_term.lower() in farm.get('name', '').lower() 
                   or search_term.lower() in farm.get('province', '').lower()
                   or search_term.lower() in farm.get('primary_crop', '').lower()]
        return filtered

def create_compare_callback(app, data_loader, figure_creator):
    """Create a callback for farm comparison"""
    
    @app.callback(
        Output("compare-chart", "figure"),
        Input("compare-farms", "value"),
        prevent_initial_call=True
    )
    def update_compare_chart(selected_farms):
        if not selected_farms or len(selected_farms) == 0:
            return figure_creator.create_empty_figure()
        
        df = data_loader()
        filtered_df = df[df['farm_name'].isin(selected_farms)]
        return figure_creator.create_comparison_figure(filtered_df, selected_farms)
