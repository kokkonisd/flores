import os

from flores.generator import Generator


def test_generate_site_with_assets(test_data_dir: str) -> None:
    """Generate a test site with assets.

    We expect the assets to be directly copied to the build directory.
    By default, we do not expect any image optimization to happen.
    """
    generator = Generator(test_data_dir)

    generator.build()

    expected_assets = [
        "assets",
        os.path.join("assets", "images"),
        os.path.join("assets", "images", "blog"),
        os.path.join("assets", "images", "blog", "coffee.jpg"),
        os.path.join("assets", "images", "blog", "village.jpg"),
        os.path.join("assets", "images", "site"),
        os.path.join("assets", "images", "site", "sea.jpg"),
        os.path.join("assets", "images", "site", "vases.png"),
        os.path.join("assets", "txt"),
        os.path.join("assets", "txt", "hello.txt"),
    ]

    actual_assets = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            actual_assets.append(os.path.join(dirpath, element))

    assert sorted(actual_assets) == sorted(
        [os.path.join(generator.build_dir, asset) for asset in expected_assets]
    ), actual_assets
