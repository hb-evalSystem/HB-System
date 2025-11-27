

# 🧠 HB-Eval System™ — Open-Core Edition
The Leading Behavioral Evaluation & Trustworthy Agentic AI Framework

This repository contains the fully functional research-grade **Open-Core** version of HB-Eval System™.

It provides core evaluation, adaptation, memory, and foundational trust-analysis modules for next-generation Agentic AI.

## ⭐ Overview

Modern Agentic AI still struggles with four core limitations. The HB-Eval System addresses these challenges directly:

| Problem Area | HB-Eval System Solution | Included in Open-Core |
| :--- | :--- | :--- |
| **Evaluation** | PEI / FRR / TI Behavioral Metrics | ✓ |
| **Adaptive Planning** | Adapt-Plan (rule-based) | ✓ |
| **Long-Term Memory** | Eval-Driven Memory (EDM) | ✓ |
| **Human-Aligned Trust (XAI)** | Explanation-Driven Memory Signals | ✓ (basic demo) |

This Open-Core edition is optimized for research, benchmarking, and reproducible experimentation.

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone [https://github.com/hb-evalSystem/HB-System.git](https://github.com/hb-evalSystem/HB-System.git)
cd HB-System
````

### 2\. Install dependencies

```bash
pip install -e .
```

### 3\. Run the demo

```bash
python open_core/demo.py
```

## 📦 Project Structure

```
open_core/
 ├── adapt_planner.py        # Adapt-Plan: deterministic adaptive planner
 ├── agent_loop.py           # Main agent inference/control loop
 ├── edm_memory.py           # Eval-Driven Memory (EDM)
 ├── external_llm_api.py     # External LLM interface (OpenAI-ready)
 ├── demo.py                 # Full system demo
papers/
 ├── research_paper_1.pdf    # (Placeholder for uploaded papers)
 └── ...
setup.py
Dockerfile
README.md
LICENSE
```

## 🧩 Core Components

### 1\. PEI / FRR Behavioral Evaluation

The system uses probabilistic-behavior models to evaluate:

  * **PEI (Performance Efficiency Index)**
  * **FRR (Failure Recovery Rate)**
  * **TI (Task Integrity)**

These three form a stable benchmark across 500+ tasks.

### 2\. Adapt-Plan Engine

A lightweight deterministic planner that:

  * decomposes goals
  * generates sub-goals
  * adapts steps from similar past experiences
  * produces new executable plans when no memory match exists

### 3\. Eval-Driven Memory (EDM)

A memory system that:

  * stores plans
  * ranks past experiences using PEI
  * retrieves the closest match to new goals
  * learns progressively with use

### 4\. Explanation Signals (XAI Foundations)

Basic signals included for research:

  * memory traces
  * decision rationales
  * scoring path per step

The Full XAI controller is not part of the Open-Core edition.

## 🛠 Example Code Snippet

```python
from open_core.edm_memory import EDM, Experience, ExperienceMetrics
from open_core.adapt_planner import AdaptPlan, Plan
from open_core.agent_loop import AgentLoop

edm = EDM()
planner = AdaptPlan()
agent = AgentLoop(edm, planner)

result = agent.run("Optimize General Operations")
```

## 🐳 Docker Support

| Command | Description |
| :--- | :--- |
| `docker build -t hb-eval-open-core .` | Build the environment. |
| `docker run --rm hb-eval-open-core` | Run the system demo. |

## 🔌 External LLM Integration (Optional)

The system includes a plug-and-play API wrapper in `open_core/external_llm_api.py`.
It supports:

  * Real OpenAI API (with configuration)
  * Local / Mock LLM mode (default)
  * Custom endpoints

## 📚 Research Papers (Open-Series 2025)

The 4-paper series evaluates:

  * Behavioral Gaps in Agentic AI
  * Adaptive Planning Under Uncertainty
  * Memory-Grounded Behavior Correction
  * Human Trust & Multi-Agent Alignment

*(Links added upon publication.)*

## 📜 License

This Open-Core version is licensed under:
**Apache License 2.0**

You may use it for:

  * research
  * academic work
  * commercial integration (open-core only)
  * derivative frameworks

Enterprise modules are not included.

## 💼 Enterprise Features (Premium-Core)

The full commercial version includes the proprietary **MetaController** (full XAI), **Advanced EDM** (Semantic Memory), and high-reliability Adaptive Planning. These features are essential for mission-critical and production environments.

**Work is currently underway to launch the commercial version. For licensing and commercial inquiries, please contact us via email or check the company website upon its launch.**

## 🤝 Contributing

We welcome:

  * bug reports
  * new planners
  * new memory algorithms
  * PEI/FRR enhancements
  * reproducibility improvements

Open an issue or submit a PR anytime.

## 🌟 Citation

If you use HB-Eval System in research:

```
@software{
  hb_eval_system_2025,
  title={HB-Eval System: Behavioral Evaluation & Trustworthy Agentic AI},
  author={Abuelgasim Adam},
  year={2025},
  url={[https://github.com/hb-evalSystem/HB-System](https://github.com/hb-evalSystem/HB-System)}
}
```

## 🔗 Repository

https://github.com/hb-evalSystem/HB-System

```
```
