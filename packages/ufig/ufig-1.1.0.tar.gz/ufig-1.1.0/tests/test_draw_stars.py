# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Aug 06 2024


import os

import h5py
import numpy as np
from ivy import context

from ufig.plugins import draw_stars_besancon_map


def test_draw_stars_gaia_splice():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        pixscale=0.168,
        ra0=34.2148760330578,
        dec0=-5.20661157024793,
        # crpix_ra=2100.0,
        # crpix_dec=10100.0,
        nside_sampling=2048,
        size_x=4200,
        size_y=4200,
        besancon_map_path="besancon_HSC.h5",
        maps_remote_dir=os.path.join(os.path.dirname(__file__), "res"),
        reference_band="i",
        filters=["g", "r", "i", "z", "y"],
        stars_mag_min=16,
        stars_mag_max=24,
        star_catalogue_type="besancon_gaia_splice",
        filepath_gaia="gaiadr3.cat",
        seed=42,
        star_num_seed_offset=0,
        star_dist_seed_offset=0,
    )
    ctx.parameters.filepath_gaia = os.path.join(
        ctx.parameters.maps_remote_dir, ctx.parameters.filepath_gaia
    )
    plugin = draw_stars_besancon_map.Plugin(ctx)
    plugin()

    assert len(ctx.stars.x) == len(ctx.stars.y)
    assert np.all(list(ctx.stars.magnitude_dict.keys()) == ctx.parameters.filters)
    assert len(ctx.stars.magnitude_dict[ctx.parameters.reference_band]) == len(
        ctx.stars.x
    )
    mags = ctx.stars.magnitude_dict[ctx.parameters.reference_band]
    assert np.all(mags >= ctx.parameters.stars_mag_min)
    assert np.all(mags <= ctx.parameters.stars_mag_max)
    assert np.all(ctx.stars.x >= 0)
    assert np.all(ctx.stars.x < ctx.parameters.size_x)
    assert np.all(ctx.stars.y >= 0)
    assert np.all(ctx.stars.y < ctx.parameters.size_y)


def generate_besancon_map(filepath):
    with h5py.File(filepath, "w") as file:
        healpix_list_group = file.create_group("healpix_list")
        dtype = np.dtype(
            [
                ("g", np.float64),
                ("r", np.float64),
                ("i", np.float64),
                ("z", np.float64),
                ("y", np.float64),
            ]
        )

        for i in range(768):
            name = f"{i:04d}"
            if i in [403]:  # Add data only to specific indices
                data = np.random.uniform(12, 26, size=1000).astype(dtype)
                healpix_list_group.create_dataset(name, data=data)
            else:
                healpix_list_group.create_dataset(name, data=np.array([], dtype=dtype))

        healpix_mask = np.full(768, 0, dtype=np.float64)
        file.create_dataset("healpix_mask", data=healpix_mask)

        file.create_dataset("nside", data=8)
        file.create_dataset("simulation_area", data=0.4)


def test_draw_star_map():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        pixscale=0.168,
        ra0=34.2148760330578,
        dec0=-5.20661157024793,
        crpix_ra=2100.0,
        crpix_dec=10100.0,
        nside_sampling=2048,
        size_x=4200,
        size_y=4200,
        besancon_map_path="besancon_map.h5",
        star_catalogue_type="besancon_map",
        maps_remote_dir=os.getcwd(),
        filters=["g", "r", "i", "z", "y"],
        reference_band="i",
        stars_mag_min=16,
        stars_mag_max=24,
        seed=42,
        star_num_seed_offset=0,
        star_dist_seed_offset=0,
    )
    filepath = os.path.join(ctx.parameters.maps_remote_dir, "besancon_map.h5")
    generate_besancon_map(filepath)

    plugin = draw_stars_besancon_map.Plugin(ctx)
    plugin()

    assert len(ctx.stars.x) == len(ctx.stars.y)
    assert np.all(list(ctx.stars.magnitude_dict.keys()) == ctx.parameters.filters)
    assert len(ctx.stars.magnitude_dict[ctx.parameters.reference_band]) == len(
        ctx.stars.x
    )
    mags = ctx.stars.magnitude_dict[ctx.parameters.reference_band]
    assert np.all(mags >= ctx.parameters.stars_mag_min)
    assert np.all(mags <= ctx.parameters.stars_mag_max)
    assert np.all(ctx.stars.x >= 0)
    assert np.all(ctx.stars.x < ctx.parameters.size_x)
    assert np.all(ctx.stars.y >= 0)
    assert np.all(ctx.stars.y < ctx.parameters.size_y)

    os.remove(filepath)
