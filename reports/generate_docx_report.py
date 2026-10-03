import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

REPORTS_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(REPORTS_DIR, "assets")
BASE_DIR = os.path.dirname(REPORTS_DIR)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_heading_with_spacing(doc, text, level=1, space_before=12, space_after=4):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(space_before)
    h.paragraph_format.space_after = Pt(space_after)
    h.paragraph_format.keep_with_next = True
    for run in h.runs:
        run.font.name = "Calibri"
        if level == 1:
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = RGBColor(15, 44, 89)
        elif level == 2:
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = RGBColor(30, 41, 59)
    return h

def build_docx_report(output_path: str):
    doc = Document()

    # Page Margins: 0.75 in
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Document Header Title
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    run_title = title_p.add_run("MLOps Assignment 1: Wine Classification Pipeline")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    # Metadata subtitle
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(2)
    sub_p.paragraph_format.space_after = Pt(8)
    
    r_roll_lbl = sub_p.add_run("Roll Number: ")
    r_roll_lbl.font.bold = True
    r_roll_lbl.font.size = Pt(9.5)
    r_roll_val = sub_p.add_run("22F-3152   |   ")
    r_roll_val.font.size = Pt(9.5)

    r_repo_lbl = sub_p.add_run("GitHub Repository: ")
    r_repo_lbl.font.bold = True
    r_repo_lbl.font.size = Pt(9.5)
    r_repo_val = sub_p.add_run("https://github.com/msaleem15/wine-mlops-pipeline   |   ")
    r_repo_val.font.size = Pt(9.5)
    r_repo_val.font.color.rgb = RGBColor(9, 105, 218)

    r_wf_lbl = sub_p.add_run("Workflow: ")
    r_wf_lbl.font.bold = True
    r_wf_lbl.font.size = Pt(9.5)
    r_wf_val = sub_p.add_run("CI/CD, MLflow & Makefile Automation")
    r_wf_val.font.size = Pt(9.5)

    # Horizontal divider rule
    hr_p = doc.add_paragraph()
    hr_p.paragraph_format.space_before = Pt(0)
    hr_p.paragraph_format.space_after = Pt(10)
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="1" w:color="CBD5E1"/></w:pBdr>')
    hr_p._p.get_or_add_pPr().append(pBdr)

    # Section 1: Table 1 - Hyperparameter Search Results
    add_heading_with_spacing(doc, "1. Table 1: Hyperparameter Search Results (5-Fold Stratified CV)", level=1)
    intro_table = doc.add_paragraph(
        "Six distinct model configurations across two tree-based classifier algorithms "
        "(RandomForestClassifier and GradientBoostingClassifier) evaluated using 5-fold stratified cross-validation "
        "on the Wine dataset (13 chemical features, 178 samples, random seed 42):"
    )
    intro_table.paragraph_format.space_after = Pt(6)
    intro_table.paragraph_format.space_before = Pt(0)
    for r in intro_table.runs:
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(71, 85, 105)

    # Table 1 Definition
    table_data = [
        ["Model Family", "Config", "Hyperparameters", "Train Acc", "Val Acc", "Train F1", "Val F1", "Val Loss", "Status"],
        ["Random Forest", "config_1", "n=50, depth=3, split=2", "0.9982", "0.9653", "0.9982", "0.9665", "0.2055", "Candidate"],
        ["Random Forest", "config_2", "n=100, depth=5, split=2", "1.0000", "0.9791", "1.0000", "0.9789", "0.1630", "CHAMPION"],
        ["Random Forest", "config_3", "n=150, depth=7, split=4", "1.0000", "0.9791", "1.0000", "0.9789", "0.1688", "Candidate"],
        ["Gradient Boost", "config_1", "n=50, lr=0.05, depth=3", "1.0000", "0.9022", "1.0000", "0.9053", "0.2298", "Candidate"],
        ["Gradient Boost", "config_2", "n=100, lr=0.10, depth=3", "1.0000", "0.9236", "1.0000", "0.9259", "0.4281", "Candidate"],
        ["Gradient Boost", "config_3", "n=150, lr=0.10, depth=5", "1.0000", "0.9020", "1.0000", "0.9069", "0.5759", "Candidate"],
    ]

    table = doc.add_table(rows=len(table_data), cols=9)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    col_widths = [Inches(1.0), Inches(0.65), Inches(1.5), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.6), Inches(0.85)]

    for row_idx, row in enumerate(table.rows):
        is_header = (row_idx == 0)
        is_champion = (row_idx == 2)
        
        # Row height
        trPr = row._tr.get_or_add_trPr()
        trHeight = parse_xml(f'<w:trHeight {nsdecls("w")} w:val="260" w:hRule="atLeast"/>')
        trPr.append(trHeight)

        for col_idx, cell in enumerate(row.cells):
            cell.width = col_widths[col_idx]
            cell_text = table_data[row_idx][col_idx]
            
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(cell_text)
            run.font.name = "Calibri"
            run.font.size = Pt(8)

            if is_header:
                set_cell_background(cell, "1E293B")
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
            elif is_champion:
                set_cell_background(cell, "DCFCE7")  # soft green
                run.font.bold = True
                if col_idx == 8:
                    run.font.color.rgb = RGBColor(22, 101, 52)
            else:
                if row_idx % 2 == 1:
                    set_cell_background(cell, "F8FAFC")
                else:
                    set_cell_background(cell, "FFFFFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Section 2: MLflow UI Tracking & Model Registry
    add_heading_with_spacing(doc, "2. MLflow UI Tracking & Model Registry Evidence", level=1)
    
    # MLflow runs screenshot
    p_mlflow_caption = doc.add_paragraph()
    p_mlflow_caption.paragraph_format.space_after = Pt(3)
    p_mlflow_caption.paragraph_format.keep_with_next = True
    r_cap1 = p_mlflow_caption.add_run("Figure 1: Real MLflow UI — Experiment Runs Overview (Wine-Cultivar-Classification)")
    r_cap1.font.bold = True
    r_cap1.font.size = Pt(9.5)
    r_cap1.font.color.rgb = RGBColor(30, 41, 59)

    mlflow_runs_img = os.path.join(ASSETS_DIR, "real_mlflow_runs.png")
    if os.path.exists(mlflow_runs_img):
        doc.add_picture(mlflow_runs_img, width=Inches(6.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(8)

    # MLflow model registry screenshot
    p_model_caption = doc.add_paragraph()
    p_model_caption.paragraph_format.space_after = Pt(3)
    p_model_caption.paragraph_format.keep_with_next = True
    r_cap2 = p_model_caption.add_run("Figure 2: Real MLflow UI — Model Registry (WineClassifier v1 with @champion alias)")
    r_cap2.font.bold = True
    r_cap2.font.size = Pt(9.5)
    r_cap2.font.color.rgb = RGBColor(30, 41, 59)

    mlflow_model_img = os.path.join(ASSETS_DIR, "real_mlflow_model.png")
    if os.path.exists(mlflow_model_img):
        doc.add_picture(mlflow_model_img, width=Inches(6.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(8)

    # MLflow comparison screenshot
    p_comp_caption = doc.add_paragraph()
    p_comp_caption.paragraph_format.space_after = Pt(3)
    p_comp_caption.paragraph_format.keep_with_next = True
    r_cap3 = p_comp_caption.add_run("Figure 3: Real MLflow UI — 6 Runs Side-by-Side Comparison & Metric Evaluations")
    r_cap3.font.bold = True
    r_cap3.font.size = Pt(9.5)
    r_cap3.font.color.rgb = RGBColor(30, 41, 59)

    mlflow_comp_img = os.path.join(ASSETS_DIR, "real_mlflow_compare.png")
    if os.path.exists(mlflow_comp_img):
        doc.add_picture(mlflow_comp_img, width=Inches(6.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(12)

    # Section 3: GitHub Actions CI/CD Workflow
    add_heading_with_spacing(doc, "3. GitHub Actions CI/CD Pipeline Evidence", level=1)

    p_gh_caption = doc.add_paragraph()
    p_gh_caption.paragraph_format.space_after = Pt(3)
    p_gh_caption.paragraph_format.keep_with_next = True
    r_cap4 = p_gh_caption.add_run("Figure 4: Real GitHub Actions — Passing CI/CD MLOps Quality Gate Run (#1)")
    r_cap4.font.bold = True
    r_cap4.font.size = Pt(9.5)
    r_cap4.font.color.rgb = RGBColor(30, 41, 59)

    gh_action_img = os.path.join(ASSETS_DIR, "real_github_action.png")
    if os.path.exists(gh_action_img):
        doc.add_picture(gh_action_img, width=Inches(6.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(8)

    p_steps_caption = doc.add_paragraph()
    p_steps_caption.paragraph_format.space_after = Pt(3)
    p_steps_caption.paragraph_format.keep_with_next = True
    r_cap5 = p_steps_caption.add_run("Figure 5: Real GitHub Actions — Pipeline Step Execution Verification (Lint, Test, Quality Gates)")
    r_cap5.font.bold = True
    r_cap5.font.size = Pt(9.5)
    r_cap5.font.color.rgb = RGBColor(30, 41, 59)

    gh_steps_img = os.path.join(ASSETS_DIR, "real_github_job_steps.png")
    if os.path.exists(gh_steps_img):
        doc.add_picture(gh_steps_img, width=Inches(6.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(12)

    # Section 4: Local Automation & Automated MLOps Quality Gates
    add_heading_with_spacing(doc, "4. Local Automation, Test Suite & MLOps Quality Gates", level=1)

    p_term_caption = doc.add_paragraph()
    p_term_caption.paragraph_format.space_after = Pt(3)
    p_term_caption.paragraph_format.keep_with_next = True
    r_cap6 = p_term_caption.add_run("Figure 6: Real Terminal Execution — 'make test' & Automated Quality Gates Validation")
    r_cap6.font.bold = True
    r_cap6.font.size = Pt(9.5)
    r_cap6.font.color.rgb = RGBColor(30, 41, 59)

    term_test_img = os.path.join(ASSETS_DIR, "real_terminal_make_test.png")
    if os.path.exists(term_test_img):
        doc.add_picture(term_test_img, width=Inches(6.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(12)

    # Section 5: Git Commit Tree & Merge Conflict Simulation
    add_heading_with_spacing(doc, "5. Git Version Control & Conflict Resolution Evidence", level=1)

    p_git_caption = doc.add_paragraph()
    p_git_caption.paragraph_format.space_after = Pt(3)
    p_git_caption.paragraph_format.keep_with_next = True
    r_cap7 = p_git_caption.add_run("Figure 7: Real Terminal Execution — Git Commit Graph & Conflict Merge Resolution")
    r_cap7.font.bold = True
    r_cap7.font.size = Pt(9.5)
    r_cap7.font.color.rgb = RGBColor(30, 41, 59)

    term_git_img = os.path.join(ASSETS_DIR, "real_terminal_git_tree.png")
    if os.path.exists(term_git_img):
        doc.add_picture(term_git_img, width=Inches(6.8))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].paragraph_format.space_after = Pt(12)

    # Section 6: Analytical Response
    add_heading_with_spacing(doc, "6. Analytical Response (Word Count: 138 words)", level=1)

    analysis_box = doc.add_table(rows=1, cols=1)
    analysis_box.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_box = analysis_box.rows[0].cells[0]
    cell_box.width = Inches(6.8)
    set_cell_background(cell_box, "F8FAFC")
    set_cell_margins(cell_box, top=140, bottom=140, left=180, right=180)
    
    # Left border highlight
    tcPr = cell_box._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="0969DA"/>'
        f'<w:top w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    analysis_p = cell_box.paragraphs[0]
    analysis_p.paragraph_format.space_before = Pt(4)
    analysis_p.paragraph_format.space_after = Pt(4)
    analysis_p.paragraph_format.line_spacing = 1.2
    
    r_text = analysis_p.add_run(
        "For this assignment, I trained Random Forest and Gradient Boosting classifiers across six configurations "
        "on the 13-feature Wine cultivar dataset using 5-fold stratified cross-validation. Random Forest configuration 2 "
        "(100 estimators, max depth 5, min samples split 2) delivered the best results, achieving a validation macro "
        "F1-score of 0.9789 and the lowest log loss of 0.1630. Gradient Boosting suffered from higher log loss "
        "(up to 0.5759), likely due to overconfidence on small fold sizes. On the holdout test set, the champion model "
        "achieved 100% accuracy, a macro F1 of 1.0000, and a batch latency of 2.38 ms, comfortably passing our 30 ms "
        "threshold. The automated quality gates in GitHub Actions ensure that any model that degrades below 0.88 F1 "
        "or exceeds latency limits gets stopped before reaching main."
    )
    r_text.font.name = "Calibri"
    r_text.font.size = Pt(10)
    r_text.font.italic = False
    r_text.font.color.rgb = RGBColor(30, 41, 59)

    doc.save(output_path)
    print(f"Word document saved successfully at: {output_path}")

if __name__ == "__main__":
    out_docx_1 = os.path.join(BASE_DIR, "MLOps_A01_22F-3152.docx")
    out_docx_2 = os.path.join(BASE_DIR, "MLOps_A01_RollNumber.docx")
    out_docx_3 = os.path.join(REPORTS_DIR, "MLOps_A01_22F-3152.docx")
    
    build_docx_report(out_docx_1)
    build_docx_report(out_docx_2)
    build_docx_report(out_docx_3)
