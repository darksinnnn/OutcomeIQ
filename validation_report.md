# CAT OutcomeIQ — Validation Report

**Readiness score: 100.0%**  (65/65 checks passed, 0 hard failures, 0 warnings)

| Check | Status | Detail |
|---|---|---|
| infra:/health reachable | PASS | 6ms |
| infra:/ reachable | PASS | 22ms |
| infra:/docs reachable | PASS | 2ms |
| contract:mission_contract:MISSION-FALSE-IDLE:confidence range | PASS |  |
| contract:mission_contract:MISSION-FALSE-IDLE:evidence present | PASS | 5 item(s) |
| contract:mission_contract:MISSION-ON-TIME-LOW-QUALITY:confidence range | PASS |  |
| contract:mission_contract:MISSION-ON-TIME-LOW-QUALITY:evidence present | PASS | 5 item(s) |
| contract:mission_contract:MISSION-OPERATOR-CONTEXT-MISMATCH:confidence range | PASS |  |
| contract:mission_contract:MISSION-OPERATOR-CONTEXT-MISMATCH:evidence present | PASS | 5 item(s) |
| contract:mission_contract:MISSION-WHAT-IF-RECOVERY:confidence range | PASS |  |
| contract:mission_contract:MISSION-WHAT-IF-RECOVERY:evidence present | PASS | 5 item(s) |
| contract:time_model:MISSION-FALSE-IDLE:confidence range | PASS |  |
| contract:time_model:MISSION-FALSE-IDLE:evidence present | PASS | 2 item(s) |
| time_model:MISSION-FALSE-IDLE:quantile ordering | PASS | P10=60.8 P50=69.7 P90=79.9 |
| contract:time_model:MISSION-ON-TIME-LOW-QUALITY:confidence range | PASS |  |
| contract:time_model:MISSION-ON-TIME-LOW-QUALITY:evidence present | PASS | 4 item(s) |
| time_model:MISSION-ON-TIME-LOW-QUALITY:quantile ordering | PASS | P10=36.8 P50=49.9 P90=55.0 |
| contract:time_model:MISSION-OPERATOR-CONTEXT-MISMATCH:confidence range | PASS |  |
| contract:time_model:MISSION-OPERATOR-CONTEXT-MISMATCH:evidence present | PASS | 3 item(s) |
| time_model:MISSION-OPERATOR-CONTEXT-MISMATCH:quantile ordering | PASS | P10=67.7 P50=97.9 P90=98.9 |
| contract:time_model:MISSION-WHAT-IF-RECOVERY:confidence range | PASS |  |
| contract:time_model:MISSION-WHAT-IF-RECOVERY:evidence present | PASS | 2 item(s) |
| time_model:MISSION-WHAT-IF-RECOVERY:quantile ordering | PASS | P10=34.8 P50=55.4 P90=65.2 |
| contract:reality_engine:MISSION-FALSE-IDLE:confidence range | PASS |  |
| contract:reality_engine:MISSION-FALSE-IDLE:evidence present | PASS | 3 item(s) |
| reality_engine:FALSE_IDLE:class | PASS | class=external_workflow |
| reality_engine:FALSE_IDLE:evidence mentions truck | PASS |  |
| contract:reality_engine:MISSION-ON-TIME-LOW-QUALITY:confidence range | PASS |  |
| contract:reality_engine:MISSION-ON-TIME-LOW-QUALITY:evidence present | PASS | 3 item(s) |
| contract:reality_engine:MISSION-OPERATOR-CONTEXT-MISMATCH:confidence range | PASS |  |
| contract:reality_engine:MISSION-OPERATOR-CONTEXT-MISMATCH:evidence present | PASS | 3 item(s) |
| contract:reality_engine:MISSION-WHAT-IF-RECOVERY:confidence range | PASS |  |
| contract:reality_engine:MISSION-WHAT-IF-RECOVERY:evidence present | PASS | 1 item(s) |
| contract:root_cause:MISSION-FALSE-IDLE:confidence range | PASS |  |
| contract:root_cause:MISSION-FALSE-IDLE:evidence present | PASS | 5 item(s) |
| contract:root_cause:MISSION-ON-TIME-LOW-QUALITY:confidence range | PASS |  |
| contract:root_cause:MISSION-ON-TIME-LOW-QUALITY:evidence present | PASS | 5 item(s) |
| contract:root_cause:MISSION-OPERATOR-CONTEXT-MISMATCH:confidence range | PASS |  |
| contract:root_cause:MISSION-OPERATOR-CONTEXT-MISMATCH:evidence present | PASS | 5 item(s) |
| root_cause:OPERATOR_CONTEXT_MISMATCH:top cause | PASS | contributors={'operator': 0.49, 'weather': 0.46, 'truck': 0.02, 'unknown': 0.02, 'machine': 0.01} |
| contract:root_cause:MISSION-WHAT-IF-RECOVERY:confidence range | PASS |  |
| contract:root_cause:MISSION-WHAT-IF-RECOVERY:evidence present | PASS | 5 item(s) |
| contract:outcome_guardian:MISSION-FALSE-IDLE:confidence range | PASS |  |
| contract:outcome_guardian:MISSION-FALSE-IDLE:evidence present | PASS | 4 item(s) |
| contract:outcome_guardian:MISSION-ON-TIME-LOW-QUALITY:confidence range | PASS |  |
| contract:outcome_guardian:MISSION-ON-TIME-LOW-QUALITY:evidence present | PASS | 4 item(s) |
| outcome_guardian:ON_TIME_LOW_QUALITY:time signal green | PASS |  |
| outcome_guardian:ON_TIME_LOW_QUALITY:quality/acceptance flagged | PASS | quality=red acceptance=red |
| outcome_guardian:ON_TIME_LOW_QUALITY:rework_probability present | PASS | 0.83 |
| contract:outcome_guardian:MISSION-OPERATOR-CONTEXT-MISMATCH:confidence range | PASS |  |
| contract:outcome_guardian:MISSION-OPERATOR-CONTEXT-MISMATCH:evidence present | PASS | 4 item(s) |
| contract:outcome_guardian:MISSION-WHAT-IF-RECOVERY:confidence range | PASS |  |
| contract:outcome_guardian:MISSION-WHAT-IF-RECOVERY:evidence present | PASS | 4 item(s) |
| what_if:WHAT_IF_RECOVERY:recovery shown | PASS | before=55.4 after=38.7 |
| contract:what_if:WHAT_IF_RECOVERY (add_truck):confidence range | PASS |  |
| contract:what_if:WHAT_IF_RECOVERY (add_truck):evidence present | PASS | 1 item(s) |
| mission_contract:vs_db:MISSION-FALSE-IDLE:objective_quantity matches | PASS |  |
| mission_contract:vs_db:MISSION-FALSE-IDLE:quality_tolerance matches | PASS |  |
| mission_contract:vs_db:MISSION-ON-TIME-LOW-QUALITY:objective_quantity matches | PASS |  |
| mission_contract:vs_db:MISSION-ON-TIME-LOW-QUALITY:quality_tolerance matches | PASS |  |
| mission_contract:vs_db:MISSION-OPERATOR-CONTEXT-MISMATCH:objective_quantity matches | PASS |  |
| mission_contract:vs_db:MISSION-OPERATOR-CONTEXT-MISMATCH:quality_tolerance matches | PASS |  |
| mission_contract:vs_db:MISSION-WHAT-IF-RECOVERY:objective_quantity matches | PASS |  |
| mission_contract:vs_db:MISSION-WHAT-IF-RECOVERY:quality_tolerance matches | PASS |  |
| trust_language: all live responses clean | PASS | 20 responses scanned |

## Not automated by this script — verify manually
- WebSocket live telemetry stream (`/api/telemetry/ws/{mission_id}`) — connect a client and confirm ticks arrive.
- Data-leakage review: grep `time_model` feature-building code for any reference to `outcome.*` fields — this script can't see your source, only your API responses.
- Frontend rendering of confidence + evidence on every screen (Frontend.md requirement) — this script only checks the API contract, not that the UI actually surfaces it.
