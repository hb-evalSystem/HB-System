# 🧠 HB-Eval System™ — Open-Core Edition

**The Leading Behavioral Evaluation & Trustworthy Agentic AI Framework**

<p align="center">
  <img src="https://img.shields.io/badge/PEI-0.92-8A2BE2?style=for-the-badge" />
  <img src="https://img.shields.io/badge/FRR-92%25-32CD32?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Human%20Trust-4.62%2F5.0-1E90FF?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Benchmark-500%20Tasks-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Papers-4%20Series-red?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge" />
</p>

> This repository contains the **fully functional research-grade Open-Core version** of HB-Eval System™.
> It provides: evaluation, adaptation, memory, and trust-analysis modules for next-generation Agentic AI.

---

## ⭐ Overview

Modern Agentic AI still struggles with four core limitations:

| Problem Area              | HB-Eval System Solution           | Included in Open-Core |
| ------------------------- | --------------------------------- | --------------------- |
| Evaluation                | PEI / FRR / TI Behavioral Metrics | ✓                     |
| Adaptive Planning         | Adapt-Plan (rule-based)           | ✓                     |
| Long-Term Memory          | Eval-Driven Memory (EDM)          | ✓                     |
| Human-Aligned Trust (XAI) | Explanation-Driven Memory Signals | ✓ (basic demo)        |

This Open-Core edition is optimized for **research, benchmarking, and reproducible experimentation**.

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Run the demo

```bash
python open_core/demo.py
```

---

## 📦 Project Structure

```
open_core/
 ├── adapt_planner.py        # Adapt-Plan: deterministic adaptive planner
 ├── agent_loop.py           # Main agent inference/control loop
 ├── edm_memory.py           # Eval-Driven Memory (EDM)
 ├── external_llm_api.py     # External LLM interface (OpenAI-ready)
 ├── demo.py                 # Full system demo
setup.py
Dockerfile
README.md
```

---

## 🧩 Core Components

### 1. **PEI / FRR Behavioral Evaluation**

The system uses probabilistic-behavior models to evaluate:

* **PEI**: Performance Efficiency Index
* **FRR**: Failure Recovery Rate
* **TI**: Task Integrity

These three form a stable benchmark across 500+ tasks.

---

### 2. **Adapt-Plan Engine**

A lightweight deterministic planner that:

* decomposes goals
* generates sub-goals
* adapts steps from similar past experiences
* produces new executable plans when no memory match exists

---

### 3. **Eval-Driven Memory (EDM)**

A memory system that:

* stores plans
* ranks past experiences using PEI
* retrieves the closest match to new goals
* learns progressively with use

---

### 4. **Explanation Signals (XAI Foundations)**

Basic signals included for research:

* memory traces
* decision rationales
* scoring path per step

Full XAI controller is not part of the Open-Core edition.

---

## 🛠 Example Code Snippet

```python
from edm_memory import EDM, Experience, ExperienceMetrics
from adapt_planner import AdaptPlan, Plan
from agent_loop import AgentLoop

edm = EDM()
planner = AdaptPlan()
agent = AgentLoop(edm, planner)

result = agent.run("Optimize General Operations")
```

---

## 🐳 Docker Support

Build:

```bash
docker build -t hb-eval-open-core .
```

Run:

```bash
docker run --rm hb-eval-open-core
```

---

## 🔌 External LLM Integration (Optional)

The system includes a plug-and-play API wrapper:

```
open_core/external_llm_api.py
```

Supports:

* Real OpenAI API
* Local / Mock LLM mode
* Custom endpoints

---

## 📚 Research Papers (Open-Series 2025)

The 4-paper series evaluates:

1. Behavioral Gaps in Agentic AI
2. Adaptive Planning Under Uncertainty
3. Memory-Grounded Behavior Correction
4. Human Trust & Multi-Agent Alignment

(Links added upon publication.)

---

## 📜 License

This Open-Core version is licensed under:

**Apache License 2.0**

You may use it for:

* research
* academic work
* commercial integration (open-core only)
* derivative frameworks

Enterprise modules are not included.

---

## 🤝 Contributing

We welcome:

* bug reports
* new planners
* new memory algorithms
* PEI/FRR enhancements
* reproducibility improvements

Open an issue or submit a PR anytime.

---

## 🌟 Citation

If you use HB-Eval System in research:

```
@software{
  hb_eval_system_2025,
  title={HB-Eval System: Behavioral Evaluation & Trustworthy Agentic AI},
  author={Abuelgasim Adam},
  year={2025},
  url={https://github.com/hb-evalSystem/HB-System}
}
```

---

## 🔗 Repository

[https://github.com/hb-evalSystem/HB-System](https://github.com/hb-evalSystem/HB-System)
