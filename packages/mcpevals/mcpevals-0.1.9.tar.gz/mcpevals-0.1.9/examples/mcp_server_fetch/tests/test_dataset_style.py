"""Dataset-style evaluation tests."""

import asyncio
from mcp_eval import Case, Dataset, test_session
from mcp_eval import ToolWasCalled, ResponseContains, LLMJudge


# Define test cases for dataset evaluation
basic_fetch_cases = [
    Case(
        name="fetch_example_com",
        inputs="Fetch the content from https://example.com",
        expected_output=None,  # Don't expect exact output from LLM
        metadata={"difficulty": "easy", "category": "basic_functionality"},
        evaluators=[
            ToolWasCalled("fetch"),
            ResponseContains(
                "example", case_sensitive=False
            ),  # Just check it mentions example
        ],
    ),
    Case(
        name="fetch_json_content",
        inputs="Fetch https://httpbin.org/json and tell me about the content",
        metadata={"difficulty": "medium", "category": "content_processing"},
        evaluators=[
            ToolWasCalled("fetch"),
            ResponseContains("json", case_sensitive=False),
            LLMJudge("Response correctly identifies and describes JSON content"),
        ],
    ),
    Case(
        name="fetch_html_content",
        inputs="Fetch https://httpbin.org/html and summarize what you find",
        metadata={"difficulty": "medium", "category": "content_processing"},
        evaluators=[
            ToolWasCalled("fetch"),
            LLMJudge("Response provides a meaningful summary of the HTML content"),
        ],
    ),
    Case(
        name="handle_fetch_error",
        inputs="Try to fetch https://this-domain-does-not-exist-xyz123.com",
        metadata={"difficulty": "medium", "category": "error_handling"},
        evaluators=[
            ToolWasCalled("fetch"),  # Should attempt the fetch
            LLMJudge(
                "Response appropriately handles the fetch error and explains what went wrong"
            ),
            # Note: Don't use ToolSuccessRate here as we expect the fetch to fail
        ],
    ),
    Case(
        name="fetch_with_chunking",
        inputs="Fetch https://httpbin.org/json and if the content is truncated, continue fetching until complete",
        metadata={"difficulty": "hard", "category": "advanced_features"},
        evaluators=[
            ToolWasCalled("fetch", min_times=1),
            LLMJudge(
                "Response demonstrates awareness of content truncation and appropriate handling"
            ),
        ],
    ),
]

# Create dataset
fetch_dataset = Dataset(
    name="MCP Fetch Server Basic Tests",
    cases=basic_fetch_cases,
    server_name="fetch",
    # Agent configuration is now driven by global provider/model settings in mcpeval.yaml
    evaluators=[
        # Global evaluators applied to all cases
        ToolWasCalled(
            "fetch", min_times=1
        ),  # Every test should call fetch at least once
        # LLMJudge("Response is relevant and addresses the user's request appropriately"),
    ],
)


async def fetch_task_function(inputs: str) -> str:
    """Task function for dataset evaluation."""
    async with test_session("dataset_evaluation") as agent:
        return await agent.generate_str(inputs)


async def run_dataset_evaluation():
    """Run the dataset evaluation."""
    print("Starting MCP Fetch Server dataset evaluation...")

    report = await fetch_dataset.evaluate(
        fetch_task_function,
        max_concurrency=2,  # Test concurrency
    )

    # Print detailed report
    report.print(
        include_input=True,
        include_output=True,
        include_scores=True,
        include_durations=True,
    )

    # Save results
    import json

    with open("dataset_results.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2, default=str)

    print("\nDataset evaluation completed!")
    print(
        f"Results: {report.passed_cases}/{report.total_cases} cases passed ({report.success_rate:.1%})"
    )
    print(f"Average duration: {report.average_duration_ms:.0f}ms")

    return report


if __name__ == "__main__":
    asyncio.run(run_dataset_evaluation())
