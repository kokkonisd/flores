import nox

TEST_DEPS = [
    ("pytest", "7.1.2"),
    ("pytest-cov", "3.0.0"),
    ("requests", "2.28.1"),
]


MAIN_PYTHON_VERSION = "3.9"
SUPPORTED_PYTHON_VERSIONS = ["3.8", MAIN_PYTHON_VERSION, "3.10"]


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the testsuite."""
    # Install the runtime requirements.
    session.install("-r", "requirements.txt")
    # Install the test dependencies.
    for dep, version in TEST_DEPS:
        session.install(f"{dep}=={version}")
    # Install saul itself.
    session.install("-e", ".")

    # Run the testsuite & coverage report.
    session.run(
        "pytest",
        "-vv",
        "--cov=flores",
        "--no-cov-on-fail",
        "--cov-fail-under=100",
        "--cov-report=term-missing",
        "--cov-report=xml",
    )


@nox.session(python=MAIN_PYTHON_VERSION)
def lint(session: nox.Session) -> None:
    """Run the linters."""
    # Install the developer requirements.
    session.install("-r", "requirements-dev.txt")
    # Run pre-commit.
    session.run("pre-commit", "run", "--all-files")
