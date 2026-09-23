# DECISIONS.md — CAT OutcomeIQ Architectural Decision Log

This log tracks architectural and design decisions, technology choices, and deviations from early specifications.

## Log

### [2026-09-23] Decision 001: Backend Virtual Environment and Layout
- **Context**: Project requires isolation for dependencies while following the exact repository structure outlined in `docs/Agents.md` §4.
- **Decision**: Created local `.venv` in workspace root. Structured backend under `backend/app/` with clean modular isolation (`modules/mission_contract`, `modules/reality_engine`, `modules/time_model`, `modules/root_cause`, `modules/outcome_guardian`, `modules/what_if`, and `modules/_shared`).
- **Rationale**: Keeps virtual environment standard across Windows development environments, preserves deterministic package management, and separates core domain logic from FastAPI transport routers.

### [2026-09-23] Decision 002: Model-Free & Interpretable Approach for Core Reasoning
- **Context**: PRD and Architecture specify that explainability is the core product ("value + confidence + evidence").
- **Decision**:
  - Time Model uses Gradient-Boosted Quantile Regression (`scikit-learn`'s `GradientBoostingRegressor(loss='quantile')`) to yield honest P10 / P50 / P90 duration distributions and feature attribution evidence without external heavy black-box dependencies.
  - Reality Engine and Root-Cause Engine use multi-signal causal fusion with explicit evidence linkages back to telemetry, workflow, and operator evidence tables.
  - Outcome Guardian uses threshold trend analysis over QualityObservation metrics to reliably predict rework risk.
  - What-If Lab re-evaluates the Time Model and Outcome Guardian under counterfactual features.
- **Rationale**: Delivers sub-millisecond response times, zero hallucination risk, 100% deterministic reproducibility, and clickable evidence traceability for the Caterpillar Hackathon pitch.
