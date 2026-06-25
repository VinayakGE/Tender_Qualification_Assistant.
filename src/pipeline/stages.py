"""Pipeline stage tracking for observability."""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineStage:
    """Tracks the execution of a single pipeline stage.

    Used to measure duration and capture input/output summaries
    for observability and debugging.

    Usage:
        stage = PipelineStage(name="parser")
        stage.start()
        result = do_work()
        stage.complete(output_summary={"chars": len(result)})
    """

    name: str
    input_summary: dict[str, Any] = field(default_factory=dict)
    output_summary: dict[str, Any] = field(default_factory=dict)
    duration_seconds: float | None = None
    error: str | None = None
    _start_time: float = field(default=0.0, repr=False)

    def start(self, input_summary: dict[str, Any] | None = None) -> "PipelineStage":
        """Mark the stage as started.

        Args:
            input_summary: Optional dict describing the stage input.

        Returns:
            Self, for chaining.
        """
        self._start_time = time.perf_counter()
        if input_summary:
            self.input_summary = input_summary
        return self

    def complete(self, output_summary: dict[str, Any] | None = None) -> "PipelineStage":
        """Mark the stage as completed successfully.

        Args:
            output_summary: Optional dict describing the stage output.

        Returns:
            Self, for chaining.
        """
        self.duration_seconds = round(time.perf_counter() - self._start_time, 3)
        if output_summary:
            self.output_summary = output_summary
        return self

    def fail(self, error: str) -> "PipelineStage":
        """Mark the stage as failed.

        Args:
            error: Error message or exception string.

        Returns:
            Self, for chaining.
        """
        self.duration_seconds = round(time.perf_counter() - self._start_time, 3)
        self.error = error
        return self

    @property
    def succeeded(self) -> bool:
        """Return True if the stage completed without error."""
        return self.error is None and self.duration_seconds is not None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dict for logging or storage."""
        return {
            "stage": self.name,
            "duration_seconds": self.duration_seconds,
            "succeeded": self.succeeded,
            "error": self.error,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
        }


@dataclass
class PipelineRun:
    """Aggregates all stage records for a single pipeline run."""

    tender_id: str
    company_id: str
    stages: list[PipelineStage] = field(default_factory=list)
    _run_start: float = field(default=0.0, repr=False)

    def __post_init__(self) -> None:
        self._run_start = time.perf_counter()

    def add_stage(self, stage: PipelineStage) -> None:
        """Add a completed stage to the run record."""
        self.stages.append(stage)

    @property
    def total_duration_seconds(self) -> float:
        """Total elapsed time for the pipeline run."""
        return round(time.perf_counter() - self._run_start, 3)

    @property
    def succeeded(self) -> bool:
        """Return True if all stages succeeded."""
        return all(s.succeeded for s in self.stages)

    @property
    def failed_stage(self) -> PipelineStage | None:
        """Return the first failed stage, or None."""
        return next((s for s in self.stages if not s.succeeded), None)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dict for logging."""
        return {
            "tender_id": self.tender_id,
            "company_id": self.company_id,
            "total_duration_seconds": self.total_duration_seconds,
            "succeeded": self.succeeded,
            "stages": [s.to_dict() for s in self.stages],
        }
