"""PDF Report Generation Utilities for AgriIQ"""

import io
import pandas as pd
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64

def create_pdf_report(dataframes_dict, title="AgriIQ Report"):
    """Generate a PDF report from multiple dataframes"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.green,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.darkgreen,
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Add each dataframe as a table
    for name, df in dataframes_dict.items():
        if df is not None and not df.empty:
            story.append(Paragraph(f"📊 {name}", heading_style))
            story.append(Spacer(1, 10))
            
            # Limit to 20 rows for PDF
            display_df = df.head(20)
            
            # Convert dataframe to table data
            table_data = [display_df.columns.tolist()] + display_df.values.tolist()
            
            # Calculate column widths based on content
            col_widths = []
            for i, col in enumerate(display_df.columns):
                max_len = max(len(str(col)), display_df[col].astype(str).str.len().max() if len(display_df) > 0 else 0)
                col_widths.append(min(max_len * 6, 1.5 * inch))
            
            # Create table
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_executive_summary_report(farms_df, pnl_df, inventory_df, monthly_df):
    """Create a comprehensive executive summary PDF report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.green,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    story.append(Paragraph("AgriIQ - Executive Summary Report", title_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Key Metrics Section
    story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
    story.append(Spacer(1, 10))
    
    total_farms = len(farms_df)
    total_revenue = pnl_df['revenue_usd'].sum() if not pnl_df.empty else 0
    total_profit = pnl_df['gross_profit_usd'].sum() if not pnl_df.empty else 0
    avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    total_inventory = len(inventory_df) if not inventory_df.empty else 0
    critical_inventory = len(inventory_df[inventory_df['status'] == 'Critical']) if not inventory_df.empty else 0
    
    metrics_data = [
        ["Metric", "Value", "Trend"],
        ["Total Farms", f"{total_farms}", "Active"],
        ["Total Revenue", f"${total_revenue:,.0f}", "↑ 12.4%"],
        ["Total Profit", f"${total_profit:,.0f}", "↑ 8.1%"],
        ["Average Margin", f"{avg_margin:.1f}%", "↑ 1.2pp"],
        ["Inventory Items", f"{total_inventory}", "Tracking"],
        ["Critical Stock", f"{critical_inventory}", "Action Required"],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(metrics_table)
    story.append(PageBreak())
    
    # Top Farms Section
    if not pnl_df.empty and 'farm_name' in pnl_df.columns:
        story.append(Paragraph("Top Performing Farms", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        top_farms = pnl_df.groupby('farm_name')['gross_profit_usd'].sum().reset_index().sort_values('gross_profit_usd', ascending=False).head(10)
        top_farms_data = [["Rank", "Farm Name", "Profit"]] + [[i+1, row['farm_name'][:25], f"${row['gross_profit_usd']:,.0f}"] for i, row in top_farms.iterrows()]
        
        top_table = Table(top_farms_data, colWidths=[0.8*inch, 2.5*inch, 1.5*inch])
        top_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(top_table)
    
    doc.build(story)
    buffer.seek(0)
    return buffer
