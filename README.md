<p align="center">
  <a href="https://github.com/hb-evalSystem/HB-System">
    <img src="https://github.com/hb-evalSystem/HB-System/blob/main/assets/hb-eval-logo.png" alt="HB-Eval System" width="520"/>
  </a>
</p>

<h1 align="center">HB-Eval System™</h1>
<h3 align="center"><b>Behavioral Evaluation & Trustworthy Agentic AI Framework</b></h3>

<p align="center">
  <a href="https://github.com/hb-evalSystem/HB-System/releases"><img src="https://img.shields.io/github/v/release/hb-evalSystem/HB-System?label=Latest%20Release&style=for-the-badge" alt="Release"/></a>
  <img src="https://img.shields.io/badge/PEI-0.92-brightgreen?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/FRR-92%25-success?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Human%20Trust-4.62%2F5.0-blueviolet?style=for-the-badge"/>
  <img src="https://img.shields.io/github/stars/hb-evalSystem/HB-System?style=for-the-badge&color=yellow"/>
  <img src="https://img.shields.io/github/forks/hb-evalSystem/HB-System?style=for-the-badge&color=lightblue"/>
</p>

<p align="center">
  <b>500-Task Longitudinal Benchmark • 4-Paper Series (Nov 2025) • Open-Core (Apache 2.0)</b>
</p>

> **"The first complete framework that actually solves the four biggest problems in Agentic AI."**

---

## Why HB-Eval System Exists

| Problem                     | Current Solutions (2025)         | HB-Eval System Solution                        | Result                |
|----------------------------|----------------------------------|------------------------------------------------|-----------------------|
| Unreliable Evaluation       | Accuracy-only metrics            | PEI / FRR / TI (behavioral)                    | PEI = **0.92**        |
| Agents get stuck & fail     | Retry / human-in-the-loop        | Quantitative MetaController                   | FRR = **92%**         |
| Poor long-term memory       | Vector DB spam                   | Eval-Driven Memory (EDM) – stores only high-PEI | MRS = **0.07**        |
| Humans don’t trust output   | Tracing tools only               | HCI-EDM – full human-readable explanations    | Trust = **4.62/5.0**  |

## 500-Task Longitudinal Benchmark

- 500 real-world tasks (planning, tool-use, reasoning, alignment)  
- Fully reproducible JSON specs → [`/benchmarks/tasks/`](benchmarks/tasks/)  
- Baselines vs **AgentBench**, **WebArena**, **GAIA**  
- Automated evaluation scripts + CI validation  

→ [benchmarks/](benchmarks/)

## Human Trust Study (240 participants)

- Stratified sampling, inter-rater agreement **κ = 0.81**  
- Raw anonymized data & full statistical analysis  
→ [studies/human_eval_report.pdf](studies/human_eval_report.pdf)

## Comparison With Leading Frameworks (2025)

| Framework     | Behavioral Metrics | FRR   | Trust Score | Zero-Hallucination Control | Production Ready |
|---------------|--------------------|-------|-------------|-----------------------------|------------------|
| LangGraph     | No                 | ~75%  | ~3.9        | No (LLM-based)              | Prototyping      |
| CrewAI        | No                 | ~78%  | 4.1         | No                          | Good             |
| AutoGen       | No                 | ~72%  | 4.0         | No                          | Good             |
| **HB-Eval System** | Yes PEI/FRR/TI     | **92%** | **4.62**    | Yes Quantitative only       | **High-stakes**  |

## Quick Start (30 seconds)

```bash
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System
pip install -e .
export LLM_API_KEY=sk-...
python open_core/demo.py
