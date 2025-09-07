"""Custom cells not included in the HHI standard PDK."""

import gdsfactory as gf

from hhi import cells, tech
from hhi.cells import die_rf
from hhi.samples.components import JonnysDevice


@gf.cell
def MZMsection(N=10) -> gf.Component:
    """Define a Twin MZM section without MMIs."""
    C = gf.Component()

    # Add the BBs
    mzm_mid = C << cells.HHI_EOPMTWTwinDD(N=N)
    mzm_r50 = C << cells.HHI_EOPMTermination()

    # Connections
    mzm_mid.mirror_x()
    mzm_r50.connect("s1", mzm_mid.ports["g1"])

    # Helper function to replace the port names
    def replace_inplace(port, x, y):
        port.name = port.name.replace(x, y)
        return port

    # Ground ports
    C.add_ports([p for p in mzm_mid.ports if p.name.startswith("n")], prefix="left_")
    C.add_ports([p for p in mzm_mid.ports if p.name.startswith("n")], prefix="right_")
    C.auto_rename_ports()
    C.auto_rename_ports(lambda ports: [replace_inplace(p, "e", "n") for p in ports])

    # Optical ports
    C.add_ports(
        [p for p in mzm_mid.ports if p.name.startswith("o") and p.orientation == 180],
        prefix="left_",
    )
    C.add_ports(
        [p for p in mzm_mid.ports if p.name.startswith("o") and p.orientation == 0],
        prefix="right_",
    )
    C.auto_rename_ports(
        lambda ports: C.kcl.rename_function(
            [p for p in ports if p.port_type == "optical"]
        )
    )
    # RF ports
    C.add_ports([mzm_mid.ports["g1"], mzm_mid.ports["s1"]])
    return C


@gf.cell
def RFtestchip() -> gf.Component:
    """Create a test chip with RF and optical connections"""
    C = gf.Component()
    ### Get RFconnect template
    rfc = C << die_rf()

    # Fixed Parameters
    mzm_N = 12
    mzm_pos = (1800, int(rfc.dysize / 2 + 125 * 7))

    ### Add BBs

    pd = C << cells.HHI_PDDC()
    wgt = C << cells.HHI_WGTE200E1700()
    bend180 = C << gf.components.bend_circular180(cross_section="E1700")
    bj1 = C << cells.HHI_BJtwin()
    dfb = C << cells.HHI_DFB()
    mmi1 = C << JonnysDevice()
    mzm = C << MZMsection(mzm_N)
    mmi2 = C << JonnysDevice()
    bj2 = C << cells.HHI_BJtwin()

    # Move MZM
    mzm.mirror_y()
    mzm.dmove(mzm_pos)

    ### Add RF connection BBs
    conv_mz = C << cells.HHI_GSGtoGS()
    bend_gs = C << gf.components.bend_circular(
        cross_section="GS", radius=mzm.dymin - 500 * 4 - 22
    )

    ### Optical connections
    mmi1.connect("o2", mzm.ports["o1"])
    mmi2.connect("o1", mzm.ports["o4"])
    bj1.connect("o2", mmi1.ports["o1"])
    bj2.connect("o2", mmi2.ports["o4"])
    bend180.connect("o2", bj1.ports["o1"])
    dfb.connect("o1", bend180.ports["o1"])
    wgt.connect("o2", dfb.ports["o2"])
    pd.connect("o2", wgt.ports["o1"])

    ### RF connections
    conv_mz.connect("s1", rfc.ports["rf_e12"])
    bend_gs.connect("e2", mzm.ports["g1"])

    tech.route_single_sbend_gs(
        C, conv_mz.ports["g2"], bend_gs.ports["e1"], cross_section="GS"
    )

    ### DC routing
    # Define the BB ports to contact
    ctrl_ports_top_up = [dfb.ports["s1"], dfb.ports["g2"]]

    ctrl_ports_top_down = [dfb.ports["e1"], dfb.ports["e2"], pd.ports["p1"]]
    #  pd.ports['p1']]

    mzm_ports_bbs_top = [
        mmi1.ports["p1"],
        mmi1.ports["p2"],
        mzm.ports["n3"],
        mzm.ports["n4"],
        mmi2.ports["p1"],
        mmi2.ports["p2"],
    ]

    # Define the corresponding top DC pad indices (from left to right)
    c_dc1, c_dc2 = (
        len(ctrl_ports_top_up),
        len(ctrl_ports_top_up) + len(ctrl_ports_top_down),
    )

    m_dc1 = len(ctrl_ports_top_up) + len(ctrl_ports_top_down)
    m_dc2 = m_dc1 + len(mzm_ports_bbs_top)

    dc_ports_pads_top = [
        p for p in rfc.ports if "e4" in p.name and p.name.startswith("top_")
    ]
    dc_ports_pads_top.sort(key=lambda p: p.x)

    # Double the port that will contact the MZM gnd port
    mgnd_dc = c_dc2 + mzm_ports_bbs_top.index(mzm.ports["n3"])

    # Route upward pointing control ports to DC pads
    gf.routing.route_bundle(
        C,
        dc_ports_pads_top[:c_dc1],
        ctrl_ports_top_up,
        separation=10,
        start_straight_length=55.5,
        cross_section="DC",
        allow_width_mismatch=True,
        auto_taper=False,
    )

    # Route downward pointing control ports to DC pads
    gf.routing.route_bundle(
        C,
        dc_ports_pads_top[c_dc2 - 1 : c_dc1 - 1 : -1],
        ctrl_ports_top_down,
        separation=10,
        # end_straight_length=30,
        cross_section="DC",
        allow_width_mismatch=True,
        auto_taper=False,
    )

    # Route MZM-type device ports to DC pads
    gf.routing.route_bundle(
        C,
        dc_ports_pads_top[m_dc1 : m_dc2 - 1] + [dc_ports_pads_top[mgnd_dc]],
        mzm_ports_bbs_top,
        separation=10,
        start_straight_length=450,
        sort_ports=True,
        cross_section="DC",
        allow_width_mismatch=True,
        auto_taper=False,
        on_collision="show_warning",
    )

    # Connect the GND ports
    gnd_portpairs = [
        (pd.ports["n1"], dfb.ports["g2"]),
        (mmi1.ports["n1"], mzm.ports["n1"]),
        (mmi2.ports["n1"], mzm.ports["n2"]),
    ]

    for port1, port2 in gnd_portpairs:
        gf.routing.route_single(
            C,
            port1,
            port2,
            end_straight_length=15,
            cross_section="DC",
            allow_width_mismatch=True,
            auto_taper=False,
        )

    ### Optical routing
    mzm_midput_ports = [bj2.ports["o3"], bj2.ports["o1"]]
    ssc_ports = [
        p for p in rfc.ports if p.name.startswith("SSC_o1_") and p.name.endswith("_1")
    ]
    gf.routing.route_bundle_sbend(
        C,
        mzm_midput_ports,
        ssc_ports[1:3],
        allow_min_radius_violation=True,
        cross_section="E1700",
        sort_ports=False,
    )
    ### Add alignment PDs
    bend = C << gf.components.bend_circular(cross_section="E1700", radius=350)
    wgt = C << cells.HHI_WGTE200E1700()
    pd = C << cells.HHI_PDDC()

    # Connect the alignment PDs
    bend.connect("o2", rfc.ports["SSC_o1_1_1"])
    wgt.connect("o2", bend.ports["o1"])
    pd.connect("o1", wgt.ports["o1"])

    # Add the routes from the DC pad to the PD
    for dc, pn in zip([22, 23], ["p1", "n1"]):
        gf.routing.route_single(
            C,
            rfc.ports[f"top_e4_1_{dc}"],
            pd.ports[pn],
            cross_section="DC",
            allow_width_mismatch=True,
            auto_taper=False,
        )

    # Mirror copy the entire structure to the lower side, mirror along y = 2000 axis
    MC = C.dup()
    # rfc.delete()  # Do not mirror the RF connection template
    rfcname = rfc.name
    for r in C.references:
        if r.name[:20] == rfcname[:20]:
            continue  # Do not mirror the RF connection template
        r.dmirror_y(y=2000)

    _ = C << MC

    # Rename all cells to remove the `:`, `,` characters
    for cell in C.references:
        cell.name = cell.name.replace(":", "_").replace(",", "_")

    return C


if __name__ == "__main__":
    C = RFtestchip()
    C.show()
    # C.write_gds(PATH.extra / "RFtestchip.gds")
