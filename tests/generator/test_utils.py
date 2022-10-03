import os
import re
from typing import Any

import pytest

from flores.exceptions import (
    FileOrDirNotFoundError,
    FloresError,
    FloresErrorCode,
    MissingElementError,
    YAMLError,
)
from flores.generator import Generator


def test_failing_with_general_error_code() -> None:
    """Attempt to trigger a failure with a general error code (1).

    We expect the generator to raise a FloresError exception in non-CLI mode.
    """
    generator = Generator(".")
    # Mypy does not track private attribute name mangling, so we're forced to go through
    # `getattr()`.
    fail = getattr(generator, "_Generator__fail")
    fail_message = "This should fail."

    with pytest.raises(FloresError, match=re.escape(fail_message)):
        fail(fail_message, exit_code=FloresErrorCode.GENERAL_ERROR)


def test_generator_with_invalid_dir() -> None:
    """Attempt to use an invalid directory as a project directory.

    We expect an error to be raised if the project directory is invalid.
    """
    bogus_dir = "this-is-totaly_not-a-legit-dir"
    with pytest.raises(
        FileOrDirNotFoundError,
        match=re.escape(f"Invalid project directory: '{bogus_dir}'."),
    ):
        Generator(bogus_dir)


def test_frontmatter_parsing(test_data_dir: str) -> None:
    """Test that the frontmatter files are parsed properly."""
    generator = Generator(test_data_dir)
    # Mypy does not track private attribute name mangling, so we're forced to go through
    # `getattr()`.
    parse = getattr(generator, "_Generator__parse_frontmatter_file")

    frontmatter_dir = os.path.join(test_data_dir, "frontmatter")
    empty_file = os.path.join(frontmatter_dir, "empty.md")
    ok_file = os.path.join(frontmatter_dir, "ok.md")
    ko_file = os.path.join(frontmatter_dir, "ko.md")
    hline_file = os.path.join(frontmatter_dir, "hline.md")

    # Frontmatter must always be there, even if it is empty.
    with pytest.raises(
        MissingElementError, match=re.escape(f"{empty_file}: Missing frontmatter.")
    ):
        parse(empty_file)

    ok_fm, ok_content = parse(ok_file)
    ok_fm_expected = {"hello": "world", "this": {"is": {"some": ["nested", "content"]}}}
    ok_content_expected = [
        "Hey! I can do _italics_ and **bold** and _**both**_!",
        "",
        "~~strikethrough~~",
        "",
        "# header!",
        "",
        "### another header!",
        "",
        "> I can also have a class",
        "{:.test-class}",
    ]

    assert ok_fm == ok_fm_expected
    assert ok_content == "\n".join(ok_content_expected)

    # Incorrect YAML in frontmatter should be detected.
    with pytest.raises(
        YAMLError,
        match=re.escape(f"{ko_file}: Error parsing frontmatter (invalid YAML)."),
    ):
        parse(ko_file)

    # An <hr> should not confuse the frontmatter parser.
    hline_fm, hline_content = parse(hline_file)
    hline_fm_expected: dict[str, Any] = {}
    hline_content_expected = [
        "---",
        "",
        "This is an example of an hline.",
        "",
        "---",
    ]

    assert hline_fm == hline_fm_expected
    assert hline_content == "\n".join(hline_content_expected)


def test_element_collection(test_data_dir: str) -> None:
    """Test that the element collection utility functions as expected."""
    generator = Generator(test_data_dir)
    # Mypy does not track private attribute name mangling, so we're forced to go through
    # `getattr()`.
    collect = getattr(generator, "_Generator__collect_elements_from_dir")

    # Check that we can't pass mutually exclusive arguments.
    with pytest.raises(
        AssertionError,
        match=re.escape(
            "The arguments 'files_only' and 'dirs_only' are mutually exclusive."
        ),
    ):
        collect(test_data_dir, files_only=True, dirs_only=True)

    # Check that it raises an error when provided with an invalid directory.
    fake_dir = os.path.join("yep", "this", "dir", "totally", "exists")
    with pytest.raises(
        FileOrDirNotFoundError, match=re.escape(f"No such directory: '{fake_dir}'.")
    ):
        collect(fake_dir)

    all_elements = collect(test_data_dir, recursive=True)
    all_elements_expected = [
        os.path.join(test_data_dir, "one.txt"),
        os.path.join(test_data_dir, "two"),
        os.path.join(test_data_dir, "two", "two.txt"),
        os.path.join(test_data_dir, "three"),
        os.path.join(test_data_dir, "three", "four"),
        os.path.join(test_data_dir, "three", "four", ".gitkeep"),
        os.path.join(test_data_dir, ".test"),
        os.path.join(test_data_dir, "frontmatter"),
        os.path.join(test_data_dir, "frontmatter", "empty.md"),
        os.path.join(test_data_dir, "frontmatter", "ok.md"),
        os.path.join(test_data_dir, "frontmatter", "ko.md"),
        os.path.join(test_data_dir, "frontmatter", "hline.md"),
    ]
    assert sorted(all_elements) == sorted(all_elements_expected)

    all_files = collect(test_data_dir, files_only=True, recursive=True)
    all_files_expected = [
        os.path.join(test_data_dir, "one.txt"),
        os.path.join(test_data_dir, "two", "two.txt"),
        os.path.join(test_data_dir, "three", "four", ".gitkeep"),
        os.path.join(test_data_dir, ".test"),
        os.path.join(test_data_dir, "frontmatter", "empty.md"),
        os.path.join(test_data_dir, "frontmatter", "ok.md"),
        os.path.join(test_data_dir, "frontmatter", "ko.md"),
        os.path.join(test_data_dir, "frontmatter", "hline.md"),
    ]
    assert sorted(all_files) == sorted(all_files_expected)

    all_dirs = collect(test_data_dir, dirs_only=True, recursive=True)
    all_dirs_expected = [
        os.path.join(test_data_dir, "two"),
        os.path.join(test_data_dir, "three"),
        os.path.join(test_data_dir, "three", "four"),
        os.path.join(test_data_dir, "frontmatter"),
    ]
    assert sorted(all_dirs) == sorted(all_dirs_expected)

    all_text_files = collect(
        test_data_dir, suffixes=[".txt"], files_only=True, recursive=True
    )
    all_text_files_expected = [
        os.path.join(test_data_dir, "one.txt"),
        os.path.join(test_data_dir, "two", "two.txt"),
    ]
    assert sorted(all_text_files) == sorted(all_text_files_expected)

    all_hidden_files = collect(
        test_data_dir, prefixes=["."], files_only=True, recursive=True
    )
    all_hidden_files_expected = [
        os.path.join(test_data_dir, ".test"),
        os.path.join(test_data_dir, "three", "four", ".gitkeep"),
    ]
    assert sorted(all_hidden_files) == sorted(all_hidden_files_expected)

    all_hidden_text_files = collect(
        test_data_dir,
        prefixes=["."],
        suffixes=[".txt"],
        files_only=True,
        recursive=True,
    )
    all_hidden_text_files_expected: list[str] = []
    assert sorted(all_hidden_text_files) == sorted(all_hidden_text_files_expected)

    root_elements = collect(test_data_dir)
    root_elements_expected = [
        os.path.join(test_data_dir, "one.txt"),
        os.path.join(test_data_dir, "two"),
        os.path.join(test_data_dir, "three"),
        os.path.join(test_data_dir, ".test"),
        os.path.join(test_data_dir, "frontmatter"),
    ]
    assert sorted(root_elements) == sorted(root_elements_expected)

    root_files = collect(test_data_dir, files_only=True)
    root_files_expected = [
        os.path.join(test_data_dir, "one.txt"),
        os.path.join(test_data_dir, ".test"),
    ]
    assert sorted(root_files) == sorted(root_files_expected)

    root_dirs = collect(test_data_dir, dirs_only=True)
    root_dirs_expected = [
        os.path.join(test_data_dir, "two"),
        os.path.join(test_data_dir, "three"),
        os.path.join(test_data_dir, "frontmatter"),
    ]
    assert sorted(root_dirs) == sorted(root_dirs_expected)

    root_text_files = collect(test_data_dir, suffixes=[".txt"], files_only=True)
    root_text_files_expected = [os.path.join(test_data_dir, "one.txt")]
    assert sorted(root_text_files) == sorted(root_text_files_expected)

    root_hidden_files = collect(test_data_dir, prefixes=["."], files_only=True)
    root_hidden_files_expected = [os.path.join(test_data_dir, ".test")]
    assert sorted(root_hidden_files) == sorted(root_hidden_files_expected)
