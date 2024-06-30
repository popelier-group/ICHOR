# ichor
---

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Run Tests](https://github.com/popelier-group/ICHOR/actions/workflows/run_tests.yml/badge.svg)](https://github.com/popelier-group/ICHOR/actions/workflows/run_tests.yml)
![Release](https://img.shields.io/github/v/release/popelier-group/ICHOR?sort=semver)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/ichor/badge/?version=latest)](https://ichor.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11182102.svg)](https://doi.org/10.5281/zenodo.11182102)

`ichor` is a Python package used to simplify data management from computational chemistry programs and aid with machine learning force field development. If you would like to request missing features or run into a bug, don't hesitate to create an [issue](https://github.com/popelier-group/ICHOR/issues).

Here is a list of things that the package is intended to do:

1. provide interfaces to any computational chemistry software to allow for easy switching between similar software and results comparison.
2. implement flexible data structures to allow for data management of hundreds of thousands of calculations from multiple programs.
3. integrate common database formats for efficient data storage, sharing, and post-processing
4. provide interfaces to workload managers on compute clusters to automate job submission
5. collate tools for machine learning dataset and model analysis, as well as molecular dynamics simulation benchmarking

Realistically, the file management portion of `ichor` (as well as the workload manager integration) is very general, so it can be used for any type of data that might not even be computational chemistry related. However, the focus of the source code itself is on computational chemistry and machine learning force field development.

## Getting Started
---
The namespace package `ichor` is divided into three parts, `ichor.core`, `ichor.hpc`, and `ichor.cli`.

### `ichor.core`
The `ichor.core` package contains classes and functions which make it easy to handle a very large number of files, perform many calculations with the outputs contained in the file, as well as aid with machine learning force field development.

### `ichor.hpc`
The `ichor.hpc` package is used to submit jobs on compute clusters (SGE/SLURM).

### `ichor.cli`
The `ichor.cli` package provides a simple to use command line interface (CLI), providing an easy access to access the most commonly used tools from ichor.

**You will need to have an `ichor_config.yaml` file in your home directory for configuration settings relating to HPC clusters, refer to the documentation for examples. An example `ichor_config.yaml` is provided in the repository.**

## Papers

The working paper for `ichor` can be found [here](https://doi.org/10.26434/chemrxiv-2024-f8h7n).

## Documentation

Documentation of all three packages, including examples, can be found [here](https://ichor.readthedocs.io/en/latest/).

## Contributing

Contributions are very welcome! More information on how to correctly contribute can be found in the [CONTRIBUTING.md](CONTRIBUTING.md) file.
