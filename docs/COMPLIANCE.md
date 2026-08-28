# Compliance & Regulatory Positioning
## HB-Eval — A Reliability Measurement Layer for Regulated AI Deployments

**Version:** 1.0.0 · **Authors:** abuelgasim mohamed ibrahim adam 
**Relevant regulations:** EU AI Act (2024/1689) · ISO/IEC 42001 · IEC 61508 · ISO 26262

> **Scope and intent.** HB-Eval is a *voluntary technical measurement tool*.
> It does **not** determine legal compliance, does **not** issue regulatory
> certifications, and does **not** replace the conformity assessment that
> accredited bodies and providers are required to perform. The mappings below
> indicate where HB-Eval's reliability evidence is *relevant to*, and can
> *contribute to the technical documentation for*, specific regulatory
> requirements. Whether any requirement is satisfied is decided by a full
> conformity assessment, not by HB-Eval. References to SIL/ASIL are an
> interpretive comparison of stringency, not a claim of certified safety
> integrity.

---

## Why Regulation Now Demands What HB-Eval Measures

The EU Artificial Intelligence Act (Regulation 2024/1689), which entered into force August 2024 and becomes fully applicable by August 2026, creates a legal obligation that did not previously exist: organizations deploying AI systems in high-risk contexts must provide **documented evidence of reliability before deployment** and must **monitor reliability continuously during operation**.

Article 9 requires that high-risk AI systems undergo a conformity assessment that includes, among other criteria, evaluation of "the expected lifetime of the AI system and any necessary maintenance and care measures to ensure the continued compliance with the requirements." Article 17 mandates a quality management system that includes "techniques, procedures and systematic actions to be used for risk management." Annex III defines the high-risk categories, which include AI systems used in critical infrastructure, employment, essential private services, law enforcement, border control, and administration of justice.

HB-Eval was designed to provide exactly the evidence these articles require — not as a post-hoc compliance tool, but as an engineering-first reliability framework that generates compliance documentation as a natural byproduct of rigorous measurement.

---

## Mapping HB-Eval Metrics to Regulatory Requirements

The five reliability metrics in HB-Eval are relevant to the performance and risk management requirements of the EU AI Act and ISO/IEC safety standards. Understanding this mapping is essential for compliance teams using HB-Eval as part of their technical documentation.

**FRR (Failure Resilience Rate) is relevant to EU AI Act Article 9(4)(b):** Risk management measures must include "the implementation of appropriate risk management measures." FRR measures whether your agent recovers from failures in a controlled and predictable manner. A system with FRR below the Tier 1 threshold of 0.70 is a system where failures cascade unpredictably — exactly the scenario that Article 9 requires you to identify and mitigate before deployment.

**PEI (Planning Efficiency Index) is relevant to ISO/IEC 42001 Section 9.1:** This section requires "monitoring, measurement, analysis and evaluation" of AI performance. PEI provides a quantitative answer to the question: is this agent solving tasks in the minimum necessary steps, or is it taking excessive actions that increase the surface area for errors? An agent with low PEI that uses three times more steps than necessary is an agent whose behavior is fundamentally harder to audit and predict.

**IRS (Intentional Recovery Score) is relevant to EU AI Act Article 13 (Transparency) and Article 14 (Human Oversight):** These articles require that AI systems allow human operators to understand what the system is doing and why. IRS distinguishes between recoveries that are guided by memory of past situations — which can be explained and logged — versus random trial-and-error recoveries that produce outputs no human can interpret or predict. A system with low IRS is a system where recovery behavior is opaque by design, which directly undermines the transparency requirements of Articles 13 and 14.

**TI (Traceability Index) is relevant to EU AI Act Article 12 (Record-Keeping) and Annex IV (Technical Documentation):** Annex IV requires that technical documentation describe "the methods and steps performed for the development of the AI system, including, where relevant, recourse to pre-trained systems or tools provided by third parties and how these have been used." TI measures whether the agent's reasoning chain is auditable — whether there is a traceable log of why each decision was made. A calibrated LLM judge for TI (validated at Pearson r = 0.89, κ = 0.82 in our paper) provides exactly the kind of systematic, documented evaluation that Annex IV demands.

**CSI (Consistency Stability Index) is relevant to EU AI Act Article 9(6) (Post-Market Monitoring):** Article 9(6) requires providers to "ensure that the post-market monitoring plan addresses the collection and analysis of data provided by the deployers." CSI is specifically designed as a drift-detection instrument — it monitors whether reliability is degrading over thousands of runs. An enterprise running CSI monitoring on its deployed agent has implemented a measurement that can contribute to the evidence base for a post-market monitoring system under Article 9(6); whether it satisfies the Article is determined by the provider's full conformity assessment, not by HB-Eval.

---

## The Tier Certification System as Regulatory Evidence

The three-tier system in HB-Eval (Tier 1: Supervised Deployment, Tier 2: Production with Oversight, Tier 3: Autonomous Operation) was designed to map to the three risk-management postures that safety-critical standards recommend.

**Tier 1** (all five metrics meeting minimum thresholds) is comparable in stringency—for interpretive context only—to what IEC 61508 calls "SIL 1": the system can operate in production but requires human oversight at all stages and should not be deployed in contexts where autonomous errors have irreversible consequences.

**Tier 2 certification** corresponds to "SIL 2" — the system has demonstrated sufficient robustness to operate with periodic rather than continuous oversight, suitable for high-throughput production environments where human review of every output is impractical but where exceptions can be escalated.

**Tier 3 certification** (all five metrics at their highest thresholds, validated over at least 100 consecutive runs using a Bayesian posterior with a 90% credible interval) corresponds to "SIL 3" — the system has demonstrated the kind of sustained, verifiable reliability that justifies reduced human oversight even in consequential contexts.

The weakest-link rule — where a single metric below threshold prevents the higher tier even if all others exceed it — is directly derived from the IEC 61508 principle that safety integrity cannot be aggregated across subsystems. A vehicle with a perfect engine and failed brakes is not a partially safe vehicle; it is an unsafe vehicle. The same principle applies to AI agents: an agent with perfect planning efficiency but opaque reasoning (low TI) is an agent whose safety properties cannot be established.

---

## What an EU AI Act Compliance Package Looks Like Using HB-Eval

For organizations deploying AI agents in high-risk categories, a complete compliance package built on HB-Eval consists of the following components. First, a **pre-deployment reliability assessment** — minimum 100 evaluation runs across the five metrics, stored in the HB-Eval Supabase database with immutable audit logs, producing a Tier qualification with a Bayesian credible interval that quantifies uncertainty. This assessment becomes part of the technical documentation required by Annex IV.

Second, a **continuous post-market monitoring deployment** — ongoing use of the HB-Eval SDK in production, with CSI monitoring configured to alert when consistency drops below the qualified threshold. This satisfies Article 9(6)'s post-market monitoring requirement.

Third, a **signed qualification record** (available in the Pro plan) — a machine-readable, digitally signed record that captures the qualification date, expiry date, all five metric values at qualification time, the number of evaluation runs, and the Bayesian credible interval. This artifact can be shared with regulators, customers, or auditors as evidence of a structured reliability assessment.

Fourth, an **audit trail** — every evaluation run stored in chronological order with timestamps, the specific model version being evaluated (where the API provides this information), and the verdict (SAFE/UNSAFE) alongside all metric values. This provides the longitudinal evidence record that Article 17's quality management system requirements demand.

---

## Positioning Statement for Procurement and Due Diligence

If you are a compliance officer, procurement specialist, or auditor evaluating AI vendors who use HB-Eval certification as part of their documentation, the following points are relevant. HB-Eval uses measurement methodologies derived from established safety engineering standards (IEC 61508, ISO 26262) and applies them to LLM-based agents through a novel but scientifically grounded adaptation. The adaptation is documented in a paper currently under review, with the experimental dataset (14,000 records across 14 models and five critical domains; 10,998 published, see data/results/SCHEMA.md) available for independent verification.

The certification is not self-certification by the AI vendor — it is produced by running the vendor's agent through an independent evaluation framework. The results are stored in a database that neither the agent's operator nor the agent itself can modify. Tier 3 certification, in particular, requires 100 consecutive successful runs across all five thresholds, a standard that cannot be achieved by selective testing or gaming.

For questions about using HB-Eval as part of an EU AI Act compliance strategy, contact: anonymous@example.org

---

## Limitations and Scope

HB-Eval is a reliability evaluation framework, not a legal compliance instrument. Achieving Tier 3 certification through HB-Eval does not by itself constitute legal compliance with the EU AI Act, ISO 42001, or any other regulation. Compliance with these regulations involves legal, organizational, and governance dimensions that extend far beyond technical reliability measurement.

What HB-Eval provides is the **technical evidence layer** — the documented, reproducible, quantitative measurement of reliability properties — that is a necessary but not sufficient component of a full compliance strategy. Organizations should work with legal counsel and certified conformity assessment bodies when preparing formal EU AI Act compliance documentation.

---

*HB-Eval v1.0.0 · [Certification Framework](certification.md) · [API Reference](api.md) · [Main Repository](https://github.com/hb-evalSystem/HB-System)*
