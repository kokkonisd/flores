import os
import re

import pytest
import sass

from flores.generator import Generator


def test_scss_compilation_error(test_data_dir: str) -> None:
    """Attempt to generate a site containing an error in a stylesheet.

    We expect an exception to be raised when invalid Sass/SCSS is present in a
    stylesheet.
    """
    generator = Generator(os.path.join(test_data_dir, "css_error"))
    with pytest.raises(
        sass.CompileError, match=re.escape("Invalid name in @mixin definition")
    ):
        generator.build()


def test_generate_site_with_scss(test_data_dir: str) -> None:
    """Generate a test site with Sass/SCSS/CSS.

    We expect the Sass/SCSS to be compiled to CSS, and the CSS itself to be left as-is.
    """
    generator = Generator(os.path.join(test_data_dir, "complete_css"))
    generator.build()

    expected_site_main = "a{color:#000102}a:hover{color:#030405}a:active{color:#060708}"
    expected_blog_main = "h1{color:#090a0b}"
    expected_blog_aux = "p {\n    font-style: italic;\n}"

    with open(os.path.join(generator.css_build_dir, "site", "main.css"), "r") as file:
        actual_site_main = file.read().strip()
    with open(os.path.join(generator.css_build_dir, "blog", "main.css"), "r") as file:
        actual_blog_main = file.read().strip()
    with open(os.path.join(generator.css_build_dir, "blog", "other.css"), "r") as file:
        actual_blog_aux = file.read().strip()

    assert actual_site_main == expected_site_main
    assert actual_blog_main == expected_blog_main
    assert actual_blog_aux == expected_blog_aux
