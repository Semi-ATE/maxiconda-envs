# maxiconda-meta

[![GitHub](https://img.shields.io/github/license/Semi-ATE/maxiconda-meta?color=black)](https://github.com/Semi-ATE/maxiconda/blob/main/LICENSE)

[![CI](https://github.com/Semi-ATE/maxiconda-meta/workflows/CI/badge.svg?branch=main)](https://github.com/Semi-ATE/maxiconda-meta/actions?query=workflow%3ACI)
[![CD](https://github.com/Semi-ATE/maxiconda-meta/workflows/CD/badge.svg)](https://github.com/Semi-ATE/maxiconda-meta/actions?query=workflow%3ACD)

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Semi-ATE/maxiconda-meta?color=blue&label=GitHub&sort=semver)](https://github.com/Semi-ATE/maxiconda-meta/releases/latest)
[![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/Semi-ATE/maxiconda-meta/latest)](https://github.com/Semi-ATE/maxiconda-meta)

[![GitHub issues](https://img.shields.io/github/issues/Semi-ATE/maxiconda-meta)](https://github.com/Semi-ATE/maxiconda-meta/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Semi-ATE/maxiconda-meta)](https://github.com/Semi-ATE/maxiconda-meta/pulls)

In this repository we maintain and release the `maxiconda` and `_spyder_` metapackages.

The contents of the metapackages can be found [here](metapackages.xlsx).

Building the packages is done here with GitHub Actions, and the released packages are uploaded to the [Semi-ATE](https://anaconda.org/Semi-ATE/) channel.

This `Semi-ATE` channel is included when installing with the [maxiconda installers](https://github.com/Semi-ATE/maxiconda).

## Usage

### maxiconda

```bash
(base) me@mybox:~$ conda create -n some_env maxiconda
````

or alternatively

```bash
(base) me@mybox:~$ mamba create -n some_env maxiconda
```

The above will create an environment with the name (-n) `some_env` and install the `maxiconda` meta package in it.

### \_spyder\_

```bash
(base) me@mybox:~$ conda create -n _spyder_ _spyder_
````

or alternatively

```bash
(base) me@mybox:~$ mamba create -n _spyder_ _spyder_
```

The above will create a [spyder](https://github.com/spyder-ide/spyder) application environment called `_spyder_` and installs the `_spyder_` metapackage in it.

### whe Semi-ATE channel is not configured

In case you don't have the Semi-ATE channel available (for example you installed with [miniforge](https://github.com/conda-forge/miniforge)) you can do this :

```
(base) me@mybox:~$ conda create -n some_env maxiconda -c Semi-ATE
```

or alternatively first add the channel like so :

```
(base) me@mybox:~$ conda config --set channel_priority strict
(base) me@mybox:~$ conda config --append channels Semi-ATE
(base) me@mybox:~$ conda create -n some_env maxiconda
```
