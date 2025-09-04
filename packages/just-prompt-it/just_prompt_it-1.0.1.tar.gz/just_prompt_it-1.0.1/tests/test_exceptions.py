"""Tests for custom exceptions."""

from prompt_studio.exceptions import (
    PromptNotFoundError,
    PromptStudioError,
    TemplateRenderError,
)


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_prompt_studio_error(self):
        """Test base PromptStudioError."""
        error = PromptStudioError("Base error")
        assert str(error) == "Base error"
        assert isinstance(error, Exception)

    def test_prompt_not_found_error(self):
        """Test PromptNotFoundError inheritance."""
        error = PromptNotFoundError("Prompt not found")
        assert str(error) == "Prompt not found"
        assert isinstance(error, PromptStudioError)
        assert isinstance(error, Exception)

    def test_template_render_error(self):
        """Test TemplateRenderError inheritance."""
        error = TemplateRenderError("Template error")
        assert str(error) == "Template error"
        assert isinstance(error, PromptStudioError)
        assert isinstance(error, Exception)

    def test_exception_hierarchy(self):
        """Test exception hierarchy."""
        # All custom exceptions should inherit from PromptStudioError
        assert issubclass(PromptNotFoundError, PromptStudioError)
        assert issubclass(TemplateRenderError, PromptStudioError)

        # PromptStudioError should inherit from Exception
        assert issubclass(PromptStudioError, Exception)
