import os
import re

import pytest

from flores.exceptions import FileOrDirNotFoundError, FloresError, TemplateError
from flores.generator import Generator


def test_generate_user_data_pages_with_template_errors(test_data_dir: str) -> None:
    """Attempt to generate user data pages containing template errors.

    We expect that template errors within the pages themselves will be reported along
    with information about which file contains the error.
    """
    generator = Generator(os.path.join(test_data_dir, "user_data_page_template_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.project_dir, '_mypages', 'my-first-page.md')}: "
            "'site_owner' is undefined."
        ),
    ):
        generator.build()


def test_generate_user_data_pages_with_templates_with_template_errors(
    test_data_dir: str,
) -> None:
    """Attempt to generate user data pages with templates containing template errors.

    We expect that template errors within the templates themselves will be reported
    along with information about which file contains the error.
    """
    generator = Generator(os.path.join(test_data_dir, "template_template_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.templates_dir, 'main.html')}:? (from "
            f"{os.path.join(generator.project_dir, '_mypages', 'my-first-page.md')}): "
            "'pag' is undefined."
        ),
    ):
        generator.build()


def test_generate_user_data_pages_with_missing_template(test_data_dir: str) -> None:
    """Attempt to generate user data pages with a missing template.

    We expect that an error is reported when attempting to use a template that does not
    exist.
    """
    generator = Generator(os.path.join(test_data_dir, "missing_template"))

    with pytest.raises(
        FileOrDirNotFoundError,
        match=re.escape(
            f"{os.path.join(generator.project_dir, '_mypages', 'my-first-page.md')}: "
            f"Template 'main' not found in {generator.templates_dir}."
        ),
    ):
        generator.build()


def test_generate_user_data_pages_with_permalinks(test_data_dir: str) -> None:
    """Attempt to generate a site with user data pages that contain permalinks.

    Since permalinks are not allowed for user data pages, we expect them to trigger an
    error that's reported along with the name of the offending page file.
    """
    generator = Generator(
        os.path.join(test_data_dir, "user_data_pages_with_permalinks")
    )

    with pytest.raises(
        FloresError,
        match=re.escape(
            f"{os.path.join(generator.project_dir, '_mypages', 'hello.md')}: "
            "Permalinks are not allowed for user data pages."
        ),
    ):
        generator.build()


def test_generate_site_with_user_data_pages(test_data_dir: str) -> None:
    """Generate a site containing custom user data pages.

    We expect that all the directories prefixed by an underscore (_) will contain custom
    user data pages, and that they will all be picked up and used in the final build of
    the site.
    """
    generator = Generator(os.path.join(test_data_dir, "complete_pages"))
    generator.build()

    expected_elements = [
        os.path.join(generator.build_dir, "mypages"),
        os.path.join(generator.build_dir, "myotherpages"),
        os.path.join(generator.build_dir, "mypages", "my-first-page.html"),
        os.path.join(generator.build_dir, "mypages", "my-first-page"),
        os.path.join(generator.build_dir, "mypages", "my-first-page", "index.html"),
        os.path.join(generator.build_dir, "mypages", "my-second-page.html"),
        os.path.join(generator.build_dir, "mypages", "my-second-page"),
        os.path.join(generator.build_dir, "mypages", "my-second-page", "index.html"),
        os.path.join(generator.build_dir, "myotherpages", "my-third-page.html"),
        os.path.join(generator.build_dir, "myotherpages", "my-third-page"),
        os.path.join(
            generator.build_dir, "myotherpages", "my-third-page", "index.html"
        ),
    ]

    actual_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            actual_elements.append(os.path.join(dirpath, element))

    assert sorted(actual_elements) == sorted(expected_elements)

    expected_first_page = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <p>Hello!</p>",
            "    </body>",
            "</html>",
        ]
    )
    expected_second_page = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <p>Hi again!</p>",
            "    </body>",
            "</html>",
        ]
    )
    expected_third_page = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <p>Salutations for the third time!</p>",
            "    </body>",
            "</html>",
        ]
    )

    with open(
        os.path.join(generator.build_dir, "mypages", "my-first-page.html"), "r"
    ) as file:
        actual_first_page = file.read()
    with open(
        os.path.join(generator.build_dir, "mypages", "my-first-page", "index.html"), "r"
    ) as file:
        actual_first_page_with_slash = file.read()
    with open(
        os.path.join(generator.build_dir, "mypages", "my-second-page.html"), "r"
    ) as file:
        actual_second_page = file.read()
    with open(
        os.path.join(generator.build_dir, "mypages", "my-second-page", "index.html"),
        "r",
    ) as file:
        actual_second_page_with_slash = file.read()
    with open(
        os.path.join(generator.build_dir, "myotherpages", "my-third-page.html"), "r"
    ) as file:
        actual_third_page = file.read()
    with open(
        os.path.join(
            generator.build_dir, "myotherpages", "my-third-page", "index.html"
        ),
        "r",
    ) as file:
        actual_third_page_with_slash = file.read()

    assert actual_first_page == expected_first_page
    assert actual_first_page_with_slash == expected_first_page
    assert actual_second_page == expected_second_page
    assert actual_second_page_with_slash == expected_second_page
    assert actual_third_page == expected_third_page
    assert actual_third_page_with_slash == expected_third_page
