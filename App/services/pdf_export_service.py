import io
import html
import re
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

PURPLE = colors.HexColor("#6C3EB5")
DARK = colors.HexColor("#222222")
GREY = colors.HexColor("#666666")


def _markdown_to_plain(text: str) -> str:
    """Cleans markdown/HTML artifacts so reportlab's paragraph parser doesn't choke."""
    # Normalize all dash-like/hyphen-like unicode characters to a plain ASCII hyphen
    for ch in ["\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "■"]:
        text = text.replace(ch, "-")

    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')

    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")

    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

    # Remove table/divider separator lines (dashes, pipes, colons, spaces only)
    # Must run BEFORE pipe-to-space conversion below
    text = re.sub(r"^[\s\|\-:]{3,}$", "", text, flags=re.MULTILINE)

    text = text.replace("**", "")
    text = re.sub(r"(?<!\*)\*(?!\*)", "", text)

    # Convert markdown links [text](url) into "text (url)"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)

    text = text.replace("|", "  ")

    text = html.escape(text, quote=False)
    return text


def _escape_only(text: str) -> str:
    """Minimal cleaning for short strings (ATS fields) - just remove dashes/HTML tags and escape."""
    for ch in ["\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2015", "■"]:
        text = text.replace(ch, "-")
    text = text.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")
    text = text.replace("**", "")
    text = re.sub(r"(?<!\*)\*(?!\*)", "", text)
    text = html.escape(text, quote=False)
    return text


def generate_report_pdf(
    career_report: str = None,
    job_results: str = None,
    ats_result=None,
    cover_letter: str = None,
    candidate_name: str = "Candidate",
) -> bytes:
    """
    Builds a single PDF combining whichever sections are available:
    Career Evaluation Report, Job Search Results, ATS Score.
    Returns the PDF as bytes, ready for Streamlit's download_button.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], textColor=PURPLE, fontSize=20, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"], textColor=GREY, fontSize=10, spaceAfter=16
    )
    section_heading = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"], textColor=PURPLE, fontSize=15,
        spaceBefore=14, spaceAfter=8
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["Normal"], fontSize=10, textColor=DARK,
        leading=14, alignment=TA_LEFT, spaceAfter=6
    )

    story = []

    story.append(Paragraph("UniAgent — Career Report", title_style))
    story.append(Paragraph(
        f"Prepared for: {candidate_name} · Generated on {datetime.now().strftime('%d %B %Y')}",
        subtitle_style
    ))

    def add_section(title: str, content: str):
        story.append(Paragraph(title, section_heading))
        cleaned = _markdown_to_plain(content)
        for para in cleaned.split("\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 6))

    if career_report:
        add_section("Career Evaluation Report", career_report)
        story.append(PageBreak())

    if job_results:
        add_section("Job Search Results", job_results)

    if ats_result:
        story.append(PageBreak())
        story.append(Paragraph("ATS Score Check", section_heading))
        story.append(Paragraph(f"Overall Score: {ats_result.overall_score}/100", body_style))
        story.append(Paragraph(f"Format Score: {ats_result.format_score}/100", body_style))
        if ats_result.keyword_match_score is not None:
            story.append(Paragraph(f"Keyword Match: {ats_result.keyword_match_score}/100", body_style))

        if ats_result.format_issues:
            story.append(Spacer(1, 8))
            story.append(Paragraph("Format Issues:", body_style))
            for issue in ats_result.format_issues:
                story.append(Paragraph(f"• {_escape_only(issue)}", body_style))

        if ats_result.recommendations:
            story.append(Spacer(1, 8))
            story.append(Paragraph("Recommendations:", body_style))
            for rec in ats_result.recommendations:
                story.append(Paragraph(f"• {_escape_only(rec)}", body_style))

    if cover_letter:
        story.append(PageBreak())
        add_section("Cover Letter", cover_letter)

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()