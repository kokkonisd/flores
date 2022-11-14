"""The entrypoint to Flores' CLI."""

import argparse
import logging
import os
import sys

from flores import __version__
from flores.exceptions import FloresErrorCode
from flores.generator import GENERATOR_LOGGER, Generator
from flores.server import Server


def init_cmd(args: argparse.Namespace) -> None:
    """Run the 'init' command."""
    # Refuse to initialize on an existing directory/file to avoid destroying
    # something by accident.
    if os.path.exists(args.project_dir):
        GENERATOR_LOGGER.critical(
            f"Cannot initialize: '{args.project_dir}' already exists."
        )
        sys.exit(FloresErrorCode.FILE_OR_DIR_NOT_FOUND.value)

    os.makedirs(args.project_dir)

    generator = Generator(
        project_dir=args.project_dir, cli_mode=True, log_level=logging.INFO
    )
    generator.init()


def build_cmd(args: argparse.Namespace) -> None:
    """Run the 'build' command."""
    generator = Generator(
        project_dir=args.project_dir,
        cli_mode=True,
        log_level=logging.DEBUG if args.verbose else logging.INFO,
        log_file=args.log_file,
        no_color=args.no_color,
    )
    generator.build(
        include_drafts=args.drafts,
    )


def clean_cmd(args: argparse.Namespace) -> None:
    """Run the 'clean' command."""
    generator = Generator(
        project_dir=args.project_dir, cli_mode=True, log_level=logging.INFO
    )
    generator.clean()


def serve_cmd(args: argparse.Namespace) -> None:
    """Run the 'serve' command."""
    server = Server(
        project_dir=args.project_dir,
        port=args.port,
        log_level=logging.DEBUG if args.verbose else logging.INFO,
        log_file=args.log_file,
        no_color=args.no_color,
    )
    server.serve(
        include_drafts=args.drafts,
        disable_image_rebuild=args.disable_image_rebuild,
        auto_rebuild=args.auto_rebuild,
    )


def __add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add some common arguments to a parser."""
    parser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="The directory of the project.",
    )
    parser.add_argument(
        "-d", "--drafts", help="Include drafts in the site.", action="store_true"
    )

    logging_group = parser.add_argument_group("logging")
    logging_group.add_argument(
        "-v",
        "--verbose",
        help="Provide more detailed information in the logs.",
        action="store_true",
    )
    logging_group.add_argument(
        "--log-file",
        help="The file to write logs to (by default, logs are written in stderr).",
    )
    logging_group.add_argument(
        "--no-color", help="Disable colors in the logs.", action="store_true"
    )


def main() -> None:
    """Parse command-line arguments and run Flores."""
    parser = argparse.ArgumentParser(description="Build/serve a static site.")
    parser.set_defaults(func=None)
    parser.add_argument(
        "--version",
        help="Show the version of Flores.",
        action="version",
        version=f"flores, version {__version__}",
    )

    subparsers = parser.add_subparsers()

    init_subparser = subparsers.add_parser("init", help="Initialize a basic site.")
    init_subparser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="The directory of the project.",
    )
    init_subparser.set_defaults(func=init_cmd)

    build_subparser = subparsers.add_parser("build", help="Build the static site.")
    __add_common_args(build_subparser)
    build_subparser.set_defaults(func=build_cmd)

    clean_subparser = subparsers.add_parser(
        "clean", help="Remove the local build of the static site."
    )
    clean_subparser.add_argument(
        "project_dir",
        nargs="?",
        default=".",
        help="The directory of the project.",
    )
    clean_subparser.set_defaults(func=clean_cmd)

    serve_subparser = subparsers.add_parser(
        "serve", help="Build and serve the static site locally."
    )
    __add_common_args(serve_subparser)
    serve_subparser.add_argument(
        "-p",
        "--port",
        help="The port to serve the site on.",
        type=int,
    )

    rebuild_group = serve_subparser.add_argument_group("auto-rebuild")
    rebuild_group.add_argument(
        "-r",
        "--auto-rebuild",
        help="Rebuild any time a file changes.",
        action="store_true",
    )
    rebuild_group.add_argument(
        "-I",
        "--disable-image-rebuild",
        help="Do not rebuild images to accelerate rebuilds.",
        action="store_true",
    )
    serve_subparser.set_defaults(func=serve_cmd)

    args = parser.parse_args()
    assert args is not None

    if args.func is not None:
        args.func(args)
    else:
        parser.print_help()
