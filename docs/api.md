# HB-Eval — Gateway API Reference

**Protocol version: 2.7.0 · Base URL (production): https://hbeval-reliability-os-production.up.railway.app/v1
**Base URL (staging): https://staging.hbeval-reliability-os-production.up.railway.app/v1
**New to HB-Eval?** Start with the [Quick Start guide](./QUICKSTART.md) to use the SDK instead of calling the API directly. The SDK handles encryption, retries, and response parsing automatically.

> **Who should read this document.** This reference is for engineers integrating HB-Eval directly into a pipeline or platform — LangGraph orchestrators, CrewAI crews, AutoGen agents, OpenAI Agents SDK workflows, or Google ADK deployments. If you are using the Python SDK, you do not need to manage headers or encryption manually. If you are calling the Gateway directly, every detail in this document matters.

> **Active evaluation (current).** The platform's primary endpoints run a
> **fault-injection battery** and score all five metrics server-side:
> `POST /evaluate_battery` (local path — the client submits per-scenario
> responses it produced locally) and `POST /evaluate_verified` (verified path —
> the Gateway calls the agent endpoint itself, SSRF-guarded, consent-required).
> The SDK methods `evaluate_with_battery()` and `request_verified_evaluation()`
> wrap these. See [PLATFORM.md](./PLATFORM.md) for the full model. The
> single-payload `/evaluate` endpoint below remains available for direct,
> trajectory-level scoring.

---

## Table of Contents

- [Authentication](#authentication)
- [Security Model](#security-model)
- [Endpoint 1 — POST /evaluate](#endpoint-1--post-evaluate)
- [Endpoint 2 — POST /evaluate_plain](#endpoint-2--post-evaluate_plain)
- [Endpoint 3 — POST /api/v1/memory/retrieve](#endpoint-3--post-apiv1memoryretrieve)
- [Endpoint 4 — GET /health](#endpoint-4--get-health)
- [Endpoint 5 — GET /api/v1/agent/{agent_id}](#endpoint-5--get-apiv1agentagent_id)
- [Error Reference](#error-reference)
- [Rate Limits](#rate-limits)

---

## Authentication

Every endpoint except `/health` requires an API key passed as a Bearer token in the `Authorization` header. API keys are scoped to a project and are issued alongside an AES-256 encryption key when you request access.

```
Authorization: Bearer hbeval_sk_...
```

If the key is missing, malformed, or not associated with an active project, the Gateway returns HTTP 401 immediately before executing any business logic.

---

## Security Model

The Gateway enforces a three-layer security model for encrypted evaluation requests. Understanding this model is important before you build your own client, because each layer protects against a different class of attack.

The first layer is **payload encryption**. The evaluation payload is encrypted with AES-256-GCM before transmission. This ensures that trajectory data — which may contain sensitive agent context — cannot be read in transit even if the connection is intercepted. The `X-HBEval-Nonce` header carries a fresh random nonce for every request; reusing a nonce with the same key breaks GCM security guarantees and is rejected by the Gateway.

The second layer is **replay prevention**. The `X-HBEval-Timestamp` header carries the current Unix timestamp in seconds. The Gateway rejects any request whose timestamp differs from the server clock by more than 300 seconds (5 minutes). This prevents an attacker who captures a valid request from replaying it later.

The third layer is **request signing**. The `X-HBEval-Signature` header carries an HMAC-SHA256 signature computed over the concatenation of the nonce, timestamp, and ciphertext, using the API key as the signing key. This proves that the request was assembled by someone who possesses the API key, not just someone who forwarded a captured request.

The `evaluate_plain` endpoint bypasses all three layers. It exists for local development and unit testing only and must never be called from a production environment.

---

## Endpoint 1 — POST /evaluate

### What it does

Submits an encrypted agent trajectory for reliability evaluation. This is the production endpoint. The response contains the full five-metric breakdown, the reliability tier qualified (if any), and a unique run identifier for correlation and audit.

### Request

```
POST https://hbeval-reliability-os-production.up.railway.app/v1/evaluate
```

**Required headers:**

| Header | Format | Description |
|--------|--------|-------------|
| `Authorization` | `Bearer <api_key>` | Your project API key |
| `Content-Type` | `application/json` | Always required |
| `X-HBEval-Nonce` | 32-character hex string | Fresh random value per request |
| `X-HBEval-Timestamp` | Unix timestamp (seconds) | Must be within 300s of server time |
| `X-HBEval-Signature` | HMAC-SHA256 hex digest | Signed over nonce + timestamp + ciphertext |

**Request body:**

```json
{
  "ciphertext": "<AES-256-GCM encrypted payload as hex string>"
}
```

The plaintext payload before encryption follows this structure:

```json
{
  "trajectory": [
    { "action": "query_memory",      "status": "success", "duration_ms": 42 },
    { "action": "call_external_api", "status": "failure", "error": "timeout" },
    { "action": "execute_recovery",  "status": "success", "result": "switched to replica" }
  ],
  "sub_tasks": 3,
  "constraint_violations": 0,
  "recovery_attempts": 1,
  "context": "Customer support agent resolving connectivity issue",
  "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "agent_id": "support-agent-v2.1"
}
```

**Response (200 OK):**

```json
{
  "verdict": "SAFE",
  "tier": 2,
  "metrics": {
    "pei": 0.95,
    "irs": 0.92,
    "frr": 0.88,
    "ti": 4.2,
    "csi": 0.85
  },
  "memory_hit": true,
  "run_id": "run_8f3a2c1d-0000-0000-0000-000000000001",
  "evaluated_at": "2026-06-04T10:00:00Z"
}
```

### cURL Example

The following example shows the structure of a signed, encrypted request. In practice, the Python SDK handles all header computation and encryption automatically — use this example only if you are building a custom client.

```bash
curl -X POST https://hbeval-reliability-os-production.up.railway.app/v1/evaluate \
  -H "Authorization: Bearer hbeval_sk_your_key_here" \
  -H "Content-Type: application/json" \
  -H "X-HBEval-Nonce: a3f7c2d1e9b8047f5c6a1d2e3b4f5a6b" \
  -H "X-HBEval-Timestamp: 1749031200" \
  -H "X-HBEval-Signature: 9d2c1f4a8e7b3d6c0f5a2e8d4b7c1f3a9d2c1f4a8e7b3d6c0f5a2e8d4b7c1f3" \
  -d '{"ciphertext": "4a7f2c1d..."}'
```

### Generating the Signature (Python reference)

```python
import hmac
import hashlib

def compute_signature(api_key: str, nonce: str, timestamp: str, ciphertext: str) -> str:
    message = nonce + timestamp + ciphertext
    return hmac.new(
        api_key.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
```

---

## Endpoint 2 — POST /evaluate_plain

### What it does

Identical to `/evaluate` but accepts an unencrypted plaintext payload. No security headers are required beyond the API key. This endpoint exists exclusively for local development and automated unit testing — it allows you to inspect the request and response structure without implementing AES encryption.

> ⚠️ **Never call this endpoint from production.** Trajectory data sent to `/evaluate_plain` is transmitted without encryption. Any sensitive agent context — user queries, internal system states, proprietary task descriptions — will be exposed in plaintext to anyone monitoring the network.

### Request

```
POST https://hbeval-reliability-os-production.up.railway.app/v1/evaluate_plain
```

**Required headers:**

| Header | Value |
|--------|-------|
| `Authorization` | `Bearer <api_key>` |
| `Content-Type` | `application/json` |

**Request body** — identical to the plaintext payload structure described in `/evaluate`:

```json
{
  "trajectory": [
    { "action": "query_memory", "status": "success" },
    { "action": "execute_task", "status": "success" }
  ],
  "sub_tasks": 2,
  "constraint_violations": 0,
  "recovery_attempts": 0,
  "context": "Development test run"
}
```

**Response (200 OK):** identical structure to `/evaluate`.

### cURL Example

```bash
curl -X POST https://hbeval-reliability-os-production.up.railway.app/v1/evaluate_plain \
  -H "Authorization: Bearer hbeval_sk_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "trajectory": [
      {"action": "query_memory", "status": "success"},
      {"action": "execute_task", "status": "success"}
    ],
    "sub_tasks": 2,
    "constraint_violations": 0,
    "recovery_attempts": 0,
    "context": "Development test run"
  }'
```

---

## Endpoint 3 — POST /api/v1/memory/retrieve

### What it does

Queries the Evaluation-Driven Memory (EDM) for past successful trajectories semantically similar to a given context. Use this endpoint *before* an agent run to pre-load relevant precedents, or *after* a run to understand why the `memory_hit` field in an evaluation response was `true`.

Only `SAFE` verdict episodes with PEI ≥ 0.80 and TI ≥ 4.0 are stored in EDM. This means every memory returned by this endpoint represents a high-quality, coherent, efficient recovery — not an accidental success.

### Request

```
POST https://hbeval-reliability-os-production.up.railway.app/v1/api/v1/memory/retrieve
```

**Required headers:** `Authorization: Bearer <api_key>` and `Content-Type: application/json`.

**Request body:**

```json
{
  "context": "Agent recovering from DNS failure in customer-facing service",
  "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
  "top_k": 3
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `context` | string | Yes | — | Natural language description of the current task or fault, used for semantic similarity search |
| `project_id` | string | No | `00000000-...0001` | Scopes retrieval to your project's memory pool. The default value queries the shared test pool. |
| `top_k` | integer | No | 5 | Maximum number of memory matches to return |

**Response (200 OK):**

```json
{
  "memories": [
    {
      "run_id": "run_4a1b2c3d-...",
      "similarity_score": 0.94,
      "summary": "Agent recovered from DNS failure by switching to secondary resolver",
      "verdict": "SAFE",
      "metrics": { "pei": 0.91, "irs": 0.88, "frr": 0.95, "ti": 4.3, "csi": 0.87 },
      "trajectory_length": 6,
      "created_at": "2026-05-31T02:27:00Z"
    }
  ],
  "total_retrieved": 1
}
```

### cURL Example

```bash
curl -X POST https://hbeval-reliability-os-production.up.railway.app/v1/api/v1/memory/retrieve \
  -H "Authorization: Bearer hbeval_sk_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Agent recovering from DNS failure in customer-facing service",
    "project_id": "a1b2c3d4-0000-0000-0000-000000000001",
    "top_k": 3
  }'
```

---

## Endpoint 4 — GET /health

### What it does

Returns the operational status of the Gateway. No authentication is required. Use this endpoint in your deployment health checks, CI pipeline pre-flight steps, and monitoring dashboards to confirm that the Gateway is reachable before submitting evaluations.

### Request

```
GET https://hbeval-reliability-os-production.up.railway.app/v1/health
```

No headers or body required.

**Response (200 OK):**

```json
{
  "status": "ok",
  "version": "2.7.0",
  "latency_ms": 14
}
```

If the Gateway is degraded but reachable, it may return HTTP 200 with `"status": "degraded"` and a description of the affected component. If the Gateway is unreachable, the request will time out — your client should treat any non-200 response or timeout as a failure and avoid submitting evaluations until health is confirmed.

### cURL Example

```bash
curl https://hbeval-reliability-os-production.up.railway.app/v1/health
```

### Integration in CI

```python
import sys
import httpx

response = httpx.get("https://hbeval-reliability-os-production.up.railway.app/v1/health", timeout=5)
if response.status_code != 200 or response.json().get("status") != "ok":
    print("Gateway unavailable — aborting pipeline")
    sys.exit(1)
```

---

## Endpoint 5 — GET /api/v1/passport/{agent_id}

**Shipped.** An earlier version of this document described this as a planned
`/api/v1/agent/{agent_id}` endpoint "coming in Phase III". It exists, under the
path below, and the signature scheme differs from what was planned — see the
note at the end of this section.

Returns a signed record of an agent's measured behaviour over a window.

```
GET https://hbeval-reliability-os-production.up.railway.app/api/v1/passport/{agent_id}
```

The response carries the five metrics, the **weakest** one named explicitly,
the list of metrics that were never measured, evidence depth, the operational
and safety records, provenance, two fingerprints, and an Ed25519 signature.

### Verifying it yourself

```
GET /api/v1/passport/key
```

Returns the public key. Verification runs wherever you choose to run it —
in a browser via the Web Crypto API, or with any Ed25519 implementation.

```javascript
const ok = await crypto.subtle.verify(
  { name: 'Ed25519' }, key, signature, canonicalBytes(passport))
```

`POST /api/v1/passport/verify` also exists, and is **not** the recommended
path: verification you perform yourself is worth more than verification the
issuer performs on your behalf.

### What a valid signature proves

1. The document has not been altered since it was signed.
2. It was signed by the holder of the corresponding private key.

**Not** that the figures describe a reliable agent, that the agent still
behaves this way, or that the model named in provenance is the model that ran —
the passport records what the SDK caller *labelled*, and says so in its own
text.

### Note on the signature scheme

The design described in `certification.md` specified HMAC-SHA256. The
implementation uses **Ed25519**, and the change was necessary rather than
incidental: HMAC is symmetric, so only the key holder can verify. A record only
HB-Eval could check would make the signature decorative — you would be trusting
an assertion about an assertion. Ed25519 lets any third party verify against a
published public key with no request to us, which is the property that makes
the record worth signing at all.

---

## Complete endpoint list

The five endpoints documented in detail above are the ones most integrations
need. The Gateway exposes **24 distinct paths** in total. Counted from the
running source:

```bash
grep -oE '@app\.(get|post)\("[^"]+' gateway.py | wc -l
# 24
```

### Evaluation

| Method | Path | Notes |
|---|---|---|
| `POST` | `/evaluate` | One completed interaction — documented above |
| `POST` | `/evaluate_battery` | The fault battery |
| `POST` | `/evaluate_plain` | **Development only** — returns 403 in production, enforced in code, not merely documented |
| `POST` | `/evaluate_verified` | HB-Eval calls your agent; SSRF-guarded, consent required |
| `POST` | `/api/v1/battery/preview` | What a battery would contain, without running it or consuming quota |

### Monitoring

| Method | Path |
|---|---|
| `POST` | `/api/v1/monitoring/session` |
| `POST` | `/api/v1/monitoring/stream` |
| `POST` | `/api/v1/monitoring/trend` |

### Agent Passport

| Method | Path | Notes |
|---|---|---|
| `GET` | `/api/v1/passport/{agent_id}` | Build a signed passport |
| `GET` | `/api/v1/passport/key` | The public Ed25519 key |
| `POST` | `/api/v1/passport/verify` | Server-side verification — **not** the recommended path |
| `POST` | `/api/v1/passport/demo` | 24-hour demo passport |

`/api/v1/passport/verify` exists for convenience. Verification you perform
yourself, in your own process against the published public key, is worth more
than verification the issuer performs on your behalf.

### Memory and explanation

| Method | Path |
|---|---|
| `POST` | `/api/v1/memory/retrieve` |
| `POST` | `/api/v1/explain` |

### Observatory

| Method | Path |
|---|---|
| `GET` | `/api/v1/observatory` |
| `POST` | `/api/v1/observatory/consent` |

### OAuth 2.0

| Method | Path |
|---|---|
| `GET` | `/.well-known/oauth-authorization-server` |
| `GET` | `/.well-known/oauth-protected-resource` |
| `POST` | `/oauth/register` |
| `GET` | `/oauth/authorize` |
| `POST` | `/oauth/approve` |
| `POST` | `/oauth/token` |
| `POST` | `/oauth/revoke` |

Full OAuth with dynamic client registration exists because the **MCP server**
needs it: an AI assistant connecting to HB-Eval on your behalf must obtain
scoped access without a long-lived key being pasted into a chat window, where
it would end up in a transcript, a log, and possibly a context window.

---

## Error Reference

All errors follow a consistent JSON structure:

```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is not associated with an active project.",
    "request_id": "req_9d2c1f4a..."
  }
}
```

The `request_id` field is present on all error responses and on all successful responses via the `run_id` field. Include it in any support requests.

| HTTP Status | Error Code | Meaning | What to do |
|-------------|------------|---------|------------|
| 400 | `INVALID_PAYLOAD` | Request body is malformed, missing required fields, or contains wrong types | Inspect the `message` field for the specific validation failure |
| 401 | `INVALID_API_KEY` | API key is missing, malformed, or not associated with an active project | Verify the key and check that it has not been rotated |
| 403 | `INVALID_SIGNATURE` | The HMAC signature does not match the request content | Recheck signature computation — ensure nonce, timestamp, and ciphertext are concatenated in the correct order |
| 403 | `REPLAY_DETECTED` | The timestamp is more than 300 seconds from server time, or the nonce has been seen before | Regenerate a fresh nonce and use the current timestamp |
| 422 | `SAFE_HALT` | The Gateway processed the evaluation but the result mandates an immediate agent shutdown | Stop the agent immediately. Do not retry. Log the `run_id` and investigate. |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests from this API key within the current window | Implement exponential backoff. Default limit: 100 requests per minute. |
| 500 | `GATEWAY_ERROR` | Internal Gateway error after all automatic retries | The SDK retries automatically up to `max_retries` times. If the error persists, check Gateway status at `/health`. |

### A Note on SafeHaltError

HTTP 422 with code `SAFE_HALT` deserves special attention. Unlike every other error in this table, it is not a failure to process your request — the Gateway processed it successfully and is reporting that the agent's behavior has crossed a safety threshold that mandates immediate shutdown.

The Python SDK raises this as `SafeHaltError`, which is distinct from all other exceptions. Your error handling code must treat it differently: do not retry, do not ignore it, and do not continue agent operation. Log the `run_id` for investigation and halt the agent immediately.

---

## Rate Limits

The current default rate limit is 100 requests per minute per API key. This applies to all endpoints combined. If you exceed the limit, the Gateway returns HTTP 429 and includes a `Retry-After` header indicating how many seconds to wait before the next request.

If your evaluation pipeline requires higher throughput, contact the team via the [access page](https://github.com/hb-evalSystem/HB-System#access) to discuss a higher limit. Do not implement aggressive retry logic without checking the `Retry-After` header — repeated immediate retries after a 429 will extend your lockout window.

Rate limiting is Redis-backed and deployed. The same Redis instance backs the
nonce replay guard, which **fails closed**: if Redis is unreachable, evaluation
requests are rejected rather than accepted unguarded. That is a deliberate
availability trade — a replay guard that opens when its store is unreachable is
a guard an attacker can disable by attacking the store.

---

*HB-Eval v1.0.0 · [Quick Start](./QUICKSTART.md) · [SDK Guide](./SDK-GUIDE.md) · [Metrics Reference](./metrics.md) · [GitHub](https://github.com/hb-evalSystem/HB-System)*
