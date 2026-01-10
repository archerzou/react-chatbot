import os
import math
import logging
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Flowable
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

FONT_NAME = "DejaVuSans"
FONT_NAME_BOLD = "DejaVuSans-Bold"
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
]
FONT_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
]


def _register_unicode_fonts():
    """Register DejaVu Sans fonts for Unicode support (including Maori characters)."""
    font_registered = False
    bold_registered = False
    
    for path in FONT_PATHS:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(FONT_NAME, path))
                font_registered = True
                break
            except Exception as e:
                logger.warning(f"Failed to register font from {path}: {e}")
    
    for path in FONT_BOLD_PATHS:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, path))
                bold_registered = True
                break
            except Exception as e:
                logger.warning(f"Failed to register bold font from {path}: {e}")
    
    if not font_registered:
        logger.warning("DejaVu Sans font not found - falling back to Helvetica (Maori characters may not display)")
    if not bold_registered:
        logger.warning("DejaVu Sans Bold font not found - falling back to Helvetica-Bold")
    
    return font_registered, bold_registered


_fonts_registered = _register_unicode_fonts()


def safe_str(value: Any) -> str:
    """Safely convert value to string, handling None/NaN values."""
    if value is None:
        return "Not available"
    if isinstance(value, float) and math.isnan(value):
        return "Not available"
    return str(value)


class PDFHeader(Flowable):
    """Custom flowable for PDF header with blue background, wave pattern, and logo."""
    
    def __init__(self, width: float, height: float, logo_path: Optional[str] = None):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.logo_path = logo_path
    
    def draw(self):
        c = self.canv
        
        # Draw blue background
        c.setFillColor(colors.HexColor("#0099D8"))
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        # Draw white wave pattern
        c.setFillColor(colors.white)
        wave_path = c.beginPath()
        wave_path.moveTo(0, 0)
        
        wave_height = self.height * 0.25
        num_points = 100
        for i in range(num_points + 1):
            x = (i / num_points) * self.width
            y = wave_height * (0.5 + 0.5 * math.sin((i / num_points) * math.pi * 2 - math.pi / 2))
            if i == 0:
                wave_path.moveTo(x, y)
            else:
                wave_path.lineTo(x, y)
        
        wave_path.lineTo(self.width, 0)
        wave_path.lineTo(0, 0)
        wave_path.close()
        c.drawPath(wave_path, fill=1, stroke=0)
        
        # Draw logo if available
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                logo_height = self.height * 0.7
                logo_width = logo_height * 1.8
                logo_x = self.width - logo_width - 15
                logo_y = (self.height - logo_height) / 2
                
                c.drawImage(
                    self.logo_path, logo_x, logo_y,
                    width=logo_width, height=logo_height,
                    preserveAspectRatio=True, mask='auto'
                )
            except Exception as e:
                logger.warning(f"Could not draw logo: {e}")
    
    def wrap(self, availWidth: float, availHeight: float):
        return (self.width, self.height)


class PDFService:
    """Service for generating PDF reports"""
    
    def __init__(self):
        self.logo_path = self._find_logo_path()
    
    def _find_logo_path(self) -> Optional[str]:
        """Find the logo file path"""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png'),
            os.path.join(os.path.dirname(__file__), 'assets', 'logo.png'),
            '/home/ubuntu/repos/react-chatbot/assets/logo.png',
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def generate_pdf(self, data: Dict[str, Any]) -> BytesIO:
        """
        Generate formatted PDF report from data dictionary.
        Returns: PDF file buffer
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1 * cm,
            leftMargin=1 * cm,
            topMargin=1 * cm,
            bottomMargin=1 * cm
        )
        
        styles = getSampleStyleSheet()
        
        font_name = FONT_NAME if _fonts_registered[0] else 'Helvetica'
        font_name_bold = FONT_NAME_BOLD if _fonts_registered[1] else 'Helvetica-Bold'
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=font_name_bold,
            fontSize=16,
            textColor=colors.HexColor("#0099D8"),
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor("#666666"),
            spaceAfter=12
        )
        
        section_header_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName=font_name_bold,
            fontSize=12,
            textColor=colors.HexColor("#0099D8"),
            spaceBefore=14,
            spaceAfter=6,
            borderPadding=4
        )
        
        subsection_style = ParagraphStyle(
            'SubSection',
            parent=styles['Heading3'],
            fontName=font_name_bold,
            fontSize=10,
            textColor=colors.HexColor("#444444"),
            spaceBefore=10,
            spaceAfter=4
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=10,
            textColor=colors.HexColor("#333333"),
            spaceAfter=8,
            leading=14
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName=font_name,
            fontSize=9,
            textColor=colors.HexColor("#999999"),
            alignment=TA_RIGHT,
            spaceBefore=20
        )
        
        story = []
        
        # Header
        page_width = A4[0] - 2 * cm
        header = PDFHeader(width=page_width, height=2.5 * cm, logo_path=self.logo_path)
        story.append(header)
        story.append(Spacer(1, 12))
        
        # Title
        story.append(Paragraph("CLIENT BACKGROUND REPORT", title_style))
        story.append(Paragraph("Based on Plunket AI Model Analysis", subtitle_style))
        
        # Divider
        story.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#DEE2E6"),
            spaceBefore=4,
            spaceAfter=12
        ))
        
        # CLIENT INFORMATION section
        story.append(Paragraph("CLIENT INFORMATION", section_header_style))
        
        client_name = safe_str(data.get('client_name', ''))
        client_nhi = safe_str(data.get('client_nhi', ''))
        dhb = safe_str(data.get('dhb', ''))
        ethnicity = safe_str(data.get('ethnicity', ''))
        domicile = safe_str(data.get('domicile', ''))
        gender = safe_str(data.get('gender', ''))
        primary_caregiver = safe_str(data.get('primary_caregiver', ''))
        well_child_level_of_need = safe_str(data.get('well_child_level_of_need', ''))
        
        client_info_data = [
            ['Client Name:', client_name, 'Client NHI:', client_nhi],
            ['DHB:', dhb, 'Ethnicity:', ethnicity],
            ['Domicile:', domicile, 'Gender:', gender],
            ['Primary Caregiver:', primary_caregiver, 'Well Child Level of Need:', well_child_level_of_need],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M'), '', '']
        ]
        
        client_info_table = Table(client_info_data, colWidths=[3.2 * cm, 5.0 * cm, 4.3 * cm, 5.5 * cm])
        client_info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#666666")),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor("#666666")),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor("#000000")),
            ('TEXTCOLOR', (3, 0), (3, -1), colors.HexColor("#000000")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (1, 0), (1, -1), 24),
        ]))
        story.append(client_info_table)
        story.append(Spacer(1, 12))
        
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DEE2E6"), spaceAfter=8))
        
        # HOUSING RISK section - display only if housing_concerns == 1
        housing_concerns = data.get('housing_concerns', 0)
        if housing_concerns == 1:
            story.append(Paragraph("HOUSING RISK", section_header_style))
            housing_risk_categories = safe_str(data.get('housing_risk_categories', ''))
            story.append(Paragraph(f"&bull; <b>Risk Categories:</b> {housing_risk_categories}", body_style))
            story.append(Spacer(1, 12))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DEE2E6"), spaceAfter=8))
        
        # DISABILITY CONCERN section - display only if is_disability_discussed == 1
        is_disability_discussed = data.get('is_disability_discussed', 0)
        if is_disability_discussed == 1:
            story.append(Paragraph("DISABILITY CONCERN", section_header_style))
            disability_categories = safe_str(data.get('disability_categories', ''))
            family_member_disability = safe_str(data.get('family_member_disability', ''))
            story.append(Paragraph(f"&bull; <b>Disability Categories:</b> {disability_categories}", body_style))
            story.append(Paragraph(f"&bull; <b>Family Member Disability:</b> {family_member_disability}", body_style))
            story.append(Spacer(1, 12))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DEE2E6"), spaceAfter=8))
        
        # MENTAL HEALTH CONCERN section - display if mmh_concerns == 1 or family_mental_concerns == 1
        mmh_concerns = data.get('mmh_concerns', 0)
        family_mental_concerns = data.get('family_mental_concerns', 0)
        if mmh_concerns == 1 or family_mental_concerns == 1:
            story.append(Paragraph("MENTAL HEALTH CONCERN", section_header_style))
            if mmh_concerns == 1:
                mental_health_categories = safe_str(data.get('mental_health_categories', ''))
                story.append(Paragraph(f"&bull; <b>Mental Health Categories:</b> {mental_health_categories}", body_style))
            if family_mental_concerns == 1:
                family_mental_health_categories = safe_str(data.get('family_mental_health_categories', ''))
                story.append(Paragraph(f"&bull; <b>Family Mental Health Categories:</b> {family_mental_health_categories}", body_style))
            family_member_impact = safe_str(data.get('family_member_impact', ''))
            if family_member_impact and family_member_impact != "Not available":
                story.append(Paragraph(f"&bull; <b>Family Member Impact:</b> {family_member_impact}", body_style))
            story.append(Spacer(1, 12))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DEE2E6"), spaceAfter=8))
        
        # SUMMARIES section
        story.append(Paragraph("SUMMARIES", section_header_style))
        
        story.append(Paragraph("Housing Summary:", subsection_style))
        house_summary = safe_str(data.get('house_summary', ''))
        story.append(Paragraph(house_summary, body_style))
        
        story.append(Paragraph("IMPA Summary:", subsection_style))
        impa_summary = safe_str(data.get('impa_summary', ''))
        story.append(Paragraph(impa_summary, body_style))
        
        story.append(Paragraph("MMH Summary:", subsection_style))
        mmh_summary = safe_str(data.get('mmh_summary', ''))
        story.append(Paragraph(mmh_summary, body_style))
        
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DEE2E6"), spaceAfter=8))
        
        # Footer
        story.append(Paragraph("Generated by Plunket AI Model.", footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
