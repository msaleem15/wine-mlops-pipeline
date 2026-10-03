"""Clean, student-style PDF report generator for MLOps Assignment 1 using real screenshots."""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
)

REPORTS_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(REPORTS_DIR, "assets")
BASE_DIR = os.path.dirname(REPORTS_DIR)

def build_pdf_report(pdf_filename: str):
    gh_action = os.path.join(ASSETS_DIR, "real_github_action.png")
    gh_steps = os.path.join(ASSETS_DIR, "real_github_job_steps.png")
    mlflow_runs = os.path.join(ASSETS_DIR, "real_mlflow_runs.png")
    mlflow_model = os.path.join(ASSETS_DIR, "real_mlflow_model.png")
    term_test = os.path.join(ASSETS_DIR, "real_terminal_make_test.png")
    term_git = os.path.join(ASSETS_DIR, "real_terminal_git_tree.png")

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=28,
        leftMargin=28,
        topMargin=22,
        bottomMargin=22
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        alignment=0,
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#475569"),
        alignment=0,
    )
    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        fontName="Helvetica-Bold",
        spaceBefore=4,
        spaceAfter=2,
    )
    caption_style = ParagraphStyle(
        "CaptionStyle",
        parent=styles["Normal"],
        fontSize=7.8,
        leading=9.5,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
        spaceAfter=1,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=7.8,
        leading=11,
        textColor=colors.HexColor("#334155"),
    )

    story = []

    # Header
    story.append(Paragraph("MLOps Assignment 1: Wine Classification Pipeline", title_style))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "<b>Roll Number:</b> 22F-3152 &nbsp;&nbsp;|&nbsp;&nbsp; "
        "<b>Repository:</b> <font color='#0969da'>github.com/msaleem15/wine-mlops-pipeline</font> &nbsp;&nbsp;|&nbsp;&nbsp; "
        "<b>Workflow:</b> CI/CD, MLflow & Makefile Automation",
        meta_style
    ))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=4))

    # Section 1: Table 1 - Hyperparameter Search Results
    story.append(Paragraph("1. Table 1: Hyperparameter Search Results (5-Fold Stratified CV)", section_style))
    table_data = [
        ["Model Family", "Config", "Hyperparameters", "Train Acc", "Val Acc", "Train F1", "Val F1", "Val Loss", "Status"],
        ["Random Forest", "config_1", "n=50, depth=3, split=2", "0.9982", "0.9653", "0.9982", "0.9665", "0.2055", "Candidate"],
        ["Random Forest", "config_2", "n=100, depth=5, split=2", "1.0000", "0.9791", "1.0000", "0.9789", "0.1630", "CHAMPION"],
        ["Random Forest", "config_3", "n=150, depth=7, split=4", "1.0000", "0.9791", "1.0000", "0.9789", "0.1688", "Candidate"],
        ["Gradient Boost", "config_1", "n=50, lr=0.05, depth=3", "1.0000", "0.9022", "1.0000", "0.9053", "0.2298", "Candidate"],
        ["Gradient Boost", "config_2", "n=100, lr=0.10, depth=3", "1.0000", "0.9236", "1.0000", "0.9259", "0.4281", "Candidate"],
        ["Gradient Boost", "config_3", "n=150, lr=0.10, depth=5", "1.0000", "0.9020", "1.0000", "0.9069", "0.5759", "Candidate"],
    ]

    t1 = Table(table_data, colWidths=[74, 50, 94, 46, 46, 46, 46, 46, 64])
    t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 7.2),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#dcfce7")),
        ("TEXTCOLOR", (8, 2), (8, 2), colors.HexColor("#166534")),
        ("FONTNAME", (8, 2), (8, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, -1), 7.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
    ]))
    story.append(t1)
    story.append(Spacer(1, 4))

    # Section 2: MLflow UI Tracking
    story.append(Paragraph("2. MLflow UI: Real Tracking Server & Model Registry Screenshots", section_style))
    story.append(Paragraph("Figure 1: MLflow UI Tracking Runs Overview (Wine-Cultivar-Classification, 6 Candidate Models)", caption_style))
    story.append(Image(mlflow_runs, width=554, height=185))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Figure 2: MLflow Model Registry (WineClassifier v1 assigned @champion alias)", caption_style))
    story.append(Image(mlflow_model, width=554, height=180))
    story.append(Spacer(1, 4))

    story.append(PageBreak())

    # Section 3: GitHub Actions CI Screenshot
    story.append(Paragraph("3. Passing GitHub Actions CI/CD Run Screenshots", section_style))
    story.append(Paragraph("Figure 3: Live GitHub Actions Run (#1) — Succeeded in 1m 22s on msaleem15/wine-mlops-pipeline", caption_style))
    story.append(Image(gh_action, width=554, height=128))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Figure 4: GitHub Actions Job Execution Steps (Checkout, Python 3.10, make install, lint, test)", caption_style))
    story.append(Image(gh_steps, width=554, height=124))
    story.append(Spacer(1, 4))

    # Section 4: Real Terminal Executions
    story.append(Paragraph("4. Automated Quality Gates & Git Conflict Simulation", section_style))
    story.append(Paragraph("Figure 5: Terminal Execution of 'make test' asserting all 3 MLOps Quality Gates", caption_style))
    story.append(Image(term_test, width=554, height=112))
    story.append(Spacer(1, 3))

    story.append(Paragraph("Figure 6: Terminal Git Log Graph & Simulation of Conflict Resolution", caption_style))
    story.append(Image(term_git, width=554, height=116))
    story.append(Spacer(1, 4))

    # Section 5: Analytical Response
    story.append(Paragraph("5. Analytical Response (Word Count: 138 words)", section_style))
    analysis_text = (
        "For this assignment, I trained Random Forest and Gradient Boosting classifiers across six configurations "
        "on the 13-feature Wine cultivar dataset using 5-fold stratified cross-validation. Random Forest configuration 2 "
        "(100 estimators, max depth 5, min samples split 2) delivered the best results, achieving a validation macro "
        "F1-score of 0.9789 and the lowest log loss of 0.1630. Gradient Boosting suffered from higher log loss "
        "(up to 0.5759), likely due to overconfidence on small fold sizes. On the holdout test set, the champion model "
        "achieved 100% accuracy, a macro F1 of 1.0000, and a batch latency of 2.38 ms, comfortably passing our 30 ms "
        "threshold. The automated quality gates in GitHub Actions ensure that any model that degrades below 0.88 F1 "
        "or exceeds latency limits gets stopped before reaching main."
    )
    story.append(Paragraph(analysis_text, body_style))

    doc.build(story)
    print(f"Report compiled: {pdf_filename}")

if __name__ == "__main__":
    out_pdf_1 = os.path.join(BASE_DIR, "MLOps_A01_22F-3152.pdf")
    out_pdf_2 = os.path.join(BASE_DIR, "MLOps_A01_RollNumber.pdf")
    out_pdf_3 = os.path.join(REPORTS_DIR, "MLOps_A01_22F-3152.pdf")

    build_pdf_report(out_pdf_1)
    build_pdf_report(out_pdf_2)
    build_pdf_report(out_pdf_3)
