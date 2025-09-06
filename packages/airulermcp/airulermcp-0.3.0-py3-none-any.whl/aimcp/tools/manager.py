"""Tool specification manager."""

import json
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import cast

from ..cache.manager import CacheManager
from ..config.models import AIMCPConfig, GitLabRepository
from ..gitlab.client import GitLabClient, GitLabClientError
from ..utils.logging import get_logger
from .models import ConflictResolutionStrategy, ResolvedTool, ToolsSpecification
from .resolver import ToolResolver


logger = get_logger("tools.manager")


class ToolSpecificationError(Exception):
    """Error in tool specification processing."""


@dataclass(slots=True)
class ToolManager:
    """Manages tool specifications from repositories."""

    config: AIMCPConfig
    cache_manager: CacheManager
    gitlab_client: GitLabClient
    resolver: ToolResolver = field(init=False)

    def __post_init__(self) -> None:
        """Initialize resolver after dataclass initialization."""
        self.resolver = ToolResolver(ConflictResolutionStrategy.PREFIX)  # Default strategy

    async def load_all_tools(self) -> list[ResolvedTool]:
        """Load and resolve tools from all configured repositories.

        Returns:
            List of resolved tools ready for MCP registration
        """
        logger.info(
            "Loading tools from all repositories",
            count=len(self.config.gitlab.repositories),
        )

        # Load tool specifications from all repositories
        repo_tools: dict[GitLabRepository, ToolsSpecification] = {}

        for repo in self.config.gitlab.repositories:
            try:
                spec = await self._load_repository_tools(repo)
                if spec:
                    repo_tools[repo] = spec
                    logger.debug(
                        "Loaded tools from repository",
                        repository=repo.url,
                        tool_count=len(spec.tools),
                    )
                else:
                    logger.warning("Repository has no tools.json, skipping", repository=repo.url)

            except Exception as e:
                logger.exception(
                    "Failed to load tools from repository",
                    repository=repo.url,
                    error=str(e),
                )
                # Continue with other repositories
                continue

        if not repo_tools:
            logger.warning("No tool specifications loaded from any repository")
            return []

        # Resolve conflicts
        try:
            resolved_tools, conflicts = self.resolver.resolve_tools(repo_tools)

            if conflicts:
                logger.info(
                    "Tool conflicts resolved",
                    conflict_count=len(conflicts),
                    strategy=self.resolver.strategy.value,
                )

            logger.info(
                "Tool loading completed",
                total_tools=len(resolved_tools),
                repositories=len(repo_tools),
            )
        except Exception as e:
            logger.exception("Failed to resolve tool conflicts", error=str(e))
            exc_message = f"Tool conflict resolution failed: {e}"
            raise ToolSpecificationError(exc_message) from e
        else:
            return resolved_tools

    async def _load_repository_tools(self, repository: GitLabRepository) -> ToolsSpecification | None:
        """Load tool specification from a single repository.

        Args:
            repository: Repository configuration

        Returns:
            Tool specification or None if tools.json not found
        """
        cache_key = f"tools:{repository.url}:{repository.branch}"

        # Try cache first
        try:
            cached_spec = await self.cache_manager.get(cache_key)
            if cached_spec:
                logger.debug("Using cached tool specification", repository=repository.url)
                return ToolsSpecification(**cached_spec)
        except Exception as e:
            logger.debug(
                "Cache miss for tool specification",
                repository=repository.url,
                error=str(e),
            )

        # Fetch from GitLab
        try:
            content = await self.gitlab_client.get_file_content_decoded(
                repository.url,
                "tools.json",
                repository.branch,
            )

            # Parse JSON
            try:
                spec_data = json.loads(content)
                spec = ToolsSpecification(**spec_data)

                # Cache for future use
                await self.cache_manager.set(
                    cache_key,
                    spec.model_dump(),
                    ttl=self.config.cache.ttl_seconds,
                )

                logger.debug(
                    "Loaded and cached tool specification",
                    repository=repository.url,
                    tool_count=len(spec.tools),
                )
            except (json.JSONDecodeError, ValueError) as e:
                logger.exception("Invalid tools.json format", repository=repository.url, error=str(e))
                exc_message = f"Invalid tools.json in {repository.url}: {e}"
                raise ToolSpecificationError(exc_message) from e
            else:
                return spec

        except GitLabClientError as e:
            if e.status_code == HTTPStatus.NOT_FOUND:
                # tools.json not found - this is expected for some repositories
                logger.debug("tools.json not found in repository", repository=repository.url)
                return None
            # Other GitLab errors
            logger.exception(
                "Failed to fetch tools.json",
                repository=repository.url,
                error=str(e),
            )

            exc_message = f"Failed to fetch tools.json from {repository.url}: {e}"
            raise ToolSpecificationError(exc_message) from e

    async def get_resource_content(self, resource_uri: str) -> str:
        """Fetch content for a resource URI.

        Args:
            resource_uri: Resource URI in format aimcp://repo/branch/file

        Returns:
            File content

        Raises:
            ToolSpecificationError: If URI is invalid or file not accessible
        """
        # Parse URI
        if not resource_uri.startswith("aimcp://"):
            exc_message = f"Invalid resource URI scheme: {resource_uri}"
            raise ToolSpecificationError(exc_message)

        try:
            # Extract components: aimcp://repo/branch/file/path
            uri_parts = resource_uri[8:]  # Remove 'aimcp://'

            repository, branch, file_path = self._find_repo_data(uri_parts=uri_parts)

            # Find the repository config (we already validated it exists above)
            repo_config = None
            for repo in self.config.gitlab.repositories:
                if repo.url == repository and repo.branch == branch:
                    repo_config = repo
                    break

            if not repo_config:
                exc_message = f"Repository {repository}:{branch} not in configuration"
                raise ToolSpecificationError(exc_message)

            # Check if file is in allowed resources
            await self._validate_resource_access(repo_config, file_path)

            # Fetch content
            cache_key = f"resource:{repository}:{branch}:{file_path}"

            # Try cache first
            try:
                cached_content = cast("str", await self.cache_manager.get(cache_key))
            except Exception:
                logger.warning("Cache miss, continue to fetch")
            else:
                if cached_content:
                    logger.debug("Using cached resource content", uri=resource_uri)
                    return cached_content

            # Fetch from GitLab
            content = await self.gitlab_client.get_file_content_decoded(repository, file_path, branch)

            # Cache content
            await self.cache_manager.set(
                cache_key,
                content,
                ttl=self.config.cache.ttl_seconds,
            )

            logger.debug(
                "Fetched and cached resource content",
                uri=resource_uri,
                size=len(content),
            )
        except (ValueError, IndexError) as e:
            exc_message = f"Invalid resource URI format: {resource_uri}"
            raise ToolSpecificationError() from e
        except GitLabClientError as e:
            exc_message = f"Failed to fetch resource {resource_uri}: {e}"
            raise ToolSpecificationError(exc_message) from e
        else:
            return content

    def _find_repo_data(self, uri_parts: str) -> tuple[str, str, str]:
        # Find the branch part by looking for configured repos
        # Since repository URLs can contain slashes, we need to match against config

        for repo in self.config.gitlab.repositories:
            # Check if URI starts with this repository URL and branch
            expected_prefix = f"{repo.url}/{repo.branch}/"
            if uri_parts.startswith(expected_prefix):
                return (repo.url, repo.branch, uri_parts[len(expected_prefix) :])

        exc_message = "Could not parse repository, branch, and file path from URI"
        raise ValueError(exc_message)

    async def _validate_resource_access(self, repository: GitLabRepository, file_path: str) -> None:
        """Validate that a file is allowed to be accessed.

        Args:
            repository: Repository configuration
            file_path: File path to validate

        Raises:
            ToolSpecificationError: If file access is not allowed
        """
        # Load tool specification to check allowed resources
        spec = await self._load_repository_tools(repository)
        if not spec:
            exc_message = f"No tool specification found for repository {repository.url}"
            raise ToolSpecificationError(exc_message)

        # Check if file is in the resources list
        for resource in spec.resources:
            # Check if the URI matches or if it's a relative path that matches
            if resource.uri == file_path or resource.uri.endswith(f"/{file_path}"):
                logger.debug(
                    "Resource access validated",
                    repository=repository.url,
                    file_path=file_path,
                    resource_name=resource.name,
                )
                return

        # File not found in resources
        exc_message = f"File {file_path} not accessible - not listed in repository resources"
        raise ToolSpecificationError(exc_message)

    def set_conflict_strategy(self, strategy: ConflictResolutionStrategy) -> None:
        """Update conflict resolution strategy.

        Args:
            strategy: New strategy to use
        """
        self.resolver = ToolResolver(strategy)
        logger.info("Conflict resolution strategy updated", strategy=strategy.value)
