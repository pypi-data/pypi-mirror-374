"""Async GitLab API client."""

import asyncio
import base64
from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx
from httpx import AsyncClient, Response

from ..config.models import GitLabConfig, GitLabRepository
from ..utils.logging import get_logger
from .models import GitLabError, GitLabFileContent, GitLabProject


logger = get_logger("gitlab")


class GitLabClientError(Exception):
    """GitLab client error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class GitLabClient:
    """Async GitLab API client."""

    def __init__(self, config: GitLabConfig) -> None:
        """Initialize GitLab client.

        Args:
            config: GitLab configuration
        """
        self.config = config
        self.base_url = str(config.instance_url).rstrip("/")
        self.api_url = f"{self.base_url}/api/v4"

        # HTTP client configuration
        self.client = AsyncClient(
            timeout=config.timeout,
            headers={
                "Private-Token": config.token,
                "User-Agent": "AIMCP/0.1.0",
            },
        )

    async def __aenter__(self) -> "GitLabClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Response:
        """Make HTTP request to GitLab API.

        Args:
            method: HTTP method
            endpoint: API endpoint (without /api/v4 prefix)
            **kwargs: Additional request parameters

        Returns:
            HTTP response

        Raises:
            GitLabClientError: If request fails
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug("Making GitLab API request", method=method, url=url, attempt=attempt)

                response = await self.client.request(method, url, **kwargs)

                # Rate limit check
                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS and attempt < self.config.max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        "Rate limited, retrying",
                        wait_time=wait_time,
                        attempt=attempt,
                    )
                    await asyncio.sleep(wait_time)
                    continue

                if response.status_code >= HTTPStatus.BAD_REQUEST:
                    try:
                        error_data = response.json()
                        error = GitLabError(**error_data)
                        message = error.message
                    except Exception:
                        message = f"HTTP {response.status_code}: {response.text}"

                    raise GitLabClientError(message, response.status_code)

                logger.debug("GitLab API request successful", status_code=response.status_code)

            except httpx.RequestError as e:
                if attempt < self.config.max_retries:
                    wait_time = 2**attempt
                    logger.warning(
                        "Request failed, retrying",
                        error=str(e),
                        wait_time=wait_time,
                        attempt=attempt,
                    )
                    await asyncio.sleep(wait_time)
                    continue
                exc_message = f"Request failed: {e}"
                raise GitLabClientError(exc_message) from e
            else:
                return response

        exc_message = "Max retries exceeded"
        raise GitLabClientError(exc_message)

    async def get_project(self, project_path: str) -> GitLabProject:
        """Get project information.

        Args:
            project_path: Project path (e.g., "group/project")

        Returns:
            Project information
        """
        encoded_path = quote(project_path, safe="")
        response = await self._make_request("GET", f"/projects/{encoded_path}")
        return GitLabProject(**response.json())

    async def get_file(
        self,
        project_path: str,
        file_path: str,
        ref: str = "main",
    ) -> GitLabFileContent:
        """Get file content.

        Args:
            project_path: Project path
            file_path: File path within repository
            ref: Git reference

        Returns:
            File content
        """
        encoded_path = quote(project_path, safe="")
        encoded_file_path = quote(file_path, safe="")
        params = {"ref": ref}

        response = await self._make_request(
            "GET",
            f"/projects/{encoded_path}/repository/files/{encoded_file_path}",
            params=params,
        )
        return GitLabFileContent(**response.json())

    async def get_file_content_decoded(
        self,
        project_path: str,
        file_path: str,
        ref: str = "main",
    ) -> str:
        """Get file content decoded as string.

        Args:
            project_path: Project path
            file_path: File path within repository
            ref: Git reference

        Returns:
            Decoded file content
        """
        file_info = await self.get_file(project_path, file_path, ref)

        if file_info.encoding == "base64":
            content_bytes = base64.b64decode(file_info.content)
            return content_bytes.decode("utf-8")
        # Assume text content
        return file_info.content

    async def check_tools_json_exists(self, repository: GitLabRepository) -> bool:
        """Check if tools.json exists in a repository.

        Args:
            repository: Repository configuration

        Returns:
            True if tools.json exists, False otherwise
        """
        try:
            await self.get_file(
                repository.url,
                "tools.json",
                repository.branch,
            )
        except GitLabClientError as e:
            if e.status_code == HTTPStatus.NOT_FOUND:
                return False
            # Re-raise other errors
            raise
        else:
            return True

    async def fetch_tools_json(self, repository: GitLabRepository) -> str:
        """Fetch tools.json content from a repository.

        Args:
            repository: Repository configuration

        Returns:
            tools.json content as string

        Raises:
            GitLabClientError: If file doesn't exist or fetch fails
        """
        logger.info("Fetching tools.json", repository=repository.url, branch=repository.branch)

        try:
            content = await self.get_file_content_decoded(
                repository.url,
                "tools.json",
                repository.branch,
            )

            logger.debug("Fetched tools.json", repository=repository.url, size=len(content))

        except GitLabClientError as e:
            logger.exception("Failed to fetch tools.json", repository=repository.url, error=str(e))
            raise
        else:
            return content

    async def test_connection(self) -> dict[str, str]:
        """Test GitLab API connection.

        Returns:
            Connection test results
        """
        try:
            # Test API connectivity with user info
            response = await self._make_request("GET", "/user")
            user_data = response.json()

            return {
                "status": "success",
                "user": user_data.get("username", "unknown"),
                "gitlab_version": response.headers.get("x-gitlab-version", "unknown"),
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
            }
