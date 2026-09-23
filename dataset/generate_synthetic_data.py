"""
CAT OutcomeIQ — synthetic data generator.

Builds a causally-structured synthetic jobsite (not independent random() per field —
see Architecture.md §5) and loads it into a SQLite database built from schema.sql,
plus writes flat CSVs per table for quick inspection.

Run:
    python3 generate_synthetic_data.py --out ./seed --db ./seed/catiq.db --missions 200

Deterministic: fixed RNG seed, so re-running produces the same dataset, which is what
makes the three-scenario demo reproducible (Architecture.md §5 "named seed scenarios").

Stdlib only — no third-party dependencies, on purpose, so this never fails to run
on whatever machine builds the demo.
"""

import argparse
import csv
import json
import math
import os
import random
import sqlite3
import uuid
from datetime import datetime, timedelta

RNG_SEED = 42

TASK_TYPES = ["Earth Excavation", "Trenching", "Material Loading", "Grading", "Demolition"]
WEATHER_OPTIONS = ["Sunny", "Cloudy", "Rainy", "Windy"]
ADVERSE_WEATHER = {"Rainy", "Windy"}

# naive baseline estimate per task type (minutes) — mirrors the simple lookup-table
# estimate CAT's own sample data implies, kept so the demo can show old-estimate vs
# our P10/P50/P90 side by side.
NAIVE_BASE_MIN = {
    "Earth Excavation": 60,
    "Trenching": 45,
    "Material Loading": 30,
    "Grading": 35,
    "Demolition": 90,
}

SOIL_TYPES = ["clay", "sandy_loam", "gravel_fill"]
MACHINE_FAMILIES = ["excavator", "dozer", "loader"]


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


class World:
    """Holds all generated rows, table by table, ready to insert/export."""

    def __init__(self):
        self.tables = {
            "project": [], "zone": [], "operator": [], "machine": [],
            "operator_capability_evidence": [], "machine_health": [],
            "mission": [], "environment": [], "workflow_event": [],
            "telemetry": [], "quality_observation": [], "outcome": [],
        }

    def add(self, table, row):
        self.tables[table].append(row)


# ----------------------------------------------------------------------------
# Reference data
# ----------------------------------------------------------------------------

def build_reference_data(world: World, rng: random.Random):
    project_id = "PRJ-001"
    world.add("project", {
        "id": project_id, "name": "North Ridge Site", "deadline": "2026-12-31T18:00:00",
        "target_quantity": 50000, "quality_criteria": json.dumps({"tolerance_cm": 5}),
    })

    zones = []
    for i, soil in enumerate(["clay", "sandy_loam", "gravel_fill", "clay"]):
        zid = f"ZONE-{chr(65+i)}"
        zones.append(zid)
        world.add("zone", {
            "id": zid, "project_id": project_id, "name": f"Zone {chr(65+i)}",
            "soil_type": soil, "notes": None,
        })

    operators = []
    op_names = ["A. Rao", "J. Silva", "M. Osei", "T. Nguyen", "P. Kowalski",
                "S. Fernandes", "R. Alvarez", "K. Mensah", "D. Park", "L. Ibrahim"]
    for i, name in enumerate(op_names):
        oid = f"OP-{1001+i}"
        operators.append(oid)
        world.add("operator", {
            "id": oid, "name": name,
            "experience_years": round(rng.uniform(1, 15), 1),
            "certifications": json.dumps(["basic_excavation"]),
        })

    machines = []
    for i in range(8):
        mid = f"EXC-{100+i}" if i % 2 == 0 else f"DOZ-{200+i}"
        family = MACHINE_FAMILIES[i % len(MACHINE_FAMILIES)]
        machines.append(mid)
        world.add("machine", {
            "id": mid, "model": f"Cat {320 + i}", "machine_family": family,
            "age_years": round(rng.uniform(0.5, 8), 1),
            "install_date": "2019-01-01",
        })

    return project_id, zones, operators, machines


def weather_bucket(weather: str) -> str:
    return "adverse" if weather in ADVERSE_WEATHER else "normal"


def build_operator_evidence(world: World, rng: random.Random, operators, cold_start_pairs):
    """
    Seed each operator's passport with evidence per (task_type, weather_bucket).
    cold_start_pairs: set of (operator_id, task_type, weather_bucket) that must stay
    near-zero evidence — used by the OPERATOR_CONTEXT_MISMATCH scenario.
    """
    for oid in operators:
        base_skill = rng.uniform(0.55, 0.95)  # this operator's general competence
        for task in TASK_TYPES:
            for bucket in ["normal", "adverse"]:
                key = (oid, task, bucket)
                if key in cold_start_pairs:
                    sample_count, success_count = 0, 0
                elif oid == operators[0] and task == "Trenching" and bucket == "normal":
                    # Established high competence for FALSE_IDLE demo: proves operator is proficient
                    sample_count = 28
                    success_count = 26
                else:
                    sample_count = rng.randint(3, 30) if bucket == "normal" else rng.randint(0, 15)
                    bucket_penalty = 0.15 if bucket == "adverse" else 0.0
                    success_rate = max(0.2, min(0.98, base_skill - bucket_penalty + rng.uniform(-0.1, 0.1)))
                    success_count = round(sample_count * success_rate)

                confidence = 0.0
                if sample_count > 0:
                    success_rate = success_count / sample_count
                    # confidence grows with sample size (diminishing returns) and success rate
                    confidence = round(min(0.97, success_rate * (1 - math.exp(-sample_count / 8))), 2)

                world.add("operator_capability_evidence", {
                    "id": new_id("EV"), "operator_id": oid, "task_type": task,
                    "weather_bucket": bucket, "material": None,
                    "sample_count": sample_count, "success_count": success_count,
                    "avg_time_delta_pct": round(rng.uniform(-8, 12), 1) if sample_count else None,
                    "avg_quality_success_pct": round(rng.uniform(70, 98), 1) if sample_count else None,
                    "confidence": confidence,
                    "last_verified_at": iso(datetime(2026, 9, 20)),
                })


def evidence_confidence(world: World, operator_id, task_type, bucket) -> float:
    for row in world.tables["operator_capability_evidence"]:
        if (row["operator_id"], row["task_type"], row["weather_bucket"]) == (operator_id, task_type, bucket):
            return row["confidence"]
    return 0.3


# ----------------------------------------------------------------------------
# Causal mission generation
# ----------------------------------------------------------------------------

def gen_environment(rng: random.Random, weather: str):
    if weather == "Rainy":
        soil_moisture = rng.uniform(0.6, 0.95)
        visibility = rng.choice(["reduced", "reduced", "poor"])
        wind = rng.uniform(5, 20)
    elif weather == "Windy":
        soil_moisture = rng.uniform(0.15, 0.35)
        visibility = rng.choice(["good", "reduced"])
        wind = rng.uniform(25, 45)
    elif weather == "Cloudy":
        soil_moisture = rng.uniform(0.2, 0.45)
        visibility = "good"
        wind = rng.uniform(5, 15)
    else:  # Sunny
        soil_moisture = rng.uniform(0.05, 0.25)
        visibility = "good"
        wind = rng.uniform(0, 10)
    temp = rng.uniform(14, 34)
    return soil_moisture, visibility, temp, wind


def gen_machine_health(rng: random.Random, age_years: float):
    # older machines: lower baseline health, more fault likelihood
    health = max(55, min(99, 97 - age_years * 3.2 + rng.uniform(-4, 4)))
    hydraulic = max(50, min(99, health - rng.uniform(0, 8)))
    faults = 0
    if health < 75:
        faults = rng.choice([0, 1, 1, 2])
    return round(health, 1), round(hydraulic, 1), faults


def simulate_mission(world: World, rng: random.Random, *, mission_id, project_id, zone_id,
                      zones_soil, task_type, weather, operator_id, machine_id, machines_meta,
                      start_time, scenario_tag=None, force_truck_absent=False,
                      force_operator_cold_start=False, force_on_time_low_quality=False,
                      quantity_scale=1.0):
    """
    The single causal engine every mission (named-scenario or random) runs through.
    Chains implemented (see Architecture.md §5):
      weather -> soil_moisture -> cycle_time/fuel
      truck_present(False) -> idle -> duration  (independent of operator)
      operator context confidence -> control_smoothness -> fuel/cycle variance, quality
      machine_health -> cycle_time, fuel
    """
    bucket = weather_bucket(weather)
    soil_moisture, visibility, temp, wind = gen_environment(rng, weather)

    machine = machines_meta[machine_id]
    health_pct, hydraulic_pct, fault_count = gen_machine_health(rng, machine["age_years"])

    confidence = evidence_confidence(world, operator_id, task_type, bucket)
    if force_operator_cold_start:
        confidence = 0.05  # near-zero evidence in this exact context, by construction

    naive_base = NAIVE_BASE_MIN[task_type]
    objective_qty = round(naive_base * rng.uniform(6, 9) * quantity_scale, 1)  # m3-ish, scaled from time baseline

    world.add("mission", {
        "id": mission_id, "project_id": project_id, "zone_id": zone_id, "task_type": task_type,
        "objective_quantity": objective_qty, "objective_unit": "m3",
        "quality_tolerance_cm": 5.0, "deadline": iso(start_time + timedelta(hours=6)),
        "safety_constraints": json.dumps(["no_entry_zone_c"] if rng.random() < 0.15 else []),
        "assigned_machine_id": machine_id, "assigned_operator_id": operator_id,
        "resources": json.dumps({"trucks_required": 2 if task_type in ("Trenching", "Material Loading", "Earth Excavation") else 0}),
        "naive_estimated_time_min": naive_base,
        "start_time": iso(start_time), "status": "complete", "scenario_tag": scenario_tag,
    })

    world.add("environment", {
        "id": new_id("ENV"), "mission_id": mission_id, "weather": weather,
        "soil_moisture": round(soil_moisture, 2), "visibility": visibility,
        "temperature_c": round(temp, 1), "wind_kph": round(wind, 1),
    })

    world.add("machine_health", {
        "id": new_id("MH"), "machine_id": machine_id, "engine_hours": machine["engine_hours"],
        "health_pct": health_pct, "hydraulic_health_pct": hydraulic_pct,
        "recent_fault_count": fault_count, "recorded_at": iso(start_time),
    })

    # --- workflow: truck availability chain ---
    trucks_needed = task_type in ("Trenching", "Material Loading", "Earth Excavation")
    truck_absent_duration_min = 0.0
    if trucks_needed:
        if force_truck_absent:
            truck_present = False
            truck_eta = rng.uniform(15, 25)
            queue_start = rng.randint(2, 4)
        else:
            truck_present = rng.random() > 0.25
            truck_eta = 0.0 if truck_present else rng.uniform(5, 15)
            queue_start = rng.randint(0, 2)
        if not truck_present:
            truck_absent_duration_min = truck_eta

        for i in range(3):
            ts = start_time + timedelta(minutes=i * 12)
            world.add("workflow_event", {
                "id": new_id("WF"), "mission_id": mission_id, "timestamp": iso(ts),
                "truck_present": int(truck_present if i > 0 else True),
                "truck_eta_min": truck_eta if not truck_present else None,
                "queue_length": queue_start + i if not truck_present else max(0, queue_start - i),
                "material_available": 1,
                "nearby_machine_count": rng.randint(0, 3),
            })

    # --- cycle time / fuel causal chain ---
    soil_multiplier = 1.0 + soil_moisture * 0.55          # wetter soil -> slower cycles, more hydraulic demand
    health_multiplier = 1.0 + max(0, (85 - health_pct)) * 0.01  # degraded machine -> slower
    technique_multiplier = 1.0 + max(0, (0.6 - confidence)) * 0.35  # low-confidence context -> more correction, slower
    control_smoothness = round(max(0.35, min(0.98, confidence * 0.9 + rng.uniform(-0.05, 0.05))), 2)

    cycle_multiplier = soil_multiplier * health_multiplier * technique_multiplier
    duration_min = naive_base * cycle_multiplier + rng.uniform(-4, 4)
    idle_from_truck = truck_absent_duration_min
    duration_min += idle_from_truck

    fuel_l = round((naive_base / 15.0) * cycle_multiplier + rng.uniform(-0.5, 1.0), 1)
    load_cycles = max(4, round(objective_qty / rng.uniform(8, 14)))

    # --- telemetry ticks ---
    n_ticks = 4
    seg = duration_min / n_ticks
    cum_fuel, cum_cycles = 0.0, 0
    for i in range(n_ticks):
        ts = start_time + timedelta(minutes=seg * i)
        cum_fuel += fuel_l / n_ticks
        cum_cycles += load_cycles // n_ticks
        idle_tick = 0.0
        if trucks_needed and not (i == 0) and idle_from_truck > 0:
            idle_tick = idle_from_truck / (n_ticks - 1)

        # seatbelt: mostly fastened; occasionally a short, legitimate unfastened moment
        # during a low-speed reposition (this is the ambiguous case Reality Engine must reason about)
        moving = rng.random() < 0.8
        speed = round(rng.uniform(2, 9) if moving else 0.0, 1)
        unfastened_legit = trucks_needed and i == 1 and rng.random() < 0.12
        seatbelt = "Unfastened" if unfastened_legit else "Fastened"
        occupancy = 1
        # a genuinely suspicious pattern: unfastened + moving fast + high occupancy uncertainty (rare, deliberate)
        suspicious = (seatbelt == "Unfastened" and moving and speed > 5 and rng.random() < 0.3)
        safety_alert = 1 if suspicious else 0
        pattern = "suspicious" if suspicious else "normal"

        world.add("telemetry", {
            "id": new_id("TEL"), "mission_id": mission_id, "machine_id": machine_id,
            "operator_id": operator_id, "timestamp": iso(ts),
            "engine_hours": round(machine["engine_hours"] + i * 0.2, 1),
            "fuel_used_l": round(cum_fuel, 1), "load_cycles": cum_cycles,
            "idle_minutes": round(idle_tick, 1), "seatbelt_status": seatbelt,
            "occupancy_signal": occupancy, "machine_speed_kph": speed,
            "machine_moving": int(moving), "control_smoothness_score": control_smoothness,
            "safety_alert_triggered": safety_alert, "safety_signal_pattern": pattern,
        })
    machine["engine_hours"] += duration_min / 60.0

    # --- quality causal chain ---
    elevation_error = round(1.0 + soil_moisture * 4.0 + max(0, 0.6 - confidence) * 6.0 + rng.uniform(-0.5, 0.5), 2)
    surface_variance = round(0.05 + soil_moisture * 0.2 + max(0, 0.6 - confidence) * 0.25 + rng.uniform(-0.02, 0.02), 3)
    pass_count = rng.randint(2, 5)
    if force_on_time_low_quality:
        elevation_error = round(elevation_error + rng.uniform(2.5, 4.0), 2)
        surface_variance = round(surface_variance + rng.uniform(0.08, 0.15), 3)
        duration_min = naive_base * 1.02 + rng.uniform(-2, 2)  # stays on schedule, on purpose

    for i in range(2):
        ts = start_time + timedelta(minutes=seg * (2 + i))
        world.add("quality_observation", {
            "id": new_id("QO"), "mission_id": mission_id, "timestamp": iso(ts),
            "elevation_error_cm": round(elevation_error * (0.7 + 0.3 * i), 2),
            "pass_count": pass_count, "surface_variance": round(surface_variance * (0.7 + 0.3 * i), 3),
        })

    quality_score = round(max(0.0, min(1.0, 1 - (elevation_error / 15.0) - (surface_variance / 1.2))), 2)
    rework_flag = 1 if quality_score < 0.55 else 0

    dominant_reason = "none"
    contributions = {
        "truck": idle_from_truck,
        "weather": soil_moisture * 15,
        "operator": max(0, 0.6 - confidence) * 20,
        "machine": max(0, 85 - health_pct) * 0.5,
    }
    if max(contributions.values()) > 2:
        dominant_reason = max(contributions, key=contributions.get)

    world.add("outcome", {
        "id": new_id("OUT"), "mission_id": mission_id,
        "actual_duration_min": round(duration_min, 1), "actual_fuel_l": round(cum_fuel, 1),
        "quantity_completed": round(objective_qty * rng.uniform(0.94, 1.0), 1),
        "quality_score": quality_score, "rework_flag": rework_flag,
        "safety_event_count": sum(1 for t in world.tables["telemetry"] if t["mission_id"] == mission_id and t["safety_alert_triggered"]),
        "delay_reason": dominant_reason,
    })


# ----------------------------------------------------------------------------
# Named demo scenarios (Architecture.md §5)
# ----------------------------------------------------------------------------

def seed_named_scenarios(world, rng, project_id, zones, operators, machines, machines_meta, start_time):
    # FALSE_IDLE — truck absent, operator behaves normally, idle spikes for external reasons.
    simulate_mission(world, rng, mission_id="MISSION-FALSE-IDLE", project_id=project_id,
                      zone_id=zones[1], zones_soil=None, task_type="Trenching", weather="Cloudy",
                      operator_id=operators[0], machine_id=machines[0], machines_meta=machines_meta,
                      start_time=start_time, scenario_tag="FALSE_IDLE", force_truck_absent=True)

    # ON_TIME_LOW_QUALITY — duration on schedule, quality degrading underneath.
    simulate_mission(world, rng, mission_id="MISSION-ON-TIME-LOW-QUALITY", project_id=project_id,
                      zone_id=zones[1], zones_soil=None, task_type="Grading", weather="Rainy",
                      operator_id=operators[1], machine_id=machines[1], machines_meta=machines_meta,
                      start_time=start_time, scenario_tag="ON_TIME_LOW_QUALITY",
                      force_on_time_low_quality=True)

    # OPERATOR_CONTEXT_MISMATCH — strong general operator, zero evidence in this exact context.
    simulate_mission(world, rng, mission_id="MISSION-OPERATOR-CONTEXT-MISMATCH", project_id=project_id,
                      zone_id=zones[0], zones_soil=None, task_type="Earth Excavation", weather="Rainy",
                      operator_id=operators[2], machine_id=machines[2], machines_meta=machines_meta,
                      start_time=start_time, scenario_tag="OPERATOR_CONTEXT_MISMATCH",
                      force_operator_cold_start=True)

    # WHAT_IF_RECOVERY — truck-dominated delay, large recoverable fraction if a truck is added.
    simulate_mission(world, rng, mission_id="MISSION-WHAT-IF-RECOVERY", project_id=project_id,
                      zone_id=zones[2], zones_soil=None, task_type="Material Loading", weather="Sunny",
                      operator_id=operators[3], machine_id=machines[3], machines_meta=machines_meta,
                      start_time=start_time, scenario_tag="WHAT_IF_RECOVERY", force_truck_absent=True,
                      quantity_scale=1.3)

    return {"MISSION-FALSE-IDLE", "MISSION-ON-TIME-LOW-QUALITY",
            "MISSION-OPERATOR-CONTEXT-MISMATCH", "MISSION-WHAT-IF-RECOVERY"}


# ----------------------------------------------------------------------------
# Bulk random-but-causal missions
# ----------------------------------------------------------------------------

def seed_bulk_missions(world, rng, project_id, zones, operators, machines, machines_meta, n, start_time):
    for i in range(n):
        mission_id = new_id("MSN")
        task_type = rng.choice(TASK_TYPES)
        weather = rng.choices(WEATHER_OPTIONS, weights=[0.4, 0.25, 0.2, 0.15])[0]
        operator_id = rng.choice(operators)
        machine_id = rng.choice(machines)
        zone_id = rng.choice(zones)
        t = start_time + timedelta(hours=rng.randint(1, 400))
        simulate_mission(world, rng, mission_id=mission_id, project_id=project_id, zone_id=zone_id,
                          zones_soil=None, task_type=task_type, weather=weather, operator_id=operator_id,
                          machine_id=machine_id, machines_meta=machines_meta, start_time=t)


# ----------------------------------------------------------------------------
# Persistence
# ----------------------------------------------------------------------------

def write_csvs(world: World, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    for table, rows in world.tables.items():
        path = os.path.join(out_dir, f"{table}.csv")
        if not rows:
            continue
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def load_sqlite(world: World, db_path: str, schema_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    with open(schema_path) as f:
        conn.executescript(f.read())
    for table, rows in world.tables.items():
        if not rows:
            continue
        cols = list(rows[0].keys())
        placeholders = ",".join(["?"] * len(cols))
        sql = f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})"
        conn.executemany(sql, [[r[c] for c in cols] for r in rows])
    conn.commit()
    return conn


def sanity_check(conn):
    cur = conn.cursor()
    print("\n--- Row counts ---")
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    for table in tables:
        n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:32s} {n}")

    print("\n--- Named scenario check ---")
    for mid in ["MISSION-FALSE-IDLE", "MISSION-ON-TIME-LOW-QUALITY",
                "MISSION-OPERATOR-CONTEXT-MISMATCH", "MISSION-WHAT-IF-RECOVERY"]:
        m = cur.execute("SELECT task_type, naive_estimated_time_min FROM mission WHERE id=?", (mid,)).fetchone()
        o = cur.execute("SELECT actual_duration_min, delay_reason, quality_score FROM outcome WHERE mission_id=?", (mid,)).fetchone()
        assert m is not None and o is not None, f"missing rows for {mid}"
        print(f"{mid:34s} naive={m[1]:>5.0f}min  actual={o[0]:>6.1f}min  reason={o[1]:<9s} quality={o[2]}")

    # FALSE_IDLE assertion: idle should be nontrivial and delay_reason should be 'truck'
    r = cur.execute("""SELECT SUM(idle_minutes) FROM telemetry WHERE mission_id='MISSION-FALSE-IDLE'""").fetchone()[0]
    reason = cur.execute("SELECT delay_reason FROM outcome WHERE mission_id='MISSION-FALSE-IDLE'").fetchone()[0]
    assert r and r > 5, "FALSE_IDLE scenario did not produce a real idle spike"
    assert reason == "truck", f"FALSE_IDLE dominant reason expected 'truck', got '{reason}'"

    # ON_TIME_LOW_QUALITY assertion: duration close to naive baseline, quality below threshold
    naive, actual = cur.execute(
        "SELECT m.naive_estimated_time_min, o.actual_duration_min FROM mission m JOIN outcome o ON o.mission_id=m.id "
        "WHERE m.id='MISSION-ON-TIME-LOW-QUALITY'").fetchone()
    q = cur.execute("SELECT quality_score, rework_flag FROM outcome WHERE mission_id='MISSION-ON-TIME-LOW-QUALITY'").fetchone()
    assert abs(actual - naive) / naive < 0.15, "ON_TIME_LOW_QUALITY drifted off schedule too much"
    assert q[0] < 0.75, "ON_TIME_LOW_QUALITY quality_score not actually degraded"

    print("\nAll named-scenario assertions passed.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="./seed")
    ap.add_argument("--db", default="./seed/catiq.db")
    ap.add_argument("--schema", default="./schema.sql")
    ap.add_argument("--missions", type=int, default=200)
    args = ap.parse_args()

    rng = random.Random(RNG_SEED)
    world = World()

    project_id, zones, operators, machines = build_reference_data(world, rng)
    machines_meta = {m["id"]: {"age_years": m["age_years"], "engine_hours": rng.uniform(200, 6000)}
                      for m in world.tables["machine"]}

    # deliberately leave a few (operator, task, weather-bucket) combos at zero evidence
    cold_start_pairs = {(operators[2], "Earth Excavation", "adverse")}
    build_operator_evidence(world, rng, operators, cold_start_pairs)

    start_time = datetime(2026, 9, 1, 8, 0, 0)
    named_ids = seed_named_scenarios(world, rng, project_id, zones, operators, machines, machines_meta, start_time)
    seed_bulk_missions(world, rng, project_id, zones, operators, machines, machines_meta,
                        n=args.missions, start_time=start_time)

    os.makedirs(args.out, exist_ok=True)
    write_csvs(world, args.out)
    conn = load_sqlite(world, args.db, args.schema)
    sanity_check(conn)
    conn.close()

    print(f"\nDone. {sum(len(v) for v in world.tables.values())} rows across {len(world.tables)} tables.")
    print(f"CSV export: {args.out}")
    print(f"SQLite DB : {args.db}")


if __name__ == "__main__":
    main()
