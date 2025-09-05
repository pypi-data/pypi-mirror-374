"""Advanced feature tests demonstrating deep analysis capabilities."""

from mcp_eval import Expect
from mcp_eval import task, setup

# Note: test code references Expect.* helpers for evaluators
from mcp_eval.evaluators import EvaluatorResult
from mcp_eval.session import TestAgent, TestSession


@setup
def configure_advanced_tests():
    """Servers and agents are configured via mcpeval.yaml or mcp-agent config."""


@task("Test span tree analysis for fetch operations")
async def test_span_tree_analysis(agent: TestAgent, session: TestSession):
    """Test advanced span tree analysis capabilities."""
    await agent.generate_str(
        "Fetch content from https://example.com, then fetch https://httpbin.org/json, "
        "and compare what you found"
    )

    # Expected tool sequence
    await session.assert_that(
        Expect.tools.sequence(["fetch", "fetch"], allow_other_calls=True),
        name="correct_fetch_sequence",
    )

    # Wait for completion and analyze span tree
    span_tree = session.get_span_tree()
    if span_tree:
        # Check for performance issues
        rephrasing_loops = span_tree.get_llm_rephrasing_loops()
        if rephrasing_loops:
            session._record_evaluation_result(
                "no_rephrasing_loops",
                EvaluatorResult(passed=False, expected=0, actual=len(rephrasing_loops)),
                f"Found {len(rephrasing_loops)} LLM rephrasing loops",
            )
        else:
            session._record_evaluation_result(
                "no_rephrasing_loops", EvaluatorResult(passed=True), None
            )

        # Analyze tool path efficiency
        golden_paths = {"multi_fetch": ["fetch", "fetch"]}
        path_analyses = span_tree.get_inefficient_tool_paths(golden_paths)
        for analysis in path_analyses:
            efficiency_passed = analysis.efficiency_score >= 0.8
            session._record_evaluation_result(
                "path_efficiency",
                EvaluatorResult(
                    passed=efficiency_passed,
                    expected=">= 0.8",
                    actual=analysis.efficiency_score,
                ),
                f"Tool path efficiency: {analysis.efficiency_score:.2f}",
            )

        # Check error recovery
        recovery_sequences = span_tree.get_error_recovery_sequences()
        if recovery_sequences:
            successful_recoveries = sum(
                1 for seq in recovery_sequences if seq.recovery_successful
            )
            total_recoveries = len(recovery_sequences)
            passed = successful_recoveries == total_recoveries
            session._record_evaluation_result(
                "error_recovery",
                EvaluatorResult(
                    passed=passed,
                    expected=total_recoveries,
                    actual=successful_recoveries,
                ),
                f"Error recovery: {successful_recoveries}/{total_recoveries} successful",
            )


@task("Test enhanced LLM judge with structured output")
async def test_enhanced_llm_judge(agent: TestAgent, session: TestSession):
    """Test the enhanced LLM judge with structured JSON output."""
    response = await agent.generate_str(
        "Fetch https://httpbin.org/html and provide a detailed analysis of the content structure"
    )

    # Basic tool check
    await session.assert_that(
        Expect.tools.was_called("fetch"), name="fetch_called_for_analysis"
    )

    # Enhanced LLM judge with structured output
    enhanced_judge = Expect.judge.llm(
        rubric="""
        Evaluate the response based on these criteria:
        1. Successfully fetched the HTML content
        2. Provided structural analysis of the content
        3. Demonstrated understanding of HTML elements
        4. Gave specific details about what was found
        """,
        min_score=0.85,
        include_input=True,
        require_reasoning=True,
    )

    await session.assert_that(
        enhanced_judge, name="detailed_content_analysis", response=response
    )


@task("Test fetch server capabilities under load")
async def test_fetch_performance_analysis(agent: TestAgent, session: TestSession):
    """Test fetch server performance characteristics."""
    response = await agent.generate_str(
        "Fetch content from these URLs in sequence: "
        "https://example.com, https://httpbin.org/json, https://httpbin.org/html. "
        "Provide a summary of each."
    )

    # Should make multiple fetch calls
    await session.assert_that(
        Expect.tools.was_called("fetch", min_times=3), name="multiple_fetch_calls"
    )

    # Performance evaluation
    performance_judge = Expect.judge.llm(
        rubric="Response should demonstrate efficient fetching of multiple URLs with appropriate summaries for each",
        min_score=0.8,
    )

    await session.assert_that(
        performance_judge, name="multi_url_performance", response=response
    )

    # Check final metrics
    metrics = session.get_metrics()

    # Custom performance checks
    total_duration = metrics.total_duration_ms
    if total_duration < 30000:  # Less than 30 seconds
        session._record_evaluation_result(
            "reasonable_duration", EvaluatorResult(passed=True), None
        )
    else:
        session._record_evaluation_result(
            "reasonable_duration", False, f"Duration too long: {total_duration:.0f}ms"
        )

    # Check tool call efficiency
    tool_calls = len(metrics.tool_calls)
    if tool_calls >= 3:  # Expected number of fetch calls
        session._record_evaluation_result(
            "sufficient_tool_calls", EvaluatorResult(passed=True), None
        )
    else:
        session._record_evaluation_result(
            "sufficient_tool_calls",
            EvaluatorResult(passed=False, expected=">= 3", actual=tool_calls),
            f"Only {tool_calls} tool calls made",
        )


@task("Test fetch server error recovery patterns")
async def test_comprehensive_error_recovery(agent: TestAgent, session: TestSession):
    """Test comprehensive error recovery patterns."""
    response = await agent.generate_str(
        "Try to fetch these URLs in order, and for any that fail, "
        "try an alternative approach: "
        "1. https://invalid-domain-12345.com "
        "2. https://example.com "
        "3. https://httpbin.org/status/404 "
        "4. https://httpbin.org/json"
    )

    # Should make multiple fetch attempts
    await session.assert_that(
        Expect.tools.was_called("fetch", min_times=3), name="multiple_fetch_attempts"
    )

    # Comprehensive error handling evaluation
    error_recovery_judge = Expect.judge.llm(
        rubric="""
        Evaluate the agent's error recovery capabilities:
        1. Attempts to fetch invalid URLs and recognizes failures
        2. Successfully fetches valid URLs
        3. Handles HTTP errors appropriately
        4. Provides clear status for each URL attempt
        5. Demonstrates resilience and appropriate fallback behavior
        """,
        min_score=0.8,
        include_input=True,
    )

    await session.assert_that(
        error_recovery_judge, name="comprehensive_error_recovery", response=response
    )
