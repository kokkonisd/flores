# Changelog

This file tracks changes between different releases.


## 0.1.2

- Fix generator/server not handling Sass/SCSS compilation errors ([#11][i11])
- Fix server not rebuilding in auto-rebuild mode when a template include file was
  modified ([#10][i10])
- Revisit the datetime definitions in the posts: now, there is no need to redefine the
  entire date string, you can just incrementally define the time & timezone of the post
  ([#8][i8])
- Implement `-a/--address` switch for the server to allow it to bind to addresses other
  than `localhost` ([#12][i12])
- Implement `-f/--force` switch for the `flores init` subcommand, to allow it to
  continue if the project directory already exists ([#9][i9])
- Bump Pillow & Pygments to newer versions


## 0.1.1

- Fix errors in `setup.py`
- Fix errors in the documentation


## 0.1.0

First (not-stable-yet) release of Flores.


[i8]: https://github.com/kokkonisd/flores/issues/8
[i9]: https://github.com/kokkonisd/flores/issues/9
[i10]: https://github.com/kokkonisd/flores/issues/10
[i11]: https://github.com/kokkonisd/flores/issues/11
[i12]: https://github.com/kokkonisd/flores/issues/12
