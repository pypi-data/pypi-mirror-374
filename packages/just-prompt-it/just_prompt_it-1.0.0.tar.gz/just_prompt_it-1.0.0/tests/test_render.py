"""Tests for render functionality."""

import pytest

from prompt_studio import render
from prompt_studio.exceptions import TemplateRenderError
from prompt_studio.render import preprocess_template


class TestRender:
    """Test cases for the render function."""

    def test_basic_render(self):
        """Test basic template rendering."""
        template = "Hello, {{name}}!"
        context = {"name": "World"}
        result = render(template, context)
        assert result == "Hello, World!"

    def test_multiple_variables(self):
        """Test rendering with multiple variables."""
        template = "{{greeting}}, {{name}}! Welcome to {{platform}}."
        context = {"greeting": "Hi", "name": "Alice", "platform": "Prompt Studio"}
        result = render(template, context)
        assert result == "Hi, Alice! Welcome to Prompt Studio."

    def test_conditional_rendering(self):
        """Test conditional template rendering."""
        template = "{% if premium %}Premium user{% else %}Regular user{% endif %}"

        result_premium = render(template, {"premium": True})
        assert result_premium == "Premium user"

        result_regular = render(template, {"premium": False})
        assert result_regular == "Regular user"

    def test_conditional_with_preprocessing(self):
        """Test conditional with double braces preprocessing."""
        template = "{% if {{is_active}} %}Active{% else %}Inactive{% endif %}"
        context = {"is_active": True}
        result = render(template, context)
        assert result == "Active"

    def test_loop_rendering(self):
        """Test loop in template rendering."""
        template = "Items: {% for item in items %}{{item}}{% if not loop.last %}, {% endif %}{% endfor %}"
        context = {"items": ["apple", "banana", "cherry"]}
        result = render(template, context)
        assert result == "Items: apple, banana, cherry"

    def test_nested_data(self):
        """Test rendering with nested data structures."""
        template = "User: {{user.name}}, Age: {{user.age}}"
        context = {"user": {"name": "Bob", "age": 30}}
        result = render(template, context)
        assert result == "User: Bob, Age: 30"

    def test_strict_mode_undefined_variable(self):
        """Test strict mode with undefined variable."""
        template = "Hello, {{undefined_var}}!"
        with pytest.raises(TemplateRenderError, match="Undefined variable"):
            render(template, {}, strict=True)

    def test_non_strict_mode_undefined_variable(self):
        """Test non-strict mode with undefined variable."""
        template = "Hello, {{undefined_var}}!"
        result = render(template, {}, strict=False)
        assert result == "Hello, !"

    def test_template_syntax_error(self):
        """Test template with syntax error."""
        template = "Hello, {{name}!"  # Missing closing brace
        with pytest.raises(TemplateRenderError, match="Template syntax error"):
            render(template, {"name": "World"})

    def test_empty_template(self):
        """Test rendering empty template."""
        result = render("", {})
        assert result == ""

    def test_template_with_whitespace_control(self):
        """Test template with whitespace control."""
        template = """
        {% if name %}
        Hello, {{name}}!
        {% endif %}
        """
        context = {"name": "Alice"}
        result = render(template, context)
        assert "Hello, Alice!" in result
        assert result.strip() == "Hello, Alice!"

    def test_jinja_template_error(self, monkeypatch):
        """Test handling of generic Jinja2 TemplateError during rendering."""
        import jinja2

        def mock_render(self, *args, **kwargs):
            raise jinja2.TemplateError("Mock template error")

        # Patch Template.render to raise TemplateError
        monkeypatch.setattr(jinja2.Template, "render", mock_render)

        with pytest.raises(TemplateRenderError, match="Error rendering template"):
            render("{{ test }}", {"test": "value"})


class TestPreprocessTemplate:
    """Test cases for the preprocess_template function."""

    def test_preprocess_simple_condition(self):
        """Test preprocessing simple conditional."""
        template = "{% if {{user_active}} %}Active{% endif %}"
        processed = preprocess_template(template)
        assert processed == "{% if user_active %}Active{% endif %}"

    def test_preprocess_multiple_variables_in_block(self):
        """Test preprocessing multiple variables in control block."""
        template = (
            "{% if {{user_active}} and {{user_premium}} %}Premium Active{% endif %}"
        )
        processed = preprocess_template(template)
        assert (
            processed
            == "{% if user_active and user_premium %}Premium Active{% endif %}"
        )

    def test_preprocess_for_loop(self):
        """Test preprocessing for loop."""
        template = "{% for item in {{items}} %}{{item}}{% endfor %}"
        processed = preprocess_template(template)
        assert processed == "{% for item in items %}{{item}}{% endfor %}"

    def test_preprocess_no_change_needed(self):
        """Test preprocessing when no change is needed."""
        template = "{% if user_active %}Hello {{name}}!{% endif %}"
        processed = preprocess_template(template)
        assert processed == template

    def test_preprocess_mixed_content(self):
        """Test preprocessing with mixed content."""
        template = (
            "{% if {{active}} %}Hello {{name}}!{% endif %} Welcome to {{platform}}."
        )
        processed = preprocess_template(template)
        assert (
            processed
            == "{% if active %}Hello {{name}}!{% endif %} Welcome to {{platform}}."
        )

    def test_preprocess_nested_blocks(self):
        """Test preprocessing with nested blocks."""
        template = "{% if {{user}} %}{% for item in {{items}} %}{{item}}{% endfor %}{% endif %}"
        processed = preprocess_template(template)
        assert (
            processed
            == "{% if user %}{% for item in items %}{{item}}{% endfor %}{% endif %}"
        )

    def test_preprocess_empty_string(self):
        """Test preprocessing empty string."""
        processed = preprocess_template("")
        assert processed == ""

    def test_preprocess_complex_expressions(self):
        """Test preprocessing with complex variable expressions."""
        template = "{% if {{user.profile.active}} %}User active{% endif %}"
        processed = preprocess_template(template)
        assert processed == "{% if user.profile.active %}User active{% endif %}"

    def test_preprocess_array_access(self):
        """Test preprocessing with array access."""
        template = "{% for item in {{data[0]}} %}{{item}}{% endfor %}"
        processed = preprocess_template(template)
        assert processed == "{% for item in data[0] %}{{item}}{% endfor %}"

    def test_preprocess_set_block(self):
        """Test preprocessing with set block."""
        template = "{% set value = {{config.default}} %}{{value}}"
        processed = preprocess_template(template)
        assert processed == "{% set value = config.default %}{{value}}"

    def test_preprocess_with_block(self):
        """Test preprocessing with 'with' block."""
        template = "{% with context = {{user.context}} %}{{context}}{% endwith %}"
        processed = preprocess_template(template)
        assert processed == "{% with context = user.context %}{{context}}{% endwith %}"

    def test_preprocess_elif_block(self):
        """Test preprocessing with elif block."""
        template = "{% if condition %}A{% elif {{other_condition}} %}B{% endif %}"
        processed = preprocess_template(template)
        assert processed == "{% if condition %}A{% elif other_condition %}B{% endif %}"

    def test_preprocess_macro_block(self):
        """Test preprocessing with macro block."""
        template = "{% macro test(param={{default_value}}) %}{{param}}{% endmacro %}"
        processed = preprocess_template(template)
        assert (
            processed == "{% macro test(param=default_value) %}{{param}}{% endmacro %}"
        )

    def test_preprocess_filter_block(self):
        """Test preprocessing with filter block."""
        template = (
            "{% filter upper %}{% if {{show_text}} %}hello{% endif %}{% endfilter %}"
        )
        processed = preprocess_template(template)
        assert (
            processed
            == "{% filter upper %}{% if show_text %}hello{% endif %}{% endfilter %}"
        )

    def test_preprocess_malformed_template(self):
        """Test preprocessing with malformed template raises ValueError."""
        # This should not raise an error as the function handles it gracefully
        template = "{% if {{unclosed"
        processed = preprocess_template(template)
        assert processed == template  # Should return unchanged if no valid blocks found

    def test_preprocess_whitespace_handling(self):
        """Test preprocessing handles whitespace correctly."""
        template = "{% if {{ user_active }} %}Active{% endif %}"
        processed = preprocess_template(template)
        assert processed == "{% if user_active %}Active{% endif %}"

    def test_preprocess_multiple_control_blocks(self):
        """Test preprocessing multiple different control blocks."""
        template = "{% set x = {{value}} %}{% if {{x}} %}{% for i in {{range}} %}{{i}}{% endfor %}{% endif %}"
        processed = preprocess_template(template)
        assert (
            processed
            == "{% set x = value %}{% if x %}{% for i in range %}{{i}}{% endfor %}{% endif %}"
        )

    def test_preprocess_regex_error(self, monkeypatch):
        """Test preprocessing handles regex errors gracefully."""
        import re
        # from prompt_studio import render as render_module

        def mock_sub(*args, **kwargs):
            raise re.error("Mock regex error")

        # Patch re.sub in the global re module
        monkeypatch.setattr(re, "sub", mock_sub)

        with pytest.raises(ValueError, match="Error processing template"):
            preprocess_template("{% if {{test}} %}content{% endif %}")
