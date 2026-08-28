"""
verify_dataset.py — the published dataset matches its manifest
================================================================
    py tests/verify_dataset.py

WHY THIS RUNS IN CI
`data/results/` contains 10,998 experimental records that the paper's figures
rest on, alongside a MANIFEST.json carrying a SHA-256 for each file. A manifest
nobody checks is a manifest that silently stops being true - a file gets
regenerated, a line ending changes, someone re-exports a batch, and the hash in
the manifest quietly becomes a hash of something that no longer exists.

Running this on every push means the claim "these are the records, and here are
their hashes" is verified continuously rather than asserted once.

WHAT IT CHECKS
For every file the manifest names: that it exists, that its SHA-256 matches,
and that it holds the number of records the manifest claims. All three, not
just the hash - the record count is an independent cross-check, written down
separately from the digest.

WHAT IT DOES NOT CHECK
Whether the records are scientifically correct. This verifies integrity, not
validity. See docs/metrics.md and the paper for what the data supports.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "data", "results")


def main() -> int:
    manifest_path = os.path.join(DATA_DIR, "MANIFEST.json")
    if not os.path.exists(manifest_path):
        # The most likely cause is not a missing file on disk - it is a file
        # git was told to ignore. .gitignore once carried
        # `data/results/*.json`, from when those files were only produced at
        # runtime. After the dataset was published that rule excluded it
        # silently: no error locally, a repository that looked complete, and
        # a CI failure on a manifest GitHub had never received.
        print(f"FAIL: no manifest at {manifest_path}")
        print()
        print("  If the files exist locally but not here, check .gitignore.")
        print("  Confirm with:  git check-ignore -v data/results/MANIFEST.json")
        print("  A rule matching data/results/*.json excludes the published")
        print("  dataset without reporting anything.")
        return 1

    with open(manifest_path, encoding="utf-8") as fh:
        manifest = json.load(fh)

    print("=" * 68)
    print("PUBLISHED DATASET — INTEGRITY")
    print("=" * 68)
    print(f"  study total:    {manifest.get('study_total_experiments')}")
    print(f"  published here: {manifest.get('published_records')}")
    print()

    failures = []
    total_records = 0

    for name, meta in sorted(manifest.get("files", {}).items()):
        path = os.path.join(DATA_DIR, name)

        if not os.path.exists(path):
            print(f"  MISSING  {name}")
            failures.append(f"{name}: file not found")
            continue

        raw = open(path, "rb").read()
        digest = hashlib.sha256(raw).hexdigest()
        hash_ok = digest == meta.get("sha256")

        try:
            records = len(json.load(open(path, encoding="utf-8")))
        except Exception as exc:
            print(f"  UNREADABLE  {name}: {type(exc).__name__}")
            failures.append(f"{name}: not valid JSON")
            continue

        count_ok = records == meta.get("records")
        total_records += records

        status = "OK" if (hash_ok and count_ok) else "FAIL"
        print(f"  {status:<8} {name}")
        print(f"           {records:,} records, sha256 "
              f"{'verified' if hash_ok else 'MISMATCH'}")

        if not hash_ok:
            failures.append(
                f"{name}: sha256 {digest[:16]}... does not match manifest")
        if not count_ok:
            failures.append(
                f"{name}: {records} records, manifest says "
                f"{meta.get('records')}")

    print()
    print(f"  total records verified: {total_records:,}")

    expected_total = manifest.get("published_records")
    if expected_total is not None and total_records != expected_total:
        failures.append(
            f"records across files total {total_records}, but the manifest's "
            f"published_records says {expected_total}")

    print()
    print("=" * 68)
    if failures:
        print(f"FAILED — {len(failures)}:")
        for f in failures:
            print(f"  * {f}")
        return 1

    print("Dataset matches its manifest.")
    print()
    print("This verifies integrity — that these are the files the manifest")
    print("describes, unchanged. It says nothing about whether the records")
    print("support any particular conclusion.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
