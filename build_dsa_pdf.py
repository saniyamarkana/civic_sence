"""
Builds the CivicSense DSA Explanation PDF directly matching DSA_IN_MY_PROJECT.md
File-by-file structure with code blocks and intuitive step-by-step explanations.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CivicSense_DSA_Architecture_and_Code_Explanation.pdf")

class NumberedCanvas(canvas.Canvas):
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
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "CIVICSENSE PROJECT — DSA FILE-BY-FILE EXPLANATION")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "CivicSense Municipal System · DSA Architecture Manual")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Colors
    c_primary = colors.HexColor("#0f172a")
    c_cyan = colors.HexColor("#0891b2")
    c_slate = colors.HexColor("#1e293b")
    c_border = colors.HexColor("#cbd5e1")
    c_code_bg = colors.HexColor("#f8fafc")

    # Typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=c_primary,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14
    )

    section_header_style = ParagraphStyle(
        'SecHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    subheading_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary,
        spaceBefore=6,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_slate,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0f172a"),
        backColor=c_code_bg,
        borderColor=c_border,
        borderWidth=0.5,
        borderPadding=7,
        spaceAfter=8
    )

    story = []

    # Title Banner
    story.append(Paragraph("DSA in CivicSense Project — File by File Explanation", title_style))
    story.append(Paragraph("A direct, comprehensive architectural manual detailing how each Data Structure and Algorithm file is implemented, how the code functions, and how it is applied in the live civic system.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_cyan, spaceAfter=14))

    # Read markdown source directly
    md_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "DSA_IN_MY_PROJECT.md")
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into sections by '---'
    sections = content.split("\n---\n")

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        lines = sec.split("\n")
        in_code_block = False
        code_lines = []

        for line in lines:
            line_str = line.strip()

            # Skip main header if already printed
            if line_str.startswith("# DSA in CivicSense Project"):
                continue

            # Code block toggles
            if line_str.startswith("```"):
                if in_code_block:
                    # End of code block: render it
                    formatted_code = "<br/>".join([c.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace(" ", "&nbsp;") for c in code_lines])
                    story.append(Paragraph(formatted_code, code_style))
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                    code_lines = []
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # Section Title (e.g. ### 1. dsa/linked_list.py...)
            if line_str.startswith("### "):
                clean_title = line_str.replace("### ", "").replace("**", "")
                story.append(Spacer(1, 6))
                story.append(Paragraph(clean_title, section_header_style))
                continue

            # Subheading (e.g. #### Its Code: or #### How to Understand This Code:)
            if line_str.startswith("#### "):
                clean_sub = line_str.replace("#### ", "").replace("**", "")
                story.append(Paragraph(f"<b>{clean_sub}</b>", subheading_style))
                continue

            # Bullet points (1. 2. 3. or -)
            if line_str.startswith(("1.", "2.", "3.", "4.", "5.", "-")):
                # Format bold text
                formatted_line = line_str
                # Replace markdown bold **text** with <b>text</b>
                parts = formatted_line.split("**")
                if len(parts) > 1:
                    new_line = ""
                    for i, p in enumerate(parts):
                        if i % 2 == 1:
                            new_line += f"<b>{p}</b>"
                        else:
                            new_line += p
                    formatted_line = new_line

                # Replace inline code `code` with <code>code</code>
                code_parts = formatted_line.split("`")
                if len(code_parts) > 1:
                    new_line = ""
                    for i, p in enumerate(code_parts):
                        if i % 2 == 1:
                            new_line += f'<font face="Courier" color="#0369a1">{p}</font>'
                        else:
                            new_line += p
                    formatted_line = new_line

                # Replace math $O(1)$ with O(1)
                formatted_line = formatted_line.replace("$O(1)$", "<b>O(1)</b>")
                formatted_line = formatted_line.replace("$O(n)$", "<b>O(n)</b>")
                formatted_line = formatted_line.replace("$O(\\log n)$", "<b>O(log n)</b>")
                formatted_line = formatted_line.replace("$O(n \\log n)$", "<b>O(n log n)</b>")
                formatted_line = formatted_line.replace("$O(n^2)$", "<b>O(n²)</b>")
                formatted_line = formatted_line.replace("$100$", "100")
                formatted_line = formatted_line.replace("$1,000$", "1,000")
                formatted_line = formatted_line.replace("$10$", "10")

                story.append(Paragraph(formatted_line, body_style))
                continue

            if line_str:
                story.append(Paragraph(line_str, body_style))

        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0"), spaceAfter=10))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built matching DSA_IN_MY_PROJECT.md: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_pdf()
