# Security Policy

## Scope and Honest Posture

HB-Eval is a **research artifact** whose primary purpose is scientific
reproducibility. This document states its security posture honestly,
including known gaps, rather than implying protections the repository does
not provide. Transparency about limitations is, in a research project, a
feature rather than a weakness.

This repository contains pure-Python code for metric computation,
statistical analysis, certification logic, and the experiment
methodologies. It stores no secrets and performs no network operations
beyond the optional, clearly marked Methodology C model calls.

The cryptographic mechanisms described in the accompanying
paper—AES-256-GCM payload encryption, HMAC-SHA256 request signing, nonce
and timestamp replay prevention, and TLS transport—are properties of the
**separate hosted evaluation service**. They are **not** part of this
research repository and should not be assumed to apply to local use of
this code.

## Known Limitations

We disclose the following gaps explicitly. They are recorded here, and as
future work, rather than left for a user to discover:

- **No cryptographic signing of results produced by THIS repository.** The
  replication scripts here write plain JSON. A party with write access to
  those local files could alter recorded metrics without detection, so do
  not treat them as tamper-proof evidence in an adversarial setting.

  This limitation is scoped to the research code in this repository. The
  hosted platform **does** issue signed records: an Agent Passport is signed
  with **Ed25519** and verifiable by any third party against the public key
  at `GET /api/v1/passport/key`, without contacting HB-Eval. An earlier
  version of this document stated the limitation without that distinction,
  which would have led a reader to assume no signing existed anywhere.

  What a valid passport signature proves is narrow and worth stating: the
  document is unaltered and came from HB-Eval. It does not prove the figures
  describe a reliable agent, nor that the model named in the provenance block
  is the model that ran - the passport records what the SDK caller labelled.
- **No independent external security audit.** The code has not undergone a
  third-party security review. The accompanying automated checks (tests,
  and any dependency or code scanning enabled on the repository) are not a
  substitute for such an audit.
- **No input-integrity guarantees for evaluation payloads.** The library
  computes metrics over the trajectory it is given; it does not verify the
  provenance or integrity of that input. In a sensitive deployment, input
  authenticity must be ensured by the surrounding system.
- **No key management in the repository.** Because the research code
  performs no encryption, it includes no key-management facilities; any
  credentials for the optional hosted service are supplied by the user
  through environment variables and are never stored by this code.

- **Fault injection runs in the agent's own process.** SDK 2.11.0 injects
  real faults at instrumented tool boundaries and records evidence the agent
  cannot supply provenance for. Committed evidence is immutable, the store
  requires an instrumentation token to write to, and there is no `source=`
  parameter anywhere in the public API. None of that is a security boundary
  against code with full reflection access to the same Python process - no
  in-process design provides one, and this is stated rather than implied.

Closing these gaps—signed result manifests for the research code, a
reproducible verification trail, and an external review—is part of the
project's future-work roadmap.

## Supported Versions

Security-relevant fixes are applied to the latest released version. Users
should track the most recent release rather than relying on an older
checkout.

## Reporting a Vulnerability

If you discover a security vulnerability, please report it **privately**
and give us a reasonable opportunity to address it before any public
disclosure. Do not open a public issue for a security problem, as that
exposes other users before a fix exists.

To report, email **abuelgasim.hbeval@outlook.com** with:

- a description of the vulnerability and its potential impact,
- the steps or a minimal example needed to reproduce it,
- the affected version or commit, and
- any suggested remediation, if you have one.

You can expect an acknowledgement of your report, an assessment of the
issue, and—where a fix is warranted—a coordinated timeline for the fix
and any disclosure. We are grateful to researchers who report issues
responsibly and will credit reporters who wish to be acknowledged.

## Scope of This Policy

This policy covers the code in this repository. Issues in the separate
hosted evaluation service, or in third-party dependencies, fall outside
its scope; for dependency issues, please report upstream to the relevant
project as well.
