import os
import re

import pytest

from flores.exceptions import ImageError, MissingElementError, WrongTypeOrFormatError
from flores.generator import Generator


def test_no_optimization(test_data_dir: str) -> None:
    """Build images without any optimization.

    We expect pure copies of the original images to be used when no optimization is
    specified.
    """
    generator = Generator(os.path.join(test_data_dir, "no_optimization"))
    generator.build()

    expected_elements = [
        generator.assets_build_dir,
        os.path.join(generator.assets_build_dir, "vases.png"),
        os.path.join(generator.assets_build_dir, "sea.jpg"),
    ]

    all_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            all_elements.append(os.path.join(dirpath, element))

    assert sorted(all_elements) == sorted(expected_elements)
    # We also expect the sizes to be the same since we just copied the files over.
    assert os.path.getsize(
        os.path.join(generator.assets_dir, "vases.png")
    ) == os.path.getsize(
        os.path.join(generator.assets_build_dir, "vases.png")
    ), "Wrong size for vases.png."
    assert os.path.getsize(
        os.path.join(generator.assets_dir, "sea.jpg")
    ) == os.path.getsize(
        os.path.join(generator.assets_build_dir, "sea.jpg")
    ), "Wrong size for sea.jpg."


def test_basic_optimization(test_data_dir: str) -> None:
    """Build images with basic optimization.

    When basic optimization is specified, we expect the generated images to be smaller
    in size than the originals, but still retain the same names.
    """
    generator = Generator(os.path.join(test_data_dir, "basic_optimization"))
    generator.build()

    expected_elements = [
        generator.assets_build_dir,
        os.path.join(generator.assets_build_dir, "vases.png"),
        os.path.join(generator.assets_build_dir, "sea.jpg"),
    ]

    all_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            all_elements.append(os.path.join(dirpath, element))

    assert sorted(all_elements) == sorted(expected_elements)
    # We also expect the sizes to be a little smaller since we optimized the images.
    assert os.path.getsize(
        os.path.join(generator.assets_dir, "vases.png")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "vases.png")
    ), "vases.png is not smaller."
    assert os.path.getsize(
        os.path.join(generator.assets_dir, "sea.jpg")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "sea.jpg")
    ), "sea.jpg is not smaller."


def test_disable_processing(test_data_dir: str) -> None:
    """Attempt to build images while deactivating image builds.

    We expect to simply have direct copies of the original images if the image builds
    are deactivated (regardless of the configuration of the optimization).
    """
    generator = Generator(os.path.join(test_data_dir, "basic_optimization"))
    generator.build(disable_image_build=True)

    expected_elements = [generator.assets_build_dir]

    all_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            all_elements.append(os.path.join(dirpath, element))

    assert sorted(all_elements) == sorted(expected_elements)


def test_full_optimization(test_data_dir: str) -> None:
    """Build images with full optimization.

    We expect to be able to select not only the optimization (True/False) but also the
    size and the suffixes of the generated images.
    """
    generator = Generator(os.path.join(test_data_dir, "full_optimization"))
    generator.build()

    expected_elements = [
        generator.assets_build_dir,
        os.path.join(generator.assets_build_dir, "vases-small.png"),
        os.path.join(generator.assets_build_dir, "vases-medium.png"),
        os.path.join(generator.assets_build_dir, "vases-large.png"),
        os.path.join(generator.assets_build_dir, "sea-small.jpg"),
        os.path.join(generator.assets_build_dir, "sea-medium.jpg"),
        os.path.join(generator.assets_build_dir, "sea-large.jpg"),
    ]

    all_elements = []
    for dirpath, dirnames, filenames in os.walk(generator.build_dir):
        for element in dirnames + filenames:
            all_elements.append(os.path.join(dirpath, element))

    assert sorted(all_elements) == sorted(expected_elements)

    # The *-large images are the same dimensions as the originals, but they should still
    # be smaller in size because they're optimized.
    assert os.path.getsize(
        os.path.join(generator.assets_dir, "vases.png")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "vases-large.png")
    ), "vases-large.png is not smaller than the original."
    assert os.path.getsize(
        os.path.join(generator.assets_dir, "sea.jpg")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "sea-large.jpg")
    ), "sea-large.jpg is not smaller than the original."

    # The *-medium images should be smaller than the *-large ones.
    assert os.path.getsize(
        os.path.join(generator.assets_build_dir, "vases-large.png")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "vases-medium.png")
    ), "vases-medium.png is not smaller than vases-large.png."
    assert os.path.getsize(
        os.path.join(generator.assets_build_dir, "sea-large.jpg")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "sea-medium.jpg")
    ), "sea-medium.jpg is not smaller than sea-large.jpg."

    # The *-small images should be smaller than the *-medium ones.
    assert os.path.getsize(
        os.path.join(generator.assets_build_dir, "vases-medium.png")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "vases-small.png")
    ), "vases-small.png is not smaller than vases-medium.png."
    assert os.path.getsize(
        os.path.join(generator.assets_build_dir, "sea-medium.jpg")
    ) > os.path.getsize(
        os.path.join(generator.assets_build_dir, "sea-small.jpg")
    ), "sea-small.jpg is not smaller than sea-medium.jpg."


def test_optimize_invalid_image(test_data_dir: str) -> None:
    """Attempt to build invalid images.

    We expect an error to be raised when invalid images are provided for optimization.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_image"))
    invalid_image = os.path.join(generator.assets_dir, "notanimage.jpg")

    with pytest.raises(
        ImageError,
        match=re.escape(
            f"{invalid_image}: Cannot identify image file '{invalid_image}'."
        ),
    ):
        generator.build()


def test_invalid_config_extra_keys(test_data_dir: str) -> None:
    """Attempt to build images with extra config keys.

    We expect an error to be raised if unexpected (extra) keys are found in the config.
    """
    generator = Generator(os.path.join(test_data_dir, "invalid_config_extra_keys"))

    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{generator.config_file}: Unexpected keys 'foo, bar' in element "
            "'{'size': 0.45, 'suffix': '-a', 'optimize': False, 'foo': 1, 'bar': 2}' "
            "in key 'images'."
        ),
    ):
        generator.build()


def test_invalid_config_images_key_wrong_type(test_data_dir: str) -> None:
    """Attempt to build images with the wrong type for 'images'.

    We expect an error to be raised when the 'images' key in the config is of the wrong
    type.
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_images_key_wrong_type")
    )

    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{generator.config_file}: Expected type 'list' but got 'dict' for key "
            "'images'."
        ),
    ):
        generator.build()


def test_invalid_config_optimize_key_missing(test_data_dir: str) -> None:
    """Attempt to build images while missing the 'optimize' key.

    We expect an error to be raised when the 'optimize' key in the config is missing.
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_optimize_key_missing")
    )

    with pytest.raises(
        MissingElementError,
        match=(
            f"{generator.config_file}: Missing key 'optimize' in element "
            "'{'size': 1, 'suffix': '-raw'}' in key 'images'."
        ),
    ):
        generator.build()


def test_invalid_config_optimize_key_wrong_type(test_data_dir: str) -> None:
    """Attempt to build images with the wrong type for 'optimize'.

    We expect an error to be raised when the 'optimize' key in the config is of the
    wrong type.
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_optimize_key_wrong_type")
    )

    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{generator.config_file}: Expected type 'bool' but got 'str' for key "
            "'optimize' in element '{'size': 1, 'suffix': '', 'optimize': 'yes'}' in "
            "key 'images'."
        ),
    ):
        generator.build()


def test_invalid_config_size_key_missing(test_data_dir: str) -> None:
    """Attempt to build images while missing the 'size' key.

    We expect an error to be raised when the 'size' key in the config is missing.
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_size_key_missing")
    )

    with pytest.raises(
        MissingElementError,
        match=(
            f"{generator.config_file}: Missing key 'size' in element "
            "'{'suffix': '', 'optimize': True}' in key 'images'."
        ),
    ):
        generator.build()


def test_invalid_config_size_key_out_of_bounds(test_data_dir: str) -> None:
    """Attempt to build images while having an out-of-bounds size.

    We expect an error to be raised when the size specified is not in (0, 1].
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_size_key_out_of_bounds")
    )

    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{generator.config_file}: Expected key 'size' to be in range (0, 1] but "
            "got '100' in element '{'size': 100, 'suffix': '', 'optimize': True}' in "
            "key 'images'."
        ),
    ):
        generator.build()


def test_invalid_config_size_key_wrong_type(test_data_dir: str) -> None:
    """Attempt to build images with the wrong type for 'size'.

    We expect an error to be raised when the 'size' key in the config is of the wrong
    type.
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_size_key_wrong_type")
    )

    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{generator.config_file}: Expected type 'float' or 'int' but got 'str' "
            "for key 'size' in element "
            "'{'size': '100%', 'suffix': '', 'optimize': True}' in key 'images'."
        ),
    ):
        generator.build()


def test_invalid_config_suffix_key_missing(test_data_dir: str) -> None:
    """Attempt to build images while missing the 'suffix' key.

    We expect an error to be raised when the 'suffix' key in the config is missing.
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_suffix_key_missing")
    )

    with pytest.raises(
        MissingElementError,
        match=(
            f"{generator.config_file}: Missing key 'suffix' in element "
            "'{'size': 1, 'optimize': False}' in key 'images'."
        ),
    ):
        generator.build()


def test_invalid_config_suffix_key_wrong_type(test_data_dir: str) -> None:
    """Attempt to build images with the wrong type for 'suffix'.

    We expect an error to be raised when the 'suffix' key in the config is of the wrong
    type.
    """
    generator = Generator(
        os.path.join(test_data_dir, "invalid_config_suffix_key_wrong_type")
    )

    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{generator.config_file}: Expected type 'str' but got 'int' for key "
            "'suffix' in element '{'size': 1, 'suffix': 0, 'optimize': False}' in "
            "key 'images'."
        ),
    ):
        generator.build()
