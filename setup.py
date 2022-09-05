import setuptools

from flores import __author_email__, __author_name__, __version__, description, name

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name=name,
    version=__version__,
    author=__author_name__,
    author_email=__author_email__,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kokkonisd/saul",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        "Jinja2",
        "libsass",
        "pyyaml",
        "Markdown",
        "pymdown-extensions",
        "Pillow",
        "Pygments",
    ],
    extras_require={"test": ["nox", "pre-commit", "pytest", "pytest-cov", "requests"]},
    packages=["flores"],
    entry_points={"console_scripts": ["flores = flores.__main__:main"]},
    python_requires=">=3.8",
)
