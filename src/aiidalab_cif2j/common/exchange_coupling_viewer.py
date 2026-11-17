"""Defines the combined table + 3D overlay viewer for exchange couplings."""

import ipywidgets as ipw
import numpy
from aiida.common.links import LinkType
from aiida.orm import Node, SinglefileData, StructureData
from aiida_cif2j.data.exchange_coupling import UNITS, ExchangeCouplingData
from alc_aiidalab_widgets.widgets.structure import (
    StructureViewWidget,
    build_binned_vector_field,
)
from alc_aiidalab_widgets.widgets.tables import GenericArrayDataTableWidget

#: Default number of couplings shown in the 3D overlay, ranked by |J_iso|.
#:
#: TB2J reports every magnetic-site pair within its cutoff radius, including
#: many periodic-image repeats, which can number in the hundreds for a real
#: structure; drawing all of them floods the view with grid-like arrows in
#: every lattice direction. Showing only the strongest couplings keeps the
#: overlay readable. A nearest-neighbor-shell-based filter (as an
#: alternative, switchable in the UI) is a possible future addition.
_DEFAULT_TOP_N_COUPLINGS = 20

#: Hard cap on the "Couplings shown" slider's range, independent of how many
#: pairs TB2J actually reported -- with hundreds of pairs in range, the
#: slider becomes too coarse/hard to use precisely.
_MAX_TOP_N_COUPLINGS = 50


def _find_tb2j_structure(node: Node) -> StructureData | SinglefileData | None:
    """Find the structure a `TB2J.pickle`-derived node's results belong to.

    Walks `node`'s creating link to the `WannierTB2JCalculation` CalcJobNode
    and returns its `structure` input.

    Parameters
    ----------
    node : Node
        A node produced by `WannierTB2JCalculation`/`TB2JParser` (e.g. an
        `ExchangeCouplingData`).

    Returns
    -------
    StructureData, SinglefileData, or None
        The structure input to the creating calculation, or `None` if the
        node has no recorded creating link, or that calculation has no
        `structure` input.
    """
    creating = node.get_incoming(link_type=LinkType.CREATE).first()
    if creating is None:
        return None
    try:
        return creating.node.inputs.structure
    except AttributeError:
        return None


class ExchangeCouplingViewWidget(ipw.VBox):
    """Combined table + 3D exchange-path overlay for an `ExchangeCouplingData` node."""

    def __init__(self, node: ExchangeCouplingData, **kwargs):
        """
        ExchangeCouplingViewWidget constructor.

        Parameters
        ----------
        node : ExchangeCouplingData
            The exchange-coupling node to visualise.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        self.node = node
        self.table = GenericArrayDataTableWidget(node, units=UNITS)

        structure = _find_tb2j_structure(node)
        if structure is None:
            children = [
                self.table,
                ipw.HTML(
                    "<p><i>No provenance link to an input structure was found; "
                    "the 3D exchange-path overlay is unavailable.</i></p>"
                ),
            ]
        else:
            self.structure_view = StructureViewWidget(structure)
            n_pairs = len(node.get_array("J_iso"))
            slider_max = min(n_pairs, _MAX_TOP_N_COUPLINGS)
            self.overlay_toggle = ipw.Checkbox(
                description="Show exchange paths on structure", value=False
            )
            self.top_n_slider = ipw.IntSlider(
                description="Couplings shown:",
                min=1,
                max=slider_max,
                value=min(_DEFAULT_TOP_N_COUPLINGS, slider_max),
                continuous_update=False,
                style={"description_width": "initial"},
            )
            self.overlay_toggle.observe(self._toggle_overlay, "value")
            self.top_n_slider.observe(self._on_top_n_changed, "value")
            children = [
                self.table,
                ipw.HBox([self.overlay_toggle, self.top_n_slider]),
                self.structure_view,
            ]

        super().__init__(children=children, **kwargs)

    def _toggle_overlay(self, change) -> None:
        """Show or hide the exchange-path vector field."""
        if change["new"]:
            self._render_overlay()
        else:
            self.structure_view.set_vector_field(None)

    def _on_top_n_changed(self, _change) -> None:
        """Re-render the overlay if currently shown, with the new coupling count."""
        if self.overlay_toggle.value:
            self._render_overlay()

    def _render_overlay(self) -> None:
        """Draw the `top_n_slider`-strongest couplings as a binned vector field.

        Only the strongest couplings (by |J_iso|) are drawn, not all of them
        -- see `_DEFAULT_TOP_N_COUPLINGS`. Arrow length is fixed (the
        shortest selected bond's distance) rather than the bond's own
        distance, so length doesn't visually conflate with the color-coded
        coupling strength -- e.g. a weak, long-range coupling would
        otherwise draw a long pale arrow next to a strong, short-range one's
        short dark arrow, suggesting "longer = more significant" when the
        opposite is usually true. Revisit once there's user feedback on how
        best to convey distance and strength together (see plan).
        """
        j_iso = self.node.get_array("J_iso")
        top_n = self.top_n_slider.value
        top_indices = numpy.argsort(numpy.abs(j_iso))[::-1][:top_n]

        positions = self.structure_view.to_ase().get_positions()
        arrow_length = float(self.node.get_array("distance")[top_indices].min())
        settings = build_binned_vector_field(
            origins=positions[self.node.get_array("site_i")[top_indices]],
            vectors=self.node.get_array("distance_vector")[top_indices],
            magnitudes=numpy.abs(j_iso[top_indices]),
            arrow_length=arrow_length,
        )
        self.structure_view.set_vector_field(settings)
