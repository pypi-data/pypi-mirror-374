import gdsfactory as gf

from hhi import cells, tech
from hhi.cells import die, pad
from hhi.cells.fixed import (
    HHI_BPD,
    HHI_DBR,
    HHI_DFB,
    HHI_EAM,
    HHI_GRAT,
    HHI_MIR1E1700,
    HHI_MIR2E1700,
    HHI_MZMDD,
    HHI_MZMDU,
    HHI_PDDC,
    HHI_PMTOE200,
    HHI_PMTOE600,
    HHI_PMTOE1700,
    HHI_R50GSG,
    HHI_SGDBRTO,
    HHI_SOA,
    HHI_SSCLATE200,
    HHI_SSCLATE1700,
    HHI_WGTE200E600,
    HHI_WGTE200E1700,
    HHI_WGTE600E1700,
    HHI_BJsingle,
    HHI_BJtwin,
    HHI_DBRsection,
    HHI_DFBsection,
    HHI_DirCoupE600,
    HHI_DirCoupE1700,
    HHI_EAMsection,
    HHI_EOBiasSectionSingle,
    HHI_EOBiasSectionTwin,
    HHI_EOElectricalGND,
    HHI_EOPMTermination,
    HHI_EOPMTWSingleDD,
    HHI_EOPMTWSingleDU,
    HHI_EOPMTWTwinDD,
    HHI_EOPMTWTwinDU,
    HHI_FacetWGE200,
    HHI_FacetWGE600,
    HHI_FacetWGE1700,
    HHI_FacetWGE1700twin,
    HHI_GRATsection,
    HHI_GSGtoGS,
    HHI_ISOsectionSingle,
    HHI_ISOsectionTwin,
    HHI_METMETx,
    HHI_MMI1x2ACT,
    HHI_MMI1x2E600,
    HHI_MMI1x2E1700,
    HHI_MMI2x2ACT,
    HHI_MMI2x2E600,
    HHI_MMI2x2E1700,
    HHI_MZIswitch,
    HHI_PDRFsingle,
    HHI_PDRFtwin,
    HHI_PolConverter45,
    HHI_PolConverter90,
    HHI_PolSplitter,
    HHI_SOAsection,
    HHI_TOBiasSection,
    HHI_WGMETxACTGSGsingle,
    HHI_WGMETxACTGSGtwin,
    HHI_WGMETxACTGSsingle,
    HHI_WGMETxACTGStwin,
    HHI_WGMETxACTsingle,
    HHI_WGMETxACTtwin,
    HHI_WGMETxE200,
    HHI_WGMETxE200GS,
    HHI_WGMETxE200GSG,
    HHI_WGMETxE600,
    HHI_WGMETxE600GS,
    HHI_WGMETxE600GSG,
    HHI_WGMETxE1700GSGsingle,
    HHI_WGMETxE1700GSGtwin,
    HHI_WGMETxE1700GSsingle,
    HHI_WGMETxE1700GStwin,
    HHI_WGMETxE1700single,
    HHI_WGMETxE1700twin,
    layer_bbmetal,
    layer_bbox,
    layer_label,
    layer_pin,
    layer_pin_electrical,
    layer_pin_label,
    layer_pin_optical,
    layer_text,
    text_function,
)
from hhi.config import PATH

size1 = (2e3, 8e3)
size2 = (4e3, 8e3)
size3 = (12e3, 8e3)


@gf.cell
def sample_die(size=(8e3, 24e3), y_spacing: float = 40) -> gf.Component:
    """Returns a sample die

    Args:
        size: size of the die. Typical sizes are 2x8mm², 4x8mm² and 12x8mm².
        y_spacing: spacing between components.

    Returns:
        c: a sample die.

    .. plot::
      :include-source:

      import gdsfactory as gf
      from hhi.samples import demo

      c = demo.sample_die()
      c.draw_ports()
      c.plot()
    """
    c = gf.Component()

    rdie = c << die(size, centered=True)

    components = [
        HHI_BJsingle,
        HHI_BJtwin,
        HHI_BPD,
        HHI_DBR,
        HHI_DBRsection,
        HHI_DFB,
        HHI_DFBsection,
        HHI_DirCoupE1700,
        HHI_DirCoupE600,
        HHI_EAM,
        HHI_EAMsection,
        HHI_EOBiasSectionSingle,
        HHI_EOBiasSectionTwin,
        HHI_EOElectricalGND,
        HHI_EOPMTWSingleDD,
        HHI_EOPMTWSingleDU,
        HHI_EOPMTWTwinDD,
        HHI_EOPMTWTwinDU,
        HHI_EOPMTermination,
        HHI_FacetWGE1700,
        HHI_FacetWGE1700twin,
        HHI_FacetWGE200,
        HHI_FacetWGE600,
        HHI_GRAT,
        HHI_GRATsection,
        HHI_GSGtoGS,
        HHI_ISOsectionSingle,
        HHI_ISOsectionTwin,
        HHI_METMETx,
        HHI_MIR1E1700,
        HHI_MIR2E1700,
        HHI_MMI1x2ACT,
        HHI_MMI1x2E1700,
        HHI_MMI1x2E600,
        HHI_MMI2x2ACT,
        HHI_MMI2x2E1700,
        HHI_MMI2x2E600,
        HHI_MZIswitch,
        HHI_MZMDD,
        HHI_MZMDU,
        HHI_PDDC,
        HHI_PDRFsingle,
        HHI_PDRFtwin,
        HHI_PMTOE1700,
        HHI_PMTOE200,
        HHI_PMTOE600,
        HHI_PolConverter45,
        HHI_PolConverter90,
        HHI_PolSplitter,
        HHI_R50GSG,
        HHI_SGDBRTO,
        HHI_SOA,
        HHI_SOAsection,
        HHI_SSCLATE1700,
        HHI_SSCLATE200,
        HHI_TOBiasSection,
        HHI_WGMETxACTGSGsingle,
        HHI_WGMETxACTGSGtwin,
        HHI_WGMETxACTGSsingle,
        HHI_WGMETxACTGStwin,
        HHI_WGMETxACTsingle,
        HHI_WGMETxACTtwin,
        HHI_WGMETxE1700GSGsingle,
        HHI_WGMETxE1700GSGtwin,
        HHI_WGMETxE1700GSsingle,
        HHI_WGMETxE1700GStwin,
        HHI_WGMETxE1700single,
        HHI_WGMETxE1700twin,
        HHI_WGMETxE200,
        HHI_WGMETxE200GS,
        HHI_WGMETxE200GSG,
        HHI_WGMETxE600,
        HHI_WGMETxE600GS,
        HHI_WGMETxE600GSG,
        HHI_WGTE200E1700,
        HHI_WGTE200E600,
        HHI_WGTE600E1700,
        layer_bbmetal,
        layer_bbox,
        layer_label,
        layer_pin,
        layer_pin_electrical,
        layer_pin_label,
        layer_pin_optical,
        layer_text,
        text_function,
    ]
    ymin = rdie.dymin + 100

    # This is spaghetti code to map the cross-sections to the correct FACET BB cells
    ecdict = {
        tech.E1700: cells.HHI_FacetWGE1700,
        "E1700twin": cells.HHI_FacetWGE1700twin,
        tech.E600: cells.HHI_FacetWGE600,
        tech.E200: cells.HHI_FacetWGE200,
        tech.ACT: cells.HHI_ISOsectionSingle,  # Not really a FACET BB cell
        "ACTtwin": cells.HHI_ISOsectionTwin,
    }

    for component in components:
        ci = component()
        ci = (
            gf.routing.add_pads_bot(
                ci,
                cross_section="DC",
                straight_separation=10,
                bend="bend_circular",
                pad=pad,
                pad_pitch=150,
                force_manhattan=True,
            )
            if ci.ports.filter(port_type="electrical")
            else ci
        )
        ref = c << ci
        ref.dymin = ymin
        ref.dx = 0
        ymin = ref.dymax + y_spacing

        # get the optical ports of the component
        oports_left = ref.ports.filter(orientation=180)
        oports_right = ref.ports.filter(orientation=0)

        ### Routing to L facet
        # The `add_pads_bot` function leaves only optical ports in `ref`
        xsec = (
            tech.cross_sections[oports_left[0].info["cross_section"]]
            if oports_left
            else tech.E1700
        )
        ec = ecdict[xsec]()
        if xsec == tech.ACT:
            xlength_left = oports_left[0].dx - rdie.dxmin + 50
            ec = (
                ecdict["ACTtwin"](L_I=xlength_left)
                if len(oports_left) == 2
                else ecdict[tech.ACT](L_I=xlength_left)
            )
            # xsec = 'ACT' # TODO: find some way to allow HHI_ISOsection(Twin) to be used as a cross-section

        # if xsec == tech.E1700 and len(oports_left) == 2: # won't work
        #     ec   = ecdict['E1700twin']()

        routes_left, ports_left = gf.routing.route_ports_to_side(
            component=c,
            ports=oports_left,
            cross_section=xsec,
            side="west",
            x=rdie.dxmin + ec.xsize - 50.001 * (xsec == tech.ACT),
        )

        if oports_left:
            for p in ports_left:
                ref = c << ec
                ref.connect("o1", p)
                if "twin" in ec.name.lower():
                    break

            text = c << gf.c.text(
                text=f"{component().name}-{'+'.join([p.name.split('_')[0] for p in ports_left])}",
                size=30,
                layer="TEXT",
            )
            text.dxmin = ref.dxmin + 105
            text.dy = ref.dymax + 20

        ### Routing to R facet
        xsec = (
            tech.cross_sections[oports_right[0].info["cross_section"]]
            if oports_right
            else tech.E1700
        )
        ec = ecdict[xsec]()
        if xsec == tech.ACT:
            xlength_left = rdie.dxmax - oports_right[0].dx + 50
            ec = (
                ecdict["ACTtwin"](L_I=xlength_left)
                if len(oports_left) == 2
                else ecdict[tech.ACT](L_I=xlength_left)
            )

        routes_right, ports_right = gf.routing.route_ports_to_side(
            component=c,
            ports=oports_right,
            cross_section=xsec,
            x=rdie.dxmax - ec.xsize + 50.001 * (xsec == tech.ACT),
            side="east",
        )

        ports_right.sort(key=lambda p: p.y, reverse=True)
        if oports_right:
            for p in ports_right:
                ref = c << ec
                ref.connect("o1", p)
                if "twin" in ec.name.lower():
                    break
            text = c << gf.c.text(
                text=f"{component().name}-{'+'.join([p.name.split('_')[0] for p in ports_right])}",
                size=30,
                layer="TEXT",
            )
            text.dxmax = ref.dxmax - 105
            text.dy = ref.dymax + 20

    # Rename all cells to remove the `:`, `,` characters
    for cell in c.get_dependencies(True):
        cell.name = cell.name.replace(":", "_").replace(",", "_")

    return c


if __name__ == "__main__":
    c = sample_die()
    # c = cells.HHI_MZIswitch()
    # p = c['o1']
    c.write_gds(gdspath=PATH.extra / "sample_die.gds")
    c.show()
