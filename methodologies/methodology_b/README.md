# Methodology B — Three-Layer Constraint Verification

## Overview

Methodology B evaluates **5 frontier open-weight models** through **4,998 assessments** using a three-layer validation architecture. Each assessment combines deterministic constraint checking (Layer 2) with LLM-as-judge holistic evaluation (Layer 3), producing both a binary reliability score and a composite score.

This is the **primary implementation** — see `hb_eval_v5.py` for the complete, production-tested code that generated the paper's 4,998 evaluations.

## Models Evaluated

| Model | Organization | Parameters | Binary Reliability |
|-------|-------------|------------|-------------------|
| Llama-4-Maverick-17b | Meta AI | 17B | **73.0%** |
| GPT-OSS-120b | OpenAI | 120B | 70.9% |
| Llama-4-Scout-17b | Meta AI | 17B | 61.4% |
| Qwen3-32b | Alibaba | 32B | 44.2% |
| Llama-3.3-70b | Meta AI | 70B | 32.1% |

## Three-Layer Architecture

**Layer 1 — JSON Extraction:** Five progressive fallback strategies ensure maximum coverage even when models include markdown fences, preamble text, or produce truncated outputs.

**Layer 2 — Deterministic Constraint Checking:** Fully objective evaluation against hard constraints explicitly stated in each task. No semantic interpretation — pure rule-based verification. Weight: 60%. This layer makes the `constraint_score` publishable as a rigorous metric.

**Layer 3 — LLM Safety Judge:** The evaluated model itself assesses the overall safety of its decision. Acknowledged limitation (self-evaluation) mitigated by: ground-truth constraints provided in the prompt, temperature zero, and 40% weight cap. Layer 2/3 agreement: 87%.

**Composite Score:** `0.6 × constraint_score + 0.4 × judge_score`

## Five Domains and Five Fault Types

Domains: cybersecurity, emergency\_response, robotics, medical, logistics

Fault types: adversarial, context\_corruption, tool\_failure, stochastic, cascade\_failure (most realistic: combines information and instruction corruption simultaneously)

## Key Findings

**Scale Non-Monotonicity:** Maverick-17B outperforms Llama-3.3-70b by **40.9pp** despite having 4.1× fewer parameters. Scale alone does not predict reliability.

**Weighted Average Gap:** Cnom − Rop = **+12.5pp** across all domains and models.

**Cascade Penalty:** −21.6pp reliability degradation under sequential fault injection (z = 10.80, p < 0.001).

**Adversarial Resistance:** 64.4% overall (Claude 3.5 Sonnet reference); cybersecurity: 100%; emergency: 3.1% — revealing domain-specific training effects.

## Running the Experiment

```bash
# Quick validation run (50 experiments — ~5 minutes)
python hb_eval_v5.py  # edit GROQ_API_KEY and set TOTAL_RUNS = 50

# Full paper replication (1000 runs × 5 models = 4,998 evaluations)
# Edit hb_eval_v5.py:
#   GROQ_API_KEY = "your-key-here"
#   TOTAL_RUNS   = 1000
python hb_eval_v5.py
```

Results are saved incrementally to `hb_eval_v5_results.json` after every evaluation. Safe to interrupt and resume.

## Requirements

- Python 3.8+
- `requests` library
- Groq API key (free tier — https://console.groq.com)

## Estimated Cost

All models run on Groq free tier. Total cost: **$0.00**

Estimated runtime: ~6 hours for 1,000 runs with 5 models at free-tier rate limits.
