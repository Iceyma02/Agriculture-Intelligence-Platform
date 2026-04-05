"""Responsive sidebar with mobile support"""

from dash import html, dcc
import dash_bootstrap_components as dbc

def create_mobile_sidebar():
    """Create a responsive sidebar that collapses on mobile"""
    
    # Mobile menu button (visible on small screens)
    mobile_menu = html.Div([
        html.Button(
            html.I(className="fas fa-bars"),
            id="mobile-menu-btn",
            style={
                "position": "fixed",
                "top": "15px",
                "left": "15px",
                "zIndex": 1001,
                "backgroundColor": "#22c55e",
                "border": "none",
                "borderRadius": "8px",
                "padding": "10px 15px",
                "cursor": "pointer",
                "display": "none"  # Hidden by default, shown via CSS media query
            }
        )
    ])
    
    # Sidebar content
    sidebar_content = html.Div(
        id="sidebar",
        children=[
            html.Div([
                html.H1("AgriIQ", style={"fontSize": "1.6rem", "fontWeight": "800"}),
                html.P("Agriculture Intelligence Platform", style={"fontSize": "0.72rem"})
            ], className="sidebar-logo"),
            html.Div(id="sidebar-nav-content"),
            html.Div([
                html.P("© 2026 Anesu Manjengwa", style={"color": "#374151", "fontSize": "0.68rem"})
            ], style={"marginTop": "auto", "padding": "16px 20px"})
        ],
        className="sidebar"
    )
    
    return [mobile_menu, sidebar_content]

def add_mobile_css():
    """Add CSS for mobile responsiveness"""
    return html.Style("""
        /* Mobile styles */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
                position: fixed;
                z-index: 1000;
            }
            
            .sidebar.open {
                transform: translateX(0);
            }
            
            .main-content {
                margin-left: 0 !important;
                padding: 15px !important;
            }
            
            #mobile-menu-btn {
                display: block !important;
            }
            
            /* Stack charts vertically on mobile */
            .flex-chart-container {
                flex-direction: column !important;
            }
            
            /* Make KPI cards responsive */
            .kpi-grid {
                grid-template-columns: repeat(2, 1fr) !important;
                gap: 10px !important;
            }
            
            /* Make tables scrollable horizontally */
            .table-container {
                overflow-x: auto !important;
            }
        }
        
        /* Tablet styles */
        @media (min-width: 769px) and (max-width: 1024px) {
            .kpi-grid {
                grid-template-columns: repeat(3, 1fr) !important;
            }
        }
    """)
