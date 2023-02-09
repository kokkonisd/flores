import os
import shutil
import signal
import subprocess
import sys
import tempfile
import typing

import pytest


class FloresCLI:
    """Implement a call to the CLI of Flores.

    :ivar lingering_processes: the list of processes that might still linger and might
        need to be killed manually.
    """

    lingering_processes: list[subprocess.Popen] = []

    def run(self, *args) -> subprocess.CompletedProcess:
        """Run Flores in CLI mode with optional arguments.

        :param *args: arguments to Flores.
        :return: the result of the process running Flores.
        """
        if len(args) > 0:
            assert args[0] != "serve", "Use `runserver()` to test the Flores server."
        return subprocess.run(["flores", *args], capture_output=True, text=True)

    def runserver(self, *args) -> subprocess.Popen:
        """Run a Flores server.

        This implies the creation of a separate process, that will run in parallel;
        we will not wait for it to complete, as the whole point of running a server is
        to be able to send it requests during the test. Thus, the server processes
        created here will be stored in this class' `lingering_processes` attribute, to
        be able to be killed when the test is done.

        :param *args: arguments to the server command.
        """
        creationflags = 0
        # On Windows, we need to make sure the process is created in its own, separate
        # group, in order to make sure no signals (like Ctrl-C) are propagated upward
        # to the parent process.
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        process = subprocess.Popen(
            ["flores", "serve", *args],
            stderr=subprocess.PIPE,
            creationflags=creationflags,
        )
        self.lingering_processes.append(process)
        return process

    def clean_up(self) -> None:
        """Kill any lingering processes.

        See the docstring of the `runserver()` method.
        """
        for lingering_process in self.lingering_processes:
            if sys.platform == "win32":
                kill_signal = signal.SIGTERM
            else:
                kill_signal = signal.SIGKILL

            lingering_process.send_signal(kill_signal)
            lingering_process.wait()

        self.lingering_processes = []


@pytest.fixture()
def flores_cli() -> typing.Generator:
    """Provide a CLI object for Flores."""
    cli = FloresCLI()
    yield cli
    cli.clean_up()


@pytest.fixture()
def test_data_dir(request: typing.Any) -> typing.Generator:
    """Provide the test data directory associated with a given test.

    There should be a directory containing various data (most likely resource files to
    build a site) that has the same name as the test itself, without the '.py' at the
    end.
    """
    data_dir = request.module.__file__[:-3]
    assert os.path.isdir(data_dir), f"Missing data dir for test {request.node.name}."

    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copytree(data_dir, temp_dir, dirs_exist_ok=True)

        yield temp_dir
