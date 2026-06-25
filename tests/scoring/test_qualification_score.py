"""Tests for qualification score computation."""

import pytest

from src.qualification.eligibility import EligibilityResult, RequirementResult, RequirementStatus
from src.scoring.qualification_score import QualificationScorer


def make_result(req_id: str, is_mandatory: bool, status: RequirementStatus) -> RequirementResult:
    """Helper to create a RequirementResult."""
    return RequirementResult(
        requirement_id=req_id,
        category="turnover",
        description=f"Requirement {req_id}",
        is_mandatory=is_mandatory,
        status=status,
        evidence_available=True,
        evidence_description="Test",
    )


def make_eligibility(results: list[RequirementResult]) -> EligibilityResult:
    """Helper to build an EligibilityResult from a list of results."""
    mandatory_fails = sum(1 for r in results if r.is_mandatory and r.status == RequirementStatus.FAIL)
    return EligibilityResult(
        overall_pass=(mandatory_fails == 0),
        requirement_results=results,
        mandatory_fail_count=mandatory_fails,
        mandatory_pass_count=sum(1 for r in results if r.is_mandatory and r.status == RequirementStatus.PASS),
        optional_fail_count=sum(1 for r in results if not r.is_mandatory and r.status == RequirementStatus.FAIL),
        optional_pass_count=sum(1 for r in results if not r.is_mandatory and r.status == RequirementStatus.PASS),
    )


class TestQualificationScorer:
    def test_all_pass_returns_100(self):
        """All requirements passing returns score of 100."""
        results = [
            make_result("r1", True, RequirementStatus.PASS),
            make_result("r2", True, RequirementStatus.PASS),
            make_result("r3", False, RequirementStatus.PASS),
        ]
        eligibility = make_eligibility(results)
        scorer = QualificationScorer()
        assert scorer.score(eligibility) == 100

    def test_all_fail_returns_0(self):
        """All mandatory requirements failing returns score of 0."""
        results = [
            make_result("r1", True, RequirementStatus.FAIL),
            make_result("r2", True, RequirementStatus.FAIL),
        ]
        eligibility = make_eligibility(results)
        scorer = QualificationScorer()
        assert scorer.score(eligibility) == 0

    def test_mandatory_weighted_2x(self):
        """Mandatory requirements contribute 2x vs optional."""
        # 1 mandatory pass, 1 optional fail
        # mandatory_score = 100, optional_score = 0
        # final = (100 * 2 + 0 * 1) / 3 = 66.67 → 66
        results = [
            make_result("r1", True, RequirementStatus.PASS),
            make_result("r2", False, RequirementStatus.FAIL),
        ]
        eligibility = make_eligibility(results)
        scorer = QualificationScorer()
        score = scorer.score(eligibility)
        # With 2:1 weighting: (100*2 + 0*1)/3 = 66.67 → 66
        assert 60 <= score <= 70  # Within expected range

    def test_boundary_60_classified_marginal(self):
        """Exactly 60 should classify as MARGINAL."""
        assert QualificationScorer.classify(60) == "MARGINAL"

    def test_boundary_79_classified_marginal(self):
        """79 classifies as MARGINAL."""
        assert QualificationScorer.classify(79) == "MARGINAL"

    def test_boundary_80_classified_pass(self):
        """Exactly 80 classifies as PASS."""
        assert QualificationScorer.classify(80) == "PASS"

    def test_below_60_classified_fail(self):
        """Score below 60 classifies as FAIL."""
        assert QualificationScorer.classify(59) == "FAIL"
        assert QualificationScorer.classify(0) == "FAIL"

    def test_partial_counts_as_half(self):
        """PARTIAL status contributes 0.5 to the score."""
        results = [
            make_result("r1", True, RequirementStatus.PARTIAL),  # 0.5 / 1.0
        ]
        eligibility = make_eligibility(results)
        scorer = QualificationScorer()
        score = scorer.score(eligibility)
        # mandatory_score = 50 (0.5/1.0 * 100), optional_score = 100 (no optionals)
        # final = (50 * 2 + 100 * 1) / 3 = 66.67 → 66
        assert 60 <= score <= 70

    def test_no_requirements_returns_100(self):
        """No requirements → score 100 (nothing to fail)."""
        eligibility = EligibilityResult(overall_pass=True, requirement_results=[])
        scorer = QualificationScorer()
        score = scorer.score(eligibility)
        assert score == 100

    def test_only_optional_requirements(self):
        """Only optional requirements — score based on optional pass rate."""
        results = [
            make_result("r1", False, RequirementStatus.PASS),
            make_result("r2", False, RequirementStatus.PASS),
            make_result("r3", False, RequirementStatus.FAIL),
        ]
        eligibility = make_eligibility(results)
        scorer = QualificationScorer()
        score = scorer.score(eligibility)
        # 2/3 pass → 66.7 → 66
        assert 60 <= score <= 70
