"""Resource URI scheme handler for AIMCP."""

from urllib.parse import urlparse

from ..utils.errors import ResourceURIError
from ..utils.logging import get_logger


logger = get_logger("tools.resources")


class ResourceURIHandler:
    """Handles aimcp:// resource URI scheme."""

    SCHEME = "aimcp"
    MIN_PATH_PARTS = 2  # branch and file path

    @classmethod
    def parse_uri(cls, uri: str) -> tuple[str, str, str]:
        """Parse an aimcp:// resource URI.

        Args:
            uri: Resource URI in format aimcp://repository/branch/file/path

        Returns:
            Tuple of (repository, branch, file_path)

        Raises:
            ResourceURIError: If URI format is invalid
        """
        if not uri.startswith(f"{cls.SCHEME}://"):
            exc_message = f"Invalid URI scheme: {uri}"
            raise ResourceURIError(exc_message)

        try:
            parsed = urlparse(uri)

            if parsed.scheme != cls.SCHEME:
                exc_message = f"Expected scheme '{cls.SCHEME}', got '{parsed.scheme}'"
                raise ResourceURIError(exc_message)

            # Extract repository from netloc (host part)
            repository = parsed.netloc
            if not repository:
                exc_message = "Missing repository in URI"
                raise ResourceURIError(exc_message)

            # Extract branch and file path from path
            path_parts = parsed.path.lstrip("/").split("/", 1)
            if len(path_parts) < cls.MIN_PATH_PARTS:
                exc_message = "URI must include branch and file path"
                raise ResourceURIError(exc_message)

            branch, file_path = path_parts

            if not branch:
                exc_message = "Missing branch in URI"
                raise ResourceURIError(exc_message)
            if not file_path:
                exc_message = "Missing file path in URI"
                raise ResourceURIError(exc_message)
        except ValueError as e:
            exc_test = f"Invalid URI format: {uri}"
            raise ResourceURIError(exc_test) from e
        else:
            return repository, branch, file_path

    @classmethod
    def build_uri(cls, repository: str, branch: str, file_path: str) -> str:
        """Build an aimcp:// resource URI.

        Args:
            repository: Repository URL/name
            branch: Branch name
            file_path: File path within repository

        Returns:
            Complete resource URI
        """
        # Clean up components
        repository = repository.strip("/")
        branch = branch.strip("/")
        file_path = file_path.strip("/")

        return f"{cls.SCHEME}://{repository}/{branch}/{file_path}"

    @classmethod
    def validate_uri(cls, uri: str) -> bool:
        """Validate that a URI is a valid aimcp:// resource URI.

        Args:
            uri: URI to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            cls.parse_uri(uri)
        except ResourceURIError:
            return False
        else:
            return True

    @classmethod
    def is_aimcp_uri(cls, uri: str) -> bool:
        """Check if a URI uses the aimcp:// scheme.

        Args:
            uri: URI to check

        Returns:
            True if it's an aimcp:// URI, False otherwise
        """
        return uri.startswith(f"{cls.SCHEME}://")
