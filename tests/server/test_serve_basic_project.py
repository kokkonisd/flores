import os

import requests

from flores.server import Server


def test_serve_basic_project(flores_server: Server) -> None:
    """Test serving a basic project.

    We expect a basic project to be served correctly, and to expose certain endpoints
    (such as '/').
    """
    assert flores_server.port == Server.DEFAULT_PORT

    expected_index_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <h1>Welcome!</h1>",
            "<p>Hello world!</p>",
            "    </body>",
            "</html>",
        ]
    )

    expected_blog_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <h1>Blog</h1>",
            "<ul>",
            '<li><a href="/1970/01/01/hello">Hello everyone!</a></li>',
            "</ul>",
            "    </body>",
            "</html>",
        ]
    )

    expected_post_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <body>",
            "        <h1>Hello everyone!</h1>",
            "<p>Here's a cool image:</p>",
            '<p><img alt="Picture of the sea." src="/assets/sea.jpg"></p>',
            "    </body>",
            "</html>",
        ]
    )

    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )

    # Check that modifying the site resources will not cause the final build to change,
    # since we're not running with auto-rebuild.
    with open(
        os.path.join(flores_server.generator.pages_dir, "index.md"), "a"
    ) as index_file:
        index_file.write("\nblablabla")
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )

    blog_request = requests.get(f"http://localhost:{flores_server.port}/blog")
    assert blog_request.status_code == 200
    assert blog_request.content.decode().replace("\r\n", "\n") == expected_blog_content
    blog_request_html = requests.get(f"http://localhost:{flores_server.port}/blog.html")
    assert blog_request.content == blog_request_html.content

    post_request = requests.get(
        f"http://localhost:{flores_server.port}/1970/01/01/hello"
    )
    assert post_request.status_code == 200
    assert post_request.content.decode().replace("\r\n", "\n") == expected_post_content

    image_request = requests.get(
        f"http://localhost:{flores_server.port}/assets/sea.jpg"
    )
    assert image_request.status_code == 200

    missing_page_request = requests.get(
        f"http://localhost:{flores_server.port}/this/page/does/not/exist"
    )
    assert missing_page_request.status_code == 404
