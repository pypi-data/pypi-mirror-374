"""Validate command for checking MCP-Eval configuration."""

import asyncio
from pathlib import Path
from typing import Dict, List, Any
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from mcp_agent.app import MCPApp
from mcp_agent.config import LoggerSettings, MCPServerSettings
from mcp_agent.mcp.gen_client import gen_client
from mcp_agent.workflows.factory import (
    _llm_factory,
    agent_from_spec as _agent_from_spec_factory,
)
from mcp_agent.agents.agent_spec import AgentSpec

from mcp_eval.config import load_config, find_eval_config
from mcp_eval.cli.utils import (
    load_all_servers,
    load_all_agents,
    load_yaml,
)
from mcp_eval.cli.models import MCPServerConfig, AgentConfig

app = typer.Typer(help="Validate MCP-Eval configuration")
console = Console()


class ValidationResult:
    """Result of a validation check."""

    def __init__(
        self,
        name: str,
        success: bool,
        message: str,
        details: Dict[str, Any] | None = None,
        is_warning: bool = False,
    ):
        self.name = name
        self.success = success
        self.message = message
        self.details = details or {}
        self.is_warning = is_warning


async def validate_server(
    server: MCPServerConfig, project: Path, config_path: Path | None
) -> ValidationResult:
    """Validate a single server by connecting and listing tools."""
    try:
        # Load the full configuration from mcp-eval (includes all servers and secrets)
        settings = load_config(config_path)

        # Set logger settings to just errors to avoid noise
        settings.logger = LoggerSettings(
            type="console",
            level="error",
        )

        # Create MCP app with the settings
        mcp_app = MCPApp(settings=settings)
        async with mcp_app.run() as running:
            # Try to connect to the server
            async with gen_client(
                server.name, server_registry=running.context.server_registry
            ) as client:
                # List tools to verify connection
                result = await client.list_tools()

                tools = []
                if hasattr(result, "tools") and isinstance(result.tools, list):
                    tools = [getattr(t, "name", "unknown") for t in result.tools]

                return ValidationResult(
                    name=server.name,
                    success=True,
                    message=f"Connected successfully, found {len(tools)} tools",
                    details={"tools": tools[:10]},  # Show first 10 tools
                )
    except Exception as e:
        return ValidationResult(
            name=server.name,
            success=False,
            message=f"Failed to connect: {str(e)[:100]}",
            details={"error": str(e)},
        )


async def validate_agent(
    agent: AgentConfig, project: Path, config_path: Path | None
) -> ValidationResult:
    """Validate an agent configuration."""
    issues = []

    # Check if referenced servers exist
    all_servers = load_all_servers(project)
    missing_servers = [s for s in agent.server_names if s not in all_servers]
    if missing_servers:
        issues.append(f"Missing servers: {', '.join(missing_servers)}")

    # Load configuration using mcp-eval's config loading (handles all providers automatically)
    settings = load_config(config_path)

    # Check if provider/model or defaults are configured
    # We'll validate this by actually trying to create an LLM factory later
    # rather than trying to guess what credentials are needed for each provider

    # Try to create the agent to verify configuration
    if not issues:
        try:
            # Filter servers to only those referenced by the agent
            if settings.mcp and settings.mcp.servers:
                agent_servers = {}
                for server_name in agent.server_names:
                    if server_name in settings.mcp.servers:
                        agent_servers[server_name] = settings.mcp.servers[server_name]
                    elif server_name in all_servers:
                        # Fallback: create from all_servers if not in settings
                        server = all_servers[server_name]
                        agent_servers[server_name] = MCPServerSettings(
                            name=server.name,
                            transport=server.transport,
                            command=server.command,
                            args=server.args,
                            url=server.url,
                            headers=server.headers,
                            env=server.env,
                        )
                settings.mcp.servers = agent_servers

            # Create MCP app with the settings
            mcp_app = MCPApp(settings=settings)
            async with mcp_app.run() as running:
                # Create AgentSpec
                spec = AgentSpec(
                    name=agent.name,
                    instruction=agent.instruction,
                    server_names=agent.server_names,
                )

                # Try to create agent (agent_from_spec is not async)
                test_agent = _agent_from_spec_factory(spec, context=running.context)
                await test_agent.initialize()

                # Try to attach and test LLM if provider is configured
                provider = agent.provider or settings.provider
                model = agent.model or settings.model

                if provider:
                    try:
                        llm_factory = _llm_factory(
                            provider=provider, model=model, context=running.context
                        )
                        llm = llm_factory(test_agent)

                        # Try a simple generation to verify it works
                        response = await llm.generate_str(
                            "Say 'validation successful' and nothing else."
                        )
                        if not response or not response.strip():
                            issues.append(
                                f"LLM returned empty response - check API key for {provider}"
                            )
                        elif "validation" in response.lower():
                            return ValidationResult(
                                name=agent.name,
                                success=True,
                                message="Agent configured correctly and LLM responds",
                                details={
                                    "servers": agent.server_names,
                                    "provider": provider,
                                },
                            )
                        else:
                            issues.append(
                                f"LLM responded unexpectedly: {response[:50]}"
                            )
                    except Exception as e:
                        # Extract meaningful error message
                        error_msg = str(e)
                        if "api" in error_msg.lower() and "key" in error_msg.lower():
                            issues.append(f"Missing or invalid API key for {provider}")
                        elif "credential" in error_msg.lower():
                            issues.append(f"Missing credentials for {provider}")
                        else:
                            issues.append(f"LLM test failed: {error_msg[:100]}")
                else:
                    # No provider configured - this is only an issue if the test expects to use an LLM
                    return ValidationResult(
                        name=agent.name,
                        success=True,
                        message="Agent configuration valid (no provider configured)",
                        details={
                            "servers": agent.server_names,
                            "note": "No LLM provider configured",
                        },
                    )

        except Exception as e:
            issues.append(f"Failed to create agent: {str(e)[:50]}")

    if issues:
        return ValidationResult(
            name=agent.name,
            success=False,
            message="; ".join(issues),
            details={"issues": issues},
        )

    return ValidationResult(
        name=agent.name,
        success=True,
        message="Agent configuration valid",
        details={"servers": agent.server_names},
    )


def check_api_keys(project: Path) -> ValidationResult:
    """Check if API keys are configured."""
    secrets_path = project / "mcpeval.secrets.yaml"
    if not secrets_path.exists():
        return ValidationResult(
            name="API Keys",
            success=False,
            message="No secrets file found (mcpeval.secrets.yaml)",
        )

    secrets = load_yaml(secrets_path)
    providers = []

    if secrets.get("anthropic", {}).get("api_key"):
        providers.append("anthropic")
    if secrets.get("openai", {}).get("api_key"):
        providers.append("openai")

    if not providers:
        return ValidationResult(
            name="API Keys",
            success=False,
            message="No API keys configured",
        )

    return ValidationResult(
        name="API Keys",
        success=True,
        message=f"Configured for: {', '.join(providers)}",
        details={"providers": providers},
    )


def check_judge_config(config_path: Path | None) -> ValidationResult:
    """Check judge configuration."""
    if config_path is None:
        return ValidationResult(
            name="Judge",
            success=False,
            message="No configuration file found",
        )

    # Load typed settings to allow fallback behavior
    settings = load_config(config_path)
    cfg = load_yaml(config_path)
    judge = cfg.get("judge", {})

    model = (judge or {}).get("model")
    min_score = (judge or {}).get("min_score", 0.8)
    provider = (judge or {}).get("provider") or getattr(settings, "provider", None)
    global_model = getattr(settings, "model", None)

    if model:
        return ValidationResult(
            name="Judge",
            success=True,
            message=f"Model: {model}, Min score: {min_score}",
            details={"model": model, "min_score": min_score},
        )

    # No explicit judge model; allow auto-selection
    # We will use global model if present; otherwise the ModelSelector will pick one.
    auto_msg_parts = []
    if global_model:
        auto_msg_parts.append(f"using global model {global_model}")
    else:
        auto_msg_parts.append("model auto-selected")
    if provider:
        auto_msg_parts.append(f"provider {provider}")

    return ValidationResult(
        name="Judge",
        success=True,
        message="No judge model specified - " + ", ".join(auto_msg_parts),
        details={
            "provider": provider,
            "model": model or global_model or "auto",
            "min_score": min_score,
        },
        is_warning=True,
    )


async def run_all_validations(
    project: Path,
    config_path: Path | None,
    servers: bool,
    agents: bool,
    quick: bool,
    all_servers: Dict[str, MCPServerConfig],
    all_agents: List[AgentConfig],
) -> List[ValidationResult]:
    """Run all validations in a single async context."""
    results = []

    # Validate servers
    if servers and all_servers and not quick:
        console.print("\n[bold cyan]Validating servers...[/bold cyan]")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            for name, server in all_servers.items():
                task = progress.add_task(f"Testing {name}...", total=None)
                result = await validate_server(server, project, config_path)
                results.append(result)
                progress.update(task, description=f"Tested {name}")
                _print_result(result)

    # Validate agents
    if agents and all_agents and not quick:
        console.print("\n[bold cyan]Validating agents...[/bold cyan]")
        for agent in all_agents:
            result = await validate_agent(agent, project, config_path)
            results.append(result)
            _print_result(result)

    return results


@app.command()
def validate(
    project_dir: str = typer.Option(".", help="Project directory"),
    servers: bool = typer.Option(True, help="Validate server connections"),
    agents: bool = typer.Option(True, help="Validate agent configurations"),
    quick: bool = typer.Option(False, help="Quick validation (skip connection tests)"),
):
    """Validate MCP-Eval configuration.

    Checks:

    - API keys are configured

    - Judge configuration is valid

    - Servers can be connected to and tools listed

    - Agents reference valid servers

    - Agents can be created with configured LLMs



    Examples:

    Full validation: $ mcp-eval validate

    Quick validation (no connections): $ mcp-eval validate --quick

    Servers only: $ mcp-eval validate --no-agents
    """
    project = Path(project_dir)

    # Find config file once
    config_path = find_eval_config(project)
    if config_path:
        console.print(f"[dim]Using config: {config_path}[/dim]")
    else:
        console.print(
            "[red]Error: No mcpeval config found. Run 'mcp-eval init' first.[/red]"
        )
        console.print(
            "[dim]Searched for: mcpeval.yaml, mcpeval.config.yaml, .mcp-eval/config.yaml, etc.[/dim]"
        )
        raise typer.Exit(1)

    results: List[ValidationResult] = []

    # Check basic configuration
    console.print("\n[bold cyan]Checking configuration...[/bold cyan]")

    # API Keys
    api_result = check_api_keys(project)
    results.append(api_result)
    _print_result(api_result)

    # Judge config
    judge_result = check_judge_config(config_path)
    results.append(judge_result)
    _print_result(judge_result)

    # Load servers and agents
    all_servers = load_all_servers(project) if servers else {}
    all_agents = load_all_agents(project) if agents else []

    # Quick validation - just check configuration
    if quick:
        # Validate servers
        if servers:
            if all_servers:
                console.print("\n[bold cyan]Validating servers...[/bold cyan]")
                for name, server in all_servers.items():
                    if server.transport == "stdio" and not server.command:
                        result = ValidationResult(
                            name=name,
                            success=False,
                            message="stdio transport requires command",
                        )
                    elif server.transport != "stdio" and not server.url:
                        result = ValidationResult(
                            name=name,
                            success=False,
                            message=f"{server.transport} transport requires url",
                        )
                    else:
                        result = ValidationResult(
                            name=name,
                            success=True,
                            message="Configuration valid (not tested)",
                        )
                    results.append(result)
                    _print_result(result)
            else:
                console.print("[yellow]No servers configured[/yellow]")

        # Validate agents
        if agents:
            if all_agents:
                console.print("\n[bold cyan]Validating agents...[/bold cyan]")
                for agent in all_agents:
                    missing = [s for s in agent.server_names if s not in all_servers]
                    if missing:
                        result = ValidationResult(
                            name=agent.name,
                            success=False,
                            message=f"References missing servers: {', '.join(missing)}",
                        )
                    else:
                        result = ValidationResult(
                            name=agent.name,
                            success=True,
                            message="Configuration valid (not tested)",
                        )
                    results.append(result)
                    _print_result(result)
            else:
                console.print("[yellow]No agents configured[/yellow]")
    else:
        # Full validation with connection tests
        # Run all async validations in a single event loop
        if (servers and all_servers) or (agents and all_agents):
            async_results = asyncio.run(
                run_all_validations(
                    project=project,
                    config_path=config_path,
                    servers=servers,
                    agents=agents,
                    quick=quick,
                    all_servers=all_servers,
                    all_agents=all_agents,
                )
            )
            results.extend(async_results)
        else:
            if servers and not all_servers:
                console.print("[yellow]No servers configured[/yellow]")
            if agents and not all_agents:
                console.print("[yellow]No agents configured[/yellow]")

    # Summary
    console.print("\n[bold]Validation Summary[/bold]")
    success_count = sum(1 for r in results if r.success and not r.is_warning)
    warning_count = sum(1 for r in results if r.success and r.is_warning)
    fail_count = len(results) - success_count - warning_count

    if fail_count == 0:
        if warning_count:
            console.print(
                f"[yellow]⚠️  {success_count} passed, {warning_count} warning(s)[/yellow]"
            )
        else:
            console.print(f"[green]✅ All {len(results)} checks passed![/green]")
    else:
        console.print(
            f"[yellow]⚠️  {success_count} passed, {warning_count} warning(s), {fail_count} failed[/yellow]"
        )

        # Show failed items
        failed = [r for r in results if not r.success]
        if failed:
            console.print("\n[red]Failed checks:[/red]")
            for r in failed:
                console.print(f"  - {r.name}: {r.message}")

        # Show warnings
        warnings = [r for r in results if r.success and r.is_warning]
        if warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for r in warnings:
                console.print(f"  - {r.name}: {r.message}")

        raise typer.Exit(1)


def _print_result(result: ValidationResult):
    """Print a validation result."""
    if result.success:
        icon = "[yellow]![/yellow]" if result.is_warning else "[green]✓[/green]"
    else:
        icon = "[red]✗[/red]"

    console.print(f"{icon} {result.name}: {result.message}")

    # Show details for failures
    if not result.success and result.details.get("error"):
        console.print(f"  [dim]{result.details['error'][:200]}[/dim]")


if __name__ == "__main__":
    app()
