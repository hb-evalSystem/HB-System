# Methodology C — Closed-Weight Validation with Independent Judge

## Overview

Methodology C extends HB-Eval to three leading commercial models — GPT-4o, Claude 3.5 Sonnet, and Gemini 2.5 Flash — across **3,002 evaluations**. The critical methodological advance over Methodology B is the use of **Groq/Llama-4-Maverick as an independent third-party judge** (Layer 3), operating blind to model identity, thereby eliminating self-evaluation bias.

This is the **complete production implementation** — see `hb_eval_v7_openrouter.py` for the full code that generated the paper's 3,002 evaluations across three organisations.

## Models and Access

| Model | Organisation | API Access | Cost (1,000 runs) |
|-------|-------------|-----------|-------------------|
| GPT-4o | OpenAI | OpenRouter | ~$3.38 |
| Claude 3.5 Sonnet | Anthropic | OpenRouter | ~$4.72 |
| Gemini 2.5 Flash | Google DeepMind | Google AI Studio | ~$0.20 |
| **Groq/Maverick (Judge)** | **Meta AI** | **Groq (free)** | **$0.00** |

**Total estimated cost for full replication: ~$8.30 USD**

## Independent Judge Design

The Layer 3 judge (Groq/Llama-4-Maverick-17b) evaluates outputs from all three models at `temperature=0.0`, receiving the task's hard constraints and the first 600 characters of the model's response. The judge is called only when Layer 2 finds violations or the fault type is adversarial/cascade — a cost optimisation that does not affect coverage of critical cases. Layer 2 / independent judge agreement: 85%.

## Key Results

| Metric | GPT-4o | Claude 3.5 Sonnet | Gemini 2.5 Flash |
|--------|--------|--------------------|-----------------|
| Binary Reliability | 45.9% | **79.5%** | 6.9%* |
| Weighted Avg Gap Δ | +7.6pp | +10.6pp | +22.5pp* |
| Cascade Penalty | −9.4pp | −22.5pp | −7.5pp |
| Adversarial Resistance | 48.1% | 64.4% | — |

*Gemini results valid in cybersecurity domain only; 0% in four domains reflects a JSON format non-compliance pattern in the preview release — identified as a generational gap finding (see paper §9).

**Largest single gap observed in the entire study:** Claude 3.5 Sonnet in emergency response — +35.0pp (Cnom = 100%, Rop = 65%, p < 0.001).

**Cascade penalty replication:** Claude 3.5's −22.5pp matches Methodology B's −21.6pp across independent open-weight models, confirming the cascade effect as an architectural property rather than a model-specific artifact.

## Two-Phase Execution

```bash
# Phase 1: Configure API keys in hb_eval_v7_openrouter.py, then run
python hb_eval_v7_openrouter.py
# → Starts Gemini sequential run immediately (~67 min at free-tier 15 RPM)
# → Starts GPT-4o and Claude 3.5 via OpenRouter sequentially

# Phase 2: Script auto-detects existing progress files and resumes
python hb_eval_v7_openrouter.py
# → Evaluates all collected responses through 3-layer pipeline
# → Generates full comparative summary
```

Progress is saved after every API call. The experiment is safe to interrupt and resume at any point.

## Configuration

Edit the configuration block at the top of `hb_eval_v7_openrouter.py`:

```python
OPENROUTER_API_KEY = "sk-or-..."     # covers GPT-4o + Claude 3.5
GOOGLE_API_KEY     = "AIzaSy..."     # Gemini 2.5 Flash (free tier)
GROQ_JUDGE_API_KEY = "gsk_..."      # independent judge (free tier)
RUNS_PER_MODEL     = 1000            # set to 50 for quick validation
```

## Requirements

- Python 3.8+
- `requests` library
- OpenRouter account: https://openrouter.ai
- Google AI Studio key: https://aistudio.google.com
- Groq key: https://console.groq.com
