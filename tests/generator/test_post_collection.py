import os
import re
from datetime import datetime

import pytest

from flores.exceptions import MissingElementError, WrongTypeOrFormatError
from flores.generator import Generator, Post, PostDateInfo


def test_complete_posts(test_data_dir: str) -> None:
    """Test the collection of posts for a site."""
    generator = Generator(os.path.join(test_data_dir, "complete_posts"))
    posts = generator.collect_posts(include_drafts=False)
    posts_and_drafts = generator.collect_posts(include_drafts=True)

    expected_posts = [
        Post(
            name="post1",
            source_file=os.path.join(generator.posts_dir, "2022-09-04-post1.md"),
            base_address=os.path.join("2022", "09", "04"),
            url=os.path.join("/", "2022", "09", "04", "post1"),
            template="template1",
            title="Post 1",
            content="This is the first post.",
            is_draft=False,
            date=PostDateInfo(
                year="2022",
                month="9",
                month_padded="09",
                month_name="September",
                month_name_short="Sep",
                day="4",
                day_padded="04",
                day_name="Sunday",
                day_name_short="Sun",
                timestamp=datetime.strptime(
                    "2022-09-04 12:13:14 +0100", "%Y-%m-%d %H:%M:%S %z"
                ).timestamp(),
            ),
            categories=["cat1", "cat2"],
            tags=["tag1", "tag2"],
        ),
        Post(
            name="post2",
            source_file=os.path.join(generator.posts_dir, "2022-09-05-post2.md"),
            base_address=os.path.join("2022", "09", "05"),
            url=os.path.join("/", "2022", "09", "05", "post2"),
            template="template2",
            title="Post 2",
            content="This is the second post.",
            is_draft=False,
            date=PostDateInfo(
                year="2022",
                month="9",
                month_padded="09",
                month_name="September",
                month_name_short="Sep",
                day="5",
                day_padded="05",
                day_name="Monday",
                day_name_short="Mon",
                timestamp=datetime.strptime(
                    "2022-09-05 15:16:17 +0300", "%Y-%m-%d %H:%M:%S %z"
                ).timestamp(),
            ),
            categories=["cat3", "cat4"],
            tags=["tag3", "tag4"],
            # Ignoring the MyPy error here, as it is also ignored during page
            # construction in flores.generator.Generator.
            quote="Woohoo!",  # type: ignore
        ),
    ]

    expected_drafts = [
        Post(
            name="draft1",
            source_file=os.path.join(generator.drafts_dir, "2022-09-06-draft1.md"),
            base_address=os.path.join("2022", "09", "06"),
            url=os.path.join("/", "2022", "09", "06", "draft1"),
            template="template3",
            title="Draft 1",
            content="This is the first draft.",
            is_draft=True,
            date=PostDateInfo(
                year="2022",
                month="9",
                month_padded="09",
                month_name="September",
                month_name_short="Sep",
                day="6",
                day_padded="06",
                day_name="Tuesday",
                day_name_short="Tue",
                timestamp=datetime.strptime(
                    "2022-09-06 18:19:20 +0200", "%Y-%m-%d %H:%M:%S %z"
                ).timestamp(),
            ),
            categories=[],
            tags=[],
            # Ignoring the MyPy error here, as it is also ignored during page
            # construction in flores.generator.Generator.
            foo="bar",  # type: ignore
        )
    ]

    assert sorted(posts, key=lambda p: p["date"]["timestamp"]) == sorted(
        expected_posts, key=lambda p: p["date"]["timestamp"]
    )
    assert sorted(posts_and_drafts, key=lambda p: p["date"]["timestamp"]) == sorted(
        expected_posts + expected_drafts, key=lambda p: p["date"]["timestamp"]
    )


def test_post_incorrect_form(test_data_dir: str) -> None:
    """Attempt to collect posts that are formatted incorrectly.

    We expect an error to be raised when the post files themseleves are not formatted
    correctly.
    """
    generator = Generator(os.path.join(test_data_dir, "incorrect_form"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '20220904-post1.md')}: Post files "
            "should be of the form 'YYYY-MM-DD-post-title-here'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_missing_template(test_data_dir: str) -> None:
    """Attempt to collect posts that are missing a template.

    We expect an error to be raised when a post is missing a template.
    """
    generator = Generator(os.path.join(test_data_dir, "missing_template"))
    with pytest.raises(
        MissingElementError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Missing "
            "'template' key in frontmatter."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_missing_title(test_data_dir: str) -> None:
    """Attempt to collect posts that are missing a title.

    We expect an error to be raised when a post is missing a title.
    """
    generator = Generator(os.path.join(test_data_dir, "missing_title"))
    with pytest.raises(
        MissingElementError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Missing "
            "'title' key in frontmatter."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_type_for_template(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong type for 'template'.

    We expect an error to be raised when a post's 'template' key is of the wrong type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_template"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Expected "
            "type 'str' but got 'list' for key 'template'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_type_for_title(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong type for 'title'.

    We expect an error to be raised when a post's 'title' key is of the wrong type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_title"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Expected "
            "type 'str' but got 'dict' for key 'title'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_type_for_categories(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong type for 'categories'.

    We expect an error to be raised when a post's 'categories' key is of the wrong type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_categories"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Expected "
            "type 'list' but got 'int' for key 'categories'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_type_for_category_element(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong type for a category element.

    We expect an error to be raised when a post's 'categories' key contains an element
    that is of the wrong type.
    """
    generator = Generator(
        os.path.join(test_data_dir, "wrong_type_for_category_element")
    )
    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Expected "
            "type 'str' but got 'list' for category '['boo']'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_type_for_tags(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong type for 'tags'.

    We expect an error to be raised when a post's 'tags' key is of the wrong type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_tags"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Expected "
            "type 'list' but got 'int' for key 'tags'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_type_for_tag_element(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong type for a tag element.

    We expect an error to be raised when a post's 'tags' key contains an element that is
    of the wrong type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_tag_element"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Expected "
            "type 'str' but got 'dict' for tag '{'foo': 'bar'}'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_type_for_date_string(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong type for 'date'.

    We expect an error to be raised when a post's 'date' key is of the wrong type.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_type_for_date_string"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Expected "
            "type 'str' but got 'int' for key 'date'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_wrong_format_for_date_string(test_data_dir: str) -> None:
    """Attempt to collect posts that have a wrong format for 'date'.

    We expect an error to be raised when a post's 'date' key is of the wrong format.
    """
    generator = Generator(os.path.join(test_data_dir, "wrong_format_for_date_string"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=re.escape(
            f"{os.path.join(generator.posts_dir, '2022-09-04-post1.md')}: Time data "
            "'2022/09/04 10:11:12 +0100' does not match format '%y-%m-%d %h:%m:%s %z'."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_date_mismatch_year(test_data_dir: str) -> None:
    """Attempt to collect a post with a date mismatch on the year.

    We expect an error to be reported when the year on the post filename and the year
    defined in the post's frontmatter differ.
    """
    generator = Generator(os.path.join(test_data_dir, "date_mismatch_year"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2009-10-11-post.md')}: "
            "Year mismatch; '2009' in the filename, but '2010' in the file."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_date_mismatch_month(test_data_dir: str) -> None:
    """Attempt to collect a post with a date mismatch on the month.

    We expect an error to be reported when the month on the post filename and the month
    defined in the post's frontmatter differ.
    """
    generator = Generator(os.path.join(test_data_dir, "date_mismatch_month"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2009-10-11-post.md')}: "
            "Month mismatch; '10' in the filename, but '01' in the file."
        ),
    ):
        generator.collect_posts(include_drafts=False)


def test_post_date_mismatch_day(test_data_dir: str) -> None:
    """Attempt to collect a post with a date mismatch on the day.

    We expect an error to be reported when the day on the post filename and the day
    defined in the post's frontmatter differ.
    """
    generator = Generator(os.path.join(test_data_dir, "date_mismatch_day"))
    with pytest.raises(
        WrongTypeOrFormatError,
        match=(
            f"{os.path.join(generator.posts_dir, '2009-10-11-post.md')}: "
            "Day mismatch; '11' in the filename, but '02' in the file."
        ),
    ):
        generator.collect_posts(include_drafts=False)
