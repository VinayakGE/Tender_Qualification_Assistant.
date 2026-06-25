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
  "qualification_score": 84,
  "primary_bottleneck": "Historical vendor dominance",
  "confidence": 0.81
}
```

**Why REVIEW and not BID?** Apex Infrastructure passes all four mandatory qualification requirements. The recommendation is REVIEW because the tender document references a prior KRDCL contract (Package HB-04) — a signal of incumbent advantage. Incumbent risk score = 71, which is at the threshold (70). A bid team with a direct KRDCL relationship should proceed; one without should reconsider.

---

## Run it

### Prerequisites

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY
```

### One command

```bash
python scripts/run_pipeline.py \
  --pdf examples/Tender-001/Tender-001.pdf \
  --profile examples/Tender-001/company-profile.json
```

### Expected output

```
pipeline_started   tender_id=tender-001  company_id=APEX-INFRA-001
stage_complete     stage=parser          text_chars=4821
stage_complete     stage=extractor       requirements_found=6
stage_complete     stage=qualification   overall_pass=True  mandatory_fails=0
stage_complete     stage=scoring         qualification_score=84  incumbent_risk=71
stage_complete     stage=recommendation  recommendation=REVIEW
stage_complete     stage=ledger
pipeline_complete  recommendation=REVIEW  duration_seconds=4.2

Recommendation written to: data/outcomes/tender-001_recommendation.json
```

### Without an API key

The pipeline will still run. The `reasoning` field in the output will be `null` — the LLM explanation stage fails gracefully and the rest of the pipeline completes.

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
