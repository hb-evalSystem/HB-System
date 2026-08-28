# Reproducibility Statement
## HB-Eval — Scientific Transparency Framework

**Version:** 1.0.0 · **Author:** Abuelgasim Mohamed Ibrahim Adam  
**Last verified:** June 5, 2026 · **Statistical engine:** `core/statistics.py v1.0.0`

---

## The Honest Preamble

Reproducibility in large language model research faces a structural constraint
that does not exist in classical computer science or physics: **LLMs are
non-deterministic by design**. Running the same prompt through GPT-4o twice
produces different token sequences. This means "exact reproducibility" — where
every number matches to four decimal places — is mathematically impossible for
experiments that involve live LLM inference.

We state this clearly and upfront because scientific honesty is more valuable
than the appearance of perfect reproducibility. What we offer instead is
**stratified reproducibility**: three levels of verification, each requiring
different resources and providing different guarantees.

---

## Experimental Setup — The Actual Models and Actual Cost

**Models evaluated across three methodologies:**

| Methodology | Models | Access | Cost |
|-------------|--------|--------|------|
| A (6,000 experiments) | Llama-3.3-70B, Llama-3.1-8B, Gemma-2-9B, DeepSeek-R1-70B, Llama-3.1-70B, Mixtral-8x7B | Groq free tier | **$0.00** |
| B (4,998 experiments) | Llama-4-Maverick-17B, GPT-OSS-120B, Llama-4-Scout-17B, Qwen3-32B, Llama-3.3-70B | Groq free tier | **$0.00** |
| C (3,002 experiments) | GPT-4o, Claude 3.5 Sonnet, Gemini 2.5 Flash | OpenRouter + Google AI Studio | **~$8.30** |

**Total: 14,000 experiments · Total cost: ~$8.30 USD**

Methodologies A and B used exclusively open-weight models on Groq's free tier,
which provides sufficient capacity for the full experiment volume at zero cost.
Methodology C is the only paid component: ~$8.10 via OpenRouter for GPT-4o and
Claude 3.5 Sonnet, and ~$0.20 via Google AI Studio for Gemini 2.5 Flash with
Batch API pricing.

This cost structure is a deliberate scientific choice, not a limitation. The
fact that the nominal-operational reliability gap appears across both free and
paid models — from 7B-parameter open models to frontier commercial systems —
demonstrates that this is a structural property of current agentic paradigms,
not an artifact of model scale or cost.

For a complete step-by-step replication guide with exact commands, see
[docs/REPLICATION.md](docs/REPLICATION.md).

---

## Level 1 — Fully Deterministic Verification

**What it verifies:** The mathematical correctness of every metric formula.
Every equation in the paper (FRR, PEI, IRS, TI, CSI) is implemented in
`core/statistics.py` and covered by 45 automated tests. These tests do not
call any LLM. They feed known inputs into the metric functions and assert
known outputs.

**Resources required:** Python 3.8+, no API keys, no internet connection.  
**Setup time:** under 5 minutes.

```bash
git clone https://github.com/hb-evalSystem/HB-System.git
cd HB-System
pip install -r requirements.txt
python tests/test_suite.py
# Expected: 45 tests passed

# Also verify all paper claims offline:
python examples/replicate_paper_results.py --verify
# Expected: 10/10 claims verified in under 5 seconds
```

**Browser-based verification:** Any result from Section 5 of the paper can be
verified interactively — without installation — at the
[verification page](https://hbeval-verify-hxkrf5egzvp5qmvhs5wqcq.streamlit.app/).

---

## Level 2 — Statistical Pattern Verification

**What it verifies:** That the statistical patterns reported in the paper
emerge from the pre-collected dataset — not from selective reporting.

**Resources required:** Python 3.8+, the pre-collected results dataset
(available in [v1.0.0 release assets](https://github.com/hb-evalSystem/HB-System/releases/tag/v1.0.0)).
No API keys needed.

```bash
unzip results.zip -d data/results/
python analysis/convergence_analysis.py \
  --a data/results/methodology_a_combined_6000.json \
  --b data/results/methodology_b_4998.json \
  --c data/results/methodology_c_3002.json
# Expected: z = 0.653, p = 0.514 (convergence confirmed)
```

---

## Level 3 — Full Experimental Reproduction

**What it verifies:** That running the full experiment pipeline from scratch
produces statistical patterns consistent with those reported.

**Resources required:** Groq API key (free), OpenRouter key (~$8.10),
Google AI Studio key (~$0.20). Total: **~$8.30 USD**.

See [docs/REPLICATION.md](docs/REPLICATION.md) for the complete four-step
guide with exact commands, expected outputs, and troubleshooting notes.

**The non-determinism caveat:** Your exact numbers will differ from ours.
What should remain stable: the direction of effects (high-IRS models
outperform low-IRS models under novel faults), the existence of the gap
(Δ(π) > 0 for most models), and the relative ordering of models by tier.
Minor variance of ±2pp in aggregate metrics is expected and is not a
replication failure.

---

## The Structural Limitation We Acknowledge

The deepest reproducibility challenge we share with every empirical paper
evaluating LLMs: **we cannot guarantee that the models we tested in early 2026
will behave identically when you test them.** Providers update models
continuously. We address this by storing full experimental records with
timestamps and model identifiers, and by publishing the HB-Eval platform
so the community can continuously re-evaluate current model versions.

---

## For Journal Reviewers

If you are reviewing this paper and have questions
about reproducibility, we welcome direct correspondence. We can provide:
reviewer-only access to the full dataset in advance of publication, a live
walkthrough of the verification page, and clarification on any aspect of the
methodology.

Contact: Abuelgasim Mohamed Ibrahim Adam — abuelgasim.hbeval@outlook.com

---

*HB-Eval v1.0.0 · [Test suite](tests/test_suite.py) ·
[Replication guide](docs/REPLICATION.md) ·
[Verification page](https://hbeval-verify-hxkrf5egzvp5qmvhs5wqcq.streamlit.app/) ·
[Dataset (v1.0.0 release)](https://github.com/hb-evalSystem/HB-System/releases/tag/v1.0.0)*
