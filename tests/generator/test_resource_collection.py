import os

from flores.generator import Generator


def test_collect_basic_resources(test_data_dir: str) -> None:
    """Test the collection of the basic site resources.

    We expect all the basic resources to get picked up: pages, templates, posts...
    """
    generator = Generator(os.path.join(test_data_dir, "basic_resources"))

    expected_resources = [
        os.path.join(generator.stylesheets_dir, "main.scss"),
        os.path.join(generator.data_dir, "config.json"),
        os.path.join(generator.javascript_dir, "main.js"),
        os.path.join(generator.pages_dir, "index.md"),
        os.path.join(generator.posts_dir, "1970-01-01-hello.md"),
        os.path.join(generator.templates_dir, "main.html"),
        os.path.join(generator.templates_dir, "includes", "head.jinja"),
    ]

    assert sorted(generator.collect_resources()) == sorted(expected_resources)


def test_collect_resources_with_assets(test_data_dir: str) -> None:
    """Test the collection of site resources (including assets).

    We expect any assets that are present in the project dir to get picked up as well.
    """
    generator = Generator(os.path.join(test_data_dir, "with_assets"))

    expected_resources = [
        os.path.join(generator.assets_dir, "txt"),
        os.path.join(generator.assets_dir, "txt", "readme.txt"),
    ]

    assert sorted(generator.collect_resources()) == sorted(expected_resources)


def test_collect_resources_with_user_data_dirs(test_data_dir: str) -> None:
    """Test the collection of site resources (including user data dirs).

    We expect any user data dires that are present in the project dir to get picked up
    as well.
    """
    generator = Generator(os.path.join(test_data_dir, "with_user_data_dirs"))

    expected_resources = [
        os.path.join(generator.project_dir, "_mypages", "my-first-page.md"),
    ]

    assert sorted(generator.collect_resources()) == sorted(expected_resources)


def test_collect_resources_with_drafts(test_data_dir: str) -> None:
    """Test the collection of site resources (including drafts).

    We expect any drafts that are present in the project dir to get picked up as well,
    if the corresponding flag is activated.
    """
    generator = Generator(os.path.join(test_data_dir, "with_drafts"))

    expected_resources = [
        os.path.join(generator.drafts_dir, "1970-01-01-hello.md"),
    ]

    assert sorted(generator.collect_resources(include_drafts=True)) == sorted(
        expected_resources
    )
