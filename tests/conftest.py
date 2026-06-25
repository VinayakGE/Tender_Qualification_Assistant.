"""Shared pytest fixtures for the Tender Qualification Assistant test suite."""

import pytest

from src.extractor.requirement_extractor import Requirement
from src.qualification.eligibility import EligibilityResult, RequirementResult, RequirementStatus

# ---------------------------------------------------------------------------
# Sample tender text
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_tender_text() -> str:
    """A minimal synthetic tender document for testing."""
    return """
Government of India
Ministry of Jal Shakti
National Water Mission

NOTICE INVITING TENDER

Tender No: NIT/NWM/2024/001
Tender for: Supply, Installation, and Commissioning of Water Treatment Plant

1. ELIGIBILITY CRITERIA

1.1 The bidder shall have an average annual turnover of not less than Rs. 30 Crores
    over the last three financial years.

1.2 The bidder shall have successfully completed at least one similar work of value
    not less than Rs. 12 Crores in the last 7 years.

1.3 The bidder must hold valid ISO 9001:2015 certification.

1.4 Net worth of the bidder as per the latest audited balance sheet shall not be
    less than Rs. 10 Crores.

2. SCOPE OF WORK

The work involves supply, installation, testing and commissioning of a 5 MLD
Water Treatment Plant including all civil, mechanical, electrical, and instrumentation
works at the designated site.

3. CONTRACT DETAILS

Estimated Cost: Rs. 18.5 Crores
Contract Period: 24 months from date of work order
Submission Deadline: 15/08/2024
    """.strip()


# ---------------------------------------------------------------------------
# Sample company profile
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_company_profile() -> dict:
    """A synthetic company profile for testing eligibility checks."""
    return {
        "company_id": "TEST-001",
        "name": "Test Infrastructure Pvt Ltd",
        "pan": "AABCT1234F",
        "gstin": "27AABCT1234F1Z5",
        "annual_turnover_inr_crores": [42, 38, 51],
        "years_in_operation": 12,
        "certifications": ["ISO 9001:2015", "ISO 14001:2015"],
        "completed_projects": [
            {
                "project_id": "P001",
                "title": "Water Treatment Plant - Pune",
                "client": "Pune Municipal Corporation",
                "sector": "water_treatment",
                "contract_value_inr_crores": 18.5,
                "duration_months": 24,
                "completion_date": "2022-03-15",
                "has_completion_certificate": True,
            },
            {
                "project_id": "P002",
                "title": "Road Construction - MIDC",
                "client": "MIDC",
                "sector": "civil_works",
                "contract_value_inr_crores": 8.2,
                "duration_months": 12,
                "completion_date": "2021-06-30",
                "has_completion_certificate": True,
            },
        ],
        "financial_net_worth_inr_crores": 18.0,
        "working_capital_inr_crores": 8.5,
        "employees": 340,
        "priority_sectors": ["water_treatment", "civil_works"],
        "blacklisted": False,
    }


# ---------------------------------------------------------------------------
# Sample requirements list
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_requirements() -> list[Requirement]:
    """A list of sample requirements for testing the qualification engine."""
    return [
        Requirement(
            requirement_id="req_001",
            category="turnover",
            description="Average annual turnover of at least Rs. 30 Crores over last 3 years",
            threshold_value=30.0,
            threshold_unit="INR_crores",
            threshold_period_years=3,
            is_mandatory=True,
            source_clause="1.1",
        ),
        Requirement(
            requirement_id="req_002",
            category="experience",
            description="Completed similar work of value >= Rs. 12 Crores in last 7 years",
            threshold_value=12.0,
            threshold_unit="INR_crores",
            threshold_period_years=7,
            is_mandatory=True,
            source_clause="1.2",
            sector="water_treatment",
        ),
        Requirement(
            requirement_id="req_003",
            category="certification",
            description="Valid ISO 9001:2015 certification",
            threshold_value=None,
            threshold_unit=None,
            is_mandatory=True,
            source_clause="1.3",
            certification_name="ISO 9001:2015",
        ),
        Requirement(
            requirement_id="req_004",
            category="financial",
            description="Net worth >= Rs. 10 Crores",
            threshold_value=10.0,
            threshold_unit="INR_crores",
            is_mandatory=True,
            source_clause="1.4",
        ),
        Requirement(
            requirement_id="req_005",
            category="certification",
            description="ISO 14001:2015 certification preferred",
            threshold_value=None,
            threshold_unit=None,
            is_mandatory=False,
            source_clause="1.5",
            certification_name="ISO 14001:2015",
        ),
    ]


# ---------------------------------------------------------------------------
# Sample eligibility result (all pass)
# ---------------------------------------------------------------------------


@pytest.fixture
def all_pass_eligibility_result() -> EligibilityResult:
    """An EligibilityResult where all requirements pass with evidence."""
    results = [
        RequirementResult(
            requirement_id="req_001",
            category="turnover",
            description="Annual turnover >= 30 Cr",
            is_mandatory=True,
            status=RequirementStatus.PASS,
            evidence_available=True,
            evidence_description="Average turnover: ₹43.7 Cr over 3 years",
        ),
        RequirementResult(
            requirement_id="req_002",
            category="experience",
            description="Similar project >= 12 Cr in 7 years",
            is_mandatory=True,
            status=RequirementStatus.PASS,
            evidence_available=True,
            evidence_description="Water Treatment Plant Pune: ₹18.5 Cr",
        ),
        RequirementResult(
            requirement_id="req_003",
            category="certification",
            description="ISO 9001:2015",
            is_mandatory=True,
            status=RequirementStatus.PASS,
            evidence_available=True,
            evidence_description="ISO 9001:2015 found in profile",
        ),
        RequirementResult(
            requirement_id="req_004",
            category="financial",
            description="Net worth >= 10 Cr",
            is_mandatory=True,
            status=RequirementStatus.PASS,
            evidence_available=True,
            evidence_description="Net worth: ₹18 Cr",
        ),
        RequirementResult(
            requirement_id="req_005",
            category="certification",
            description="ISO 14001:2015",
            is_mandatory=False,
            status=RequirementStatus.PASS,
            evidence_available=True,
            evidence_description="ISO 14001:2015 found in profile",
        ),
    ]
    return EligibilityResult(
        overall_pass=True,
        requirement_results=results,
        mandatory_pass_count=4,
        mandatory_fail_count=0,
        optional_pass_count=1,
        optional_fail_count=0,
        evidence_gap_count=0,
    )


# ---------------------------------------------------------------------------
# Sample recommendation dict (for API tests)
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_recommendation_dict() -> dict:
    """A minimal valid recommendation dict."""
    return {
        "recommendation_id": "rec_test001",
        "tender_id": "test_tender",
        "company_id": "TEST-001",
        "recommendation": "BID",
        "qualification_score": 92,
        "competitive_strength": 75,
        "incumbent_risk": 35,
        "execution_risk": 25,
        "value_score": 71,
        "primary_bottleneck": None,
        "bottleneck_category": None,
        "evidence_gaps": [],
        "confidence": 0.88,
        "reasoning": "All eligibility criteria met with strong evidence. BID recommended.",
        "failed_mandatory_requirements": [],
        "pipeline_duration_seconds": 45.2,
        "created_at": "2024-06-15T10:23:44Z",
    }
