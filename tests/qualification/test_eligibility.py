"""Tests for qualification eligibility checkers."""

from src.extractor.requirement_extractor import Requirement
from src.qualification.certifications import CertificationChecker
from src.qualification.eligibility import EligibilityChecker, RequirementStatus
from src.qualification.turnover import TurnoverChecker


class TestTurnoverChecker:
    def test_pass_when_turnover_meets_threshold(self, sample_company_profile):
        """Returns PASS when company average turnover >= threshold."""
        checker = TurnoverChecker()
        req = Requirement(
            requirement_id="req_001",
            category="turnover",
            description="Average turnover >= 30 Cr",
            threshold_value=30.0,
            threshold_unit="INR_crores",
            threshold_period_years=3,
            is_mandatory=True,
        )
        result = checker.check_single(req, sample_company_profile)
        assert result.status == RequirementStatus.PASS

    def test_fail_when_turnover_below_threshold(self, sample_company_profile):
        """Returns FAIL when company average turnover < threshold."""
        checker = TurnoverChecker()
        req = Requirement(
            requirement_id="req_001",
            category="turnover",
            description="Average turnover >= 60 Cr",
            threshold_value=60.0,
            threshold_unit="INR_crores",
            threshold_period_years=3,
            is_mandatory=True,
        )
        result = checker.check_single(req, sample_company_profile)
        assert result.status == RequirementStatus.FAIL

    def test_partial_when_no_turnover_data(self):
        """Returns PARTIAL when company profile has no turnover data."""
        checker = TurnoverChecker()
        req = Requirement(
            requirement_id="req_001",
            category="turnover",
            description="Annual turnover >= 10 Cr",
            threshold_value=10.0,
            threshold_unit="INR_crores",
            is_mandatory=True,
        )
        result = checker.check_single(req, {"company_id": "empty"})
        assert result.status == RequirementStatus.PARTIAL

    def test_partial_when_no_threshold(self, sample_company_profile):
        """Returns PARTIAL when requirement has no numeric threshold."""
        checker = TurnoverChecker()
        req = Requirement(
            requirement_id="req_001",
            category="turnover",
            description="Must have adequate turnover",
            threshold_value=None,
            threshold_unit=None,
            is_mandatory=True,
        )
        result = checker.check_single(req, sample_company_profile)
        assert result.status == RequirementStatus.PARTIAL

    def test_lakh_threshold_normalized_correctly(self, sample_company_profile):
        """Lakh threshold is correctly converted to Crores for comparison."""
        checker = TurnoverChecker()
        # 3000 Lakhs = 30 Crores — company has ~43.7 Cr average → should PASS
        req = Requirement(
            requirement_id="req_001",
            category="turnover",
            description="Average turnover >= 3000 Lakhs",
            threshold_value=3000.0,
            threshold_unit="INR_lakhs",
            threshold_period_years=3,
            is_mandatory=True,
        )
        result = checker.check_single(req, sample_company_profile)
        assert result.status == RequirementStatus.PASS


class TestCertificationChecker:
    def test_pass_for_exact_cert_match(self, sample_company_profile):
        """Returns PASS when exact certification is in profile."""
        checker = CertificationChecker()
        req = Requirement(
            requirement_id="req_003",
            category="certification",
            description="ISO 9001:2015 required",
            is_mandatory=True,
            certification_name="ISO 9001:2015",
        )
        result = checker.check_single(req, sample_company_profile)
        assert result.status == RequirementStatus.PASS

    def test_fail_when_cert_missing(self, sample_company_profile):
        """Returns FAIL when required certification is not in profile."""
        checker = CertificationChecker()
        req = Requirement(
            requirement_id="req_003",
            category="certification",
            description="ISO 27001 required",
            is_mandatory=True,
            certification_name="ISO 27001",
        )
        result = checker.check_single(req, sample_company_profile)
        assert result.status == RequirementStatus.FAIL

    def test_pass_with_partial_name_match(self, sample_company_profile):
        """Partial cert name match still returns PASS (ISO 9001 matches ISO 9001:2015)."""
        checker = CertificationChecker()
        req = Requirement(
            requirement_id="req_003",
            category="certification",
            description="ISO 9001 certification required",
            is_mandatory=True,
            certification_name="ISO 9001",
        )
        result = checker.check_single(req, sample_company_profile)
        assert result.status == RequirementStatus.PASS


class TestEligibilityChecker:
    def test_overall_pass_when_all_mandatory_pass(
        self, sample_requirements, sample_company_profile
    ):
        """Overall pass when all mandatory requirements are met."""
        checker = EligibilityChecker()
        result = checker.check(sample_requirements, sample_company_profile)
        assert result.overall_pass is True
        assert result.mandatory_fail_count == 0

    def test_overall_fail_when_mandatory_fails(self, sample_company_profile):
        """Overall fail when at least one mandatory requirement fails."""
        requirements = [
            Requirement(
                requirement_id="req_001",
                category="turnover",
                description="Must have turnover >= 200 Cr",
                threshold_value=200.0,
                threshold_unit="INR_crores",
                threshold_period_years=1,
                is_mandatory=True,
            )
        ]
        checker = EligibilityChecker()
        result = checker.check(requirements, sample_company_profile)
        assert result.overall_pass is False
        assert result.mandatory_fail_count >= 1

    def test_overall_pass_when_only_optional_fails(self, sample_company_profile):
        """Overall pass even when optional requirements fail."""
        requirements = [
            Requirement(
                requirement_id="req_001",
                category="certification",
                description="Optional: ISO 27001",
                is_mandatory=False,
                certification_name="ISO 27001",
            )
        ]
        checker = EligibilityChecker()
        result = checker.check(requirements, sample_company_profile)
        assert result.overall_pass is True  # Optional fails don't fail overall

    def test_failed_mandatory_ids_populated(self, sample_company_profile):
        """failed_mandatory_ids contains IDs of failing mandatory requirements."""
        requirements = [
            Requirement(
                requirement_id="req_fail_01",
                category="turnover",
                description="Turnover >= 500 Cr",
                threshold_value=500.0,
                threshold_unit="INR_crores",
                is_mandatory=True,
            )
        ]
        checker = EligibilityChecker()
        result = checker.check(requirements, sample_company_profile)
        assert "req_fail_01" in result.failed_mandatory_ids
