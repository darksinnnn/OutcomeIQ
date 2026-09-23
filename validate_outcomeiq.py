"""
CAT OutcomeIQ — validate_outcomeiq.py

A self-check script you run AGAINST YOUR RUNNING BACKEND to verify the six
modules actually behave the way PRD.md / Architecture.md / Agents.md say they
must, not just that the endpoints return 200.

This checks three different things, and they matter for different reasons:

  1. CONTRACT compliance  — every module response has {value, confidence, evidence}
                             with the right types. Cheap to fake, so it's necessary
                             but not sufficient.
  2. SCENARIO behavior     — the actual point of the whole system: does Reality
                             Engine really say "truck", not "operator", for the
                             FALSE_IDLE mission? Does Outcome Guardian really flag
                             quality while time stays green for ON_TIME_LOW_QUALITY?
                             This is the part that proves it reasons instead of
                             just returning plausible-looking numbers.
  3. TRUST & SAFETY language — scans every live response body for banned
                             judgmental phrasing (Architecture.md §6).

Stdlib only (urllib + sqlite3 + json) — nothing to install, nothing to break
on whatever machine runs this before the demo.

USAGE
    python validate_outcomeiq.py --base-url http://localhost:8000 --db backend/app/data/seed/catiq.db

    Exit code 0  = every check passed (or only warnings).
    Exit code 1  = at least one hard failure — do not demo yet.

    Writes a full report to validation_report.md next to wherever you run it from.

If your actual route paths or request shape differ from the defaults below,
edit the ENDPOINTS dict — everything else in the script is written against
that dict, not hardcoded paths, so it's a one-place fix.
"""

import argparse
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

# ----------------------------------------------------------------------------
# Config — edit here if your actual route names differ
# ----------------------------------------------------------------------------

ENDPOINTS = {
    "mission_contract": "/api/mission-contract",
    "time_model": "/api/time-model",
    "reality_engine": "/api/reality-engine",
    "root_cause": "/api/root-cause",
    "outcome_guardian": "/api/outcome-guardian",
    "what_if": "/api/what-if",
}

NAMED_MISSIONS = [
    "MISSION-FALSE-IDLE",
    "MISSION-ON-TIME-LOW-QUALITY",
    "MISSION-OPERATOR-CONTEXT-MISMATCH",
    "MISSION-WHAT-IF-RECOVERY",
]

BANNED_PHRASES = [
    "lazy", "fatigued", "fatigue", "dangerous", "inefficient", "careless",
    "incompetent", "slacking", "irresponsible", "bad operator", "poor operator",
    "we guarantee", "guaranteed safe", "guarantee this is safe",
]

LATENCY_WARN_MS = 800
LATENCY_FAIL_MS = 3000


@dataclass
class Result:
    name: str
    passed: bool
    severity: str  # "fail" | "warn"
    detail: str = ""


@dataclass
class Report:
    results: list = field(default_factory=list)

    def ok(self, name, detail=""):
        self.results.append(Result(name, True, "info", detail))

    def fail(self, name, detail=""):
        self.results.append(Result(name, False, "fail", detail))

    def warn(self, name, detail=""):
        self.results.append(Result(name, False, "warn", detail))

    @property
    def hard_failures(self):
        return [r for r in self.results if not r.passed and r.severity == "fail"]

    @property
    def warnings(self):
        return [r for r in self.results if not r.passed and r.severity == "warn"]


# ----------------------------------------------------------------------------
# HTTP helpers — try GET path-param, GET query-param, then POST json, in that
# order, since we don't know your exact route shape from outside the repo.
# ----------------------------------------------------------------------------

def _request(url, method="GET", payload=None, timeout=6):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode()
        elapsed_ms = (time.time() - t0) * 1000
        return resp.status, body, elapsed_ms


def call_module(base_url, endpoint_path, mission_id):
    """
    Returns (status, parsed_json_or_none, raw_text, elapsed_ms, attempted_url)
    Tries the three most common shapes a FastAPI route for this would take.
    """
    attempts = [
        ("GET", f"{base_url}{endpoint_path}/{mission_id}", None),
        ("GET", f"{base_url}{endpoint_path}?mission_id={mission_id}", None),
        ("POST", f"{base_url}{endpoint_path}", {"mission_id": mission_id}),
    ]
    last_err = None
    for method, url, payload in attempts:
        try:
            status, body, elapsed = _request(url, method=method, payload=payload)
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = None
            return status, parsed, body, elapsed, url
        except urllib.error.HTTPError as e:
            last_err = f"{method} {url} -> HTTP {e.code}"
            continue
        except Exception as e:  # connection refused, timeout, etc.
            last_err = f"{method} {url} -> {e}"
            continue
    return None, None, last_err, None, None


def call_what_if(base_url, endpoint_path, mission_id, assumption):
    url = f"{base_url}{endpoint_path}"
    try:
        status, body, elapsed = _request(url, method="POST",
                                          payload={"mission_id": mission_id, "assumption_changed": assumption})
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = None
        return status, parsed, body, elapsed, url
    except Exception as e:
        return None, None, str(e), None, url


# ----------------------------------------------------------------------------
# 1. Infra checks
# ----------------------------------------------------------------------------

def check_infra(base_url, report: Report):
    for path in ["/health", "/", "/docs"]:
        try:
            status, body, elapsed = _request(f"{base_url}{path}")
            if status == 200:
                report.ok(f"infra:{path} reachable", f"{elapsed:.0f}ms")
            else:
                report.warn(f"infra:{path} reachable", f"HTTP {status}")
        except Exception as e:
            sev = report.fail if path in ("/health", "/") else report.warn
            sev(f"infra:{path} reachable", str(e))


# ----------------------------------------------------------------------------
# 2. Contract compliance — value/confidence/evidence shape
# ----------------------------------------------------------------------------

def check_contract_shape(module_name, mission_id, parsed, report: Report):
    prefix = f"contract:{module_name}:{mission_id}"
    if parsed is None:
        report.fail(prefix, "response was not valid JSON")
        return

    payload = parsed.get("value", parsed) if isinstance(parsed, dict) else None
    if payload is None:
        report.fail(prefix, "no usable JSON object in response")
        return

    has_value = "value" in parsed
    has_confidence = "confidence" in parsed
    has_evidence = "evidence" in parsed

    if not (has_value and has_confidence and has_evidence):
        missing = [k for k, present in
                   [("value", has_value), ("confidence", has_confidence), ("evidence", has_evidence)]
                   if not present]
        report.fail(prefix, f"missing top-level keys: {missing} (Architecture.md §4 envelope)")
        return

    conf = parsed["confidence"]
    if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
        report.fail(prefix, f"confidence out of [0,1] or wrong type: {conf!r}")
    else:
        report.ok(prefix + ":confidence range")

    ev = parsed["evidence"]
    if not isinstance(ev, list) or len(ev) == 0:
        report.fail(prefix, "evidence is empty or not a list — every prediction must show its reasoning")
    else:
        report.ok(prefix + ":evidence present", f"{len(ev)} item(s)")


# ----------------------------------------------------------------------------
# 3. Scenario behavior checks — the real test of whether this reasons at all
# ----------------------------------------------------------------------------

def check_time_model_ordering(parsed, mission_id, report: Report):
    try:
        v = parsed["value"]
        p10, p50, p90 = v["p10_min"], v["p50_min"], v["p90_min"]
    except Exception:
        report.fail(f"time_model:{mission_id}:quantile keys", "missing p10_min/p50_min/p90_min in value")
        return
    if p10 <= p50 <= p90:
        report.ok(f"time_model:{mission_id}:quantile ordering", f"P10={p10} P50={p50} P90={p90}")
    else:
        report.fail(f"time_model:{mission_id}:quantile ordering", f"NOT ordered: P10={p10} P50={p50} P90={p90}")


def check_reality_engine_false_idle(parsed, report: Report):
    try:
        v = parsed["value"]
        cls = v.get("explanation_class", "")
    except Exception:
        report.fail("reality_engine:FALSE_IDLE:class", "could not read explanation_class")
        return
    if cls == "operator_variation":
        report.fail("reality_engine:FALSE_IDLE:class",
                     "classified idle as operator_variation — this is the exact false-positive the module exists to avoid")
        return
    if cls in ("external_workflow", "unknown"):
        report.ok("reality_engine:FALSE_IDLE:class", f"class={cls}")
    else:
        report.warn("reality_engine:FALSE_IDLE:class", f"unexpected class={cls}, verify manually")

    ev_text = json.dumps(parsed.get("evidence", [])).lower()
    if "truck" in ev_text:
        report.ok("reality_engine:FALSE_IDLE:evidence mentions truck")
    else:
        report.warn("reality_engine:FALSE_IDLE:evidence mentions truck",
                     "evidence doesn't reference truck availability — check it's using workflow_event data")


def check_root_cause_operator_mismatch(parsed, report: Report):
    try:
        contributors = parsed["value"]["contributors"]
        by_cause = {c["cause"]: c["probability"] for c in contributors}
    except Exception:
        report.fail("root_cause:OPERATOR_CONTEXT_MISMATCH:shape", "could not read contributors list")
        return
    top_cause = max(by_cause, key=by_cause.get) if by_cause else None
    if top_cause == "operator":
        report.ok("root_cause:OPERATOR_CONTEXT_MISMATCH:top cause", f"contributors={by_cause}")
    elif by_cause.get("operator", 0) >= 0.2:
        report.warn("root_cause:OPERATOR_CONTEXT_MISMATCH:top cause",
                     f"operator not top cause but present: {by_cause} — verify against evidence text")
    else:
        report.fail("root_cause:OPERATOR_CONTEXT_MISMATCH:top cause",
                     f"operator-context evidence gap not reflected: {by_cause}")


def check_outcome_guardian_on_time_low_quality(parsed, report: Report):
    try:
        v = parsed["value"]
    except Exception:
        report.fail("outcome_guardian:ON_TIME_LOW_QUALITY:shape", "no value object")
        return
    time_sig = str(v.get("time", "")).lower()
    quality_sig = str(v.get("quality", "")).lower()
    acceptance_sig = str(v.get("acceptance", "")).lower()

    if time_sig == "green":
        report.ok("outcome_guardian:ON_TIME_LOW_QUALITY:time signal green")
    else:
        report.warn("outcome_guardian:ON_TIME_LOW_QUALITY:time signal green",
                     f"expected green, got '{time_sig}' — scenario may have drifted, check generator output")

    if quality_sig in ("amber", "red") or acceptance_sig in ("amber", "red"):
        report.ok("outcome_guardian:ON_TIME_LOW_QUALITY:quality/acceptance flagged",
                   f"quality={quality_sig} acceptance={acceptance_sig}")
    else:
        report.fail("outcome_guardian:ON_TIME_LOW_QUALITY:quality/acceptance flagged",
                     "THE key demo moment isn't firing: on-schedule mission not showing quality risk")

    if "rework_probability" in v:
        report.ok("outcome_guardian:ON_TIME_LOW_QUALITY:rework_probability present", str(v["rework_probability"]))
    else:
        report.warn("outcome_guardian:ON_TIME_LOW_QUALITY:rework_probability present", "field missing")


def check_what_if_recovery(base_url, report: Report):
    status, parsed, raw, elapsed, url = call_what_if(
        base_url, ENDPOINTS["what_if"], "MISSION-WHAT-IF-RECOVERY", {"add_truck": True})
    if status != 200 or parsed is None:
        report.fail("what_if:WHAT_IF_RECOVERY", f"call failed: {raw if not parsed else 'bad JSON'} ({url})")
        return
    try:
        v = parsed["value"]
        before = v["before"]["p50_min"] if "p50_min" in v.get("before", {}) else v["before"]["value"]["p50_min"]
        after = v["after"]["p50_min"] if "p50_min" in v.get("after", {}) else v["after"]["value"]["p50_min"]
    except Exception as e:
        report.fail("what_if:WHAT_IF_RECOVERY:shape", f"could not read before/after P50: {e}")
        return
    if after < before:
        report.ok("what_if:WHAT_IF_RECOVERY:recovery shown", f"before={before} after={after}")
    else:
        report.fail("what_if:WHAT_IF_RECOVERY:recovery shown",
                     f"adding a truck did not reduce predicted duration: before={before} after={after}")
    check_contract_shape("what_if", "WHAT_IF_RECOVERY (add_truck)", parsed, report)


# ----------------------------------------------------------------------------
# 4. Trust & safety language scan
# ----------------------------------------------------------------------------

def scan_banned_language(all_raw_bodies, report: Report):
    hits = []
    for label, raw in all_raw_bodies:
        low = raw.lower()
        for phrase in BANNED_PHRASES:
            if re.search(r"\b" + re.escape(phrase) + r"\b", low):
                hits.append((label, phrase))
    if hits:
        for label, phrase in hits:
            report.fail(f"trust_language:{label}", f"banned phrase found: '{phrase}'")
    else:
        report.ok("trust_language: all live responses clean", f"{len(all_raw_bodies)} responses scanned")


# ----------------------------------------------------------------------------
# 5. Mission Contract vs. ground truth in the seed DB
# ----------------------------------------------------------------------------

def check_mission_contract_vs_db(base_url, db_path, report: Report):
    if not db_path:
        report.warn("mission_contract:vs_db", "no --db path given, skipping ground-truth comparison")
        return
    try:
        conn = sqlite3.connect(db_path)
    except Exception as e:
        report.warn("mission_contract:vs_db", f"could not open db: {e}")
        return
    for mid in NAMED_MISSIONS:
        row = conn.execute(
            "SELECT objective_quantity, quality_tolerance_cm, deadline FROM mission WHERE id=?", (mid,)
        ).fetchone()
        if row is None:
            report.warn(f"mission_contract:vs_db:{mid}", "mission not found in seed DB")
            continue
        db_qty, db_tol, db_deadline = row

        status, parsed, raw, elapsed, url = call_module(base_url, ENDPOINTS["mission_contract"], mid)
        if status != 200 or parsed is None:
            report.fail(f"mission_contract:vs_db:{mid}", f"call failed ({url})")
            continue
        v = parsed.get("value", parsed)
        api_qty = v.get("objective_quantity")
        api_tol = v.get("quality_tolerance_cm")
        if api_qty is not None and abs(float(api_qty) - float(db_qty)) < 0.01:
            report.ok(f"mission_contract:vs_db:{mid}:objective_quantity matches")
        else:
            report.fail(f"mission_contract:vs_db:{mid}:objective_quantity matches",
                         f"db={db_qty} api={api_qty}")
        if api_tol is not None and abs(float(api_tol) - float(db_tol)) < 0.01:
            report.ok(f"mission_contract:vs_db:{mid}:quality_tolerance matches")
        else:
            report.warn(f"mission_contract:vs_db:{mid}:quality_tolerance matches",
                         f"db={db_tol} api={api_tol}")
    conn.close()


# ----------------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://localhost:8000")
    ap.add_argument("--db", default=None, help="path to catiq.db, for ground-truth checks")
    ap.add_argument("--report", default="validation_report.md")
    args = ap.parse_args()

    report = Report()
    all_raw_bodies = []

    print(f"Checking {args.base_url} ...\n")
    check_infra(args.base_url, report)

    # --- contract shape + latency, across all named missions x all modules ---
    for module_name, path in ENDPOINTS.items():
        if module_name == "what_if":
            continue  # what_if needs a POST body with an assumption, handled separately
        for mid in NAMED_MISSIONS:
            status, parsed, raw, elapsed, url = call_module(args.base_url, path, mid)
            if status != 200:
                report.fail(f"call:{module_name}:{mid}", f"HTTP {status if status else 'no response'} ({url}) — {raw if not parsed else ''}")
                continue
            all_raw_bodies.append((f"{module_name}:{mid}", raw))
            check_contract_shape(module_name, mid, parsed, report)

            if elapsed is not None:
                if elapsed > LATENCY_FAIL_MS:
                    report.fail(f"latency:{module_name}:{mid}", f"{elapsed:.0f}ms — too slow for live demo clicking")
                elif elapsed > LATENCY_WARN_MS:
                    report.warn(f"latency:{module_name}:{mid}", f"{elapsed:.0f}ms")

            # scenario-specific behavior checks, only for the mission each check targets
            if module_name == "time_model":
                check_time_model_ordering(parsed, mid, report)
            if module_name == "reality_engine" and mid == "MISSION-FALSE-IDLE":
                check_reality_engine_false_idle(parsed, report)
            if module_name == "root_cause" and mid == "MISSION-OPERATOR-CONTEXT-MISMATCH":
                check_root_cause_operator_mismatch(parsed, report)
            if module_name == "outcome_guardian" and mid == "MISSION-ON-TIME-LOW-QUALITY":
                check_outcome_guardian_on_time_low_quality(parsed, report)

    check_what_if_recovery(args.base_url, report)
    check_mission_contract_vs_db(args.base_url, args.db, report)
    scan_banned_language(all_raw_bodies, report)

    # --- report ---
    print_and_write_report(report, args.report)

    if report.hard_failures:
        print(f"\n{len(report.hard_failures)} HARD FAILURE(S). Do not demo yet — see {args.report}.")
        sys.exit(1)
    elif report.warnings:
        print(f"\nNo hard failures, {len(report.warnings)} warning(s) to review — see {args.report}.")
        sys.exit(0)
    else:
        print(f"\nAll checks passed. See {args.report} for the full readout.")
        sys.exit(0)


def print_and_write_report(report: Report, path):
    total = len(report.results)
    passed = sum(1 for r in report.results if r.passed)
    failed = len(report.hard_failures)
    warned = len(report.warnings)
    score = round(100 * passed / total, 1) if total else 0.0

    lines = [
        "# CAT OutcomeIQ — Validation Report",
        "",
        f"**Readiness score: {score}%**  ({passed}/{total} checks passed, {failed} hard failures, {warned} warnings)",
        "",
        "| Check | Status | Detail |",
        "|---|---|---|",
    ]
    for r in report.results:
        icon = "PASS" if r.passed else ("FAIL" if r.severity == "fail" else "WARN")
        lines.append(f"| {r.name} | {icon} | {r.detail} |")

    lines += [
        "",
        "## Not automated by this script — verify manually",
        "- WebSocket live telemetry stream (`/api/telemetry/ws/{mission_id}`) — connect a client and confirm ticks arrive.",
        "- Data-leakage review: grep `time_model` feature-building code for any reference to `outcome.*` fields — "
        "this script can't see your source, only your API responses.",
        "- Frontend rendering of confidence + evidence on every screen (Frontend.md requirement) — this script only "
        "checks the API contract, not that the UI actually surfaces it.",
        "",
    ]

    text = "\n".join(lines)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    print("\n".join(
        f"[{'PASS' if r.passed else ('FAIL' if r.severity == 'fail' else 'WARN')}] {r.name}" +
        (f" — {r.detail}" if r.detail else "")
        for r in report.results
    ))
    print(f"\nReadiness score: {score}%  ({passed}/{total} passed, {failed} hard failures, {warned} warnings)")


if __name__ == "__main__":
    main()
