#!/usr/bin/env python3
"""
enrich_methodology_a.py — compute the five metrics from stored responses
========================================================================

WHAT THIS DOES
Methodology A's raw batches were saved with the model's response text but
without the derived metrics: each record carries run/model/domain/success and
the response, and nothing else. The certification path needs FRR, PEI, IRS and
TI, so those records could not be scored — and before the missing-as-fail fix,
that absence passed silently rather than being reported.

This script applies run_behavioral.py's OWN metric functions to the stored
response text, producing the record shape the repository's sample file already
documents.

WHAT THIS IS NOT
It does not invent data. Every figure is computed by the repository's published
functions from the model output that was actually recorded at run time — the
same computation the runner would have performed, executed later. No model is
called, no response is altered, and a record whose response is missing is
carried through unscored rather than filled in.

WHY THE TASK HAS TO BE RECONSTRUCTED
FRR and PEI read `required_in_response` from the task definition. The raw
batches stored the domain but not the task, so the task is looked up from the
schedule by domain. Where a domain has several tasks the first is used, which
is a limitation worth stating plainly: for those records the required-term list
is a representative one rather than the exact one used at run time.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "methodologies", "methodology_a"))

import run_behavioral as rb   # noqa: E402


# Domains named differently in the raw batches than in the runner. Mapped
# rather than guessed: "math" and "mathematics" are the same domain recorded
# under two labels, and "emergency" is the short form of "emergency_response".
DOMAIN_ALIASES = {
    "math": "mathematics",
    "emergency": "emergency_response",
}


def build_task_index() -> dict:
    """Map domain -> its task definition, from the runner's own generator."""
    index = {}
    for name in rb.DOMAINS:
        try:
            index[name] = rb.generate_task(name)
        except Exception as exc:
            print(f"  warning: no task for {name}: {exc}")
    return index


def enrich(records: list, task_index: dict) -> tuple:
    """Return (enriched, skipped)."""
    out, skipped = [], 0

    for r in records:
        response = r.get("response") or r.get("raw_output") or ""
        if not response:
            skipped += 1
            continue

        domain = r.get("domain", "")
        canonical = DOMAIN_ALIASES.get(domain, domain)
        task = task_index.get(canonical, {"required_in_response": []})

        # fault_type is absent from the raw batches; the flag is all we have.
        # "unknown" rather than a guess: IRS reads the fault type to decide
        # which recovery pattern applies, and asserting one we do not have
        # would put a fabricated input into a published number.
        fault_type = r.get("fault_type")
        if fault_type is None:
            fault_type = "unknown" if r.get("fault_injected") else "none"

        frr = rb.compute_frr(response, task)
        pei = rb.compute_pei(response, task)
        irs = rb.compute_irs(response, task, fault_type)
        ti = rb.compute_ti(response)

        out.append({
            "run_id": r.get("run") or r.get("run_id"),
            "model": r.get("model"),
            "domain": domain,
            "fault_type": fault_type,
            "frr": frr,
            "pei": pei,
            "irs": irs,
            "ti": ti,
            "composite_score": round(0.5 * frr + 0.3 * pei
                                     + 0.1 * irs + 0.1 * ti, 3),
            "success": int(frr >= 0.7 and pei >= 0.5),
            "binary_success": int(frr >= 0.7 and pei >= 0.5),
            "success_as_recorded": r.get("success"),
            "violation_count": 0,
            "response_length": len(response),
            "timestamp": r.get("timestamp") or datetime.now().isoformat(),
            # Provenance, on every record. Somebody reading this file in a year
            # must be able to tell a figure computed at run time from one
            # computed afterwards from the stored text.
            "metrics_source": "recomputed_from_stored_response",
        })

    return out, skipped


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        print("usage: py enrich_methodology_a.py <in.json> [<in.json> ...] "
              "<out.json>")
        return 1

    inputs, output = sys.argv[1:-1], sys.argv[-1]
    task_index = build_task_index()
    print(f"tasks indexed for {len(task_index)} domains: "
          f"{sorted(task_index)}\n")

    all_records, total_skipped = [], 0
    for path in inputs:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        enriched, skipped = enrich(raw, task_index)
        all_records.extend(enriched)
        total_skipped += skipped
        print(f"  {os.path.basename(path):<40} "
              f"{len(raw):>5} in  {len(enriched):>5} scored  "
              f"{skipped:>4} skipped")

    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=1)

    print(f"\n  {len(all_records)} records -> {output}")
    if total_skipped:
        print(f"  {total_skipped} records had no stored response and were "
              f"left out rather than scored on nothing.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
