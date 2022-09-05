import os

import pytest

from flores.generator import Generator, Page


def test_complete_user_data_pages(test_data_dir: str) -> None:
    """Test the collection of user-defined data pages.

    We expect the user to be able to define custom "data pages", by creating page files
    under directories prefixed with an underscore (_).
    """
    generator = Generator(os.path.join(test_data_dir, "complete_pages"))
    pages = generator.collect_user_data_pages()

    expected_pages = [
        Page(
            template="template1",
            name="page1",
            content="This is the content of page 1.",
            # Ignoring the MyPy error here, as it is also ignored during page
            # construction in flores.generator.Generator.
            url=os.path.join("mypages", "page1"),  # type: ignore
            source_file=os.path.join(generator.project_dir, "_mypages", "page1.md"),
        ),
        Page(
            template="template2",
            name="page2",
            content="This is the content of page 2.",
            weather="sunny",
            # Ignoring the MyPy error here, as it is also ignored during page
            # construction in flores.generator.Generator.
            url=os.path.join("mypages", "page2"),  # type: ignore
            source_file=os.path.join(generator.project_dir, "_mypages", "page2.md"),
        ),
    ]

    assert list(pages.keys()) == ["mypages"]
    assert sorted(pages["mypages"], key=lambda p: p["name"]) == sorted(
        expected_pages, key=lambda p: p["name"]
    )


def test_empty_user_data_pages_dir(test_data_dir: str) -> None:
    """Test the collection of user-defined data pages when there are none.

    We expect the user-defined data page collection to return an empty list when no such
    pages are defined.
    """
    generator = Generator(os.path.join(test_data_dir, "empty_pages_dir"))
    pages = generator.collect_user_data_pages()

    assert list(pages.keys()) == ["empty_pages"]
    assert pages["empty_pages"] == []


def test_page_missing_template(test_data_dir: str) -> None:
    """Attempt to collect user-defined data pages when missing a template.

    We expect an error to be triggered when a user-defined data page is missing a
    template.
    """
    generator = Generator(os.path.join(test_data_dir, "missing_template"))
    page = os.path.join(
        generator.project_dir, "_missing_template_pages", "missing-template.md"
    )
    with pytest.raises(
        Exception,
        match=f"{page}: Missing 'template' key in frontmatter.",
    ):
        generator.collect_user_data_pages()


def test_page_wrong_type_for_template(test_data_dir: str) -> None:
    """Attempt to collect user-defined data pages with invalid 'template' type.

    We expect an error to be triggered when a user-defined data page's 'template' key
    is of the wrong type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_template"))
    page = os.path.join(
        generator.project_dir,
        "_wrong_type_for_template_pages",
        "wrong-type-for-template.md",
    )
    with pytest.raises(
        TypeError,
        match=f"{page}: Expected type 'str' but got 'int' for key 'template'.",
    ):
        generator.collect_user_data_pages()
