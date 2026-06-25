"""Certification requirement checker."""

from src.extractor.requirement_extractor import Requirement
from src.qualification.eligibility import RequirementResult, RequirementStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CertificationChecker:
    """Checks if the company holds certifications required by the tender.

    Matches on full certification name (e.g., "ISO 9001:2015") and partial
    name (e.g., "ISO 9001" matches "ISO 9001:2015").
    """

    def check_single(
        self,
        requirement: Requirement,
        company_profile: dict,
    ) -> RequirementResult:
        """Check a single certification requirement.

        Args:
            requirement: The certification requirement to check.
            company_profile: Company profile dict.

        Returns:
            RequirementResult with PASS or FAIL status.
        """
        company_certs: list[str] = [
            c.lower().strip() for c in company_profile.get("certifications", [])
        ]

        required_cert = requirement.certification_name or requirement.description
        required_cert_lower = required_cert.lower().strip()

        if not required_cert_lower:
            return RequirementResult(
                requirement_id=requirement.requirement_id,
                category="certification",
                description=requirement.description,
                is_mandatory=requirement.is_mandatory,
                status=RequirementStatus.PARTIAL,
                evidence_available=False,
                evidence_description="Certification name could not be parsed from requirement",
            )

        # Try exact match first
        found = required_cert_lower in company_certs

        # Try partial match (e.g., "ISO 9001" in "ISO 9001:2015")
        if not found:
            found = any(
                required_cert_lower in cert or cert in required_cert_lower
                for cert in company_certs
            )

        # Evidence: having the cert in the profile implies the certificate exists,
        # but we cannot confirm it's valid/current without a document reference
        evidence_available = found

        if found:
            matched_cert = next(
                (c for c in company_certs if required_cert_lower in c or c in required_cert_lower),
                required_cert_lower,
            )
            description = f"Company holds '{matched_cert}' — matches requirement for '{required_cert}'"
        else:
            description = (
                f"Company does not hold '{required_cert}'. "
                f"Company certifications: {', '.join(company_profile.get('certifications', [])) or 'None'}"
            )

        logger.debug(
            "certification_check",
            requirement_id=requirement.requirement_id,
            required=required_cert,
            found=found,
        )

        return RequirementResult(
            requirement_id=requirement.requirement_id,
            category="certification",
            description=requirement.description,
            is_mandatory=requirement.is_mandatory,
            status=RequirementStatus.PASS if found else RequirementStatus.FAIL,
            evidence_available=evidence_available,
            evidence_description=description,
        )
