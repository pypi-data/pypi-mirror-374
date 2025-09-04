"""Metrics collection and processing from OTEL traces."""

import json
from typing import List, Dict, Any
from dataclasses import dataclass, field

from mcp_agent.tracing.token_counter import TokenCounter


def unflatten_attributes(attributes: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """Unflatten values from span attributes with dot/list notation support.

    This reconstructs nested dicts and lists from flattened keys like:
    - "result.content.0.text" -> {"result": {"content": [{"text": ...}]}}
    - "mcp.request.argument.query" -> {"mcp": {"request": {"argument": {"query": ...}}}}

    Args:
        attributes: Span attributes dictionary
        prefix: Prefix to look for in attribute keys

    Returns:
        Nested dictionary with unflattened values (lists supported where indices are present)
    """

    def _ensure_list_size(lst: list, index: int):
        if index >= len(lst):
            lst.extend([None] * (index + 1 - len(lst)))

    def _set_path(root: Any, parts: list[str], value: Any) -> Any:
        # Returns the possibly new root after setting the path
        if not parts:
            return root

        key = parts[0]
        is_index = False
        idx = None
        if key.isdigit():
            is_index = True
            idx = int(key)

        # If we're at the last part, set the value
        if len(parts) == 1:
            if is_index:
                if not isinstance(root, list):
                    root = [] if root is None or isinstance(root, (dict,)) else []
                _ensure_list_size(root, idx)  # type: ignore[arg-type]
                root[idx] = value  # type: ignore[index]
            else:
                if not isinstance(root, dict):
                    root = {} if root is None or isinstance(root, (list,)) else {}
                root[key] = value  # type: ignore[index]
            return root

        # Not last part – ensure container and recurse
        if is_index:
            if not isinstance(root, list):
                root = []
            _ensure_list_size(root, idx)  # type: ignore[arg-type]
            next_val = root[idx]
            if next_val is None:
                # Decide next container type based on the next key
                next_key = parts[1]
                next_val = [] if next_key.isdigit() else {}
            root[idx] = _set_path(next_val, parts[1:], value)  # type: ignore[index]
            return root
        else:
            if not isinstance(root, dict):
                root = {}
            next_val = root.get(key)
            if next_val is None:
                next_key = parts[1] if len(parts) > 1 else ""
                next_val = [] if next_key.isdigit() else {}
            root[key] = _set_path(next_val, parts[1:], value)
            return root

    result: Dict[str, Any] = {}
    for full_key, value in attributes.items():
        if not full_key.startswith(prefix):
            continue
        path = full_key[len(prefix) :].split(".")
        result = _set_path(result, path, value)  # type: ignore[assignment]

    return result


@dataclass
class ToolCall:
    """Represents a single tool call."""

    name: str
    arguments: Dict[str, Any]
    result: Any
    start_time: float
    end_time: float
    is_error: bool = False
    error_message: str | None = None
    server_name: str | None = None

    @property
    def duration_ms(self) -> float:
        return (self.end_time - self.start_time) * 1000


@dataclass
class LLMMetrics:
    """LLM usage metrics."""

    model_name: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_estimate: float = 0.0
    latency_ms: float = 0.0


@dataclass
class ToolCoverage:
    """Tool coverage metrics for a server."""

    server_name: str
    available_tools: List[str] = field(default_factory=list)
    used_tools: List[str] = field(default_factory=list)

    @property
    def coverage_percentage(self) -> float:
        if not self.available_tools:
            return 0.0
        return (len(self.used_tools) / len(self.available_tools)) * 100

    @property
    def unused_tools(self) -> List[str]:
        return [tool for tool in self.available_tools if tool not in self.used_tools]


@dataclass
class TestMetrics:
    """Comprehensive test metrics derived from OTEL traces."""

    # Tool usage
    tool_calls: List[ToolCall] = field(default_factory=list)
    unique_tools_used: List[str] = field(default_factory=list)
    unique_servers_used: List[str] = field(default_factory=list)

    # Tool coverage per server
    tool_coverage: Dict[str, ToolCoverage] = field(default_factory=dict)

    # Execution metrics
    iteration_count: int = 0
    total_duration_ms: float = 0.0
    latency_ms: float = 0.0

    # LLM metrics
    llm_metrics: LLMMetrics = field(default_factory=LLMMetrics)

    # Performance metrics
    parallel_tool_calls: int = 0
    error_count: int = 0
    success_rate: float = 1.0

    # Cost estimation
    cost_estimate: float = 0.0

    # Detailed performance breakdown
    llm_time_ms: float = 0.0
    tool_time_ms: float = 0.0
    reasoning_time_ms: float = 0.0
    idle_time_ms: float = 0.0
    max_concurrent_operations: int = 0


@dataclass
class TraceSpan:
    """Represents a single OTEL span from trace file."""

    name: str
    context: Dict[str, str]
    parent: Dict[str, str] | None
    start_time: int  # nanoseconds since epoch
    end_time: int  # nanoseconds since epoch
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_json(cls, json_line: str) -> "TraceSpan":
        """Create TraceSpan from JSONL line."""
        from datetime import datetime

        data = json.loads(json_line)

        # Helper to parse timestamps
        def parse_timestamp(ts):
            if isinstance(ts, (int, float)):
                return int(ts)
            elif isinstance(ts, str):
                # Parse ISO format timestamp to nanoseconds
                if "T" in ts and ts.endswith("Z"):
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    return int(dt.timestamp() * 1e9)
                else:
                    # Try to parse as a number string
                    return int(float(ts))
            return 0

        # Handle both standard OTEL export format and Jaeger format
        if "name" in data:
            # Standard OTEL format
            return cls(
                name=data.get("name", ""),
                context=data.get("context", {}),
                parent=data.get("parent"),
                start_time=parse_timestamp(data.get("start_time", 0)),
                end_time=parse_timestamp(data.get("end_time", 0)),
                attributes=data.get("attributes", {}),
                events=data.get("events", []),
            )
        else:
            # Jaeger format fallback (from original implementation)
            return cls(
                name=data.get("operationName", ""),
                context={
                    "span_id": data.get("spanID", ""),
                    "trace_id": data.get("traceID", ""),
                },
                parent=data.get("references", [{}])[0]
                if data.get("references")
                else None,
                start_time=parse_timestamp(data.get("startTime", 0)),
                end_time=parse_timestamp(data.get("startTime", 0))
                + data.get("duration", 0),
                attributes=data.get("tags", {}),
                events=data.get("logs", []),
            )


def process_spans(spans: List[TraceSpan]) -> TestMetrics:
    """Process OTEL spans into comprehensive metrics."""
    metrics = TestMetrics()

    if not spans:
        return metrics

    # Calculate total duration
    if spans:
        start_times = [span.start_time for span in spans]
        end_times = [span.end_time for span in spans]
        metrics.total_duration_ms = (max(end_times) - min(start_times)) / 1e6

    # Process tool calls
    tool_calls = []
    for span in spans:
        if _is_tool_call_span(span):
            tool_call = _extract_tool_call(span)
            if tool_call:
                tool_calls.append(tool_call)

    metrics.tool_calls = tool_calls
    metrics.unique_tools_used = list(set(call.name for call in tool_calls))

    # Extract unique servers from tool calls
    servers = set()
    for call in tool_calls:
        if hasattr(call, "server_name") and call.server_name:
            servers.add(call.server_name)
    metrics.unique_servers_used = list(servers)

    # Calculate error metrics
    error_calls = [call for call in tool_calls if call.is_error]
    metrics.error_count = len(error_calls)
    metrics.success_rate = (
        1.0 - (len(error_calls) / len(tool_calls)) if tool_calls else 1.0
    )

    # Process LLM metrics and time breakdown
    llm_spans = [span for span in spans if _is_llm_span(span)]
    if llm_spans:
        metrics.llm_metrics = _extract_llm_metrics(llm_spans)
        # Sum LLM time from span durations
        metrics.llm_time_ms = sum((s.end_time - s.start_time) / 1e6 for s in llm_spans)

    # Calculate iteration count (number of agent turns)
    # Method 1: Look for completion turn counters in events
    max_turn = 0
    for span in spans:
        for event in span.events:
            if "attributes" in event and "completion.response.turn" in event.get(
                "attributes", {}
            ):
                turn_num = event["attributes"]["completion.response.turn"]
                max_turn = max(max_turn, turn_num + 1)  # Convert 0-based to count

    if max_turn > 0:
        metrics.iteration_count = max_turn
    elif llm_spans:
        # Method 2: Count actual LLM API calls
        metrics.iteration_count = len(llm_spans)
    else:
        # Method 3: Count high-level generate calls as a last resort
        generate_spans = [
            span
            for span in spans
            if ".generate" in span.name and "AugmentedLLM" in span.name
        ]
        metrics.iteration_count = len(generate_spans) if generate_spans else 1

    # Calculate parallel tool calls
    metrics.parallel_tool_calls = _calculate_parallel_calls(tool_calls)

    # Aggregate latency
    if tool_calls:
        metrics.latency_ms = sum(call.duration_ms for call in tool_calls)

    # Tool time is sum of tool call durations
    if tool_calls:
        metrics.tool_time_ms = sum(call.duration_ms for call in tool_calls)

    # Reasoning time heuristic: spans with 'reason' in name
    reasoning_spans = [s for s in spans if "reason" in s.name.lower()]
    metrics.reasoning_time_ms = sum(
        (s.end_time - s.start_time) / 1e6 for s in reasoning_spans
    )

    # Idle time heuristic: total time - active time (llm + tool + reasoning)
    if spans:
        total_time_ms = (
            max(s.end_time for s in spans) - min(s.start_time for s in spans)
        ) / 1e6
        active_time_ms = (
            metrics.llm_time_ms + metrics.tool_time_ms + metrics.reasoning_time_ms
        )
        metrics.idle_time_ms = max(0.0, total_time_ms - active_time_ms)

    # Max concurrency across LLM and tool spans
    metrics.max_concurrent_operations = _calculate_max_concurrent_spans(
        [s for s in spans if _is_llm_span(s) or _is_tool_call_span(s)]
    )

    # Cost estimation
    metrics.cost_estimate = _estimate_cost(metrics.llm_metrics)
    # Keep llm_metrics.cost_estimate in sync so UIs that read from llm_metrics
    # (e.g., HTML report) display the correct value
    try:
        metrics.llm_metrics.cost_estimate = metrics.cost_estimate
    except Exception:
        # Be defensive in case llm_metrics is missing or immutable
        pass

    return metrics


def _is_tool_call_span(span: TraceSpan) -> bool:
    """Determine if span represents a tool call."""
    # We want to capture the MCPAggregator.call_tool spans which are the actual tool executions
    # These have both the tool name and the actual results
    # This avoids counting the same tool call multiple times from different layers
    if span.name == "MCPAggregator.call_tool":
        # Must have a tool name to be valid
        has_tool_name = (
            span.attributes.get("gen_ai.tool.name") is not None
            or span.attributes.get("parsed_tool_name") is not None
        )
        return has_tool_name

    return False


def _is_llm_span(span: TraceSpan) -> bool:
    """Determine if span represents an LLM call."""
    return (
        span.attributes.get("gen_ai.system") is not None
        or "llm" in span.name.lower()
        or "generate" in span.name.lower()
    )


def _extract_tool_call(span: TraceSpan) -> ToolCall | None:
    """Extract tool call information from span."""
    try:
        # For MCPAggregator.call_tool spans, the parsed_tool_name contains the clean tool name
        tool_name = span.attributes.get("parsed_tool_name")
        server_name = span.attributes.get("parsed_server_name")

        # Fallback to mcp.tool.name if parsed_tool_name is not available
        if not tool_name:
            tool_name = span.attributes.get("mcp.tool.name")

        # If still no tool name, try to extract from gen_ai.tool.name (servername_toolname format)
        if not tool_name:
            gen_ai_tool_name = span.attributes.get("gen_ai.tool.name")
            if gen_ai_tool_name and "_" in gen_ai_tool_name:
                # The gen_ai.tool.name has format servername_toolname
                # In MCPAggregator spans, we also have parsed_server_name
                if not server_name:
                    server_name = span.attributes.get("parsed_server_name")

                if server_name and gen_ai_tool_name.startswith(server_name + "_"):
                    # Extract tool name after the server prefix
                    tool_name = gen_ai_tool_name[len(server_name) + 1 :]
                else:
                    # Simple split on first underscore as fallback
                    parts = gen_ai_tool_name.split("_", 1)
                    tool_name = parts[1] if len(parts) > 1 else gen_ai_tool_name
                    if not server_name and len(parts) > 1:
                        server_name = parts[0]
            elif gen_ai_tool_name:
                tool_name = gen_ai_tool_name

        # Extract arguments from the span attributes
        arguments = {}

        # MCPAggregator spans have arguments directly under "arguments."
        if span.name == "MCPAggregator.call_tool":
            arguments = unflatten_attributes(span.attributes, "arguments.")
        else:
            # Try other patterns for different span types
            if span.attributes.get("mcp.request.argument.url"):
                arguments = unflatten_attributes(
                    span.attributes, "mcp.request.argument."
                )
            elif span.attributes.get("request.params.arguments.url"):
                arguments = unflatten_attributes(
                    span.attributes, "request.params.arguments."
                )

        # Extract result
        result = unflatten_attributes(span.attributes, "result.")

        is_error = span.attributes.get("result.isError", False)
        error_message = span.attributes.get("error.message")

        return ToolCall(
            name=tool_name or "",
            arguments=arguments,
            result=result,
            start_time=span.start_time / 1e9,
            end_time=span.end_time / 1e9,
            is_error=is_error,
            error_message=error_message,
            server_name=server_name,
        )
    except Exception:
        return None


def _extract_llm_metrics(llm_spans: List[TraceSpan]) -> LLMMetrics:
    """Extract LLM metrics from spans."""
    metrics = LLMMetrics()

    for span in llm_spans:
        attrs = span.attributes

        # Model information
        if not metrics.model_name:
            metrics.model_name = attrs.get("gen_ai.request.model", "")

        # Token usage - try multiple possible attribute names
        metrics.input_tokens += (
            attrs.get("gen_ai.usage.input_tokens", 0)
            or attrs.get("llm.usage.input_tokens", 0)
            or attrs.get("input_tokens", 0)
        )
        metrics.output_tokens += (
            attrs.get("gen_ai.usage.output_tokens", 0)
            or attrs.get("llm.usage.output_tokens", 0)
            or attrs.get("output_tokens", 0)
        )

        # Latency
        duration_ms = (span.end_time - span.start_time) / 1e6
        metrics.latency_ms += duration_ms

    metrics.total_tokens = metrics.input_tokens + metrics.output_tokens
    return metrics


def _calculate_parallel_calls(tool_calls: List[ToolCall]) -> int:
    """Calculate maximum number of parallel tool calls."""
    if len(tool_calls) <= 1:
        return 0

    events = []
    for call in tool_calls:
        events.append(("start", call.start_time))
        events.append(("end", call.end_time))

    events.sort(key=lambda x: x[1])

    max_concurrent = 0
    current_concurrent = 0

    for event_type, _ in events:
        if event_type == "start":
            current_concurrent += 1
            max_concurrent = max(max_concurrent, current_concurrent)
        else:
            current_concurrent -= 1

    return max_concurrent - 1


def _calculate_max_concurrent_spans(spans: List[TraceSpan]) -> int:
    """Calculate maximum number of concurrent spans in a set."""
    if len(spans) <= 1:
        return 0

    events = []
    for s in spans:
        events.append(("start", s.start_time))
        events.append(("end", s.end_time))

    events.sort(key=lambda x: x[1])

    max_concurrent = 0
    current = 0
    for event_type, _ in events:
        if event_type == "start":
            current += 1
            max_concurrent = max(max_concurrent, current)
        else:
            current -= 1

    return max_concurrent


def _estimate_cost(llm_metrics: LLMMetrics) -> float:
    """Estimate cost based on token usage using mcp-agent's TokenCounter."""
    try:
        # Create a TokenCounter instance to use its cost calculation
        counter = TokenCounter()

        # Use the model name from metrics if available
        model_name = llm_metrics.model_name if llm_metrics.model_name else "unknown"

        # Calculate cost using mcp-agent's pricing data
        cost = counter.calculate_cost(
            model_name=model_name,
            input_tokens=llm_metrics.input_tokens,
            output_tokens=llm_metrics.output_tokens,
            provider=None,  # Will be inferred from model name
        )

        return cost
    except Exception:
        # Fallback to simple estimation if TokenCounter is not available
        cost_per_input_token = 0.000001
        cost_per_output_token = 0.000003

        return (
            llm_metrics.input_tokens * cost_per_input_token
            + llm_metrics.output_tokens * cost_per_output_token
        )


# Metric registration for extensibility
_custom_metrics: Dict[str, callable] = {}


def register_metric(name: str, processor: callable):
    """Register a custom metric processor."""
    _custom_metrics[name] = processor
