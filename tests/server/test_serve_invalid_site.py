from typing import Any

import pytest

from flores.server import Server


def test_serve_invalid_site(test_data_dir: str, capsys: Any) -> None:
    """Test serving an invalid site.

    We expect an invalid site (i.e. a site leading to a build error) to make the server
    exit immediately, as there is no point in attempting to serve a site that will not
    build.
    """
    server = Server(project_dir=test_data_dir)

    with pytest.raises(SystemExit):
        server.serve()

    captured = capsys.readouterr()
    assert "Failed to build site; nothing to serve." in captured.err
