import os

from flores.generator import Generator


def test_generate_empty_site(test_data_dir: str) -> None:
    """Generate a site with no input data whatsoever."""
    generator = Generator(test_data_dir)
    generator.build()

    assert os.path.isdir(generator.build_dir)
    assert os.listdir(generator.build_dir) == []
