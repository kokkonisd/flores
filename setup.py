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
    project_urls={
        "Source": "https://github.com/kokkonisd/flores",
        "Documentation": "https://kokkonisd.github.io/flores",
    },
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
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
    python_requires=">=3.9",
)
