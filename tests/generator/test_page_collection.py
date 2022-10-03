import os
import re

import pytest

from flores.exceptions import MissingElementError, WrongTypeOrFormatError
from flores.generator import Generator, Page


def test_complete_pages(test_data_dir: str) -> None:
    """Collect a complete set of pages."""
    generator = Generator(os.path.join(test_data_dir, "complete_pages"))
    pages = generator.collect_pages()

    expected_pages = [
        Page(
            template="template1",
            name="page1",
            content="This is the content of page 1.",
            source_file=os.path.join(generator.pages_dir, "page1.md"),
        ),
        Page(
            template="template2",
            name="page2",
            content="This is the content of page 2.",
            source_file=os.path.join(generator.pages_dir, "page2.md"),
            # Ignoring the mypy error here, as it is also ignored during page
            # construction in flores.generator.Generator.
            weather="sunny",  # type: ignore
        ),
    ]

    assert sorted(pages, key=lambda p: p["name"]) == sorted(
        expected_pages, key=lambda p: p["name"]
    )


def test_empty_pages_dir(test_data_dir: str) -> None:
    """Collect pages from a site that defines none.

    When no pages are defined, we expect the page collection to return an empty list.
    """
    generator = Generator(os.path.join(test_data_dir, "empty_pages_dir"))
    pages = generator.collect_pages()

    assert pages == []


def test_page_missing_template(test_data_dir: str) -> None:
    """Attempt to collect pages when a template is missing.

    We expect an error to be raised if a page does not define a template to be used.
    """
    generator = Generator(os.path.join(test_data_dir, "missing_template"))
    with pytest.raises(
        MissingElementError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'missing-template.md')}: Missing "
            "'template' key in frontmatter."
        ),
    ):
        generator.collect_pages()


def test_page_wrong_type_for_template(test_data_dir: str) -> None:
    """Attempt to collect pages when the 'template' key has the wrong type.

    We expect an error to be raised if a page defines a 'template' key with the wrong
    type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_template"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.pages_dir, 'wrong-type-for-template.md')}: "
            "Expected type 'str' but got 'int' for key 'template'."
        ),
    ):
        generator.collect_pages()
