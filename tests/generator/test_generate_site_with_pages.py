import os
import re

import pytest

from flores.exceptions import FileOrDirNotFoundError, TemplateError
from flores.generator import Generator


def test_generate_pages_with_template_errors(test_data_dir: str) -> None:
    """Attempt to generate pages with template errors.

    We expect that template errors within the pages themselves will be reported along
    with information about which file contains the error.
    """
    generator = Generator(os.path.join(test_data_dir, "page_template_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'index.md')}: 'user' is undefined."
        ),
    ):
        generator.build()


def test_generate_pages_with_python_errors(test_data_dir: str) -> None:
    """Attempt to generate pages with Jinja code that contains "classic" Python errors.

    We expect that any Python errors (i.e. not Jinja syntax errors) from within the
    pages themselves will be reported along with the appropriate file.
    """
    generator = Generator(os.path.join(test_data_dir, "page_python_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'index.md')}: division by zero."
        ),
    ):
        generator.build()


def test_generate_pages_with_templates_with_template_errors(test_data_dir: str) -> None:
    """Attempt to generate pages with templates that contain template errors.

    We expect that template errors within the templates used by pages will be reported
    along with information about which template and which page file contain the error.
    """
    generator = Generator(os.path.join(test_data_dir, "template_template_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.templates_dir, 'main.html')}:? (from "
            f"{os.path.join(generator.pages_dir, 'index.md')}): 'dict object' has no "
            "attribute 'blag'."
        ),
    ):
        generator.build()


def test_generate_site_with_pages_missing_template(test_data_dir: str) -> None:
    """Attempt to generate a test site with pages with missing templates.

    We expect that if a page asks for a template that does not exist, the build of the
    site should fail.
    """
    generator = Generator(os.path.join(test_data_dir, "missing_template"))

    with pytest.raises(
        FileOrDirNotFoundError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'index.md')}: Template "
            f"'what-template' not found in {generator.templates_dir}."
        ),
    ):
        generator.build()


def test_generate_site_with_pages(test_data_dir: str) -> None:
    """Generate a test site with multiple pages.

    We expect that pages work correctly, and that they pass their data to the templates.
    """
    generator = Generator(os.path.join(test_data_dir, "complete_pages"))
    generator.build()

    assert sorted(os.listdir(generator.build_dir)) == sorted(["index.html", "404.html"])

    index_page_file = os.path.join(generator.build_dir, "index.html")
    error_page_file = os.path.join(generator.build_dir, "404.html")

    expected_index_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        "        <p>Welcome to the site!</p>",
        "            <table>",
        "                <thead>",
        "                    <tr>",
        "                        <th>Fruit</th>",
        "                        <th>Do I like it?</th>",
        "                    </tr>",
        "                </thead>",
        "                <tbody>",
        "                        <tr>",
        "                            <td>Banana</td>",
        "                            <td>Yes</td>",
        "                        </tr>",
        "                        <tr>",
        "                            <td>Orange</td>",
        "                            <td>Yes</td>",
        "                        </tr>",
        "                        <tr>",
        "                            <td>Mango</td>",
        "                            <td>No</td>",
        "                        </tr>",
        "                </tbody>",
        "            </table>",
        "    </body>",
        "</html>",
    ]

    expected_error_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        "        <p>404: page not found :/</p>",
        "    </body>",
        "</html>",
    ]

    with open(index_page_file, "r") as file:
        actual_index_page = file.read()
    with open(error_page_file, "r") as file:
        actual_error_page = file.read()

    assert actual_index_page == "\n".join(expected_index_page)
    assert actual_error_page == "\n".join(expected_error_page)
