import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors

# A4 dimensions in points: 595.275 x 841.889
PAGE_WIDTH, PAGE_HEIGHT = A4

def generate_pdf(submission, output_path, base_dir=None):
    """
    Generates a pixel-faithful A4 PDF confirmation letter matching the master reference.
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    img_dir = os.path.join(base_dir, "static", "images")
    header_img_path = os.path.join(img_dir, "header.jpg")
    footer_img_path = os.path.join(img_dir, "footer.jpg")
    sig_img_path = os.path.join(img_dir, "signature.jpg")
    stamp_img_path = os.path.join(img_dir, "stamp.jpg")

    # Fallback to PNG if JPG not found
    if not os.path.exists(header_img_path):
        header_img_path = os.path.join(img_dir, "header.png")
    if not os.path.exists(footer_img_path):
        footer_img_path = os.path.join(img_dir, "footer.png")
    if not os.path.exists(sig_img_path):
        sig_img_path = os.path.join(img_dir, "signature.png")
    if not os.path.exists(stamp_img_path):
        stamp_img_path = os.path.join(img_dir, "stamp.png")

    c = canvas.Canvas(output_path, pagesize=A4)

    # 1. Header Banner
    # Reference bbox: (72.0, 28.44, 601.2, 128.64) -> w=529.2, h=100.2, top y=841.89-28.44=813.45
    header_w = 529.2
    header_h = 100.2
    header_x = 72.0
    header_y = PAGE_HEIGHT - 28.44 - header_h
    if os.path.exists(header_img_path):
        c.drawImage(header_img_path, header_x, header_y, width=header_w, height=header_h, preserveAspectRatio=True)

    # 2. Document Title
    c.setFont("Times-Bold", 13.5)
    c.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 154.0, "INTERNSHIP CONFIRMATION LETTER")

    # 3. To, & Date:
    c.setFont("Times-Bold", 12)
    c.drawString(72.0, PAGE_HEIGHT - 182.0, "To,")

    # Date formatted (DD-MM-YYYY)
    current_date = datetime.now().strftime("%d-%m-%Y")
    c.drawString(434.0, PAGE_HEIGHT - 182.0, "Date:")
    c.setFont("Times-Roman", 12)
    c.drawString(465.0, PAGE_HEIGHT - 182.0, f" {current_date}")

    # Student Info (indented at x=108.0)
    full_name = submission.get("full_name", "Sheik")
    reg_no = submission.get("registration_number", "")
    degree_dept = submission.get("degree_department", "")
    inst_name = submission.get("institution_name", "")
    inst_loc = submission.get("institution_location", "")
    domain = submission.get("internship_domain", "Fullstack Development (python)")
    
    # Format start and end dates
    s_date_raw = submission.get("start_date", "")
    e_date_raw = submission.get("end_date", "")
    try:
        s_date_fmt = datetime.strptime(s_date_raw, "%Y-%m-%d").strftime("%d-%m-%Y")
    except Exception:
        s_date_fmt = s_date_raw
    try:
        e_date_fmt = datetime.strptime(e_date_raw, "%Y-%m-%d").strftime("%d-%m-%Y")
    except Exception:
        e_date_fmt = e_date_raw

    c.setFont("Times-Roman", 12)
    c.drawString(108.0, PAGE_HEIGHT - 196.0, f"{full_name},")
    c.drawString(108.0, PAGE_HEIGHT - 210.0, f"REG NO: {reg_no},")
    c.drawString(108.0, PAGE_HEIGHT - 224.0, f"{degree_dept},")
    c.drawString(108.0, PAGE_HEIGHT - 238.0, f"{inst_name},")
    c.drawString(108.0, PAGE_HEIGHT - 251.0, f"{inst_loc}.")

    # 4. Salutation
    c.drawString(72.0, PAGE_HEIGHT - 276.0, f"Dear {full_name},")

    # 5. First Paragraph (Using Paragraph flowable for perfect justified text wrapping)
    styles = getSampleStyleSheet()
    p1_style = ParagraphStyle(
        'RefPara1',
        fontName='Times-Roman',
        fontSize=11.1,
        leading=14.0,
        alignment=TA_LEFT,
        textColor=colors.black
    )
    
    p1_text = (
        f"We are pleased to confirm your selection for the <b>{domain} Internship "
        f"Program</b> at <b>Approtech R&amp;D Solutions Pvt. Ltd.</b>, Chennai. "
        f"This internship is designed to equip you with the fundamental knowledge and practical experience."
    )
    p1 = Paragraph(p1_text, p1_style)
    p1_w, p1_h = p1.wrap(447.2, 200)
    p1.drawOn(c, 72.0, PAGE_HEIGHT - 296.0 - p1_h + 14.0)

    # 6. Heading: Internship Details
    details_y = PAGE_HEIGHT - 356.0
    c.setFont("Times-Bold", 13.4)
    c.drawString(72.0, details_y, "Internship Details")

    # 7. Bullets
    # Bullet 1: Internship Domain
    c.setFont("Symbol", 10)
    c.drawString(90.0, details_y - 24.0, "\xb7") # bullet
    c.setFont("Times-Bold", 12)
    c.drawString(108.0, details_y - 24.0, "Internship Domain:")
    c.drawString(212.0, details_y - 24.0, f" {domain}")

    # Bullet 2: Start Date
    c.setFont("Symbol", 10)
    c.drawString(90.0, details_y - 38.0, "\xb7")
    c.setFont("Times-Bold", 12)
    c.drawString(108.0, details_y - 38.0, "Start Date")
    c.drawString(205.0, details_y - 38.0, ":")
    c.setFont("Times-Roman", 12)
    c.drawString(212.0, details_y - 38.0, f" {s_date_fmt}")

    # Bullet 3: End Date
    c.setFont("Symbol", 10)
    c.drawString(90.0, details_y - 52.0, "\xb7")
    c.setFont("Times-Bold", 12)
    c.drawString(108.0, details_y - 52.0, "End Date")
    c.drawString(205.0, details_y - 52.0, ":")
    c.setFont("Times-Roman", 12)
    c.drawString(212.0, details_y - 52.0, f" {e_date_fmt}")

    # 8. Location
    loc_y = details_y - 75.0
    c.setFont("Times-Bold", 12)
    c.drawString(72.0, loc_y, "Location:")
    c.setFont("Times-Roman", 12)
    c.drawString(124.0, loc_y, " Approtech R&D Solutions Pvt. Ltd., Chennai")

    # 9. Second Paragraph
    p2_text = (
        "The internship will provide you with practical exposure to industry practices and "
        "hands-on training to build your professional skills."
    )
    p2 = Paragraph(p2_text, p1_style)
    p2_w, p2_h = p2.wrap(447.2, 100)
    p2.drawOn(c, 72.0, loc_y - 28.0 - p2_h + 14.0)

    # 10. Bring printed copy instruction
    inst_y = loc_y - 66.0
    c.setFont("Times-Roman", 12)
    c.drawString(72.0, inst_y, "Please bring a printed copy of this letter and your college ID on the first day.")

    # 11. Participation & Warm regards
    c.drawString(72.0, inst_y - 28.0, "We look forward to your participation!")
    c.drawString(72.0, inst_y - 56.0, "Warm regards,")

    # 12. Signature and Stamp
    # In reference:
    # Signature: (72.0, 592.8, 171.0, 657.36) -> w=99, h=64.5 -> ReportLab y = 841.89 - 657.36 = 184.5
    # Stamp: (213.0, 577.8, 299.28, 657.36) -> w=86.3, h=79.6 -> ReportLab y = 841.89 - 657.36 = 184.5
    sig_y = PAGE_HEIGHT - 657.36
    if os.path.exists(sig_img_path):
        c.drawImage(sig_img_path, 72.0, sig_y, width=99.0, height=64.56, mask='auto', preserveAspectRatio=True)
    if os.path.exists(stamp_img_path):
        c.drawImage(stamp_img_path, 213.0, sig_y, width=86.28, height=79.56, mask='auto', preserveAspectRatio=True)

    # 13. Authorized Signatory Text
    c.setFont("Times-Roman", 12)
    c.drawString(72.0, PAGE_HEIGHT - 669.0, "Authorized Signatory")
    c.drawString(72.0, PAGE_HEIGHT - 696.0, "Approtech R&D Solutions Pvt. Ltd")

    # 14. Footer Banner
    # Reference: bbox (72.0, 714.96, 565.44, 799.56) -> w=493.44, h=84.6
    footer_w = 493.44
    footer_h = 84.6
    footer_x = 72.0
    footer_y = PAGE_HEIGHT - 799.56
    if os.path.exists(footer_img_path):
        c.drawImage(footer_img_path, footer_x, footer_y, width=footer_w, height=footer_h, preserveAspectRatio=True)

    c.showPage()
    c.save()
    return output_path
