import os
import re

import pytest

from flores.exceptions import FileOrDirNotFoundError, TemplateError
from flores.generator import Generator


def test_generate_posts_with_template_errors(test_data_dir: str) -> None:
    """Attempt to generate posts with template errors.

    We expect that template errors within the posts themselves will be reported along
    with information about which file contains the error.
    """
    generator = Generator(os.path.join(test_data_dir, "post_template_errors"))

    with pytest.raises(
        TemplateError,
        match=(
            f"{os.path.join(generator.posts_dir, '1970-01-01-hello.md')}: 'data' is "
            "undefined."
        ),
    ):
        generator.build()


def test_generate_posts_with_templates_with_template_errors(test_data_dir: str) -> None:
    """Attempt to generate posts with templates that contain template errors.

    We expect that template errors within the templates used by posts will be reported
    along with information about which template and which post file contain the error.
    """
    generator = Generator(os.path.join(test_data_dir, "template_template_errors"))

    with pytest.raises(
        TemplateError,
        match=re.escape(
            f"{os.path.join(generator.templates_dir, 'main.html')}:? (from "
            f"{os.path.join(generator.posts_dir, '1970-01-01-hello.md')}): 'pagee' is "
            "undefined."
        ),
    ):
        generator.build()


def test_generate_site_with_posts_missing_template(test_data_dir: str) -> None:
    """Attempt to generate a test site with posts with missing templates.

    We expect that if a post asks for a template that does not exist, the build of the
    site should fail.
    """
    generator = Generator(os.path.join(test_data_dir, "missing_template"))

    with pytest.raises(
        FileOrDirNotFoundError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-12-post.md')}: Template "
            f"'what-template' not found in {generator.templates_dir}."
        ),
    ):
        generator.build()


def test_generate_site_with_posts(test_data_dir: str) -> None:
    """Generate a test site with multiple posts.

    We expect that posts work correctly, and that they pass their data to the templates.
    """
    generator = Generator(os.path.join(test_data_dir, "complete_posts"))
    generator.build()

    expected_elements = [
        os.path.join(generator.build_dir, "1999"),
        os.path.join(generator.build_dir, "2000"),
        os.path.join(generator.build_dir, "1999", "07"),
        os.path.join(generator.build_dir, "1999", "08"),
        os.path.join(generator.build_dir, "1999", "07", "10"),
        os.path.join(generator.build_dir, "1999", "08", "03"),
        os.path.join(generator.build_dir, "1999", "07", "10", "foo.html"),
        os.path.join(generator.build_dir, "1999", "08", "03", "bar.html"),
        os.path.join(generator.build_dir, "2000", "01"),
        os.path.join(generator.build_dir, "2000", "01", "02"),
        os.path.join(generator.build_dir, "2000", "01", "02", "baz.html"),
    ]

    actual_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            actual_elements.append(os.path.join(dirpath, element))

    assert sorted(actual_elements) == sorted(expected_elements)

    expected_foo_post = [
        "<!DOCTYPE html>",
        "<html>",
        "    <head>",
        "        <title>Foo - the blog</title>",
        "    </head>",
        "    <body>",
        "        <h1>Foo</h1>",
        "        <p>",
        "            Written on Saturday, July 10,",
        "            1999",
        "        </p>",
        "        <p>Categories: postin, foo</p>",
        "        <p>Tags: </p>",
        "",
        "        <p>This is the foo post.</p>",
        "    </body>",
        "</html>",
    ]
    expected_bar_post = [
        "<!DOCTYPE html>",
        "<html>",
        "    <head>",
        "        <title>Bar - the blog</title>",
        "    </head>",
        "    <body>",
        "        <h1>Bar</h1>",
        "        <p>",
        "            Written on Tuesday, August 3,",
        "            1999",
        "                (it was rainy)",
        "        </p>",
        "        <p>Categories: </p>",
        "        <p>Tags: bar</p>",
        "",
        "        <p>This is the bar post.</p>",
        "    </body>",
        "</html>",
    ]
    expected_baz_post = [
        "<!DOCTYPE html>",
        "<html>",
        "    <head>",
        "        <title>Baz - the blog</title>",
        "    </head>",
        "    <body>",
        "        <h1>Baz</h1>",
        "        <p>",
        "            Written on Sunday, January 2,",
        "            2000",
        "        </p>",
        "        <p>Categories: </p>",
        "        <p>Tags: </p>",
        "",
        "        <p>This is the baz post.</p>",
        "    </body>",
        "</html>",
    ]

    with open(
        os.path.join(generator.build_dir, "1999", "07", "10", "foo.html"), "r"
    ) as file:
        actual_foo_post = file.read()
    with open(
        os.path.join(generator.build_dir, "1999", "08", "03", "bar.html"), "r"
    ) as file:
        actual_bar_post = file.read()
    with open(
        os.path.join(generator.build_dir, "2000", "01", "02", "baz.html"), "r"
    ) as file:
        actual_baz_post = file.read()

    assert actual_foo_post == "\n".join(expected_foo_post)
    assert actual_bar_post == "\n".join(expected_bar_post)
    assert actual_baz_post == "\n".join(expected_baz_post)
