"""Core recommendation engine — implements the decision tree from docs/recommendation-engine.md."""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.bottlenecks.classifier import BottleneckClassifier
from src.bottlenecks.evidence_gap import EvidenceGapDetector
from src.bottlenecks.reasoning import ReasoningBuilder
from src.qualification.eligibility import EligibilityResult, RequirementStatus
from src.recommendation.confidence import ConfidenceEstimator
from src.scoring.qualification_score import QualificationScorer
from src.utils.config import get_config
from src.utils.helpers import generate_id, now_iso
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Recommendation:
    """The final recommendation output from the pipeline."""

    recommendation_id: str
    tender_id: str
    company_id: str
    recommendation: str  # BID, REVIEW, or NO_BID
    qualification_score: int
    competitive_strength: int | None
    incumbent_risk: int | None
    execution_risk: int | None
    value_score: int | None
    primary_bottleneck: str | None
    bottleneck_category: str | None  # internal only — not exposed in to_dict()
    evidence_gaps: list[str]
    confidence: float
    confidence_reason: list[str]
    reasoning: str | None
    failed_mandatory_requirements: list[str]
    pipeline_duration_seconds: float | None
    created_at: str

    def to_dict(self) -> dict:
        """Serialize to a dictionary suitable for JSON output."""
        return {
            "recommendation_id": self.recommendation_id,
            "tender_id": self.tender_id,
            "company_id": self.company_id,
            "recommendation": self.recommendation,
            "qualification_score": self.qualification_score,
            "competitive_strength": self.competitive_strength,
            "incumbent_risk": self.incumbent_risk,
            "execution_risk": self.execution_risk,
            "value_score": self.value_score,
            "primary_bottleneck": self.primary_bottleneck,
            "evidence_gaps": self.evidence_gaps,
            "confidence": self.confidence,
            "confidence_reason": self.confidence_reason,
            "reasoning": self.reasoning,
            "failed_mandatory_requirements": self.failed_mandatory_requirements,
            "pipeline_duration_seconds": self.pipeline_duration_seconds,
            "created_at": self.created_at,
        }


class RecommendationEngine:
    """Implements the qualification decision tree.

    Decision tree (evaluated in order):
    1. Any mandatory requirement FAIL → NO_BID
    2. qualification_score < 60 → NO_BID
    3. qualification_score 60-79 → REVIEW (always, regardless of evidence)
    4. qualification_score 80+, critical evidence gaps → REVIEW
    5. qualification_score 80+, no gaps, incumbent_risk >= 70 → REVIEW
    6. qualification_score 80+, no gaps, incumbent_risk < 70 → BID
    """

    def __init__(self) -> None:
        self.config = get_config()
        self.scorer = QualificationScorer()
        self.bottleneck_classifier = BottleneckClassifier()
        self.evidence_gap_detector = EvidenceGapDetector()
        self.reasoning_builder = ReasoningBuilder()
        self.confidence_estimator = ConfidenceEstimator()

    def recommend(
        self,
        eligibility_result: EligibilityResult,
        tender_id: str,
        company_id: str,
        competitive_strength: int | None = None,
        incumbent_risk: int | None = None,
        execution_risk: int | None = None,
        value_score: int | None = None,
        pipeline_duration_seconds: float | None = None,
    ) -> Recommendation:
        """Produce a recommendation from eligibility and scoring results.

        Args:
            eligibility_result: Result from EligibilityChecker.
            tender_id: Tender identifier.
            company_id: Company identifier.
            competitive_strength: Competitive strength score (0-100).
            incumbent_risk: Incumbent risk score (0-100).
            execution_risk: Execution risk score (0-100).
            value_score: Value score (0-100).
            pipeline_duration_seconds: Total pipeline duration for observability.

        Returns:
            Recommendation object.
        """
        qualification_score = self.scorer.score(eligibility_result)
        evidence_gaps = self.evidence_gap_detector.detect(eligibility_result)
        critical_gaps = self.evidence_gap_detector.detect_critical(eligibility_result)
        bottleneck_internal, bottleneck_label = self.bottleneck_classifier.classify(
            eligibility_result, incumbent_risk or 0
        )

        # --- Decision tree ---
        decision = self._apply_decision_tree(
            eligibility_result=eligibility_result,
            qualification_score=qualification_score,
            critical_gaps=critical_gaps,
            incumbent_risk=incumbent_risk or 0,
        )

        failed_mandatory_ids = eligibility_result.failed_mandatory_ids

        reasoning = self.reasoning_builder.build(
            eligibility_result=eligibility_result,
            qualification_score=qualification_score,
            incumbent_risk_score=incumbent_risk or 0,
            primary_bottleneck=bottleneck_label,
            evidence_gaps=critical_gaps,
            recommendation=decision,
        )

        confidence, confidence_reason = self.confidence_estimator.estimate(
            eligibility_result=eligibility_result,
            qualification_score=qualification_score,
            competitive_strength=competitive_strength or 50,
            incumbent_risk=incumbent_risk or 0,
            incumbent_risk_threshold=self.config.INCUMBENT_RISK_HIGH_THRESHOLD,
        )

        rec = Recommendation(
            recommendation_id=generate_id("rec"),
            tender_id=tender_id,
            company_id=company_id,
            recommendation=decision,
            qualification_score=qualification_score,
            competitive_strength=competitive_strength,
            incumbent_risk=incumbent_risk,
            execution_risk=execution_risk,
            value_score=value_score,
            primary_bottleneck=bottleneck_label,
            bottleneck_category=bottleneck_internal,
            evidence_gaps=evidence_gaps,
            confidence=confidence,
            confidence_reason=confidence_reason,
            reasoning=reasoning,
            failed_mandatory_requirements=failed_mandatory_ids,
            pipeline_duration_seconds=pipeline_duration_seconds,
            created_at=now_iso(),
        )

        logger.info(
            "recommendation_produced",
            recommendation=decision,
            qualification_score=qualification_score,
            incumbent_risk=incumbent_risk,
            evidence_gaps_count=len(critical_gaps),
            confidence=round(confidence, 2),
        )

        return rec

    def _apply_decision_tree(
        self,
        eligibility_result: EligibilityResult,
        qualification_score: int,
        critical_gaps: list[str],
        incumbent_risk: int,
    ) -> str:
        """Apply the decision tree and return BID, REVIEW, or NO_BID."""

        # 1. Any mandatory requirement failed → NO BID
        if not eligibility_result.overall_pass:
            logger.debug("decision_no_bid_mandatory_fail")
            return "NO_BID"

        # 2. Score below minimum threshold → NO BID
        if qualification_score < self.config.QUALIFICATION_MARGINAL_THRESHOLD:
            logger.debug("decision_no_bid_low_score", score=qualification_score)
            return "NO_BID"

        # 3. Score in marginal range → REVIEW
        if qualification_score < self.config.QUALIFICATION_PASS_THRESHOLD:
            logger.debug("decision_review_marginal_score", score=qualification_score)
            return "REVIEW"

        # qualification_score >= 80 from here on

        # 4. Critical evidence gaps → REVIEW
        if critical_gaps:
            logger.debug("decision_review_evidence_gaps", gap_count=len(critical_gaps))
            return "REVIEW"

        # 5. High incumbent risk → REVIEW
        if incumbent_risk >= self.config.INCUMBENT_RISK_HIGH_THRESHOLD:
            logger.debug("decision_review_incumbent_risk", score=incumbent_risk)
            return "REVIEW"

        # 6. All conditions met → BID
        logger.debug("decision_bid_all_clear", score=qualification_score)
        return "BID"
