# Spectrace API

> **Firmware Security & Specification Change Analysis Platform**
>
> Automated code, specification, and compliance analysis for firmware projects, powered by OpenAI LLMs.

---

## Overview

Spectrace is a FastAPI-based backend for analyzing firmware code and technical specifications, detecting changes, security issues, and validating compliance between code and documentation/specs. It leverages OpenAI LLMs for deep analysis and provides a robust API for integration and automation.

---

## Features

- **Firmware Code Comparison**: Detects line-by-line changes, security issues, and risk levels between firmware versions.
- **Specification Comparison**: Analyzes changes, new/removed features, and behavioral/security impacts between specification versions.
- **Compliance Validation**: Checks if code changes are reflected in specifications and vice versa, scoring overall compliance.
- **Security Analysis**: Flags hardcoded credentials, network calls, memory issues, privilege escalation, and more.
- **Fast Mocked Testing**: All tests run quickly using mocks—no LLM calls required for CI.

---

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**
   - Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`.
   - Or set the variable directly:
     ```bash
     $env:OPENAI_API_KEY="your-openai-key"   # PowerShell
     # or
     export OPENAI_API_KEY="your-openai-key" # Bash
     ```

3. **Run the API**
   ```bash
   uvicorn main:app --reload
   # or
   python -m uvicorn main:app --reload
   ```

4. **Run tests**
   ```bash
   pytest tests/ -v
   # or fast test runner
   python run_tests.py
   ```

---

## API Specification

### 1. Compare Firmware Code

**POST** `/api/v1/compare-code`

**Request:**
```json
{
  "old_code": "...assembly or firmware code v1...",
  "new_code": "...assembly or firmware code v2...",
  "analysis_depth": "detailed",         // optional: basic|detailed|comprehensive
  "firmware_type": "ATmega328P"         // optional
}
```

**Response:**
```json
{
  "success": true,
  "differences": [ ... ],
  "security_findings": [ ... ],
  "risk_assessment": "low|medium|high|critical",
  "change_summary": { ... },
  "recommendations": [ ... ],
  "analysis_metadata": { ... }
}
```

---

### 2. Compare Specifications

**POST** `/api/v1/compare-specs`

**Request:**
```json
{
  "old_spec": "...specification v1...",
  "new_spec": "...specification v2..."
}
```

**Response:**
```json
{
  "success": true,
  "differences": [ ... ],
  "new_features": [ ... ],
  "removed_features": [ ... ],
  "behavioral_changes": [ ... ],
  "change_summary": { ... },
  "recommendations": [ ... ],
  "analysis_metadata": { ... }
}
```

---

### 3. Validate Compliance

**POST** `/api/v1/validate-compliance`

**Request:**
```json
{
  "code_analysis": { ... },
  "spec_analysis": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "compliance_status": "compliant|partially_compliant|non_compliant",
  "mismatches": [ ... ],
  "matches": [ ... ],
  "compliance_score": 1.0,
  "summary": { ... },
  "recommendations": [ ... ],
  "analysis_metadata": { ... }
}
```

---

## Example: Compare Firmware Code

```python
import requests

payload = {
    "old_code": "; Firmware v1 - LED Blink\n...",
    "new_code": "; Firmware v2 - LED Blink (Timer-based)\n...",
    "firmware_type": "ATmega328P"
}

resp = requests.post("http://localhost:8000/api/v1/compare-code", json=payload)
print(resp.json())
```

---

## Project Structure

```
api/
├── main.py                # FastAPI app entrypoint
├── client.py              # OpenAI API client
├── prompts.py             # Prompt templates for LLM
├── schemas.py             # Pydantic models & API schemas
├── routes/
│   └── code_routes.py     # All API endpoints
├── services/
│   ├── code_analyzer.py   # Firmware code analysis logic
│   ├── spec_analyzer.py   # Specification analysis logic
│   └── compliance_analyzer.py # Compliance validation logic
├── files/                 # Example firmware/spec files
├── tests/                 # Unit tests (mocked, fast)
├── requirements.txt       # Python dependencies
├── run_tests.py           # Fast test runner
└── .env.example           # Example environment config
```

---

## License

MIT License. See `LICENSE` file.
