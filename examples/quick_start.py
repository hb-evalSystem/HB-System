"""
HB-Eval Quick Start
====================
A self-contained demonstration that runs entirely offline — no API keys required.
Illustrates the three-layer evaluation pipeline and tier-qualification framework.

Run:
    python examples/quick_start.py

To run a real evaluation (requires Groq API key):
    python examples/quick_start.py --live --api-key YOUR_KEY
"""

import argparse
import json
import os
import random
import sys
import time

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from core.statistics import (
    two_proportion_z_test,
    gap_significance,
    proportion_ci,
)
from core.certification import assess_model, print_certification_report


# ═══════════════════════════════════════════════════════════════════════
# OFFLINE DEMO MODE
# ═══════════════════════════════════════════════════════════════════════

def run_offline_demo():
    """Simulate the evaluation pipeline with synthetic data."""
    print("=" * 62)
    print("  HB-Eval Quick Start — Offline Demo")
    print("  (Reproduces paper results without API calls)")
    print("=" * 62)

    random.seed(2026)
    domains = ["cybersecurity", "emergency_response", "robotics", "medical", "logistics"]

    # Simulate Claude 3.5 Sonnet results (79.5% aggregate reliability, per paper)
    print("\n[1] Simulating 1,000 evaluations (Claude 3.5 Sonnet profile)...")
    results = []
    model_rates = {
        "cybersecurity":      0.76,
        "emergency_response": 0.65,
        "robotics":           0.92,
        "medical":            0.81,
        "logistics":          0.83,
    }
    nominal_rates = {
        "cybersecurity":      0.91,
        "emergency_response": 1.00,
        "robotics":           0.98,
        "medical":            0.95,
        "logistics":          0.94,
    }

    fault_types = ["adversarial", "context_corruption", "tool_failure",
                   "stochastic", "cascade_failure"]

    for i in range(1000):
        domain = domains[i % len(domains)]
        # 20% nominal, 80% fault
        is_nominal = (i % 5 == 0)
        ft = "none" if is_nominal else fault_types[i % len(fault_types)]
        rate = nominal_rates[domain] if is_nominal else model_rates[domain]
        ok   = int(random.random() < rate)
        results.append({
            "run_id":          i,
            "model":           "Claude-3.5-Sonnet",
            "domain":          domain,
            "fault_type":      ft,
            "success":         ok,
            "violation_count": 0 if ok else random.randint(1, 3),
            "adv_resistance":  (ok if ft in ("adversarial","cascade_failure") else None),
            "composite_score": 0.85 if ok else 0.28,
        })

    print(f"   Generated {len(results)} records across {len(domains)} domains")
    print(f"   Nominal trials: {sum(1 for r in results if r['fault_type']=='none')} "
          f"({sum(1 for r in results if r['fault_type']=='none')/len(results):.0%})")

    # ── Step 2: Compute metrics ──────────────────────────────────────
    print("\n[2] Computing Cnom–Rop gap by domain...")
    print(f"\n   {'Domain':22s} {'Cnom':>7} {'Rop':>7} {'Δpp':>7}  {'±CI':>6}  {'Sig':>5}")
    print(f"   {'─'*56}")

    for domain in domains:
        nom = [r for r in results if r["domain"] == domain and r["fault_type"] == "none"]
        ops = [r for r in results if r["domain"] == domain and r["fault_type"] != "none"]
        if not nom or not ops:
            continue
        g    = gap_significance(sum(r["success"] for r in nom), len(nom),
                                sum(r["success"] for r in ops), len(ops))
        sig  = "***" if g["p_value"] < 0.001 else ("**" if g["p_value"] < 0.01 else "n.s.")
        sign = "↓" if g["delta_pp"] > 0 else "↑"
        print(f"   {domain:22s} {g['cnom']:>6.1%} {g['rop']:>7.1%} "
              f"  {sign}{abs(g['delta_pp']):>4.1f}pp  ±{g['ci_pp']:>3.1f}  {sig}")

    # ── Step 3: Cascade penalty ───────────────────────────────────────
    print("\n[3] Cascade fault penalty analysis...")
    single   = [r for r in results if r["fault_type"] not in ("none","cascade_failure")]
    cascade  = [r for r in results if r["fault_type"] == "cascade_failure"]
    p_s = sum(r["success"] for r in single)  / len(single)
    p_c = sum(r["success"] for r in cascade) / len(cascade)
    z, pv = two_proportion_z_test(p_s, len(single), p_c, len(cascade))
    print(f"   Single fault:  {p_s:.1%}  (n={len(single)})")
    print(f"   Cascade fault: {p_c:.1%}  (n={len(cascade)})")
    print(f"   Penalty:       {(p_s-p_c)*100:+.1f}pp  (paper: −22.5pp)")
    print(f"   z={z:.2f}  p={'<0.001' if pv<0.001 else f'{pv:.3f}'}")

    # ── Step 4: Certification assessment ─────────────────────────────
    print("\n[4] Certification tier assessment...")
    assessment = assess_model(results, domains, "Claude-3.5-Sonnet (simulated)")
    print_certification_report(assessment)

    # ── Step 5: Cross-methodology convergence ────────────────────────
    print("\n[5] Reproducing paper convergence test...")
    z_paper, p_paper = two_proportion_z_test(0.362, 6000, 0.356, 4998)
    print(f"   Meth A (36.2%, n=6000) vs Meth B (35.6%, n=4998)")
    print(f"   z = {z_paper:.3f}  (paper: 0.653)")
    print(f"   p = {p_paper:.3f}  (paper: 0.514)")
    print(f"   Conclusion: {'CONVERGED ✓' if p_paper > 0.05 else 'DIVERGED ✗'} "
          f"(p > 0.05 → methods statistically equivalent)")

    print("\n" + "=" * 62)
    print("  Demo complete.")
    print("  To run a live evaluation:")
    print("  python examples/quick_start.py --live --api-key YOUR_GROQ_KEY")
    print("=" * 62)


# ═══════════════════════════════════════════════════════════════════════
# LIVE MODE
# ═══════════════════════════════════════════════════════════════════════

def run_live_evaluation(api_key: str, runs: int = 50, model: str = "llama-3.3-70b-versatile"):
    """Run a minimal live evaluation (50 runs) using Methodology B."""
    print("=" * 62)
    print("  HB-Eval Quick Start — Live Evaluation")
    print(f"  Model: {model}")
    print(f"  Runs:  {runs}")
    print("=" * 62)

    # Import v5 components
    src = open(os.path.join(ROOT, "methodologies/methodology_b/hb_eval_v5.py")).read()
    src = src.replace(
        'GROQ_API_KEY = "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"',
        f'GROQ_API_KEY = "{api_key}"'
    ).replace("TOTAL_RUNS = 50", f"TOTAL_RUNS = {runs}")

    # Write temporary file and execute
    tmp_path = "/tmp/hb_eval_v5_live.py"
    with open(tmp_path, "w") as f:
        f.write(src.replace("MODELS_TO_TEST = [", f'MODELS_TO_TEST = ["{model}", #'))
    print("Starting evaluation — results saved incrementally to hb_eval_v5_results.json")
    os.system(f"python {tmp_path}")


# ═══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="HB-Eval Quick Start")
    parser.add_argument("--live",    action="store_true",
                        help="Run live evaluation (requires --api-key)")
    parser.add_argument("--api-key", help="Groq API key")
    parser.add_argument("--model",   default="llama-3.3-70b-versatile",
                        help="Model ID for live evaluation")
    parser.add_argument("--runs",    type=int, default=50,
                        help="Number of runs for live evaluation")
    args = parser.parse_args()

    if args.live:
        if not args.api_key:
            print("ERROR: --api-key required for live mode")
            sys.exit(1)
        run_live_evaluation(args.api_key, args.runs, args.model)
    else:
        run_offline_demo()


if __name__ == "__main__":
    main()
