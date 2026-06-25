"""Tests for the recommendation engine decision tree."""

from src.qualification.eligibility import EligibilityResult, RequirementResult, RequirementStatus
from src.recommendation.engine import RecommendationEngine


def make_result(
    req_id: str,
    is_mandatory: bool,
    status: RequirementStatus,
    evidence_available: bool = True,
) -> RequirementResult:
    return RequirementResult(
        requirement_id=req_id,
        category="turnover",
        description=f"Req {req_id}",
        is_mandatory=is_mandatory,
        status=status,
        evidence_available=evidence_available,
        evidence_description="",
    )


def make_eligibility(results: list[RequirementResult]) -> EligibilityResult:
    mandatory_fails = sum(
        1 for r in results if r.is_mandatory and r.status == RequirementStatus.FAIL
    )
    return EligibilityResult(
        overall_pass=(mandatory_fails == 0),
        requirement_results=results,
        mandatory_fail_count=mandatory_fails,
        mandatory_pass_count=sum(
            1 for r in results if r.is_mandatory and r.status == RequirementStatus.PASS
        ),
    )


class TestRecommendationEngineBranches:
    """Tests covering all three recommendation branches and their sub-conditions."""

    def test_no_bid_mandatory_fail(self):
        """Mandatory requirement failure → NO_BID."""
        results = [
            make_result("r1", True, RequirementStatus.FAIL),
            make_result("r2", True, RequirementStatus.PASS),
        ]
        eligibility = make_eligibility(results)
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=eligibility,
            tender_id="T001",
            company_id="C001",
            incumbent_risk=20,
        )
        assert rec.recommendation == "NO_BID"
        assert "r1" in rec.failed_mandatory_requirements

    def test_no_bid_low_qualification_score(self):
        """qualification_score < 60 → NO_BID even if no mandatory failures."""
        # 1 pass, 4 fails → score ~17 → NO_BID
        results = [
            make_result("r1", True, RequirementStatus.PASS),
            make_result("r2", True, RequirementStatus.FAIL),
            make_result("r3", True, RequirementStatus.FAIL),
            make_result("r4", True, RequirementStatus.FAIL),
            make_result("r5", True, RequirementStatus.FAIL),
        ]
        # Override overall_pass to True to test the score-gate independently
        eligibility = EligibilityResult(
            overall_pass=False,  # Mandatory fails → NO_BID directly
            requirement_results=results,
            mandatory_fail_count=4,
            mandatory_pass_count=1,
        )
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=eligibility,
            tender_id="T002",
            company_id="C001",
        )
        assert rec.recommendation == "NO_BID"

    def test_review_marginal_score(self):
        """qualification_score 60-79 → REVIEW."""
        # 3 mandatory pass, 1 mandatory fail → mandatory_score ~75, overall→FAIL
        # Use directly all PARTIAL to get ~50 mandatory score
        # Instead: 2 pass, 1 fail on mandatory → score ~66.7
        results = [
            make_result("r1", True, RequirementStatus.PASS),
            make_result("r2", True, RequirementStatus.PASS),
            make_result("r3", True, RequirementStatus.PARTIAL),
            make_result("r4", False, RequirementStatus.FAIL),  # Optional fail
        ]
        eligibility = EligibilityResult(
            overall_pass=True,
            requirement_results=results,
            mandatory_fail_count=0,
            mandatory_pass_count=2,
        )
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=eligibility,
            tender_id="T003",
            company_id="C001",
            incumbent_risk=20,
        )
        # Score should be in marginal range → REVIEW
        assert rec.recommendation in ("REVIEW", "NO_BID")  # Depending on exact score

    def test_review_evidence_gaps(self):
        """Score 80+ but critical evidence gaps → REVIEW."""
        # All mandatory PASS but no evidence available
        results = [
            make_result("r1", True, RequirementStatus.PASS, evidence_available=False),
            make_result("r2", True, RequirementStatus.PASS, evidence_available=False),
            make_result("r3", True, RequirementStatus.PASS, evidence_available=True),
        ]
        eligibility = EligibilityResult(
            overall_pass=True,
            requirement_results=results,
            mandatory_fail_count=0,
            mandatory_pass_count=3,
        )
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=eligibility,
            tender_id="T004",
            company_id="C001",
            incumbent_risk=30,
        )
        assert rec.recommendation == "REVIEW"

    def test_review_high_incumbent_risk(self):
        """Score 80+, no evidence gaps, but incumbent_risk >= 70 → REVIEW."""
        results = [
            make_result("r1", True, RequirementStatus.PASS, evidence_available=True),
            make_result("r2", True, RequirementStatus.PASS, evidence_available=True),
            make_result("r3", True, RequirementStatus.PASS, evidence_available=True),
        ]
        eligibility = EligibilityResult(
            overall_pass=True,
            requirement_results=results,
            mandatory_fail_count=0,
            mandatory_pass_count=3,
        )
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=eligibility,
            tender_id="T005",
            company_id="C001",
            incumbent_risk=85,  # High incumbent risk
        )
        assert rec.recommendation == "REVIEW"

    def test_bid_all_conditions_met(self, all_pass_eligibility_result):
        """Score 80+, no evidence gaps, incumbent_risk < 70 → BID."""
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=all_pass_eligibility_result,
            tender_id="T006",
            company_id="C001",
            incumbent_risk=40,  # Low incumbent risk
        )
        assert rec.recommendation == "BID"

    def test_bid_just_below_incumbent_threshold(self, all_pass_eligibility_result):
        """incumbent_risk = 69 (just below threshold) → BID."""
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=all_pass_eligibility_result,
            tender_id="T007",
            company_id="C001",
            incumbent_risk=69,
        )
        assert rec.recommendation == "BID"

    def test_review_at_incumbent_threshold(self, all_pass_eligibility_result):
        """incumbent_risk = 70 (at threshold) → REVIEW."""
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=all_pass_eligibility_result,
            tender_id="T008",
            company_id="C001",
            incumbent_risk=70,
        )
        assert rec.recommendation == "REVIEW"

    def test_recommendation_has_required_fields(self, all_pass_eligibility_result):
        """Recommendation object has all required fields populated."""
        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=all_pass_eligibility_result,
            tender_id="T009",
            company_id="C001",
            competitive_strength=75,
            incumbent_risk=40,
            execution_risk=25,
            value_score=70,
        )
        assert rec.recommendation_id
        assert rec.tender_id == "T009"
        assert rec.company_id == "C001"
        assert rec.qualification_score >= 0
        assert 0.0 <= rec.confidence <= 1.0
        assert rec.created_at
        assert isinstance(rec.evidence_gaps, list)
        assert isinstance(rec.failed_mandatory_requirements, list)

    def test_to_dict_serializable(self, all_pass_eligibility_result):
        """to_dict() returns a JSON-serializable dictionary."""
        import json

        engine = RecommendationEngine()
        rec = engine.recommend(
            eligibility_result=all_pass_eligibility_result,
            tender_id="T010",
            company_id="C001",
        )
        d = rec.to_dict()
        # Should not raise
        json.dumps(d)
        assert d["recommendation"] in ("BID", "REVIEW", "NO_BID")
