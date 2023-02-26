import logging
import multiprocessing
import os
import signal
import sys
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

    # Use the "spawn" method for processes, to ensure that it is the same across all
    # platforms (see `multiprocessing`'s docs).
    # However, Flores' logger is not picklable; since logging is disregarded in tests
    # that use this fixture, we can replace it here by default loggers to make sure that
    # the final Server and Generator objects are pickleable. This will allow us to use
    # "spawn".
    server._Server__log = logging.getLogger(  # type: ignore
        f"{request.node.name}-server"
    )
    server.generator._Generator__log = logging.getLogger(  # type: ignore
        f"{request.node.name}-generator"
    )
    multiprocessing_context = multiprocessing.get_context("spawn")
    server_process = multiprocessing_context.Process(target=server.serve, kwargs=kwargs)

    server_process.start()
    # Give some time to the server to start. Since some CIs may be slow (like macOS on
    # GitHub), we overshoot the mark here by quite a bit probably; however, we get
    # stable results.
    time.sleep(2)

    yield server

    assert server_process.pid is not None
    # Send a Ctrl-C to the server to stop it.
    if sys.platform == "win32":
        # On Windows, if you do not create a new processing group when creating a
        # process, and you then send a Ctrl-C signal to that process, it is also
        # propagated to the parent. In simple terms, if we Ctrl-C the server here, it
        # also kills whatever is running the testsuite (which is obviously not what we
        # want). I cannot find a way to create a new process group when creating the
        # process, so the next simplest way to handle this is to catch the Ctrl-C when
        # it arrives at the testsuite level (here) and simply ignore it.
        try:
            os.kill(server_process.pid, signal.CTRL_C_EVENT)
            # This wait time might seem way too long, but it is once again to accomodate
            # slow CI machines. In reality, for a fast machine it does not matter: the
            # KeyboardInterrupt will happen faster, so the sleep will be interrupted.
            time.sleep(120)
            raise AssertionError("Ctrl-C handle timeout not long enough")
        except KeyboardInterrupt:
            pass
    else:
        os.kill(server_process.pid, signal.SIGINT)

    server_process.join()
