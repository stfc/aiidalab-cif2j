# AiiDAlab CIF2J

[![Release](https://img.shields.io/github/v/release/stfc/aiidalab-cif2j)](https://github.com/stfc/aiidalab-cif2j/releases)
[![PyPI](https://img.shields.io/pypi/v/aiidalab-cif2j)](https://pypi.org/project/aiidalab-cif2j/)

[![Pipeline Status](https://github.com/stfc/aiidalab-cif2j/actions/workflows/ci-testing.yml/badge.svg?branch=main)](https://github.com/stfc/aiidalab-cif2j/actions)
[![Docs status](https://github.com/stfc/aiidalab-cif2j/actions/workflows/ci-docs.yml/badge.svg?branch=main)](https://stfc.github.io/aiidalab-cif2j/)

AiiDAlab UI app for the [aiida-cif2j](https://github.com/stfc/aiida-cif2j) workflows, maintained by the
[Ada Lovelace Centre](https://adalovelacecentre.ac.uk/) (ALC). Given a CIF/MCIF structure, the app walks
through configuring and submitting the `WannierTB2JWorkChain`: a Quantum ESPRESSO SCF/NSCF calculation,
Wannierisation via Wannier90, and a TB2J calculation of the resulting magnetic exchange interactions.

The app is in early development; input and contributions are welcome. Full documentation can be found
at [https://stfc.github.io/aiidalab-cif2j/](https://stfc.github.io/aiidalab-cif2j/).

## Usage

This plugin is hosted on the AiiDAlab plugin registry and can be installed via the AiiDAlab plugin
management UI page from within the AiiDAlab application interface. Instructions for how to run AiiDAlab
itself can be found in its [documentation](https://aiidalab.readthedocs.io/en/latest/usage/access/index.html).

Running the underlying workflow additionally requires:

- A configured AiiDA profile and computer, with codes installed for `pw.x`, `pw2wannier90.x`,
  `wannier90.x` and TB2J (see the **Setup Resources** page within the app).
- The [`aiida-cif2j`](https://github.com/stfc/aiida-cif2j) plugin, installed automatically as a
  dependency of this app.
- [`aiida-wannier90`](https://github.com/aiidateam/aiida-wannier90) and
  [`aiida-wannier90-workflows`](https://github.com/aiidateam/aiida-wannier90-workflows), neither of
  which is published on PyPI and so can't be declared as regular dependencies. They are installed
  automatically from GitHub, via `aiida-cif2j`'s own `cif2j wannier90 install` command, by this app's
  `post_install` script, which AiiDAlab runs after installing the app.

## For Developers

### Style Checking

This package uses pre-commit hooks to check for style consistency, to use these the ``pre-commit`` tool is required.
This can be installed alongside the base package by running,

``` sh
pip install .[dev]
```

or separately via,

``` sh
pip install pre-commit
```

Once installed run,

``` sh
pre-commit install
```

in the base repository to enable the pre-commit hooks.
This will now run style and formatting checks on every commit.

### Testing

This package uses [pytest](https://docs.pytest.org/en/stable/)
to run all unit tests which is included in the ```[dev]``` optional
package dependencies. Once installed it can be run from the project root directory.
The CI workflows are configured to ensure all tests pass
before a pull request can be accepted into the main repository.

``` sh
pytest --cov=aiidalab_cif2j
```

### Documentation

The documentation, including a User Guide and an API reference,
is built using [sphinx](https://www.sphinx-doc.org/). The source
for which is contained in the ```docs/``` directory. All required packages can
be installed alongside the core package via,

``` sh
pip install .[docs]
```

and then the documentation can be built using sphinx-build,

``` sh
sphinx-build -b html docs/source/ docs/build/html
```

from the root directory.

## License

[BSD 3-Clause License](LICENSE)

## Funding

Contributors to this project were funded by

<div align="center">
    <a href="https://adalovelacecentre.ac.uk/">
        <img src="images/alc.svg" alt="ALC Logo" style="width: 30%">
    </a>
</div>
