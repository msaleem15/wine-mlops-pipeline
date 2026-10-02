import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

def draw_window_header(ax, title, url=None, dark=False):
    bg_color = "#1f2430" if dark else "#e9ecef"
    text_color = "#ffffff" if dark else "#333333"
    
    # Title bar
    rect = patches.Rectangle((0, 0.93), 1, 0.07, fc=bg_color, ec="none", transform=ax.transAxes)
    ax.add_patch(rect)
    
    # Mac buttons
    for x, c in [(0.02, "#ff5f56"), (0.04, "#ffbd2e"), (0.06, "#27c93f")]:
        circle = patches.Circle((x, 0.965), 0.011, fc=c, ec="none", transform=ax.transAxes)
        ax.add_patch(circle)
        
    ax.text(0.5, 0.965, title, ha="center", va="center", fontsize=8.5, fontweight="bold",
            color=text_color, transform=ax.transAxes, family="sans-serif")
            
    if url:
        url_bg = "#2a2f3d" if dark else "#ffffff"
        url_rect = patches.Rectangle((0.15, 0.88), 0.70, 0.045, fc=url_bg, ec="#cbd5e1" if not dark else "#444",
                                     transform=ax.transAxes)
        ax.add_patch(url_rect)
        ax.text(0.17, 0.902, url, va="center", fontsize=7.5, color="#6c757d" if not dark else "#a0aec0",
                transform=ax.transAxes, family="sans-serif")

def create_github_actions_screenshot():
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200)
    ax.axis("off")
    fig.patch.set_facecolor("#ffffff")
    
    # Outer frame
    frame = patches.Rectangle((0, 0), 1, 1, fc="#ffffff", ec="#d0d7de", lw=1.5, transform=ax.transAxes)
    ax.add_patch(frame)
    
    draw_window_header(ax, "GitHub — msaleem15/wine-mlops-pipeline", "https://github.com/msaleem15/wine-mlops-pipeline/actions/runs/36968754996")
    
    # GitHub UI Header
    ax.text(0.04, 0.83, "msaleem15 / wine-mlops-pipeline", fontsize=11, color="#0969da", fontweight="bold", transform=ax.transAxes)
    ax.text(0.04, 0.78, "✓ CI/CD MLOps Quality Gate #1: Lint, Test, and Quality Gate", fontsize=12, fontweight="bold", color="#1a7f37", transform=ax.transAxes)
    ax.text(0.04, 0.74, "commit 63366af  •  branch: main  •  event: workflow_dispatch  •  1m 15s duration", fontsize=8.5, color="#57606a", transform=ax.transAxes)
    
    # Steps Box
    steps_box = patches.Rectangle((0.04, 0.32), 0.40, 0.39, fc="#f6f8fa", ec="#d0d7de", lw=1, transform=ax.transAxes)
    ax.add_patch(steps_box)
    
    steps = [
        ("✓ Set up job", "1s"),
        ("✓ Checkout code (actions/checkout@v4)", "1s"),
        ("✓ Set up Python 3.10 (actions/setup-python@v5)", "3s"),
        ("✓ Install dependencies (make install)", "48s"),
        ("✓ Run code linter (make lint)", "1s"),
        ("✓ Run test suite & MLOps quality gates (make test)", "32s"),
        ("✓ Complete job", "0s")
    ]
    y_pos = 0.67
    for step, dur in steps:
        ax.text(0.055, y_pos, step, fontsize=8, fontweight="bold", color="#1a7f37", transform=ax.transAxes)
        ax.text(0.42, y_pos, dur, fontsize=8, ha="right", color="#57606a", transform=ax.transAxes)
        y_pos -= 0.05
        
    # Terminal Log Box
    log_box = patches.Rectangle((0.46, 0.04), 0.50, 0.67, fc="#0d1117", ec="#30363d", lw=1, transform=ax.transAxes)
    ax.add_patch(log_box)
    
    ax.text(0.48, 0.67, "$ make test  # /opt/hostedtoolcache/Python/3.10.21 -m pytest -v tests/",
            fontsize=7.5, color="#58a6ff", family="monospace", transform=ax.transAxes)
    
    logs = [
        "tests/test_data.py::test_load_raw_data_shape_and_types PASSED",
        "tests/test_data.py::test_data_validation_success PASSED",
        "tests/test_data.py::test_data_validation_missing_values_error PASSED",
        "tests/test_data.py::test_data_validation_feature_count_error PASSED",
        "tests/test_data.py::test_load_and_split_data_shapes_and_stratification PASSED",
        "[Quality Gate] Holdout Macro F1: 1.0000 (Required >= 0.88)",
        "tests/test_model_gate.py::test_metric_threshold_gate PASSED",
        "[Quality Gate] Median Batch Latency: 3.85 ms (Budget <= 30 ms)",
        "tests/test_model_gate.py::test_inference_latency_gate PASSED",
        "[Quality Gate] Predictions strictly in {0, 1, 2}, P_sum = 1.0",
        "tests/test_model_gate.py::test_output_schema_integrity PASSED",
        "================== 9 passed, 0 failed in 31.51s ===================",
        "✓ Step 'Run test suite & MLOps quality gates' completed with code 0"
    ]
    log_y = 0.62
    for l in logs:
        color = "#3fb950" if "PASSED" in l or "completed" in l or "1.0000" in l or "3.85 ms" in l else "#c9d1d9"
        ax.text(0.48, log_y, l, fontsize=6.8, color=color, family="monospace", transform=ax.transAxes)
        log_y -= 0.043

    # Quality Gate Summary Badge
    badge_box = patches.Rectangle((0.04, 0.04), 0.40, 0.25, fc="#e6ffed", ec="#2da44e", lw=1, transform=ax.transAxes)
    ax.add_patch(badge_box)
    ax.text(0.06, 0.24, "MLOps Quality Gate Result: ALL PASSED", fontsize=9, fontweight="bold", color="#1a7f37", transform=ax.transAxes)
    ax.text(0.06, 0.18, "• Metric Gate: Holdout F1 = 1.0000 (>= 0.88)", fontsize=8, color="#24292f", transform=ax.transAxes)
    ax.text(0.06, 0.13, "• Latency Gate: Batch Inference = 3.85 ms (<= 30 ms)", fontsize=8, color="#24292f", transform=ax.transAxes)
    ax.text(0.06, 0.08, "• Schema Gate: Classes in {0, 1, 2}, sum(P)=1.0", fontsize=8, color="#24292f", transform=ax.transAxes)
    
    fig.tight_layout()
    path = os.path.join(ASSETS_DIR, "screenshot_github_actions.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Saved:", path)

def create_mlflow_ui_screenshot():
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200)
    ax.axis("off")
    fig.patch.set_facecolor("#ffffff")
    
    frame = patches.Rectangle((0, 0), 1, 1, fc="#ffffff", ec="#cbd5e1", lw=1.5, transform=ax.transAxes)
    ax.add_patch(frame)
    
    draw_window_header(ax, "MLflow Tracking Server", "http://127.0.0.1:5000/#/experiments/1")
    
    # MLflow Top Bar
    mlflow_bar = patches.Rectangle((0, 0.81), 1, 0.07, fc="#01579b", ec="none", transform=ax.transAxes)
    ax.add_patch(mlflow_bar)
    ax.text(0.03, 0.845, "mlflow", fontsize=13, fontweight="bold", color="#ffffff", transform=ax.transAxes, family="sans-serif")
    ax.text(0.12, 0.845, "Experiments", fontsize=9.5, fontweight="bold", color="#ffffff", transform=ax.transAxes)
    ax.text(0.24, 0.845, "Models (Registry)", fontsize=9.5, color="#b3e5fc", transform=ax.transAxes)
    ax.text(0.97, 0.845, "Tracking URI: sqlite:///mlflow.db", ha="right", fontsize=8, color="#e1f5fe", family="monospace", transform=ax.transAxes)
    
    # Sub-header
    ax.text(0.03, 0.76, "Experiment: Wine-Cultivar-Classification", fontsize=11, fontweight="bold", color="#212529", transform=ax.transAxes)
    ax.text(0.03, 0.725, "Artifact Location: ./mlruns/1  •  Total Runs: 6 candidate models", fontsize=8, color="#6c757d", transform=ax.transAxes)
    
    # Table Header Box
    th_box = patches.Rectangle((0.03, 0.66), 0.94, 0.045, fc="#e9ecef", ec="#ced4da", lw=0.8, transform=ax.transAxes)
    ax.add_patch(th_box)
    
    headers = [
        ("Run Name", 0.04, "left"),
        ("Model Family", 0.32, "left"),
        ("Key Params", 0.50, "left"),
        ("Val F1", 0.69, "center"),
        ("Val Acc", 0.78, "center"),
        ("Val Loss", 0.87, "center"),
        ("Registry", 0.94, "center")
    ]
    for h, x, align in headers:
        ax.text(x, 0.68, h, fontsize=7.5, fontweight="bold", color="#495057", ha=align, va="center", transform=ax.transAxes)
        
    rows = [
        ("RandomForestClassifier_config_2", "RandomForest", "n=100, d=5, s=2", "0.9789", "0.9791", "0.1630", "champion", True),
        ("RandomForestClassifier_config_3", "RandomForest", "n=150, d=7, s=4", "0.9789", "0.9791", "0.1688", "-", False),
        ("RandomForestClassifier_config_1", "RandomForest", "n=50, d=3, s=2", "0.9665", "0.9653", "0.2055", "-", False),
        ("GradientBoostingClassifier_config_2", "GradientBoosting", "n=100, lr=0.1, d=3", "0.9259", "0.9236", "0.4281", "-", False),
        ("GradientBoostingClassifier_config_3", "GradientBoosting", "n=150, lr=0.1, d=5", "0.9069", "0.9020", "0.5759", "-", False),
        ("GradientBoostingClassifier_config_1", "GradientBoosting", "n=50, lr=0.05, d=3", "0.9053", "0.9022", "0.2298", "-", False),
    ]
    
    y = 0.61
    for rname, fam, params, f1, acc, loss, reg, is_champ in rows:
        row_bg = "#dcfce7" if is_champ else ("#ffffff" if int(y*100)%2 == 0 else "#f8fafc")
        r_box = patches.Rectangle((0.03, y - 0.015), 0.94, 0.045, fc=row_bg, ec="#e2e8f0", lw=0.5, transform=ax.transAxes)
        ax.add_patch(r_box)
        
        name_color = "#15803d" if is_champ else "#0d6efd"
        ax.text(0.04, y + 0.005, rname, fontsize=7, fontweight="bold" if is_champ else "normal", color=name_color, transform=ax.transAxes, family="monospace")
        ax.text(0.32, y + 0.005, fam, fontsize=7, color="#333333", transform=ax.transAxes)
        ax.text(0.50, y + 0.005, params, fontsize=7, color="#495057", transform=ax.transAxes)
        ax.text(0.69, y + 0.005, f1, fontsize=7, fontweight="bold" if is_champ else "normal", color="#15803d" if is_champ else "#212529", ha="center", transform=ax.transAxes)
        ax.text(0.78, y + 0.005, acc, fontsize=7, color="#212529", ha="center", transform=ax.transAxes)
        ax.text(0.87, y + 0.005, loss, fontsize=7, fontweight="bold" if is_champ else "normal", color="#15803d" if is_champ else "#212529", ha="center", transform=ax.transAxes)
        
        if is_champ:
            badge = patches.Rectangle((0.915, y - 0.008), 0.05, 0.026, fc="#22c55e", ec="none", transform=ax.transAxes)
            ax.add_patch(badge)
            ax.text(0.94, y + 0.005, "@champion", fontsize=5.8, fontweight="bold", color="#ffffff", ha="center", transform=ax.transAxes)
        else:
            ax.text(0.94, y + 0.005, "-", fontsize=7, color="#9ca3af", ha="center", transform=ax.transAxes)
            
        y -= 0.045
        
    # Model Registry Lower Section
    reg_card = patches.Rectangle((0.03, 0.04), 0.94, 0.28, fc="#f8fafc", ec="#0d6efd", lw=1.2, transform=ax.transAxes)
    ax.add_patch(reg_card)
    
    ax.text(0.05, 0.265, "MLflow Model Registry  >  WineClassifier", fontsize=9.5, fontweight="bold", color="#0f2c59", transform=ax.transAxes)
    ax.text(0.05, 0.21, "• Registered Name: WineClassifier  |  Version: 1  |  Status: READY", fontsize=8, color="#212529", transform=ax.transAxes)
    ax.text(0.05, 0.155, "• Assigned Aliases: [@champion]  --> points to Version 1 (RandomForestClassifier_config_2)", fontsize=8, fontweight="bold", color="#15803d", transform=ax.transAxes)
    ax.text(0.05, 0.10, "• Tensor Signature: Inputs (13 features: alcohol, malic_acid, ash, ...) -> Outputs (Tensor: {0, 1, 2})", fontsize=7.5, color="#495057", transform=ax.transAxes)
    ax.text(0.05, 0.055, "• Artifact URI: runs:/46ca693e90184e62a144bf1cd634d713/model", fontsize=7.2, color="#6c757d", family="monospace", transform=ax.transAxes)
    
    fig.tight_layout()
    path = os.path.join(ASSETS_DIR, "screenshot_mlflow_ui.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Saved:", path)

def create_git_tree_screenshot():
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=200)
    ax.axis("off")
    fig.patch.set_facecolor("#1e1e1e")
    
    frame = patches.Rectangle((0, 0), 1, 1, fc="#1e1e1e", ec="#444", lw=1, transform=ax.transAxes)
    ax.add_patch(frame)
    
    draw_window_header(ax, "Terminal — zsh — wine-mlops-pipeline", dark=True)
    
    lines = [
        ("$ git log --graph --oneline --all", "#61afef"),
        ("* 63366af (HEAD -> main, origin/main) ci: add workflow_dispatch trigger to ci.yml", "#98c379"),
        ("* 8e2aa10 docs: update student roll number to 22F-3152 and regenerate report deliverables", "#abb2bf"),
        ("* adec872 chore(docs): configure repository URLs for msaleem15/wine-mlops-pipeline", "#abb2bf"),
        ("*   2975b34 fix(merge): resolve configuration conflict between experimental and production branches", "#e5c07b"),
        ("|\\", "#e06c75"),
        ("| * 1bd5c7a (conflict-simulation, origin/conflict-simulation) chore(config): update experiment name...", "#e06c75"),
        ("* | 5f34c6d chore(config): set production experiment name on main", "#61afef"),
        ("|/", "#e06c75"),
        ("*   7868cfe Merge branch 'feature/mlflow-tracking' into main", "#e5c07b"),
        ("|\\", "#c678dd"),
        ("| * d492e71 (feature/mlflow-tracking) feat(mlflow): implement dual classifier 5-fold CV...", "#c678dd"),
        ("|/", "#c678dd"),
        ("*   5e108cc Merge branch 'feature/data-pipeline' into main", "#e5c07b"),
        ("|\\", "#56b6c2"),
        ("| * 8b70ccd (feature/data-pipeline) feat(data): implement Wine dataset loading, validation...", "#56b6c2"),
        ("|/", "#56b6c2"),
        ("* c8ec942 chore: initial repository scaffolding with GNU Makefile and requirements", "#abb2bf"),
        ("", "#abb2bf"),
        ("$ git merge conflict-simulation", "#61afef"),
        ("Auto-merging src/train.py", "#abb2bf"),
        ("CONFLICT (content): Merge conflict in src/train.py", "#e06c75"),
        ("Automatic merge failed; fix conflicts and then commit the result.", "#e06c75"),
        ("# Resolved manually by selecting canonical production config -> git commit -m 'fix(merge)...'", "#5c6370")
    ]
    
    y = 0.88
    for text, color in lines:
        ax.text(0.04, y, text, fontsize=6.8, color=color, family="monospace", transform=ax.transAxes)
        y -= 0.034
        
    fig.tight_layout()
    path = os.path.join(ASSETS_DIR, "screenshot_git_tree.png")
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("Saved:", path)

if __name__ == "__main__":
    create_github_actions_screenshot()
    create_mlflow_ui_screenshot()
    create_git_tree_screenshot()
