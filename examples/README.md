# Examples

Clone the repository, run one command, see the pipeline produce a recommendation.

---

## Tender-001

A synthetic but realistic Indian government tender: construction of a two-lane road in Karnataka, issued by KRDCL (Karnataka Road Development Corporation Limited).

| Field | Value |
|---|---|
| Authority | KRDCL |
| Work | Two-lane road construction, Hubli–Dharwad (22.4 km) |
| Estimated value | Rs. 38.5 Crore |
| Duration | 24 months |
| Company | Apex Infrastructure Pvt Ltd |

### Files

| File | Description |
|---|---|
| `Tender-001.pdf` | The tender document (6 pages) |
| `company-profile.json` | Company profile used for qualification |
| `Tender-001-parsed.json` | Expected output from the extraction stage |
| `Tender-001-output.json` | Expected final recommendation |

### Expected recommendation

```json
{
  "recommendation": "REVIEW",
  "qualification_score": 100,
  "primary_bottleneck": "Historical Vendor Dominance",
  "confidence": 1.0,
  "confidence_reason": [
    "4 of 4 mandatory requirements verified",
    "Incumbent risk score (75) exceeds threshold — prior vendor advantage inferred from tender language"
  ]
}
```

**Why REVIEW and not BID?** Apex Infrastructure passes all four mandatory qualification requirements. The recommendation is REVIEW because the tender document references a prior KRDCL contract (Package HB-04) — a signal of incumbent advantage. Incumbent risk score = 71, which is at the threshold (70). A bid team with a direct KRDCL relationship should proceed; one without should reconsider.

---

## Run it

### Prerequisites

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# No API key required. Copy .env.example if you want to add one later.
```

### One command

```bash
python scripts/run_pipeline.py \
  --pdf examples/Tender-001/Tender-001.pdf \
  --profile examples/Tender-001/company-profile.json
```

### Expected output

```
Processing: Tender-001.pdf
Profile:    company-profile.json

============================================================
RECOMMENDATION: REVIEW
Qualification Score: 100/100
Competitive Strength: 44/100
Incumbent Risk: 75/100
Execution Risk: 13/100
Value Score: 58/100
Confidence: 1.00

Primary Bottleneck: Historical Vendor Dominance
============================================================
```

The `reasoning` field is `null` unless `ANTHROPIC_API_KEY` is set — the LLM explanation stage is skipped gracefully and the rest of the pipeline completes normally.

---

## Adding your own tender

1. Place the PDF in `data/incoming/`
2. Place the matching company profile in `data/company-profiles/<company-id>.json`
3. Run:
   ```bash
   python scripts/run_pipeline.py \
     --pdf data/incoming/your-tender.pdf \
     --profile data/company-profiles/your-company.json
   ```
4. Find the result in `data/outcomes/`

The folder watcher (`src/pipeline/watcher.py`) automates steps 1–4 — any PDF dropped into `data/incoming/` with a matching profile triggers the pipeline automatically.
