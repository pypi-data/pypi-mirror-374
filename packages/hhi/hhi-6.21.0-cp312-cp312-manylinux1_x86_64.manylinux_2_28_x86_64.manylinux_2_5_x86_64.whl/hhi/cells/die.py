from functools import partial
from typing import Any

import gdsfactory as gf
import numpy as np
from gdsfactory.typings import (
    ComponentSpec,
    Float2,
    LayerSpec,
    LayerSpecs,
    Size,
)

from hhi.tech import LAYER


@gf.cell
def pad(size: Size = (66, 66)) -> gf.Component:
    """Returns rectangular pad with ports.

    Args:
        size: x, y size.
    """
    return gf.c.pad(
        size=size,
        layer="M2",
        bbox_layers=("M1", "ISO"),
        bbox_offsets=(2, 2),
    )


@gf.cell
def cleave_mark() -> gf.Component:
    """Create a cleave mark for the die."""
    c = gf.Component(name="cleave_mark")
    c.add_polygon([[0.0, 0.0], [15.442, 33.12], [33.119, 15.441]], layer=LAYER.TEXT)
    return c


@gf.cell
def pad_GSG(xsize: float = 98, pitch: float = 136) -> gf.Component:
    c = gf.components.straight_array(
        n=1, spacing=pitch, length=xsize, cross_section="GSG"
    ).copy()
    gf.add_padding(
        component=c,
        layers=("BB_outline",),
        default=0,
    )
    gf.add_padding(
        component=c,
        layers=("ISO",),
        default=0,
        right=16,
        left=16,
    )
    c.flatten()
    return c


@gf.cell
def pad_GS(xsize: float = 98, pitch: float = 24) -> gf.Component:
    c = gf.components.straight_array(
        n=2, spacing=pitch, length=xsize, cross_section="GS"
    ).copy()
    gf.add_padding(
        component=c,
        layers=("ISO",),
        default=0,
        right=16,
        left=16,
    )
    c.flatten()
    return c


@gf.cell
def die(
    size: tuple[float, float] = (8000, 4000), centered: bool = False
) -> gf.Component:
    """Create a die template with cleave marks.

    Args:
        size: Size of the die.
        centered: If True, center the die on the origin.
    """
    c = gf.Component()
    allowed_sizes = (
        np.array(
            [
                (1, 1),
                (1, 2),
                (1, 4),
                (1, 6),
                (1, 8),
                (2, 1),
                (2, 2),
                (2, 4),
                (2, 6),
                (4, 1),
                (8, 1),
                (2, 2),
                (4, 2),
                (8, 2),
                (12, 2),
                (4, 4),
                (8, 4),
                (12, 4),
                (1, 8),
                (2, 8),
                (3, 8),
                (4, 8),
                (1, 12),
                (12, 12),
                (2, 12),
                (3, 12),
                (4, 12),
                (8, 24),
            ]
        )
        * 1000
    )

    # Check size is in the available sizes
    if not any(np.allclose(size, s) for s in allowed_sizes):
        raise ValueError(f"Size must be one of {np.round(allowed_sizes * 1e-3)} mm")
    # Add the BB exclusion zone, demarking the chip boundary
    die = c << gf.components.die(size=size, street_width=50, die_name="")
    if not centered:
        die.movex(size[0] / 2)
        die.movey(size[1] / 2)

    # Add the 4 cleave marks in each corner
    for corner, p2 in zip(
        [(0, 0), (0, 1), (1, 0), (1, 1)], [(1, 1), (1, 0), (0, 1), (1, -1)]
    ):
        cm = c << cleave_mark()
        p1 = (0, 0)
        p2 = (p2[0], p2[1])
        cm.dmirror(p1=p1, p2=p2)
        cm.movex(corner[0] * size[0] - size[0] / 2 * (centered))
        cm.movey(corner[1] * size[1] - size[1] / 2 * (centered))

    return c


@gf.cell
def die_rf(
    size: tuple[float, float] = (8000, 4000),
    num_dc_pads: int = 23,
    dc_pad_pitch: float = 150.0,
    dc_pad_size: tuple[float, float] = (98, 138),
    num_rf_pads: int = 8,
    rf_pad_sizex: float = 98.0,
    rf_pad_pitch: float = 136,
    rf_pad_pos=(100, 250),
    num_SSCs: int = 10,
    ssc: ComponentSpec = "HHI_SSCLATE1700",
) -> gf.Component:
    """Create a template for RF connections.
    # TODO: Add the RF connections, text labels, design region, etc.

    Args:
        size: Size of the die.
        num_dc_pads: Number of DC pads.
        dc_pad_pitch: Spacing between DC pads.
        dc_pad_size: Size of the DC pads.
        num_rf_pads: Number of RF pads.
        rf_pad_sizex: Size of the RF pads in the x-direction.
        rf_pad_pitch: Spacing between RF pads.
        rf_pad_pos: Position of the RF pads.
        num_SSCs: Number of spot size converters SSCs.
        ssc: SSC component.
    """
    c = gf.Component()

    # Fixed parameters
    id_pos = (size[0] - 150, 150)
    dc_pad_pos1 = (3231, size[1] - 114 - dc_pad_size[1] / 2)
    dc_pad_pos2 = (3231, 114 + dc_pad_size[1] / 2)

    ssc = gf.get_component(ssc)

    SSCs_pos = (size[0] - ssc.xsize / 2, size[1] / 2)
    SSCs_spacing = 127

    _ = c << die(size=size)

    # Add HHI_ID cell square
    HHI_ID = gf.components.rectangle(
        size=(100, 100), layer="BB_outline", centered=True, port_type=None
    ).copy()
    HHI_ID.name = "HHI_ID"
    hhi_id = c << HHI_ID
    hhi_id.move(id_pos)

    # Add the DC pads at the top
    for dc_pad_pos in [dc_pad_pos1, dc_pad_pos2]:
        dc_pads = c << gf.components.array(
            pad(size=dc_pad_size), column_pitch=dc_pad_pitch, columns=num_dc_pads
        )
        dc_pads.move(dc_pad_pos)
        c.add_ports(dc_pads.ports, prefix=["top_", "bot_"][(dc_pad_pos == dc_pad_pos2)])

    # Add the RF ports on the left side
    rf_pads = c << gf.components.straight_array(
        n=num_rf_pads, spacing=rf_pad_pitch, length=rf_pad_sizex, cross_section="GSG"
    )
    rf_pads.move(rf_pad_pos)
    rf_ports = rf_pads.ports.filter(orientation=0)
    c.add_ports(rf_ports, prefix="rf_")

    # Add the SSCs at the right side
    sscs = c << gf.components.array(
        ssc,
        row_pitch=SSCs_spacing,
        columns=1,
        rows=num_SSCs,
        centered=True,
    )
    sscs.move(SSCs_pos)
    SSC_E1700_ports = gf.port.get_ports_list(sscs.ports, prefix="o1")
    c.add_ports(SSC_E1700_ports, prefix="SSC_")
    return c


add_pads_bot = partial(
    gf.routing.add_pads_bot,
    component="HHI_DFB",
    pad="pad",
    cross_section="DC",
    straight_separation=30,
    bend="bend_circular",
    port_names=("e1", "e2"),
    auto_taper=False,
)


@gf.cell
def edge_coupler_with_angle(
    angle: float | None = -8,
    cross_section="E1700",
    edge_coupler: ComponentSpec = "HHI_SSCLATE1700",
) -> gf.Component:
    """Inverse taper edge coupler Cband."""
    c = gf.get_component(edge_coupler)

    if angle:
        c2 = gf.Component()
        ref = c2.add_ref(c)
        ref.rotate(angle=angle)
        bend = c2.create_vinst(
            gf.c.bend_euler_all_angle(angle=angle, cross_section=cross_section)
        )
        bend.connect("o2", ref.ports["o1"])
        c2.add_port(name="o1", port=bend.ports["o1"])
        c2.add_port(name="o2", port=ref.ports["o2"])
        c2.flatten()
        return c2
    else:
        c.flatten()
        return c


@gf.cell
def text_rectangular(
    text: str = "abc",
    size: float = 3,
    justify: str = "left",
    layer: LayerSpec = "M1",
) -> gf.Component:
    """Returns Pixel based font, guaranteed to be manhattan, without acute angles.

    Args:
        text: string.
        size: pixel size.
        justify: left, right or center.
        layer: for text.
    """
    return gf.c.text_rectangular(
        text=text,
        size=size,
        justify=justify,
        layer=None,
        position=(0.0, 0.0),
        layers=(layer,),
    )


@gf.cell
def text_rectangular_multi_layer(
    text: str = "abc",
    layers: LayerSpecs = (
        "M1",
        "M2",
    ),
    text_factory: ComponentSpec = "text_rectangular",
    **kwargs: Any,
) -> gf.Component:
    """Returns rectangular text in different layers.

    Args:
        text: string of text.
        layers: list of layers to replicate the text.
        text_factory: function to create the text Components.
        kwargs: keyword arguments for text_factory.
    """
    return gf.c.text_rectangular_multi_layer(
        text=text,
        layers=layers,
        text_factory=text_factory,
        **kwargs,
    )


@gf.cell
def edge_coupler_array(
    edge_coupler: ComponentSpec = "edge_coupler_with_angle",
    n: int = 5,
    pitch: float = 127.0,
    text: ComponentSpec | None = "text_rectangular",
    text_offset: Float2 = (-50, 0),
    text_rotation: float = 0,
) -> gf.Component:
    """Fiber array edge coupler.

    Args:
        edge_coupler: edge coupler.
        cross_section: spec.
        radius: bend radius loopback (um).
        n: number of channels.
        pitch: Fiber pitch (um).
        text: Optional text spec.
        text_offset: x, y.
        text_rotation: text rotation in degrees.
    """

    return gf.c.edge_coupler_array(
        edge_coupler=edge_coupler,
        n=n,
        pitch=pitch,
        text=text,
        text_offset=text_offset,
        text_rotation=text_rotation,
        x_reflection=False,
    )


if __name__ == "__main__":
    from hhi.config import PATH

    # c = edge_coupler_array()
    # c = gf.grid(
    #     [pad_GSG, gf.import_gds(PATH.home / "Downloads" / "GSG.gds")], spacing=100
    # )
    c = gf.grid([pad, gf.import_gds(PATH.home / "Downloads" / "DC.gds")], spacing=100)
    c.pprint_ports()
    c.show()
