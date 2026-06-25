# RA-1 Extraction Accuracy Report

For each tender, compare every extracted field against the source PDF.
Fill in after manual review. This report is independent of qualification and recommendation quality.

---

## How to use this report

1. Run the pipeline. Save the output JSON.
2. Open the source PDF manually.
3. For each field in the table below, verify the extracted value against the PDF.
4. Mark: ✓ (correct), ✗ (wrong value), — (field absent in this tender), ? (unable to verify).
5. Note the clause/page reference when marking ✗.

---

## Per-Tender Field Accuracy

### Tender 01

| Field | Extracted | Correct | Source (page/clause) | Notes |
|---|---|---|---|---|
| Tender ID | | | | |
| Authority | | | | |
| Tender Title | | | | |
| Contract Value | | | | |
| EMD | | | | |
| Submission Deadline | | | | |
| Contract Duration | | | | |
| Turnover requirement | | | | |
| Experience requirement | | | | |
| Financial requirement | | | | |
| ISO / Certification | | | | |
| Equipment requirement | | | | |
| JV clause | | | | |
| Registration requirement | | | | |
| Extraction warnings generated | | | | |

---

### Tender 02

| Field | Extracted | Correct | Source (page/clause) | Notes |
|---|---|---|---|---|
| Tender ID | | | | |
| Authority | | | | |
| Tender Title | | | | |
| Contract Value | | | | |
| EMD | | | | |
| Submission Deadline | | | | |
| Contract Duration | | | | |
| Turnover requirement | | | | |
| Experience requirement | | | | |
| Financial requirement | | | | |
| ISO / Certification | | | | |
| Equipment requirement | | | | |
| JV clause | | | | |
| Registration requirement | | | | |
| Extraction warnings generated | | | | |

---

### Tender 03

| Field | Extracted | Correct | Source (page/clause) | Notes |
|---|---|---|---|---|
| Tender ID | | | | |
| Authority | | | | |
| Tender Title | | | | |
| Contract Value | | | | |
| EMD | | | | |
| Submission Deadline | | | | |
| Contract Duration | | | | |
| Turnover requirement | | | | |
| Experience requirement | | | | |
| Financial requirement | | | | |
| ISO / Certification | | | | |
| Equipment requirement | | | | |
| JV clause | | | | |
| Registration requirement | | | | |
| Extraction warnings generated | | | | |

---

### Tenders 04–10

_(Copy the table above for each remaining tender.)_

---

## Aggregate Accuracy Table

Fill in after all 10 tenders.

| Field | Correct | Wrong | Absent | Unable to verify | Accuracy |
|---|---|---|---|---|---|
| Tender ID | | | | | |
| Authority | | | | | |
| Tender Title | | | | | |
| Contract Value | | | | | |
| EMD | | | | | |
| Submission Deadline | | | | | |
| Contract Duration | | | | | |
| Turnover requirement | | | | | |
| Experience requirement | | | | | |
| Financial requirement | | | | | |
| ISO / Certification | | | | | |
| Equipment requirement | | | | | |
| JV clause | | | | | |
| Registration requirement | | | | | |

**Accuracy = Correct / (Correct + Wrong)**. Absent fields are excluded from the denominator.

---

## Extraction Warning Quality

| Metric | Count |
|---|---|
| Tenders where warnings were generated | |
| Warnings that correctly identified a real issue | |
| Warnings that were false alarms | |
| Real issues that were NOT warned about | |

Warning precision = Correct warnings / Total warnings generated
Warning recall = Correct warnings / Total real issues

---

## Top Extraction Gaps

List the fields or requirement types that were most frequently wrong or missing.
These become the input to the post-RA-1 engineering priorities.

1. 
2. 
3. 
4. 
5. 
