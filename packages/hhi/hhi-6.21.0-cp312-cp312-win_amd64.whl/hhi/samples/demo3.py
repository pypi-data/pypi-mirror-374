import gdsfactory as gf

from hhi import cells

if __name__ == "__main__":
    c = gf.Component("test")
    dfb = cells.HHI_DFB()
    # dfbref  = c << dfb
    bend = c << gf.components.bend_circular(cross_section="E1700")
    wgt = c << cells.HHI_WGTE200E1700()
    pd = cells.HHI_PDDC()
    # pdref   = c << pd

    ci = gf.routing.add_pads_bot(
        dfb,
        pad=cells.pad,
        cross_section="DC",
        straight_separation=30,  # doesn not default to value in pdk tech.py
        bend=gf.components.bend_circular,
    )  # the default wire corner doesn't work
    dfbref = c << ci

    cpd = gf.routing.add_pads_top(
        pd,
        pad=cells.pad,
        cross_section="DC",
        straight_separation=30,  # doesn not default to value in pdk tech.py
        bend=gf.components.bend_circular,
        optical_routing_type=2,  # we still end up with collisions
    )  # the default wire corner doesn't work
    pdref = c << cpd

    # connections
    bend.connect("o1", dfb.ports["o1"])
    wgt.connect("o2", bend.ports["o2"])
    pdref.connect("o1", wgt.ports["o1"])
    c.show()
