import os
import signal
import tempfile
import time

import requests

from flores.exceptions import FloresErrorCode

# We can ignore the I900 error here, this is purely to make mypy happy.
from tests.conftest import FloresCLI  # noqa: I900


def test_cli_no_args(flores_cli: FloresCLI) -> None:
    """Test a call with no arguments."""
    res = flores_cli.run()
    # Should print the help screen.
    assert res.returncode == 0


def test_cli_init(flores_cli: FloresCLI) -> None:
    """Test the `init` command to initialize a basic site."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = os.path.join(temp_dir, "my_site")
        res = flores_cli.run("init", project_dir)
        assert res.returncode == 0

        expected_elements = [
            os.path.join(project_dir, "_data"),
            os.path.join(project_dir, "_data", "config.json"),
            os.path.join(project_dir, "_pages"),
            os.path.join(project_dir, "_pages", "index.md"),
            os.path.join(project_dir, "_templates"),
            os.path.join(project_dir, "_templates", "main.html"),
        ]

        actual_elements = []
        for dirpath, dirnames, filenames in os.walk(project_dir):
            for element in dirnames + filenames:
                actual_elements.append(os.path.join(dirpath, element))

        assert sorted(actual_elements) == sorted(expected_elements)

        # Attempt to build site, to make sure it works.
        res = flores_cli.run("build", project_dir)
        assert res.returncode == 0


def test_cli_init_force(flores_cli: FloresCLI) -> None:
    """Test the `init` command with the `--force` switch."""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = temp_dir
        # Create some files to make sure that `init` won't clear what is already there.
        with open(os.path.join(temp_dir, "existing.txt"), "w") as existing_file:
            existing_file.write("hello")

        res = flores_cli.run("init", "--force", project_dir)
        assert res.returncode == 0

        expected_elements = [
            os.path.join(project_dir, "existing.txt"),
            os.path.join(project_dir, "_data"),
            os.path.join(project_dir, "_data", "config.json"),
            os.path.join(project_dir, "_pages"),
            os.path.join(project_dir, "_pages", "index.md"),
            os.path.join(project_dir, "_templates"),
            os.path.join(project_dir, "_templates", "main.html"),
        ]

        actual_elements = []
        for dirpath, dirnames, filenames in os.walk(project_dir):
            for element in dirnames + filenames:
                actual_elements.append(os.path.join(dirpath, element))

        assert sorted(actual_elements) == sorted(expected_elements)

        # Attempt to build site, to make sure it works.
        res = flores_cli.run("build", project_dir)
        assert res.returncode == 0


def test_cli_init_existing_dir(flores_cli: FloresCLI, test_data_dir: str) -> None:
    """When attempting to call `init` on a non-empty dir, it should fail."""
    res = flores_cli.run("init", test_data_dir)
    assert res.returncode == FloresErrorCode.FILE_OR_DIR_NOT_FOUND.value
    assert f"Cannot initialize: '{test_data_dir}' already exists." in res.stderr


def test_cli_build(flores_cli: FloresCLI, test_data_dir: str) -> None:
    """Test a simple call to `build`."""
    res = flores_cli.run("build", test_data_dir)
    assert res.returncode == 0
    assert os.path.isdir(os.path.join(test_data_dir, "_site"))


def test_cli_build_and_clean(flores_cli: FloresCLI, test_data_dir: str) -> None:
    """Test a call to `build` followed by a call to `clean`."""
    res = flores_cli.run("build", test_data_dir)
    assert res.returncode == 0
    assert os.path.isdir(os.path.join(test_data_dir, "_site"))

    res = flores_cli.run("clean", test_data_dir)
    assert res.returncode == 0
    assert not os.path.isdir(os.path.join(test_data_dir, "_site"))


def test_cli_serve(flores_cli: FloresCLI, test_data_dir: str) -> None:
    """Test a call to `serve` with a custom port."""
    server = flores_cli.runserver(test_data_dir, "-p", "8000")

    # Wait for the server to start.
    time.sleep(1)

    index_request = requests.get("http://localhost:8000")
    assert index_request.status_code == 200

    server.send_signal(signal.SIGINT)
    server.wait()
    assert server.returncode == 0


def test_cli_build_invalid_project_dir(
    flores_cli: FloresCLI, test_data_dir: str
) -> None:
    """Test a call to build with an invalid directory."""
    bogus_dir = os.path.join("this", "dir", "does", "not", "exist")
    res = flores_cli.run("build", bogus_dir)
    assert res.returncode == FloresErrorCode.FILE_OR_DIR_NOT_FOUND.value
    assert f"Invalid project directory: '{bogus_dir}'." in res.stderr


def test_cli_run_double_server(flores_cli: FloresCLI, test_data_dir: str) -> None:
    """Test a double call to `serve` with overlapping ports."""
    server1 = flores_cli.runserver(test_data_dir, "-p", "8000")
    # Wait for the first server to start.
    time.sleep(1)

    server2 = flores_cli.runserver(test_data_dir, "-p", "8000")
    # Wait for the second server to start.
    time.sleep(1)

    # A server should be up.
    index_request = requests.get("http://localhost:8000")
    assert index_request.status_code == 200

    # The second server should have failed to start.
    server2.wait()
    assert (
        "Address `http://localhost:8000` is already in use; is another server running?"
        in server2.stderr.read().decode()  # type: ignore
    )

    server1.send_signal(signal.SIGINT)
    server1.wait()
    assert server1.returncode == 0
