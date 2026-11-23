"""Slide-sized charts for the final presentation, built from results/metrics/*.json.

Run from the repository root:  python report/presentation/make_slide_figures.py
Writes PNGs to report/presentation/figures/.
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "results" / "metrics"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)

SPARSE = "#2a78d6"    # TF-IDF (sparse) models
DENSE = "#eb6834"     # SVD-300 (dense) models
BASELINE = "#8a8984"  # baselines
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"

plt.rcParams.update({
    "font.size": 18,
    "axes.edgecolor": INK_2,
    "axes.labelcolor": INK,
    "xtick.color": INK_2,
    "ytick.color": INK,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def load(name):
    return json.loads((METRICS / f"{name}.json").read_text(encoding="utf-8"))


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)


# 1. Product routing: every model vs. the mid-term baseline -------------------------
rows = [
    ("Naive Bayes (mid-term baseline)", 0.695, BASELINE),  # README / report Table II
]
for key, label in [
    ("naive_bayes", "Multinomial NB (tuned)"),
    ("complement_nb", "Complement NB"),
    ("logistic_regression", "Logistic regression"),
    ("linear_svm", "Linear SVM"),
]:
    rows.append((label, load(key)["test_macro_f1"], SPARSE))
for key, label in [
    ("knn", "k-NN"),
    ("random_forest", "Random forest"),
    ("gradient_boosting", "Gradient boosting"),
    ("mlp", "MLP"),
]:
    rows.append((label, load(key)["test_macro_f1"], DENSE))
rows.sort(key=lambda r: r[1])

fig, ax = plt.subplots(figsize=(13, 7.2))
labels, values, colors = zip(*rows)
bars = ax.barh(labels, values, color=colors, height=0.68, edgecolor="white", linewidth=2)
for bar, value in zip(bars, values):
    weight = "bold" if value == max(values) else "normal"
    ax.text(value + 0.008, bar.get_y() + bar.get_height() / 2, f"{value:.3f}",
            va="center", fontsize=17, color=INK, fontweight=weight)
ax.axvline(0.695, color=BASELINE, linestyle="--", linewidth=2)
ax.set_xlim(0, 1)
ax.set_xlabel("Test macro-F1 (32,500 complaints)")
style(ax)
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (SPARSE, DENSE, BASELINE)]
ax.legend(handles, ["Full TF-IDF (sparse)", "SVD-300 (dense)", "Baseline"],
          loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=3, frameon=False, fontsize=16)
fig.tight_layout()
fig.savefig(OUT / "slide_routing_vs_baseline.png", dpi=200)
plt.close(fig)

# 2. Monetary relief: PR-AUC lift over the prevalence baseline ----------------------
relief = [
    ("Prevalence baseline", "relief_prevalence", BASELINE),
    ("Product only", "relief_product", SPARSE),
    ("Text only", "relief_text", SPARSE),
    ("Text + product", "relief_text_product", SPARSE),
    ("Text + product + company", "relief_text_product_company", SPARSE),
]
names, scores, colors = [], [], []
for label, key, color in relief:
    m = load(key)
    names.append(label)
    scores.append(m["test_pr_auc"])
    colors.append(color)
prevalence = load("relief_prevalence")["prevalence"]

fig, ax = plt.subplots(figsize=(13, 6.5))
bars = ax.barh(names, scores, color=colors, height=0.62, edgecolor="white", linewidth=2)
for bar, score in zip(bars, scores):
    lift = score / prevalence
    ax.text(score + 0.006, bar.get_y() + bar.get_height() / 2,
            f"{score:.3f}  ({lift:.1f}× base rate)", va="center", fontsize=17, color=INK)
ax.invert_yaxis()
ax.set_xlim(0, 0.6)
ax.set_xlabel("Test PR-AUC (5.6% of complaints get monetary relief)")
style(ax)
fig.tight_layout()
fig.savefig(OUT / "slide_relief_lift.png", dpi=200)
plt.close(fig)

print("Wrote", sorted(p.name for p in OUT.glob("slide_*.png")))
