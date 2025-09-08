[![PyPI](https://img.shields.io/pypi/v/nipreps_versions)](https://pypi.org/project/nipreps-versions/)
[![Tox](https://github.com/nipreps/version-schemes/actions/workflows/tox.yml/badge.svg)](https://github.com/nipreps/version-schemes/actions/workflows/tox.yml)

# Nipreps version schemes

This package provides a `setuptools_scm` plugin for version schemes used
by the Nipreps family of projects.

## Usage

Add `nipreps_versions` to your `build-system.requires` list, e.g.,

```TOML
[build-system]
requires = [
    "flit_scm",
    "nipreps_versions",
]
build-backend = "flit_scm:buildapi"
```

or

```TOML
[build-system]
requires = [
    "setuptools",
    "setuptools_scm",
    "nipreps_versions",
]
build-backend = "setuptools.build_meta"
```

Then request a nipreps version scheme:

```TOML
[tool.setuptools_scm]
version_scheme = "nipreps-calver"
```

## Schemes

Currently, only one versioning scheme is implemented:

### `nipreps-calver`

As described in [Releases - Principles](https://www.nipreps.org/devs/releases/#principles),

> The basic release form is `YY.MINOR.PATCH`, so the first minor release of 2020 is 20.0.0, and the first minor release of 2021 will be 21.0.0, whatever the final minor release of 2020 is. A series of releases share a `YY.MINOR`. prefix, which we refer to as the `YY.MINOR.x` series. For example, the 20.0.x series contains version 20.0.0, 20.0.1, and any other releases needed.

If the last tag was 22.1.0 and the year remains 2022, the development version is
`22.2.0.devN`. When the year changes to 2023, the development version will become
`23.0.0.devN`.
If the branch is `maint/22.1.x`, then the computed version will be `22.1.1.devN`.
If the branch is `rel/22.0.3` (and the last tag for that branch is 22.0.2), then
the computed version will be `22.0.3.devN`.
