import os

from flores.generator import Generator


def test_generate_site_with_js(test_data_dir: str) -> None:
    """Generate a test site with JavaScript assets.

    We expect that the JavaScript assets (under `_js/`) will be transferred into the
    build directory while preserving their structure, and without any modifications.
    """
    generator = Generator(test_data_dir)
    generator.build()

    index_page_file = os.path.join(generator.build_dir, "index.html")
    expected_elements = [
        index_page_file,
        os.path.join(generator.build_dir, "js"),
        os.path.join(generator.build_dir, "js", "site"),
        os.path.join(generator.build_dir, "js", "site", "main"),
        os.path.join(generator.build_dir, "js", "site", "other"),
        os.path.join(generator.build_dir, "js", "site", "main", "main.js"),
        os.path.join(generator.build_dir, "js", "site", "other", "stuff.js"),
        os.path.join(generator.build_dir, "js", "blog"),
        os.path.join(generator.build_dir, "js", "blog", "tracker.js"),
    ]

    actual_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            actual_elements.append(os.path.join(dirpath, element))

    assert sorted(actual_elements) == sorted(expected_elements)

    expected_index_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <body>",
        '            <script src="js/site/main/main.js"></script>',
        '            <script src="js/site/aux/stuff.js"></script>',
        '            <script src="js/blog/tracker.js"></script>',
        "    </body>",
        "</html>",
    ]

    with open(index_page_file, "r") as file:
        actual_index_page = file.read().split("\n")

    assert actual_index_page == expected_index_page
