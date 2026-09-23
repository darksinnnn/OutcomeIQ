# OutcomeIQ — Backend

Autonomous Mission Intelligence Loop for Connected Operations.

## Quickstart

### 1. Environment Setup
```powershell
# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies (if not already installed)
pip install -r backend/requirements.txt
```

### 2. Run the API Server
```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### 3. Run Tests
```powershell
pytest backend/tests
```
