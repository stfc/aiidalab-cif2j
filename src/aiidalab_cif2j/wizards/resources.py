"""Defines the model and view for the (multi-code) resource setup stage."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets as tl
from alc_aiidalab_widgets.widgets import CodeSelector

from aiidalab_cif2j.common.utils import add_button_style_class, cif2j_button_style
from aiidalab_cif2j.models.resources import (
    MPI_CAPABLE_CODES,
    OPTIONAL_CODES,
    REQUIRED_CODES,
    MultiCodeResourcesModel,
)
from aiidalab_cif2j.utils import test_aiida_cif2j_import

#: Human-readable label per code name, used for the selector row and guide text.
_CODE_DESCRIPTIONS = {
    "pw": "pw.x (Quantum ESPRESSO)",
    "pw2wannier90": "pw2wannier90.x (Quantum ESPRESSO)",
    "wannier90": "wannier90.x",
    "tb2j": "TB2J",
    "projwfc": "projwfc.x (optional)",
    "open_grid": "open_grid.x (optional)",
}


class ResourceSetupBox(ipw.VBox):
    """A box widget for defining computational resources across all required codes."""

    def __init__(self, model: MultiCodeResourcesModel, **kwargs):
        """
        ResourceSetupBox constructor.

        Parameters
        ----------
        model : MultiCodeResourcesModel
            The model holding the resource configuration.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(layout={"margin": "auto", "width": "80%"}, **kwargs)
        self.model = model

        self.required_rows = [
            CodeSelector(
                model,
                name,
                description=_CODE_DESCRIPTIONS.get(name, name),
                show_mpi=name in MPI_CAPABLE_CODES,
            )
            for name in REQUIRED_CODES
        ]
        self.optional_rows = [
            CodeSelector(
                model,
                name,
                description=_CODE_DESCRIPTIONS.get(name, name),
                auto_default=False,
                show_mpi=name in MPI_CAPABLE_CODES,
            )
            for name in OPTIONAL_CODES
        ]

        self.refresh_btn = ipw.Button(
            description="Refresh all",
            tooltip="Refresh the list of available codes for every row",
            icon="refresh",
            layout={"width": "auto"},
        )
        self.refresh_btn.on_click(self._refresh_all)
        add_button_style_class(self.refresh_btn)
        self.refresh_row = ipw.HBox(
            children=[self.refresh_btn],
            layout=ipw.Layout(width="100%", justify_content="flex-end"),
        )

        self.optional_codes_box = ipw.Accordion(
            children=[ipw.VBox(children=self.optional_rows)]
        )
        self.optional_codes_box.set_title(0, "Optional codes")
        self.optional_codes_box.selected_index = None

        self.label = ipw.Text(
            value=model.process_label,
            placeholder="Enter process label",
            description="Label:",
            style={"description_width": "180px"},
            layout=ipw.Layout(width="80%"),
        )
        tl.link((self.label, "value"), (model, "process_label"))

        self.description = ipw.Textarea(
            value=model.process_description,
            placeholder="Enter process description",
            description="Description:",
            style={"description_width": "180px"},
            layout=ipw.Layout(width="80%", height="120px"),
        )
        tl.link((self.description, "value"), (model, "process_description"))

        self.children = [
            cif2j_button_style(),
            self.refresh_row,
            *self.required_rows,
            self.optional_codes_box,
            self.label,
            self.description,
        ]

    def _refresh_all(self, _=None) -> None:
        """Refresh the list of available codes for every row."""
        for row in (*self.required_rows, *self.optional_rows):
            row.update_codes()
        return


class ComputationalResourcesWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """Main view for the resource setup stage."""

    def __init__(self, model: MultiCodeResourcesModel, **kwargs):
        """
        ComputationalResourcesWizardStep constructor.

        Parameters
        ----------
        model : MultiCodeResourcesModel
            The model holding the resource configuration.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.model = model
        self.rendered = False

        self.cif2j_installed = test_aiida_cif2j_import()
        self.cif2j_warning = ipw.HTML("", layout={"margin": "auto"})

        self.guide = ipw.HTML(self.model.default_guide)

        self.submit_btn = ipw.Button(
            description="Submit",
            button_style="success",
            tooltip="Submit the calculation",
            icon="check",
            layout={"width": "60%", "height": "30px", "margin": "20px auto 8px"},
        )
        self.submit_btn.on_click(self._submit)
        add_button_style_class(self.submit_btn)

        self.children = [
            cif2j_button_style(),
            self.guide,
            self.cif2j_warning if not self.cif2j_installed else ipw.HTML(""),
            ResourceSetupBox(model=self.model),
            self.submit_btn,
        ]
        return

    def render(self):
        """Render the wizard's contents if not already rendered."""
        if self.rendered:
            return
        self._refresh_widget()
        self.rendered = True
        return

    def _submit(self, _=None) -> None:
        """Handle the submission of the AiiDA process."""
        if self.model.validate():
            self.model.submitted = True
            self.submit_btn.disabled = True
            self.submit_btn.description = "Submitted"
            # Mark the (collapsed) step as complete via the AWB wizard icon.
            self.state = self.State.SUCCESS
        else:
            print("ERROR: Input Validation Failed")
        return

    def _refresh_widget(self) -> None:
        """Refresh the widget's contents."""
        self.cif2j_installed = test_aiida_cif2j_import()
        if not self.cif2j_installed:
            self.submit_btn.disabled = True
            self.cif2j_warning.value = (
                "<p style='color:red;'>"
                "The aiida-cif2j plugin is not installed. Please install it "
                "to proceed."
                "</p>"
            )
        else:
            self.cif2j_warning.value = ""
            self.submit_btn.disabled = False
