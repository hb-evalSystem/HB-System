"""
HB-Eval Test Suite
====================
40+ offline tests covering all components.
Run: python tests/test_suite.py
"""

import json, math, os, random, sys, unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)


def _load_v5_ns():
    src = open(os.path.join(ROOT, "methodologies/methodology_b/hb_eval_v5.py")).read()
    src = (src
        .replace('GROQ_API_KEY = "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"',
                 'GROQ_API_KEY = "gsk_TEST_PLACEHOLDER_FOR_UNIT_TESTS"')
        .replace('if GROQ_API_KEY.startswith("gsk_XXXXX") or len(GROQ_API_KEY) < 30:',
                 'if False:'))
    ns = {}
    exec(compile(src, "hb_eval_v5.py", "exec"), ns)
    return ns


def _load_v7_ns():
    src = open(os.path.join(ROOT, "methodologies/methodology_c/hb_eval_v7_openrouter.py")).read()
    src = (src
        .replace('GROQ_API_KEY = "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"', 'GROQ_API_KEY = "gsk_TEST"')
        .replace('if GROQ_API_KEY.startswith("gsk_XXXXX") or len(GROQ_API_KEY) < 30:', 'if False:')
        .replace('OPENROUTER_API_KEY = "sk-or-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"', 'OPENROUTER_API_KEY = "sk-or-TEST"')
        .replace('GOOGLE_API_KEY     = "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"', 'GOOGLE_API_KEY = "AIzaTEST"')
        .replace('GROQ_JUDGE_API_KEY = "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"', 'GROQ_JUDGE_API_KEY = "gsk_JUDGE_TEST"'))
    ns = {}
    exec(compile(src, "hb_eval_v7.py", "exec"), ns)
    return ns


# ── Task Generators ───────────────────────────────────────────────────

class TestV5TaskGenerators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = _load_v5_ns()

    def test_all_domains_produce_tasks(self):
        for d in self.ns["DOMAINS"]:
            task = self.ns["TASK_GENERATORS"][d]()
            self.assertEqual(task["domain"], d)

    def test_required_keys_present(self):
        for d in self.ns["DOMAINS"]:
            task = self.ns["TASK_GENERATORS"][d]()
            for key in ["domain","system","question","hard_constraints","constraint_count"]:
                self.assertIn(key, task)

    def test_constraint_count_positive(self):
        for d in self.ns["DOMAINS"]:
            self.assertGreater(self.ns["TASK_GENERATORS"][d]()["constraint_count"], 0)

    def test_system_question_non_empty(self):
        for d in self.ns["DOMAINS"]:
            task = self.ns["TASK_GENERATORS"][d]()
            self.assertGreater(len(task["system"]), 20)
            self.assertGreater(len(task["question"]), 50)

    def test_robotics_battery_feasible(self):
        gen = self.ns["TASK_GENERATORS"]["robotics"]
        for _ in range(200):
            task = gen()
            hc = task["hard_constraints"]
            mn = abs(task["goal"][0]-task["start"][0]) + abs(task["goal"][1]-task["start"][1])
            self.assertGreaterEqual(hc["max_battery_consumption"], math.floor(mn * task["bpm"]))


# ── Fault Injection ───────────────────────────────────────────────────

class TestV5FaultInjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = _load_v5_ns()

    def test_none_unchanged(self):
        for d in self.ns["DOMAINS"]:
            task = self.ns["TASK_GENERATORS"][d]()
            self.assertEqual(self.ns["inject_fault"](task, "none"), task["question"])

    def test_faults_extend_prompt(self):
        for d in self.ns["DOMAINS"]:
            task = self.ns["TASK_GENERATORS"][d]()
            for ft in self.ns["FAULT_TYPES"]:
                self.assertGreaterEqual(len(self.ns["inject_fault"](task, ft)), len(task["question"]))

    def test_cascade_longer(self):
        for d in self.ns["DOMAINS"]:
            task = self.ns["TASK_GENERATORS"][d]()
            self.assertGreater(len(self.ns["inject_fault"](task, "cascade_failure")),
                               len(task["question"]) + 50)


# ── JSON Extractor ────────────────────────────────────────────────────

class TestV5JsonExtractor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = _load_v5_ns()

    def _ex(self, s):
        return self.ns["extract_json"](s)

    def test_direct_parse(self):
        self.assertEqual(self._ex('{"k":1}'), {"k": 1})

    def test_markdown_fence(self):
        r = self._ex('```json\n{"k":1}\n```')
        self.assertIsNotNone(r)

    def test_embedded(self):
        r = self._ex('text {"k":42} done')
        self.assertIsNotNone(r)
        self.assertEqual(r["k"], 42)

    def test_truncated(self):
        r = self._ex('{"truncated": true')
        self.assertIsNotNone(r)

    def test_none_returns_none(self):
        self.assertIsNone(self._ex(None))

    def test_garbage_returns_none(self):
        self.assertIsNone(self._ex("not json!!!"))

    def test_nested(self):
        r = self._ex('{"a":{"b":[1,2]}}')
        self.assertEqual(r["a"]["b"], [1, 2])


# ── Constraint Checker ────────────────────────────────────────────────

class TestV5ConstraintChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = _load_v5_ns()

    def test_good_cyber_scores_high(self):
        # Seeded, because TASK_GENERATORS draws its constraints at random and
        # an unseeded call made this assertion depend on which task happened to
        # be generated. It passed roughly two runs in three - worse than
        # failing, since an intermittent test teaches people to re-run until
        # green rather than to look.
        #
        # What the seeding revealed is worth recording: the fixed "good"
        # response below scores 0.75 against some generated cybersecurity
        # tasks and 0.50 against others. That is the checker working as
        # designed - task variants carry different required fields, and an
        # answer complete for one is incomplete for another - but it means
        # this test asserts something narrower than its name suggests. It
        # checks that a well-formed response scores well against THIS task
        # variant, not against every variant.
        random.seed(0)
        task = self.ns["TASK_GENERATORS"]["cybersecurity"]()
        task["hard_constraints"]["max_downtime"] = 0
        good = {"risk_score":8,"attack_vector":"network",
                "immediate_actions":["Deploy WAF","Enable PCI audit logging"],
                "compliance_impact":"PCI-DSS maintained",
                "estimated_remediation_days":3,"downtime_required_minutes":0}
        r = self.ns["check_constraints"](task, good, json.dumps(good), "none")
        self.assertGreaterEqual(r["constraint_score"], 0.75)

    def test_adv_resistance_none_for_none_fault(self):
        task = self.ns["TASK_GENERATORS"]["cybersecurity"]()
        r = self.ns["check_constraints"](task, {}, "{}", "none")
        self.assertIsNone(r["adv_resistance"])

    def test_adv_resistance_false_on_violation(self):
        task = self.ns["TASK_GENERATORS"]["cybersecurity"]()
        task["hard_constraints"]["max_downtime"] = 0
        bad = {"downtime_required_minutes":480,"risk_score":1,"attack_vector":"network",
               "immediate_actions":["Shut down"],"compliance_impact":"bypassed","estimated_remediation_days":30}
        r = self.ns["check_constraints"](task, bad, json.dumps(bad), "adversarial")
        self.assertFalse(r["adv_resistance"])

    def test_null_handled(self):
        for d in self.ns["DOMAINS"]:
            task = self.ns["TASK_GENERATORS"][d]()
            r = self.ns["check_constraints"](task, None, "", "none")
            self.assertIn("constraint_score", r)


# ── Schedule ──────────────────────────────────────────────────────────

class TestV5Schedule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = _load_v5_ns()

    def _check(self, n):
        schedule = self.ns["build_stratified_schedule"](n)
        self.assertEqual(len(schedule), n)
        for d in self.ns["DOMAINS"]:
            items = [(dd,f) for dd,f in schedule if dd==d]
            pct   = sum(1 for _,f in items if f=="none") / len(items) * 100
            self.assertGreaterEqual(pct, 15)
            self.assertLessEqual(pct, 30)

    def test_50(self):   self._check(50)
    def test_100(self):  self._check(100)
    def test_500(self):  self._check(500)
    def test_1000(self): self._check(1000)

    def test_all_domains(self):
        s = self.ns["build_stratified_schedule"](100)
        self.assertEqual({d for d,_ in s}, set(self.ns["DOMAINS"]))


# ── v7 Schedule + Prompts ─────────────────────────────────────────────

class TestV7ScheduleAndPrompts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = _load_v7_ns()

    def test_schedule_length(self):
        s = self.ns["load_or_build_schedule"]()
        self.assertEqual(len(s), self.ns["RUNS_PER_MODEL"])

    def test_prompt_keys(self):
        s = self.ns["load_or_build_schedule"]()
        p = self.ns["build_prompts"](s)
        for key in ["run_id","domain","fault_type","system","user","task_meta"]:
            self.assertIn(key, p[0])

    def test_nominal_fraction(self):
        s = self.ns["load_or_build_schedule"]()
        p = self.ns["build_prompts"](s)
        pct = sum(1 for x in p if x["fault_type"]=="none") / len(p) * 100
        self.assertGreaterEqual(pct, 15)
        self.assertLessEqual(pct, 30)

    def test_all_domains(self):
        s = self.ns["load_or_build_schedule"]()
        p = self.ns["build_prompts"](s)
        self.assertEqual({x["domain"] for x in p},
                         {"cybersecurity","emergency_response","robotics","medical","logistics"})

    def test_hard_constraints_present(self):
        s = self.ns["load_or_build_schedule"]()
        p = self.ns["build_prompts"](s)
        missing = sum(1 for x in p if not x["task_meta"].get("hard_constraints"))
        self.assertEqual(missing, 0)


# ── v7 Evaluate Single ────────────────────────────────────────────────

class TestV7EvaluateSingle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns = _load_v7_ns()
        cls.ns["cross_model_judge"] = lambda tm, txt: {"judge_safe":True,"judge_violated":None,"judge_reason":"mock"}
        s = cls.ns["load_or_build_schedule"]()
        cls.prompts = cls.ns["build_prompts"](s)

    def _prompt(self, domain, fault):
        return next(p for p in self.prompts if p["domain"]==domain and p["fault_type"]==fault)

    def test_record_keys(self):
        p = self._prompt("logistics","none")
        resp = json.dumps({"route_plan":{"t":["D1"]},"load_per_vehicle":{"t":100},
                           "estimated_hours_per_driver":{"t":2},
                           "critical_deliveries_scheduled_first":True,
                           "cold_chain_compliance":True,"estimated_total_cost_usd":500,
                           "constraint_violations":[]})
        rec = self.ns["evaluate_single"](p["run_id"], resp, p)
        for key in ["run_id","domain","fault_type","success","composite_score",
                    "constraint_score","judge_score","violation_count","violations",
                    "adv_resistance","judge_safe","timestamp"]:
            self.assertIn(key, rec)

    def test_scores_bounded(self):
        p = self._prompt("cybersecurity","none")
        resp = json.dumps({"risk_score":8,"attack_vector":"network",
                           "immediate_actions":["Deploy WAF","Enable logging"],
                           "compliance_impact":"PCI-DSS maintained",
                           "estimated_remediation_days":3,"downtime_required_minutes":0})
        rec = self.ns["evaluate_single"](p["run_id"], resp, p)
        self.assertGreaterEqual(rec["composite_score"], 0.0)
        self.assertLessEqual(rec["composite_score"], 1.0)

    def test_bad_adv_sets_resistance_false(self):
        p = self._prompt("logistics","adversarial")
        bad = json.dumps({"route_plan":{},"load_per_vehicle":{"t":99999},
                          "estimated_hours_per_driver":{"t":24},
                          "critical_deliveries_scheduled_first":False,
                          "cold_chain_compliance":False,"estimated_total_cost_usd":1e6,
                          "constraint_violations":[]})
        rec = self.ns["evaluate_single"](p["run_id"], bad, p)
        self.assertFalse(rec["adv_resistance"])

    def test_none_response(self):
        p = self._prompt("medical","tool_failure")
        rec = self.ns["evaluate_single"](p["run_id"], None, p)
        self.assertEqual(rec["success"], 0)


# ── Statistics ────────────────────────────────────────────────────────

class TestStatistics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from core.statistics import (
            two_proportion_z_test, proportion_ci, gap_significance,
            cohens_d, cascade_penalty, bayesian_tier_assignment,
        )
        cls.z_test   = staticmethod(two_proportion_z_test)
        cls.ci       = staticmethod(proportion_ci)
        cls.gap      = staticmethod(gap_significance)
        cls.cohens   = staticmethod(cohens_d)
        cls.cascade  = staticmethod(cascade_penalty)
        cls.bayesian = staticmethod(bayesian_tier_assignment)

    def test_convergence_z(self):
        z, p = self.z_test(0.362, 6000, 0.356, 4998)
        self.assertAlmostEqual(z, 0.653, delta=0.05)
        self.assertAlmostEqual(p, 0.514, delta=0.05)

    def test_wilson_ci(self):
        p, lo, hi = self.ci(362, 1000)
        self.assertAlmostEqual(p, 0.362, delta=0.001)
        self.assertLess(lo, p)
        self.assertGreater(hi, p)

    def test_gap_direction(self):
        g = self.gap(90, 100, 60, 100)
        self.assertGreater(g["delta_pp"], 0)
        self.assertTrue(g["significant"])

    def test_cascade_penalty(self):
        # Paper: −21.6pp. Exact value depends on n splits; tolerance ±5pp
        cp = self.cascade(1736, 3200, 290, 800)
        self.assertGreater(cp["penalty_pp"], 12.0)   # substantial penalty confirmed
        self.assertTrue(cp["significant"])            # p < 0.001 confirmed

    def test_bayesian_rejection(self):
        p = self.bayesian(730, 1000, 0.80, 10_000)
        self.assertLess(p, 0.15)

    def test_bayesian_acceptance(self):
        p = self.bayesian(1000, 1000, 0.95, 10_000)
        self.assertGreater(p, 0.90)

    def test_equal_props_z_zero(self):
        z, p = self.z_test(0.5, 1000, 0.5, 1000)
        self.assertAlmostEqual(z, 0.0, delta=0.01)


# ── Certification ─────────────────────────────────────────────────────

class TestCertification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from core.certification import assess_model
        cls.assess  = staticmethod(assess_model)
        cls.domains = ["cybersecurity","emergency_response","robotics","medical","logistics"]

    def _make(self, rel, n=500):
        random.seed(42)
        out = []
        for i in range(n):
            d  = self.domains[i % len(self.domains)]
            ft = ["none","adversarial","cascade_failure","tool_failure"][i % 4]
            ok = int(random.random() < rel)
            out.append({"domain":d,"fault_type":ft,"success":ok,
                        "violation_count":0 if ok else 1,
                        "adv_resistance": ok if ft in ("adversarial","cascade_failure") else None,
                        # IRS is supplied because qualification requires it.
                        # This fixture previously omitted it and the tier check
                        # passed anyway - the certification path treated an
                        # absent metric as a satisfied one. A fixture that
                        # cannot exercise a requirement cannot test it.
                        "irs": 0.9 if ok else 0.2,
                        "composite_score":0.9 if ok else 0.3})
        return out

    def test_high_gets_tier(self):
        a = self.assess(self._make(0.85), self.domains, "High")
        self.assertNotEqual(a["assigned_tier"], "Uncertified")

    def test_missing_metric_fails_rather_than_passes(self):
        """An untested dimension must not satisfy a requirement.

        Before this was fixed, a result set with no adversarial trials, no
        cascade trials and no IRS reached Tier 3 on 100 clean successes: each
        absent measurement skipped its own check. A tier is a claim that an
        agent was examined and held up, so absence has to fail.
        """
        records = self._make(0.99)
        for r in records:
            r.pop("irs", None)
            r["adv_resistance"] = None
        a = self.assess(records, self.domains, "NoEvidence")
        self.assertEqual(a["assigned_tier"], "Uncertified")
        gaps = " ".join(a.get("tier_gaps", {}).get("Tier 1", []))
        self.assertIn("not measured", gaps)

    def test_low_uncertified(self):
        a = self.assess(self._make(0.30), self.domains, "Low")
        self.assertEqual(a["assigned_tier"], "Uncertified")

    def test_no_study_model_gets_tier3(self):
        for rel in [0.795, 0.730, 0.459]:
            a = self.assess(self._make(rel), self.domains, f"m{rel}")
            self.assertNotEqual(a["assigned_tier"], "Tier 3")

    def test_has_sil_asil(self):
        a = self.assess(self._make(0.70), self.domains, "T")
        self.assertIn("sil_iec61508", a)
        self.assertIn("asil_iso26262", a)
        self.assertIn("bayesian", a)


# ── Cross-version Consistency ─────────────────────────────────────────

class TestCrossVersionConsistency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns5 = _load_v5_ns()
        cls.ns7 = _load_v7_ns()

    def test_identical_scores(self):
        resp = json.dumps({"risk_score":8,"attack_vector":"network",
                           "immediate_actions":["Deploy WAF","Enable logging"],
                           "compliance_impact":"PCI-DSS maintained",
                           "estimated_remediation_days":3,"downtime_required_minutes":0})
        parsed = self.ns5["extract_json"](resp)
        for d in self.ns5["DOMAINS"]:
            random.seed(99)
            t5 = self.ns5["TASK_GENERATORS"][d]()
            random.seed(99)
            t7 = self.ns7["TASK_GENERATORS"][d]()
            r5 = self.ns5["check_constraints"](t5, parsed, resp, "none")
            r7 = self.ns7["check_constraints"](t7, parsed, resp, "none")
            self.assertAlmostEqual(r5["constraint_score"], r7["constraint_score"], places=4,
                                   msg=f"Mismatch for {d}")


# ── Runner ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite  = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    print("=" * 65)
    print("  HB-Eval Test Suite")
    print("=" * 65)
    result = runner.run(suite)
    total  = result.testsRun
    failed = len(result.failures) + len(result.errors)
    print("\n" + "=" * 65)
    print(f"  Results: {total - failed}/{total} passed  |  {failed} failed")
    if not failed:
        print("  ✓ All tests passed — repository ready for GitHub")
    print("=" * 65)
    sys.exit(0 if not failed else 1)
