# 🧠 HB-Eval System™ — Open-Core Edition

**The Leading Behavioral Evaluation & Trustworthy Agentic AI Framework**

<p align="center">
  <img src="https://img.shields.io/badge/PEI-0.92-8A2BE2?style=for-the-badge" alt="PEI Score" />
  <img src="https://img.shields.io/badge/FRR-92%25-32CD32?style=for-the-badge" alt="FRR Score" />
  <img src="https://img.shields.io/badge/Human%20Trust-4.62%2F5.0-1E90FF?style=for-the-badge" alt="Trust Score" />
  <img src="https://img.shields.io/badge/Benchmark-500%20Tasks-orange?style=for-the-badge" alt="Benchmark" />
  <img src="https://img.shields.io/badge/Series-4%20Papers-red?style=for-the-badge" alt="Papers" />
  <img src="https://img.shields.io/badge/License-Apache%202.0-green?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge" alt="Python Version" />
</p>

---

## 📖 Overview

**HB-Eval System** is a research-grade framework for **behavioral evaluation** and **trustworthy agentic AI**. This Open-Core edition provides the essential components for evaluating, planning, and executing AI agent behaviors with measurable performance metrics.

### 🎯 Key Capabilities

| Component | Description | Status |
|-----------|-------------|--------|
| **PEI/FRR/TI Metrics** | Behavioral performance evaluation | ✅ Open-Core |
| **Adaptive Planning** | Rule-based deterministic planner | ✅ Open-Core |
| **Eval-Driven Memory (EDM)** | Experience-based plan retrieval | ✅ Open-Core |
| **LLM Integration** | Pluggable external LLM support | ✅ Open-Core |
| **Agent Loop** | Step-by-step execution with recovery | ✅ Open-Core |
| **MetaController (XAI)** | Advanced explainability layer | 🔒 Commercial |
| **Semantic EDM** | Embedding-based memory | 🔒 Commercial |

### 🚨 Important Note on Metrics

The performance metrics shown in badges (PEI=0.92, FRR=92%, Trust=4.62/5.0) are results from **internal testing**. This Open-Core release is designed to facilitate **independent verification** and **external benchmarking** by the research community.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System

# Install dependencies
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

### Basic Usage

```python
from hb_eval import EDM, AdaptPlan, AgentLoop

# Initialize components
edm = EDM()
planner = AdaptPlan()
agent = AgentLoop(edm, planner)

# Execute a goal
result = agent.run("Optimize system performance")
print(result)
```

### Run the Demo

```bash
# Interactive demo with examples
python -m hb_eval.demo

# Or run directly
python hb_eval/demo.py
```

---

## 📦 Project Structure

```
HB-System/
├── hb_eval/                    # Main package
│   ├── __init__.py            # Package exports
│   ├── core/                  # Core modules
│   │   ├── edm_memory.py      # Eval-Driven Memory
│   │   ├── adapt_planner.py   # Adaptive Planner
│   │   ├── agent_loop.py      # Agent Execution Loop
│   │   └── external_llm_api.py # LLM API wrapper
│   ├── utils/                 # Utilities
│   └── demo.py                # Interactive demo
├── tests/                     # Test suite
├── papers/                    # Research papers (4-paper series)
├── tasks/                     # Task definitions (500+ tasks)
├── .github/workflows/         # CI/CD automation
├── docs/                      # Documentation
├── examples/                  # Usage examples
├── setup.py                   # Setup script
├── pyproject.toml             # Modern Python config
├── requirements.txt           # Dependencies
├── Dockerfile                 # Container image
├── README.md                  # This file
└── LICENSE                    # Apache 2.0 License
```

---

## 🧩 Core Components

### 1. Eval-Driven Memory (EDM)

EDM stores and retrieves past planning experiences based on similarity and performance:

```python
from hb_eval import EDM, Experience, ExperienceMetrics, Plan

# Initialize EDM
edm = EDM(storage_threshold=0.75, retrieval_threshold=0.40)

# Create and store an experience
plan = Plan(goal="Optimize workflow", sub_goals=["Step 1", "Step 2"])
exp = Experience(plan=plan, metrics=ExperienceMetrics(pei=0.85))
edm.store(exp)

# Retrieve similar experience
retrieved = edm.retrieve_procedural_guide("Optimize processes")
```

**Key Features:**
- Jaccard similarity matching
- PEI-based quality filtering
- Memory size management
- Top-N retrieval by performance

### 2. Adaptive Planner

Generates procedural plans through retrieval or template-based generation:

```python
from hb_eval import AdaptPlan, EDM

planner = AdaptPlan(enable_verbose=True)
edm = EDM()

# Generate plan (retrieves from memory if available)
plan = planner.generate_plan("Improve efficiency", edm)

# Force new plan generation
new_plan = planner.generate_plan("New goal", edm, force_new=True)

# Recovery replanning
recovery_plan = planner.replan(failed_plan, edm, failure_point=2)
```

**Planning Strategies:**
- Memory-based retrieval
- Template-based generation
- Adaptive replanning
- Failure recovery

### 3. Agent Execution Loop

Step-by-step plan execution with metrics tracking:

```python
from hb_eval import AgentLoop, EDM, AdaptPlan

edm = EDM()
planner = AdaptPlan()
agent = AgentLoop(
    edm, 
    planner, 
    max_recovery_attempts=3,
    enable_verbose=True
)

# Execute with automatic experience storage
result = agent.run("Complete task", store_experience=True)
```

**Features:**
- Step-by-step execution
- Real-time metrics (PEI, FRR, TI)
- Automatic failure recovery
- Experience storage
- Execution callbacks

### 4. LLM Integration

Flexible LLM API integration with multiple providers:

```python
from hb_eval.core.external_llm_api import (
    LLMConfig, LLMProvider, set_global_config, llm_call
)

# Configure for OpenAI
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    api_key="your-key",
    model="gpt-3.5-turbo",
    temperature=0.7
)
set_global_config(config)

# Make calls
response = llm_call("Your prompt here")

# Mock mode for testing
mock_config = LLMConfig(provider=LLMProvider.MOCK)
set_global_config(mock_config)
```

**Supported Modes:**
- OpenAI API
- Mock mode (testing)
- Custom endpoints
- Automatic retry logic
- Error handling

---

## 🐳 Docker Support

### Build Image

```bash
docker build -t hb-eval-system:latest .
```

### Run Demo

```bash
docker run --rm hb-eval-system:latest
```

### Interactive Mode

```bash
docker run --rm -it hb-eval-system:latest python -m hb_eval.demo
```

### With API Key

```bash
docker run --rm -e LLM_API_KEY="your-key" hb-eval-system:latest
```

---

## 📊 Performance Metrics

### PEI (Performance Efficiency Index)

Measures overall execution efficiency:
- **Formula**: `completion_rate - failure_penalty - recovery_penalty`
- **Range**: 0.0 to 1.0
- **Threshold**: ≥0.75 for storage

### FRR (Failure Recovery Rate)

Measures resilience and recovery capability:
- **Calculation**: Success rate after failures
- **Range**: 0.0 to 1.0 (or 0% to 100%)
- **Target**: ≥90% for production systems

### TI (Task Integrity)

Measures correctness and goal alignment:
- **Evaluation**: Goal achievement verification
- **Range**: 0.0 to 1.0
- **Minimum**: ≥0.80 for acceptable results

---

## 🧪 Testing & Development

### Run Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=hb_eval --cov-report=html
```

### Code Quality

```bash
# Format code
black hb_eval/

# Sort imports
isort hb_eval/

# Type checking
mypy hb_eval/

# Linting
flake8 hb_eval/
```

---

## 📚 Research Papers

The **HB-Eval System** is backed by a 4-paper research series (2025):

1. **Paper 1**: Behavioral Gaps in Current Agentic AI Systems
2. **Paper 2**: Adaptive Planning Under Uncertainty
3. **Paper 3**: Memory-Grounded Behavior Correction
4. **Paper 4**: Human Trust & Multi-Agent Alignment

> 📄 Upon official publication, all papers will include detailed experimental protocols, complete task datasets, and human subject descriptions for full reproducibility.

**Current Status**: Papers in preparation for submission to top-tier AI conferences.

---

## 📖 Documentation

### API Reference

Full API documentation is available in the `docs/` directory:
- Core modules documentation
- Usage examples
- Best practices
- Troubleshooting guide

### Examples

Check the `examples/` directory for:
- Basic usage patterns
- Advanced configurations
- Integration examples
- Custom extensions

---

## 🤝 Contributing

We welcome contributions from the research community!

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas of Interest

- 🐛 Bug fixes and issue reports
- 📈 Performance improvements
- 🧪 New evaluation metrics
- 🔧 Additional planning algorithms
- 📊 Benchmark validations
- 📝 Documentation improvements
- 🎨 UI/UX enhancements

---

## 💼 Commercial Version

The **HB-Eval System Premium-Core** includes:

| Feature | Open-Core | Premium-Core |
|---------|-----------|--------------|
| PEI/FRR/TI Evaluation | ✅ | ✅ |
| Basic EDM | ✅ | ✅ |
| Adaptive Planning | ✅ | ✅ |
| LLM Integration | ✅ | ✅ |
| **MetaController (XAI)** | ❌ | ✅ |
| **Semantic EDM** | ❌ | ✅ |
| **Real-time Monitoring** | ❌ | ✅ |
| **Multi-Agent Coordination** | ❌ | ✅ |
| **Enterprise Support** | ❌ | ✅ |

**🚧 Commercial Launch Status**: Currently under development. For licensing inquiries, please contact us via email or check the company website upon launch.

---

## 📜 License

This Open-Core version is licensed under **Apache License 2.0**.

### You may:
- ✅ Use for research and academic work
- ✅ Use for commercial integration (Open-Core components only)
- ✅ Modify and create derivative works
- ✅ Distribute and sublicense

### You must:
- 📋 Include the original license and copyright notice
- 📋 State any significant changes made
- 📋 Include a copy of the Apache 2.0 license

### Commercial Use

**Enterprise features** (MetaController, Advanced EDM, Real-time Evaluation) require a separate commercial license. See `COMMERCIAL_LICENSE.md` for details.

---

## 🌟 Citation

If you use HB-Eval System in your research, please cite:

```bibtex
@software{hb_eval_system_2025,
  title={HB-Eval System: Behavioral Evaluation \& Trustworthy Agentic AI},
  author={Abuelgasim Mohamed Ibrahim Adam},
  year={2025},
  url={https://github.com/hb-evalSystem/HB-System},
  version={1.0.0},
  license={Apache-2.0}
}
```

---

## 📧 Contact & Support

- **Email**: hbevalframe@gmail.com
- **GitHub Issues**: [Report bugs or request features](https://github.com/hb-evalSystem/HB-System/issues)
- **Discussions**: [Community discussions](https://github.com/hb-evalSystem/HB-System/discussions)

---

## 🙏 Acknowledgments

Special thanks to the research community for valuable feedback and to all contributors who help improve this framework.

---

## 🔗 Links

- 🌐 **Repository**: https://github.com/hb-evalSystem/HB-System
- 📚 **Documentation**: Coming soon
- 🏢 **Company Website**: Under development
- 📄 **Research Papers**: To be published in 2025

---

<p align="center">
  <b>Made with ❤️ for the AI Research Community</b>
</p>

<p align="center">
  <i>© 2025 Abuelgasim Mohamed Ibrahim Adam. All rights reserved.</i>
</p>
