"""ToolCalledWith evaluator for checking tool call arguments."""

from mcp_eval.evaluators.base import EvaluatorContext
from mcp_eval.evaluators.shared import EvaluatorResult
from mcp_eval.evaluators.tool_was_called import ToolWasCalled


class ToolCalledWith(ToolWasCalled):
    """
    Evaluator that checks if a tool was called with specific arguments.

    Requires final metrics: True (runs after full OTEL trace is processed).
    """

    def __init__(self, tool_name: str, expected_args: dict):
        super().__init__(tool_name)
        self.expected_args = expected_args
        self.requires_final_metrics = True

    def evaluate_sync(self, ctx: EvaluatorContext) -> EvaluatorResult:
        tool_calls = [call for call in ctx.tool_calls if call.name == self.tool_name]
        matching_calls = [
            call
            for call in tool_calls
            if all(call.arguments.get(k) == v for k, v in self.expected_args.items())
        ]
        matches = bool(matching_calls)

        # Build actual message showing what tool calls were made
        if tool_calls:
            actual_calls = []
            for call in tool_calls:
                actual_calls.append(f"{self.tool_name}({call.arguments})")
            actual_msg = f"tool calls: {', '.join(actual_calls)}"
        else:
            actual_msg = f"tool '{self.tool_name}' not called"

        return EvaluatorResult(
            passed=matches,
            expected=f"tool '{self.tool_name}' called with {self.expected_args}",
            actual=actual_msg,
            details={
                "tool_name": self.tool_name,
                "expected_args": self.expected_args,
                "matching_calls": len(matching_calls),
                "total_calls": len(tool_calls),
                "actual_calls": [call.arguments for call in tool_calls],
            },
        )
