import nox

MAIN_PYTHON_VERSION = "3.9"
SUPPORTED_PYTHON_VERSIONS = [MAIN_PYTHON_VERSION, "3.10"]


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the testsuite."""
    # Install the runtime requirements.
    session.install("-r", "requirements.txt")
    # Install the test dependencies.
    session.install("-r", "requirements-test.txt")
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
