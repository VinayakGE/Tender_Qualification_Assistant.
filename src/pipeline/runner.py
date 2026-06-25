"""Pipeline orchestrator — runs all stages in order for a single tender."""

from pathlib import Path

from src.extractor.metadata import MetadataExtractor
from src.extractor.requirement_extractor import RequirementExtractor
from src.ledger.decisions import DecisionLedger
from src.parser.cleaner import TextCleaner
from src.parser.pdf_parser import PDFParser
from src.pipeline.stages import PipelineRun, PipelineStage
from src.qualification.eligibility import EligibilityChecker
from src.recommendation.engine import Recommendation, RecommendationEngine
from src.recommendation.explanation import ExplanationGenerator
from src.scoring.competitiveness import CompetitivenessScorer
from src.scoring.execution_risk import ExecutionRiskScorer
from src.scoring.incumbent_risk import IncumbentRiskScorer
from src.scoring.value_score import ValueScorer
from src.utils.config import get_config
from src.utils.helpers import ensure_dir, load_json, now_iso, save_json, slugify
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineRunner:
    """Orchestrates the full qualification pipeline from PDF to recommendation.

    Stages:
    1. Parse PDF → clean text
    2. Extract metadata + requirements
    3. Check eligibility
    4. Compute five scores
    5. Classify bottleneck
    6. Produce recommendation
    7. Generate LLM explanation
    8. Append to decision ledger
    9. Save recommendation JSON to outcomes/
    """

    def __init__(self) -> None:
        self.config = get_config()
        ensure_dir(self.config.OUTCOMES_DIR)
        ensure_dir(self.config.PARSED_DIR)

    def run(
        self,
        pdf_path: Path | str,
        company_profile_path: Path | str,
    ) -> Recommendation:
        """Run the full pipeline on a single tender PDF.

        Args:
            pdf_path: Path to the tender PDF.
            company_profile_path: Path to the company profile JSON.

        Returns:
            Recommendation object.

        Raises:
            FileNotFoundError: If PDF or company profile does not exist.
            RuntimeError: If any pipeline stage fails critically.
        """
        pdf_path = Path(pdf_path)
        profile_path = Path(company_profile_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"Tender PDF not found: {pdf_path}")
        if not profile_path.exists():
            raise FileNotFoundError(f"Company profile not found: {profile_path}")

        company_profile = load_json(profile_path)
        company_id = company_profile.get("company_id", slugify(profile_path.stem))
        tender_id = slugify(pdf_path.stem)

        run = PipelineRun(tender_id=tender_id, company_id=company_id)

        logger.info(
            "pipeline_started",
            tender_id=tender_id,
            company_id=company_id,
            pdf_path=str(pdf_path),
        )

        # Stage 1: Parse
        stage = PipelineStage("parser").start({"pdf_path": str(pdf_path)})
        try:
            raw_text = PDFParser(
                ocr_fallback_threshold=self.config.OCR_FALLBACK_CHARS_PER_PAGE
            ).extract_text(pdf_path)
            clean_text = TextCleaner().clean(raw_text)
            stage.complete({"text_chars": len(clean_text)})
        except Exception as exc:
            stage.fail(str(exc))
            run.add_stage(stage)
            raise RuntimeError(f"Parser failed: {exc}") from exc
        run.add_stage(stage)

        # Save parsed text (version metadata added after extraction)
        _parsed_payload = {"tender_id": tender_id, "clean_text": clean_text, "parsed_at": now_iso()}

        # Stage 2: Extract requirements
        stage = PipelineStage("extractor").start({"text_chars": len(clean_text)})
        try:
            metadata = MetadataExtractor().extract(clean_text)
            extraction = RequirementExtractor().extract(clean_text, tender_id=tender_id)
            requirements = extraction.requirements
            extraction_warnings = extraction.warnings
            stage.complete(
                {
                    "requirements_found": len(requirements),
                    "extraction_warnings": len(extraction_warnings),
                }
            )
        except Exception as exc:
            stage.fail(str(exc))
            run.add_stage(stage)
            raise RuntimeError(f"Extractor failed: {exc}") from exc
        run.add_stage(stage)

        # Save parsed text + version provenance
        _parsed_payload.update(
            {
                "extractor_version": extraction.extractor_version,
                "prompt_version": extraction.prompt_version,
                "schema_version": extraction.schema_version,
            }
        )
        save_json(_parsed_payload, self.config.PARSED_DIR / f"{tender_id}.json")

        # Stage 3: Qualify
        stage = PipelineStage("qualification").start({"requirements": len(requirements)})
        try:
            eligibility_result = EligibilityChecker().check(requirements, company_profile)
            stage.complete(
                {
                    "overall_pass": eligibility_result.overall_pass,
                    "mandatory_fails": eligibility_result.mandatory_fail_count,
                }
            )
        except Exception as exc:
            stage.fail(str(exc))
            run.add_stage(stage)
            raise RuntimeError(f"Qualification failed: {exc}") from exc
        run.add_stage(stage)

        # Stage 4: Score
        stage = PipelineStage("scoring").start()
        try:
            competitive_strength = CompetitivenessScorer().score(
                company_profile=company_profile,
                contract_value_inr=metadata.contract_value_inr,
                tender_sector=metadata.tender_type,
                requirements_count=len(requirements),
            )
            incumbent_risk = IncumbentRiskScorer().score(
                tender_text=clean_text,
                contract_duration_months=metadata.contract_duration_months,
            )
            from src.scoring.qualification_score import QualificationScorer

            qual_score = QualificationScorer().score(eligibility_result)
            execution_risk = ExecutionRiskScorer().score(
                tender_text=clean_text,
                company_profile=company_profile,
                contract_duration_months=metadata.contract_duration_months,
                requirements_count=len(requirements),
                qualification_score=qual_score,
            )
            value_score = ValueScorer().score(
                company_profile=company_profile,
                contract_value_inr=metadata.contract_value_inr,
                tender_sector=metadata.tender_type,
                qualification_score=qual_score,
                competitive_strength=competitive_strength,
                incumbent_risk=incumbent_risk,
            )
            stage.complete(
                {
                    "qualification_score": qual_score,
                    "competitive_strength": competitive_strength,
                    "incumbent_risk": incumbent_risk,
                }
            )
        except Exception as exc:
            stage.fail(str(exc))
            run.add_stage(stage)
            raise RuntimeError(f"Scoring failed: {exc}") from exc
        run.add_stage(stage)

        # Stage 5-6: Recommend
        stage = PipelineStage("recommendation").start()
        try:
            recommendation = RecommendationEngine().recommend(
                eligibility_result=eligibility_result,
                tender_id=tender_id,
                company_id=company_id,
                competitive_strength=competitive_strength,
                incumbent_risk=incumbent_risk,
                execution_risk=execution_risk,
                value_score=value_score,
                extraction_warnings=extraction_warnings,
                pipeline_duration_seconds=run.total_duration_seconds,
            )
            stage.complete({"recommendation": recommendation.recommendation})
        except Exception as exc:
            stage.fail(str(exc))
            run.add_stage(stage)
            raise RuntimeError(f"Recommendation engine failed: {exc}") from exc
        run.add_stage(stage)

        # Stage 7: LLM explanation (non-critical — failure does not abort pipeline)
        stage = PipelineStage("explanation").start()
        try:
            explanation = ExplanationGenerator().generate(recommendation)
            recommendation.reasoning = explanation
            stage.complete({"explanation_chars": len(explanation)})
        except Exception as exc:
            stage.fail(str(exc))
            logger.warning("explanation_stage_failed", error=str(exc))
        run.add_stage(stage)

        # Stage 8: Ledger
        stage = PipelineStage("ledger").start()
        try:
            DecisionLedger().append(recommendation)
            stage.complete()
        except Exception as exc:
            stage.fail(str(exc))
            logger.error("ledger_append_failed", error=str(exc))
        run.add_stage(stage)

        # Stage 9: Save outcome JSON
        output_path = self.config.OUTCOMES_DIR / f"{tender_id}_recommendation.json"
        save_json(recommendation.to_dict(), output_path)

        logger.info(
            "pipeline_complete",
            tender_id=tender_id,
            recommendation=recommendation.recommendation,
            duration_seconds=run.total_duration_seconds,
            output_path=str(output_path),
        )

        return recommendation
