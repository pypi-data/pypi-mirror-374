"""Integration tests for the SDK."""

from prompt_studio import PromptStudio, render


class TestIntegration:
    """Integration test cases."""

    def test_full_workflow(self, httpx_mock):
        """Test complete workflow: fetch prompt and render."""
        studio = PromptStudio(api_key="test-key")

        # Mock API response
        httpx_mock.add_response(
            url="https://api-studio.dev.trustsoft.ai/sdk-api/prompt?projectName=test-project&promptName=greeting-prompt",
            json={"body": "Hello, {{name}}! Welcome to {{platform}}."},
            status_code=200,
        )

        # Fetch prompt
        prompt = studio.get_prompt("test-project", "greeting-prompt")

        # Render prompt
        result = render(prompt, {"name": "Alice", "platform": "Prompt Studio"})

        assert result == "Hello, Alice! Welcome to Prompt Studio."

    def test_workflow_with_conditional_template(self, httpx_mock):
        """Test workflow with conditional template."""
        studio = PromptStudio(api_key="test-key")

        # Mock API response with conditional template
        httpx_mock.add_response(
            url="https://api-studio.dev.trustsoft.ai/sdk-api/prompt?projectName=test-project&promptName=user-greeting",
            json={
                "body": "{% if user.premium %}Welcome back, premium user {{user.name}}!{% else %}Hello {{user.name}}, consider upgrading!{% endif %}"
            },
            status_code=200,
        )

        # Fetch prompt
        prompt = studio.get_prompt("test-project", "user-greeting")

        # Test premium user
        result_premium = render(prompt, {"user": {"name": "Bob", "premium": True}})
        assert result_premium == "Welcome back, premium user Bob!"

        # Test regular user
        result_regular = render(prompt, {"user": {"name": "Alice", "premium": False}})
        assert result_regular == "Hello Alice, consider upgrading!"

    def test_import_all_components(self):
        """Test that all components can be imported."""
        from prompt_studio import (
            PromptNotFoundError,
            PromptStudio,
            PromptStudioError,
            TemplateRenderError,
            render,
        )

        # Verify all imports work
        assert PromptStudio is not None
        assert render is not None
        assert PromptStudioError is not None
        assert PromptNotFoundError is not None
        assert TemplateRenderError is not None
