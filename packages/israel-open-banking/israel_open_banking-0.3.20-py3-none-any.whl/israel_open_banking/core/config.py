"""
Configuration management for the Israel Open Banking SDK.

This module handles configuration loading from environment variables
and provides a centralized configuration interface.
"""

import os
from typing import Any

from dotenv import load_dotenv

from .exceptions import ConfigurationError


class OpenBankingConfig:
    """Configuration manager for the Open Banking SDK."""

    def __init__(self, config_path: str | None = None) -> None:
        """
        Initialize configuration with optional .env file path.

        Args:
            config_path: Path to .env file (defaults to .env in current directory)
        """
        # Load environment variables from .env file if it exists
        if config_path:
            load_dotenv(config_path)
        else:
            load_dotenv()

        # API Configuration
        self.api_base_url = self._get_required_env("OPEN_BANKING_API_BASE_URL")
        self.api_timeout = int(self._get_env("OPEN_BANKING_API_TIMEOUT", "30"))
        self.api_retry_attempts = int(
            self._get_env("OPEN_BANKING_API_RETRY_ATTEMPTS", "3")
        )

        # Authentication
        self.client_id = self._get_required_env("OPEN_BANKING_CLIENT_ID")
        self.client_secret = self._get_required_env("OPEN_BANKING_CLIENT_SECRET")
        self.redirect_uri = self._get_required_env("OPEN_BANKING_REDIRECT_URI")

        # Logging
        self.log_level = self._get_env("OPEN_BANKING_LOG_LEVEL", "INFO")
        self.log_format = self._get_env(
            "OPEN_BANKING_LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        # Development settings
        self.debug = self._get_env("OPEN_BANKING_DEBUG", "false").lower() == "true"
        self.mock_responses = (
            self._get_env("OPEN_BANKING_MOCK_RESPONSES", "false").lower() == "true"
        )

        # Provider-specific settings
        self.providers = self._load_provider_config()

    def _get_env(self, key: str, default: str) -> str:
        """Get environment variable with default value."""
        return os.getenv(key, default)

    def _get_required_env(self, key: str) -> str:
        """Get required environment variable, raising error if not found."""
        value = os.getenv(key)
        if not value:
            raise ConfigurationError(f"Required environment variable {key} is not set")
        return value

    def _load_provider_config(self) -> dict[str, dict[str, Any]]:
        """Load provider-specific configuration."""
        providers = {}

        # Isracard configuration
        isracard_config = {}
        if os.getenv("ISRACARD_API_URL"):
            isracard_config["api_url"] = os.getenv("ISRACARD_API_URL")
        if os.getenv("ISRACARD_CLIENT_ID"):
            isracard_config["client_id"] = os.getenv("ISRACARD_CLIENT_ID")
        if os.getenv("ISRACARD_CLIENT_SECRET"):
            isracard_config["client_secret"] = os.getenv("ISRACARD_CLIENT_SECRET")

        if isracard_config:
            providers["isracard"] = isracard_config

        # Max configuration
        max_config = {}
        if os.getenv("MAX_API_URL"):
            max_config["api_url"] = os.getenv("MAX_API_URL")
        if os.getenv("MAX_CLIENT_ID"):
            max_config["client_id"] = os.getenv("MAX_CLIENT_ID")
        if os.getenv("MAX_CLIENT_SECRET"):
            max_config["client_secret"] = os.getenv("MAX_CLIENT_SECRET")

        if max_config:
            providers["max"] = max_config

        # Cal configuration
        cal_config = {}
        if os.getenv("CAL_API_URL"):
            cal_config["api_url"] = os.getenv("CAL_API_URL")
        if os.getenv("CAL_CLIENT_ID"):
            cal_config["client_id"] = os.getenv("CAL_CLIENT_ID")
        if os.getenv("CAL_CLIENT_SECRET"):
            cal_config["client_secret"] = os.getenv("CAL_CLIENT_SECRET")

        if cal_config:
            providers["cal"] = cal_config

        return providers

    def get_provider_config(self, provider: str) -> dict[str, Any]:
        """
        Get configuration for a specific provider.

        Args:
            provider: Provider name (e.g., 'isracard', 'max', 'cal')

        Returns:
            Provider-specific configuration dictionary

        Raises:
            ConfigurationError: If provider configuration is not found
        """
        if provider not in self.providers:
            raise ConfigurationError(
                f"Configuration not found for provider: {provider}"
            )
        return self.providers[provider]

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            "api_base_url": self.api_base_url,
            "api_timeout": self.api_timeout,
            "api_retry_attempts": self.api_retry_attempts,
            "redirect_uri": self.redirect_uri,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "debug": self.debug,
            "mock_responses": self.mock_responses,
            "providers": list(self.providers.keys()),
        }
