import requests

from flores.server import Server


def test_serve_custom_404_page(flores_server: Server) -> None:
    """Test a custom 404 page.

    If a custom 404 page is provided, then it should be served instead of the default
    404 page.
    """
    expected_four_oh_four_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <p>This is a custom 404 page!</p>",
            "    </body>",
            "</html>",
        ]
    )

    four_oh_four_request = requests.get(
        f"http://localhost:{flores_server.port}/this/page/does/not/exist"
    )
    assert four_oh_four_request.status_code == 404
    assert four_oh_four_request.content.decode() == expected_four_oh_four_content
