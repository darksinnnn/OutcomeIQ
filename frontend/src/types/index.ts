/**
 * CAT OutcomeIQ — TypeScript API and Domain Types.
 * Strictly aligned with Architecture.md schemas and module payloads.
 */

export interface EvidenceFactor {
  factor: string;
  weight_or_probability: number;
  detail: string;
}

export interface PredictionEnvelope<T = any> {
  value: T;
  confidence: number; // 0.0 - 1.0
  evidence: EvidenceFactor[];
}

export interface Mission {
  id: string;
  project_id: string;
  zone_id: string;
  task_type: string;
  objective_quantity: number;
  objective_unit: string;
  naive_estimated_time_min: number;
  deadline: string;
  assigned_operator_id: string;
  assigned_machine_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'quality_alert';
  scenario_tag: 'FALSE_IDLE' | 'OPERATOR_CONTEXT_MISMATCH' | 'ON_TIME_LOW_QUALITY' | 'WHAT_IF_RECOVERY' | string | null;
  start_time: string;
}

export interface MissionContractInput {
  task_type: string;
  objective_quantity: number;
  objective_unit: string;
  deadline: string;
  quality_tolerance_cm: number;
  safety_max_speed_kph: number;
  assigned_operator_id: string;
  assigned_machine_id: string;
  assigned_resources: string[];
}

export interface MissionContractValue {
  mission_id: string;
  task_type: string;
  objective_quantity: number;
  objective_unit: string;
  deadline: string;
  quality_tolerance_cm: number;
  safety_constraints: {
    max_speed_kph: number;
    seatbelt_required: boolean;
  };
  assigned_operator_id: string;
  assigned_machine_id: string;
  assigned_resources: string[];
  is_valid: boolean;
  validation_issues: string[];
}

export interface RealityEngineValue {
  explanation_class: 'external_workflow' | 'operator_variation' | 'machine_condition' | 'weather_condition' | 'unknown';
  headline: string;
  primary_driver: string;
  workflow_context: {
    truck_present: boolean;
    queue_length: number;
    material_available: boolean;
    weather: string;
  };
}

export interface TimeModelValue {
  p10_min: number;
  p50_min: number;
  p90_min: number;
  expected_fuel_l: number;
  fuel_range_min_l: number;
  fuel_range_max_l: number;
  naive_baseline_min: number;
  time_saved_vs_baseline_min: number;
}

export interface RootCauseContributor {
  cause: string;
  cause_category: 'external_workflow' | 'operator_variation' | 'machine_condition' | 'weather_condition' | 'unknown';
  probability: number;
  evidence: string;
}

export interface RootCauseValue {
  deviation_min: number;
  primary_cause: string;
  contributors: RootCauseContributor[];
}

export type SignalState = 'green' | 'amber' | 'red';

export interface OutcomeGuardianValue {
  signals: {
    time: SignalState;
    safety: SignalState;
    productivity: SignalState;
    fuel: SignalState;
    quality: SignalState;
    acceptance: SignalState;
  };
  rework_probability: number;
  quality_observation: {
    elevation_error_cm: number;
    surface_variance: number;
    pass_count: number;
  };
  headline: string;
}

export interface WhatIfAssumption {
  operator_id?: string;
  add_truck?: boolean;
  weather?: string;
  route_change?: boolean;
}

export interface WhatIfValue {
  assumption_changed: WhatIfAssumption;
  description: string;
  before: TimeModelValue;
  after: TimeModelValue;
  time_delta_min: number;
  fuel_delta_l: number;
  quality_risk_delta_pct: number;
}

export interface OperatorCapabilityRecord {
  id: string;
  operator_id: string;
  task_type: string;
  material_type: string;
  weather_condition: string;
  sample_count: number;
  success_count: number;
  avg_time_delta_pct: number;
  avg_quality_success_pct: number;
  confidence: number;
  last_verified_at: string;
}

export interface Operator {
  id: string;
  name: string;
  experience_years: number;
  certifications?: string[];
}

export interface MachineHealth {
  machine_id: string;
  model: string;
  engine_hours: number;
  health_pct: number;
  hydraulic_health_pct: number;
  recent_fault_count: number;
  status: 'healthy' | 'maintenance_due' | 'critical';
}

export interface TelemetryTick {
  tick_index?: number;
  timestamp: string;
  engine_hours: number;
  fuel_used_l: number;
  load_cycles: number;
  idle_minutes: number;
  seatbelt_status: boolean;
  machine_moving: boolean;
  machine_speed_kph: number;
  control_smoothness_score: number;
  safety_alert_triggered: boolean;
  safety_signal_pattern: string;
}

export interface CompositeLiveOperation {
  mission_id: string;
  contract: PredictionEnvelope<MissionContractValue>;
  reality_engine: PredictionEnvelope<RealityEngineValue>;
  time_model: PredictionEnvelope<TimeModelValue>;
  outcome_guardian: PredictionEnvelope<OutcomeGuardianValue>;
  telemetry_window: TelemetryTick[];
}
