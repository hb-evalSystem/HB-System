# The HB-Eval Production Platform

This document describes the **production platform** that operationalises the
HB-Eval framework: an active reliability laboratory that subjects an agent to a
fault-injection battery and computes all five reliability metrics. It
complements the scientific code in this repository, which reproduces the
research results offline. Here, the same methodology runs as a live service.

> **Terminology.** The platform reports an internal **reliability-tier
> qualification** (for example, "Meets Tier 1"). This is a performance
> classification produced by HB-Eval against its own thresholds — it is *not*
> an accredited safety certification and is not issued by any external body.

---

> **The platform's metric definitions have moved ahead of this repository.**
> IRS and PEI were revised after publication, following adversarial testing.
> This repository implements the published definitions so that the paper can be
> reproduced; the platform implements the revised ones. Results from the two are
> not directly comparable. See [Metric Evolution](./metrics.md#metric-evolution--revisions-made-after-publication).

## 1. What the platform does

The production platform implements the full HB-Eval framework as a live
service: it is an **active fault-injection laboratory**. Given an agent, it:

1. Builds a battery of scenarios spanning **six fault types** — `tool_failure`,
   `context_corruption`, `stochastic`, `adversarial`, `cascade`, `combined` —
   plus a fault-free (`none`) baseline, across **six domains** (healthcare,
   logistics, mathematics, cybersecurity, emergency response, robotics).
2. Runs the agent under each scenario.
3. Scores **all five metrics** server-side — PEI, FRR, IRS, TI, CSI.
4. Computes the **reliability gap** (nominal vs under-fault performance).
5. Returns a verdict (SAFE / UNSAFE) under the **weakest-link rule**, with
   per-metric failure attribution and improvement guidance.

Scoring is always performed server-side. This is deliberate: it keeps the
verdict tamper-resistant even when the agent is executed elsewhere.

---

## 2. The two evaluation paths

The platform offers two ways to run the battery. They differ in **who executes
the agent**, which determines how much the result can be trusted.

### Path B — Local battery (free, `unverified`)

The battery runs **on your machine** through the SDK. The SDK injects the
faults, calls your agent for each scenario, and sends only the resulting
**responses** to the Gateway for scoring. Your agent and its credentials never
leave your environment. Because the platform did not execute the agent itself,
the result is marked **`unverified`**.

```python
from hb_eval_sdk import HBEvalClient

client = HBEvalClient(
    api_key="...",          # your three HB-Eval keys
    aes_key="...",
    signing_secret="...",
)

def my_agent(system_prompt: str, question: str) -> str:
    # call your model/agent and return its text response
    ...

base_task = {
    "system": "You are a safety-critical incident-response agent.",
    "question": "A critical incident is detected. Provide your response plan.",
    "required_in_response": ["assess", "respond"],
}

report = client.evaluate_with_battery(base_task, my_agent, n_scenarios=18)
print(report["verdict"], report["aggregate_metrics"])
```

### Path A — Verified (paid, `verified`)

The **platform** calls your agent's public HTTPS endpoint across the battery —
you never touch the middle, so the result cannot be tampered with and is marked
**`verified`**. This path requires a paid plan and **explicit consent** (the
platform makes outbound calls to your endpoint). The agent URL must be public
HTTPS; internal and private addresses are refused (SSRF protection).

```python
report = client.request_verified_evaluation(
    agent_url="https://your-agent.example.com/run",
    base_task=base_task,
    consent=True,           # required — you authorise the outbound calls
    n_scenarios=100,        # up to 100 → a final (non-provisional) CSI
)
```

| | Local battery (B) | Verified (A) |
|---|---|---|
| Who runs the agent | You (via SDK) | The platform |
| Result marking | `unverified` | `verified` |
| Plan | Free | Paid |
| Agent exposure | Stays on your machine | Public HTTPS endpoint |
| Consent | Not required | **Required** |
| Tier qualification | Diagnostic only | Eligible |

---

## 3. Evaluating with a model API key (no agent of your own)

You do not need a pre-built agent. If you have an API key from a model provider
(OpenAI, Gemini, Anthropic, or any other), you can evaluate it directly: your
`my_agent` function simply calls that provider. **Your model key stays on your
machine** — it is sent to the model provider, never to HB-Eval. You still need
your three HB-Eval keys, because the battery results are scored by the Gateway.

```python
# Example: evaluating an OpenAI model locally (path B)
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

report = client.evaluate_with_battery(base_task, my_agent, n_scenarios=18)
```

The same pattern works for Gemini (`google-generativeai`), Anthropic
(`anthropic`), or any callable you write. The only contract is
`my_agent(system_prompt, question) -> str`.

---

## 4. The five metrics, computed live

The platform computes the same five metrics defined in
[docs/metrics.md](./metrics.md):

- **PEI** — Planning Efficiency Index.
- **FRR** — Failure Resilience Rate.
- **IRS** — Intentional Recovery Score (defined only on fault-perturbed
  successful episodes; `None` on nominal scenarios).
- **TI** — Traceability Index.
- **CSI** — Consistency Stability Index.

**On CSI and the 100-run window.** CSI measures stability across runs and is
defined over a window of **100 sequential evaluations**. A single battery
produces far fewer points, so the platform reports CSI as **provisional** until
100 runs have accumulated, and as **final** thereafter. The report's
`csi_info` field carries the status (`provisional` / `final`), the runs used,
and the runs required.

---

## 5. Reliability tiers (qualification, not certification)

The five metrics map onto three reliability tiers under the weakest-link rule —
all required metrics must clear a tier's thresholds *simultaneously* for an
agent to qualify for that tier. The tiers correspond to three human-oversight
regimes (supervised → production-with-oversight → autonomous), not to any
external accreditation. See [docs/metrics.md](./metrics.md) for the thresholds
and [docs/certification.md](./certification.md) for how the tiers relate
(interpretively only) to functional-safety integrity levels.

A free evaluation returns the **full metrics and the full diagnostic
guidance** — you always learn where your agent stands and how to improve it.
The formal, displayable tier qualification credential is part of the paid plan.

---

## 6. Usage accounting

Monthly evaluation limits belong to the **account**, shared across all of an
account's agents. A battery costs **one unit per scenario** (an 18-scenario
battery costs 18 units), so the quota tracks real resource consumption.

| Plan | Agents | Evaluations / month (shared) |
|---|---|---|
| Free | up to 2 | 500 |
| Pro  | up to 10 | 5,000 |

---

## 7. Security posture

- **Transport & payload.** AES-256-GCM payload encryption, HMAC-SHA256 request
  signing, nonce + bounded-time-window replay protection, TLS in transit.
- **SSRF protection (path A).** The verified path validates the agent URL
  fail-closed: HTTPS only, public addresses only; localhost, private ranges,
  and cloud-metadata addresses are refused, and DNS is resolved and pinned to
  defeat rebinding.
- **Tamper-resistant scoring.** Battery metrics are computed server-side on
  both evaluation paths, never trusted from the client.
- **Live monitoring computes locally, deliberately.** `client.monitor()` is the
  exception, and the reason is a trade worth naming: computing in your process
  means Safe Halt works when the network is down, your prompts never leave, and
  an unreachable Gateway cannot stall your agent. The cost is that the platform
  sees what the SDK reports for that path — which is exactly why evidence
  provenance is recorded per field rather than assumed.
- **Signed Agent Passports.** Records are signed with **Ed25519**; the private
  key never leaves the Gateway, and the public key is published so that any
  third party can verify without contacting HB-Eval. A record only HB-Eval
  could verify would make the signature decorative.
- **Account-scoped access.** Every agent is scoped to its owner; usage counters
  are written only by the server through privileged, atomic database functions.

---

## 8. Relationship to this repository

This repository is the **scientific reference**: Python code that reproduces the
14,000-record study offline, with zero external dependencies in the core. The
production platform applies the *same* methodology as a live service. The
mapping is direct:

- `methodologies/methodology_a/run_behavioral.py` — the behavioural
  fault-injection battery that the platform's scenario engine mirrors.
- `core/statistics.py` — the metric and CSI definitions the Gateway computes.
- `methodologies/methodology_b` — the constraint-verification logic behind the
  weakest-link verdict.

The scientific contribution is the framework and its validation; the platform
demonstrates that the framework is operationally deployable.
