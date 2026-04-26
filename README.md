# CAD Design Validator

Validate STEP files for manufacturability issues in seconds — no CAD software required.

## What it does
Upload any `.step` file and get a JSON report flagging:
- **Overhang detection** (active) — flags faces exceeding your printable angle limit
- **Thin wall detection** (WIP)
- **Sharp edge detection** (WIP)

## Demo
Try the 3 sample files (thin wall, overhang, clean part) on the web UI.

## Run locally
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 app.py
# Open http://localhost:8080
```

## Example output
```json
{
  "status": "FAIL",
  "total_issues": 2,
  "critical": 1,
  "analysis_time_sec": 3.2,
  "confidence": 0.92,
  "risk_level": "HIGH"
}
```

## Why it matters
Catches design flaws before they hit the printer or CNC machine — reduces failed prints, saves material cost, enables automated design validation pipelines.
