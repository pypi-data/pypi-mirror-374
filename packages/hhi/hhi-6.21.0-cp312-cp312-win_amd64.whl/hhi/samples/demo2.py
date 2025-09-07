from functools import partial

import gdsfactory as gf

from hhi import PDK, cells
from hhi.cells import pad

if __name__ == "__main__":
    PDK.activate()
    # c = cells.HHI_DirCoup(L_C=100)
    c = cells.HHI_WGMETxE1700GSGsingle()
    # c = gf.routing.add_pads_top(
    #     c,
    #     pad=pad,
    #     pad_pitch=150,
    #     optical_routing_type=0,
    # )

    p = partial(gf.c.pad, size=(100, 100))

    cc = gf.routing.add_pads_top(
        c,
        # width=16,
        cross_section="DC",
        straight_separation=36,
        pad_pitch=150,
        pad=pad,
        bend=gf.components.bend_circular,
    )
    cc.show()
