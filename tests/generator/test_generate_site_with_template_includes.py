import os
import re

import pytest

from flores.exceptions import TemplateError
from flores.generator import Generator


def test_template_errors(test_data_dir: str) -> None:
    """Generate a site with templates that contain errors.

    We expect that any errors from within the templates themselves will be reported
    along with the appropriate file (and possibly line number).
    """
    generator = Generator(os.path.join(test_data_dir, "template_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.templates_dir, 'main.html')}:4: unexpected '}}'."
        ),
    ):
        generator.build()


def test_template_python_errors(test_data_dir: str) -> None:
    """Generate a site with templates that contain "classic" Python errors.

    We expect that any Python errors (i.e. not Jinja syntax errors) from within the
    templates themselves will be reported along with the appropriate file (and possibly
    line number).
    """
    generator = Generator(os.path.join(test_data_dir, "template_python_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.templates_dir, 'main.html')}:? (from "
            f"{os.path.join(generator.pages_dir, 'index.md')}): division by zero."
        ),
    ):
        generator.build()


def test_template_include_errors(test_data_dir: str) -> None:
    """Generate a site with template includes that contain errors.

    We expect that any errors from within the template includes themselves will be
    reported along with the appropriate file (and possibly line number).
    """
    generator = Generator(os.path.join(test_data_dir, "template_include_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.templates_dir, 'includes', 'footer.html')}:2 "
            f"(from {os.path.join(generator.pages_dir, 'index.md')}): "
            "unexpected '}'."
        ),
    ):
        generator.build()


def test_generate_site_with_template_includes(test_data_dir: str) -> None:
    """Generate a site with complex templates.

    We expect that templates can include other templates, and that data is correctly
    propagated to all templates and includes.
    """
    generator = Generator(os.path.join(test_data_dir, "complete_templates"))
    generator.build()
