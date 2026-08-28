# HB-Eval Replication Guide

## Overview

This guide provides a complete, step-by-step walkthrough for reproducing every result in the HB-Eval paper. The full study of 14,000 evaluations across 14 models costs approximately **$8.30 USD** and requires roughly 16 hours of sequential execution. Steps 1–3 are entirely free.

---

## Prerequisites

**Software:** Python 3.8 or higher, `pip install -r requirements.txt`

**API Keys Required:**

| Key | Used For | Cost | Obtain At |
|-----|---------|------|-----------|
| Groq API key | Methodologies A and B (all open-weight models) | Free | https://console.groq.com |
| OpenRouter key | Methodology C: GPT-4o and Claude 3.5 Sonnet | ~$8.10 | https://openrouter.ai |
| Google AI Studio key | Methodology C: Gemini 2.5 Flash | ~$0.20 | https://aistudio.google.com |

---

## Step 1: Methodology A — Original Validation (3,000 experiments)

Models evaluated: Llama-3.3-70B, Llama-3.1-8B, Gemma-2-9B  
Domains: Healthcare, Logistics, Mathematics  
Estimated time: ~4 hours | Cost: $0.00

```bash
python methodologies/methodology_a/run_behavioral.py \
  --api-key YOUR_GROQ_KEY \
  --runs 1000 \
  --models llama-3.3-70b-versatile llama-3.1-8b-instant gemma2-9b-it \
  --output data/results/methodology_a_original_3000.json
```

Results are saved after every evaluation. If the run is interrupted, add `--resume` to continue from the last saved position.

**Expected output:** Aggregate reliability 30–42% across models with selective domain collapse (0% in some domains, 100% in mathematics).

---

## Step 2: Methodology A — Expansion Validation (3,000 experiments)

Models evaluated: DeepSeek-R1-Distill-70B, Llama-3.1-70B, Mixtral-8x7B-MoE  
Domains: Cybersecurity, Emergency Response, Robotics  
Estimated time: ~4 hours | Cost: $0.00

```bash
python methodologies/methodology_a/run_behavioral.py \
  --api-key YOUR_GROQ_KEY \
  --runs 1000 \
  --models deepseek-r1-distill-llama-70b llama-3.1-70b-versatile mixtral-8x7b-32768 \
  --output data/results/methodology_a_expansion_3000.json
```

**Expected output:** Three architecturally distinct models converge at 36.2% reliability, replicating the selective collapse pattern from the original validation.

---

## Step 3: Methodology B — Constraint Verification (4,998 evaluations)

Models evaluated: Llama-4-Maverick-17B, GPT-OSS-120B, Llama-4-Scout-17B, Qwen3-32B, Llama-3.3-70B  
Domains: Cybersecurity, Emergency Response, Robotics, Medical, Logistics  
Estimated time: ~6 hours | Cost: $0.00

Edit `methodologies/methodology_b/hb_eval_v5.py` — set your Groq key and run count:

```python
GROQ_API_KEY = "gsk_your_key_here"
TOTAL_RUNS   = 1000
```

Then run:

```bash
python methodologies/methodology_b/hb_eval_v5.py
```

The script saves progress after every single evaluation. A quick validation run with `TOTAL_RUNS = 50` takes approximately 5 minutes.

**Expected output:** Weighted average Cnom–Rop gap of +12.5pp. Scale non-monotonicity: Maverick-17B at 73.0% vs Llama-3.3-70B at 32.1% (+40.9pp gap despite 4.1× fewer parameters).

---

## Step 4: Methodology C — Closed-Weight Validation (3,002 evaluations)

Models evaluated: GPT-4o, Claude 3.5 Sonnet, Gemini 2.5 Flash  
Independent judge: Groq/Llama-4-Maverick (free, blind evaluation)  
Estimated time: ~2 hours | Cost: ~$8.30

Edit `methodologies/methodology_c/hb_eval_v7_openrouter.py` — configure all keys:

```python
OPENROUTER_API_KEY = "sk-or-your_key"      # GPT-4o + Claude 3.5
GOOGLE_API_KEY     = "AIzaSy_your_key"     # Gemini 2.5 Flash
GROQ_JUDGE_API_KEY = "gsk_your_key"        # Independent judge (free)
RUNS_PER_MODEL     = 1000
```

Then run:

```bash
python methodologies/methodology_c/hb_eval_v7_openrouter.py
```

The script executes Gemini sequentially (15 RPM free tier, ~67 minutes), then GPT-4o and Claude 3.5 via OpenRouter. Progress is saved after every call. If only the Google key is available, Gemini results alone will be generated and the script will skip GPT-4o and Claude.

**Expected output:** Claude 3.5 Sonnet 79.5% binary, GPT-4o 45.9%, Gemini 6.9% (cybersecurity only). Cascade penalty −22.5pp for Claude 3.5, matching Methodology B's −21.6pp.

---

## Step 5: Convergence Analysis

```bash
python analysis/convergence_analysis.py \
  --a data/results/methodology_a_combined_6000.json \
  --b data/results/methodology_b_4998.json \
  --c data/results/methodology_c_3002.json \
  --out data/results/convergence_report.json
```

Or run with synthetic data to verify formulas without result files:

```bash
python analysis/convergence_analysis.py --demo
```

**Expected output:** z = 0.653, p = 0.514 for Methodology A vs B (convergence confirmed).

---

## Step 6: Generate Paper Figures

```bash
python analysis/gap_visualizer.py \
  --b data/results/methodology_b_4998.json \
  --c data/results/methodology_c_3002.json \
  --out figures/
```

This generates six publication-quality PDF figures matching those in the paper. Without result files, the script falls back to paper values for all data points.

---

## Verification Without Running Experiments

To verify that the statistical formulas reproduce all published numbers without executing any experiments:

```bash
python examples/replicate_paper_results.py --verify
```

This checks 10 paper claims including the convergence test, cascade penalty, Bayesian tier assignments, and confidence intervals — all offline in under 5 seconds.

---

## Resuming Interrupted Runs

All three methodologies implement automatic progress saving. Methodology A saves after every evaluation and accepts `--resume`. Methodologies B and C save after every single API call and resume automatically when re-executed with the same configuration. No data is lost on interruption.

---

## Troubleshooting

**HTTP 429 Rate Limit:** All scripts implement exponential backoff. For Groq free tier, the default `time.sleep(1.0)` between calls is sufficient. If sustained 429s occur, increase the sleep interval in the configuration section.

**Gemini 0% in multiple domains:** This is an expected finding (generational gap, §9), not a configuration error. Gemini 2.5 Flash in its evaluated version does not reliably produce valid JSON in four of five domains.

**Model ID not found (HTTP 400):** Groq model IDs change as new versions are released. Run the `verify_models()` function in `hb_eval_v5.py` to confirm which models are available on your account.

**Results diverge from paper:** Minor variance is expected due to model non-determinism even at temperature 0.0. Aggregate metrics across 1,000 runs should match paper values within ±2pp.
