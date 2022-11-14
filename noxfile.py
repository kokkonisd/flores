import shutil

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
    # Install flores itself.
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


@nox.session(python=SUPPORTED_PYTHON_VERSIONS)
def docs(session: nox.Session) -> None:
    """Build the documentation."""
    # Install the standard requirements and the documentation requirements.
    # The standard requirements are needed because we are using autodoc to parse the
    # docstrings, types etc from the code, thus following imports.
    session.install("-r", "requirements.txt")
    session.install("-r", "requirements-docs.txt")
    # Build the documentation in HTML, treating warnings as errors.
    session.run("sphinx-build", "-W", "-b", "html", "docs/", "docs/_build_html/")
    # Build the documentation in LaTeX, treating warnings as errors.
    session.run("sphinx-build", "-W", "-b", "latex", "docs/", "docs/_build_pdf/")
    # Make sure the LaTeX version can be compiled to a PDF.
    # NOTE: this step assumes that `pdflatex` is installed.
    pdflatex = shutil.which("pdflatex")
    if pdflatex is None:
        session.warn(
            "`pdflatex` not found; skipping compilation to PDF for LaTeX documentation."
        )
    else:
        with session.chdir("docs/_build_pdf/"):
            session.run(
                pdflatex, "--interaction=nonstopmode", "flores.tex", external=True
            )
            session.run(pdflatex, "flores.tex", external=True)
