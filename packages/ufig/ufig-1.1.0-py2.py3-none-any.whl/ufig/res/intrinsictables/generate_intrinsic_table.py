"""
Created on Dec 2, 2014

@author: Claudio Bruderer
"""


from ivy import context

from ufig.plugins import gamma_interpolation_table


def test_interpolation_table():
    ctx = context.create_ctx()
    ctx.parameters = context.create_immutable_ctx(
        compute_gamma_table_onthefly=True,
        sersicprecision=9,
        gammaprecision=13,
        gammaprecisionhigh=4,
    )

    plugin = gamma_interpolation_table.Plugin(ctx)
    plugin()

    plugin.save_new_interpolation_table()


if __name__ == "__main__":
    test_interpolation_table()
