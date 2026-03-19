"""
PDF report generator — creates professional security audit reports using ReportLab.
"""
import os
import io
import logging
from datetime import datetime
from typing import Optional

from models.schemas import ScanResponse, VulnerabilityOut

logger = logging.getLogger(__name__)

SEVERITY_COLORS = {
    "critical": (0.85, 0.1, 0.1),
    "high": (0.9, 0.5, 0.1),
    "medium": (0.85, 0.75, 0.1),
    "low": (0.2, 0.5, 0.85),
    "info": (0.5, 0.5, 0.5),
}


class ReportGenerator:
    """Generate professional PDF security reports."""

    @staticmethod
    def generate(scan: ScanResponse) -> bytes:
        """Generate PDF report from scan results. Returns PDF bytes."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch, cm
            from reportlab.lib.colors import HexColor, Color
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak, HRFlowable,
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        except ImportError:
            logger.error("ReportLab not installed")
            raise RuntimeError("ReportLab is required for PDF generation")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            leftMargin=1.2 * cm, rightMargin=1.2 * cm,
            topMargin=2 * cm, bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()

        # Custom styles
        styles.add(ParagraphStyle(
            "ReportTitle", parent=styles["Title"],
            fontSize=28, spaceAfter=6, fontName="Helvetica-Bold",
            textColor=HexColor("#111111"),
        ))
        styles.add(ParagraphStyle(
            "ReportSubtitle", parent=styles["Normal"],
            fontSize=11, spaceAfter=20, textColor=HexColor("#666666"),
        ))
        styles.add(ParagraphStyle(
            "SectionHeader", parent=styles["Heading2"],
            fontSize=16, spaceBefore=20, spaceAfter=10,
            fontName="Helvetica-Bold", textColor=HexColor("#111111"),
        ))
        styles.add(ParagraphStyle(
            "VulnTitle", parent=styles["Normal"],
            fontSize=11, fontName="Helvetica-Bold",
            textColor=HexColor("#111111"), spaceAfter=4,
        ))
        styles.add(ParagraphStyle(
            "BodyMono", parent=styles["Normal"],
            fontSize=8, fontName="Courier", textColor=HexColor("#333333"),
            leftIndent=10,
        ))

        elements = []

        # ── Title page ──
        elements.append(Spacer(1, 2 * inch))
        elements.append(Paragraph("REPOGUARD AI", styles["ReportTitle"]))
        elements.append(Paragraph("Security Audit Report", styles["ReportSubtitle"]))
        elements.append(HRFlowable(width="100%", color=HexColor("#CCCCCC")))
        elements.append(Spacer(1, 0.3 * inch))

        # Metadata table
        meta_data = [
            ["Repository", scan.repo_url],
            ["Scan ID", scan.id],
            ["Date", datetime.now().strftime("%Y-%m-%d %H:%M UTC")],
            ["Risk Score", f"{scan.risk_score} / 100"],
            ["Total Findings", str(len(scan.vulnerabilities))],
            ["Languages", ", ".join(scan.languages_detected) if scan.languages_detected else "N/A"],
        ]
        meta_table = Table(meta_data, colWidths=[2.5 * cm, 14 * cm])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TEXTCOLOR", (0, 0), (0, -1), HexColor("#666666")),
            ("TEXTCOLOR", (1, 0), (1, -1), HexColor("#111111")),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(meta_table)
        elements.append(PageBreak())

        # ── Executive Summary ──
        elements.append(Paragraph("Executive Summary", styles["SectionHeader"]))
        elements.append(Paragraph(
            scan.summary or "No summary available.",
            styles["Normal"],
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # Severity breakdown
        severity_counts = {}
        for v in scan.vulnerabilities:
            severity_counts[v.severity] = severity_counts.get(v.severity, 0) + 1

        breakdown_data = [["Severity", "Count"]]
        for sev in ["critical", "high", "medium", "low", "info"]:
            if sev in severity_counts:
                breakdown_data.append([sev.upper(), str(severity_counts[sev])])

        if len(breakdown_data) > 1:
            breakdown_table = Table(breakdown_data, colWidths=[5 * cm, 3 * cm])
            breakdown_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F0F0F0")),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#DDDDDD")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(breakdown_table)

        elements.append(PageBreak())

        # ── Vulnerability Details ──
        elements.append(Paragraph("Vulnerability Details", styles["SectionHeader"]))

        for i, vuln in enumerate(scan.vulnerabilities):
            sev_color = SEVERITY_COLORS.get(vuln.severity, (0.5, 0.5, 0.5))
            color_hex = "#{:02x}{:02x}{:02x}".format(
                int(sev_color[0] * 255), int(sev_color[1] * 255), int(sev_color[2] * 255)
            )

            # Vulnerability header
            elements.append(Paragraph(
                f'<font color="{color_hex}">■</font> #{i+1} — {vuln.title}',
                styles["VulnTitle"],
            ))
            elements.append(Paragraph(
                f'<font color="#999999">Severity: {vuln.severity.upper()} | Tool: {vuln.tool} | Category: {vuln.category}</font>',
                ParagraphStyle("meta", parent=styles["Normal"], fontSize=8),
            ))
            elements.append(Spacer(1, 4))
            elements.append(Paragraph(vuln.description, styles["Normal"]))

            # File location
            loc = vuln.file_path
            if vuln.line_number:
                loc += f":{vuln.line_number}"
            elements.append(Paragraph(f'<font color="#666666">📄 {loc}</font>', styles["Normal"]))

            # Code snippet
            if vuln.code_snippet:
                elements.append(Spacer(1, 4))
                # Escape HTML in code
                safe_code = vuln.code_snippet.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                elements.append(Paragraph(safe_code, styles["BodyMono"]))

            # Fix suggestion
            if vuln.fix_suggestion:
                elements.append(Spacer(1, 4))
                elements.append(Paragraph(
                    f'<font color="#2563EB">💡 Fix: </font>{vuln.fix_suggestion}',
                    ParagraphStyle("fix", parent=styles["Normal"], fontSize=9),
                ))

            elements.append(Spacer(1, 0.15 * inch))
            elements.append(HRFlowable(width="100%", color=HexColor("#EEEEEE")))
            elements.append(Spacer(1, 0.1 * inch))

        # Build PDF
        doc.build(elements)
        return buffer.getvalue()
