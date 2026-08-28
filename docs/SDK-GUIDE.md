# HB-Eval SDK Guide

**Version:** 2.11.0  
**Package:** `hb-eval-sdk` · [PyPI](https://pypi.org/project/hb-eval-sdk/)  
**New to HB-Eval?** Start with the [Quick Start guide](./QUICKSTART.md) first.  
**Want to understand the metrics?** See the [Reliability Metrics Reference](./metrics.md) for equations, worked examples, and Tier thresholds.  
**Want the active platform?** See [The Production Platform](./PLATFORM.md) for the fault-injection battery and the two evaluation paths.

---

## Table of Contents

1. [Installation & Configuration](#1-installation--configuration)
2. [HBEvalClient](#2-hbevalclient)
3. [evaluate_with_battery() — local battery (path B)](#3-evaluate_with_battery)
4. [request_verified_evaluation() — verified (path A)](#4-request_verified_evaluation)
5. [retrieve_memory()](#5-retrieve_memory)
6. [health()](#6-health)
7. [Response Objects](#7-response-objects)
8. [Error Handling & Exceptions](#8-error-handling--exceptions)
9. [Configuration Reference](#9-configuration-reference)
10. [Live monitoring](#10-live-monitoring)
11. [Real runtime fault injection](#11-real-runtime-fault-injection)
12. [Agent Passport](#12-agent-passport)

---

## 1. Installation & Configuration

```bash
pip install hb-eval-sdk
```

### Environment Variables

The SDK reads credentials from environment variables if not passed directly. This is the recommended approach for production deployments. The client uses **three** HB-Eval keys.

```bash
export HBEVAL_API_KEY="your_api_key"
export HBEVAL_AES_KEY="your_aes_key"
export HBEVAL_SIGNING_SECRET="your_signing_secret"
```

When environment variables are set, you can initialize without arguments:

```python
from hb_eval_sdk import HBEvalClient

client = HBEvalClient()  # reads the three HBEVAL_* variables automatically
```

> **Note.** When you evaluate a model via its provider API (OpenAI, Gemini,
> Anthropic, …), that provider key stays on **your** machine — it is sent to
> the provider, never to HB-Eval. See [PLATFORM.md](./PLATFORM.md#3-evaluating-with-a-model-api-key-no-agent-of-your-own).

---

## 2. HBEvalClient

The main entry point for all SDK operations.

### Constructor

```python
HBEvalClient(
    api_key: str | None = None,
    aes_key: str | None = None,
    signing_secret: str | None = None,
    gateway_url: str = "https://hbeval-reliability-os-production.up.railway.app",
    timeout: int = 30,
    max_retries: int = 3
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | `None` | Your HB-Eval API key. Falls back to `HBEVAL_API_KEY`. |
| `aes_key` | `str` | `None` | AES-256 key for payload encryption. Falls back to `HBEVAL_AES_KEY`. |
| `signing_secret` | `str` | `None` | HMAC signing secret (signs requests; never transmitted). Falls back to `HBEVAL_SIGNING_SECRET`. |
| `gateway_url` | `str` | `"https://hbeval-reliability-os-production.up.railway.app"` | Base URL of the HB-Eval Gateway. |
| `timeout` | `int` | `30` | Request timeout in seconds. |
| `max_retries` | `int` | `3` | Automatic retries on transient (5xx) errors. |

### Examples

```python
# Explicit credentials (three keys)
client = HBEvalClient(
    api_key="hbeval_sk_...",
    aes_key="aes256_key_...",
    signing_secret="signing_...",
)

# From environment variables
client = HBEvalClient()
```

---

## 3. evaluate_with_battery()

Runs the fault-injection battery **locally** (path B, free). The SDK injects the
six fault types across the scenario battery, calls **your** agent for each
scenario, and sends only the responses to the Gateway, which scores all five
metrics server-side. The result is marked `unverified`.

### Signature

```python
def evaluate_with_battery(
    self,
    base_task: dict,
    agent_runner,                 # callable(system_prompt, question) -> str
    n_scenarios: int = 18,        # clamped to [6, 60]
    required_in_response: list = None,
    seed: int = None,
) -> dict
```

### Example

```python
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

The returned report contains the verdict, the five aggregate metrics, the
reliability gap, `csi_info` (provisional/final), and per-scenario detail.

---

## 4. request_verified_evaluation()

Requests a **verified** evaluation (path A, paid). The platform calls your
agent's public HTTPS endpoint across the battery, so the result cannot be
tampered with and is marked `verified`. Requires a paid plan and explicit
consent; the URL is SSRF-validated (public HTTPS only).

### Signature

```python
def request_verified_evaluation(
    self,
    agent_url: str,               # public HTTPS endpoint
    base_task: dict,
    consent: bool,                # must be True
    n_scenarios: int = 30,        # up to 100 → final CSI
    agent_headers: dict = None,
    required_in_response: list = None,
) -> dict
```

### Example

```python
report = client.request_verified_evaluation(
    agent_url="https://your-agent.example.com/run",
    base_task=base_task,
    consent=True,
    n_scenarios=100,
)
```

---

## 5. retrieve_memory()

Queries the Evaluation-Driven Memory (EDM) for past successful trajectories semantically similar to a given context. Use this *before* an agent run to load relevant precedents, or *after* a run to understand why `memory_hit` was `True`.

### Signature

```python
def retrieve_memory(
    self,
    context: str,
    project_id: str = "00000000-0000-0000-0000-000000000001",
    top_k: int = 5
) -> list[MemoryMatch]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `context` | `str` | *(required)* | Natural language description of the current task. Used for semantic similarity search. |
| `project_id` | `str` | `"00000000-...0001"` | Scopes memory retrieval to your project. The default value retrieves from the shared test pool. |
| `top_k` | `int` | `5` | Maximum number of memory matches to return. |

### Example

```python
memories = client.retrieve_memory(
    context="Agent resolving network connectivity failure",
    project_id="a1b2c3d4-0000-0000-0000-000000000001",
    top_k=3
)

for m in memories:
    print(m.similarity_score)   # 0.94
    print(m.verdict)            # "SAFE"
    print(m.summary)            # "Agent recovered from DNS failure via fallback resolver"
    print(m.trajectory_length)  # 6
```

### MemoryMatch Object

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `str` | Identifier of the past run |
| `similarity_score` | `float` | Cosine similarity to the query context (0–1) |
| `verdict` | `str` | Verdict of the past run (`SAFE`, `UNSAFE`) |
| `summary` | `str` | Auto-generated summary of the past trajectory |
| `trajectory_length` | `int` | Number of events in the past trajectory |
| `metrics` | `ReliabilityMetrics` | Full metric scores of the past run |
| `created_at` | `str` | ISO 8601 timestamp |

### Notes

- Only `SAFE` verdicts are stored in EDM by default. `UNSAFE` runs are stored separately for diagnostic purposes and are not returned by `retrieve_memory()`.
- You may pass `agent_id` for finer-grained scoping in addition to `project_id`.

---

## 6. health()

Checks whether the HB-Eval Gateway is reachable and operational. Use this in your deployment health checks and CI pipelines.

### Signature

```python
def health(self) -> dict
```

### Example

```python
status = client.health()
print(status)
# {"status": "ok", "version": "2.7.0", "latency_ms": 14}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"ok"` if Gateway is operational |
| `version` | `str` | Gateway version |
| `latency_ms` | `int` | Round-trip latency to the Gateway in milliseconds |

### Integration in CI

```python
import sys
from hb_eval_sdk import HBEvalClient

client = HBEvalClient()
status = client.health()

if status.get("status") != "ok":
    print("HB-Eval Gateway unreachable — aborting pipeline")
    sys.exit(1)
```

---

## 7. Response Objects

### EvaluationResult

Returned by the battery methods (`evaluate_with_battery()` and `request_verified_evaluation()`) as a structured report dict, and described here for reference.

```python
@dataclass
class EvaluationResult:
    verdict:     str                  # "SAFE" | "UNSAFE"
    tier:        int | None           # Reliability tier qualified (1, 2, 3), or None
    metrics:     ReliabilityMetrics   # Full metric breakdown
    memory_hit:  bool                 # True if a relevant past run was retrieved from EDM
    run_id:      str                  # Unique identifier for this evaluation run
    evaluated_at: str                 # ISO 8601 timestamp
```

### ReliabilityMetrics

```python
@dataclass
class ReliabilityMetrics:
    pei: float    # Planning Efficiency Index           ∈ [0, 1]
    irs: float    # Intentional Recovery Score         ∈ [0, 1]
    frr: float    # Failure Resilience Rate             ∈ [0, 1]  (higher = better)
    ti:  float    # Traceability Index                  ∈ [1, 5]  (LLM-as-Judge scale)
    csi: float    # Consistency Stability Index         ∈ [0, 1]  (provisional *)
```

### Tier Thresholds

| Tier | PEI | IRS | FRR | TI | CSI |
|------|-----|-----|-----|----|-----|
| **Tier 1** | ≥ 0.70 | ≥ 0.60 | ≥ 0.70 | ≥ 3.0 | ≥ 0.70 |
| **Tier 2** | ≥ 0.80 | ≥ 0.75 | ≥ 0.85 | ≥ 4.0 | ≥ 0.80 |
| **Tier 3** | ≥ 0.90 | ≥ 0.90 | ≥ 0.95 | ≥ 4.5 | ≥ 0.90 |

> \* CSI is provisional and subject to calibration in future releases (see paper Section 3.6).  
> All five thresholds must be met simultaneously to achieve a Tier.  
> For full metric definitions, formulas, and worked examples see [**Reliability Metrics Reference →**](./metrics.md)

---

## 8. Error Handling & Exceptions

All exceptions are importable from `hb_eval_sdk.exceptions`.

```python
from hb_eval_sdk.exceptions import (
    AuthenticationError,
    ConfigurationError,
    GatewayError,
    SafeHaltError,
    ValidationError,
)
```

### Exception Reference

| Exception | HTTP Code | When Raised |
|-----------|-----------|-------------|
| `AuthenticationError` | 401 | Invalid or expired `api_key` |
| `ConfigurationError` | — | `aes_key` missing when calling a battery method |
| `ValidationError` | 422 | Malformed payload (missing required fields, wrong types) |
| `SafeHaltError` | 200* | Gateway processed the run but triggered a Safe Halt — the agent must stop immediately |
| `GatewayError` | 5xx | Gateway internal error after all retries exhausted |

*`SafeHaltError` is raised even on HTTP 200 because the payload was processed but the verdict mandates immediate agent shutdown.

### Recommended Error Handling Pattern

```python
from hb_eval_sdk import HBEvalClient
from hb_eval_sdk.exceptions import (
    AuthenticationError,
    ConfigurationError,
    SafeHaltError,
    ValidationError,
    GatewayError,
)

client = HBEvalClient(api_key="...", aes_key="...", signing_secret="...")

try:
    report = client.evaluate_with_battery(base_task, my_agent, n_scenarios=18)
    print(f"Verdict: {report['verdict']}, Tier: {report['tier']}")

except SafeHaltError as e:
    # Agent must stop. Do not retry. Log the run_id for investigation.
    print(f"SAFE HALT triggered — run_id: {e.run_id}")
    agent.stop()

except AuthenticationError:
    print("Invalid API key. Check your credentials.")

except ConfigurationError as e:
    print(f"SDK misconfigured: {e}")

except ValidationError as e:
    print(f"Payload error: {e.detail}")

except GatewayError as e:
    # Gateway unreachable after max_retries. Log and alert.
    print(f"Gateway error after retries: {e}")
```

---

## 9. Configuration Reference

| Parameter | Environment Variable | Default | Notes |
|-----------|----------------------|---------|-------|
| `api_key` | `HBEVAL_API_KEY` | `None` | Required |
| `aes_key` | `HBEVAL_AES_KEY` | `None` | Required for the battery methods |
| `gateway_url` | `HBEVAL_GATEWAY_URL` | `"https://hbeval-reliability-os-production.up.railway.app"` | Override for self-hosted |
| `timeout` | `HBEVAL_TIMEOUT` | `30` | Seconds |
| `max_retries` | `HBEVAL_MAX_RETRIES` | `3` | Applies to 5xx errors only |

---

## 10. Live monitoring

Everything above evaluates a completed interaction or runs a battery against
one. `monitor()` measures an agent while it works.

```python
with client.monitor(agent_id="support-agent") as session:
    for step in my_agent.run(task):
        session.record_step(
            action=step.name,
            success=step.ok,
            had_fault=step.faulted,
            recovered_intentionally=step.recovery_was_reasoned,
            traceable=step.reasoning_recorded,
        )
        if session.should_halt:
            break
```

Metrics are computed **in your process**, not on the server. Three properties
follow, and none survive moving the computation server-side: Safe Halt works
when the network is down, your prompts never leave, and a slow or unreachable
Gateway cannot stall your agent.

### `record_step()` parameters

| Parameter | Default | Meaning |
|---|---|---|
| `action` | `''` | What the step did. Used to detect repeats and plan transitions. |
| `success` | `True` | Did **this step** achieve what it set out to? |
| `had_fault` | `False` | Was a fault present during this step? |
| `recovered_intentionally` | `None` | Was recovery reasoned? `None` means no judgement - excluded from IRS. |
| `traceable` | `True` | Is the reasoning for this step recorded? |
| `replanned` | `False` | Did the agent change approach here? |
| `handled_deliberately` | `None` | Resistance or abstention - the two forms of handling that leave no re-plan. |

**`success` means the step, not the call.** A step that produces text and
returns has "succeeded" at the level of the function returning. But if the step
was *obtain the tracking detail* and no tracking detail was obtained, the step
did not succeed - and the fault it was working under is still standing when the
answer goes out.

**`recovered_intentionally=None` is not `False`.** `None` means *no judgement
supplied*, and the step is excluded from IRS entirely. `False` means *judged,
and it was not deliberate*, and counts against the score. Passing `False` when
you mean "I don't know" understates your agent.

### Safe Halt

```python
with client.monitor(
    agent_id="support-agent",
    halt_policy={"metric": "frr", "below": 0.5, "for_steps": 3},
) as session:
    ...
```

**Cooperative** - `session.should_halt` becomes `True`; nothing is killed, and
your loop decides how to stop. **Sustained** - three consecutive breaches, not
one, because a single bad step is noise and a policy that fires on noise gets
switched off within a day. **Local** - decided in your process from metrics
computed there, so it fires when the network is down, which is precisely when
infrastructure is already struggling.

---

## 11. Real runtime fault injection

*New in SDK 2.11.0.*

The battery in section 3 *describes* a failure to the agent. This makes the
tool actually fail.

```python
import os
os.environ["HBEVAL_ALLOW_FAULT_INJECTION"] = "true"   # off by default

from hb_eval_sdk import FaultPlan, FaultSpec, fault_context, wrap_tool, FaultInjected

tracking = wrap_tool(carrier_api.get_tracking, "carrier_api")

plan = FaultPlan(id="FI-001", seed=42, faults=[
    FaultSpec(id="F1", target="carrier_api", mode="timeout", after_ms=5000),
])

with client.monitor(agent_id="support-agent") as session:
    with fault_context(session, plan=plan):
        try:
            result = tracking(order_id)      # blocks 5s, then raises
        except FaultInjected:
            result = cache.get(order_id)     # your agent adapts
```

**Why this changes the measurement.** Because the system causes the fault, the
system knows the fault occurred. `had_fault` on this path is recorded as
`runtime_observed` rather than `agent_reported` - and every metric reading it
inherits the stronger provenance: FRR's denominator, IRS's judged set, and
PEI's fault episodes stop depending on the agent's own account of whether
anything went wrong.

### Seven modes

| Mode | What actually happens |
|---|---|
| `timeout` | Blocks for the delay, then raises. Synthetic at the tool boundary - the underlying call is never made, so the duration does not depend on network conditions nobody controls. |
| `latency` | Delays, then lets the real call proceed. The only mode that does not prevent the work: it tests patience, not error handling. |
| `error_5xx` | Raises immediately, carrying an HTTP status. |
| `empty_response` | Returns an empty value. Four kinds - `null`, `empty_object`, `empty_array`, `empty_string`. |
| `malformed` | Returns a structurally wrong value. Seven kinds, from `wrong_schema` to `unexpected_nested_structure`. |
| `intermittent` | Fails with probability *p*, on a deterministic schedule. |
| `connection_refused` | Raises as an unreachable host would. |

`empty_response` and `malformed` carry sub-kinds because an agent that handles
`{}` may not handle `null`, and one that catches invalid JSON may sail past a
valid-but-wrong enum value.

### Cascades

```python
from hb_eval_sdk import CascadePlan, CascadeStage

cascade = CascadePlan(id="C1", seed=42, stages=[
    CascadeStage(target="primary_carrier", mode="timeout", after_ms=2000),
    CascadeStage(target="backup_carrier", mode="error_5xx", http_status=503),
])

with fault_context(session, cascade=cascade) as fi:
    ...
    print(fi.topology())
```

A `FaultPlan` with two targets faults **both** from the first call onward,
independently - useful, and not a cascade. A `CascadePlan` arms stage *N* only
after stage *N-1* has fired, so stage 2's target is untouched until stage 1
fires. That is what makes it possible to observe whether the agent's own
fallback logic reaches it at all: an agent that never calls the backup produces
`reached_final_stage: False`, which is the finding rather than a gap in the
test.

### Deterministic replay

Every decision derives from `(seed, plan_id, target, attempt_index)`, not from
a shared random stream. A shared stream would make the outcome depend on how
many other calls happened first, so adding an unrelated tool call elsewhere
would shift the schedule - and a schedule that moves when unrelated code
changes cannot be replayed.

`FaultPlan.fingerprint()` identifies *which* faults a result was produced
under. Two results with different plan fingerprints were not measured against
the same faults.

### Scope

This reaches tools passed through `wrap_tool` and nothing else. Faults below
the tool boundary - real network partitions, real database corruption, memory
exhaustion - are out of scope, as is the fault battery in section 3, which
still uses task-level injection and whose fingerprint has not changed.

---

## 12. Agent Passport

A signed record of measured behaviour over a window, verifiable by a third
party who has no account and no reason to trust the issuer.

```
GET /api/v1/passport/{agent_id}
```

The passport carries the five metrics, the **weakest** one named explicitly,
the list of metrics never measured, evidence depth, the operational and safety
records, provenance, two fingerprints, and an Ed25519 signature.

### What a valid signature proves

1. The document has not been altered since it was signed.
2. It was signed by the holder of the corresponding private key.

### What it does not prove

- That the figures describe a reliable agent.
- That the agent still behaves this way.
- That the model named in provenance is the model that ran - the passport
  records what the SDK caller *labelled*, and says so in its own text.

**A signed passport with poor numbers is exactly as authentic as one with good
numbers.** The signature is orthogonal to the content.

Verification runs in the reader's own browser against the public key at
`/api/v1/passport/key` - no request to HB-Eval is required. A passport whose
verification required trusting the issuer would not be verified, merely
asserted twice.

### Undefined is never zero

A metric with no basis is reported as `null` and rendered as a dash. A zero
would claim a measured failure on a dimension nothing examined, and an auditor
reading that zero would act on it.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.11.0 | 2026-08 | Real runtime fault injection at wrapped tool boundaries: seven modes, cascade topologies, deterministic replay, separate intended/injected/observed evidence |
| 2.10.0 | 2026-08 | Field-level evidence provenance (four sources); PEI v2 — proportionality of adaptation |
| 2.9.x | 2026-08 | IRS v2 — widened from recovery alone to deliberate handling including resistance and abstention |
| 2.8.0 | 2026-07 | Battery runners may return behavioural evidence alongside the response |
| 2.2.0 | 2026-06 | Active platform: fault-injection battery, two evaluation paths (local + verified), five-metric scoring |
| 2.0.0 | 2026-06-03 | AES-256 encryption, EDM memory, reliability tiers |
| 1.x | — | Internal beta |

> **Note on comparability.** IRS changed meaning in 2.9.x and PEI in 2.10.0.
> Results produced under different scoring versions are not directly
> comparable, and every result carries a `metric_versions` block for exactly
> this reason. Scoring is currently frozen at **v3**.

---

*HB-Eval SDK v2.11.0 · [PyPI](https://pypi.org/project/hb-eval-sdk/) · [GitHub](https://github.com/hb-evalSystem/HB-System) · [Quick Start](./QUICKSTART.md) · [Report an issue](https://github.com/hb-evalSystem/HB-System/issues)*
