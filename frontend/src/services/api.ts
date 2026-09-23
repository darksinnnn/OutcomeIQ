import {
  Mission,
  PredictionEnvelope,
  MissionContractValue,
  RealityEngineValue,
  TimeModelValue,
  RootCauseValue,
  OutcomeGuardianValue,
  WhatIfValue,
  Operator,
  OperatorCapabilityRecord,
  MachineHealth,
  TelemetryTick,
  CompositeLiveOperation,
} from '../types';

const API_BASE = '/api';

/**
 * Helper to fetch API with fallback to structured synthetic development data
 */
async function fetchWithFallback<T>(url: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${url}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`[API Fallback] ${url} unavailable, using structured synthetic dev payload.`, err);
    return fallback;
  }
}

/**
 * Structured Seeded Demo Missions
 */
export const SEEDED_MISSIONS: Mission[] = [
  {
    id: 'MIS-101',
    project_id: 'PRJ-CAT-2026',
    zone_id: 'ZONE-NORTH-CUT',
    task_type: 'Bulk Excavation & Loading',
    objective_quantity: 450,
    objective_unit: 'm3',
    naive_estimated_time_min: 180,
    deadline: '2026-09-24T18:00:00Z',
    assigned_operator_id: 'OP-101',
    assigned_machine_id: 'MAC-CAT-349',
    status: 'in_progress',
    scenario_tag: 'FALSE_IDLE',
    start_time: '2026-09-23T08:00:00Z',
  },
  {
    id: 'MIS-102',
    project_id: 'PRJ-CAT-2026',
    zone_id: 'ZONE-EAST-TRENCH',
    task_type: 'Wet Slope Trenching',
    objective_quantity: 120,
    objective_unit: 'm',
    naive_estimated_time_min: 240,
    deadline: '2026-09-24T20:00:00Z',
    assigned_operator_id: 'OP-102',
    assigned_machine_id: 'MAC-CAT-336',
    status: 'in_progress',
    scenario_tag: 'OPERATOR_CONTEXT_MISMATCH',
    start_time: '2026-09-23T09:30:00Z',
  },
  {
    id: 'MIS-103',
    project_id: 'PRJ-CAT-2026',
    zone_id: 'ZONE-SOUTH-GRADE',
    task_type: 'Subgrade Compaction & Elev',
    objective_quantity: 850,
    objective_unit: 'm2',
    naive_estimated_time_min: 300,
    deadline: '2026-09-24T17:00:00Z',
    assigned_operator_id: 'OP-103',
    assigned_machine_id: 'MAC-CAT-14M',
    status: 'quality_alert',
    scenario_tag: 'ON_TIME_LOW_QUALITY',
    start_time: '2026-09-23T07:00:00Z',
  },
  {
    id: 'MIS-104',
    project_id: 'PRJ-CAT-2026',
    zone_id: 'ZONE-WEST-HAUL',
    task_type: 'Rock Quarry Stockpiling',
    objective_quantity: 600,
    objective_unit: 'tons',
    naive_estimated_time_min: 210,
    deadline: '2026-09-24T19:00:00Z',
    assigned_operator_id: 'OP-104',
    assigned_machine_id: 'MAC-CAT-988',
    status: 'in_progress',
    scenario_tag: 'WHAT_IF_RECOVERY',
    start_time: '2026-09-23T10:00:00Z',
  },
];

export const outcomeIQApi = {
  // System Health
  async getPing(): Promise<{ status: string; message: string }> {
    return fetchWithFallback('/ping', {
      status: 'ok',
      message: 'OutcomeIQ mission intelligence loop active (Dev Adapter)',
    });
  },

  // Missions
  async getMissions(): Promise<Mission[]> {
    return fetchWithFallback('/missions', SEEDED_MISSIONS);
  },

  // Composite Live Operation
  async getLiveOperationComposite(missionId: string): Promise<CompositeLiveOperation> {
    const isFalseIdle = missionId === 'MIS-101';
    const isQualityAlert = missionId === 'MIS-103';
    const isOperatorMismatch = missionId === 'MIS-102';

    const fallback: CompositeLiveOperation = {
      mission_id: missionId,
      contract: {
        value: {
          mission_id: missionId,
          task_type: isFalseIdle ? 'Bulk Excavation' : isQualityAlert ? 'Grade Compaction' : 'Trenching',
          objective_quantity: isFalseIdle ? 450 : 850,
          objective_unit: isFalseIdle ? 'm3' : 'm2',
          deadline: '2026-09-24T18:00:00Z',
          quality_tolerance_cm: 2.5,
          safety_constraints: { max_speed_kph: 25, seatbelt_required: true },
          assigned_operator_id: isFalseIdle ? 'OP-101' : 'OP-103',
          assigned_machine_id: isFalseIdle ? 'MAC-CAT-349' : 'MAC-CAT-14M',
          assigned_resources: ['Cat 349 Excavator', '3x 777 Haul Trucks', 'GPS Base Station'],
          is_valid: true,
          validation_issues: [],
        },
        confidence: 0.98,
        evidence: [
          { factor: 'Contract Verification', weight_or_probability: 0.98, detail: 'Objective & safety constraints parsed cleanly from work order #WO-9921.' }
        ],
      },
      reality_engine: {
        value: {
          explanation_class: isFalseIdle ? 'external_workflow' : isOperatorMismatch ? 'operator_variation' : 'weather_condition',
          headline: isFalseIdle
            ? 'Idle spike (24 min) caused by Haul Truck queue bottleneck'
            : isOperatorMismatch
            ? 'Control variance detected in high-moisture clay trenching'
            : 'Operational trajectory aligned with baseline targets',
          primary_driver: isFalseIdle ? 'Haul Truck Absence (7 min arrival gap)' : 'Soil Moisture (34% wet clay)',
          workflow_context: {
            truck_present: !isFalseIdle,
            queue_length: isFalseIdle ? 0 : 3,
            material_available: true,
            weather: isOperatorMismatch ? 'Rain' : 'Clear',
          },
        },
        confidence: isFalseIdle ? 0.92 : 0.84,
        evidence: [
          { factor: 'Telematics Seatbelt & Occupancy', weight_or_probability: 0.95, detail: 'Operator seatbelt fastened, engine running at low RPM, operator in seat continuously.' },
          { factor: 'Workflow Event Stream', weight_or_probability: 0.91, detail: isFalseIdle ? 'Zero haul trucks present in loader radius for 18 consecutive minutes.' : 'Haul trucks arriving on 4 min cadence.' },
          { factor: 'Operator Control Smoothness', weight_or_probability: 0.88, detail: 'Smoothness index 91/100 (normal hydraulic modulation).' },
        ],
      },
      time_model: {
        value: {
          p10_min: isFalseIdle ? 165 : 190,
          p50_min: isFalseIdle ? 198 : 220,
          p90_min: isFalseIdle ? 245 : 260,
          expected_fuel_l: 142.5,
          fuel_range_min_l: 130,
          fuel_range_max_l: 160,
          naive_baseline_min: 180,
          time_saved_vs_baseline_min: -18,
        },
        confidence: 0.86,
        evidence: [
          { factor: 'Operator Context Evidence', weight_or_probability: 0.85, detail: 'OP-101 has 38 completed excavation missions in dry soil (avg delta +2%).' },
          { factor: 'Machine Hydraulic Health', weight_or_probability: 0.92, detail: 'Cat 349 hydraulic pressure baseline 97%.' },
          { factor: 'Environmental Moisture', weight_or_probability: 0.78, detail: 'Soil moisture 18% (optimal compaction range).' },
        ],
      },
      outcome_guardian: {
        value: {
          signals: {
            time: isFalseIdle ? 'amber' : 'green',
            safety: 'green',
            productivity: isFalseIdle ? 'amber' : 'green',
            fuel: 'green',
            quality: isQualityAlert ? 'red' : 'green',
            acceptance: isQualityAlert ? 'amber' : 'green',
          },
          rework_probability: isQualityAlert ? 0.38 : 0.04,
          quality_observation: {
            elevation_error_cm: isQualityAlert ? 4.8 : 0.8,
            surface_variance: isQualityAlert ? 0.35 : 0.08,
            pass_count: isQualityAlert ? 2 : 4,
          },
          headline: isQualityAlert
            ? 'On schedule, but subgrade elevation deviation exceeds +2.5cm tolerance'
            : isFalseIdle
            ? 'Task time drifting (+18 min) due to truck shortage; quality & safety green'
            : 'All 6 mission outcome signals green and on track',
        },
        confidence: isQualityAlert ? 0.94 : 0.91,
        evidence: [
          { factor: 'GPS Elevation Sensor', weight_or_probability: 0.94, detail: isQualityAlert ? 'Pass 2 elevation variance +4.8cm at Grid E-4.' : 'Pass 4 surface tolerance ±0.8cm.' },
          { factor: 'Safety Telemetry Audit', weight_or_probability: 0.99, detail: '0 speed violations, 100% seatbelt compliance.' },
        ],
      },
      telemetry_window: Array.from({ length: 15 }, (_, i) => ({
        timestamp: new Date(Date.now() - (15 - i) * 60000).toISOString(),
        engine_hours: 1420.5 + i * 0.016,
        fuel_used_l: 120 + i * 0.4,
        load_cycles: isFalseIdle && i > 5 && i < 12 ? 8 : 8 + i * 2,
        idle_minutes: isFalseIdle && i > 5 ? (i - 5) * 2 : Math.floor(i * 0.2),
        seatbelt_status: true,
        machine_moving: !(isFalseIdle && i > 5),
        machine_speed_kph: isFalseIdle && i > 5 ? 0 : 14.2,
        control_smoothness_score: 92,
        safety_alert_triggered: false,
        safety_signal_pattern: 'normal_operation',
      })),
    };

    return fetchWithFallback(`/composite/live-operation/${missionId}`, fallback);
  },

  // Mission Contract
  async getMissionContract(missionId: string): Promise<PredictionEnvelope<MissionContractValue>> {
    const liveComp = await this.getLiveOperationComposite(missionId);
    return liveComp.contract;
  },

  // Reality Engine
  async getRealityEngine(missionId: string): Promise<PredictionEnvelope<RealityEngineValue>> {
    const liveComp = await this.getLiveOperationComposite(missionId);
    return liveComp.reality_engine;
  },

  // Time Model
  async getTimeModel(missionId: string): Promise<PredictionEnvelope<TimeModelValue>> {
    const liveComp = await this.getLiveOperationComposite(missionId);
    return liveComp.time_model;
  },

  // Root Cause Engine
  async getRootCause(missionId: string): Promise<PredictionEnvelope<RootCauseValue>> {
    const isFalseIdle = missionId === 'MIS-101';
    const isOperatorMismatch = missionId === 'MIS-102';

    const fallback: PredictionEnvelope<RootCauseValue> = {
      value: {
        deviation_min: isFalseIdle ? 18 : isOperatorMismatch ? 32 : 5,
        primary_cause: isFalseIdle
          ? 'External Workflow (Haul Truck Availability)'
          : isOperatorMismatch
          ? 'Operator Technique Mismatch (Wet Clay Context)'
          : 'Normal Operational Variance',
        contributors: isFalseIdle
          ? [
              { cause: 'Truck Availability & Haul Cycle Lag', cause_category: 'external_workflow', probability: 0.72, evidence: '777 Haul Truck queue dropped to 0 for 22 minutes.' },
              { cause: 'Soil Resistance & Moisture', cause_category: 'weather_condition', probability: 0.18, evidence: 'Soil moisture spike to 28% increased cycle duration by 1.2s.' },
              { cause: 'Operator Technique Variation', cause_category: 'operator_variation', probability: 0.08, evidence: 'Smoothness score stable at 91/100; no technique deviation observed.' },
              { cause: 'Machine Hydraulic Lag', cause_category: 'machine_condition', probability: 0.02, evidence: 'Hydraulic pressure nominal at 97%.' },
            ]
          : [
              { cause: 'Operator Experience Gap in Wet Clay Context', cause_category: 'operator_variation', probability: 0.64, evidence: 'OP-102 has 2 prior missions in wet clay vs 45 in dry soil.' },
              { cause: 'Rain & Clay Silt Saturation', cause_category: 'weather_condition', probability: 0.26, evidence: 'Rainfall 12mm/hr increased material adhesion in bucket.' },
              { cause: 'Excavator Bucket Teeth Wear', cause_category: 'machine_condition', probability: 0.10, evidence: 'Tool wear estimated at 64% lifespan.' },
            ],
      },
      confidence: 0.89,
      evidence: [
        { factor: 'Workflow Sensor Signals', weight_or_probability: 0.72, detail: 'RFID haul gate sensors logged 3 trucks delayed at crusher loop.' },
        { factor: 'Operator Passport Context Baseline', weight_or_probability: 0.85, detail: 'Operator technique parameters matched historical baseline for dry excavation.' },
        { factor: 'Telemetry Smoothness Stream', weight_or_probability: 0.91, detail: 'Hydraulic stick/boom joystick variance within 1.2 sigma.' },
      ],
    };

    return fetchWithFallback(`/root-cause/${missionId}`, fallback);
  },

  // Outcome Guardian
  async getOutcomeGuardian(missionId: string): Promise<PredictionEnvelope<OutcomeGuardianValue>> {
    const liveComp = await this.getLiveOperationComposite(missionId);
    return liveComp.outcome_guardian;
  },

  // What-If Lab Simulation
  async simulateWhatIf(missionId: string, assumption: any): Promise<PredictionEnvelope<WhatIfValue>> {
    const fallback: PredictionEnvelope<WhatIfValue> = {
      value: {
        assumption_changed: assumption,
        description: assumption.add_truck
          ? 'Intervention: Dispatch +1 777 Haul Truck to Zone North'
          : assumption.operator_id
          ? 'Intervention: Swap Operator to OP-101 (Master Excavator Cert)'
          : 'Intervention: Route optimization around soft clay patch',
        before: {
          p10_min: 175,
          p50_min: 198,
          p90_min: 245,
          expected_fuel_l: 142.5,
          fuel_range_min_l: 130,
          fuel_range_max_l: 160,
          naive_baseline_min: 180,
          time_saved_vs_baseline_min: -18,
        },
        after: {
          p10_min: 155,
          p50_min: 172,
          p90_min: 195,
          expected_fuel_l: 136.0,
          fuel_range_min_l: 125,
          fuel_range_max_l: 148,
          naive_baseline_min: 180,
          time_saved_vs_baseline_min: 8,
        },
        time_delta_min: -26,
        fuel_delta_l: -6.5,
        quality_risk_delta_pct: -12,
      },
      confidence: 0.91,
      evidence: [
        { factor: 'Re-simulation over Time Model Quantiles', weight_or_probability: 0.91, detail: 'Adding 1 truck reduces loader waiting queue time from 18 min to 2 min per 100m3.' },
        { factor: 'Operator Capability Feature Swap', weight_or_probability: 0.88, detail: 'Feature vector updated with high-confidence wet trenching evidence.' },
      ],
    };

    try {
      const res = await fetch(`${API_BASE}/what-if/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mission_id: missionId, assumption }),
      });
      if (!res.ok) throw new Error();
      return await res.json();
    } catch {
      return fallback;
    }
  },

  // Operator Passport
  async getOperatorPassport(operatorId: string): Promise<{ operator: Operator; evidence_count: number; evidence_records: OperatorCapabilityRecord[] }> {
    const fallback = {
      operator: {
        id: operatorId,
        name: operatorId === 'OP-101' ? 'Marcus Vance' : operatorId === 'OP-102' ? 'Elena Rostova' : 'David Chen',
        experience_years: operatorId === 'OP-101' ? 12 : 6,
        certifications: ['Master Excavator Level III', 'GPS Grade Control Expert', 'Heavy Mining Safety'],
      },
      evidence_count: 4,
      evidence_records: [
        {
          id: 'EVI-801',
          operator_id: operatorId,
          task_type: 'Bulk Excavation',
          material_type: 'Dry Gravel & Rock',
          weather_condition: 'Clear / Dry',
          sample_count: 42,
          success_count: 40,
          avg_time_delta_pct: -3.2,
          avg_quality_success_pct: 96.8,
          confidence: 0.94,
          last_verified_at: '2026-09-21T16:00:00Z',
        },
        {
          id: 'EVI-802',
          operator_id: operatorId,
          task_type: 'Subgrade Finishing',
          material_type: 'Crushed Limestone',
          weather_condition: 'Clear',
          sample_count: 28,
          success_count: 26,
          avg_time_delta_pct: 0.5,
          avg_quality_success_pct: 94.2,
          confidence: 0.88,
          last_verified_at: '2026-09-18T14:30:00Z',
        },
        {
          id: 'EVI-803',
          operator_id: operatorId,
          task_type: 'Wet Slope Trenching',
          material_type: 'Wet Clay & Silt',
          weather_condition: 'Rain / Heavy Moisture',
          sample_count: 4,
          success_count: 2,
          avg_time_delta_pct: 14.8,
          avg_quality_success_pct: 72.0,
          confidence: 0.58, // Low confidence due to small sample size!
          last_verified_at: '2026-09-10T11:15:00Z',
        },
        {
          id: 'EVI-804',
          operator_id: operatorId,
          task_type: 'Rock Stockpiling',
          material_type: 'Blasted Granite',
          weather_condition: 'High Wind / Dust',
          sample_count: 18,
          success_count: 17,
          avg_time_delta_pct: -1.8,
          avg_quality_success_pct: 95.0,
          confidence: 0.85,
          last_verified_at: '2026-09-05T09:00:00Z',
        },
      ],
    };

    return fetchWithFallback(`/operators/${operatorId}/passport`, fallback);
  },
};
