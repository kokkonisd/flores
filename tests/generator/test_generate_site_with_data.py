import os
import re

import pytest

from flores.exceptions import JSONError
from flores.generator import Generator


def test_json_error_in_config_data(test_data_dir: str) -> None:
    """Attempt to generate a site with a config data file containing invalid JSON.

    We expect an exception to be raised when invalid JSON is present in config file.
    """
    generator = Generator(os.path.join(test_data_dir, "config_json_error"))
    with pytest.raises(
        JSONError,
        match=re.escape(
            f"{generator.config_file}: Expecting property name enclosed in double "
            "quotes: line 2 column 5 (char 6)."
        ),
    ):
        generator.build()


def test_json_error_in_data(test_data_dir: str) -> None:
    """Attempt to generate a site with data files containing invalid JSON.

    We expect an exception to be raised when invalid JSON is present in the data files.
    """
    generator = Generator(os.path.join(test_data_dir, "json_error"))
    with pytest.raises(
        JSONError,
        match=re.escape(
            f"{os.path.join(generator.data_dir, 'problematic.json')}: Invalid control "
            "character at: line 2 column 10 (char 11)."
        ),
    ):
        generator.build()


def test_generate_site_with_complete_data(test_data_dir: str) -> None:
    """Generate a test site with data.

    We expect the data to be loaded and to be usable in the templates and pages.
    Furthermore, the "config.json" data should be considered "special" and parsed in a
    different way.
    """
    generator = Generator(os.path.join(test_data_dir, "complete_data"))
    generator.build()

    # The config.json file is special and should be parsed as the site configuration.
    assert generator.config == {
        "title": "My awesome site!",
        "name": "John Doe",
        "email": "john@doe.com",
    }

    index_page_file = os.path.join(generator.build_dir, "index.html")
    # Only a single file should be generated.
    assert os.listdir(generator.build_dir) == ["index.html"]

    expected_index_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <head>",
        "        <title> My awesome site! </title>",
        "    </head>",
        "    <body>",
        "        <h1>John Doe (john@doe.com)</h1>",
        "<table>",
        "<thead>",
        "<tr>",
        "<th>Company</th>",
        "<th>Year range</th>",
        "</tr>",
        "</thead>",
        "<tbody>",
        "<tr>",
        "<td>Foo Corp.</td>",
        "<td>1982-1987</td>",
        "</tr>",
        "<tr>",
        "<td>Bar Unltd.</td>",
        "<td>1987-1989</td>",
        "</tr>",
        "<tr>",
        "<td>Boo Bar Baz Inc.</td>",
        "<td>1989-today</td>",
        "</tr>",
        "</tbody>",
        "</table>",
        "    </body>",
        "</html>",
    ]

    with open(index_page_file, "r") as file:
        actual_index_page = file.read().split("\n")

    assert actual_index_page == expected_index_page
