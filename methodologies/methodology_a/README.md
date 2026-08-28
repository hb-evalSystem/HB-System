# Methodology A — Behavioral Trajectory Analysis

## Overview

Methodology A evaluates **6 open-weight models** across **6 safety-critical domains** through **6,000 experiments** using four orthogonal reliability metrics. It constitutes the first of three independent validation frameworks in HB-Eval.

## Models Evaluated

| Study | Models | Domains | Runs |
|-------|--------|---------|------|
| Original (3,000) | Llama-3.3-70b, Llama-3.1-8b, Gemma-2-9b | Healthcare, Logistics, Mathematics | 1,000 each |
| Expansion (3,000) | DeepSeek-R1-70b, Llama-3.1-70b, Mixtral-8x7b | Cybersecurity, Emergency, Robotics | 1,000 each |

## Key Finding

Three architecturally distinct models — DeepSeek-R1 (chain-of-thought distillation), Llama-3.1-70b (standard transformer), and Mixtral-8x7b (mixture-of-experts) — converge at **identical 36.2% aggregate reliability** despite radical differences in architecture, training methodology, and parameter allocation. This convergence provides structural evidence of a universal constraint in current agentic paradigms.

## Four Metrics

**FRR (Failure Resilience Rate):** Graded scoring (0/0.4/0.7/1.0) measuring systematic recovery quality. Expert calibration: κ = 0.76 (95% CI [0.72, 0.80]).

**PEI (Planning Efficiency Index):** Trajectory optimality against oracle-verified minimal paths. PEI = (L_oracle / L_actual) × QF. Expert calibration: κ = 0.78.

**IRS (Intentional Recovery Score):** Novel metric distinguishing memory-guided recovery (89% success under distribution shift) from trial-and-error (34% — a 55pp gap). Only 23% of recoveries in the study were intentional.

**TI (Traceability Index):** Reasoning transparency via a calibrated LLM-as-judge (Pearson r = 0.89 with expert annotations). Methodology A records success/failure only; TI is measured in Methodologies B and C.

## Running the Experiment

```bash
# Replicate original validation (3,000 experiments)
python run_behavioral.py \
  --api-key YOUR_GROQ_KEY \
  --runs 1000 \
  --models llama-3.3-70b-versatile llama-3.1-8b-instant gemma2-9b-it \
  --output ../../data/results/methodology_a_original_3000.json

# Replicate expansion validation (3,000 experiments)
python run_behavioral.py \
  --api-key YOUR_GROQ_KEY \
  --runs 1000 \
  --models deepseek-r1-distill-llama-70b llama-3.1-70b-versatile mixtral-8x7b-32768 \
  --output ../../data/results/methodology_a_expansion_3000.json
```

## Requirements

- Python 3.8+
- `requests` library
- Groq API key (free tier sufficient — see https://console.groq.com)

## Estimated Cost

All six models are available on Groq free tier. Total cost: **$0.00**.
