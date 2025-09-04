"""Tests for PromptStudio class."""

import os
from unittest.mock import patch

import pytest

from prompt_studio import PromptStudio
from prompt_studio.exceptions import APIKeyError, PromptNotFoundError


class TestPromptStudio:
    """Test cases for the PromptStudio class."""

    def test_init(self):
        """Test PromptStudio initialization."""
        studio = PromptStudio(api_key="test-key")
        assert studio.api_key == "test-key"
        assert studio.base_url == "https://api-studio.dev.trustsoft.ai"
        assert studio.headers["Authorization"] == "Bearer test-key"

    def test_init_custom_base_url(self):
        """Test PromptStudio initialization with custom base URL."""
        custom_url = "https://custom.api.com"
        studio = PromptStudio(api_key="test-key", base_url=custom_url)
        assert studio.base_url == custom_url

    def test_init_from_env(self):
        """Test PromptStudio initialization from environment variable."""
        with patch.dict(os.environ, {"PROMPT_STUDIO_API_KEY": "env-key"}):
            studio = PromptStudio()
            assert studio.api_key == "env-key"

    def test_init_no_api_key(self):
        """Test PromptStudio initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(APIKeyError, match="API key must be provided"):
                PromptStudio()

    def test_get_prompt_success(self, httpx_mock):
        """Test successful prompt retrieval."""
        studio = PromptStudio(api_key="test-key")

        httpx_mock.add_response(
            url="https://api-studio.dev.trustsoft.ai/sdk-api/prompt?projectName=test-project&promptName=test-prompt",
            json={"body": "Hello, {{name}}!"},
            status_code=200,
        )

        result = studio.get_prompt("test-project", "test-prompt")
        assert result == "Hello, {{name}}!"

    def test_get_prompt_with_alias(self, httpx_mock):
        """Test prompt retrieval with alias."""
        studio = PromptStudio(api_key="test-key")

        httpx_mock.add_response(
            url="https://api-studio.dev.trustsoft.ai/sdk-api/prompt?projectName=test-project&promptName=test-prompt&alias=v1.0",
            json={"body": "Hello, {{name}}!"},
            status_code=200,
        )

        result = studio.get_prompt("test-project", "test-prompt", alias="v1.0")
        assert result == "Hello, {{name}}!"

    def test_get_prompt_not_found(self, httpx_mock):
        """Test prompt not found error."""
        studio = PromptStudio(api_key="test-key")

        httpx_mock.add_response(
            url="https://api-studio.dev.trustsoft.ai/sdk-api/prompt?projectName=test-project&promptName=nonexistent-prompt",
            status_code=404,
        )

        with pytest.raises(PromptNotFoundError, match="not found in project"):
            studio.get_prompt("test-project", "nonexistent-prompt")

    def test_get_prompt_api_error(self, httpx_mock):
        """Test API error handling."""
        studio = PromptStudio(api_key="test-key")

        httpx_mock.add_response(
            url="https://api-studio.dev.trustsoft.ai/sdk-api/prompt?projectName=test-project&promptName=test-prompt",
            text="Internal Server Error",
            status_code=500,
        )

        with pytest.raises(PromptNotFoundError, match="Failed to fetch prompt"):
            studio.get_prompt("test-project", "test-prompt")

    @pytest.mark.asyncio
    async def test_a_get_prompt_success(self, httpx_mock):
        """Test successful async prompt retrieval."""
        studio = PromptStudio(api_key="test-key")

        httpx_mock.add_response(
            url="https://api-studio.dev.trustsoft.ai/sdk-api/prompt?projectName=test-project&promptName=test-prompt",
            json={"body": "Hello, {{name}}!"},
            status_code=200,
        )

        result = await studio.a_get_prompt("test-project", "test-prompt")
        assert result == "Hello, {{name}}!"
