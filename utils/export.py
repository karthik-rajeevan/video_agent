import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate


def build_report(result: dict) -> dict:
    return {
        "title": result.get("title", "Untitled"),
        "summary": result.get("summary", ""),
        "action_items": result.get("action_items", ""),
        "key_decisions": result.get("key_decisions", ""),
        "open_questions": result.get("open_questions", ""),
        "transcript": result.get("transcript", ""),
    }


def export_txt(report: dict, path: str) -> str:
    parts = [
        f"AI MEETING ASSISTANT REPORT",
        f"=" * 40,
        f"Title   : {report['title']}",
        "",
        "SUMMARY",
        "-" * 40,
        report["summary"],
        "",
        "ACTION ITEMS",
        "-" * 40,
        report["action_items"],
        "",
        "KEY DECISIONS",
        "-" * 40,
        report["key_decisions"],
        "",
        "OPEN QUESTIONS",
        "-" * 40,
        report["open_questions"],
        "",
        "FULL TRANSCRIPT",
        "-" * 40,
        report["transcript"],
    ]
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    return path


def export_pdf(report: dict, path: str) -> str:
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"], fontSize=18, textColor=colors.HexColor("#5b21b6")
    )
    heading_style = ParagraphStyle(
        "Heading", parent=styles["Heading2"], fontSize=13, spaceBefore=14, textColor=colors.HexColor("#06b6d4")
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["BodyText"], fontSize=10, leading=15
    )

    def esc(text: str) -> str:
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    story = [
        Paragraph(f"AI MEETING ASSISTANT REPORT", title_style),
        Spacer(1, 6),
        Paragraph(f"Title: <b>{esc(report['title'])}</b>", body_style),
        Spacer(1, 12),
        Paragraph("Summary", heading_style),
        Paragraph(esc(report["summary"]) if report["summary"].strip() else "<i>No summary.</i>", body_style),
        Paragraph("Action Items", heading_style),
        Paragraph(esc(report["action_items"]) if report["action_items"].strip() else "<i>None.</i>", body_style),
        Paragraph("Key Decisions", heading_style),
        Paragraph(esc(report["key_decisions"]) if report["key_decisions"].strip() else "<i>None.</i>", body_style),
        Paragraph("Open Questions", heading_style),
        Paragraph(esc(report["open_questions"]) if report["open_questions"].strip() else "<i>None.</i>", body_style),
        Paragraph("Full Transcript", heading_style),
        Paragraph(esc(report["transcript"]) or "<i>No transcript.</i>", body_style),
    ]

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=inch, rightMargin=inch)
    doc.build(story)
    return path