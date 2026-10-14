import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
import qrcode
from PIL import Image as PILImage

# Primary brand colors (MedCare Khairpur palette)
COLOR_NAVY_DARK = colors.HexColor('#102146')
COLOR_NAVY      = colors.HexColor('#1F3971')
COLOR_NAVY_LIGHT= colors.HexColor('#2A4D96')
COLOR_RED       = colors.HexColor('#E53935')
COLOR_YELLOW    = colors.HexColor('#FFAE27')
COLOR_GREEN     = colors.HexColor('#10B981')
COLOR_GRAY_BG   = colors.HexColor('#F8FAFC')
COLOR_BORDER    = colors.HexColor('#E2E8F0')
COLOR_TEXT_DARK = colors.HexColor('#0F172A')
COLOR_TEXT_MUTED= colors.HexColor('#64748B')
COLOR_WHITE     = colors.HexColor('#FFFFFF')

# Priority Colors
COLOR_CRITICAL  = colors.HexColor('#DC2626')
COLOR_HIGH      = colors.HexColor('#EA580C')
COLOR_MEDIUM    = colors.HexColor('#CA8A04')
COLOR_LOW       = colors.HexColor('#16A34A')


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_TEXT_MUTED)

        # Top thin decorative bar
        self.setFillColor(COLOR_NAVY)
        self.rect(36, self._pagesize[1] - 18, self._pagesize[0] - 72, 3, stroke=0, fill=1)
        self.setFillColor(COLOR_YELLOW)
        self.rect(36, self._pagesize[1] - 18, 90, 3, stroke=0, fill=1)

        # Bottom footer separator
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.75)
        self.line(36, 38, self._pagesize[0] - 36, 38)

        # Footer Left: MedCare Helpline & System notice
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(COLOR_NAVY)
        self.drawString(36, 26, "MEDCARE KHAIRPUR")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(COLOR_TEXT_MUTED)
        self.drawString(125, 26, "| Emergency Directorate 24/7 Hotline: +92 300 1234567 / 1122 | Official Record")

        # Footer Right: Page X of Y
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(self._pagesize[0] - 36, 26, page_str)
        self.restoreState()


def _get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=COLOR_NAVY_DARK,
    ))

    styles.add(ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=COLOR_TEXT_MUTED,
    ))

    styles.add(ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=COLOR_NAVY,
        spaceBefore=8,
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=COLOR_WHITE,
        alignment=0,
    ))

    styles.add(ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_TEXT_DARK,
    ))

    styles.add(ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_TEXT_DARK,
    ))

    styles.add(ParagraphStyle(
        'TableCellMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=8.5,
        textColor=COLOR_TEXT_MUTED,
    ))

    styles.add(ParagraphStyle(
        'BadgeText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=8.5,
        alignment=1,
    ))

    styles.add(ParagraphStyle(
        'KeyLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=COLOR_TEXT_MUTED,
    ))

    styles.add(ParagraphStyle(
        'ValText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10.5,
        textColor=COLOR_TEXT_DARK,
    ))

    return styles


def _create_qr_flowable(data, size=64):
    """Create a flowable Image containing a QR code for the given data."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=1,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#102146", back_color="#FFFFFF")
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return Image(buf, width=size, height=size)
    except Exception:
        return None


def _build_header(logo_path, report_title, report_subtitle, styles, width=523):
    """Builds the official MedCare header with logo & institutional details."""
    logo_flowable = None
    if logo_path and os.path.exists(logo_path):
        try:
            # Aspect ratio for ~2142x734 is roughly 2.9:1
            logo_flowable = Image(logo_path, width=130, height=44)
        except Exception:
            logo_flowable = None

    title_block = [
        Paragraph(report_title, styles['DocTitle']),
        Spacer(1, 2),
        Paragraph(report_subtitle, styles['DocSub']),
        Paragraph("MedCare Khairpur Emergency Resource Directorate · Sindh Health Network", styles['TableCellMuted']),
    ]

    if logo_flowable:
        data = [[logo_flowable, title_block]]
        col_widths = [140, width - 140]
    else:
        badge_p = Paragraph("<font color='#E53935'><b>[+] MEDCARE 24/7</b></font><br/><font color='#1F3971'><b>KHAIRPUR</b></font>", styles['DocTitle'])
        data = [[badge_p, title_block]]
        col_widths = [110, width - 110]

    header_table = Table(data, colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    return header_table


# =========================================================================
# 1. EMERGENCY CASES REGISTRY & TRIAGE REPORT (PDF LIST)
# =========================================================================

def generate_cases_pdf(cases, priority_filter='all', logo_path=None, generated_by='Admin Desk'):
    """
    Generates a smart, professional PDF of all or filtered emergency cases.
    Returns: BytesIO buffer containing the PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=28,
        bottomMargin=46,
    )

    styles = _get_styles()
    story = []
    content_width = 523  # A4 width (595.27) - 72pt margins

    # --- Header ---
    title = "EMERGENCY CASES REGISTRY REPORT"
    subtitle = f"Filter Scope: <b>{priority_filter.upper()}</b> · Official Audit & Triage Manifest"
    story.append(_build_header(logo_path, title, subtitle, styles, width=content_width))
    story.append(Spacer(1, 6))

    # --- Metadata Strip & Stats Counters ---
    now_str = datetime.utcnow().strftime('%d %b %Y, %I:%M %p UTC')
    
    total = len(cases)
    crit = sum(1 for c in cases if c.priority == 'Critical')
    high = sum(1 for c in cases if c.priority == 'High')
    med  = sum(1 for c in cases if c.priority == 'Medium')
    low  = sum(1 for c in cases if c.priority == 'Low')
    active = sum(1 for c in cases if c.status in ('Active', 'Dispatched', 'Incoming'))
    closed = sum(1 for c in cases if c.status == 'Closed')

    meta_text = (
        f"<b>Generated:</b> {now_str} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Staff Operator:</b> {generated_by} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>System:</b> MedCare Khairpur Node 01"
    )

    meta_table = Table(
        [[Paragraph(meta_text, styles['DocSub'])]],
        colWidths=[content_width]
    )
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_GRAY_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # --- KPI Stats Row ---
    stats_data = [
        [
            Paragraph("<font size=6 color='#64748B'>TOTAL CASES</font><br/><b>" + str(total) + "</b>", styles['BadgeText']),
            Paragraph("<font size=6 color='#DC2626'>CRITICAL</font><br/><b>" + str(crit) + "</b>", styles['BadgeText']),
            Paragraph("<font size=6 color='#EA580C'>HIGH</font><br/><b>" + str(high) + "</b>", styles['BadgeText']),
            Paragraph("<font size=6 color='#CA8A04'>MEDIUM</font><br/><b>" + str(med) + "</b>", styles['BadgeText']),
            Paragraph("<font size=6 color='#16A34A'>LOW</font><br/><b>" + str(low) + "</b>", styles['BadgeText']),
            Paragraph("<font size=6 color='#1F3971'>ACTIVE / IN ROUTE</font><br/><b>" + str(active) + "</b>", styles['BadgeText']),
            Paragraph("<font size=6 color='#64748B'>RESOLVED / CLOSED</font><br/><b>" + str(closed) + "</b>", styles['BadgeText']),
        ]
    ]
    stat_w = content_width / 7.0
    stats_table = Table(stats_data, colWidths=[stat_w]*7)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 10))

    # --- Cases Table ---
    # Col widths sum to 523:
    # Code (42), Patient & Age (100), Priority (48), Status (52), Condition (115), Doctor (76), Bed/Amb (90)
    col_widths = [40, 100, 48, 52, 115, 78, 90]
    
    headers = [
        Paragraph("<b>Code</b>", styles['TableHeader']),
        Paragraph("<b>Patient Name & Age</b>", styles['TableHeader']),
        Paragraph("<b>Priority</b>", styles['TableHeader']),
        Paragraph("<b>Status</b>", styles['TableHeader']),
        Paragraph("<b>Symptoms / Condition</b>", styles['TableHeader']),
        Paragraph("<b>Assigned Doctor</b>", styles['TableHeader']),
        Paragraph("<b>Bed & Ambulance</b>", styles['TableHeader']),
    ]
    table_rows = [headers]

    for c in cases:
        # Priority badge style
        p_color = '#16A34A'
        if c.priority == 'Critical': p_color = '#DC2626'
        elif c.priority == 'High':   p_color = '#EA580C'
        elif c.priority == 'Medium': p_color = '#CA8A04'
        p_p = Paragraph(f"<font color='{p_color}'><b>● {c.priority}</b></font>", styles['TableCellBold'])

        # Status
        s_color = '#2563EB'
        if c.status == 'Dispatched': s_color = '#DC2626'
        elif c.status == 'Incoming': s_color = '#B45309'
        elif c.status == 'Closed':   s_color = '#64748B'
        s_p = Paragraph(f"<font color='{s_color}'><b>{c.status}</b></font>", styles['TableCellBold'])

        # Patient
        pat_p = Paragraph(f"<b>{c.patient_name}</b><br/><font color='#64748B'>{c.age} yrs</font>", styles['TableCell'])

        # Condition
        cond_text = (c.condition or 'Emergency triage')[:75]
        if len(c.condition or '') > 75: cond_text += '...'
        cond_p = Paragraph(cond_text, styles['TableCell'])

        # Doctor
        doc_name = c.doctor.name if c.doctor else "—"
        doc_p = Paragraph(f"<b>{doc_name}</b>", styles['TableCell'])

        # Bed & Ambulance
        bed_str = f"Bed {c.bed.bed_code}" if c.bed else "No Bed"
        amb_str = f"Amb: {c.ambulance.vehicle_id or c.ambulance.name}" if c.ambulance else "No Amb"
        alloc_p = Paragraph(f"{bed_str}<br/><font color='#64748B'>{amb_str}</font>", styles['TableCell'])

        code_p = Paragraph(f"<b>{c.case_code}</b>", styles['TableCellBold'])

        table_rows.append([code_p, pat_p, p_p, s_p, cond_p, doc_p, alloc_p])

    if len(cases) == 0:
        table_rows.append([
            Paragraph("—", styles['TableCell']),
            Paragraph("No emergency cases recorded under this scope.", styles['TableCellMuted']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
        ])

    cases_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 0.75, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]

    # Alternating row colors
    for i in range(1, len(table_rows)):
        bg = COLOR_WHITE if i % 2 == 1 else COLOR_GRAY_BG
        t_style.append(('BACKGROUND', (0, i), (-1, i), bg))

    cases_table.setStyle(TableStyle(t_style))
    story.append(cases_table)
    story.append(Spacer(1, 14))

    # --- Institutional Sign-off Block ---
    sign_data = [
        [
            Paragraph("<b>MedCare Emergency Directorate - Khairpur</b><br/><font color='#64748B' size=6.5>Verified via Automated Triage Algorithm HT-03<br/>Official Sindh Medical Emergency Network Document</font>", styles['DocSub']),
            Paragraph("<b>Authorized Verification Seal</b><br/><font color='#64748B' size=6.5>MedCare Chief Medical Officer / Admin Desk<br/>Status: Electronically Certified</font>", styles['DocSub']),
        ]
    ]
    sign_table = Table(sign_data, colWidths=[content_width*0.6, content_width*0.4])
    sign_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(sign_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


# =========================================================================
# 2. SINGLE PATIENT EMERGENCY INTAKE & DISPATCH SLIP (PDF)
# =========================================================================

def generate_single_case_pdf(case, logo_path=None, track_url=None):
    """
    Generates an official, smart 1-page Patient Emergency Intake & Dispatch Slip.
    Returns: BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=26,
        bottomMargin=40,
    )

    styles = _get_styles()
    story = []
    content_width = 540  # Letter width (612) - 72pt

    # --- Header ---
    title = f"EMERGENCY INTAKE & DISPATCH SLIP"
    subtitle = f"Official Patient Medical Emergency Ticket · Case Reference: <b>{case.case_code}</b>"
    story.append(_build_header(logo_path, title, subtitle, styles, width=content_width))
    story.append(Spacer(1, 8))

    # --- Urgent Top Banner with QR Code ---
    qr_data = track_url if track_url else f"https://medcare-khairpur.gov.pk/track/{case.case_code}"
    qr_flowable = _create_qr_flowable(qr_data, size=64)

    # Priority styling
    p_color = '#16A34A'
    p_bg = '#F0FDF4'
    if case.priority == 'Critical':
        p_color = '#DC2626'; p_bg = '#FEF2F2'
    elif case.priority == 'High':
        p_color = '#EA580C'; p_bg = '#FFF7ED'
    elif case.priority == 'Medium':
        p_color = '#CA8A04'; p_bg = '#FEFCE8'

    banner_left = [
        Paragraph(f"<font size=13 color='#102146'><b>CASE FILE: #{case.case_code}</b></font>", styles['Normal']),
        Spacer(1, 3),
        Paragraph(f"Triage Level: <font color='{p_color}'><b>● {case.priority.upper()} PRIORITY</b></font> &nbsp;&nbsp;|&nbsp;&nbsp; Current Status: <b>{case.status.upper()}</b>", styles['DocSub']),
        Paragraph(f"Intake Logged: <b>{case.registered_at.strftime('%d %B %Y at %I:%M %p') if case.registered_at else 'Active'}</b>", styles['TableCellMuted']),
    ]

    banner_cells = [[banner_left, qr_flowable or Paragraph("", styles['Normal'])]]
    banner_table = Table(banner_cells, colWidths=[content_width - 80, 80])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(p_bg)),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(p_color)),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 10))

    # --- Section 1: Patient Demographics & Location ---
    story.append(Paragraph("1. PATIENT DEMOGRAPHICS & INCIDENT LOCATION", styles['SectionHeading']))
    
    pat_phone = getattr(case, 'patient_phone', None) or 'Not Specified'
    pat_data = [
        [
            Paragraph("Patient Name", styles['KeyLabel']),
            Paragraph(f"<b>{case.patient_name}</b>", styles['ValText']),
            Paragraph("Patient Age / Gender", styles['KeyLabel']),
            Paragraph(f"{case.age} Years", styles['ValText']),
        ],
        [
            Paragraph("Contact Phone", styles['KeyLabel']),
            Paragraph(f"<b>{pat_phone}</b>", styles['ValText']),
            Paragraph("Incident Location", styles['KeyLabel']),
            Paragraph(f"{case.patient_address or 'Khairpur Urban Zone'}", styles['TableCellBold']),
        ],
        [
            Paragraph("GPS Coordinates", styles['KeyLabel']),
            Paragraph(f"{round(case.patient_lat, 4) if case.patient_lat else 27.5300}, {round(case.patient_lng, 4) if case.patient_lng else 68.7600}", styles['TableCell']),
            Paragraph("Triage Priority", styles['KeyLabel']),
            Paragraph(f"<b>{case.priority}</b>", styles['ValText']),
        ]
    ]
    col_w_2 = [110, 160, 110, 160]
    pat_table = Table(pat_data, colWidths=col_w_2)
    pat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_GRAY_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(pat_table)
    story.append(Spacer(1, 10))

    # --- Section 2: Clinical Symptoms & Condition ---
    story.append(Paragraph("2. CLINICAL TRIAGE & REPORTED SYMPTOMS", styles['SectionHeading']))
    
    cond_text = case.condition or "Patient presented with acute medical emergency symptoms."
    clinical_data = [
        [
            Paragraph("Reported Condition / Chief Complaint:", styles['KeyLabel']),
        ],
        [
            Paragraph(f"<b>{cond_text}</b>", styles['TableCell']),
        ]
    ]
    clinical_table = Table(clinical_data, colWidths=[content_width])
    clinical_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_WHITE),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(clinical_table)
    story.append(Spacer(1, 10))

    # --- Section 3: Allocated Emergency Resources ---
    story.append(Paragraph("3. ALLOCATED EMERGENCY HEALTHCARE RESOURCES", styles['SectionHeading']))

    hosp_name = case.hospital_name or "Khairpur Medical Complex (KMC)"
    doc_name = case.doctor.name if case.doctor else "On-Duty Emergency Medical Officer"
    doc_spec = case.doctor.specialty if case.doctor and case.doctor.specialty else "Emergency Medicine"
    bed_name = f"Bed {case.bed.bed_code} ({case.bed.bed_type} Ward)" if case.bed else "Pending Bed Allocation"
    
    amb_name = "No Ambulance Required / Self-Transport"
    if case.ambulance:
        amb_name = f"Unit {case.ambulance.vehicle_id or case.ambulance.name} ({case.ambulance.vehicle_type or 'ALS'} Unit)"
    elif case.needs_ambulance:
        amb_name = "Dispatch In Queue (Awaiting unit release)"

    resource_data = [
        [
            Paragraph("Assigned Hospital", styles['KeyLabel']),
            Paragraph(f"<b>{hosp_name}</b>", styles['ValText']),
            Paragraph("Attending Doctor", styles['KeyLabel']),
            Paragraph(f"<b>{doc_name}</b><br/><font size=6.5 color='#64748B'>{doc_spec}</font>", styles['TableCellBold']),
        ],
        [
            Paragraph("Reserved Bed", styles['KeyLabel']),
            Paragraph(f"<b>{bed_name}</b>", styles['TableCellBold']),
            Paragraph("Dispatched Ambulance", styles['KeyLabel']),
            Paragraph(f"<b>{amb_name}</b>", styles['TableCellBold']),
        ]
    ]
    res_table = Table(resource_data, colWidths=col_w_2)
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_GRAY_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(res_table)
    story.append(Spacer(1, 10))

    # --- Section 4: Handover Protocol & Critical Emergency Instructions ---
    story.append(Paragraph("4. PATIENT ATTENDANT & HOSPITAL HANDOVER PROTOCOL", styles['SectionHeading']))
    
    protocol_text = (
        "<b>1.</b> Keep this official emergency slip or its reference QR code ready upon arrival at the emergency triage desk.<br/>"
        "<b>2.</b> Ambulance crew and hospital ER staff are synchronised in real-time via the MedCare Khairpur Network.<br/>"
        "<b>3.</b> For updates or ambulance route assistance, call the 24/7 Directorate Emergency Dispatch Helpline: <b>+92 300 1234567</b> or <b>1122</b>.<br/>"
        "<b>4.</b> Official record generated electronically under Government of Sindh Healthcare Regulations."
    )
    protocol_table = Table([[Paragraph(protocol_text, styles['TableCell'])]], colWidths=[content_width])
    protocol_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(protocol_table)
    story.append(Spacer(1, 14))

    # --- Stamp / Signature Box ---
    sig_data = [
        [
            Paragraph("<b>MedCare Dispatch Officer</b><br/><font color='#64748B' size=6.5>Triage Operator Desk 01 · Khairpur Hub</font>", styles['DocSub']),
            Paragraph("<b>Receiving Hospital Emergency Desk</b><br/><font color='#64748B' size=6.5>Medical Officer Signature & Stamp</font>", styles['DocSub']),
            Paragraph("<b>QR Verification Code</b><br/><font color='#64748B' size=6.5>Scan to track ambulance in real-time</font>", styles['DocSub']),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[content_width*0.35, content_width*0.35, content_width*0.30])
    sig_table.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sig_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


# =========================================================================
# 3. DOCTOR'S PATIENT ROSTER REPORT (PDF)
# =========================================================================

def generate_doctor_patients_pdf(doctor_user, cases, logo_path=None):
    """
    Generates a doctor's assigned patient roster & triage history report.
    Returns: BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=28,
        bottomMargin=46,
    )

    styles = _get_styles()
    story = []
    content_width = 523

    title = "PHYSICIAN PATIENT ROSTER REPORT"
    subtitle = f"Attending Physician: <b>{doctor_user.name}</b> ({doctor_user.specialty or 'Emergency Medicine'})"
    story.append(_build_header(logo_path, title, subtitle, styles, width=content_width))
    story.append(Spacer(1, 6))

    now_str = datetime.utcnow().strftime('%d %b %Y, %I:%M %p UTC')
    doc_info = (
        f"<b>Physician:</b> {doctor_user.name} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Specialty:</b> {doctor_user.specialty or 'Emergency'} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Contact:</b> {doctor_user.phone or 'Active on Duty'} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"<b>Reported:</b> {now_str}"
    )
    meta_table = Table([[Paragraph(doc_info, styles['DocSub'])]], colWidths=[content_width])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), COLOR_GRAY_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # Table of patients
    col_widths = [45, 110, 50, 55, 135, 60, 68]
    headers = [
        Paragraph("<b>Code</b>", styles['TableHeader']),
        Paragraph("<b>Patient Name & Age</b>", styles['TableHeader']),
        Paragraph("<b>Priority</b>", styles['TableHeader']),
        Paragraph("<b>Status</b>", styles['TableHeader']),
        Paragraph("<b>Clinical Condition</b>", styles['TableHeader']),
        Paragraph("<b>Bed Code</b>", styles['TableHeader']),
        Paragraph("<b>Intake Date</b>", styles['TableHeader']),
    ]
    table_rows = [headers]

    for c in cases:
        p_color = '#16A34A'
        if c.priority == 'Critical': p_color = '#DC2626'
        elif c.priority == 'High':   p_color = '#EA580C'
        elif c.priority == 'Medium': p_color = '#CA8A04'
        p_p = Paragraph(f"<font color='{p_color}'><b>● {c.priority}</b></font>", styles['TableCellBold'])

        s_p = Paragraph(f"<b>{c.status}</b>", styles['TableCellBold'])
        pat_p = Paragraph(f"<b>{c.patient_name}</b><br/><font color='#64748B'>{c.age} yrs</font>", styles['TableCell'])
        cond_p = Paragraph((c.condition or 'Emergency')[:80], styles['TableCell'])
        bed_str = f"{c.bed.bed_code} ({c.bed.bed_type})" if c.bed else "—"
        bed_p = Paragraph(bed_str, styles['TableCell'])
        date_str = c.registered_at.strftime('%d %b, %H:%M') if c.registered_at else "—"
        date_p = Paragraph(date_str, styles['TableCellMuted'])
        code_p = Paragraph(f"<b>{c.case_code}</b>", styles['TableCellBold'])

        table_rows.append([code_p, pat_p, p_p, s_p, cond_p, bed_p, date_p])

    if len(cases) == 0:
        table_rows.append([
            Paragraph("—", styles['TableCell']),
            Paragraph("No assigned patients currently on roster.", styles['TableCellMuted']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
            Paragraph("—", styles['TableCell']),
        ])

    patients_table = Table(table_rows, colWidths=col_widths, repeatRows=1)
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 0.75, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
    ]
    for i in range(1, len(table_rows)):
        bg = COLOR_WHITE if i % 2 == 1 else COLOR_GRAY_BG
        t_style.append(('BACKGROUND', (0, i), (-1, i), bg))
    patients_table.setStyle(TableStyle(t_style))
    story.append(patients_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer


# =========================================================================
# 4. HOSPITAL RESOURCE AUDIT & INVENTORY REPORT (PDF)
# =========================================================================

def generate_resources_pdf(beds, doctors, ambulances, logo_path=None):
    """
    Generates a full hospital resource audit report (Beds, Doctors, Ambulance Fleet).
    Returns: BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=28,
        bottomMargin=46,
    )

    styles = _get_styles()
    story = []
    content_width = 523

    title = "HOSPITAL EMERGENCY RESOURCE AUDIT REPORT"
    subtitle = "Khairpur Emergency Health Network · Real-Time Readiness Inventory"
    story.append(_build_header(logo_path, title, subtitle, styles, width=content_width))
    story.append(Spacer(1, 6))

    now_str = datetime.utcnow().strftime('%d %b %Y, %I:%M %p UTC')
    meta_text = f"<b>Audit Timestamp:</b> {now_str} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Facility:</b> MedCare Khairpur Central Emergency Hub"
    story.append(Table([[Paragraph(meta_text, styles['DocSub'])]], colWidths=[content_width], style=[
        ('BACKGROUND', (0,0), (-1,-1), COLOR_GRAY_BG),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 8))

    # 1. Beds Table
    story.append(Paragraph("1. HOSPITAL BEDS INVENTORY", styles['SectionHeading']))
    bed_headers = [
        Paragraph("<b>Bed Code</b>", styles['TableHeader']),
        Paragraph("<b>Category / Ward</b>", styles['TableHeader']),
        Paragraph("<b>Status</b>", styles['TableHeader']),
        Paragraph("<b>Assigned Case</b>", styles['TableHeader']),
    ]
    bed_rows = [bed_headers]
    for b in beds:
        st_color = '#10B981' if b.status == 'Available' else '#DC2626'
        case_txt = f"Case #{b.assigned_case_id}" if b.assigned_case_id else "Unassigned"
        bed_rows.append([
            Paragraph(f"<b>{b.bed_code}</b>", styles['TableCellBold']),
            Paragraph(b.bed_type, styles['TableCell']),
            Paragraph(f"<font color='{st_color}'><b>● {b.status}</b></font>", styles['TableCellBold']),
            Paragraph(case_txt, styles['TableCellMuted']),
        ])
    bed_table = Table(bed_rows, colWidths=[100, 150, 130, 143])
    bed_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(bed_table)
    story.append(Spacer(1, 10))

    # 2. Doctors Table
    story.append(Paragraph("2. MEDICAL SPECIALISTS & DOCTORS ROSTER", styles['SectionHeading']))
    doc_headers = [
        Paragraph("<b>Doctor Name</b>", styles['TableHeader']),
        Paragraph("<b>Specialty</b>", styles['TableHeader']),
        Paragraph("<b>Contact Phone</b>", styles['TableHeader']),
        Paragraph("<b>Duty Status</b>", styles['TableHeader']),
    ]
    doc_rows = [doc_headers]
    for d in doctors:
        st_color = '#10B981' if d.status == 'Available' else '#EA580C'
        doc_rows.append([
            Paragraph(f"<b>{d.name}</b>", styles['TableCellBold']),
            Paragraph(d.specialty or 'General Medicine', styles['TableCell']),
            Paragraph(d.phone or 'Active On Call', styles['TableCell']),
            Paragraph(f"<font color='{st_color}'><b>● {d.status}</b></font>", styles['TableCellBold']),
        ])
    doc_table = Table(doc_rows, colWidths=[140, 150, 120, 113])
    doc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(doc_table)
    story.append(Spacer(1, 10))

    # 3. Ambulance Fleet
    story.append(Paragraph("3. EMERGENCY AMBULANCE FLEET (10 UNITS)", styles['SectionHeading']))
    amb_headers = [
        Paragraph("<b>Unit Code</b>", styles['TableHeader']),
        Paragraph("<b>Vehicle Type</b>", styles['TableHeader']),
        Paragraph("<b>Current Status</b>", styles['TableHeader']),
        Paragraph("<b>Base GPS Position</b>", styles['TableHeader']),
    ]
    amb_rows = [amb_headers]
    for a in ambulances:
        st_color = '#10B981' if a.status == 'Available' else ('#DC2626' if a.status == 'On the way' else '#CA8A04')
        coords = f"{round(a.lat, 4)}, {round(a.lng, 4)}" if (a.lat and a.lng) else "Khairpur Hub"
        amb_rows.append([
            Paragraph(f"<b>{a.vehicle_id or a.name}</b>", styles['TableCellBold']),
            Paragraph(a.vehicle_type or 'ALS Unit', styles['TableCell']),
            Paragraph(f"<font color='{st_color}'><b>● {a.status}</b></font>", styles['TableCellBold']),
            Paragraph(coords, styles['TableCell']),
        ])
    amb_table = Table(amb_rows, colWidths=[120, 120, 140, 143])
    amb_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_NAVY),
        ('BOX', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(amb_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
