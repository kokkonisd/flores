# Flores

![CI](https://github.com/kokkonisd/flores/actions/workflows/ci.yaml/badge.svg?branch=main)
![codecov](https://codecov.io/gh/kokkonisd/flores/branch/main/graph/badge.svg)

Yet another static site generator.


## Motivation

Why create another static site generator when there are
[so many out there](https://jamstack.org/generators/)?

Mainly for two reasons

1. For the learning and fun of it.
2. Because most generators are very complex because they aim to be very powerful.

Flores is supposed to be as simple as possible, and yet be powerful enough to do what
most static sites need. Its basic functionality is heavily inspired by
[Jekyll](https://jekyllrb.com/).

The idea is to be able to use it on a large number of platforms (although Windows is not
yet supported!) with not a ton of dependencies or custom plugins.


## Features

For the moment, Flores supports the following features:

- Markdown-based pages and posts
- User-defined data and custom "data pages"
- Out-of-the-box image optimization
- Out-of-the-box Sass/SCSS support
- A local testing/preview server


## Documentation

You can read the latest documentation for the ``main`` branch
[here](https://kokkonisd.github.io/flores), or you can build it yourself from source:

```bash
$ python -m pip install requirements-docs.txt
$ sphinx-build -b html docs/ docs/_build/
```
