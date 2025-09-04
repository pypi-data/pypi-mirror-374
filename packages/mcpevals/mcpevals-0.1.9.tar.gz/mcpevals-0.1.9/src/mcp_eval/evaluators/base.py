"""Base evaluator classes and context."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar, TYPE_CHECKING
from dataclasses import dataclass

from mcp_eval.metrics import TestMetrics
from mcp_eval.otel.span_tree import SpanTree

if TYPE_CHECKING:
    from mcp_eval.evaluators import EvaluatorResult


InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


@dataclass
class EvaluatorContext(Generic[InputType, OutputType]):
    """Context provided to evaluators during evaluation."""

    inputs: InputType
    output: OutputType
    expected_output: OutputType | None
    metadata: Dict[str, Any] | None
    metrics: TestMetrics
    span_tree: SpanTree | None = None

    @property
    def tool_calls(self):
        """Convenience property to access tool calls from metrics."""
        return self.metrics.tool_calls

    @property
    def llm_metrics(self):
        """Convenience property to access LLM metrics."""
        return self.metrics.llm_metrics


class Evaluator(ABC, Generic[InputType, OutputType]):
    """Base class for all evaluators."""

    # If True, evaluator prefers to run after the full trace/metrics are finalized
    # (i.e., at session end). Defaults to False for immediate-capable checks.
    requires_final_metrics: bool = False

    @abstractmethod
    async def evaluate(
        self, ctx: EvaluatorContext[InputType, OutputType]
    ) -> "EvaluatorResult":
        """
        Evaluate the test case.

        Returns:
            EvaluatorResult: Detailed evaluation results
        """
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluator to dictionary for serialization."""
        return {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Evaluator":
        """Create evaluator from dictionary."""
        return cls(**data)


class SyncEvaluator(Evaluator[InputType, OutputType]):
    """Base class for synchronous evaluators."""

    async def evaluate(
        self, ctx: EvaluatorContext[InputType, OutputType]
    ) -> "EvaluatorResult":
        """Async wrapper for sync evaluation."""
        return self.evaluate_sync(ctx)

    @abstractmethod
    def evaluate_sync(
        self, ctx: EvaluatorContext[InputType, OutputType]
    ) -> "EvaluatorResult":
        """Synchronous evaluation method."""
        pass
