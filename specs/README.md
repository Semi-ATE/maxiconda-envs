# maxiconda-envs/specs

The `matrix.yaml` and `primary_packages.yaml` files are maintained by/in this repository, but the `solutions` directory is maintained (automatically and daily) through the maxiconda-bot repository.

## matrix.yaml

This file maintains and defines the name for supported Operating Systems, Processors an Python versions.

Note: both the CPython and the PyPy version (if available) will be installed next to eachother.

## primary_packages.yaml

In this file we define the environments and the **primary packages** that make up the environment.

In order for the `maxiconda` installer to function propperly, there should be **AT LEAST** the following environments:
- base : A lean-mean-fighting-machine environment that is **NOT** used as a development environment.
- \_spyder\_ : The `spyder` application environment.
- maxiconda : An environment that suit most average use-cases. 

Next to those we can define a number of other environments that focus on specific tasks. 

