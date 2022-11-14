"""The Flores static site generator.

This site generator is meant to be used either in CLI mode (via flores.__main__:main)
or in 'library' mode, i.e. programmatically.
"""

import json
import logging
import os
import re
import shutil
import sys
import time
from datetime import datetime
from typing import Any, Optional, TypedDict, Union

import jinja2
import markdown
import pygments
import sass
import yaml
from PIL import Image

from flores.exceptions import ERROR_CODE_EXCEPTION_MAP, FloresError, FloresErrorCode
from flores.logger import FloresLogger


class Page(TypedDict):
    """Describe a page of the site.

    :ivar template: the Jinja (HTML) template to use for the page.
    :ivar content: the actual content of the page.
    :ivar name: the name of the page (based on the filename).
    :ivar source_file: the path to the source file of the page.
    """

    template: str
    content: str
    name: str
    source_file: str


class PostDateInfo(TypedDict):
    """Describe information regarding the date of a given post.

    This interface is exposed to the author of the posts, so that they can add the date
    information of the post in the page, should they wish to.

    :ivar year: the full year the post was written on (e.g. 2022).
    :ivar month: the number of the month the post was written on, without padding (e.g.
        3).
    :ivar month_padded: the padded version of `month` (e.g. 03).
    :ivar month_name: the full name of the month the post was written on (e.g. March).
    :ivar month_name_short: the shortened version of `month_name` (e.g. Mar).
    :ivar day: the number of the day the post was written on, without padding (e.g. 4).
    :ivar day_padded: the padded version of `day` (e.g. 04).
    :ivar day_name: the full name of the day the post was written on (e.g. Friday).
    :ivar day_name_short: the shortened version of `day_name` (e.g. Fri).
    :ivar timestamp: the timestamp of the precise date and time the post was written on.
    """

    year: str
    month: str
    month_padded: str
    month_name: str
    month_name_short: str
    day: str
    day_padded: str
    day_name: str
    day_name_short: str
    timestamp: float


class Post(TypedDict):
    """Describe a post page.

    Post pages are unique, in the sense that their relative position on the site is
    determined by their post date. They also have a title (which pages do not
    necessarily have), and they can have associated categories and tags.

    :ivar template: the Jinja (HTML) template to use for the post.
    :ivar title: the title of the post.
    :ivar date: the date the post was written on (see
        :class:`flores.generator.PostDateInfo`).
    :ivar categories: categories associated with the post.
    :ivar tags: tags associated with the post.
    :ivar content: the actual content of the post.
    :ivar name: the name of the post (based on the filename).
    :ivar source_file: the path to the source file of the post.
    :ivar base_address: the base address of the post, meaning the path of the directory
        in which the post will be placed in the final build (e.g. for
        '1970-01-01-post.md' it will be '1970/01/01').
    :ivar url: the final URL of the post (relative to the site's root).
    :ivar is_draft: True if the post is a draft, False otherwise.
    """

    template: str
    title: str
    date: PostDateInfo
    categories: list[str]
    tags: list[str]
    content: str
    name: str
    source_file: str
    base_address: str
    url: str
    is_draft: bool


class ImageConfig(TypedDict):
    """Describe an image configuration.

    Image configurations are used to determine the images that will be generated for
    the site.

    :ivar size: the size of the image, expressed as a fraction of the original image's
        size in (0, 1].
    :ivar suffix: the suffix to append to the image file.
    :ivar optimize: if True, optimize the image.
    """

    size: Union[float, int]
    suffix: str
    optimize: bool


# Ensure that a single logger is used for all generators.
GENERATOR_LOGGER = FloresLogger("generator")


class Generator:
    """Implement the Flores static site generator.

    :cvar FRONTMATTER_REGEX: the regex used to detect the frontmatter region of the
        Markdown-frontmatter files.
    :cvar MD_EXTENSIONS: the list of extensions used when parsing Markdown.
    :cvar DEFAULT_CONFIG: the default configuration of the site generator.
    :cvar IMAGE_EXTENSIONS: the image extensions recognized by Flores.
    :cvar INIT_CONFIG_FILE: the default config file that gets generated when
        initializing a new site.
    :cvar INIT_TEMPLATE_FILE: the default template file that gets generated when
        initializing a new site.
    :cvar INIT_PAGE_FILE: the default page file that gets generated when
        initializing a new site.
    """

    FRONTMATTER_REGEX = r"---\n(((?!---)[\s\S])*)\n?---"

    MD_EXTENSIONS = [
        "pymdownx.tilde",
        "pymdownx.emoji",
        "pymdownx.extra",
        "codehilite",
        "fenced_code",
    ]

    DEFAULT_CONFIG = {
        "pygments_style": None,
        "images": [{"size": 1, "suffix": "", "optimize": False}],
    }

    IMAGE_EXTENSIONS = [".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG"]

    INIT_CONFIG_FILE = "\n".join(
        [
            "{",
            '    "title": "My awesome site"',
            "}",
        ]
    )

    INIT_TEMPLATE_FILE = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> {{ site.config.title }} </title>",
            "    </head>",
            "    <body>",
            "        {{ page.content }}",
            "    </body>",
            "</html>",
        ]
    )

    INIT_PAGE_FILE = "\n".join(
        [
            "---",
            "template: main",
            "---",
            "This site is built with Flores!",
        ]
    )

    def __init__(
        self,
        project_dir: str,
        log_level: Any = logging.DEBUG,
        log_file: Optional[str] = None,
        no_color: bool = False,
        cli_mode: bool = False,
    ) -> None:
        """Initialize the site generator.

        :param project_dir: the root directory of the project, containing all the
            necessary resources for the site.
        :param log_level: the level of logging
            (i.e. logging.DEBUG|INFO|WARNING|ERROR|CRITICAL).
        :param log_file: the file to write the logs to; if None, write logs to stderr.
        :param no_color: if True, disable colors when logging.
        :param cli_mode: if True, run in CLI mode (this mostly affects the handling of
            critical errors).
        """
        self.__log = GENERATOR_LOGGER
        self.__log.set_level(log_level)
        self.__log.set_log_file(log_file)
        self.__log.set_color(not no_color)
        self.__cli_mode = cli_mode

        if not os.path.isdir(project_dir):
            self.__fail(
                f"Invalid project directory: '{project_dir}'.",
                exit_code=FloresErrorCode.FILE_OR_DIR_NOT_FOUND,
                clean_up=False,
            )

        # We need to have the absolute path, to avoid any weirdness with relative paths.
        self.__project_dir = os.path.abspath(project_dir)
        self.__jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            # This may seem like a bad idea, but actually everything that is fed to the
            # Jinja templates is controlled by the user. Thus, it is the user's
            # responsibility to check their own HTML.
            # A more practical explanation is that it's tedious to have to remember to
            # add `| safe` filters practically everywhere, and as we control the input
            # it should not pose a security risk.
            autoescape=False,
        )

    def __fail(
        self,
        message: str,
        exit_code: FloresErrorCode = FloresErrorCode.GENERAL_ERROR,
        clean_up: bool = True,
    ) -> None:
        """Handle a critical failure.

        :param message: the message to report.
        :param exit_code: the code to exit the program with.
        :param clean_up: if True, clean up the build directory before exiting.
        """
        self.__log.critical(message)
        if clean_up:
            self.clean()

        # If we're running in CLI mode, now is the time to bail.
        if self.__cli_mode:
            sys.exit(exit_code.value)

        # If we reached this point, it means that we are not in CLI mode, and thus this
        # code is being used in a library (or programmatically in general). This means
        # that we should raise an exception instead of causing the entire program to
        # shut down.
        exception_type = ERROR_CODE_EXCEPTION_MAP.get(exit_code, FloresError)
        raise exception_type(message)

    @property
    def jinja_env(self) -> jinja2.Environment:
        """Get the Jinja environment that holds the templates.

        :return: the Jinja environment instance associated to the project.
        """
        return self.__jinja_env

    @property
    def config(self) -> dict[str, Any]:
        """Get the config of the generator.

        :return: the config dictionary.
        """
        return self.__get_config()

    @property
    def project_dir(self) -> str:
        """Get the root project directory.

        :return: the path to the root project directory.
        """
        return self.__project_dir

    @property
    def templates_dir(self) -> str:
        """Get the project directory containing the templates.

        :return: the path to the templates directory.
        """
        return os.path.join(self.project_dir, "_templates")

    @property
    def pages_dir(self) -> str:
        """Get the project directory containing the pages.

        :return: the path to the pages directory.
        """
        return os.path.join(self.project_dir, "_pages")

    @property
    def stylesheets_dir(self) -> str:
        """Get the project directory containing the stylesheets (Sass/SCSS/CSS).

        :return: the path to the stylesheets directory.
        """
        return os.path.join(self.project_dir, "_css")

    @property
    def javascript_dir(self) -> str:
        """Get the project directory containing the JavaScript files.

        :return: the path to the JavaScript files directory.
        """
        return os.path.join(self.project_dir, "_js")

    @property
    def posts_dir(self) -> str:
        """Get the project directory containing the posts.

        :return: the path to the posts directory.
        """
        return os.path.join(self.project_dir, "_posts")

    @property
    def drafts_dir(self) -> str:
        """Get the project directory containing the drafts.

        :return: the path to the drafts directory.
        """
        return os.path.join(self.project_dir, "_drafts")

    @property
    def data_dir(self) -> str:
        """Get the project directory containing the data files.

        :return: the path to the data files directory.
        """
        return os.path.join(self.project_dir, "_data")

    @property
    def assets_dir(self) -> str:
        """Get the project directory containing the various assets (images, PDFs...).

        :return: the path to the assets directory.
        """
        return os.path.join(self.project_dir, "_assets")

    @property
    def protected_dirs(self) -> list[str]:
        """Get a list of the protected directories of the project.

        All of the directories that are by convention recognized by the generator are
        considered protected; this is to differentiate them from other, user-defined
        directories.

        :return: the list of the paths to the protected directories.
        """
        return [
            self.templates_dir,
            self.pages_dir,
            self.stylesheets_dir,
            self.javascript_dir,
            self.posts_dir,
            self.drafts_dir,
            self.data_dir,
            self.assets_dir,
            self.build_dir,
        ]

    @property
    def build_dir(self) -> str:
        """Get the build directory of the project.

        This directory will host the final static site after the build.

        :return: the path to the build directory.
        """
        return os.path.join(self.project_dir, "_site")

    @property
    def css_build_dir(self) -> str:
        """Get the CSS build directory of the project.

        This directory will host the final CSS files for the site after the build.

        :return: the path to the CSS build directory.
        """
        return os.path.join(self.build_dir, "css")

    @property
    def javascript_build_dir(self) -> str:
        """Get the JavaScript build directory of the project.

        This directory will host the final JavaScript files for the site after the
        build.

        :return: the path to the JavaScript build directory.
        """
        return os.path.join(self.build_dir, "js")

    @property
    def assets_build_dir(self) -> str:
        """Get the assets build directory of the project.

        This directory will host the final asset files for the site after the build.

        :return: the path to the assets build directory.
        """
        return os.path.join(self.build_dir, "assets")

    @property
    def config_file(self) -> str:
        """Get the path of the config file.

        Note that this will return the path of where the config file is supposed to be;
        it does not mean that the config file is guaranteed to exist.

        :return: the path of the config file.
        """
        return os.path.join(self.data_dir, "config.json")

    def __get_config(self) -> dict[str, Any]:
        """Parse the configuration for the site generator.

        If a special `config.json` file is present in the data directory of the project,
        then it is used as the configuration for the site generator. Otherwise, the
        default configuration (`self.DEFAULT_CONFIG`) is used.

        :return: the parsed configuration for the site generator.
        """
        if os.path.isfile(self.config_file):
            self.__log.debug(f"Loading site config file: '{self.config_file}'.")
            with open(self.config_file, "r") as config_file:
                raw_data = config_file.read()

            try:
                config = json.loads(raw_data)
            except json.decoder.JSONDecodeError as e:
                self.__fail(
                    f"{self.config_file}: {str(e).rstrip('.')}.",
                    exit_code=FloresErrorCode.JSON_ERROR,
                )
            return config

        self.__log.debug("Loading default site config (no config file found).")
        return self.DEFAULT_CONFIG

    def __get_pygments_style(self) -> Optional[str]:
        style = self.config.get("pygments_style")

        if style is None:
            return None

        # The user has specified a style for Pygments; validate it before passing it on.
        if type(style) != str:
            self.__fail(
                message=(
                    f"{self.config_file}: Expected type 'str' but got "
                    f"'{type(style).__name__}' for key 'pygments_style'."
                ),
                exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
            )

        pygments_styles = list(pygments.styles.get_all_styles())
        if style not in pygments_styles:
            self.__fail(
                message=(
                    f"{self.config_file}: Style '{style}' is not a valid Pygments "
                    f"style ({', '.join(pygments_styles)})."
                ),
                exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
            )

        return style

    def __get_image_configs(self) -> list[ImageConfig]:
        raw_config = self.config.get("images")

        if raw_config is None:
            # By default, we should just copy the images over. So, no optimization, and
            # only one size (100%, without a suffix).
            return [ImageConfig(size=1, suffix="", optimize=False)]

        image_configs = []
        # The user has specified a config for images; validate each element before
        # parsing it.
        if type(raw_config) != list:
            self.__fail(
                message=(
                    f"{self.config_file}: Expected type 'list' but got "
                    f"'{type(raw_config).__name__}' for key 'images'."
                ),
                exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
            )

        for image_config in raw_config:
            # Create a working copy of the image config, so that we can safely remove
            # keys without ruining the original.
            image_config_copy = dict(image_config)

            if "size" not in image_config_copy:
                self.__fail(
                    message=(
                        f"{self.config_file}: Missing key 'size' in element "
                        f"'{image_config}' in key 'images'."
                    ),
                    exit_code=FloresErrorCode.MISSING_ELEMENT,
                )

            size = image_config_copy.pop("size")
            if type(size) != float and type(size) != int:
                self.__fail(
                    message=(
                        f"{self.config_file}: Expected type 'float' or 'int' but got "
                        f"'{type(size).__name__}' for key 'size' in element "
                        f"'{image_config}' in key 'images'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )
            if size <= 0 or size > 1:
                self.__fail(
                    message=(
                        f"{self.config_file}: Expected key 'size' to be in range "
                        f"(0, 1] but got '{size}' in element '{image_config}' in key "
                        "'images'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            if "suffix" not in image_config_copy:
                self.__fail(
                    message=(
                        f"{self.config_file}: Missing key 'suffix' in element "
                        f"'{image_config}' in key 'images'."
                    ),
                    exit_code=FloresErrorCode.MISSING_ELEMENT,
                )

            suffix = image_config_copy.pop("suffix")
            if type(suffix) != str:
                self.__fail(
                    message=(
                        f"{self.config_file}: Expected type 'str' but got "
                        f"'{type(suffix).__name__}' for key 'suffix' in element "
                        f"'{image_config}' in key 'images'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            if "optimize" not in image_config_copy:
                self.__fail(
                    message=(
                        f"{self.config_file}: Missing key 'optimize' in element "
                        f"'{image_config}' in key 'images'."
                    ),
                    exit_code=FloresErrorCode.MISSING_ELEMENT,
                )

            optimize = image_config_copy.pop("optimize")
            if type(optimize) != bool:
                self.__fail(
                    message=(
                        f"{self.config_file}: Expected type 'bool' but got "
                        f"'{type(optimize).__name__}' for key 'optimize' in element "
                        f"'{image_config}' in key 'images'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            remaining_image_keys = ", ".join(image_config_copy.keys())
            if remaining_image_keys:
                self.__fail(
                    message=(
                        f"{self.config_file}: Unexpected keys '{remaining_image_keys}' "
                        f"in element '{image_config}' in key 'images'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            image_configs.append(
                ImageConfig(size=size, suffix=suffix, optimize=optimize)
            )

        return image_configs

    def __split_filepath_elements(self, filepath: str) -> tuple[str, str, str]:
        """Split a filepath to its elements (base directory, name, extension).

        :param filepath: the filepath to split.
        :return: a (base directory, name, extension) 3-tuple.
        """
        base_directory, filename_with_extension = os.path.split(filepath)
        filename, extension = os.path.splitext(filename_with_extension)

        # Remove the leading '.' from the extension.
        return (base_directory, filename, extension[1:])

    def __collect_elements_from_dir(
        self,
        directory: str,
        prefixes: Optional[list[str]] = None,
        suffixes: Optional[list[str]] = None,
        files_only: bool = False,
        dirs_only: bool = False,
        recursive: bool = False,
    ) -> list[str]:
        """Collect elements from a given directory.

        Collect elements (filenames and/or directory names) from a given directory.

        :param directory: the base directory in which to look for elements.
        :param prefixes: a list of authorized prefixes to use as a filter.
        :param suffixes: a list of authorized suffixes to use as a filter.
        :param files_only: if True then only collect files (mutually exclusive with
            `dirs_only`).
        :param dirs_only: if True then only collect directories (mutually exclusive with
            `files_only`).
        :param recursive: if True, search the base directory recursively.
        :return: the list of the paths to the collected elements.
        """
        assert not (
            files_only and dirs_only
        ), "The arguments 'files_only' and 'dirs_only' are mutually exclusive."
        # os.walk() does not report an error if an unvalid directory is passed to it, so
        # we should report one here manually to make the behavior uniform regardless of
        # the value of the 'recursive' argument.
        if not os.path.isdir(directory):
            self.__fail(
                f"No such directory: '{directory}'.",
                exit_code=FloresErrorCode.FILE_OR_DIR_NOT_FOUND,
            )

        all_elements = []

        if recursive:
            for dirpath, dirnames, filenames in os.walk(directory):
                for name in dirnames + filenames:
                    all_elements.append(os.path.join(dirpath, name))
        else:
            all_elements = [
                os.path.join(directory, element) for element in os.listdir(directory)
            ]

        if files_only:
            all_elements = [
                element for element in all_elements if os.path.isfile(element)
            ]
        elif dirs_only:
            all_elements = [
                element for element in all_elements if os.path.isdir(element)
            ]

        if prefixes is not None:
            all_elements = [
                element
                for element in all_elements
                if any(
                    [
                        os.path.split(element)[-1].startswith(prefix)
                        for prefix in prefixes
                    ]
                )
            ]
        if suffixes is not None:
            all_elements = [
                element
                for element in all_elements
                if any([element.endswith(suffix) for suffix in suffixes])
            ]

        return all_elements

    def __collect_markdown_files_from_dir(self, directory: str) -> list[str]:
        """Collect all the Markdown files from a given directory.

        :param directory: the directory to collect markdown files from.
        :return: the list of the paths to the markdown files.
        """
        if not os.path.isdir(directory):
            return []

        return self.__collect_elements_from_dir(
            directory,
            suffixes=[".md", ".markdown"],
            files_only=True,
        )

    @property
    def page_files(self) -> list[str]:
        """Collect all the page files of the project.

        :return: the list of the paths to the project's page files.
        """
        return self.__collect_markdown_files_from_dir(self.pages_dir)

    @property
    def template_files(self) -> list[str]:
        """Collect all the template files of the project.

        :return: the list of the paths to the project's template files.
        """
        if not os.path.isdir(self.templates_dir):
            return []

        return self.__collect_elements_from_dir(
            self.templates_dir,
            suffixes=[".html", ".htm"],
            files_only=True,
        )

    @property
    def stylesheet_files(self) -> list[str]:
        """Collect all the stylesheet files of the project.

        :return: the list of the paths to the project's stylesheet files.
        """
        if not os.path.isdir(self.stylesheets_dir):
            return []

        return self.__collect_elements_from_dir(
            self.stylesheets_dir,
            suffixes=[".css", ".scss", ".sass"],
            files_only=True,
            recursive=True,
        )

    @property
    def javascript_files(self) -> list[str]:
        """Collect all the JavaScript files of the project.

        :return: the list of the paths to the project's JavaScript files.
        """
        if not os.path.isdir(self.javascript_dir):
            return []

        return self.__collect_elements_from_dir(
            self.javascript_dir,
            suffixes=[".js"],
            files_only=True,
            recursive=True,
        )

    @property
    def post_files(self) -> list[str]:
        """Collect all the post files of the project.

        :return: the list of the paths to the project's post files.
        """
        return self.__collect_markdown_files_from_dir(self.posts_dir)

    @property
    def draft_files(self) -> list[str]:
        """Collect all the draft files of the project.

        :return: the list of the paths to the project's draft files.
        """
        return self.__collect_markdown_files_from_dir(self.drafts_dir)

    @property
    def data_files(self) -> list[str]:
        """Collect all the data files of the project.

        :return: the list of the paths to the project's data files.
        """
        if not os.path.isdir(self.data_dir):
            return []

        return self.__collect_elements_from_dir(
            self.data_dir,
            suffixes=[".json"],
            files_only=True,
        )

    @property
    def user_data_dirs(self) -> list[str]:
        """Collect all the user data directories of the project.

        The user can create custom data directories, prefixed with an underscore (_).
        Any Markdown-frontmatter files in these directories will be parsed as a user
        data page.

        :return: the list of the paths to the project's user data directories.
        """
        all_dirs = self.__collect_elements_from_dir(
            self.project_dir,
            prefixes=["_"],
            dirs_only=True,
        )

        return [
            directory for directory in all_dirs if directory not in self.protected_dirs
        ]

    def __parse_frontmatter_file(self, filepath: str) -> tuple[dict[str, Any], str]:
        """Parse a Markdown file that may contain frontmatter.

        Frontmatter is essentially just a YAML header to a Markdown file; if it exists,
        it is preceded and succeeded by three dashes:

        ```
        ---
        # Frontmatter goes here
        ---

        Content goes here
        ```

        :param filepath: the path to the frontmatter file to parse.
        :return: a (frontmatter, markdown) tuple.
        """
        self.__log.debug(f"Parsing frontmatter file: '{filepath}'.")
        with open(filepath, "r") as input_file:
            raw_content = input_file.read()

        # Detect the YAML part (the frontmatter).
        frontmatter_match = re.search(self.FRONTMATTER_REGEX, raw_content)
        if frontmatter_match is None:
            self.__fail(
                f"{filepath}: Missing frontmatter.",
                exit_code=FloresErrorCode.MISSING_ELEMENT,
            )

        assert frontmatter_match is not None
        # Parse the YAML part (the frontmatter). If it's empty, we should put an empty
        # dict instead, because that's what an empty frontmatter is equivalent to.
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1)) or {}
        except yaml.parser.ParserError:
            self.__fail(
                f"{filepath}: Error parsing frontmatter (invalid YAML).",
                exit_code=FloresErrorCode.YAML_ERROR,
            )

        # Do not render the Markdown part to HTML (yet)! It might contain Jinja stuff
        # (expressions, statements etc) so we need to wait until build time to do that.
        raw_content = raw_content[frontmatter_match.span()[1] :].strip()

        return (frontmatter, raw_content)

    @property
    def __md_extension_configs(self) -> dict[str, dict[str, Any]]:
        """Assemble the configurations for the Markdown extensions.

        This interface allows us to dynamically configure the Markdown extensions used
        to render Markdown to HTML, based on the configuration of the site generator.

        :return: a dictionary of configurations for the Markdown extensions.
        """
        extension_configs = {}

        pygments_style = self.__get_pygments_style()
        if pygments_style is not None:
            # In order to allow a given Pygments style to be used natively (without the
            # user having to provide special CSS files), we set the noclasses attribute
            # to True, which causes the styling of the code highlights to be embedded in
            # the HTML.
            extension_configs["codehilite"] = {
                "noclasses": True,
                "pygments_style": pygments_style,
            }

        return extension_configs

    def __render_markdown(self, source: str) -> str:
        """Render a Markdown string to HTML.

        During the rendering, the extensions and the extension configurations of the
        generator are used.

        :param source: the Markdown source to render.
        :return: the resulting HTML.
        """
        return markdown.markdown(
            source,
            extensions=self.MD_EXTENSIONS,
            extension_configs=self.__md_extension_configs,
            output_format="html",
        )

    def collect_pages(self) -> list[Page]:
        """Collect and prepare all the main pages of the project.

        :return: a list of Page objects.
        """
        pages = []
        for page_file in self.page_files:
            self.__log.debug(f"Collecting page from file: '{page_file}'.")
            frontmatter, content = self.__parse_frontmatter_file(filepath=page_file)

            if "template" not in frontmatter:
                self.__fail(
                    f"{page_file}: Missing 'template' key in frontmatter.",
                    exit_code=FloresErrorCode.MISSING_ELEMENT,
                )

            if type(frontmatter["template"]) != str:
                self.__fail(
                    message=(
                        f"{page_file}: Expected type 'str' but got "
                        f"'{type(frontmatter['template']).__name__}' for key "
                        "'template'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            page_data = dict(frontmatter)
            # Overwriting the 'name' and 'content' keys is intentional here; if the user
            # provides keys with the same name, we don't want them to collide or erase
            # the actual name/content of the page.
            _, page_data["name"], _ = self.__split_filepath_elements(page_file)
            page_data["content"] = content
            page_data["source_file"] = page_file

            pages.append(
                Page(
                    # See https://github.com/python/mypy/issues/8890.
                    **page_data  # type: ignore
                )
            )

            self.__log.debug(f"Collected page: {pages[-1]}.")

        return pages

    def collect_templates(self) -> list[jinja2.Template]:
        """Collect and prepare all the Jinja templates of the project.

        :return: a list of Template objects.
        """
        templates = []
        for template_file in self.template_files:
            # If any exceptions occur, override them to provide more information about
            # which part failed and where.
            try:
                templates.append(
                    self.jinja_env.get_template(os.path.split(template_file)[-1])
                )
            except jinja2.exceptions.TemplateError as e:
                filename = getattr(e, "filename", template_file)
                lineno = getattr(e, "lineno", "?")
                self.__fail(
                    f"{filename}:{lineno}: {e.message.rstrip('.')}.",
                    exit_code=FloresErrorCode.TEMPLATE_ERROR,
                )

        return templates

    def collect_posts(self, include_drafts: bool) -> list[Post]:
        """Collect and prepare all the post pages of the project.

        A post is a special type of page that refers specifically to a blogpost; its
        filename must be of the format `YYYY-MM-DD-<name>.md|markdown`. The date will
        be inferred by the filename by default, but a `date` key can also be specified
        in the file's frontmatter, which will override the date provided in the file.
        However, the two must match: the `date` key's purpose in the frontmatter is to
        provide a specific time and timezone if needed.
        The post will be stored in `<build_dir>/YYYY/MM/DD/<name>.html` in the final
        build of the site.

        :param include_drafts: if True, include draft posts.
        :return: a list of Post objects.
        """
        posts = []
        files = self.post_files
        if include_drafts:
            files += self.draft_files

        for post_file in files:
            self.__log.debug(f"Collecting post from file: '{post_file}'.")
            frontmatter, content = self.__parse_frontmatter_file(post_file)

            for mandatory_key in ("template", "title"):
                if mandatory_key not in frontmatter:
                    self.__fail(
                        f"{post_file}: Missing '{mandatory_key}' key in frontmatter.",
                        exit_code=FloresErrorCode.MISSING_ELEMENT,
                    )

            template = frontmatter.pop("template")
            if type(template) != str:
                self.__fail(
                    message=(
                        f"{post_file}: Expected type 'str' but got "
                        f"'{type(template).__name__}' for key 'template'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            title = frontmatter.pop("title")
            if type(title) != str:
                self.__fail(
                    message=(
                        f"{post_file}: Expected type 'str' but got "
                        f"'{type(title).__name__}' for key 'title'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            categories = frontmatter.pop("categories", [])
            if type(categories) != list:
                self.__fail(
                    message=(
                        f"{post_file}: Expected type 'list' but got "
                        f"'{type(categories).__name__}' for key 'categories'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )
            for category in categories:
                if type(category) != str:
                    self.__fail(
                        message=(
                            f"{post_file}: Expected type 'str' but got "
                            f"'{type(category).__name__}' for category '{category}'."
                        ),
                        exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                    )

            tags = frontmatter.pop("tags", [])
            if type(tags) != list:
                self.__fail(
                    message=(
                        f"{post_file}: Expected type 'list' but got "
                        f"'{type(tags).__name__}' for key 'tags'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )
            for tag in tags:
                if type(tag) != str:
                    self.__fail(
                        message=(
                            f"{post_file}: Expected type 'str' but got "
                            f"'{type(tag).__name__}' for tag '{tag}'."
                        ),
                        exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                    )

            # Keep filename only, remove extension.
            _, filename, _ = self.__split_filepath_elements(post_file)
            post_name_elements = filename.split("-")
            if len(post_name_elements) < 4:
                self.__fail(
                    message=(
                        f"{post_file}: Post files should be of the form "
                        "'YYYY-MM-DD-post-title-here'."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )
            filename_year = post_name_elements.pop(0)
            filename_month = post_name_elements.pop(0)
            filename_day = post_name_elements.pop(0)
            name = "-".join(post_name_elements)
            base_address = os.path.join(filename_year, filename_month, filename_day)
            url = os.path.join("/", base_address, name)

            date_string = frontmatter.pop("date", None)
            if date_string is not None:
                if type(date_string) != str:
                    self.__fail(
                        message=(
                            f"{post_file}: Expected type 'str' but got "
                            f"'{type(date_string).__name__}' for key 'date'."
                        ),
                        exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                    )
            else:
                date_string = (
                    f"{filename_year}-{filename_month}-{filename_day} 00:00:00 +0000"
                )

            try:
                date = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %z")
            except ValueError as e:
                error_message = str(e).rstrip(".")
                error_message = error_message[0].upper() + error_message[1:]
                self.__fail(
                    f"{post_file}: {error_message}.",
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            post_date_info = PostDateInfo(
                year=date.strftime("%Y"),
                month=date.strftime("%-m"),
                month_padded=date.strftime("%m"),
                month_name=date.strftime("%B"),
                month_name_short=date.strftime("%b"),
                day=date.strftime("%-d"),
                day_padded=date.strftime("%d"),
                day_name=date.strftime("%A"),
                day_name_short=date.strftime("%a"),
                timestamp=date.timestamp(),
            )

            if filename_year != post_date_info["year"]:
                self.__fail(
                    message=(
                        f"{post_file}: Year mismatch; '{filename_year}' in the "
                        f"filename, but '{post_date_info['year']}' in the file."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )
            if filename_month != post_date_info["month_padded"]:
                self.__fail(
                    message=(
                        f"{post_file}: Month mismatch; '{filename_month}' in the "
                        f"filename, but '{post_date_info['month_padded']}' in the file."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )
            if filename_day != post_date_info["day_padded"]:
                self.__fail(
                    message=(
                        f"{post_file}: Day mismatch; '{filename_day}' in the "
                        f"filename, but '{post_date_info['day_padded']}' in the file."
                    ),
                    exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                )

            post_data = dict(frontmatter)
            # Overwriting the following keys is intentional here; if the user provides
            # keys with the same name, we don't want them to collide or erase the actual
            # keys. For example writing 'is_draft: false' in the frontmatter shouldn't
            # override the logic that determines whether or not something is a draft.
            post_data["name"] = name
            post_data["base_address"] = base_address
            post_data["url"] = url
            post_data["template"] = template
            post_data["title"] = title
            post_data["content"] = content
            post_data["is_draft"] = post_file in self.draft_files
            post_data["date"] = post_date_info
            post_data["categories"] = categories
            post_data["tags"] = tags
            post_data["source_file"] = post_file

            posts.append(
                Post(
                    # See https://github.com/python/mypy/issues/8890.
                    **post_data  # type: ignore
                )
            )

            self.__log.debug(f"Collected post: {posts[-1]}.")

        # Sort the posts by timestamp, oldest post first.
        return sorted(posts, key=lambda post: post["date"]["timestamp"], reverse=True)

    def collect_data(self) -> dict[Any, Any]:
        """Collect the site data from the data files.

        Site data is stored in a dictionary; it is indexed by the names of the data
        files. For example, the data contained in `names.json` will be indexed under
        `data["names"]`.

        :return: the full data dictionary of the site.
        """
        data = {}
        for data_file in self.data_files:
            # Keep the filename and get rid of the extension.
            _, name, _ = self.__split_filepath_elements(data_file)
            # Skip the config file, as that is handled separately; see
            # `flores.generator.Generator.config`.
            if name == "config":
                continue

            with open(data_file, "r") as file:
                raw_data = file.read()

            try:
                data[name] = json.loads(raw_data)
            except json.decoder.JSONDecodeError as e:
                self.__fail(
                    f"{data_file}: {str(e).rstrip('.')}.",
                    exit_code=FloresErrorCode.JSON_ERROR,
                )

        return data

    def collect_user_data_pages(self) -> dict[str, list[Page]]:
        """Collect the user-defined data pages.

        The user-defined data pages will be collected just like normal pages; see
        `user_data_dirs()` for more information about which directories can contain
        them. They will be indexed by the name of each user data page directory; for
        for example, pages under `_projects` will be indexed via `data["projects"]`.

        :return: a dictionary containing the user-defined pages, indexed by their names.
        """
        data: dict[str, list[Page]] = {}
        for directory in self.user_data_dirs:
            markdown_files = self.__collect_markdown_files_from_dir(directory)
            # Remove the leading '_' from the directory name.
            data_category = os.path.basename(directory)[1:]
            data[data_category] = []
            for file in markdown_files:
                self.__log.debug(f"Collecting user data page from file: '{file}'.")
                frontmatter, content = self.__parse_frontmatter_file(file)

                if "template" not in frontmatter:
                    self.__fail(
                        f"{file}: Missing 'template' key in frontmatter.",
                        exit_code=FloresErrorCode.MISSING_ELEMENT,
                    )

                if type(frontmatter["template"]) != str:
                    self.__fail(
                        message=(
                            f"{file}: Expected type 'str' but got "
                            f"'{type(frontmatter['template']).__name__}' for key "
                            "'template'."
                        ),
                        exit_code=FloresErrorCode.WRONG_TYPE_OR_FORMAT,
                    )

                page_data = frontmatter
                # Only keep the filename, without the extension.
                _, page_data["name"], _ = self.__split_filepath_elements(file)
                page_data["url"] = os.path.join(data_category, page_data["name"])
                page_data["content"] = content
                page_data["source_file"] = file

                data[data_category].append(
                    Page(
                        # See https://github.com/python/mypy/issues/8890.
                        **page_data  # type: ignore
                    )
                )

                self.__log.debug(
                    f"Collected user data page: {data[data_category][-1]}."
                )

        return data

    def collect_images(self) -> list[str]:
        """Collect the image files from the assets.

        :return: the paths to the image files.
        """
        if not os.path.isdir(self.assets_dir):
            return []

        return self.__collect_elements_from_dir(
            self.assets_dir,
            suffixes=self.IMAGE_EXTENSIONS,
            files_only=True,
            recursive=True,
        )

    def collect_resources(self, include_drafts: bool = False) -> list[str]:
        """Collect all the resources of the site.

        By "resources" we refer to all the files used to build the site, such as pages,
        templates, data files etc. This is used for example in the server
        (flores.server.Server), to monitor if any of the resources have been modified.

        :param include_drafts: if True, include the drafts in the resources.
        :return: a list of paths to the resources.
        """
        resources = (
            self.page_files
            + self.template_files
            + self.post_files
            + self.data_files
            + self.stylesheet_files
            + self.javascript_files
        )

        for directory in (
            self.pages_dir,
            self.templates_dir,
            self.posts_dir,
            self.data_dir,
            self.stylesheets_dir,
            self.javascript_dir,
        ):
            if os.path.isdir(directory):
                resources.append(directory)

        if os.path.isdir(self.assets_dir):
            resources += self.__collect_elements_from_dir(
                self.assets_dir, files_only=True, recursive=True
            ) + [self.assets_dir]

        for directory in self.user_data_dirs:
            resources += self.__collect_markdown_files_from_dir(directory) + [directory]

        if include_drafts:
            resources += self.draft_files + [self.drafts_dir]

        return resources

    def build_images(self) -> None:
        """Build the final images.

        Starting from the original images of the site, build the final images based on
        the configuration of the site. The user can specify different sizes,
        optimization etc in the configuration of the site, so multiple images can be
        generated from one base image.
        """
        image_files = self.collect_images()
        image_configs = self.__get_image_configs()

        for i, source_file in enumerate(image_files):
            self.__log.debug(
                f"Building image '{source_file}' ({i + 1}/{len(image_files)})..."
            )

            for image_config in image_configs:
                size_factor = image_config["size"]
                suffix = image_config["suffix"]
                optimize = image_config["optimize"]
                # Figure out the destination directory & filepath of the image file.
                (
                    source_dirpath,
                    source_name,
                    source_extension,
                ) = self.__split_filepath_elements(source_file)
                dest_dirpath = os.path.join(
                    self.assets_build_dir,
                    os.path.relpath(source_dirpath, self.assets_dir),
                )
                dest_file = os.path.join(
                    dest_dirpath, f"{source_name}{suffix}.{source_extension}"
                )
                # Make sure to create any directories that are needed on the destination
                # first.
                os.makedirs(dest_dirpath, exist_ok=True)

                # If the size factor is 1 and optimization is disabled, there are no
                # modifications to make to this image; just copy it over.
                if size_factor == 1 and not optimize:
                    self.__log.debug(f"Copying image '{source_file}'...")
                    shutil.copy2(source_file, dest_file)
                    self.__log.debug(f"Image '{source_file}' copied to '{dest_file}'.")
                    continue

                self.__log.debug(f"Loading image '{source_file}'...")
                try:
                    source_image = Image.open(source_file)
                except Exception as e:
                    error_message = str(e).rstrip(".")
                    error_message = error_message[0].upper() + error_message[1:]
                    self.__fail(
                        f"{source_file}: {error_message}.",
                        exit_code=FloresErrorCode.IMAGE_ERROR,
                    )

                dest_image_size = (
                    int(source_image.size[0] * size_factor),
                    int(source_image.size[1] * size_factor),
                )
                dest_image = source_image.resize(
                    dest_image_size, Image.Resampling.LANCZOS
                )
                dest_image.save(dest_file, optimize=optimize)
                self.__log.debug(f"Image '{source_file}' saved at '{dest_file}'.")

        self.__log.debug("Done building images.")

    def init(self) -> None:
        """Initialize a basic site."""
        self.__log.info(f"Initializing basic site at '{self.project_dir}'...")

        # We should be okay to create the project directory.
        # The basic template used by `init` will only contain a basic config data file,
        # a basic template and a basic page.
        os.makedirs(self.data_dir)
        os.makedirs(self.templates_dir)
        os.makedirs(self.pages_dir)

        # We can now write the appropriate template data into each file.
        with open(self.config_file, "w") as config_file:
            config_file.write(self.INIT_CONFIG_FILE)
        with open(os.path.join(self.templates_dir, "main.html"), "w") as main_template:
            main_template.write(self.INIT_TEMPLATE_FILE)
        with open(os.path.join(self.pages_dir, "index.md"), "w") as main_page:
            main_page.write(self.INIT_PAGE_FILE)

        self.__log.info(f"Done! Site initialized at '{self.project_dir}'.")

    def clean(self) -> None:
        """Clean up the generated site."""
        self.__log.debug(f"Cleaning project build dir: '{self.build_dir}'.")
        if os.path.isdir(self.build_dir):
            shutil.rmtree(self.build_dir)

    def build(
        self,
        include_drafts: bool = False,
        disable_image_build: bool = False,
    ) -> None:
        """Build the final site.

        Use all of the resources of the project to build the actual site.

        :param include_drafts: if True, include drafts along with posts.
        :param disable_image_build: if True, do not build images. This can be used to
            speed up consecutive site builds, when there are a lot of generated images.
        """
        self.__log.info(
            f"Building static site from project directory '{self.project_dir}'..."
        )
        start_build_time = time.time()

        # Purge any previous builds and start from scratch.
        self.clean()
        os.makedirs(self.build_dir, exist_ok=True)

        pages = self.collect_pages()
        templates = self.collect_templates()
        posts = self.collect_posts(include_drafts=include_drafts)
        data = self.collect_data()
        user_data_pages = self.collect_user_data_pages()

        # Collect categories and tags.
        categories = set()
        tags = set()
        for post in posts:
            for category in post["categories"]:
                categories.add(category)
            for tag in post["tags"]:
                tags.add(tag)

        site_data = {
            **user_data_pages,
            "pages": pages,
            "posts": posts,
            "data": data,
            "blog": {
                "categories": sorted(categories),
                "tags": sorted(tags),
            },
            "config": self.config,
        }

        for page in pages:
            page_templates = [
                template
                for template in templates
                if self.__split_filepath_elements(template.name)[1] == page["template"]
            ]
            if not page_templates:
                self.__fail(
                    message=(
                        f"{page['source_file']}: Template '{page['template']}' not "
                        f"found in {self.templates_dir}."
                    ),
                    exit_code=FloresErrorCode.FILE_OR_DIR_NOT_FOUND,
                )

            template = page_templates[0]

            # Given that the user can embed Jinja statements, variables etc in their
            # markdown (e.g. {% for post in site.posts %}), we need to first render
            # those out.
            try:
                flat_page_content = self.jinja_env.from_string(page["content"]).render(
                    site=site_data, page=page
                )
            except jinja2.exceptions.TemplateError as e:
                self.__fail(
                    f"{page['source_file']}: {e.message.rstrip('.')}.",
                    exit_code=FloresErrorCode.TEMPLATE_ERROR,
                )
            # Now that the markdown file is "flat" (i.e. it doesn't contain any Jinja
            # statements, variables etc), we can actually render the markdown.
            page["content"] = self.__render_markdown(flat_page_content)

            with open(
                os.path.join(self.build_dir, f"{page['name']}.html"), "w"
            ) as html_file:
                try:
                    html_file.write(template.render(site=site_data, page=page))
                except jinja2.exceptions.TemplateError as e:
                    filename = getattr(e, "filename", template.filename)
                    lineno = getattr(e, "lineno", "?")
                    self.__fail(
                        message=(
                            f"{filename}:{lineno} (from {page['source_file']}): "
                            f"{e.message.rstrip('.')}."
                        ),
                        exit_code=FloresErrorCode.TEMPLATE_ERROR,
                    )

        # Render the posts.
        for post in posts:
            # We first need to create the hierarchy to display the posts. The posts will
            # be stored in folders in the following fashion:
            # 'YYYY-MM-DD-post-title-here.md' -> YYYY/MM/DD/post-title-here.html
            os.makedirs(
                os.path.join(self.build_dir, post["base_address"]), exist_ok=True
            )

            post_templates = [
                template
                for template in templates
                if self.__split_filepath_elements(template.name)[1] == post["template"]
            ]
            if not post_templates:
                self.__fail(
                    message=(
                        f"{post['source_file']}: Template '{post['template']}' not "
                        f"found in {self.templates_dir}."
                    ),
                    exit_code=FloresErrorCode.FILE_OR_DIR_NOT_FOUND,
                )

            template = post_templates[0]

            # Given that the user can embed Jinja statements, variables etc in their
            # markdown (e.g. {% for post in site.posts %}), we need to first render
            # those out.
            try:
                flat_post_content = self.jinja_env.from_string(post["content"]).render(
                    site=site_data, page=post
                )
            except jinja2.exceptions.TemplateError as e:
                self.__fail(
                    f"{post['source_file']}: {e.message.rstrip('.')}.",
                    exit_code=FloresErrorCode.TEMPLATE_ERROR,
                )
            # Now that the markdown file is "flat" (i.e. it doesn't contain any Jinja
            # statements, variables etc), we can actually render the markdown.
            post["content"] = self.__render_markdown(flat_post_content)

            with open(
                os.path.join(
                    self.build_dir, post["base_address"], f"{post['name']}.html"
                ),
                "w",
            ) as final_post_file:
                try:
                    final_post_file.write(template.render(site=site_data, page=post))
                except jinja2.exceptions.TemplateError as e:
                    filename = getattr(e, "filename", template.filename)
                    lineno = getattr(e, "lineno", "?")
                    self.__fail(
                        message=(
                            f"{filename}:{lineno} (from {post['source_file']}): "
                            f"{e.message.rstrip('.')}."
                        ),
                        exit_code=FloresErrorCode.TEMPLATE_ERROR,
                    )

        # Render the custom user pages.
        for data_page_category in user_data_pages:
            # First, create a directory to host the pages. For example, if this data
            # is projects, we will make a "projects" dir and then host the pages inside
            # it: "projects/my_project.html", "projects/another_project.html" etc.
            os.makedirs(os.path.join(self.build_dir, data_page_category))

            for data_page in user_data_pages[data_page_category]:
                data_page_templates = [
                    template
                    for template in templates
                    if self.__split_filepath_elements(template.name)[1]
                    == data_page["template"]
                ]
                if not data_page_templates:
                    self.__fail(
                        message=(
                            f"{data_page['source_file']}: Template "
                            f"'{data_page['template']}' not found in "
                            f"{self.templates_dir}."
                        ),
                        exit_code=FloresErrorCode.FILE_OR_DIR_NOT_FOUND,
                    )

                template = data_page_templates[0]

                # Given that the user can embed Jinja statements, variables etc in their
                # markdown (e.g. {% for post in site.posts %}), we need to first render
                # those out.
                try:
                    flat_data_page_content = self.jinja_env.from_string(
                        data_page["content"]
                    ).render(site=site_data, page=data_page)
                except jinja2.exceptions.TemplateError as e:
                    self.__fail(
                        f"{data_page['source_file']}: {e.message.rstrip('.')}.",
                        exit_code=FloresErrorCode.TEMPLATE_ERROR,
                    )
                # Now that the markdown file is "flat" (i.e. it doesn't contain any
                # Jinja statements, variables etc), we can actually render the markdown.
                data_page["content"] = self.__render_markdown(flat_data_page_content)

                with open(
                    os.path.join(
                        self.build_dir, data_page_category, f"{data_page['name']}.html"
                    ),
                    "w",
                ) as final_data_page_file:
                    try:
                        final_data_page_file.write(
                            template.render(site=site_data, page=data_page)
                        )
                    except jinja2.exceptions.TemplateError as e:
                        filename = getattr(e, "filename", template.filename)
                        lineno = getattr(e, "lineno", "?")
                        self.__fail(
                            message=(
                                f"{filename}:{lineno} "
                                f"(from {data_page['source_file']}): "
                                f"{e.message.rstrip('.')}."
                            ),
                            exit_code=FloresErrorCode.TEMPLATE_ERROR,
                        )

        if os.path.isdir(self.stylesheets_dir):
            sass.compile(
                dirname=(self.stylesheets_dir, self.css_build_dir),
                output_style="compressed",
            )
            # Unfortunately, the sass library will only pick up on *.scss and *.sass
            # files. If there are any *.css files, we'll have to copy them over
            # manually.
            pure_css_files = self.__collect_elements_from_dir(
                self.stylesheets_dir, files_only=True, suffixes=[".css"], recursive=True
            )
            for pure_css_file in pure_css_files:
                destination_file = os.path.join(
                    self.css_build_dir,
                    os.path.relpath(pure_css_file, self.stylesheets_dir),
                )
                destination_dir, _, _ = self.__split_filepath_elements(destination_file)
                # Make sure to create any directories that are needed on the destination
                # first; some files might be nested and their parent directories might
                # not exist in the build directory.
                os.makedirs(destination_dir, exist_ok=True)
                # Use shutil.copy2() here to copy file permissions, as well as metadata.
                shutil.copy2(pure_css_file, destination_file)

        if os.path.isdir(self.javascript_dir):
            # Copy the entire JS dir into the build directory, preserving its
            # structure.
            shutil.copytree(self.javascript_dir, self.javascript_build_dir)

        if os.path.isdir(self.assets_dir):
            # Copy the entire assets dir into the build directory, preserving its
            # structure.
            shutil.copytree(self.assets_dir, self.assets_build_dir)
            # Remove all the image files, as they will get handled separately.
            for image_file in self.__collect_elements_from_dir(
                self.assets_build_dir,
                suffixes=self.IMAGE_EXTENSIONS,
                files_only=True,
                recursive=True,
            ):
                os.remove(image_file)

        if not disable_image_build:
            self.build_images()

        stop_build_time = time.time()
        self.__log.info(
            f"Done ({stop_build_time - start_build_time:.2f}s)! The finished site is "
            f"available in '{self.build_dir}'."
        )
