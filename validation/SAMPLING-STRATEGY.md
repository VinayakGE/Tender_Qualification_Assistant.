# Evidence Collection Sampling Strategy

The goal is not volume. It is coverage.
Ten tenders from one authority reveal that authority's patterns.
They say nothing about the distribution of Indian government procurement.

---

## RA-1 — Baseline (10 tenders)

**Objective:** Can the pipeline process real tenders at all?

**Sample:** Any 10 real tenders, any authority, any sector.

**Exit question:** Does the pipeline run? Where does it fail?

**Success:** Evidence Yield > 1. At least one clear engineering priority.

---

## RA-2 — Authority Sampling (target: 30 tenders total)

**Objective:** Do different procuring authorities produce structurally different documents?

**Sample:** 4–5 tenders each from distinct authority types:

| Authority type | Example |
|---|---|
| Central road agency | NHAI, NHIDCL |
| Central infrastructure | CPWD, Railways |
| State PWD | Karnataka PWD, Maharashtra PWD |
| Public sector undertaking | ONGC, BHEL, NTPC |
| Urban local body | BBMP, MCGM |

**Exit question:** Are parser/extraction failures authority-specific or universal?

**Success:** We can describe which authority types require special handling and why.

---

## RA-3 — Sector Sampling (target: 50 tenders total)

**Objective:** Do different procurement sectors produce different eligibility structures?

**Sample:** 4–5 tenders each from distinct sectors:

| Sector | Eligibility characteristics to watch |
|---|---|
| Civil construction | Turnover, experience, equipment, JV clauses |
| IT services | CMMI levels, data security certifications |
| Healthcare / pharma | CDSCO approvals, cold chain capacity |
| Consulting / advisory | CVs, methodology, key personnel |
| Equipment supply | OEM authorization, warranty terms |

**Exit question:** Do qualification categories generalize, or are they sector-specific?

**Success:** We know which requirement categories are universal and which need sector-specific extractors.

---

## Evidence Stability Rule

After each sprint, before opening engineering:

> Did the last N tenders introduce genuinely new classes of findings?

If yes → continue collecting.
If no → evidence base is stabilizing for that dimension. Engineering is now justified.

Collect evidence across dimensions (authority type, sector) before assuming the finding is universal.
A bug found in 3 NHAI tenders may not exist in Railways tenders.
A bug found in 3 IT tenders may not exist in civil construction tenders.

---

## What We Are Not Doing

- We are not maximizing tender count.
- We are not processing tenders to validate our existing code.
- We are not stopping once the code works on a favorable sample.

We are sampling the space of Indian government procurement systematically, so that the Evidence Corpus reflects the distribution we will encounter in production — not the distribution that is easiest to handle.
