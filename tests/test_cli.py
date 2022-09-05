import os
import signal
import time

import requests

from flores.exceptions import FloresErrorCode


def test_cli_no_args(flores_cli):
    """Test a call with no arguments."""
    res = flores_cli.run()
    # Should print the help screen.
    assert res.returncode == 0


def test_cli_build(flores_cli, test_data_dir):
    """Test a simple call to `build`."""
    res = flores_cli.run("build", test_data_dir)
    assert res.returncode == 0
    assert os.path.isdir(os.path.join(test_data_dir, "_site"))


def test_cli_build_and_clean(flores_cli, test_data_dir):
    """Test a call to `build` followed by a call to `clean`."""
    res = flores_cli.run("build", test_data_dir)
    assert res.returncode == 0
    assert os.path.isdir(os.path.join(test_data_dir, "_site"))

    res = flores_cli.run("clean", test_data_dir)
    assert res.returncode == 0
    assert not os.path.isdir(os.path.join(test_data_dir, "_site"))


def test_cli_serve(flores_cli, test_data_dir):
    """Test a call to `serve` with a custom port."""
    server = flores_cli.runserver(test_data_dir, "-p", "8000")

    # Wait for the server to start.
    time.sleep(0.5)

    index_request = requests.get("http://localhost:8000")
    assert index_request.status_code == 200

    server.send_signal(signal.SIGINT)
    server.wait()
    assert server.returncode == 0


def test_cli_build_invalid_project_dir(flores_cli, test_data_dir):
    """Test a call to build with an invalid directory."""
    bogus_dir = os.path.join("this", "dir", "does", "not", "exist")
    res = flores_cli.run("build", bogus_dir)
    assert res.returncode == FloresErrorCode.FILE_OR_DIR_NOT_FOUND.value
    assert f"Invalid project directory: '{bogus_dir}'." in res.stderr


def test_cli_run_double_server(flores_cli, test_data_dir):
    """Test a double call to `serve` with overlapping ports."""
    server1 = flores_cli.runserver(test_data_dir, "-p", "8000")
    # Wait for the first server to start.
    time.sleep(0.5)

    server2 = flores_cli.runserver(test_data_dir, "-p", "8000")
    # Wait for the second server to start.
    time.sleep(0.5)

    # A server should be up.
    index_request = requests.get("http://localhost:8000")
    assert index_request.status_code == 200

    # The second server should have failed to start.
    server2.wait()
    assert (
        "Address `http://localhost:8000` is already in use; is another server running?"
        in server2.stderr.read().decode()
    )

    server1.send_signal(signal.SIGINT)
    server1.wait()
    assert server1.returncode == 0
