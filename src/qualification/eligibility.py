"""Overall eligibility checker — orchestrates all qualification sub-checkers."""

from dataclasses import dataclass, field
from enum import Enum

from src.extractor.requirement_extractor import Requirement
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RequirementStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    NOT_CHECKED = "NOT_CHECKED"


@dataclass
class RequirementResult:
    """Result of checking a single requirement against a company profile."""

    requirement_id: str
    category: str
    description: str
    is_mandatory: bool
    status: RequirementStatus
    evidence_available: bool
    evidence_description: str
    notes: str = ""


@dataclass
class EligibilityResult:
    """Aggregated result of all requirement checks."""

    overall_pass: bool
    requirement_results: list[RequirementResult] = field(default_factory=list)
    mandatory_fail_count: int = 0
    mandatory_pass_count: int = 0
    optional_fail_count: int = 0
    optional_pass_count: int = 0
    evidence_gap_count: int = 0

    @property
    def total_requirements(self) -> int:
        return len(self.requirement_results)

    @property
    def failed_mandatory_ids(self) -> list[str]:
        return [
            r.requirement_id
            for r in self.requirement_results
            if r.is_mandatory and r.status == RequirementStatus.FAIL
        ]


class EligibilityChecker:
    """Checks a company profile against all extracted tender requirements.

    Routes each requirement to the appropriate sub-checker based on category,
    then aggregates results into an EligibilityResult.
    """

    def check(
        self,
        requirements: list[Requirement],
        company_profile: dict,
    ) -> EligibilityResult:
        """Check all requirements against the company profile.

        Args:
            requirements: List of requirements extracted from the tender.
            company_profile: Company profile dict matching company.schema.json.

        Returns:
            EligibilityResult with overall pass/fail and per-requirement details.
        """
        from src.qualification.certifications import CertificationChecker
        from src.qualification.experience import ExperienceChecker
        from src.qualification.financial import FinancialChecker
        from src.qualification.turnover import TurnoverChecker

        checkers = {
            "turnover": TurnoverChecker(),
            "experience": ExperienceChecker(),
            "certification": CertificationChecker(),
            "financial": FinancialChecker(),
        }

        results: list[RequirementResult] = []

        for req in requirements:
            checker = checkers.get(req.category)
            if checker:
                result = checker.check_single(req, company_profile)
            else:
                # technical / other — cannot be checked automatically
                result = RequirementResult(
                    requirement_id=req.requirement_id,
                    category=req.category,
                    description=req.description,
                    is_mandatory=req.is_mandatory,
                    status=RequirementStatus.PARTIAL,
                    evidence_available=False,
                    evidence_description="Cannot be automatically checked — requires manual review",
                    notes=f"Category '{req.category}' has no automatic checker",
                )
            results.append(result)

        # Compute summary stats
        mandatory_fails = sum(
            1 for r in results if r.is_mandatory and r.status == RequirementStatus.FAIL
        )
        mandatory_passes = sum(
            1 for r in results if r.is_mandatory and r.status == RequirementStatus.PASS
        )
        optional_fails = sum(
            1 for r in results if not r.is_mandatory and r.status == RequirementStatus.FAIL
        )
        optional_passes = sum(
            1 for r in results if not r.is_mandatory and r.status == RequirementStatus.PASS
        )
        evidence_gaps = sum(1 for r in results if not r.evidence_available)

        overall_pass = mandatory_fails == 0

        eligibility_result = EligibilityResult(
            overall_pass=overall_pass,
            requirement_results=results,
            mandatory_fail_count=mandatory_fails,
            mandatory_pass_count=mandatory_passes,
            optional_fail_count=optional_fails,
            optional_pass_count=optional_passes,
            evidence_gap_count=evidence_gaps,
        )

        logger.info(
            "eligibility_check_complete",
            overall_pass=overall_pass,
            total_requirements=len(results),
            mandatory_fails=mandatory_fails,
            evidence_gaps=evidence_gaps,
        )

        return eligibility_result
