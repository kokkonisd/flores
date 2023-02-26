import os
import re
from typing import Any

import pytest

from flores.exceptions import (
    FileOrDirNotFoundError,
    TemplateError,
    WrongTypeOrFormatError,
)
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


def test_generate_site_with_permalinks_with_wrong_type(test_data_dir: str) -> None:
    """Attempt to generate a site with pages that contain permalinks of the wrong type.

    Since all permalinks should be of type `str`, we expect non-`str` permalinks to
    trigger an error that's reported along with the name of the offending page file.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_type_permalinks"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'foo.md')}: Expected type 'str' but "
            "got 'int' for key 'permalink'."
        ),
    ):
        generator.build()


def test_generate_site_with_relative_permalinks(test_data_dir: str) -> None:
    """Attempt to generate a site with pages that contain relative permalinks.

    Since all permalinks should be absolute (i.e. they should start with a slash), we
    expect relative permalinks to trigger an error that's reported along with the name
    of the offending page file.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_relative_permalinks"))

    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'foo.md')}: Relative permalink "
            "'about/foo' (should start with a slash)."
        ),
    ):
        generator.build()


def test_generate_site_with_root_permalinks(test_data_dir: str) -> None:
    """Attempt to generate a site with pages that contain root permalinks (/).

    Since defining a permalink that simply points to the root (e.g. "/foo") is the same
    as defining no permalink (which can be misleading), we expect root permalinks to
    trigger an error that's reported along with the name of the offending page file.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_root_permalinks"))

    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'foo.md')}: Redundant root permalink "
            "'/foo'."
        ),
    ):
        generator.build()


def test_generate_site_with_index_permalinks(test_data_dir: str) -> None:
    """Attempt to generate a site with pages that contain index permalinks (/).

    Since defining a permalink that simply points to the global index ("/") is an
    attempt to redefine the `index.md` page, we expect index permalinks to trigger an
    error that's reported along with the name of the offending page file.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_index_permalinks"))

    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'foo.md')}: Illegal index permalink "
            "'/' (would overwrite index)."
        ),
    ):
        generator.build()


def test_generate_site_with_malformed_permalinks(test_data_dir: str) -> None:
    """Attempt to generate a site with pages that contain root permalinks (/).

    Since defining a permalink that is malformed (e.g. "/../../tmp/"), we expect
    malformed permalinks to trigger an error that's reported along with the name of the
    offending page file.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_malformed_permalinks"))

    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'foo.md')}: Malformed permalink "
            f"'/aa/../../../../foo' (invalid or illegal path)."
        ),
    ):
        generator.build()


def test_generate_site_with_pages_with_conflicting_permalinks(
    test_data_dir: str, capsys: Any
) -> None:
    """Generate a test site with multiple pages with conflicting permalinks.

    Page conflicts because of permalinks should not trigger an error, but they should
    trigger a warning because most likely they are not intentional.
    """
    generator = Generator(
        os.path.join(test_data_dir, "pages_with_conflicting_permalinks")
    )
    generator.build()

    expected_elements = [
        os.path.join(generator.build_dir, "index.html"),
        os.path.join(generator.build_dir, "404.html"),
        os.path.join(generator.build_dir, "blog.html"),
        os.path.join(generator.build_dir, "blog"),
        os.path.join(generator.build_dir, "blog", "index.html"),
    ]

    actual_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            actual_elements.append(os.path.join(dirpath, element))

    assert sorted(actual_elements) == sorted(expected_elements)

    captured = capsys.readouterr()

    assert (
        f"Pages {os.path.join(generator.pages_dir, 'error.md')} and "
        f"{os.path.join(generator.pages_dir, '404.md')} have conflicting permalinks "
        "(the first will overwrite the second)."
    ) in captured.err
    assert (
        f"Pages {os.path.join(generator.pages_dir, 'categories.md')} and "
        f"{os.path.join(generator.pages_dir, 'blog.md')} have conflicting permalinks "
        "(the first will overwrite the second)."
    ) in captured.err


def test_generate_site_with_pages_with_permalinks(test_data_dir: str) -> None:
    """Generate a test site with multiple pages with permalinks.

    We expect that permalinks work correctly, and that pages are created at the
    locations described by the permalinks.
    """
    generator = Generator(os.path.join(test_data_dir, "pages_with_permalinks"))
    generator.build()

    expected_elements = [
        os.path.join(generator.build_dir, "index.html"),
        os.path.join(generator.build_dir, "blog.html"),
        os.path.join(generator.build_dir, "blog"),
        os.path.join(generator.build_dir, "blog", "index.html"),
        os.path.join(generator.build_dir, "blog", "categories.html"),
        os.path.join(generator.build_dir, "blog", "categories"),
        os.path.join(generator.build_dir, "blog", "categories", "index.html"),
        os.path.join(generator.build_dir, "profile"),
        os.path.join(generator.build_dir, "profile", "projects.html"),
        os.path.join(generator.build_dir, "profile", "projects"),
        os.path.join(generator.build_dir, "profile", "projects", "index.html"),
        os.path.join(generator.build_dir, "profile", "about"),
        os.path.join(generator.build_dir, "profile", "about", "contact.html"),
        os.path.join(generator.build_dir, "profile", "about", "contact"),
        os.path.join(generator.build_dir, "profile", "about", "contact", "index.html"),
    ]

    actual_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            actual_elements.append(os.path.join(dirpath, element))

    assert sorted(actual_elements) == sorted(expected_elements)

    expected_categories_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        "        <h1>Categories</h1>",
        "<ul>",
        "<li>foo</li>",
        "<li>bar</li>",
        "<li>baz</li>",
        "</ul>",
        "    </body>",
        "</html>",
    ]
    expected_projects_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        "        <h1>Projects</h1>",
        "    </body>",
        "</html>",
    ]
    expected_contact_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        "        <h1>Contact me</h1>",
        "    </body>",
        "</html>",
    ]

    with open(
        os.path.join(generator.build_dir, "blog", "categories.html"), "r"
    ) as file:
        actual_categories_page = file.read()
    with open(
        os.path.join(generator.build_dir, "blog", "categories", "index.html"), "r"
    ) as file:
        actual_categories_page_with_slash = file.read()
    with open(
        os.path.join(generator.build_dir, "profile", "projects.html"), "r"
    ) as file:
        actual_projects_page = file.read()
    with open(
        os.path.join(generator.build_dir, "profile", "projects", "index.html"), "r"
    ) as file:
        actual_projects_page_with_slash = file.read()
    with open(
        os.path.join(generator.build_dir, "profile", "about", "contact.html"), "r"
    ) as file:
        actual_contact_page = file.read()
    with open(
        os.path.join(generator.build_dir, "profile", "about", "contact", "index.html"),
        "r",
    ) as file:
        actual_contact_page_with_slash = file.read()

    assert actual_categories_page == "\n".join(expected_categories_page)
    assert actual_categories_page_with_slash == "\n".join(expected_categories_page)
    assert actual_projects_page == "\n".join(expected_projects_page)
    assert actual_projects_page_with_slash == "\n".join(expected_projects_page)
    assert actual_contact_page == "\n".join(expected_contact_page)
    assert actual_contact_page_with_slash == "\n".join(expected_contact_page)
