"""
Configuration for YouTrack MCP server.

This module handles all configuration for the YouTrack MCP server including:
- API credentials and URL configuration
- SSL certificate verification settings
- Cloud vs self-hosted instance detection
- MCP server settings

Important notes for using the server:
1. Always use get_project_detailed() before creating issues to see required fields
2. Project short names (e.g., 'ITSFT') are automatically resolved to IDs
3. Custom field values must match exactly from possible_values (case-sensitive)
4. Use field names or IDs when setting custom fields
"""

import os
import ssl

# Optional import for dotenv
try:
    from dotenv import load_dotenv

    # Load environment variables from .env file if it exists
    load_dotenv()
except ImportError:
    # dotenv is not required
    pass


class Config:
    """Configuration settings for YouTrack MCP server."""

    # YouTrack API configuration
    YOUTRACK_URL: str = os.getenv('YOUTRACK_URL', '')
    YOUTRACK_API_TOKEN: str = os.getenv('YOUTRACK_API_TOKEN', '')
    VERIFY_SSL: bool = os.getenv('YOUTRACK_VERIFY_SSL', 'true').lower() in ('true', '1', 'yes')

    # Cloud instance configuration
    YOUTRACK_CLOUD: bool = os.getenv('YOUTRACK_CLOUD', 'false').lower() in ('true', '1', 'yes')

    # API client configuration
    MAX_RETRIES: int = int(os.getenv('YOUTRACK_MAX_RETRIES', '3'))
    RETRY_DELAY: float = float(os.getenv('YOUTRACK_RETRY_DELAY', '1.0'))

    # MCP Server configuration
    MCP_SERVER_NAME: str = os.getenv('MCP_SERVER_NAME', 'youtrack-rocket-mcp')
    MCP_SERVER_DESCRIPTION: str = os.getenv('MCP_SERVER_DESCRIPTION', '🚀 YouTrack Rocket MCP Server')
    MCP_DEBUG: bool = os.getenv('MCP_DEBUG', 'false').lower() in ('true', '1', 'yes')

    @classmethod
    def from_dict(cls, config_dict: dict[str, str | int | float | bool]) -> None:
        """
        Update configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration values
        """
        # Set configuration values from the dictionary
        for key, value in config_dict.items():
            if hasattr(cls, key):
                setattr(cls, key, value)

    @classmethod
    def validate(cls) -> None:
        """
        Validate the configuration settings.

        Raises:
            ValueError: If required settings are missing or invalid
        """
        # API token is always required
        if not cls.YOUTRACK_API_TOKEN:
            raise ValueError(
                'YouTrack API token is required. '
                'Provide it using YOUTRACK_API_TOKEN environment variable or in configuration.'
            )

        # URL is only required for self-hosted instances (Cloud instances can use API token only)
        if not cls.YOUTRACK_CLOUD and not cls.YOUTRACK_URL:
            raise ValueError(
                'YouTrack URL is required for self-hosted instances. '
                'Provide it using YOUTRACK_URL environment variable '
                'or set YOUTRACK_CLOUD=true for cloud instances.'
            )

        # If URL is provided, ensure it doesn't end with a trailing slash
        if cls.YOUTRACK_URL:
            cls.YOUTRACK_URL = cls.YOUTRACK_URL.rstrip('/')

    @classmethod
    def get_ssl_context(cls) -> ssl.SSLContext | None:
        """
        Get SSL context for HTTPS requests.

        Returns:
            SSLContext with proper configuration or None for default behavior
        """
        if not cls.VERIFY_SSL:
            # Create a context that doesn't verify certificates
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context

        return None

    @classmethod
    def is_cloud_instance(cls) -> bool:
        """
        Check if the configured YouTrack instance is a cloud instance.

        Returns:
            True if the instance is a cloud instance, False otherwise
        """
        return cls.YOUTRACK_CLOUD or not cls.YOUTRACK_URL

    @classmethod
    def get_base_url(cls) -> str:
        """
        Get the base URL for the YouTrack instance API.

        For self-hosted instances, this is the configured URL.
        For cloud instances, this is the workspace-specific youtrack.cloud API URL,
        which is extracted from the API token or used directly if provided.

        Returns:
            Base URL for the YouTrack API
        """
        # If URL is explicitly provided, use it regardless of cloud setting
        if cls.YOUTRACK_URL:
            return f'{cls.YOUTRACK_URL}/api'

        # For cloud instances without explicit URL, try to extract from token
        if cls.is_cloud_instance():
            # Handle both token formats: perm: and perm-
            if '.' in cls.YOUTRACK_API_TOKEN and (
                cls.YOUTRACK_API_TOKEN.startswith('perm:') or cls.YOUTRACK_API_TOKEN.startswith('perm-')
            ):
                token_parts = cls.YOUTRACK_API_TOKEN.split('.')

                # Extract workspace from specific token formats
                if len(token_parts) > 1:
                    # For format: perm:username.workspace.12345...
                    if cls.YOUTRACK_API_TOKEN.startswith('perm:'):
                        workspace = token_parts[1]
                        return f'https://{workspace}.youtrack.cloud/api'

                    # For format: perm-base64.base64.hash
                    if cls.YOUTRACK_API_TOKEN.startswith('perm-'):
                        # If we have a fixed workspace name from environment, use it
                        workspace_env: str | None = os.getenv('YOUTRACK_WORKSPACE')
                        if workspace_env is not None:
                            return f'https://{workspace_env}.youtrack.cloud/api'

                        if os.getenv('YOUTRACK_URL'):
                            return f'{os.getenv("YOUTRACK_URL")}/api'

            # Fallback error with better guidance
            raise ValueError(
                'Could not determine YouTrack Cloud URL. Please either:\n'
                '1. Set YOUTRACK_URL to your YouTrack Cloud URL (e.g., https://yourworkspace.youtrack.cloud)\n'
                '2. Set YOUTRACK_WORKSPACE to your workspace name\n'
                '3. Use a token in the format perm:username.workspace.12345...'
            )

        # Should never reach here as is_cloud_instance() returns True if URL is missing
        raise ValueError('YouTrack URL is required. Please set YOUTRACK_URL environment variable.')


# Create a global config instance
config = Config()
