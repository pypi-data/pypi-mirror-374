import gdsfactory as gf

from hhi import PDK, cells, tech


@gf.cell
def sample_route_bundle_rf():
    """sample route bundle with mzm.

    fixme: this should be a test

    """
    c = gf.Component()
    m1 = c << cells.HHI_MZMDU()

    p1 = c << cells.pad_GS()
    p1.rotate(90)
    p1.center = m1.ports["s2"].center
    p1.movey(2000)
    p1.movex(400)
    _ = tech.route_bundle_rf(
        c,
        [m1["s2"], m1.ports["g2"]],
        [p1.ports["e1"], p1.ports["e2"]],
        end_straight_length=20,
    )

    p2 = c << cells.pad_GS()
    p2.rotate(90)
    p2.center = m1.ports["s2"].center
    p2.movey(2000)
    p2.movex(-5000)
    _ = tech.route_bundle_rf(
        c,
        [m1["s1"], m1.ports["g1"]],
        [p2.ports["e1"], p2.ports["e2"]],
        end_straight_length=20,
        sort_ports=True,
        steps=[dict(dy=-500, dx=-2000), dict(dy=+1000)],
    )
    return c


@gf.cell
def sample_route_bundle_sbend_rf():
    """Sample route bundle with MZM."""
    c = gf.Component()
    m1 = c << cells.HHI_MZMDU()

    p1 = c << cells.pad_GS()
    p1.rotate(90)
    p1.center = m1.ports["s2"].center
    p1.movey(800)
    p1.movex(50)
    _ = tech.route_bundle_sbend_rf(
        c,
        [m1["s2"], m1.ports["g2"]],
        [p1.ports["e1"], p1.ports["e2"]],
    )
    return c


if __name__ == "__main__":
    PDK.activate()
    c = sample_route_bundle_rf()
    c.show()
