<p align="center">
  <a href="https://github.com/hb-evalSystem/HB-System">
    <img src="https://github.com/hb-evalSystem/HB-System/blob/main/assets/hb-eval-logo.png" alt="HB-Eval System" width="520"/>
  </a>
</p>

<h1 align="center">HB-Eval System™</h1>
<h3 align="center"><b>Behavioral Evaluation & Trustworthy Agentic AI Framework</b></h3>

<p align="center">
  <a href="https://github.com/hb-evalSystem/HB-System/releases"><img src="https://img.shields.io/github/v/release/hb-evalSystem/HB-System?label=Latest%20Release&style=for-the-badge" alt="Release"/></a>
  <img src="https://img.shields.io/badge/PEI-0.92-brightgreen?style=for-the-badge" alt="PEI"/>
  <img src="https://img.shields.io/badge/FRR-92%25-success?style=for-the-badge" alt="FRR"/>
  <img src="https://img.shields.io/badge/Human%20Trust-4.62%2F5.0-blueviolet?style=for-the-badge" alt="Trust"/>
  <img src="https://img.shields.io/github/stars/hb-evalSystem/HB-System?style=for-the-badge&color=yellow" alt="Stars"/>
  <img src="https://img.shields.io/github/forks/hb-evalSystem/HB-System?style=for-the-badge&color=lightblue" alt="Forks"/>
</p>

<p align="center">
  <b>500-Task Longitudinal Benchmark • 4-Paper Series (Nov 2025) • Open-Core (Apache 2.0)</b>
</p>

> **"The first complete framework that actually solves the four biggest problems in Agentic AI."**

---

## Why HB-Eval System Exists

| Problem                     | Current Solutions (2025)                  | HB-Eval System Solution                          | Result                     |
|----------------------------|-------------------------------------------|--------------------------------------------------|----------------------------|
| Unreliable Evaluation       | Accuracy-only metrics                     | PEI / FRR / TI (behavioral)                      | PEI = **0.92**             |
| Agents get stuck & fail     | Retry / human-in-the-loop                 | Quantitative MetaController                     | FRR = **92%**              |
| Poor long-term memory       | Vector DB spam                            | Eval-Driven Memory (EDM) – stores only high-PEI   | MRS = **0.07**             |
| Humans don’t trust output   | Tracing tools only                        | HCI-EDM – full human-readable explanations       | Trust = **4.62/5.0**       |

**HB-Eval is the only system that closes all four gaps with reproducible, quantitative metrics.**

## Key Metrics (Formal Definitions)

| Metric | Formula | HB-System (Nov 2025) |
|-------|--------|----------------------|
| **PEI** (Performance Evaluation Index) | `PEI = 0.5·A + 0.3·S + 0.2·C` | **0.92** |
| **FRR** (Failure Recovery Rate)       | `FRR = Recovered / Total Failures` | **92%** |
| **MRS** (Memory Redundancy Score)      | `MRS = Duplicates / Total Entries` | **0.07** |
| **Trust Score** (240 participants)     | 5-point Likert (κ=0.81) | **4.62 / 5.0** |

Full definitions & derivations → [docs/metrics.md](docs/metrics.md)

## Architecture Overview

```text
                    ┌─────────────────┐
                    │   MetaController│ ← Quantitative (zero LLM)
                    └───────┬─────────┘
                            ▼
               ┌─────────────────────────────┐
               │        Agent Loop           │
               │  Evaluation → Adaptation    │
               │        → Memory → Trust     │
               └───────┬──────────┬──────────┘
   Evaluation ◀──────┘          │
                                 ▼
                         Eval-Driven Memory (EDM)
                                 ▼
                         HCI-EDM Explanations
