# Spectrace API

Firmware security analysis API powered by OpenAI LLM.

## Features

- **Code Analysis**: Compare firmware versions and detect security issues
- **Specification Analysis**: Compare specification changes
- **Compliance Validation**: Ensure code matches specifications
- **Security Focus**: Detects credentials, network calls, memory issues

## Quick Start

1. **Install**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Run**
   ```bash
   uvicorn main:app --reload
   ```

4. **Test**
   ```bash
   pytest tests/ -v
   # OR use the fast test runner
   python run_tests.py
   ```

## API Endpoints

### Compare Code
```bash
POST /api/v1/compare-code
```
```json
{
  "old_code": "assembly code v1",
  "new_code": "assembly code v2", 
  "firmware_type": "ATmega328P"
}
```

### Compare Specifications  
```bash
POST /api/v1/compare-specs
```
```json
{
  "old_spec": "specification v1",
  "new_spec": "specification v2"
}
```

### Validate Compliance
```bash
POST /api/v1/validate-compliance
```
```json
{
  "code_analysis": {...},
  "spec_analysis": {...}
}
```

## Example Usage

```python
import requests

# Compare firmware code
payload = {
    "old_code": "ldi r16, 0x01\nout PORTB, r16",
    "new_code": "ldi r16, 0x02\nout PORTB, r16"
}

response = requests.post("http://localhost:8000/api/v1/compare-code", json=payload)
result = response.json()

print(f"Changes: {len(result['differences'])}")
print(f"Security issues: {len(result['security_findings'])}")
print(f"Risk: {result['risk_assessment']}")
```

## Project Structure

```
api/
├── main.py              # FastAPI app
├── schemas.py           # Data models  
├── client.py            # OpenAI client
├── routes/code_routes.py # Endpoints
├── services/            # Analysis services
├── tests/               # Unit tests
└── requirements.txt     # Dependencies
```
