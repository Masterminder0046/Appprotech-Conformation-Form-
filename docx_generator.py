import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=0, bottom=0, left=0, right=0):
    """Set cell margins in twips."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def remove_table_borders(table):
    """Remove all borders from a table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(r'''
        <w:tblBorders %s>
            <w:top w:val="none"/>
            <w:left w:val="none"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
            <w:insideH w:val="none"/>
            <w:insideV w:val="none"/>
        </w:tblBorders>
    ''' % nsdecls('w'))
    tblPr.append(borders)

def generate_docx(submission, output_path, base_dir=None):
    """
    Generates a high-fidelity editable Word (.docx) confirmation letter.
    """
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    img_dir = os.path.join(base_dir, "static", "images")
    header_img = os.path.join(img_dir, "header.jpg")
    footer_img = os.path.join(img_dir, "footer.jpg")
    sig_img = os.path.join(img_dir, "signature.jpg")
    stamp_img = os.path.join(img_dir, "stamp.jpg")

    if not os.path.exists(header_img):
        header_img = os.path.join(img_dir, "header.png")
    if not os.path.exists(footer_img):
        footer_img = os.path.join(img_dir, "footer.png")
    if not os.path.exists(sig_img):
        sig_img = os.path.join(img_dir, "signature.png")
    if not os.path.exists(stamp_img):
        stamp_img = os.path.join(img_dir, "stamp.png")

    doc = Document()

    # Page Setup: A4 Portrait, ~0.65 to 0.75 in margins
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.4)
    section.bottom_margin = Inches(0.4)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    # Base font: Times New Roman
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].font.size = Pt(12)
    doc.styles['Normal'].font.color.rgb = RGBColor(0, 0, 0)

    content_width = Inches(6.67)

    # 1. Header Banner Image
    if os.path.exists(header_img):
        p_hdr = doc.add_paragraph()
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hdr.paragraph_format.space_before = Pt(0)
        p_hdr.paragraph_format.space_after = Pt(14)
        run_hdr = p_hdr.add_run()
        run_hdr.add_picture(header_img, width=content_width)

    # 2. Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(14)
    run_title = p_title.add_run("INTERNSHIP CONFIRMATION LETTER")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(13.5)
    run_title.bold = True

    # 3. To, & Date: Table (Borderless)
    current_date = datetime.now().strftime("%d-%m-%Y")
    full_name = submission.get("full_name", "Sheik")
    reg_no = submission.get("registration_number", "")
    degree_dept = submission.get("degree_department", "")
    inst_name = submission.get("institution_name", "")
    inst_loc = submission.get("institution_location", "")
    domain = submission.get("internship_domain", "Fullstack Development (python)")

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

    to_table = doc.add_table(rows=1, cols=2)
    to_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(to_table)
    to_table.autofit = False

    cell_left = to_table.rows[0].cells[0]
    cell_right = to_table.rows[0].cells[1]
    cell_left.width = Inches(4.5)
    cell_right.width = Inches(2.17)
    set_cell_margins(cell_left, 0, 0, 0, 0)
    set_cell_margins(cell_right, 0, 0, 0, 0)

    # Left cell: To, and indented details
    p_to = cell_left.paragraphs[0]
    p_to.paragraph_format.space_before = Pt(0)
    p_to.paragraph_format.space_after = Pt(2)
    p_to.paragraph_format.line_spacing = 1.15
    run_to = p_to.add_run("To,")
    run_to.bold = True

    details_lines = [
        f"{full_name},",
        f"REG NO: {reg_no},",
        f"{degree_dept},",
        f"{inst_name},",
        f"{inst_loc}."
    ]
    for line in details_lines:
        p_line = cell_left.add_paragraph()
        p_line.paragraph_format.left_indent = Inches(0.4)
        p_line.paragraph_format.space_before = Pt(0)
        p_line.paragraph_format.space_after = Pt(2)
        p_line.paragraph_format.line_spacing = 1.15
        run_l = p_line.add_run(line)
        run_l.font.name = 'Times New Roman'
        run_l.font.size = Pt(11.5)

    # Right cell: Date
    p_date = cell_right.paragraphs[0]
    p_date.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_date.paragraph_format.space_before = Pt(0)
    p_date.paragraph_format.space_after = Pt(0)
    run_date_lbl = p_date.add_run("Date: ")
    run_date_lbl.bold = True
    run_date_val = p_date.add_run(current_date)
    run_date_val.bold = False

    # 4. Salutation
    p_salut = doc.add_paragraph()
    p_salut.paragraph_format.space_before = Pt(10)
    p_salut.paragraph_format.space_after = Pt(6)
    p_salut.add_run(f"Dear {full_name},")

    # 5. First Paragraph
    p1 = doc.add_paragraph()
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(10)
    p1.paragraph_format.line_spacing = 1.15
    p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    p1.add_run("We are pleased to confirm your selection for the ")
    run_dom = p1.add_run(f"{domain} Internship Program")
    run_dom.bold = True
    p1.add_run(" at ")
    run_comp = p1.add_run("Approtech R&D Solutions Pvt. Ltd.")
    run_comp.bold = True
    p1.add_run(", Chennai. This internship is designed to equip you with the fundamental knowledge and practical experience.")

    # 6. Heading: Internship Details
    p_det_h = doc.add_paragraph()
    p_det_h.paragraph_format.space_before = Pt(6)
    p_det_h.paragraph_format.space_after = Pt(4)
    run_det_h = p_det_h.add_run("Internship Details")
    run_det_h.bold = True
    run_det_h.font.size = Pt(13)

    # 7. Bullets
    bullets = [
        ("Internship Domain: ", domain, True),
        ("Start Date : ", s_date_fmt, False),
        ("End Date   : ", e_date_fmt, False)
    ]
    for label, val, is_val_bold in bullets:
        p_b = doc.add_paragraph()
        p_b.paragraph_format.left_indent = Inches(0.4)
        p_b.paragraph_format.space_before = Pt(1)
        p_b.paragraph_format.space_after = Pt(2)
        p_b.paragraph_format.line_spacing = 1.15
        
        # bullet symbol
        run_sym = p_b.add_run("•  ")
        run_sym.bold = True
        
        run_lbl = p_b.add_run(label)
        run_lbl.bold = True
        
        run_v = p_b.add_run(val)
        run_v.bold = is_val_bold

    # 8. Location
    p_loc = doc.add_paragraph()
    p_loc.paragraph_format.space_before = Pt(8)
    p_loc.paragraph_format.space_after = Pt(8)
    run_loc_lbl = p_loc.add_run("Location: ")
    run_loc_lbl.bold = True
    p_loc.add_run("Approtech R&D Solutions Pvt. Ltd., Chennai")

    # 9. Second Paragraph
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_before = Pt(0)
    p2.paragraph_format.space_after = Pt(8)
    p2.paragraph_format.line_spacing = 1.15
    p2.add_run("The internship will provide you with practical exposure to industry practices and hands-on training to build your professional skills.")

    # 10. Instruction & Closing
    p3 = doc.add_paragraph()
    p3.paragraph_format.space_before = Pt(0)
    p3.paragraph_format.space_after = Pt(8)
    p3.add_run("Please bring a printed copy of this letter and your college ID on the first day.")

    p4 = doc.add_paragraph()
    p4.paragraph_format.space_before = Pt(0)
    p4.paragraph_format.space_after = Pt(8)
    p4.add_run("We look forward to your participation!")

    p_warm = doc.add_paragraph()
    p_warm.paragraph_format.space_before = Pt(0)
    p_warm.paragraph_format.space_after = Pt(4)
    p_warm.add_run("Warm regards,")

    # 11. Signature & Stamp (Side-by-side Table)
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.LEFT
    remove_table_borders(sig_table)
    cell_sig = sig_table.rows[0].cells[0]
    cell_stmp = sig_table.rows[0].cells[1]
    cell_sig.width = Inches(1.8)
    cell_stmp.width = Inches(2.2)
    set_cell_margins(cell_sig, 0, 0, 0, 0)
    set_cell_margins(cell_stmp, 0, 0, 0, 0)

    if os.path.exists(sig_img):
        p_sig = cell_sig.paragraphs[0]
        p_sig.paragraph_format.space_before = Pt(0)
        p_sig.paragraph_format.space_after = Pt(0)
        p_sig.add_run().add_picture(sig_img, width=Inches(1.4))

    if os.path.exists(stamp_img):
        p_stmp = cell_stmp.paragraphs[0]
        p_stmp.paragraph_format.space_before = Pt(0)
        p_stmp.paragraph_format.space_after = Pt(0)
        p_stmp.add_run().add_picture(stamp_img, width=Inches(1.2))

    # 12. Authorized Signatory text
    p_auth = doc.add_paragraph()
    p_auth.paragraph_format.space_before = Pt(2)
    p_auth.paragraph_format.space_after = Pt(1)
    p_auth.add_run("Authorized Signatory")

    p_comp_sign = doc.add_paragraph()
    p_comp_sign.paragraph_format.space_before = Pt(0)
    p_comp_sign.paragraph_format.space_after = Pt(10)
    p_comp_sign.add_run("Approtech R&D Solutions Pvt. Ltd")

    # 13. Footer Banner Image
    if os.path.exists(footer_img):
        p_ftr = doc.add_paragraph()
        p_ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ftr.paragraph_format.space_before = Pt(4)
        p_ftr.paragraph_format.space_after = Pt(0)
        run_ftr = p_ftr.add_run()
        run_ftr.add_picture(footer_img, width=content_width)

    doc.save(output_path)
    return output_path
