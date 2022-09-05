import multiprocessing
import os
import signal
import time
import typing

import pytest
import pytest_cov
from _pytest.config import Config

from flores.server import Server


def pytest_configure(config: Config) -> None:
    """Add a marker for the arguments passed to the server.

    See the `flores_server()` fixture below.
    """
    config.addinivalue_line("markers", "server_data: mark arguments for server")


@pytest.fixture
def flores_server(test_data_dir: str, request: typing.Any) -> typing.Generator:
    """Set up a local Flores server.

    :param test_data_dir: the directory containing the data (site assets) needed for
        the test (should have the same name as the test).
    """
    server = Server(project_dir=test_data_dir)
    # We need to get the arguments passed to `flores.server.Server.serve()` via a pytest
    # marker.
    marker = request.node.get_closest_marker("server_data")
    kwargs = {}
    if marker is not None:
        kwargs["include_drafts"] = marker.kwargs.get("include_drafts", False)
        kwargs["disable_image_rebuild"] = marker.kwargs.get(
            "disable_image_rebuild", False
        )
        kwargs["auto_rebuild"] = marker.kwargs.get("auto_rebuild", False)

    # Allow pytest-cov to track coverage on the server via a different process.
    # See https://pytest-cov.readthedocs.io/en/latest/subprocess-support.html\
    #     if-you-use-multiprocessing-process.
    pytest_cov.embed.cleanup_on_sigterm()
    server_process = multiprocessing.Process(target=server.serve, kwargs=kwargs)

    server_process.start()
    # Give some time to the server to start.
    time.sleep(0.5)

    yield server

    assert server_process.pid is not None
    # Send a Ctrl-C to the server to stop it.
    os.kill(server_process.pid, signal.SIGINT)
    server_process.join()
