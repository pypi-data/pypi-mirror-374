"""CLI entry point for AIMCP."""

import asyncio
from pathlib import Path

import typer
from pydantic import ValidationError

from . import __version__
from .cache.factory import create_cache_manager
from .config.models import AIMCPConfig
from .gitlab.client import GitLabClient
from .server.factory import create_mcp_server
from .utils.health import CacheHealthChecker, GitLabHealthChecker, SystemHealthChecker
from .utils.logging import setup_logging


def _exit_with_error(code: int = 1) -> None:
    """Helper function to exit with error code."""
    raise typer.Exit(code)


def _exit_with_health_status(status: str) -> None:
    """Helper function to exit with health-based error code."""
    if status == "unhealthy":
        raise typer.Exit(2)  # Critical health issues
    if status == "degraded":
        raise typer.Exit(1)  # Warning health issues


app = typer.Typer(
    name="aimcp",
    help="MCP server for distributing tool specifications from GitLab repositories",
    add_completion=False,
)

# Module-level defaults for typer options
CONFIG_OPTION = typer.Option(
    None,
    "--config",
    "-c",
    help="Path to configuration file",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
)

CONFIG_ARGUMENT = typer.Argument(
    ...,
    help="Path to configuration file",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
)


@app.command()
def serve(
    config: Path | None = CONFIG_OPTION,
    host: str | None = typer.Option(
        None,
        "--host",
        "-h",
        help="Server host (overrides config)",
    ),
    port: int | None = typer.Option(
        None,
        "--port",
        "-p",
        help="Server port (overrides config)",
    ),
    transport: str | None = typer.Option(
        None,
        "--transport",
        "-t",
        help="Transport type: stdio, http, sse (overrides config)",
    ),
) -> None:
    """Start the AIMCP MCP server."""
    try:
        # Build override settings
        overrides: dict[str, str | int] = {}
        if host:
            overrides["host"] = host
        if port:
            overrides["port"] = port
        if transport:
            overrides["transport"] = transport

        # Load configuration
        config_obj = AIMCPConfig.create(config, overrides)

        # Setup logging
        setup_logging(config_obj.logging)

        # Start server
        typer.echo(f"Starting AIMCP server: {config_obj.server.name}")
        typer.echo(f"Transport: {config_obj.server.transport.value}")
        if config_obj.server.transport.value != "stdio":
            typer.echo(f"Address: {config_obj.server.host}:{config_obj.server.port}")
        typer.echo(f"Monitoring {len(config_obj.gitlab.repositories)} repositories")
        typer.echo(f"Cache backend: {config_obj.cache.backend.value}")

        async def run_server() -> None:
            server = await create_mcp_server(config_obj)

            try:
                server_runner = await server.get_server_runner()
                typer.echo("✓ AIMCP server started successfully")
                typer.echo("Press Ctrl+C to stop the server")
                await server_runner()
            except KeyboardInterrupt:
                typer.echo("\nShutting down server...")
            except Exception as e:
                typer.echo(f"✗ Server failed to start: {e}", err=True)
                raise typer.Exit(1) from e
            finally:
                await server.cleanup()

        asyncio.run(run_server())

    except ValidationError as e:
        typer.echo(f"Configuration error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error starting server: {e}", err=True)
        raise typer.Exit(1) from e


@app.command("validate-config")
def validate_config_command(
    config: Path = CONFIG_ARGUMENT,
) -> None:
    """Validate configuration file."""
    try:
        config_obj = AIMCPConfig.create(config)

        typer.echo("✓ Configuration is valid")
        typer.echo(f"  Server: {config_obj.server.host}:{config_obj.server.port} ({config_obj.server.transport})")
        typer.echo(f"  GitLab: {config_obj.gitlab.instance_url}")
        typer.echo(f"  Repositories: {len(config_obj.gitlab.repositories)}")
        typer.echo(f"  Cache: {config_obj.cache.backend} (TTL: {config_obj.cache.ttl_seconds}s)")

    except ValidationError as e:
        typer.echo("✗ Configuration validation failed:", err=True)
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            typer.echo(f"  {location}: {error['msg']}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error loading configuration: {e}", err=True)
        raise typer.Exit(1) from e


@app.command("test-gitlab")
def test_gitlab_command(
    config: Path = CONFIG_ARGUMENT,  # noqa: PT028
) -> None:
    """Test GitLab connectivity and repository access."""
    try:
        config_obj = AIMCPConfig.create(config)

        typer.echo("Testing GitLab connectivity...")
        typer.echo(f"Instance: {config_obj.gitlab.instance_url}")

        async def test_connection() -> None:
            async with GitLabClient(config_obj.gitlab) as client:
                # Test basic connection
                result = await client.test_connection()
                if result["status"] == "success":
                    typer.echo(f"✓ Connected as user: {result['user']}")
                    typer.echo(f"  GitLab version: {result['gitlab_version']}")
                else:
                    typer.echo(f"✗ Connection failed: {result['error']}")
                    _exit_with_error()

                # Test repository access
                typer.echo("\nTesting repository access:")
                for repo in config_obj.gitlab.repositories:
                    try:
                        project = await client.get_project(repo.url)
                        typer.echo(f"✓ {repo.url} - {project.name}")

                        # Test tools.json detection
                        has_tools = await client.check_tools_json_exists(repo)
                        if has_tools:
                            try:
                                tools_content = await client.fetch_tools_json(repo)
                                typer.echo(f"  ✓ Found tools.json ({len(tools_content)} bytes)")
                            except Exception as e:
                                typer.echo(f"  ⚠ tools.json exists but failed to fetch: {e}")
                        else:
                            typer.echo("  ⚠ No tools.json found")

                    except Exception as e:
                        typer.echo(f"✗ {repo.url} - Error: {e}")
                        continue

        asyncio.run(test_connection())

    except ValidationError as e:
        typer.echo(f"Configuration error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error testing GitLab: {e}", err=True)
        raise typer.Exit(1) from e


@app.command("cache")
def cache_command() -> None:
    """Cache management commands."""
    typer.echo("Use 'cache clear' or 'cache stats' subcommands")


@app.command("cache-clear")
def cache_clear_command(
    config: Path = CONFIG_ARGUMENT,
) -> None:
    """Clear the cache."""
    try:
        config_obj = AIMCPConfig.create(config)

        typer.echo("Clearing cache...")

        async def clear_cache() -> None:
            cache_manager = create_cache_manager(config_obj.cache)

            async with cache_manager:
                await cache_manager.clear_all()
                typer.echo("✓ Cache cleared successfully")

        asyncio.run(clear_cache())

    except ValidationError as e:
        typer.echo(f"Configuration error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error clearing cache: {e}", err=True)
        raise typer.Exit(1) from e


@app.command("health-check")
def health_check_command(
    config: Path = CONFIG_ARGUMENT,
) -> None:
    """Check system health status."""
    try:
        config_obj = AIMCPConfig.create(config)

        typer.echo("Checking system health...")

        async def check_health() -> None:
            # Create components
            cache_manager = create_cache_manager(config_obj.cache)
            gitlab_client = GitLabClient(config_obj.gitlab)

            # Create health checkers
            gitlab_checker = GitLabHealthChecker(gitlab_client, config_obj.gitlab.repositories)
            cache_checker = CacheHealthChecker(cache_manager)

            system_checker = SystemHealthChecker([gitlab_checker, cache_checker])

            # Run health checks
            async with cache_manager:
                system_health = await system_checker.check_all()

                # Display results
                status_colors = {
                    "healthy": typer.colors.GREEN,
                    "degraded": typer.colors.YELLOW,
                    "unhealthy": typer.colors.RED,
                }

                color = status_colors.get(system_health.status, typer.colors.WHITE)
                typer.echo("\nSystem Health: ", nl=False)
                typer.secho(system_health.status.upper(), fg=color, bold=True)
                typer.echo(f"Checked at: {system_health.checked_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")

                for check in system_health.checks:
                    status_symbol = {
                        "healthy": "✓",
                        "degraded": "⚠",
                        "unhealthy": "✗",
                    }.get(check.status, "?")

                    check_color = status_colors.get(check.status, typer.colors.WHITE)

                    typer.echo(f"\n{status_symbol} ", nl=False)
                    typer.secho(f"{check.component.upper()}: {check.status}", fg=check_color)
                    typer.echo(f"  Message: {check.message}")

                    if check.details:
                        typer.echo("  Details:")
                        for key, value in check.details.items():
                            typer.echo(f"    {key}: {value}")

                # Set exit code based on overall health
                _exit_with_health_status(system_health.status)
                # Healthy = exit code 0

        asyncio.run(check_health())

    except ValidationError as e:
        typer.echo(f"Configuration error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error checking health: {e}", err=True)
        raise typer.Exit(1) from e


@app.command()
def version() -> None:
    """Show version information."""

    typer.echo(f"AIMCP version {__version__}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
