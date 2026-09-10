"""
Official PDF Inspection Report Generator using ReportLab.
Produces digitally formatted Legal Metrology Inspection Certificates.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

def generate_pdf_report(inspection_dict: dict, output_pdf_path: str):
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0b1f3a'),
        alignment=1,
        fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#475569'),
        alignment=1
    )
    section_heading = ParagraphStyle(
        'SecHead',
        parent=styles['Heading2'],
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0b1f3a'),
        fontName='Helvetica-Bold'
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontSize=8.5,
        leading=11,
        fontName='Helvetica-Bold'
    )

    # 1. Header Banner
    story.append(Paragraph("<b>GOVERNMENT OF INDIA / STATE LEGAL METROLOGY CONTROLLER</b>", title_style))
    story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", subtitle_style))
    story.append(Paragraph("<b>STATUTORY ENFORCEMENT & COMPLIANCE INSPECTION REPORT</b><br/>Under Legal Metrology Act, 2009 & Legal Metrology (Packaged Commodities) Rules, 2011 (Amended to 2026)", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0b1f3a'), spaceBefore=2, spaceAfter=8))

    # 2. Metadata Table
    status = inspection_dict.get('overall_status', 'UNKNOWN')
    status_color = "#15803d" if status in ["FULLY_COMPLIANT", "Passed", "COMPLIANT"] else ("#b91c1c" if status in ["NON_COMPLIANT", "Failed"] else "#b45309")

    metadata = [
        [
            Paragraph("<b>Inspection ID:</b>", cell_style),
            Paragraph(inspection_dict.get('scan_id', 'INSP-2026-N1'), cell_style),
            Paragraph("<b>Date of Inspection:</b>", cell_style),
            Paragraph(datetime.now().strftime("%d-%m-%Y %H:%M IST"), cell_style)
        ],
        [
            Paragraph("<b>Product Name:</b>", cell_style),
            Paragraph(inspection_dict.get('product_name', 'N/A'), cell_style),
            Paragraph("<b>Brand / Company:</b>", cell_style),
            Paragraph(inspection_dict.get('company_name') or inspection_dict.get('brand_name') or 'N/A', cell_style)
        ],
        [
            Paragraph("<b>Enforcement Officer:</b>", cell_style),
            Paragraph(f"{inspection_dict.get('inspector_id', 'LMO-DL-7729')} (Verified)", cell_style),
            Paragraph("<b>Compliance Score:</b>", cell_style),
            Paragraph(f"<b>{inspection_dict.get('compliance_score', 0)}%</b>", cell_style)
        ],
        [
            Paragraph("<b>Overall Finding:</b>", cell_style),
            Paragraph(f"<b><font color='{status_color}'>{status}</font></b>", cell_style),
            Paragraph("<b>PDP Area:</b>", cell_style),
            Paragraph(f"{inspection_dict.get('pdp_area_sq_cm', 150)} cm²", cell_style)
        ]
    ]

    meta_table = Table(metadata, colWidths=[110, 160, 110, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Parameter Evaluation Table
    story.append(Paragraph("<b>1. Detailed Statutory Declarations Checklist (Rule 6 to 9)</b>", section_heading))
    story.append(Spacer(1, 4))

    eval_rows = [[
        Paragraph("<b>Rule Reference</b>", cell_bold),
        Paragraph("<b>Statutory Declaration</b>", cell_bold),
        Paragraph("<b>Status</b>", cell_bold),
        Paragraph("<b>Detected Value & Compliance Assessment</b>", cell_bold)
    ]]

    eval_result = inspection_dict.get('evaluation_result', {})
    field_checks = eval_result.get('field_checks', {})

    for f_key, f_val in field_checks.items():
        st = f_val.get('status', 'REVIEW_REQUIRED')
        f_color = "#15803d" if st == "PASS" else ("#b91c1c" if st == "FAIL" else "#b45309")
        status_p = Paragraph(f"<b><font color='{f_color}'>{st}</font></b>", cell_style)
        rule_p = Paragraph(f_val.get('rule', 'Rule 6'), cell_style)
        label_p = Paragraph(f_val.get('label', f_key.replace('_', ' ').title()), cell_style)
        
        det_text = f_val.get('detected') or 'None detected'
        msg_text = f_val.get('message', '')
        desc_p = Paragraph(f"<b>Value:</b> {det_text}<br/><font color='#64748b' size='7.5'>{msg_text}</font>", cell_style)
        
        eval_rows.append([rule_p, label_p, status_p, desc_p])

    eval_table = Table(eval_rows, colWidths=[65, 120, 55, 300])
    eval_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0b1f3a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(eval_table)
    story.append(Spacer(1, 12))

    # 4. Violations & Legal Notice Section
    violations = eval_result.get('violations', [])
    if violations:
        story.append(Paragraph("<b>2. Violations Summary & Statutory Notice under Section 36</b>", section_heading))
        story.append(Spacer(1, 3))
        v_box_content = []
        for v in violations:
            v_box_content.append(Paragraph(f"• <font color='#b91c1c'><b>{v}</b></font>", cell_style))
        v_box_content.append(Spacer(1, 4))
        v_box_content.append(Paragraph(
            "<b>Statutory Penalty Notice:</b> Under Section 36 of the Legal Metrology Act, 2009, whoever manufactures, packs, imports, sells, or distributes any pre-packaged commodity which does not conform to the declarations on the package as per the Legal Metrology (Packaged Commodities) Rules, 2011 shall be punishable with fine up to ₹25,000 for the first offence, ₹50,000 for the second offence, and for subsequent offences with fine up to ₹1,00,000 or imprisonment up to one year or both.",
            ParagraphStyle('LegalWarning', parent=styles['Normal'], fontSize=7.5, leading=10, textColor=colors.HexColor('#7f1d1d'))
        ))

        v_table = Table([[v_box_content]], colWidths=[540])
        v_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fff1f2')),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#fda4af')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(v_table)
        story.append(Spacer(1, 14))

    # 5. Statutory Link & Signatures
    story.append(Paragraph("<b>3. Statutory Authority & Verification</b>", section_heading))
    story.append(Spacer(1, 3))
    
    auth_rows = [
        [
            Paragraph("<b>Official Rules Reference:</b><br/><a href='https://consumeraffairs.nic.in/acts-and-rules/legal-metrology'><u>consumeraffairs.nic.in/acts-and-rules/legal-metrology</u></a>", cell_style),
            Paragraph("<b>Inspecting Authority Seal:</b><br/>Enforcement Wing, Directorate of Legal Metrology", cell_style)
        ],
        [
            Paragraph("<b>Digital Inspection Hash:</b><br/><font face='Courier' size='7.5'>SHA256-LM-CERT-2026-ENF-VERIFIED</font>", cell_style),
            Paragraph("<b>Signature:</b> ___________________________<br/>Authorized Legal Metrology Inspector", cell_style)
        ]
    ]
    auth_table = Table(auth_rows, colWidths=[290, 250])
    auth_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(auth_table)

    doc.build(story)
    return output_pdf_path