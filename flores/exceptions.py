"""The Flores exceptions and error codes.

Exceptions are used when Flores is used in 'library' mode, while error codes are used
when Flores is used in CLI mode.

The mapping between the two is defined by ERROR_CODE_EXCEPTION_MAP.
"""

import enum

import jinja2
import yaml


class FloresError(Exception):
    """The base error class for Flores."""


class FileOrDirNotFoundError(FloresError, FileNotFoundError):
    """Error for a file or directory could not be found."""


class MissingElementError(FloresError, KeyError, ValueError):
    """Error for a missing element (such as a 'template' key)."""


class WrongTypeOrFormatError(FloresError, TypeError, ValueError):
    """Error for a wrong type or format (such as a wrong format of a post file)."""


class TemplateError(FloresError, jinja2.exceptions.TemplateError):
    """Error for a Jinja template."""


class YAMLError(FloresError, yaml.parser.ParserError):
    """Error for a frontmatter (YAML)."""


class JSONError(FloresError):
    """Error for a data file (JSON)."""


class ImageError(FloresError):
    """Error for an image file."""


@enum.unique
class FloresErrorCode(enum.Enum):
    """Describe the Flores error codes.

    The reason why error codes find themselves in the range 3-126 is because POSIX
    defines very specific error cases for values 1-2, 126-165 and 255.
    Of course, 1 is defined here as it is *the* catchall value for errors.
    Source: https://tldp.org/LDP/abs/html/exitcodes.html.
    """

    GENERAL_ERROR = 1
    FILE_OR_DIR_NOT_FOUND = 3
    MISSING_ELEMENT = 4
    WRONG_TYPE_OR_FORMAT = 5
    TEMPLATE_ERROR = 6
    YAML_ERROR = 7
    JSON_ERROR = 8
    IMAGE_ERROR = 9


ERROR_CODE_EXCEPTION_MAP = {
    FloresErrorCode.GENERAL_ERROR: FloresError,
    FloresErrorCode.FILE_OR_DIR_NOT_FOUND: FileOrDirNotFoundError,
    FloresErrorCode.MISSING_ELEMENT: MissingElementError,
    FloresErrorCode.WRONG_TYPE_OR_FORMAT: WrongTypeOrFormatError,
    FloresErrorCode.TEMPLATE_ERROR: TemplateError,
    FloresErrorCode.YAML_ERROR: YAMLError,
    FloresErrorCode.JSON_ERROR: JSONError,
    FloresErrorCode.IMAGE_ERROR: ImageError,
}
