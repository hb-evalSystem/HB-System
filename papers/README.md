
# Research Papers

This directory contains summaries and supplementary materials for the four-paper research series that forms the foundation of the HB-Eval System.

---

## 📚 Paper Series Overview

The HB-Eval framework is backed by a systematic research program addressing **Four Critical Gaps** in Agentic AI:

```
Gap 1: Evaluation        → Paper 1: HB-Eval Framework
Gap 2: Adaptation        → Paper 2: Adapt-Plan Architecture  
Gap 3: Long-Term Memory  → Paper 3: Eval-Driven Memory (EDM)
Gap 4: Trust & HCI       → Paper 4: HCI-EDM
```

---

## 📄 Paper 1: HB-Eval Framework

**Full Title**: A Methodological Analysis of Agentic AI Evaluation: The HB-Eval Framework

**Author**: A. Abuelgasim

**Status**: Ready for submission (NeurIPS/ICML 2026)

### Abstract

The rapid advancement of Agentic AI has outpaced current evaluation methodologies, which primarily focus on outcome-based metrics like Success Rate, neglecting critical aspects such as behavioral reliability, planning efficiency, and transparency. This paper introduces the Hierarchical Behavioral Evaluation Framework (HB-Eval), a novel diagnostic framework that integrates traditional performance metrics with new behavioral indicators.

### Key Contributions

1. **Novel Behavioral Metrics**:
   - **FRR (Failure Recovery Rate)**: ε_recovered / ε_total
   - **PEI (Planning Efficiency Index)**: L_min / L_actual
   - **MIR (Memory Immunization Rate)**: Resistance to memory poisoning
   - **TI (Traceability Index)**: Reasoning transparency (LLM-as-Judge)
   - **UAS (Unified Agent Score)**: Weighted holistic score

2. **Fault Injection Testbed (FIT)**: Open-source systematic testing environment

3. **Empirical Proof**: AP-EDM Agent achieves FRR=100%, PEI=0.90, outperforming ReAct and Reflexion

### Experimental Setup

- **Baselines**: ReAct-Based (A1), Reflexion-Based (A2)
- **Proposed**: AP-EDM Agent (A3)
- **Environment**: Simulated tasks with fault injection
- **Metrics**: SR, FRR, PEI, TI, MIR, UAS

### Key Results

| Agent | SR | FRR | PEI | TI | UAS |
|-------|-----|-----|-----|----|----|
| ReAct | 85% | 40% | 0.75 | 4.5 | 0.65 |
| Reflexion | 82% | 75% | 0.60 | 3.2 | 0.72 |
| **AP-EDM** | **88%** | **100%** | **0.90** | **4.8** | **0.87** |

**Validation**: UAS ranking perfectly aligns with human expert evaluation (Spearman ρ=1.00)

### Files

- `paper_1_summary.md` - Extended summary
- `paper_1_figures/` - Key figures and visualizations
- `paper_1_supplementary.pdf` - Supplementary materials (when available)

---

## 📄 Paper 2: Adapt-Plan Architecture

**Full Title**: Adapt-Plan: A Hybrid Agent Architecture for PEI-Guided Strategic Adaptation in Dynamic Environments

**Author**: A. Abuelgasim

**Status**: Ready for submission

### Abstract

Current agent architectures suffer from cognitive rigidity, limiting their ability to adapt strategically in dynamic environments. This paper introduces Adapt-Plan, a novel hybrid architecture that integrates Extended Dynamic Memory (EDM) with real-time Planning Efficiency Index (PEI) from HB-Eval as an intrinsic control signal.

### Architecture Overview

```
┌─────────────────────────────────────────┐
│         LLM Core (GPT/Claude)           │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┴─────────┐
     │                   │
┌────▼─────┐      ┌─────▼──────┐
│ HB-Eval  │      │    EDM     │
│ (PEI)    │◄────►│  Memory    │
└────┬─────┘      └─────┬──────┘
     │                  │
┌────▼──────────────────▼────┐
│   Dual Planning Unit       │
│  (Strategic + Tactical)    │
└────────────┬────────────────┘
             │
      ┌──────▼───────┐
      │ Environment  │
      │   Adapter    │
      └──────────────┘
```

### Key Innovation

**PEI-Guided Control Loop**:
- Calculate PEI at each step
- If PEI < τ (threshold = 0.70): Trigger adaptation
- Strategic vs Tactical decision based on severity

### Experimental Results

**Phase I (Efficiency & Generalization)**:

| Agent | SR | Avg PEI | Avg TI | Semantic Sim |
|-------|-----|---------|--------|--------------|
| ReAct | 88% | 0.65 | 4.2 | - |
| Reflexion | 92% | 0.75 | 4.6 | - |
| **Adapt-Plan** | **95%** | **0.91** | **4.8** | **0.93** |

**Phase II (Reliability & Recovery)**:

| Agent | SR | FRR | PEI Drop After Fault |
|-------|-----|-----|----------------------|
| ReAct | 70% | 40% | -0.35 |
| Reflexion | 85% | 65% | -0.20 |
| **Adapt-Plan** | **94%** | **78%** | **-0.05** |

### Files

- `paper_2_summary.md` - Extended summary
- `paper_2_architecture.png` - Architecture diagram
- `paper_2_results/` - Experimental results

---

## 📄 Paper 3: Eval-Driven Memory (EDM)

**Full Title**: Eval-Driven Memory (EDM): A Hybrid Memory Mechanism for Selective Storage and Reliable Retrieval in Adaptive Agents

**Author**: A. Abuelgasim

**Status**: Ready for submission

### Abstract

Agentic AI systems suffer from cumulative performance degradation due to indiscriminate storage of procedural experiences (Flat Memory Problem). This paper introduces Eval-Driven Memory (EDM), a novel hybrid long-term memory architecture that uses real-time behavioral metrics from HB-Eval—primarily the Planning Efficiency Index (PEI)—as a quality gate for selective storage and retrieval.

### EDM Four-Stage Cycle

```
1. Harvesting
   ↓ (Full trace logging)
2. Evaluation  
   ↓ (HB-Eval: PEI, FRR, TI)
3. Selective Consolidation
   ↓ (Store if PEI ≥ τ_storage = 0.78)
4. Plan-Guided Retrieval
   ↓ (Top-k high-PEI episodes)
```

### Novel Metrics Introduced

1. **MP (Memory Precision)**: % of retrieved episodes with PEI ≥ 0.8
2. **MRS (Memory Retention Stability)**: σ(PEI over last N tasks) - lower is better
3. **CER (Cognitive Efficiency Ratio)**: Steps_with_EDM / Steps_baseline - <1 is better
4. **ΔPEI∞ (Cumulative PEI Gain)**: PEI_final - PEI_initial - positive = learning

### 500-Task Longitudinal Study Results

| System | MP | MRS | CER | ΔPEI∞ | Final PEI |
|--------|-----|-----|-----|-------|-----------|
| Flat Memory | 47% | 0.24 | 1.04 | -0.19 | 0.61 |
| Recency-Only | 62% | 0.18 | 0.91 | -0.08 | 0.70 |
| Generative Agents | 69% | 0.15 | 0.87 | +0.03 | 0.79 |
| **EDM** | **88.4%** | **0.07** | **0.73** | **+0.21** | **0.92** |

**Key Finding**: EDM is the **only system** showing positive cumulative learning (ΔPEI∞ = +0.21)

### Files

- `paper_3_summary.md` - Extended summary
- `paper_3_longitudinal_data/` - 500-task study data
- `paper_3_metrics.png` - Metric definitions

---

## 📄 Paper 4: HCI-EDM (Human Trust)

**Full Title**: HCI-EDM: Enhancing Human Trust and Transparency in Adaptive Agents using Performance-Driven Memory

**Author**: A. Abuelgasim

**Status**: Ready for submission

### Abstract

Despite dramatic advances in efficiency and long-term learning, current agentic AI systems remain opaque "black boxes" to human overseers, especially during failure and recovery. This paper presents HCI-EDM, the first human-centric explainability framework that grounds all explanations in quantitative performance evidence stored in Eval-Driven Memory (EDM).

### Core Innovation

**Performance-Driven Explanations** (vs Language-Driven CoT):
- Every explanation references specific high-PEI episodes from EDM
- Quantitative evidence (PEI values, episode IDs)
- Verifiable and traceable

### Three Explanation Types

1. **Success Confirmation**: "Reusing proven plan #204 (PEI=0.98, completed in 4 steps)"
2. **Drift Correction**: "Detected PEI drift 0.91→0.63, switched to tactical path from episode #89"
3. **Recovery Narrative**: "Tool failed as in episode #156. Applied stored recovery sequence → success"

### Human Study (n=240)

**Design**:
- 240 participants (120 technical, 120 non-technical)
- 12 enterprise logistics tasks with 4 injected failures
- Randomized: CoT baseline vs HCI-EDM explanations

**Results**:

| Metric | CoT Baseline | HCI-EDM | Improvement | p-value |
|--------|-------------|---------|-------------|---------|
| Trust Score | 3.10 ± 0.81 | **4.62 ± 0.44** | +49% | <0.001 |
| Transparency (TI) | 0.45 | **0.91** | +102% | <0.001 |
| Cognitive Load (s) | 18.5 ± 4.1 | **9.2 ± 2.3** | -51% | <0.001 |
| Error Detection | 65% | **90%** | +38% | <0.001 |
| Perceived Reliability | 3.4 | **4.7** | +38% | <0.001 |

**Key Finding**: **4.62/5.0 Trust Score** is the **highest ever reported** in agentic AI user studies

### Qualitative Feedback

> "Finally I understand WHY the agent changed its plan — it showed me the exact past success."

> "The numbers (PEI values) make me trust it much more than fluffy text."

### Files

- `paper_4_summary.md` - Extended summary
- `paper_4_human_study/` - Study protocol and results
- `paper_4_questionnaires.pdf` - Study instruments

---

## 📊 Unified Framework Results

The four papers combine to form a complete trustworthy agent stack:

```
HB-Eval Framework → Metrics
       ↓
Adapt-Plan → Uses PEI for control
       ↓
EDM → Enables cumulative learning
       ↓
HCI-EDM → Grounds explanations

Result: PEI=0.92, FRR=92-100%, Trust=4.62/5.0
```

---

## 📥 Full Papers

**Status**: Manuscripts ready for submission

**Availability**:
- ArXiv pre-prints: Coming January 2026
- Conference submission: NeurIPS/ICML/ICLR 2026
- Open access: Upon acceptance

**Contact for early access**: hbevalframe@gmail.com

---

## 🎯 Target Venues

### Tier 1 (Primary Targets)
- **NeurIPS 2026** (Neural Information Processing Systems)
- **ICML 2026** (International Conference on Machine Learning)
- **ICLR 2026** (International Conference on Learning Representations)

### Tier 2 (Backup Options)
- **AAAI 2026** (Association for Advancement of Artificial Intelligence)
- **IJCAI 2026** (International Joint Conference on AI)
- **ACL 2026** (if emphasizing NLP aspects)

### Workshops (Fast Track)
- NeurIPS 2025 Workshops (December)
- ICML 2026 Workshops

---

## 📖 How to Cite

See [CITATION.bib](../CITATION.bib) for BibTeX entries.

**Main Framework**:
```bibtex
@software{hb_eval_system_2025,
  title = {{HB-Eval System: Behavioral Evaluation \& Trustworthy Agentic AI}},
  author = {Abuelgasim, A.},
  year = {2025},
  url = {https://github.com/hb-evalSystem/HB-System}
}
```

**Complete Series**:
```bibtex
@collection{abuelgasim2025series,
  title = {From Black Box to Trustworthy Agent: A Four-Paper Framework for Reliable Agentic {AI}},
  author = {Abuelgasim, A.},
  year = {2025}
}
```

---

## 🤝 Collaboration

Interested in collaborating on this research?

- **Independent Validation**: Reproduce our experiments
- **Extensions**: Apply to new domains
- **Joint Projects**: Co-author follow-up papers
- **Industry Pilots**: Test in production environments

Contact: hbevalframe@gmail.com

---

## 📂 Directory Structure

```
papers/
├── README.md                    # This file
├── paper_1_hbeval/
│   ├── summary.md
│   ├── figures/
│   └── supplementary/
├── paper_2_adaptplan/
│   ├── summary.md
│   ├── architecture.png
│   └── results/
├── paper_3_edm/
│   ├── summary.md
│   ├── longitudinal_data/
│   └── metrics.png
├── paper_4_hciedm/
│   ├── summary.md
│   ├── human_study/
│   └── questionnaires.pdf
└── unified_results/
    ├── comparison_table.md
    └── visualization/
```

---

<p align="center">
  <b>Research advancing the frontier of Trustworthy Agentic AI</b>
</p>
