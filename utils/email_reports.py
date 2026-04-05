"""Email report generation functionality"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from datetime import datetime
import plotly.io as pio
import io

class EmailReporter:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def generate_pdf_report(self, data, title="AgriIQ Weekly Report"):
        """Generate a PDF report from data"""
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.green,
            spaceAfter=30
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add farm summary table
        if isinstance(data, pd.DataFrame):
            table_data = [data.columns.tolist()] + data.head(10).values.tolist()
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def send_weekly_report(self, recipient_emails, data):
        """Send weekly report via email"""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(recipient_emails)
        msg['Subject'] = f"AgriIQ Weekly Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2 style="color: #22c55e;">AgriIQ Weekly Report</h2>
            <p>Dear Stakeholder,</p>
            <p>Please find attached this week's AgriIQ report with key metrics:</p>
            <ul>
                <li>Portfolio Revenue: ${data.get('total_revenue', 0):,.0f}</li>
                <li>Total Profit: ${data.get('total_profit', 0):,.0f}</li>
                <li>Average Margin: {data.get('avg_margin', 0):.1f}%</li>
                <li>Active Farms: {data.get('active_farms', 0)}</li>
            </ul>
            <p>Login to the AgriIQ platform for real-time updates.</p>
            <hr>
            <p style="color: #6b7280; font-size: 12px;">This is an automated report from AgriIQ.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Attach PDF report
        pdf_buffer = self.generate_pdf_report(data.get('df', pd.DataFrame()))
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(pdf_buffer.read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', f'attachment; filename=agriiq_report_{datetime.now().strftime("%Y%m%d")}.pdf')
        msg.attach(attachment)
        
        # Send email
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
