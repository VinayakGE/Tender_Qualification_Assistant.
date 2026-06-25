"""FastAPI route definitions for the Tender Qualification Assistant API."""

import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from src.ledger.decisions import DecisionLedger
from src.ledger.outcomes import OutcomeTracker
from src.pipeline.runner import PipelineRunner
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/analyze", summary="Analyze a tender PDF")
async def analyze_tender(
    tender_pdf: UploadFile = File(..., description="Tender document in PDF format"),
    company_profile_json: str = Form(..., description="Company profile JSON string matching company.schema.json"),
) -> JSONResponse:
    """Run the full qualification pipeline on a tender PDF.

    Accepts a PDF file and a company profile JSON string.
    Returns the recommendation JSON.

    - **tender_pdf**: The tender document PDF
    - **company_profile_json**: JSON string of the company profile
    """
    # Validate company profile JSON
    try:
        company_profile = json.loads(company_profile_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid company_profile_json: {exc}")

    if not company_profile.get("company_id"):
        raise HTTPException(status_code=422, detail="company_profile_json must include 'company_id'")

    # Save uploaded PDF to a temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        content = await tender_pdf.read()
        tmp_pdf.write(content)
        tmp_pdf_path = Path(tmp_pdf.name)

    with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False, encoding="utf-8") as tmp_profile:
        json.dump(company_profile, tmp_profile)
        tmp_profile_path = Path(tmp_profile.name)

    try:
        runner = PipelineRunner()
        recommendation = runner.run(tmp_pdf_path, tmp_profile_path)
        logger.info(
            "api_analyze_complete",
            recommendation=recommendation.recommendation,
            tender_id=recommendation.tender_id,
        )
        return JSONResponse(content=recommendation.to_dict(), status_code=200)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        logger.error("api_analyze_error", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")
    finally:
        tmp_pdf_path.unlink(missing_ok=True)
        tmp_profile_path.unlink(missing_ok=True)


@router.get("/ledger", summary="List all decisions")
async def list_decisions(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Results per page"),
) -> JSONResponse:
    """Return a paginated list of all decisions in the ledger, newest first."""
    ledger = DecisionLedger()
    entries, total = ledger.read_paginated(page=page, page_size=page_size)
    return JSONResponse(content={
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": entries,
    })


@router.get("/ledger/{recommendation_id}", summary="Get a single decision")
async def get_decision(recommendation_id: str) -> JSONResponse:
    """Return a single decision by recommendation ID."""
    ledger = DecisionLedger()
    entry = ledger.find_by_id(recommendation_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Recommendation '{recommendation_id}' not found")
    return JSONResponse(content=entry)


@router.post("/outcomes/{recommendation_id}", summary="Record bid outcome")
async def record_outcome(
    recommendation_id: str,
    bid_submitted: bool = Form(..., description="Was a bid submitted?"),
    bid_won: bool | None = Form(default=None, description="Was the bid won? (null if result not yet known)"),
    contract_value_inr: float | None = Form(default=None, description="Contract value in INR if won"),
    human_decision: str | None = Form(default=None, description="Actual team decision (BID or NO_BID)"),
    loss_reason: str | None = Form(default=None, description="Why the bid was lost (if applicable)"),
    notes: str | None = Form(default=None, description="Free-text notes"),
) -> JSONResponse:
    """Record the actual outcome of a bid against a recommendation.

    Used for accuracy tracking and learning. Links the actual result back
    to the original recommendation by ID.
    """
    # Look up the original recommendation to get tender_id and company_id
    ledger = DecisionLedger()
    original = ledger.find_by_id(recommendation_id)
    if original is None:
        raise HTTPException(
            status_code=404,
            detail=f"Recommendation '{recommendation_id}' not found in ledger",
        )

    tracker = OutcomeTracker()
    outcome = tracker.record(
        recommendation_id=recommendation_id,
        tender_id=original["tender_id"],
        company_id=original["company_id"],
        bid_submitted=bid_submitted,
        bid_won=bid_won,
        contract_value_inr=contract_value_inr,
        system_recommendation=original.get("recommendation"),
        human_decision=human_decision,
        loss_reason=loss_reason,
        notes=notes,
    )

    logger.info(
        "api_outcome_recorded",
        recommendation_id=recommendation_id,
        bid_submitted=bid_submitted,
        bid_won=bid_won,
    )

    return JSONResponse(content=outcome, status_code=201)


@router.get("/health", summary="Health check")
async def health() -> JSONResponse:
    """Simple health check endpoint."""
    return JSONResponse(content={"status": "ok"})
