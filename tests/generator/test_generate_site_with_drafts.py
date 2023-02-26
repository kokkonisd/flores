import os

from flores.generator import Generator


def test_generate_site_with_drafts(test_data_dir: str) -> None:
    """Generate a test site with drafts of posts.

    We expect the drafts to only be generated if the correct flag is passed to the
    generator.
    """
    generator = Generator(test_data_dir)
    generator.build()

    # Without including drafts, the generated site should be empty.
    assert os.listdir(generator.build_dir) == []

    # Rebuild, including drafts this time.
    generator.build(include_drafts=True)

    draft_page_file = os.path.join(
        generator.build_dir, "1999", "01", "02", "secret-post.html"
    )
    draft_page_file_with_slash = os.path.join(
        generator.build_dir, "1999", "01", "02", "secret-post", "index.html"
    )

    expected_site_elements = [
        os.path.join(generator.build_dir, "1999"),
        os.path.join(generator.build_dir, "1999", "01"),
        os.path.join(generator.build_dir, "1999", "01", "02"),
        draft_page_file,
        os.path.join(generator.build_dir, "1999", "01", "02", "secret-post"),
        draft_page_file_with_slash,
    ]

    actual_site_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            actual_site_elements.append(os.path.join(dirpath, element))

    assert sorted(actual_site_elements) == sorted(expected_site_elements)

    expected_draft_page = [
        "<!DOCTYPE html>",
        "<html>",
        "    <head>",
        "        <title> Site with drafts </title>",
        "    </head>",
        "    <body>",
        "        <h2> The secret post </h2>",
        "",
        "        <hr>",
        "",
        "        <p>Name: name</p>",
        "<p>Email: email</p>",
        "<p>Secret: abcdefg</p>",
        "",
        "        <h3> Quote of the day </h3>",
        "        <blockquote> Wake up and do stuff </blockquote>",
        "    </body>",
        "</html>",
    ]

    with open(draft_page_file, "r") as file:
        actual_draft_page = file.read().split("\n")
    with open(draft_page_file_with_slash, "r") as file:
        actual_draft_page_with_slash = file.read().split("\n")

    assert actual_draft_page == expected_draft_page
    assert actual_draft_page_with_slash == expected_draft_page
