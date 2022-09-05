import pytest
import requests

from flores.server import Server


def test_serve_draft_without_including_drafts(flores_server: Server) -> None:
    """Attempt to access a draft while serving with include_drafts=False.

    We expect a draft page to return a 404 when serving without including drafts.
    """
    draft_request = requests.get(
        f"http://localhost:{flores_server.port}/1970/01/01/draft"
    )
    assert draft_request.status_code == 404


@pytest.mark.server_data(include_drafts=True)
def test_serve_draft_while_including_drafts(flores_server: Server) -> None:
    """Attempt to access a draft while serving with include_drafts=True.

    We expect a draft to be accessible when serving and including drafts.
    """
    expected_draft_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <p>This is a draft.</p>",
            "    </body>",
            "</html>",
        ]
    )

    draft_request = requests.get(
        f"http://localhost:{flores_server.port}/1970/01/01/draft"
    )
    assert draft_request.status_code == 200
    assert draft_request.content.decode() == expected_draft_content
