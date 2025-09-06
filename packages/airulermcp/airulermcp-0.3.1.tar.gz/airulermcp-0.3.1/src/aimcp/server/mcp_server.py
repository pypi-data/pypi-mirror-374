"""FastMCP server implementation."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from functools import partial
from typing import Any

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from ..cache.manager import CacheManager
from ..config.models import AIMCPConfig
from ..gitlab.client import GitLabClient
from ..tools.manager import ToolManager
from ..tools.models import ConflictResolutionStrategy, MCPResource, ResolvedTool
from ..utils.health import HealthStatus, SystemHealthChecker
from ..utils.logging import get_logger


logger = get_logger("mcp.server")

# Constants
MAX_SIZE_FOR_AUTOLOADED_RESOURCES = 50000  # 50KB for text
HIGH_PRIORITY_THRESHOLD = 0.8  # Priority threshold for auto-loading resources


@dataclass(slots=True)
class MCPServer:
    """MCP server with FastMCP."""

    config: AIMCPConfig
    cache_manager: CacheManager
    gitlab_client: GitLabClient
    tool_manager: ToolManager
    health_checker: SystemHealthChecker

    _server: FastMCP = field(init=False)

    def __post_init__(self) -> None:
        """Initialize FastMCP server."""
        self._server = FastMCP(self.config.server.name)

        # Set tool manager conflict resolution strategy
        try:
            strategy = ConflictResolutionStrategy(self.config.tools.conflict_resolution_strategy)
            self.tool_manager.set_conflict_strategy(strategy)
        except ValueError:
            logger.warning(
                "Invalid conflict resolution strategy, using default",
                strategy=self.config.tools.conflict_resolution_strategy,
                default="prefix",
            )

        # Register built-in tools
        self._register_builtin_tools()

        logger.info("MCP server initialized", name=self.config.server.name)

    async def get_server_runner(self) -> Callable[[], Awaitable[None]]:
        """Get server runner coroutine for the configured transport.

        Returns:
            Async callable that runs the server with configured transport
        """
        # Start cache manager
        await self.cache_manager.start()

        # Attach health check handler
        self._attach_health_checks()

        # Load and register tools
        await self._load_and_register_tools()

        # Return appropriate runner based on transport
        match self.config.server.transport:
            case "stdio":
                logger.info("Server ready for STDIO transport")
                return self._run_stdio
            case "http":
                logger.info(
                    "Server ready for HTTP transport",
                    host=self.config.server.host,
                    port=self.config.server.port,
                )
                return partial(self._run_http, self.config.server.host, self.config.server.port)
            case "sse":
                logger.info(
                    "Server ready for SSE transport",
                    host=self.config.server.host,
                    port=self.config.server.port,
                )
                return partial(self._run_sse, self.config.server.host, self.config.server.port)
            case _:
                exc_message = f"Unsupported transport: {self.config.server.transport}"
                raise ValueError(exc_message)

    async def cleanup(self) -> None:
        """Clean up server resources."""
        logger.info("Cleaning up MCP server resources")

        # Stop cache manager
        await self.cache_manager.stop()

        # Close GitLab client
        await self.gitlab_client.close()

        logger.info("MCP server cleanup completed")

    async def __aenter__(self) -> Callable[[], Awaitable[None]]:
        """Async context manager entry - returns server runner."""
        return await self.get_server_runner()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.cleanup()

    def _attach_health_checks(self) -> None:
        @self._server.custom_route("/healthz", methods=["GET"])
        async def health_check(_: Request) -> Response:
            return Response(status_code=HTTP_200_OK)

        @self._server.custom_route("/ready", methods=["GET"])
        async def ready_check(_: Request) -> JSONResponse:
            system_check = await self.health_checker.check_all()
            status_code = HTTP_200_OK

            if system_check.status != HealthStatus.HEALTHY:
                status_code = HTTP_503_SERVICE_UNAVAILABLE

            return JSONResponse({"status": system_check.status, "service": "mcp-server"}, status_code=status_code)

    async def _load_and_register_tools(self) -> None:
        """Load tool specifications and register MCP tools."""
        try:
            # Load resolved tools from all repositories
            resolved_tools = await self.tool_manager.load_all_tools()

            if not resolved_tools:
                logger.warning("No tools loaded from any repository")
                return

            # Register each tool with FastMCP
            for tool in resolved_tools:
                self._register_mcp_tool(tool)

            logger.info("Tools loaded and registered successfully", count=len(resolved_tools))

        except Exception as e:
            logger.exception("Failed to load and register tools", error=str(e))
            # Continue startup even if tool loading fails

    def _register_mcp_tool(self, tool: ResolvedTool) -> None:
        """Register a single resolved tool with FastMCP.

        Args:
            tool: ResolvedTool instance to register
        """

        # Create tool handler that provides structured resource information
        async def tool_handler() -> dict[str, Any]:
            """Handle tool execution by providing structured resource information."""
            resources = []

            if tool.related_resources is not None:
                # Add structured resource information
                for resource in tool.related_resources:
                    # Generate URI from resource
                    uri = f"aimcp://{tool.repository}/{tool.branch}/{resource.uri}"

                    resource_info: dict[str, Any] = {
                        "name": resource.name,
                        "uri": uri,
                        "description": resource.description,
                        "mimeType": resource.mimeType,
                    }

                    # For small/critical resources, include content directly
                    # For others, provide URI for on-demand loading with load-resource tool
                    try:
                        should_auto_load = self._should_auto_load_resource(resource)
                        if should_auto_load:
                            content = await self.tool_manager.get_resource_content(uri)
                            resource_info["content"] = content
                            resource_info["loaded"] = True
                        else:
                            resource_info["loaded"] = False
                            resource_info["load_hint"] = f"Use load-resource tool with URI: {uri}"

                    except Exception as e:
                        logger.exception(
                            "Failed to fetch resource content",
                            resource=resource.name,
                            error=str(e),
                        )
                        resource_info["error"] = str(e)
                        resource_info["loaded"] = False

                    resources.append(resource_info)

            return {
                "tool": tool.resolved_name,
                "repository": tool.repository,
                "branch": tool.branch,
                "resources": resources,
            }

        # Register with FastMCP using the tool decorator
        self._server.tool(
            tool_handler,
            name=tool.resolved_name,
            description=tool.specification.description,
        )

        logger.debug(
            "Registered MCP tool",
            name=tool.resolved_name,
            repository=tool.repository,
            resources=len(tool.related_resources) if tool.related_resources else 0,
        )

    async def _run_stdio(self) -> None:
        """Run server with STDIO transport."""
        await self._server.run_stdio_async()

    async def _run_http(self, host: str, port: int) -> None:
        """Run server with HTTP transport."""
        await self._server.run_http_async(host=host, port=port)

    async def _run_sse(self, host: str, port: int) -> None:
        """Run server with SSE transport."""
        await self._server.run_sse_async(host=host, port=port)

    @property
    def server(self) -> FastMCP:
        """Get the FastMCP server instance."""
        return self._server

    def _register_builtin_tools(self) -> None:
        """Register built-in tools."""

        @self._server.tool(
            name="load-resource",
            description="Load content from a resource URI (aimcp://repo/branch/file)",
        )
        async def load_resource(uri: str) -> str:
            """Load resource content by URI.

            Args:
                uri: Resource URI in format aimcp://repo/branch/file

            Returns:
                Resource content as string
            """
            try:
                content = await self.tool_manager.get_resource_content(uri)
                logger.debug("Resource loaded successfully", uri=uri, size=len(content))
            except Exception as e:
                error_msg = f"Failed to load resource {uri}: {e}"
                logger.exception("Resource loading failed", uri=uri, error=str(e))
                return error_msg
            else:
                return content

    def _should_auto_load_resource(self, resource: MCPResource) -> bool:
        """Determine if a resource should be auto-loaded with tool execution.

        Args:
            resource: MCPResource instance

        Returns:
            True if resource should be loaded automatically
        """
        # Auto-load based on size (configurable threshold)
        if resource.size and resource.size <= self.config.tools.max_auto_load_size:
            return True

        # Auto-load based on priority annotation
        if (
            resource.annotations is not None
            and resource.annotations.priority is not None
            and resource.annotations.priority >= HIGH_PRIORITY_THRESHOLD
        ):
            return True

        # Auto-load based on MIME type (text files are usually small and important)
        auto_load_types = [
            "text/markdown",
            "text/plain",
            "application/json",
            "text/yaml",
        ]
        return resource.mimeType in auto_load_types and (
            not resource.size or resource.size <= MAX_SIZE_FOR_AUTOLOADED_RESOURCES
        )
