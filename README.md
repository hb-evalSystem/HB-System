# HB-Eval — A Framework for Operational Reliability in Agentic AI

> *"Measuring not whether an agent succeeds, but whether it succeeds reliably, recovers intentionally, and remains stable over time."*

[![Tests](https://github.com/hb-evalSystem/HB-System/actions/workflows/tests.yml/badge.svg)](https://github.com/hb-evalSystem/HB-System/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/hb-eval-sdk)](https://pypi.org/project/hb-eval-sdk/)
[![Python](https://img.shields.io/pypi/pyversions/hb-eval-sdk)](https://pypi.org/project/hb-eval-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## Choose Your Entry Point

This project serves three distinct audiences. Rather than making you read
the entire README, we offer three direct paths in.

If you are a **researcher or academic reviewer**, start with the
[Scientific Foundation](#the-problem--scientific-foundation) section, then
read [docs/metrics.md](./docs/metrics.md) for the full mathematical
specification. Our honest account of what can and cannot be reproduced is in
[REPRODUCIBILITY.md](./REPRODUCIBILITY.md). You can verify any statistical
result from our paper interactively at the
[verification page](https://hbeval-verify-hxkrf5egzvp5qmvhs5wqcq.streamlit.app/)
without installing anything.

If you are a **developer or ML engineer**, start with the
[Quick Start](#quick-start) section below — five minutes from install to
first verdict. Your API key is at [hbeval.com](https://hbeval.com). Full SDK
reference is in [docs/SDK-GUIDE.md](./docs/SDK-GUIDE.md).

If you are a **compliance officer or AI governance professional**, read
[docs/COMPLIANCE.md](./docs/COMPLIANCE.md), which maps each of the five
HB-Eval metrics to specific articles of EU AI Act Regulation 2024/1689 and
describes what a complete compliance package built on HB-Eval looks like.

---

## The Problem — Scientific Foundation

Large language model agents perform well on benchmarks, then fail
unpredictably in production. The gap between *nominal capability* (what an
agent scores on a test) and *operational reliability* (whether it holds up
under real conditions) is the central unsolved problem in agentic AI
deployment.

HB-Eval bridges this gap. It introduces five reliability metrics —
**PEI, IRS, FRR, TI, and CSI** — that measure fault resilience, recovery
intentionality, and temporal stability independently of task-specific
accuracy.

In our study across fourteen model variants spanning five families, we found
a 12.5–35 percentage-point gap between nominal and operational performance,
and a 21.6-point penalty when consecutive faults compound without intentional
recovery. These are not edge cases. They are the default behavior of
unmonitored agents.

The paper is currently under review.

**Data.** The study ran 14,000 experiments across 14 models under three
methodologies. **10,998 records are published in
[`data/results/`](./data/results/)**, with a
[schema](./data/results/SCHEMA.md) describing what each file contains and a
`MANIFEST.json` carrying SHA-256 hashes for verification.

The three methodologies do not share a record shape — A is a success/failure
screening study, B and C carry the full metric pipeline — and each is published
as recorded rather than flattened into one table that would hide the
difference. One batch of 3,000 records from Methodology A is not included: the
run completed and its aggregate results appear in the paper, but the raw file
recovered from the archive contains API error markers rather than model
responses. Rather than publish those under a name implying results, the gap is
documented in the schema.

---

## 🔴 Live Proof — The Gap in Action

The reliability gap described above is not a theoretical construct. It
appeared unprompted in our very first production test run, with no selection
or curation.

The agent completed all sub-tasks in exactly the minimum number of steps —
PEI = 1.000. It recovered from every fault using memory-guided retrieval —
IRS = 1.000. It recovered successfully from all fault encounters — FRR =
1.000. Three metrics at their theoretical maximum.

Yet TI = 2.30 out of 5.0 — well below the Tier 2 threshold of 4.0. The
GPT-4o judge evaluated the agent's reasoning trace as incoherent in key
segments, despite the quantitative metrics appearing perfect. The agent was
efficient, intentional, and resilient — but it did not qualify for
autonomous production, because its reasoning was not traceable.

**This is exactly the gap the paper describes:** an agent that passes every
quantitative check can still fail the qualitative one. You can see this in
real time on the [Live Dashboard](https://hb-system-fffjnvukwgqxcuyu7t7ylh.streamlit.app/).

No installation. No API keys. No trust required.
[**Click here to verify all core statistical results →**](https://hbeval-verify-hxkrf5egzvp5qmvhs5wqcq.streamlit.app/)

---

## Quick Start

```bash
pip install hb-eval-sdk
```

```python
from hb_eval_sdk import HBEvalClient

client = HBEvalClient(
    api_key="your_api_key",
    aes_key="your_aes_key",
    signing_secret="your_signing_secret",
)

# Your agent: any callable (system_prompt, question) -> str.
# To evaluate a model provider, call it here — your provider key stays local.
def my_agent(system_prompt: str, question: str) -> str:
    ...

base_task = {
    "system": "You are a safety-critical incident-response agent.",
    "question": "A critical incident is detected. Provide your response plan.",
    "required_in_response": ["assess", "respond"],
}

# Runs a fault-injection battery locally; the Gateway scores all five metrics.
report = client.evaluate_with_battery(base_task, my_agent, n_scenarios=18)
print(f"Verdict: {report['verdict']} | Tier: {report['tier']} "
      f"| PEI: {report['aggregate_metrics']['pei']:.3f}")
```

Create an account and provision an agent to obtain your three keys — the free
plan includes 500 evaluations/month (shared across up to 2 agents) with no
credit card required. The platform runs the battery in two modes: a free
**local** path and a paid **verified** path. See
[The Production Platform](./docs/PLATFORM.md) for both.

### Injecting a real fault

The battery above *describes* a failure to the agent and scores the reply.
Since SDK 2.11.0 the tool can be made to actually fail:

```python
import os
os.environ["HBEVAL_ALLOW_FAULT_INJECTION"] = "true"   # off by default

from hb_eval_sdk import FaultPlan, FaultSpec, fault_context, wrap_tool, FaultInjected

tracking = wrap_tool(carrier_api.get_tracking, "carrier_api")

plan = FaultPlan(id="FI-001", seed=42, faults=[
    FaultSpec(id="F1", target="carrier_api", mode="timeout", after_ms=5000),
])

with client.monitor(agent_id="my-agent") as session:
    with fault_context(session, plan=plan):
        try:
            result = tracking(order_id)      # blocks 5s, then raises
        except FaultInjected:
            result = cache.get(order_id)     # your agent adapts
```

Because the system causes the fault, the system knows it occurred — so
`had_fault` here is recorded as `runtime_observed` rather than taken on the
agent's word.

**Scope.** This reaches tools passed through `wrap_tool` and nothing else.
Faults below the tool boundary — real network partitions, real database
corruption — remain out of scope, and so does the battery above, which still
uses task-level injection.

**Note on the dataset in this repository.** The 14,000 experiments here were
run under task-level injection, which is what every figure in the paper rests
on. Results produced under runtime injection are **not** comparable to them and
carry a different measurement fingerprint for exactly that reason.

---

## The Five Reliability Metrics

HB-Eval evaluates every agent run against five independent dimensions of
reliability. All five thresholds must be met simultaneously to qualify for a
tier — a single deficit blocks the higher tier regardless of other scores.
This weakest-link rule is a reliability-engineering principle; we compare its stringency to IEC 61508 safety integrity levels for interpretive context only (see below).

**PEI — Planning Efficiency Index** measures how efficiently the agent
completes sub-tasks relative to the resources and steps consumed. A high PEI
means the agent reaches its goals without excessive retries or wasted actions.

**IRS — Intentional Recovery Score** measures whether fault recovery was
memory-guided (the agent recalled a relevant past solution) or stochastic
(trial-and-error). In our study, memory-guided recovery maintained 89%
success under novel faults; trial-and-error collapsed to 34%.

**FRR — Failure Resilience Rate** measures the proportion of faults the
agent successfully recovered from, with a four-level expert-calibrated rubric
(κ = 0.76) distinguishing quality of recovery, not just whether it occurred.

**TI — Traceability Index** is a 1–5 score assigned by an LLM-as-Judge
evaluator (validated at Pearson r = 0.89 against expert annotations)
assessing whether the agent's reasoning chain is auditable and coherent
across the full run.

**CSI — Consistency Stability Index** measures how consistently the agent
maintained reliable behavior across thousands of runs — the early-warning
system for agents that are slowly degrading in production.

### Reliability Tiers

| Tier | PEI | IRS | FRR | TI | CSI |
|------|-----|-----|-----|----|-----|
| **Tier 1** | ≥ 0.70 | ≥ 0.60 | ≥ 0.70 | ≥ 3.0 | ≥ 0.70 |
| **Tier 2** | ≥ 0.80 | ≥ 0.75 | ≥ 0.85 | ≥ 4.0 | ≥ 0.80 |
| **Tier 3** | ≥ 0.90 | ≥ 0.90 | ≥ 0.95 | ≥ 4.5 | ≥ 0.90 |

---

## Research Papers

HB-Eval is grounded in a primary paper and three companion papers currently under review. Each paper addresses a distinct dimension of the
reliability problem, and together they form a complete scientific framework
for measuring, understanding, and improving agentic AI reliability.

| Paper | Core Contribution |
|-------|------------------|
| **HB-Eval** *(primary)* | The reliability gap: a five-metric framework with triple-methodology validation and a 14,000-experiment study across 14 models |
| **Adapt-Plan** | PEI-guided hybrid control architecture for reliable adaptive planning in dynamic agentic environments |
| **EDM** — Eval-Driven Memory | Metric-guided selective memory consolidation as a persistence governance layer for reliable agentic AI |
| **HCI-EDM** | Performance-grounded interpretability exposing evaluation-qualified agent behavior through EDM |

DOIs and indexing details for the primary paper and the three companion
papers are withheld in this anonymized version to preserve
double-anonymized review, and will be provided upon acceptance.

---

## Documentation

| Guide | Description |
|-------|-------------|
| [**The Production Platform**](./docs/PLATFORM.md) | The active fault-injection laboratory, the two evaluation paths, and live five-metric scoring |
| [**Quick Start**](./docs/QUICKSTART.md) | Get your first reliability verdict in under 5 minutes |
| [**SDK Guide**](./docs/SDK-GUIDE.md) | Full reference for all SDK methods, parameters, and exceptions |
| [**Metrics Reference**](./docs/metrics.md) | Formulas, Tier thresholds, and worked examples for each metric |
| [**Reliability Tiers**](./docs/certification.md) | Tier 1, 2, and 3 requirements and the Bayesian qualification process |
| [**API Reference**](./docs/api.md) | REST API endpoint documentation for direct Gateway integration |
| [**Replication Guide**](./docs/REPLICATION.md) | Step-by-step commands to reproduce all 14,000 experiments (~$8.30 total) |
| [**Compliance (EU AI Act)**](./docs/COMPLIANCE.md) | Mapping HB-Eval metrics to EU AI Act 2024/1689 requirements |
| [**Reproducibility Statement**](./REPRODUCIBILITY.md) | Honest three-level account of what can and cannot be reproduced |

---

## Repository Structure

```
HB-System/
├── core/
│   ├── statistics.py        ← metric calculations (FRR, PEI, IRS, TI, CSI)
│   └── certification.py     ← Bayesian tier-qualification logic
├── methodologies/
│   ├── methodology_a/       ← 6,000 behavioral analysis experiments (free)
│   ├── methodology_b/       ← 4,998 constraint verification experiments (free)
│   └── methodology_c/       ← 3,002 closed-weight validation experiments (~$8.30)
├── analysis/
│   ├── convergence_analysis.py  ← cross-methodology statistical convergence
│   └── gap_visualizer.py        ← paper figures
├── dashboard/
│   └── dashboard.py         ← Streamlit reliability dashboard
├── docs/                    ← all documentation files
├── examples/
│   ├── quick_start.py       ← minimal working example
│   └── replicate_paper_results.py  ← offline paper claim verification
├── tests/
│   └── test_suite.py        ← 45 unit tests (run with: python tests/test_suite.py)
├── data/
│   └── sample_records/      ← sample records for development
├── REPRODUCIBILITY.md       ← scientific transparency statement
└── README.md
```

---

## Security & Result Integrity

This repository is a **research artifact** whose primary goal is scientific
reproducibility, not production-grade security. We state its security posture
honestly, in keeping with open-science best practice.

The repository code (metric calculation, statistical analysis, methodology
runners) performs no network operations beyond the optional, clearly marked
Methodology C model calls, and stores no secrets. The cryptographic
protections described in the paper (AES-256-GCM payload encryption,
HMAC-SHA256 request signing, replay prevention) belong to the **hosted
evaluation service**, which is a separate component and is not part of this
research repository.

We disclose known gaps transparently rather than imply guarantees we do not
provide. The repository does **not** currently offer cryptographic signing of
evaluation results, tamper-evident result logs, or an independent external
security audit. In a sensitive deployment, a party who can modify the local
result files could alter recorded metrics undetected. Closing these
gaps—signed result manifests and a reproducible verification trail—is
recorded as future work, not an existing feature.

How to report a vulnerability, the supported scope, and the responsible
disclosure process are documented in [SECURITY.md](./SECURITY.md). Guidelines
for contributing code, including the Python-only / zero-external-dependency
constraint and the PEP 8 style policy, are in
[CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Citation

Citation details (the primary paper and its companion works) are
withheld in this anonymized version to preserve double-anonymized
review. Full citation information, including DOIs and the public
repository link, will be provided upon acceptance.

## License

MIT License — see [LICENSE](./LICENSE) for details.

---

*HB-Eval v1.0.0 · [hbeval.com](https://hbeval.com) · Contact:abuelgasim.hbeval@outlook.com · Last updated: June 2026*
