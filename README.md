# 🧠 HB-Eval System™ — Open-Core Edition

**The First Comprehensive Behavioral Evaluation Framework for Agentic AI**
<div align="center">
  <img src="assets/hb-eval-logo.png" alt="HB-Eval Logo" width="500"/>
  
  <h1>HB-Eval: Hybrid Behavioral Evaluation Framework</h1>
  
  <p><strong>A comprehensive evaluation framework for embodied AI agents</strong></p>

  [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
  [![arXiv](https://img.shields.io/badge/arXiv-Coming%20Soon-b31b1b.svg)](#research)

</div>

---

## 🎯 What is HB-Eval System?

**HB-Eval System** is the **first comprehensive behavioral evaluation framework** for Agentic AI, addressing critical gaps in reliability, transparency, and trustworthiness through a **4-paper research series** and novel evaluation metrics.

### 🌟 Core Innovation

Unlike outcome-focused benchmarks (AgentBench, GAIA), HB-Eval introduces **9 novel process-based behavioral metrics**:

| Metric | Measures | Paper | Typical Value |
|--------|----------|-------|---------------|
| **FRR** | Failure Recovery Rate | Paper 1 | 92-100% |
| **PEI** | Planning Efficiency Index | Papers 1,2,3 | 0.90-0.92 |
| **TI** | Traceability Index (Transparency) | Papers 1,4 | 4.5-4.8/5.0 |
| **MIR** | Memory Immunization Rate | Paper 1 | 85-90% |
| **MP** | Memory Precision | Paper 3 | 88.4% |
| **MRS** | Memory Retention Stability | Paper 3 | 0.07 |
| **CER** | Cognitive Efficiency Ratio | Paper 3 | 0.73 |
| **ΔPEI∞** | Cumulative Learning | Paper 3 | +0.21 |
| **UAS** | Unified Agent Score | Paper 1 | 0.87 |

### 🏆 Research Validation

- **4-Paper Series**: Comprehensive coverage from evaluation to human trust
- **500-Task Longitudinal Study**: First system showing positive cumulative learning (ΔPEI∞ = +0.21)
- **Human Study (n=240)**: Trust Score = **4.62/5.0** — **highest ever reported** in agentic AI
- **AP-EDM Agent**: Achieves **FRR=100%**, **PEI=0.92**, surpassing ReAct & Reflexion

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System

# Install (choose one method)
pip install -e .                    # Editable install
pip install -r requirements.txt     # Requirements only
```

### Basic Usage (3 Lines!)

```python
from hb_eval import EDM, AdaptPlan, AgentLoop

agent = AgentLoop(EDM(), AdaptPlan())
result = agent.run("Optimize system performance")
print(f"PEI: {result.metrics.pei:.2f}")  # e.g., PEI: 0.92
```

### Run Interactive Demo

```bash
python -m hb_eval.demo
# or
python hb_eval/demo.py
```

---

## 📊 Why HB-Eval? (Comparison)

### vs Traditional Benchmarks

| Framework | Focus | Metrics | HB-Eval Integration |
|-----------|-------|---------|---------------------|
| **AgentBench** | Task completion | Success Rate | ✅ Add behavioral depth |
| **GAIA** | Multi-modal tasks | Accuracy | ✅ Measure reliability |
| **AutoGenBench** | AutoGen agents | Speed, Cost | ✅ Evaluate planning |
| **HB-Eval** | **Behavioral reliability** | **9 novel metrics** | — Native framework |

### vs Agent Building Frameworks

| Framework | Type | Purpose | Relationship to HB-Eval |
|-----------|------|---------|-------------------------|
| **LangChain** | Builder | Construct agents | ✅ **Build** with LangChain → **Evaluate** with HB-Eval |
| **AutoGen** | Orchestrator | Multi-agent systems | ✅ **Orchestrate** with AutoGen → **Validate** with HB-Eval |
| **CrewAI** | Coordinator | Team collaboration | ✅ **Coordinate** with CrewAI → **Monitor** with HB-Eval |

**Use Case Flow**: `Build Agent (LangChain) → Evaluate (HB-Eval) → Deploy with Confidence`

---

## 📚 Research Foundation

### Four-Paper Research Series

This framework is backed by comprehensive research addressing **Four Critical Gaps**:

```
Gap 1: Evaluation Crisis
    ↓ Paper 1: HB-Eval Framework
Gap 2: Adaptation & Reasoning  
    ↓ Paper 2: Adapt-Plan Architecture
Gap 3: Long-Term Memory
    ↓ Paper 3: Eval-Driven Memory (EDM)
Gap 4: Trust & Transparency
    ↓ Paper 4: HCI-EDM (Human Trust)
```

### Key Results (From Papers)

#### Paper 1: Evaluation Framework

| Agent | SR | FRR | PEI | TI | UAS |
|-------|-----|-----|-----|----|----|
| ReAct | 85% | 40% | 0.75 | 4.5 | 0.65 |
| Reflexion | 82% | 75% | 0.60 | 3.2 | 0.72 |
| **AP-EDM** | **88%** | **100%** | **0.90** | **4.8** | **0.87** |

**Key Finding**: UAS ranking aligns perfectly with human evaluation (Spearman ρ=1.00)

#### Paper 3: Memory System (500-Task Study)

| System | MP | MRS | CER | ΔPEI∞ | Final PEI |
|--------|-----|-----|-----|-------|-----------|
| Flat Memory | 47% | 0.24 | 1.04 | **-0.19** ❌ | 0.61 |
| Recency-Only | 62% | 0.18 | 0.91 | **-0.08** ❌ | 0.70 |
| Generative Agents | 69% | 0.15 | 0.87 | +0.03 | 0.79 |
| **EDM** | **88.4%** | **0.07** | **0.73** | **+0.21** ✅ | **0.92** |

**Key Finding**: EDM is the **only system** showing positive cumulative learning

#### Paper 4: Human Trust Study (n=240)

| Metric | CoT Baseline | HCI-EDM | Improvement |
|--------|-------------|---------|-------------|
| Trust Score | 3.10 | **4.62** | **+49%** |
| Transparency | 0.45 | **0.91** | **+102%** |
| Cognitive Load | 18.5s | **9.2s** | **-51%** |
| Error Detection | 65% | **90%** | **+38%** |

**Key Finding**: 4.62/5.0 is the **highest trust score ever reported** in agentic AI

📄 **Full Research Documentation**: See [RESEARCH.md](RESEARCH.md)

---

## 🧩 Core Components

### 1. Eval-Driven Memory (EDM)

```python
from hb_eval import EDM, Experience, ExperienceMetrics, Plan

# Initialize with quality threshold
edm = EDM(storage_threshold=0.78)

# Store high-quality experience
plan = Plan(goal="Optimize", sub_goals=["Analyze", "Execute"])
exp = Experience(plan=plan, metrics=ExperienceMetrics(pei=0.92))
edm.store(exp)  # Stores only if PEI ≥ 0.78

# Retrieve similar experience
retrieved = edm.retrieve_procedural_guide("Optimize system")
```

**Features**: Selective consolidation • Semantic retrieval • Performance metadata • Cumulative learning

### 2. Adaptive Planner (Adapt-Plan)

```python
from hb_eval import AdaptPlan

planner = AdaptPlan(enable_verbose=True)

# Generate plan (retrieves from memory if available)
plan = planner.generate_plan("Deploy new feature", edm)

# PEI-guided control: adapts if PEI < 0.70
# Strategic replanning vs Tactical adaptation
```

**Features**: PEI-guided control • Dual planning • Semantic generalization • Fault recovery

### 3. Agent Execution Loop

```python
from hb_eval import AgentLoop

agent = AgentLoop(
    edm=edm,
    planner=planner,
    max_recovery_attempts=3,
    enable_verbose=True
)

# Execute with automatic metrics
result = agent.run("Complex task", store_experience=True)

# Access metrics
print(f"Steps: {len(result.plan.steps_taken)}")
print(f"PEI: {result.metrics.pei:.2f}")
print(f"Status: {result.status}")
```

**Features**: Step-by-step execution • Real-time PEI • Automatic recovery • Experience storage

### 4. LLM Integration

```python
from hb_eval.core.external_llm_api import LLMConfig, LLMProvider, set_global_config

# OpenAI
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    api_key="your-key",
    model="gpt-4"
)
set_global_config(config)

# Mock mode (testing)
mock_config = LLMConfig(provider=LLMProvider.MOCK)
set_global_config(mock_config)
```

**Supported**: OpenAI • Mock mode • Custom endpoints • Retry logic

---

## 📦 Project Structure

```
HB-System/
├── hb_eval/              # Main package ⭐
│   ├── core/            # Core modules (EDM, Adapt-Plan, Agent Loop)
│   ├── utils/           # Utilities
│   └── demo.py          # Interactive demo
├── tests/               # Test suite (>80% coverage)
├── examples/            # Usage examples
├── papers/              # Research papers summaries 📄
├── docs/                # Documentation
│   └── metrics.md       # Complete metrics guide
├── benchmarks/          # Benchmarking suite 🧪
│   ├── datasets/        # 500-task benchmark
│   ├── baselines/       # Reference implementations
│   └── fit/             # Fault Injection Testbed
├── tasks/               # Task definitions
├── RESEARCH.md          # Research summary
├── ROADMAP.md           # Development roadmap
├── CITATION.bib         # Citation file
├── CHANGELOG.md         # Version history
└── README.md            # This file
```

---

## 🐳 Docker Support

```bash
# Build
docker build -t hb-eval-system:latest .

# Run demo
docker run --rm hb-eval-system:latest

# Interactive mode
docker run --rm -it hb-eval-system:latest python -m hb_eval.demo

# With API key
docker run --rm -e LLM_API_KEY="your-key" hb-eval-system:latest
```

**Image**: Multi-stage build • Non-root user • Health checks • ~85MB

---

## 🧪 Testing & Benchmarking

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=hb_eval --cov-report=html

# Specific module
pytest tests/test_core.py -v
```

### Run Benchmarks

```bash
# Quick benchmark (50 tasks)
python benchmarks/quick_benchmark.py --agent your_agent

# Full benchmark (500 tasks)
python benchmarks/run_benchmark.py --dataset core_500

# Compare with baselines
python benchmarks/compare_agents.py --agents react reflexion your_agent
```

📊 **Benchmarking Guide**: See [benchmarks/README.md](benchmarks/README.md)

---

## 📈 Metrics Reference

### Core Behavioral Metrics

| Metric | Formula | Range | Ideal | Use Case |
|--------|---------|-------|-------|----------|
| **FRR** | ε_recovered / ε_total | 0-100% | ≥80% | Reliability |
| **PEI** | L_min / L_actual | 0.0-1.0 | ≥0.80 | Efficiency |
| **TI** | Avg(Judge scores) | 1.0-5.0 | ≥4.0 | Transparency |
| **MIR** | Correct / Total queries | 0.0-1.0 | ≥0.85 | Security |

### Memory Metrics (Paper 3)

| Metric | Measures | Lower/Higher Better |
|--------|----------|---------------------|
| **MP** | Quality of retrieval | Higher (88.4%) |
| **MRS** | Performance stability | Lower (0.07) |
| **CER** | Reasoning efficiency | Lower (<1.0) |
| **ΔPEI∞** | Cumulative learning | Higher (+0.21) |

📖 **Complete Guide**: See [docs/metrics.md](docs/metrics.md)

---

## 🎓 Citation

If you use HB-Eval System in your research:

```bibtex
@software{hb_eval_system_2025,
  title = {{HB-Eval System: Behavioral Evaluation \& Trustworthy Agentic AI}},
  author = {Abuelgasim, A.},
  year = {2025},
  version = {1.0.0-alpha},
  url = {https://github.com/hb-evalSystem/HB-System},
  license = {Apache-2.0}
}
```

**Full Citations**: See [CITATION.bib](CITATION.bib)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas of Interest

- 🐛 Bug reports & fixes
- 📊 Independent benchmark validation
- 🔌 New LLM provider integrations
- 📝 Documentation improvements
- 🧪 New evaluation metrics
- 💡 Feature suggestions

**Special Call**: We encourage **independent validation** of our reported metrics!

---

## 🗺️ Roadmap

### Phase 1 (0-6 months) - Current

- ✅ Open-source launch
- 🔄 Documentation site
- 🔄 ArXiv pre-prints (Jan 2026)
- 🔄 Conference submissions
- 🎯 500+ GitHub stars
- 🎯 10+ contributors

### Phase 2 (6-12 months)

- 📊 Public benchmark dataset
- 🏆 Online leaderboard
- 🤝 Academic partnerships
- 💼 Industry pilots
- 🌐 Community growth

📅 **Full Roadmap**: See [ROADMAP.md](ROADMAP.md)

---

## 📜 License

**Open-Core**: Apache License 2.0

### You May:
- ✅ Use for research & academic work
- ✅ Use for commercial applications (open-core components)
- ✅ Modify and create derivatives
- ✅ Distribute and sublicense

### You Must:
- 📋 Include original license notice
- 📋 State significant changes
- 📋 Include copy of Apache 2.0 license

### Commercial License

**Enterprise features** (MetaController, Advanced EDM) require separate commercial license.

📄 See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for details.

---

## 📞 Contact & Support

### General
- **Email**: hbevalframe@gmail.com
- **GitHub Issues**: [Report bugs](https://github.com/hb-evalSystem/HB-System/issues)
- **Discussions**: [Ask questions](https://github.com/hb-evalSystem/HB-System/discussions)

### Research Collaboration
- Independent validation
- Joint projects
- Academic partnerships
- Industry pilots

### Commercial
- Enterprise features
- Custom evaluation frameworks
- Training & consulting

**Response Time**: Usually within 48 hours

---

## 🌟 Acknowledgments

### Research Inspiration
- ReAct (Yao et al., 2022)
- Reflexion (Shinn et al., 2023)
- Generative Agents (Park et al., 2023)

### Community
- Open-source AI community
- Early testers and contributors
- Academic researchers providing feedback

---

## 📊 Project Status

| Aspect | Status | Notes |
|--------|--------|-------|
| **Code** | ✅ Stable | v1.0.0-alpha released |
| **Research** | 🔄 Under Review | Papers submitted Q1 2026 |
| **Documentation** | ✅ Complete | Comprehensive guides |
| **Testing** | ✅ >80% Coverage | CI/CD automated |
| **Benchmarks** | 🔄 In Progress | Public release Q1 2026 |
| **Community** | 🌱 Growing | Just launched |

---

## 🔗 Links

- 🏠 **Homepage**: https://github.com/hb-evalSystem/HB-System
- 📚 **Documentation**: [README](README.md) • [Research](RESEARCH.md) • [Metrics](docs/metrics.md)
- 🗺️ **Roadmap**: [ROADMAP.md](ROADMAP.md)
- 📄 **Papers**: [papers/README.md](papers/README.md)
- 🧪 **Benchmarks**: [benchmarks/README.md](benchmarks/README.md)
- 📖 **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

## 🎯 Why Choose HB-Eval?

✅ **First of its kind** - Only comprehensive behavioral evaluation framework  
✅ **Research-backed** - 4-paper series with empirical validation  
✅ **Proven results** - Highest human trust score (4.62/5.0) ever reported  
✅ **Production-ready** - Clean code, tests, CI/CD  
✅ **Well-documented** - Extensive guides and examples  
✅ **Open & extensible** - Apache 2.0, community-driven  
✅ **Actively maintained** - Regular updates and support  

---

<p align="center">
  <b>🚀 Start evaluating trustworthy agents today!</b><br>
  <code>pip install -e .</code> · <code>python -m hb_eval.demo</code>
</p>

<p align="center">
  <i>Built with ❤️ for the AI Research Community</i><br>
  <i>© 2025 Abuelgasim Mohamed Ibrahim Adam. All rights reserved.</i>
</p>

---

**⭐ If you find this useful, please star the repository!**
