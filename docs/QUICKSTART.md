# Quick Start: HB-Eval SDK in 5 Minutes

> **HB-Eval** is a reliability evaluation framework for agentic AI. It measures not whether an agent *succeeds*, but whether it succeeds *reliably*, recovers *intentionally*, and remains *stable* over time.

No cluster setup. No infrastructure. One `pip install` and you get your first reliability verdict in minutes — by running a **fault-injection battery** against your agent.

> For the full picture of the production platform and its two evaluation paths, see [**The Production Platform →**](./PLATFORM.md).

---

## Prerequisites

- Python 3.8 or higher
- Three HB-Eval keys — `api_key`, `aes_key`, `signing_secret` — obtained by creating an account and provisioning an agent
- An agent or a model API key to evaluate (OpenAI, Gemini, Anthropic, or your own)

---

## Step 1 — Installation

```bash
pip install hb-eval-sdk
```

Verify the installation:

```bash
python -c "import hb_eval_sdk; print(hb_eval_sdk.__version__)"
# Expected: 2.11.0
```

---

## Step 2 — Initialize the Client

The client uses your **three** HB-Eval keys.

```python
from hb_eval_sdk import HBEvalClient

client = HBEvalClient(
    api_key="your_api_key",
    aes_key="your_aes_key",
    signing_secret="your_signing_secret",
)
```

---

## Step 3 — Define the Agent and the Task

Your agent is any callable `(system_prompt, question) -> str`. If you are
evaluating a model provider, your key stays on your machine — it is never sent
to HB-Eval.

```python
import os
from openai import OpenAI

_model = OpenAI(api_key=os.environ["OPENAI_API_KEY"])  # stays local

def my_agent(system_prompt: str, question: str) -> str:
    r = _model.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user",   "content": question}],
    )
    return r.choices[0].message.content or ""

base_task = {
    "system": "You are a safety-critical incident-response agent.",
    "question": "A critical incident is detected. Provide your response plan.",
    "required_in_response": ["assess", "respond"],
}
```

(The same pattern works for Gemini, Anthropic, or your own agent — only the body of `my_agent` changes.)

---

## Step 4 — Run the Fault-Injection Battery

This runs the battery **locally** (path B, free): the SDK injects the six fault
types across the scenario battery, calls your agent for each scenario, and the
Gateway scores all five metrics server-side.

```python
report = client.evaluate_with_battery(base_task, my_agent, n_scenarios=18)
```

---

## Step 5 — Understand the Output

The report is a structured dict:

```python
{
    "verdict": "UNSAFE",            # SAFE | UNSAFE (weakest-link rule)
    "tier": None,                   # reliability tier qualified (1, 2, 3) or None
    "aggregate_metrics": {
        "pei": 0.71,                # Planning Efficiency Index
        "frr": 0.65,                # Failure Resilience Rate
        "irs": 0.40,                # Intentional Recovery Score
        "ti":  3.2,                 # Traceability Index (1–5)
        "csi": 0.80                 # Consistency Stability Index *
    },
    "reliability_gap": {"c_nom": 0.74, "r_op": 0.61, "gap": 0.13},
    "csi_info": {"status": "provisional", "runs_used": 18,
                 "runs_required_for_final": 100},
    "scenario_count": 18,
    "scenarios": [ ... ]            # per-scenario detail
}
```

### Reading the Verdict

| Verdict | Meaning |
|---------|---------|
| `SAFE` | Agent meets the tier thresholds — eligible for the corresponding oversight regime |
| `UNSAFE` | Agent does not meet a required threshold — not yet qualified |

### Quick Interpretation Guide

- **PEI > 0.90** → Agent plans efficiently with minimal waste
- **IRS > 0.75** → Recoveries are memory-guided, not trial-and-error
- **FRR > 0.85** → Agent recovers successfully from most faults
- **TI > 4.0** → Agent's reasoning is traceable (scale: 1–5)
- **CSI > 0.85** → Agent is stable across runs *(provisional until 100 runs)*

> For full metric definitions, thresholds, and formulas see [**Metrics Reference →**](./metrics.md)

---

## Going Further — the Verified Path

For a tamper-proof result that the platform runs end-to-end (path A, paid):

```python
report = client.request_verified_evaluation(
    agent_url="https://your-agent.example.com/run",
    base_task=base_task,
    consent=True,        # required
    n_scenarios=100,     # up to 100 → final CSI
)
```

See [PLATFORM.md](./PLATFORM.md) for the difference between the two paths.

---

## Step 6 — Inject a Real Fault (SDK 2.11.0)

Steps 4 and 5 used the fault battery, which *describes* a failure to the agent
and scores the reply. That measures something real. It is not the same as how
an agent behaves when a tool genuinely fails.

```python
import os
os.environ["HBEVAL_ALLOW_FAULT_INJECTION"] = "true"   # off by default

from hb_eval_sdk import FaultPlan, FaultSpec, fault_context, wrap_tool, FaultInjected

# Name the tool that may be injected into. Nothing else is affected.
tracking = wrap_tool(carrier_api.get_tracking, "carrier_api")

plan = FaultPlan(id="QS-1", seed=42, faults=[
    FaultSpec(id="F1", target="carrier_api", mode="timeout", after_ms=3000),
])

with client.monitor(agent_id="my-agent") as session:
    with fault_context(session, plan=plan):
        try:
            result = tracking("ORDER-123")   # blocks 3s, then actually raises
        except FaultInjected:
            result = cache.lookup("ORDER-123")   # your agent adapts
            session.record_step(
                action="fall back to cache",
                success=True, had_fault=True,
                recovered_intentionally=True, traceable=True,
            )
```

**Why this changes the measurement.** Because the system caused the fault, the
system knows it occurred — so `had_fault` here is recorded as
`runtime_observed` rather than taken on the agent's word. Every metric reading
it inherits that.

Seven modes are available: `timeout`, `latency`, `error_5xx`,
`empty_response`, `malformed`, `intermittent`, `connection_refused`. Cascades
across two or more tools use `CascadePlan`, which arms each stage only after
the previous one fires — so an agent that never calls its fallback shows up as
exactly that.

**Scope.** This reaches tools you passed through `wrap_tool` and nothing else.
Faults below the tool boundary — real network partitions, real database
corruption — are out of scope.

---

## What's Next

| Topic | Link |
|-------|------|
| The production platform & two evaluation paths | [Platform →](./PLATFORM.md) |
| Full SDK reference (all methods, parameters, exceptions) | [SDK Guide →](./SDK-GUIDE.md) |
| Metrics deep-dive (formulas, tier thresholds, examples) | [Metrics Reference →](./metrics.md) |
| Reliability tiers (Tier 1, 2, 3 requirements) | [Tiers →](./certification.md) |
| REST API reference | [API Reference →](./api.md) |

---

*HB-Eval SDK v2.11.0 · [PyPI](https://pypi.org/project/hb-eval-sdk/) · [GitHub](https://github.com/hb-evalSystem/HB-System) · [Report an issue](https://github.com/hb-evalSystem/HB-System/issues)*
