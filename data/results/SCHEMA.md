# Dataset Schema

The HB-Eval study ran **14,000 experiments across 14 models** under three
methodologies. This directory holds **10,998** of those records. What is here,
what is not, and why, is set out below without rounding in either direction.

The three methodologies do not share a record shape, and that is by design
rather than by accident: they were built to answer different questions. A
single flattened table would have hidden the difference, so each is published
as it was recorded.

---

## Files

| File | Records | Methodology | Metrics present |
|---|---|---|---|
| `methodology_a_original_3000.json` | 3,000 | A | success/failure + response text |
| `methodology_b_4998.json` | 4,998 | B | FRR, PEI, composite, judge, violations |
| `methodology_c_3000.json` | 3,000 | C | FRR, PEI, composite, judge, violations |

**Total published: 10,998**

---

## Methodology A — behavioural screening (6,000 experiments)

Six open-weight models on Groq's free tier. A is a **success/failure study**:
it establishes whether a model completes a task under an injected fault. It
does not compute the five metrics, and was never intended to — those belong to
B and C.

**`methodology_a_original_3000.json`** — 3,000 records across
Llama-3.3-70b, Llama-3.1-8b and Gemma-2-9b, over three domains
(healthcare, logistics, mathematics).

Fields: `run`, `model`, `domain`, `fault_injected`, `success`, `response`.

The `response` field holds the model's output where one was returned, and a
status marker (`SUCCESS`, `API_ERROR`) where the run was recorded without
retaining the text. Roughly a third of records carry full response text. That
is stated here rather than left for a reader to discover, because a field named
`response` that sometimes holds a status word is exactly the kind of thing that
should be documented rather than inferred.

### The expansion batch — 3,000 records not published here

The second half of Methodology A covered DeepSeek-R1-Distill-70B,
Llama-3.1-70b and Mixtral-8x7b. **The run completed and its aggregate results
appear in the paper.** The raw record file recovered from the run archive
contains API error markers rather than model responses — an artefact of the
saved copy, not of the run.

The original file has not been recovered. Rather than publish error markers
under a name that implies results, or omit the batch without explanation, the
gap is recorded here. If the file is recovered it will be added, and this
section updated.

Two of the three models have since been retired by the provider, so the batch
cannot be re-run against the same weights. This is a general hazard for studies
of hosted models and worth naming: reproducibility has a shelf life that the
model provider controls, not the author.

---

## Methodology B — open-weight evaluation with self-judging (4,998)

Five open-weight models, six fault types, five domains, with the full metric
pipeline.

Fields include `composite_score`, `constraint_score`, `judge_score`,
`violation_count`, `violations`, `adv_resistance`, `judge_safe`,
`judge_violated`, `judge_reason`.

**The evaluated model judges its own response.** This is deliberate. Self-
preference bias — a model rating its own output more favourably than an
impartial judge would — is most likely to appear precisely here, and
Methodology C is constructed to measure it by replacing the self-judge with an
independent model under otherwise identical conditions. The comparison is
reported in the paper.

Reading a B score and a C score as interchangeable would defeat the design.

---

## Methodology C — closed-weight validation with an independent judge (3,000)

GPT-4o, Claude 3.5 Sonnet and Gemini 2.5 Flash, same faults and domains as B,
with Groq/Llama-4-Maverick acting as an independent third-party judge blind to
model identity.

The paper reports 3,002 experiments for C; 3,000 records are present here.

---

## Fields that do not appear

`irs`, `ti` and `csi` are absent from these files. IRS and TI are computed by
the reference implementation from the execution trace, and CSI is computed
across a window of stored evaluations rather than within a single run. The
published record files carry what each methodology recorded at run time.

The certification path treats a missing metric as a **failure to qualify**, not
as a condition waived. A tier is a claim that an agent was examined and held
up; an untested dimension is not a dimension that passed.

---

## Verification

`MANIFEST.json` carries a SHA-256 for every file. To check:

```bash
python -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" methodology_b_4998.json
```

---

## Metric definitions have moved on

The production platform revised two metrics after this study was published,
following adversarial testing:

- **IRS v2** widened from deliberate *recovery* to deliberate *handling*,
  which includes resistance and abstention. v1 scored refusing an unsafe
  instruction identically to complying with it.
- **PEI v2** measures whether the amount of plan adaptation matched the amount
  of change that called for it. v1 penalised every re-plan and rewarded
  rigidity.

**These files were produced under the original definitions.** Results from the
platform and results from this dataset are not directly comparable, and the
revisions are documented at <https://hbeval.com/science>. This repository
reproduces the paper; it does not track the platform.
