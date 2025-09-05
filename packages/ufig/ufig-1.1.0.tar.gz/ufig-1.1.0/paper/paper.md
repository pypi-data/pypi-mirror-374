---
title: '`UFig v1`: The ultra-fast image generator'
tags:
  - Python
  - astronomical images
  - cosmology
  - GalSBI
authors:
  - name: Silvan Fischbacher
    orcid: 0000-0003-3799-4451
    affiliation: 1
    equal-contrib: true
  - name: Beatrice Moser
    orcid: 0000-0001-9864-3124
    affiliation: 1
    equal-contrib: true
  - name: Tomasz Kacprzak
    orcid: 0000-0001-5570-7503
    affiliation: "1, 2"
    equal-contrib: true
  - name: Luca Tortorelli
    affiliation: "1, 3"
    equal-contrib: true
    orcid: 0000-0002-8012-7495
  - name: Joerg Herbel
    affiliation: 1
    equal-contrib: true
  - name: Claudio Bruderer
    affiliation: 1
    equal-contrib: true
  - name: Uwe Schmitt
    affiliation: "1, 4"
    orcid: 0000-0002-4658-0616
  - name: Alexandre Refregier
    orcid: 0000-0003-3416-9317
    affiliation: 1
  - name: Joel Berge
    orcid: 0000-0002-7493-7504
    affiliation: "1, 5"
  - name: Lukas Gamper
    affiliation: 1
  - name: Adam Amara
    affiliation: "1,6"
    orcid: 0000-0003-3481-3491

affiliations:
 - name: ETH Zurich, Institute for Particle Physics and Astrophysics, Wolfgang-Pauli-Strasse 27, 8093 Zurich, Switzerland
   index: 1
 - name: Swiss Data Science Center, Paul Scherrer Institute, Forschungsstrasse 111, 5232 Villigen, Switzerland
   index: 2
 - name: University Observatory, Faculty of Physics, Ludwig-Maximilian-Universität München, Scheinerstrasse 1, 81679 Munich, Germany
   index: 3
 - name: ETH Zurich, Scientific IT Services, Binzmühlestrasse 130, 8092 Zürich, Switzerland
   index: 4
 - name: DPHY, ONERA, Université Paris Saclay, F-92322 Châtillon, France
   index: 5
 - name: School of Mathematics and Physics, University of Surrey, Guildford, Surrey, GU2 7XH, UK
   index: 6

date: XXXX-XX-XX
bibliography: paper.bib
---

# Summary

With the rise of simulation-based inference (SBI) methods (see e.g. @sbi_review),
simulations need to be fast as well as realistic.
`UFig v1` is a public Python package that generates simulated astronomical images with
exceptional speed - taking approximately the same time as source extraction.
This makes it particularly well-suited for simulation-based inference (SBI) methods
where computational efficiency is crucial.
To render an image, `UFig` requires a galaxy catalog, and a description of the point
spread function (PSF).
It can also add background noise, sample stars using the Besançon model of the Milky
Way [@besancon], and run `SExtractor` [@sextractor] to extract sources from the rendered image.
The extracted sources can be matched to the intrinsic catalog using the method described
in @moser, flagged based on `SExtractor` output and survey masks, emulators can be used
to bypass the image simulation and extraction steps [@fischbacher].
A first version of `UFig` was presented in @ufig and the software has since been used
and further developed in a variety of forward modelling applications
[@chang;@bruderer;@herbel;@kacprzak;@tortorelli1;@tortorelli2;@moser;@fischbacher].

# Statement of need

`UFig` is a crucial part of the GalSBI framework.
GalSBI is a galaxy population model that is used to generate mock galaxy catalogs for
all kinds of cosmological applications such as photometric redshift estimation, shear
and blending calibration or to forward model selection effects and measure galaxy
population properties.
Constraining this model is done by comparing simulated data to observed data.
To accurately compare the simulations with the data, the simulations need to be as
realistic as possible.
We therefore need to include instrumental and observational effects such as the PSF and
the background noise of the data, as well as the survey masks.
This can be done by rendering images from the intrinsic GalSBI catalogs and extracting
the sources from the images with the same method as for the data.

Since the dimensionality of the parameter space of the galaxy population model is high
(around 50 parameters) and the numbers of simulations required to constrain the model
is hence large, a fast image generator is crucial to make the inference feasible.
`UFig`'s rendering implementation is based on a combination of pixel-based and
photon-based rendering methods (see @ufig for more details).
This hybrid approach is one of the key factors behind `UFig`'s fast rendering speed,
which is roughly comparable to the time required for source extraction from the images.
For the simulations of the Hyper-Suprime-Cam (HSC, @hsc) deep fields
presented in @moser and @fischbacher, the rendering time is between 5 and 10 seconds
for a typical image on a single CPU core.

`UFig` is optimized for wide-field galaxy surveys, where saturated bright objects or
artifacts are typically masked, and detailed galaxy morphology (e.g., spiral structures)
is not critical.
As a result, the software includes only a simplified treatment of saturation,
does not simulate artifacts such as cosmic rays, and models galaxy light profiles using
Sérsic profiles.

At the same time, `UFig` is capable of accurately modelling background noise, including
correlated noise from the coaddition process, and the point-spread function (PSF).
This is essential for applying `UFig` to galaxy surveys, such as weak lensing, where
precise shape measurements are required.
This balance makes `UFig` unique in the field of image simulation compared to other
software packages, such as `GalSim` [@galsim] and `GalSim`-based packages like
`ImSim` [@imsim] and the GREAT3 simulations [@great3], as well as `PhoSim` [@phosim],
`Skymaker` [@skymaker], and other GREAT challenge simulations [@great8;@great10].
To flexibly adapt to different use cases, `UFig` is based on the `ivy` workflow engine
and provides plugins for the different steps of the image generation process.
The full workflow can then be defined in a single configuration file, where the user
can specify which plugins to use and how to configure them, e.g. by defining the PSF
or background model, making the image generation process flexible and easy to use.
Examples of configuration files can be found in the Advanced UFig tutorial in the
`UFig` documentation.

Compared to the first version of `UFig` presented in @ufig, new features and
improvements have been added.
In @chang, `UFig` was used to model the transfer function of images of the Dark Energy
Survey (DES, @des) from intrinsic galaxy catalogs to measured properties.
@bruderer used `UFig` to render DES-like images for which the PSF modeling and the
background noise were adapted to the DES data.
Furthermore, to ensure a realistic distributions of the stars in the images, a plugin
to sample stars from the Besançon model of the Milky Way [@besancon] was added, see
also @bruderer_phd for an comprehensive overview of the `UFig` features at that time.
@herbel constrained a galaxy population model using `UFig`.
This galaxy population model was then used to measure cosmic shear in @kacprzak.
This effort required major improvements in the background and PSF modelling.
The PSF modelling based on a convolutional neural network (CNN) was first presented in
@herbel_psf.
@tortorelli3 and @tortorelli2 adapted `UFig` to render images for narrow-band filters
in the context of the Physics of the Accelerating Universe (PAU, [@pau1;@pau2]) Survey.
@moser used `UFig` to simulate deep fields of the Hyper Suprime-Cam (HSC) which
required further adaptions for the PSF modelling and the matching of the extracted
sources to the input catalog.
Finally, @fischbacher introduced emulators to bypass the image simulation and
extraction steps.

A possible workflow using `UFig` could be the following:

1. Define an intrinsic galaxy catalog. An easy way to do this is to use the GalSBI
galaxy population model and its catalog generator @galsbi.
However, the catalog can also be generated manually without using the GalSBI model.

2. Sample stars from the Besançon model with the `UFig` plugin.

3. Add observational effects such as the PSF, background noise or saturation with the
corresponding `UFig` plugins.

4. Obtain the measured catalog, either by rendering the image, running `SExtractor`,
matching the extracted sources to the intrinsic catalog and flagging the sources based
on the `SExtractor` output and survey masks, or by using emulators to bypass the image
simulation and extraction steps.

5. Save the measured catalog and/or the rendered image.

Apart from the first step, all steps can be done with `UFig` plugins.

# `UFig` images and catalogs

![Rendered image with three galaxies (a large object at bottom center, an elliptical one at upper-left below a star, and a fuzzier one at upper-right) and three bright stars (round and bright at center-left, center-right, and upper-left). The PSF size varies with different seeing conditions and no background noise is added.\label{fig:psfonly}](figures/psf_variations.png)

In the simplest case, `UFig` can render an image with a few predefined galaxies and
stars without background noise.
An example of such a rendered image is shown in \autoref{fig:psfonly}.
From left to right, you see the same objects with different seeing conditions, which
change the size of the PSF.
The PSF is modelled as a mixture of one or two Moffat profiles $I_i(r)$ given by
\begin{equation}
    \begin{aligned}
        I_i(r) &= I_{0,i}\left(1 + \left(\frac{r}{\alpha_i}\right)^2\right)^{-\beta_i},
    \end{aligned}
\end{equation}
with a constant base profile across the image.
The ratio of $I_{0,1}$ and $I_{0,2}$ is a free parameter (in the case of a two-component
Moffat) and the sum of the two profiles is determined by the number of photons of the
object.
The $\beta_i$ parameter is free and $\alpha_i$ is chosen such that the half light radius
of the profile is one pixel.
This base profile is then distorted at each position of an object by three
transformations accounting for the size of the PSF, the shape of the PSF (ellipticity,
skewness, triangularity and kurtosity) and the position of the PSF, see @herbel_psf
for more details.
These distortions can be passed as a constant value across the image, as a map with
varying values for each pixel or estimated using the CNN presented in @herbel_psf.
Additionally, an approximated brighter-fatter effect can be included by using a
first-order linear correction that scales the PSF size and ellipticity components
based on the source magnitude relative to a reference magnitude.


\autoref{fig:bkg} shows the same image as in \autoref{fig:psfonly} but with added
background noise.
Background noise can be added as a Gaussian with constant mean and standard deviation
across the image or as a map with varying mean and standard deviation for each pixel.
Correlated noise is introduced by Lanczos resampling.

![Rendered image with three galaxies (a large object at bottom center, an elliptical one at upper-left below a star, and a fuzzier one at upper-right) and three bright stars (round and bright at center-left, center-right, and upper-left). The PSF size is constant PSF and the background level is varied. The left panel shows an image with low background noise, the middle panel higher noise and the right panel shows an image where each quarter has a different background noise.\label{fig:bkg}](figures/bkg_variations.png)

Creating a more realistic galaxy catalog can be done by using the GalSBI galaxy
population model and the corresponding galaxy sampling plugins of the ``galsbi`` Python
package [@galsbi].
An example of rendered images for different bands with galaxies sampled from the GalSBI
model presented in @fischbacher is shown in \autoref{fig:galsbi}.

![Rendered images with galaxies sampled from the GalSBI model for different bands. Background level and PSF estimation correspond to a typical HSC deep field image.\label{fig:galsbi}](figures/galsbi.png)

`UFig` also includes plugins to extract sources from the rendered images using `SExtractor` [@sextractor], where the user can specify the `SExtractor` configuration file.
This saves the detected objects in a catalog.
\autoref{fig:sextractor} shows an example of the extracted sources from a rendered image.
Stars have a constant size corresponding to the PSF size and ellipticities close to
zero as expected for a point source whereas galaxies have broader distributions of sizes
and ellipticities.

![Catalog of sources extracted from a rendered image using `SExtractor`.The apparent
magnitude (`MAG_AUTO`), angular size in pixel (`FLUX_RADIUS`) and the absolute
ellipticity (`ELLIPTICITY`) are shown. All objects in the image are shown in blue, stars
are shown in red.
\label{fig:sextractor}](figures/catalog.png)

# Acknowledgments

This project was supported in part by grant 200021_143906, 200021_169130 and
200021_192243 from the Swiss National Science Foundation.

We acknowledge the use of the following software packages:
`numpy` [@numpy], `scipy` [@scipy], `astropy` [@astropy], `healpy` [@healpy],
`numba` [@numba], `edelweiss` [@fischbacher], `scikit-learn` [@scikit-learn].
For the plots in this paper and the documentation, we used `matplotlib` [@matplotlib],
and `trianglechain` [@trianglechain1;@trianglechain2].
The authors with equal contribution are listed in inverse order of their main
contribution.

# References
