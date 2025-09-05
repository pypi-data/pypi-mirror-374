# Ultra Fast Image Generator (UFig)

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ufig.svg)](https://pypi.python.org/pypi/ufig/)
[![PyPI version](https://badge.fury.io/py/ufig.svg)](https://badge.fury.io/py/ufig)
[![pipeline](https://gitlab.com/cosmology-ethz/ufig/badges/main/pipeline.svg)](https://gitlab.com/cosmology-ethz/ufig/-/pipelines)
[![coverage](https://gitlab.com/cosmology-ethz/ufig/badges/main/coverage.svg)](https://gitlab.com/cosmology-ethz/ufig)
<a href="https://cosmo-docs.phys.ethz.ch/ufig/htmlcov/index.html">
  <img src="https://img.shields.io/badge/coverage_report-green"
    alt="coverage report"/>
</a>

[![image](https://img.shields.io/badge/arXiv-1209.1200-B31B1B.svg?logo=arxiv&style=flat)](https://arxiv.org/abs/1209.1200)
[![image](https://img.shields.io/badge/arXiv-2412.08716-B31B1B.svg?logo=arxiv&style=flat)](https://arxiv.org/abs/2412.08716)
[![Docs](https://badgen.net/badge/icon/Documentation?icon=https://cdn.jsdelivr.net/npm/simple-icons@v13/icons/gitbook.svg&label)](https://cosmo-docs.phys.ethz.ch/ufig/)
[![Source Code](https://badgen.net/badge/icon/Source%20Code?icon=gitlab&label)](https://gitlab.com/cosmology-ethz/ufig)

Simulate realistic astronomical images with high-speed and modular adjustable image properties according to the user.

For the original paper describing this project, see: [Bergé et al. (2013)](http://arxiv.org/abs/1209.1200).
The first public release of UFig is descibed in [Fischbacher et al. (2024)](https://arxiv.org/abs/2412.08716).

## Installation

To install the latest release from PyPI, use pip:

```bash
pip install ufig
```

## Features

- Ultra fast speed
- Modular structure that can be easily integrated and expanded
- User interacts with the program through Python scripts
- Structured unit tests for continuous robust development

Note: For not supported features, see the plugins (including the deprecated ones)
in the archive branch (https://gitlab.com/cosmology-ethz/ufig/-/tree/old_master_before_11_2024).

## Introduction

The **Ultra Fast Image Generator (UFig)** is an image simulation tool that generates simulated astronomical images for scientific usage.

The code is implemented in pure Python and highly optimized in terms of speed.

The output images are useful for developing analysis algorithms and data processing pipelines in the field of astronomy/cosmology.

Conceptually, a typical UFig program involves two things:

1. **Config file:** sets up the workflow by calling a series of plugins.

   The content in each config file includes importing or setting the relevant input parameters and arranging the list of plugins that are being called. The main set of common parameters are listed in the "common" module at `ufig.config.common`. Examples of config files can be found also be found in the documentation.

2. **Plugin:** implement specific jobs.

   The nature of the plugins ranges from mundane data handling (e.g., I/O of data files), PSF estimation and background addition to rendering and processing the images. The plugins are stored in `ufig.plugins` and can be easily extended by the user.


## Credits
This package was developped by the Cosmology group at ETH Zurich and is currently
maintained by Silvan Fischbacher: silvanf@phys.ethz.ch

## Contributions
Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.
