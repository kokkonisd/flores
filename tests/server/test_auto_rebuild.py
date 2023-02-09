import json
import os
import time

import pytest
import requests

from flores.server import Server


@pytest.mark.server_data(auto_rebuild=True)
def test_auto_rebuild_page(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing a page.

    We expect the site to be auto-rebuilt when editing a page.
    """
    expected_index_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is the index page.</p>",
            "    </body>",
            "</html>",
        ]
    )
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )

    # Modify the index page, and expect a rebuild.
    with open(
        os.path.join(flores_server.generator.pages_dir, "index.md"), "a"
    ) as index_file:
        index_file.write("\n\nHello!")

    # Wait for the rebuild.
    time.sleep(1)

    expected_index_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is the index page.</p>",
            "<p>Hello!</p>",
            "    </body>",
            "</html>",
        ]
    )
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )


@pytest.mark.server_data(auto_rebuild=True)
def test_auto_rebuild_template(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing a template.

    We expect the site to be auto-rebuilt when editing a template.
    """
    expected_index_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is the index page.</p>",
            "    </body>",
            "</html>",
        ]
    )
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )

    # Modify the index template, and expect a rebuild.
    with open(
        os.path.join(flores_server.generator.templates_dir, "main.html"), "w"
    ) as index_file:
        index_file.write("{{ page.content }}")

    # Wait for the rebuild.
    time.sleep(1)

    expected_index_content = "<p>This is the index page.</p>"
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )


@pytest.mark.server_data(auto_rebuild=True)
def test_auto_rebuild_post(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing a post.

    We expect the site to be auto-rebuilt when editing a post.
    """
    expected_post_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is a post.</p>",
            "    </body>",
            "</html>",
        ]
    )
    post_request = requests.get(
        f"http://localhost:{flores_server.port}/1970/01/01/post"
    )
    assert post_request.status_code == 200
    assert post_request.content.decode().replace("\r\n", "\n") == expected_post_content

    # Modify the post page, and expect a rebuild.
    with open(
        os.path.join(flores_server.generator.posts_dir, "1970-01-01-post.md"), "a"
    ) as post_file:
        post_file.write("\n\nHello!")

    # Wait for the rebuild.
    time.sleep(1)

    expected_post_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is a post.</p>",
            "<p>Hello!</p>",
            "    </body>",
            "</html>",
        ]
    )
    post_request = requests.get(
        f"http://localhost:{flores_server.port}/1970/01/01/post"
    )
    assert post_request.status_code == 200
    assert post_request.content.decode().replace("\r\n", "\n") == expected_post_content


@pytest.mark.server_data(auto_rebuild=True)
def test_auto_rebuild_asset(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing an asset.

    We expect the site to be auto-rebuilt when editing an asset.
    """
    expected_asset_content = "This is an asset.\n"
    asset_request = requests.get(
        f"http://localhost:{flores_server.port}/assets/hello.txt"
    )
    assert asset_request.status_code == 200
    assert (
        asset_request.content.decode().replace("\r\n", "\n") == expected_asset_content
    )

    # Modify the asset page, and expect a rebuild.
    with open(
        os.path.join(flores_server.generator.assets_dir, "hello.txt"), "w"
    ) as asset_file:
        asset_file.write("This has changed!")

    # Wait for the rebuild.
    time.sleep(1)

    expected_asset_content = "This has changed!"
    asset_request = requests.get(
        f"http://localhost:{flores_server.port}/assets/hello.txt"
    )
    assert asset_request.status_code == 200
    assert (
        asset_request.content.decode().replace("\r\n", "\n") == expected_asset_content
    )


@pytest.mark.server_data(include_drafts=True, auto_rebuild=True)
def test_auto_rebuild_draft(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing a draft.

    We expect the site to be auto-rebuilt when editing a draft.
    """
    expected_draft_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
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
    assert (
        draft_request.content.decode().replace("\r\n", "\n") == expected_draft_content
    )

    # Modify the draft page, and expect a rebuild.
    with open(
        os.path.join(flores_server.generator.drafts_dir, "1970-01-01-draft.md"), "a"
    ) as draft_file:
        draft_file.write("\n\nHello!")

    # Wait for the rebuild.
    time.sleep(1)

    expected_draft_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is a draft.</p>",
            "<p>Hello!</p>",
            "    </body>",
            "</html>",
        ]
    )
    draft_request = requests.get(
        f"http://localhost:{flores_server.port}/1970/01/01/draft"
    )
    assert draft_request.status_code == 200
    assert (
        draft_request.content.decode().replace("\r\n", "\n") == expected_draft_content
    )


@pytest.mark.server_data(auto_rebuild=True)
def test_auto_rebuild_css(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing a stylesheet file.

    We expect the site to be auto-rebuilt when editing a stylesheet file.
    """
    expected_css_content = "\n".join(
        [
            "body {",
            "    color: red;",
            "}",
            "",
        ]
    )
    css_request = requests.get(f"http://localhost:{flores_server.port}/css/main.css")
    assert css_request.status_code == 200
    assert css_request.content.decode().replace("\r\n", "\n") == expected_css_content

    # Modify the css page, and expect a rebuild.
    with open(
        os.path.join(flores_server.generator.stylesheets_dir, "main.css"), "a"
    ) as css_file:
        css_file.write("\na{background-color: yellow;}")

    # Wait for the rebuild.
    time.sleep(1)

    expected_css_content = "\n".join(
        [
            "body {",
            "    color: red;",
            "}",
            "",
            "a{background-color: yellow;}",
        ]
    )
    css_request = requests.get(f"http://localhost:{flores_server.port}/css/main.css")
    assert css_request.status_code == 200
    assert css_request.content.decode().replace("\r\n", "\n") == expected_css_content


@pytest.mark.server_data(auto_rebuild=True)
def test_auto_rebuild_js(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing a JavaScript file.

    We expect the site to be auto-rebuilt when editing a JavaScript file.
    """
    expected_js_content = 'console.log("Hello");\n'
    js_request = requests.get(f"http://localhost:{flores_server.port}/js/main.js")
    assert js_request.status_code == 200
    assert js_request.content.decode().replace("\r\n", "\n") == expected_js_content

    # Modify the js page, and expect a rebuild.
    with open(
        os.path.join(flores_server.generator.javascript_dir, "main.js"), "a"
    ) as js_file:
        js_file.write('console.log("Goodbye");')

    # Wait for the rebuild.
    time.sleep(1)

    expected_js_content = 'console.log("Hello");\nconsole.log("Goodbye");'
    js_request = requests.get(f"http://localhost:{flores_server.port}/js/main.js")
    assert js_request.status_code == 200
    assert js_request.content.decode().replace("\r\n", "\n") == expected_js_content


@pytest.mark.server_data(auto_rebuild=True)
def test_auto_rebuild_data(flores_server: Server) -> None:
    """Test the auto-rebuild feature when editing a data file.

    We expect the site to be auto-rebuilt when editing a data file.
    """
    expected_index_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is the index page.</p>",
            "    </body>",
            "</html>",
        ]
    )
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )

    # Modify the site config, and expect a rebuild.
    config = flores_server.generator.config
    config["title"] += "! Exclamation marks!!!"
    with open(
        os.path.join(flores_server.generator.data_dir, "config.json"), "w"
    ) as index_file:
        index_file.write(json.dumps(config))

    # Wait for the rebuild.
    time.sleep(1)

    expected_index_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site! Exclamation marks!!! </title>",
            "    </head>",
            "    <body>",
            "        <p>This is the index page.</p>",
            "    </body>",
            "</html>",
        ]
    )
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )


@pytest.mark.server_data(auto_rebuild=True)
def test_failed_auto_rebuild(flores_server: Server) -> None:
    """Attempt to auto-rebuild after introducing an error in a file.

    We expect the site to "go down" after a failed attempt at auto-rebuilding.
    """
    expected_index_content = "\n".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "    <head>",
            "        <title> My site </title>",
            "    </head>",
            "    <body>",
            "        <p>This is the index page.</p>",
            "    </body>",
            "</html>",
        ]
    )
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 200
    assert (
        index_request.content.decode().replace("\r\n", "\n") == expected_index_content
    )

    # Modify the index page, and expect a failed rebuild as no frontmatter is provided.
    with open(
        os.path.join(flores_server.generator.pages_dir, "index.md"), "w"
    ) as index_file:
        index_file.write("Whoops!")

    # Wait for the rebuild.
    time.sleep(1)

    # We should get a 404 when trying to reload the page, as the server has nothing to
    # serve (unsuccessful build).
    index_request = requests.get(f"http://localhost:{flores_server.port}")
    assert index_request.status_code == 404
