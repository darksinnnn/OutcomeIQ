"""
CAT OutcomeIQ — FastAPI Application Entrypoint.

Mission Intelligence Loop for Connected Operations.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.mission_contract import router as mission_contract_router
from backend.app.api.time_model import router as time_model_router
from backend.app.api.reality_engine import router as reality_engine_router
from backend.app.api.root_cause import router as root_cause_router
from backend.app.api.outcome_guardian import router as outcome_guardian_router
from backend.app.api.what_if import router as what_if_router
from backend.app.api.live_feed import router as live_feed_router
from backend.app.api.overview import router as overview_router

app = FastAPI(
    title="CAT OutcomeIQ — Mission Intelligence Loop",
    description="Context-aware reasoning and outcome assurance above connected-machine telemetry.",
    version="1.0.0",
)

# Enable CORS for local development and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All 6 Reasoning Modules + Data & Streaming Routers
app.include_router(mission_contract_router)
app.include_router(time_model_router)
app.include_router(reality_engine_router)
app.include_router(root_cause_router)
app.include_router(outcome_guardian_router)
app.include_router(what_if_router)
app.include_router(live_feed_router)
app.include_router(overview_router)


@app.get("/", tags=["System"])
async def root():
    """Root status endpoint."""
    return {
        "service": "CAT OutcomeIQ",
        "status": "healthy",
        "version": "1.0.0",
        "description": "Mission Intelligence Loop",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": "OutcomeIQ",
        "version": "1.0.0",
    }


@app.get("/api/ping", tags=["System"])
async def ping():
    """Quick ping endpoint for frontend connectivity check."""
    return {
        "status": "ok",
        "message": "OutcomeIQ mission intelligence loop active",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
