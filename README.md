# maxiconda-envs

[![GitHub](https://img.shields.io/github/license/Semi-ATE/maxiconda-meta?color=black)](https://github.com/Semi-ATE/maxiconda/blob/main/LICENSE)

[![Continuous Integration](https://github.com/Semi-ATE/maxiconda-envs/actions/workflows/CI.yaml/badge.svg)](https://github.com/Semi-ATE/maxiconda-envs/actions/workflows/CI.yaml)
[![Continuous Delivery](https://github.com/Semi-ATE/maxiconda-envs/actions/workflows/CD.yaml/badge.svg)](https://github.com/Semi-ATE/maxiconda-envs/actions/workflows/CD.yaml)

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Semi-ATE/maxiconda-meta?color=blue&label=GitHub&sort=semver)](https://github.com/Semi-ATE/maxiconda-meta/releases/latest)
[![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/Semi-ATE/maxiconda-meta/latest)](https://github.com/Semi-ATE/maxiconda-meta)

[![GitHub issues](https://img.shields.io/github/issues/Semi-ATE/maxiconda-meta)](https://github.com/Semi-ATE/maxiconda-meta/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Semi-ATE/maxiconda-meta)](https://github.com/Semi-ATE/maxiconda-meta/pulls)

In this repository we maintain and release the maxiconda environments. The overview of the environments and their contents can be found in the [maxiconda_envs.xlsx](https://github.com/Semi-ATE/maxiconda-envs/blob/main/maxiconda_envs.xlsx) file.

Solving the [specifications](https://github.com/Semi-ATE/maxiconda-envs/blob/main/specs.yaml) is done daily with GitHub Actions. New sollutions are commited directly to the [recipes](https://github.com/Semi-ATE/maxiconda-envs/tree/main/recipes) directory. Releases are made once so often, which will upload them to the [anaconda.org/Semi-ATE](https://anaconda.org/Semi-ATE/) channel.

This `anaconda.org/Semi-ATE` channel is included when installing with the [maxiconda installers](https://github.com/Semi-ATE/maxiconda).

## Usage

### Installing the maxiconda meta package

```bash
(base) me@mybox:~$ conda create -n some_env maxiconda
````

or alternatively

```bash
(base) me@mybox:~$ mamba create -n some_env maxiconda
```

The above will create an environment with the name (-n) `some_env` and install the `maxiconda` meta package in it.

### Installing the \_spyder\_ meta package

```bash
(base) me@mybox:~$ conda create -n _spyder_ _spyder_
````

or alternatively

```bash
(base) me@mybox:~$ mamba create -n _spyder_ _spyder_
```

The above will create a [spyder application environment](https://github.com/spyder-ide/spyder) called `_spyder_` and installs the `_spyder_` metapackage in it.

**_NOTE:_** Environments starting with an underscore ('_') are considered to be application environments, as Spyder is an application it is good practice to install it in an environment starting with an underscore.

### Whe Semi-ATE channel is not configured

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
