"""
HB-Eval Analysis — Cnom–Rop Gap Visualizer
============================================
Generates publication-quality figures matching the HB-Eval paper.

All figures are produced with matplotlib only — no seaborn dependency.
Color palette chosen for accessibility (colorblind-safe).

Figures produced:
  Figure 1 — Overall reliability by model (all 14 models, 3 methodologies)
  Figure 2 — Cnom vs Rop per domain (grouped bars, all models)
  Figure 3 — Scale non-monotonicity (Meth B models, parameter count vs reliability)
  Figure 4 — Cascade penalty comparison across methodologies
  Figure 5 — IRS distribution shift impact (intentional vs trial-and-error)
  Figure 6 — Certification tier landscape

Usage:
    python analysis/gap_visualizer.py \\
        --b  data/results/methodology_b_4998.json \\
        --c  data/results/methodology_c_3002.json \\
        --out figures/
"""

from typing import Optional
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import matplotlib.ticker as mticker
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("WARNING: matplotlib not installed — text summaries only.")
    print("Install with: pip install matplotlib")

from core.statistics import gap_significance, proportion_ci, cascade_penalty

# ── Color palette (colorblind-safe) ──────────────────────────────────
NAVY   = "#1B3A6B"
STEEL  = "#4472C4"
TEAL   = "#2E86AB"
GREEN  = "#2D9E6B"
AMBER  = "#E6A817"
RED    = "#C0392B"
GRAY   = "#7F8C8D"
LGRAY  = "#ECF0F1"

DOMAIN_COLORS = {
    "cybersecurity":      RED,
    "emergency_response": AMBER,
    "robotics":           GREEN,
    "medical":            TEAL,
    "logistics":          STEEL,
}

DOMAINS = ["cybersecurity", "emergency_response", "robotics", "medical", "logistics"]


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 1 — Overall Model Reliability
# ═══════════════════════════════════════════════════════════════════════

def figure_overall_reliability(results_b: list, results_c: list, out_dir: str):
    """Bar chart of binary reliability for all evaluated models."""

    # Build model → reliability mapping
    entries = []

    b_models_ordered = [
        ("meta-llama/llama-4-maverick-17b-128e-instruct", "Llama-4\nMaverick-17B", "Meth B"),
        ("openai/gpt-oss-120b",                           "GPT-OSS\n120B",          "Meth B"),
        ("meta-llama/llama-4-scout-17b-16e-instruct",     "Llama-4\nScout-17B",     "Meth B"),
        ("qwen/qwen3-32b",                                "Qwen3\n32B",             "Meth B"),
        ("llama-3.3-70b-versatile",                       "Llama-3.3\n70B",         "Meth B"),
    ]
    for model_id, short, meth in b_models_ordered:
        mr = [r for r in results_b
              if model_id.lower() in r.get("model","").lower()
              or short.replace("\n"," ").split()[0].lower() in r.get("model","").lower()]
        if not mr:
            mr = [r for r in results_b
                  if any(tok.lower() in r.get("model","").lower()
                         for tok in short.replace("\n"," ").split()[:2])]
        if mr:
            p, lo, hi = proportion_ci(sum(r["success"] for r in mr), len(mr))
            entries.append({"label": short, "rel": p, "lo": lo, "hi": hi,
                            "method": meth, "color": NAVY})

    c_order = [("GPT-4o", "GPT-4o", "Meth C", TEAL),
               ("Claude-3.5-Sonnet", "Claude 3.5\nSonnet", "Meth C", GREEN),
               ("Gemini-2.5-Flash", "Gemini 2.5\nFlash*", "Meth C", AMBER)]
    for search, short, meth, col in c_order:
        mr = [r for r in results_c
              if search.lower() in r.get("model","").lower()]
        if mr:
            p, lo, hi = proportion_ci(sum(r["success"] for r in mr), len(mr))
            entries.append({"label": short, "rel": p, "lo": lo, "hi": hi,
                            "method": meth, "color": col})

    if not entries:
        print("  Figure 1: no data available")
        return

    if not HAS_MPL:
        print("\n[Figure 1 — Overall Reliability]")
        for e in entries:
            bar = "█" * int(e["rel"] * 40)
            print(f"  {e['label'].replace(chr(10),' '):20s}: {e['rel']:.1%}  {bar}")
        return

    fig, ax = plt.subplots(figsize=(12, 5))

    xs     = range(len(entries))
    bars   = ax.bar(xs, [e["rel"] for e in entries],
                    color=[e["color"] for e in entries],
                    width=0.6, zorder=3)
    yerr_lo = [e["rel"] - e["lo"] for e in entries]
    yerr_hi = [e["hi"] - e["rel"] for e in entries]
    ax.errorbar(xs, [e["rel"] for e in entries],
                yerr=[yerr_lo, yerr_hi],
                fmt="none", ecolor="#333", elinewidth=1.2, capsize=4, zorder=4)

    # Convergence line (36.2%)
    ax.axhline(0.362, color=GRAY, linestyle="--", linewidth=1.2, zorder=2,
               label="36.2% convergence (Meth A/B)")

    # Tier lines
    ax.axhline(0.80, color=GREEN, linestyle=":", linewidth=1.0, alpha=0.7, label="Tier 2 threshold (80%)")
    ax.axhline(0.95, color=NAVY,  linestyle=":", linewidth=1.0, alpha=0.7, label="Tier 3 threshold (95%)")

    # Labels inside bars
    for bar, e in zip(bars, entries):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.015,
                f"{h:.0%}", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax.set_xticks(list(xs))
    ax.set_xticklabels([e["label"] for e in entries], fontsize=9)
    ax.set_ylabel("Binary Reliability (Rop)", fontsize=10)
    ax.set_title("Figure 1 — Overall Model Reliability Across All HB-Eval Evaluations\n"
                 "(Methods B + C; Method A aggregate = 36.2%)", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.grid(axis="y", alpha=0.3, zorder=1)
    ax.legend(fontsize=8, loc="upper left")

    _add_method_bands(ax, entries)
    _save(fig, out_dir, "figure1_overall_reliability.pdf")


def _add_method_bands(ax, entries):
    """Add subtle background bands to distinguish methodology groups."""
    methods = [e["method"] for e in entries]
    i = 0
    while i < len(methods):
        j = i
        while j < len(methods) and methods[j] == methods[i]:
            j += 1
        if methods[i] == "Meth C":
            ax.axvspan(i - 0.5, j - 0.5, alpha=0.06, color=TEAL, zorder=0)
        i = j


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 2 — Cnom vs Rop Gap by Domain
# ═══════════════════════════════════════════════════════════════════════

def figure_gap_by_domain(results_b: list, out_dir: str):
    """Grouped bar chart: nominal vs operational per domain."""
    domains = DOMAINS
    cnom_vals, rop_vals, ci_vals, sig_labels = [], [], [], []

    all_nom = [r for r in results_b if r["fault_type"] == "none"]
    all_ops = [r for r in results_b if r["fault_type"] != "none"]

    for domain in domains:
        nom = [r for r in all_nom if r["domain"] == domain]
        ops = [r for r in all_ops if r["domain"] == domain]
        if not nom or not ops:
            cnom_vals.append(0); rop_vals.append(0); ci_vals.append(0)
            sig_labels.append("")
            continue
        g = gap_significance(sum(r["success"] for r in nom), len(nom),
                             sum(r["success"] for r in ops), len(ops))
        cnom_vals.append(g["cnom"])
        rop_vals.append(g["rop"])
        ci_vals.append(g["ci_pp"] / 100)
        sig_labels.append("***" if g["p_value"] < 0.001 else
                          ("**" if g["p_value"] < 0.01 else "n.s."))

    domain_labels = ["Cyber-\nsecurity", "Emergency\nResponse",
                     "Robotics", "Medical", "Logistics"]

    if not HAS_MPL:
        print("\n[Figure 2 — Cnom vs Rop Gap]")
        for d, cn, ro, sig in zip(domain_labels, cnom_vals, rop_vals, sig_labels):
            gap = cn - ro
            print(f"  {d.replace(chr(10),' '):20s}: Cnom={cn:.1%}  Rop={ro:.1%}  "
                  f"Δ={gap*100:+.1f}pp  {sig}")
        return

    x      = range(len(domains))
    width  = 0.35
    fig, ax = plt.subplots(figsize=(11, 5))

    bars_nom = ax.bar([xi - width/2 for xi in x], cnom_vals,
                      width, label="Nominal (Cnom)", color=STEEL, zorder=3)
    bars_rop = ax.bar([xi + width/2 for xi in x], rop_vals,
                      width, label="Operational (Rop)", color=AMBER,
                      zorder=3, alpha=0.9)

    # CI error bars on Rop
    ax.errorbar([xi + width/2 for xi in x], rop_vals,
                yerr=ci_vals, fmt="none", ecolor="#333",
                elinewidth=1.2, capsize=4, zorder=4)

    # Gap annotations
    for xi, cn, ro, sig in zip(x, cnom_vals, rop_vals, sig_labels):
        gap = (cn - ro) * 100
        if gap > 1:
            mid_y = (cn + ro) / 2
            ax.annotate(f"Δ{gap:.1f}pp\n{sig}",
                        xy=(xi + width/2, ro),
                        xytext=(xi + width/2, mid_y + 0.05),
                        ha="center", fontsize=8,
                        arrowprops=dict(arrowstyle="-", color=RED, lw=1.5),
                        color=RED, fontweight="bold")

    ax.set_xticks(list(x))
    ax.set_xticklabels(domain_labels, fontsize=9)
    ax.set_ylabel("Reliability", fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_title("Figure 2 — Cnom–Rop Gap by Domain (Methodology B, Aggregated)\n"
                 "Gap = nominal reliability − operational reliability under fault injection",
                 fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3, zorder=1)

    _save(fig, out_dir, "figure2_gap_by_domain.pdf")


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 3 — Scale Non-Monotonicity
# ═══════════════════════════════════════════════════════════════════════

def figure_scale_nonmonotonicity(results_b: list, out_dir: str):
    """Parameter count vs reliability (Meth B models)."""
    # Model sizes and paper results
    model_data = [
        ("Llama-4-Maverick-17B", 17,  0.730),
        ("GPT-OSS-120B",         120, 0.709),
        ("Llama-4-Scout-17B",    17,  0.614),
        ("Qwen3-32B",            32,  0.442),
        ("Llama-3.3-70B",        70,  0.321),
    ]

    if not HAS_MPL:
        print("\n[Figure 3 — Scale Non-Monotonicity]")
        for name, params, rel in sorted(model_data, key=lambda x: x[1]):
            print(f"  {params:4d}B  {rel:.1%}  {name}")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    params  = [d[1] for d in model_data]
    rels    = [d[2] for d in model_data]
    names   = [d[0] for d in model_data]
    colors  = [NAVY, RED, TEAL, AMBER, STEEL]

    for p, r, name, col in zip(params, rels, names, colors):
        ax.scatter(p, r, s=220, color=col, zorder=4, edgecolors="white", linewidths=1.5)
        offset_y = 0.025 if name != "Llama-4-Maverick-17B" else -0.04
        ax.annotate(name, (p, r), xytext=(p + 2, r + offset_y),
                    fontsize=8.5, color=col)

    # Highlight the 40.9pp gap between Maverick-17B and Llama-3.3-70B
    ax.annotate("",
                xy=(70, 0.321), xytext=(17, 0.730),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
    ax.text(43, 0.54, "40.9pp gap\n(4.1× more params)", ha="center",
            fontsize=9, color=RED, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    ax.set_xlabel("Model Parameters (billions)", fontsize=10)
    ax.set_ylabel("Binary Reliability (Rop)", fontsize=10)
    ax.set_title("Figure 3 — Scale Non-Monotonicity\n"
                 "Maverick-17B outperforms Llama-3.3-70B by 40.9pp despite 4.1× fewer parameters",
                 fontsize=10)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_xlim(0, 135)
    ax.set_ylim(0.2, 0.85)
    ax.grid(alpha=0.3)

    _save(fig, out_dir, "figure3_scale_nonmonotonicity.pdf")


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 4 — Cascade Penalty Comparison
# ═══════════════════════════════════════════════════════════════════════

def figure_cascade_penalty(results_b: list, results_c: list, out_dir: str):
    """Cascade penalty (pp) comparison across methodologies."""
    penalties = {}

    for label, results in [("Meth B\n(Open-weight)", results_b),
                            ("Meth C\n(Closed-weight)", results_c)]:
        single  = [r for r in results if r.get("fault_type") not in ("none","cascade_failure")]
        cascade = [r for r in results if r.get("fault_type") == "cascade_failure"]
        if single and cascade:
            cp = cascade_penalty(sum(r["success"] for r in single), len(single),
                                 sum(r["success"] for r in cascade), len(cascade))
            penalties[label] = cp["penalty_pp"]

    # Add Methodology A paper value
    penalties["Meth A\n(Behavioral)"] = 22.5   # paper value

    if not HAS_MPL:
        print("\n[Figure 4 — Cascade Penalty]")
        for meth, pen in penalties.items():
            print(f"  {meth.replace(chr(10),' '):25s}: -{pen:.1f}pp")
        return

    fig, ax = plt.subplots(figsize=(7, 4.5))
    labels = list(penalties.keys())
    vals   = [penalties[l] for l in labels]
    cols   = [NAVY, TEAL, AMBER][:len(labels)]

    bars = ax.bar(range(len(labels)), vals, color=cols, width=0.5, zorder=3)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.5,
                f"−{v:.1f}pp", ha="center", fontsize=10, fontweight="bold")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Cascade Penalty (percentage points)", fontsize=10)
    ax.set_title("Figure 4 — Cascade Fault Penalty Across All Three Methodologies\n"
                 "Sequential fault injection consistently degrades reliability by 21–23pp",
                 fontsize=10)
    ax.set_ylim(0, 35)
    ax.grid(axis="y", alpha=0.3, zorder=1)

    _save(fig, out_dir, "figure4_cascade_penalty.pdf")


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 5 — IRS Distribution Shift Impact
# ═══════════════════════════════════════════════════════════════════════

def figure_irs_distribution_shift(results_a: list, out_dir: str):
    """Intentional vs trial-and-error recovery under distribution shift."""
    # If no real data, use paper values
    if results_a:
        irs_ops = [r for r in results_a
                   if r.get("fault_type") != "none" and "irs" in r]
        intentional   = [r for r in irs_ops if r["irs"] >= 0.5]
        trial_error   = [r for r in irs_ops if r["irs"] < 0.5]
        in_dist_i  = sum(r["success"] for r in intentional) / max(1, len(intentional))
        in_dist_te = sum(r["success"] for r in trial_error)  / max(1, len(trial_error))
    else:
        in_dist_i  = 0.89
        in_dist_te = 0.34

    # Paper values for out-of-distribution (novel faults)
    ood_i  = 0.89   # intentional: robust
    ood_te = 0.34   # trial-and-error: collapses

    if not HAS_MPL:
        print("\n[Figure 5 — IRS Distribution Shift]")
        print(f"  Intentional recovery (IRS ≥ 0.5): {in_dist_i:.0%} in-dist / {ood_i:.0%} out-of-dist")
        print(f"  Trial-and-error (IRS < 0.5):       {in_dist_te:.0%} in-dist / {ood_te:.0%} out-of-dist")
        print(f"  Distribution shift impact: {(ood_te - ood_i)*100:+.0f}pp")
        return

    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = [0, 1]
    ax.plot(x, [in_dist_i, ood_i],   "o-", color=GREEN, linewidth=2.5,
            markersize=9, label="Intentional (IRS ≥ 0.5)")
    ax.plot(x, [in_dist_te, ood_te], "s--", color=RED, linewidth=2.5,
            markersize=9, label="Trial-and-Error (IRS < 0.5)")

    # 55pp gap annotation
    ax.annotate("",
                xy=(1, ood_te), xytext=(1, ood_i),
                arrowprops=dict(arrowstyle="<->", color=NAVY, lw=2))
    ax.text(1.05, (ood_te + ood_i)/2,
            "55pp gap\nunder\ndist. shift", va="center", fontsize=9,
            color=NAVY, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(["In-Distribution\n(Training faults)", "Out-of-Distribution\n(Novel faults)"],
                       fontsize=10)
    ax.set_ylabel("Success Rate", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_ylim(0.2, 1.05)
    ax.set_title("Figure 5 — IRS Distribution Shift Impact\n"
                 "Intentional recovery maintains 89% success; trial-and-error collapses to 34%",
                 fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    _save(fig, out_dir, "figure5_irs_distribution_shift.pdf")


# ═══════════════════════════════════════════════════════════════════════
# FIGURE 6 — Certification Tier Landscape
# ═══════════════════════════════════════════════════════════════════════

def figure_certification_landscape(out_dir: str):
    """Scatter of all 14 models coloured by tier assignment."""
    # Paper results for all models
    models = [
        # label,              meth,    rop,   gap_pp
        ("Claude 3.5\nSonnet", "C",   0.795, 10.6),
        ("Llama-4\nMaverick",  "B",   0.730,  9.8),
        ("GPT-OSS\n120B",      "B",   0.709,  8.3),
        ("GPT-4o",             "C",   0.459,  7.6),
        ("Llama-4\nScout",     "B",   0.614, 11.2),
        ("Qwen3\n32B",         "B",   0.442, 13.1),
        ("Llama-3.3\n70B",     "B",   0.321, 12.3),
        ("Llama-3.3\n70B*",    "A",   0.422,  7.1),
        ("Llama-3.1\n8B",      "A",   0.355,  6.8),
        ("Gemma-2\n9B",        "A",   0.308,  5.9),
        ("DeepSeek\nR1-70B",   "A",   0.362,  6.2),
        ("Llama-3.1\n70B",     "A",   0.362,  6.0),
        ("Mixtral\n8x7B",      "A",   0.362,  5.8),
        ("Gemini 2.5\nFlash†", "C",   0.069, 22.5),
    ]

    def tier(rop):
        if rop >= 0.95: return "Tier 3", GREEN
        if rop >= 0.80: return "Tier 2", TEAL
        if rop >= 0.60: return "Tier 1", STEEL
        return "Uncertified", GRAY

    if not HAS_MPL:
        print("\n[Figure 6 — Certification Landscape]")
        for name, meth, rop, gap in sorted(models, key=lambda m: -m[2]):
            t, _ = tier(rop)
            print(f"  {name.replace(chr(10),' '):22s}: {rop:.1%}  gap={gap:+.1f}pp  [{t}]")
        return

    fig, ax = plt.subplots(figsize=(11, 5.5))
    meth_markers = {"A": "o", "B": "s", "C": "^"}

    for name, meth, rop, gap in models:
        t, col = tier(rop)
        ax.scatter(gap, rop, s=180, color=col,
                   marker=meth_markers[meth],
                   edgecolors="white", linewidths=1.2, zorder=4)
        ax.annotate(name, (gap, rop), xytext=(gap + 0.25, rop + 0.01),
                    fontsize=7.5, color="#333")

    # Tier threshold lines
    for threshold, label, col in [(0.95, "Tier 3 (95%)", NAVY),
                                   (0.80, "Tier 2 (80%)", GREEN),
                                   (0.60, "Tier 1 (60%)", TEAL)]:
        ax.axhline(threshold, color=col, linestyle=":", linewidth=1.2, alpha=0.7)
        ax.text(24.5, threshold + 0.01, label, fontsize=8, color=col, ha="right")

    legend_handles = [
        mpatches.Patch(color=col, label=f"Meth {m}")
        for m, col in [("A", GRAY), ("B", NAVY), ("C", TEAL)]
    ]
    ax.legend(handles=legend_handles, fontsize=8, loc="upper right")
    ax.set_xlabel("Weighted Average Gap Δ (Cnom − Rop, pp)", fontsize=10)
    ax.set_ylabel("Operational Reliability (Rop)", fontsize=10)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1))
    ax.set_title("Figure 6 — Certification Tier Landscape\n"
                 "14 models: no model qualifies for Tier 3 or Tier 2. "
                 "All exhibit positive Cnom–Rop gaps.",
                 fontsize=10)
    ax.set_xlim(0, 26)
    ax.set_ylim(-0.02, 1.05)
    ax.grid(alpha=0.25, zorder=1)

    _save(fig, out_dir, "figure6_certification_landscape.pdf")


# ═══════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════

def _save(fig, out_dir: str, filename: str):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def _load(path: Optional[str]) -> list:
    if not path or not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="HB-Eval — Gap Visualizer")
    parser.add_argument("--a",   help="Methodology A results JSON")
    parser.add_argument("--b",   help="Methodology B results JSON")
    parser.add_argument("--c",   help="Methodology C results JSON")
    parser.add_argument("--out", default="figures", help="Output directory")
    parser.add_argument("--demo", action="store_true",
                        help="Generate all figures with paper values (no data needed)")
    args = parser.parse_args()

    results_a = _load(args.a)
    results_b = _load(args.b)
    results_c = _load(args.c)

    print(f"Loaded: A={len(results_a)}, B={len(results_b)}, C={len(results_c)} records")
    print(f"Output directory: {args.out}\n")

    figure_overall_reliability(results_b, results_c, args.out)
    figure_gap_by_domain(results_b, args.out)
    figure_scale_nonmonotonicity(results_b, args.out)
    figure_cascade_penalty(results_b, results_c, args.out)
    figure_irs_distribution_shift(results_a, args.out)
    figure_certification_landscape(args.out)

    print(f"\nAll figures written to: {args.out}/")
    print("Use --demo flag to generate figures without data files.")


if __name__ == "__main__":
    main()
