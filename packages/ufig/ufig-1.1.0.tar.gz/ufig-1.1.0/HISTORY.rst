.. :changelog:

History
-------

1.1.0 (2025-09-04)
++++++++++++++++++

* **New feature**: added PSF estimation using pretrained CNN
* compatibility with numpy 2+
* improved documentation

1.0.0 (2024-12-13)
++++++++++++++++++

* First release on PyPI.

0.2.1 (2016-06-16)
++++++++++++++++++

* Support of the generation of images in multiple bands with the config file multi_band_variable_systematics
* All functionalities concerning the rendering of single-band images released in previous versions are not affected by this
* For multi-band rendering: galaxy number counts are obtained from a luminosity function
* For multi-band rendering: galaxy redshifts and absolute magnitudes are sampled from luminosity function
* For multi-band rendering: galaxy spectra are sampled using template spectra and a distribution of template coefficients
* For multi-band rendering: apparent galaxy magnitudes can be calculated in multiple filter bands
* For multi-band rendering: extinction is taken into account
* For multi-band rendering: star number counts and magnitudes from Besancon model of Milky Way
* New way of reading in Healpix maps using astropy.io.fits instead of healpy.read_map to avoid dtype conversions and lower memory footprint


0.2.0 (2016-05-31)
++++++++++++++++++

* Support of two core config files: constant_systematics and variable_systematics
* Update the io_util to handle absolute paths for file names
* Rendering using noise maps is more memory efficient
* Support for variable shear, exposure time, and background maps
* Improved test coverage; especially testing the rendered galaxy and star profiles to 1e-4 precision
* Add correct scatter when converting a magnitude to a number of photons
* Functionalities to read in a catalog
* Module to more realistically handle sky subtraction as performed on real images


0.1.1 (2014-07-16)
++++++++++++++++++

* Based on Ivy
* Improved test coverage
* Improved documentation
* Fixed x-y problem
* Fix image size bug
* Sextractor support

0.1.0 (2014-02-13)
++++++++++++++++++

* First release.
