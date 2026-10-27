"""Defines the model and view for the (multi-code) resource setup stage."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets as tl
from aiida.orm import ContainerizedCode, InstalledCode, PortableCode, QueryBuilder

from aiidalab_cif2j.common.utils import add_button_style_class, cif2j_button_style
from aiidalab_cif2j.models.resources import (
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


class CodeSelectorRow(ipw.HBox):
    """A single "code dropdown + refresh" row, linked to one model trait."""

    def __init__(self, model: MultiCodeResourcesModel, code_name: str, **kwargs):
        """
        CodeSelectorRow constructor.

        Parameters
        ----------
        model : MultiCodeResourcesModel
            The model holding the resolved code labels.
        code_name : str
            One of the code names in ``REQUIRED_CODES``/``OPTIONAL_CODES``;
            selects which ``{code_name}_code`` trait this row is linked to.
        **kwargs :
            Keyword arguments passed to the `ipywidgets.HBox.__init__()`.
        """
        self.code_name = code_name
        self.code = ipw.Dropdown(
            description=_CODE_DESCRIPTIONS.get(code_name, code_name),
            style={"description_width": "180px"},
            layout={"width": "70%"},
        )
        self.update_codes()
        tl.link((self.code, "value"), (model, f"{code_name}_code"))

        self.refresh_button = ipw.Button(
            tooltip="Refresh the list of available codes",
            icon="refresh",
            layout={"width": "15%"},
        )
        self.refresh_button.on_click(self.update_codes)
        add_button_style_class(self.refresh_button)

        super().__init__(
            children=[self.code, self.refresh_button],
            layout={"width": "100%"},
            **kwargs,
        )
        return

    def update_codes(self, _=None) -> None:
        """Update the list of available codes."""
        qb = QueryBuilder()
        qb.append((InstalledCode, ContainerizedCode, PortableCode))
        codes = qb.all()
        code_labels = [f"{code[0].label}@{code[0].computer.label}" for code in codes]
        self.code.options = ["", *code_labels]
        return


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

        self.required_rows = [CodeSelectorRow(model, name) for name in REQUIRED_CODES]
        self.optional_rows = [CodeSelectorRow(model, name) for name in OPTIONAL_CODES]
        self.optional_codes_box = ipw.Accordion(
            children=[ipw.VBox(children=self.optional_rows)]
        )
        self.optional_codes_box.set_title(0, "Optional codes")
        self.optional_codes_box.selected_index = None

        self.pseudo_family = ipw.Text(
            value=model.pseudo_family,
            placeholder="e.g. SSSP/1.3/PBE/efficiency",
            description="Pseudopotential family:",
            style={"description_width": "180px"},
            layout=ipw.Layout(width="80%"),
        )
        tl.link((self.pseudo_family, "value"), (model, "pseudo_family"))

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
            *self.required_rows,
            self.optional_codes_box,
            self.pseudo_family,
            self.label,
            self.description,
        ]


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
