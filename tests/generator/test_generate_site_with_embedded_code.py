import os
import re

import pygments.styles
import pytest

from flores.exceptions import WrongTypeOrFormatError
from flores.generator import Generator


def test_generate_site_with_embedded_code_invalid_style(test_data_dir: str) -> None:
    """Attempt to generate a site with an invalid Pygments style.

    We expect an exception to be raised when the user defines an invalid Pygments style
    in the site config.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_style"))

    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{generator.config_file}: Expected type 'str' but got 'int' for key "
            "'pygments_style'."
        ),
    ):
        generator.build()


def test_generate_site_with_embedded_code_unknown_style(test_data_dir: str) -> None:
    """Attempt to generate a site with a Pygments style that does not exist.

    We expect an exception to be raised when the user defines a Pygments style that is
    not known by Pygments.
    """
    generator = Generator(os.path.join(test_data_dir, "unknown_style"))
    bogus_style = "yepthisistotallyapygmentsstylethatexistssure"

    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{generator.config_file}: Style '{bogus_style}' is not a valid Pygments "
            f"style ({', '.join(list(pygments.styles.get_all_styles()))})."
        ),
    ):
        generator.build()


def test_generate_site_with_embedded_code_no_style(test_data_dir: str) -> None:
    """Generate a test site with code snippets.

    We expect that by default no style will be applied to the code snippets.
    """
    generator = Generator(os.path.join(test_data_dir, "no_style"))
    generator.build()

    index_page_file = os.path.join(generator.build_dir, "index.html")
    # Only a single file should be generated.
    assert os.listdir(generator.build_dir) == ["index.html"]

    expected_index_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        "        <p>Some inline code: <code>x = lambda p: p * 3</code></p>",
        "<p>A code block:</p>",
        (
            '<div class="myclass codehilite"><table class="myclass codehilitetable">'
            '<tr><td class="linenos"><div class="linenodiv"><pre><span class="normal">'
            '1</span></pre></div></td><td class="code"><div><pre><span></span><code>'
            '<span class="nb">print</span><span class="p">(</span><span class="s2">'
            '&quot;Hello, World!&quot;</span><span class="p">)</span>'
        ),
        "</code></pre></div></td></tr></table></div>",
        "    </body>",
        "</html>",
    ]

    with open(index_page_file, "r") as file:
        actual_index_page = file.read().split("\n")

    assert actual_index_page == expected_index_page


def test_generate_site_with_embedded_code_custom_style(test_data_dir: str) -> None:
    """Generate a test site with code snippets and a custom highlighting style.

    We expect that specifying a Pygments style in the config will change the default
    highlighting style of the code snippets.
    """
    generator = Generator(os.path.join(test_data_dir, "custom_style"))
    generator.build()

    index_page_file = os.path.join(generator.build_dir, "index.html")
    # Only a single file should be generated.
    assert os.listdir(generator.build_dir) == ["index.html"]

    expected_index_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        "        <p>Some inline code: <code>x = lambda p: p * 3</code></p>",
        "<p>A code block:</p>",
        (
            '<div class="myclass codehilite" style="background: #f8f8f8">'
            '<table class="myclass codehilitetable"><tr><td class="linenos">'
            '<div class="linenodiv"><pre>'
            '<span style="color: inherit; background-color: transparent; '
            'padding-left: 5px; padding-right: 5px;">1</span></pre></div></td>'
            '<td class="code"><div><pre style="line-height: 125%;"><span></span><code>'
            '<span style="color: #008000">print</span>(<span style="color: #BA2121">'
            "&quot;Hello, World!&quot;</span>)"
        ),
        "</code></pre></div></td></tr></table></div>",
        "    </body>",
        "</html>",
    ]

    with open(index_page_file, "r") as file:
        actual_index_page = file.read().split("\n")

    assert actual_index_page == expected_index_page
