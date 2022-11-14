"""The local Flores server.

This server is **NOT** meant to be used in production; it is only meant to be used as a
local testing server to preview the site and play around with local modifications.
"""

import logging
import os
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional

from flores.exceptions import FloresError
from flores.generator import Generator
from flores.logger import FloresLogger


class FloresHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Implement a custom request handler for the Flores server.

    This is mostly a workaround to have custom 404 pages and to not have to specify
    '.html' at the end of each page.
    """

    __custom_404_response = None

    def do_GET(self):
        """Handle a GET request.

        This is a workaround to be able to access pages without specifying '.html' at
        the end.
        """
        # If we got a request for an endpoint that's missing the .html extension, add it
        # here so the server can handle it properly.
        if os.path.isfile(self.translate_path(self.path) + ".html"):
            self.path += ".html"

        super().do_GET()

    def send_error(self, code: int, *args, **kwargs):
        """Handle custom 404 pages.

        We override this method to be able to serve a custom 404 page if it exists.
        """
        custom_404_file = self.translate_path("404.html")
        # Look for a custom 404 file, and load it for further use if it exists.
        if self.__custom_404_response is None and os.path.exists(custom_404_file):
            with open(custom_404_file, "r") as file:
                self.__custom_404_response = file.read()

        # If we have a custom 404 response, serve that instead.
        if code == 404 and self.__custom_404_response is not None:
            self.error_message_format = self.__custom_404_response

        super().send_error(code, *args, **kwargs)


# Ensure that a single logger is used for all servers.
SERVER_LOGGER = FloresLogger("server")


class Server:
    """Implement the Flores local site server.

    This server is **NOT** a production server; it is only meant to be used locally.

    :cvar DEFAULT_PORT: the default port when serving a site on localhost.
    """

    DEFAULT_PORT = 4000

    def __init__(
        self,
        project_dir: str,
        port: Optional[int] = None,
        log_level: Any = logging.DEBUG,
        log_file: Optional[str] = None,
        no_color: bool = False,
    ) -> None:
        """Initialize the server.

        :param project_dir: the root directory of the project, containing all the
            necessary resources for the site.
        :param port: the port to serve the site on.
        :param log_level: the level of logging
            (i.e. logging.DEBUG|INFO|WARNING|ERROR|CRITICAL).
        :param log_file: the file to write the logs to; if None, write logs to stderr.
        :param no_color: if True, disable colors when logging.
        """
        self.port = port or self.DEFAULT_PORT

        # Set up logging.
        self.__log = SERVER_LOGGER
        self.__log.set_level(log_level)
        self.__log.set_log_file(log_file)
        self.__log.set_color(not no_color)

        # Make sure to convert this to an absolute path, to avoid issues with relative
        # paths when looking up files etc.
        project_dir = os.path.abspath(project_dir)
        self.site_dir = os.path.join(project_dir, "_site")
        self.__generator = Generator(
            project_dir=project_dir,
            cli_mode=False,
            log_level=log_level,
            log_file=log_file,
            no_color=no_color,
        )

    @property
    def generator(self) -> Generator:
        """Get the site generator associated to the server."""
        return self.__generator

    def __compute_resource_hash(self, include_drafts: bool) -> int:
        """Compute the hash of the resources of the site.

        This hash allows us to monitor for possible changes in the site.

        :param include_drafts: if True, include the drafts in the resources.
        :return: the hash of all the resources.
        """
        self.__log.debug("Computing resource hash...")
        resource_mtime_string = ""
        for resource in sorted(
            self.generator.collect_resources(include_drafts=include_drafts)
        ):
            resource_mtime_string += str(os.path.getmtime(resource))

        return hash(resource_mtime_string)

    def serve(
        self,
        include_drafts: bool = False,
        disable_image_rebuild: bool = False,
        auto_rebuild: bool = False,
    ) -> None:
        """Serve the site on localhost.

        :param include_drafts: if True, include the drafts in the site.
        :param disable_image_rebuild: if True, do not rebuild images.
        :param auto_rebuild: if True, monitor site resources for changes and rebuild
            automatically when a change is detected.
        """
        self.__log.debug("Initializing site to serve...")
        resource_hash = self.__compute_resource_hash(include_drafts=include_drafts)

        # If the site cannot build to start with, there is no point in attempting to
        # serve it.
        try:
            self.generator.build(include_drafts=include_drafts)
        except FloresError:
            self.__log.critical("Failed to build site; nothing to serve.")
            sys.exit(1)

        # Set up the server thread.
        try:
            server = ThreadingHTTPServer(
                ("localhost", self.port),
                partial(FloresHTTPRequestHandler, directory=self.site_dir),
            )
        except OSError:
            self.__log.critical(
                f"Address `http://localhost:{self.port}` is already in use; is another "
                "server running?"
            )
            sys.exit(1)
        server.timeout = 0.5
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.start()

        self.__log.info(f"Serving site at http://localhost:{self.port}.")

        try:
            if auto_rebuild:
                self.__log.debug("Running with auto-rebuild.")
                while True:
                    new_resource_hash = self.__compute_resource_hash(
                        include_drafts=include_drafts
                    )
                    if new_resource_hash != resource_hash:
                        self.__log.info("Site files changed, rebuilding.")
                        resource_hash = new_resource_hash
                        try:
                            self.generator.build(
                                include_drafts=include_drafts,
                                disable_image_build=disable_image_rebuild,
                            )
                        except FloresError:
                            self.__log.warning("Failed to rebuild site.")
                    time.sleep(0.5)
            else:
                self.__log.debug("Running without auto-rebuild.")
                while True:
                    pass
        except KeyboardInterrupt:
            self.__log.info("Stopping server.")
            server.shutdown()
            server.server_close()
            server_thread.join()
