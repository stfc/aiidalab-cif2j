"""Defines the model and view for the workflow configuration stage.

Unlike ``aiidalab-chemshell`` (which offers several workflow types selected
via tabs), this app only exposes one workflow (Wannier90 + TB2J), so this
step is a single parameter form rather than a tabbed selector.
"""

import json
from functools import partial

import aiidalab_widgets_base as awb
import ipywidgets as ipw
import traitlets as tl

from aiidalab_cif2j.common.utils import (
    add_button_style_class,
    cif2j_button_style,
    get_installed_pseudo_family_labels,
)
from aiidalab_cif2j.models.workflow import Cif2JWorkflowModel
from aiidalab_cif2j.utils import APPS_DIRECTORY, open_link_in_new_tab


def _enum_dropdown(enum_cls, value, **kwargs) -> ipw.Dropdown:
    """Build a dropdown whose options are an Enum's members."""
    return ipw.Dropdown(
        options=[(member.name, member) for member in enum_cls],
        value=value,
        **kwargs,
    )


def _pseudo_family_warning_html(pseudo_family_labels: list[str]) -> str:
    """Return the warning HTML to show when no pseudopotential family is installed."""
    if pseudo_family_labels:
        return ""
    return (
        "<p style='color:#b35900;'>No pseudopotential families installed."
        " Run e.g. <code>aiida-pseudo install sssp</code> in this"
        " environment, then reload the app.</p>"
    )


class WorkflowWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """Wizard step for configuring the Wannier90 + TB2J workflow parameters."""

    def __init__(self, model: Cif2JWorkflowModel, **kwargs):
        """
        WorkflowWizardStep constructor.

        Parameters
        ----------
        model : Cif2JWorkflowModel
            The model controlling the workflow parameters.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.rendered = False
        self.model = model

        self.info = ipw.HTML(
            """
                <p>
                    Configure the Wannier90 + TB2J workflow used to compute magnetic
                    exchange interactions.
                </p>
            """
        )

        style = {"description_width": "180px"}
        layout = ipw.Layout(width="80%")

        self.protocol = _enum_dropdown(
            type(model.protocol),
            model.protocol,
            description="Protocol:",
            style=style,
            layout=layout,
        )
        tl.link((self.protocol, "value"), (model, "protocol"))

        self.spin_type = _enum_dropdown(
            type(model.spin_type),
            model.spin_type,
            description="Spin type:",
            style=style,
            layout=layout,
        )
        tl.link((self.spin_type, "value"), (model, "spin_type"))

        self.electronic_type = _enum_dropdown(
            type(model.electronic_type),
            model.electronic_type,
            description="Electronic type:",
            style=style,
            layout=layout,
        )
        tl.link((self.electronic_type, "value"), (model, "electronic_type"))

        self.projection_type = _enum_dropdown(
            type(model.projection_type),
            model.projection_type,
            description="Wannier projection type:",
            style=style,
            layout=layout,
        )
        tl.link((self.projection_type, "value"), (model, "projection_type"))

        pseudo_family_labels = get_installed_pseudo_family_labels()
        self.pseudo_family = ipw.Dropdown(
            options=[("Select a pseudopotential family…", "")]
            + [(label, label) for label in pseudo_family_labels],
            value=model.pseudo_family if model.pseudo_family in pseudo_family_labels else "",
            description="Pseudopotential family:",
            style=style,
            layout=layout,
            disabled=not pseudo_family_labels,
        )
        tl.link((self.pseudo_family, "value"), (model, "pseudo_family"))

        self.pseudo_family_manage_btn = ipw.Button(
            description="Manage",
            button_style="info",
            tooltip="Open the pseudopotential manager to install or inspect families",
            icon="external-link",
            layout={"width": "auto"},
        )
        self.pseudo_family_manage_btn.on_click(
            partial(
                open_link_in_new_tab,
                APPS_DIRECTORY + "cif2j/notebooks/pseudos.ipynb",
            )
        )

        self.pseudo_family_refresh_btn = ipw.Button(
            description="Refresh",
            tooltip="Refresh the list of installed pseudopotential families",
            icon="refresh",
            layout={"width": "auto"},
        )
        self.pseudo_family_refresh_btn.on_click(self._refresh_pseudo_families)

        add_button_style_class(
            self.pseudo_family_manage_btn, self.pseudo_family_refresh_btn
        )
        self.pseudo_family_buttons = ipw.HBox(
            children=[self.pseudo_family_manage_btn, self.pseudo_family_refresh_btn],
            layout=ipw.Layout(width="80%", justify_content="flex-end"),
        )

        self.pseudo_family_warning = ipw.HTML(
            _pseudo_family_warning_html(pseudo_family_labels)
        )

        self.magnetic_elements = ipw.Text(
            value=", ".join(model.magnetic_elements),
            placeholder="Leave blank to auto-detect",
            description="Magnetic elements:",
            style=style,
            layout=layout,
        )
        self.magnetic_elements.observe(self._on_magnetic_elements_change, "value")

        self.tb2j_parameters = ipw.Textarea(
            value=json.dumps(model.tb2j_parameters, indent=2),
            placeholder="{}",
            description="tb2j.parameters (JSON):",
            style=style,
            layout=ipw.Layout(width="80%", height="120px"),
        )
        self.tb2j_parameters.observe(
            lambda change: self._on_json_change(change, "tb2j_parameters"), "value"
        )

        self.tb2j_options = ipw.Textarea(
            value=json.dumps(model.tb2j_options, indent=2),
            placeholder="{}",
            description="tb2j.metadata.options (JSON):",
            style=style,
            layout=ipw.Layout(width="80%", height="120px"),
        )
        self.tb2j_options.observe(
            lambda change: self._on_json_change(change, "tb2j_options"), "value"
        )

        self.json_error = ipw.HTML("")

        self.advanced = ipw.Accordion(
            children=[
                ipw.VBox(
                    children=[
                        self.tb2j_parameters,
                        self.tb2j_options,
                        self.json_error,
                    ]
                )
            ]
        )
        self.advanced.set_title(0, "Advanced")
        self.advanced.selected_index = None

    def render(self) -> None:
        """Render the wizard's contents if not already rendered."""
        if self.rendered:
            return

        self.submit_btn = ipw.Button(
            description="Submit Workflow Configuration",
            disabled=False,
            button_style="success",
            tooltip="Submit the workflow configuration",
            icon="check",
            layout={"width": "60%", "height": "30px", "margin": "20px auto 8px"},
        )
        add_button_style_class(self.submit_btn)
        self.submit_btn.on_click(self._submit)

        self.error = ipw.HTML("")

        self.children = [
            cif2j_button_style(),
            self.info,
            self.protocol,
            self.spin_type,
            self.electronic_type,
            self.projection_type,
            self.pseudo_family,
            self.pseudo_family_buttons,
            self.pseudo_family_warning,
            self.magnetic_elements,
            self.advanced,
            self.error,
            self.submit_btn,
        ]
        self.rendered = True
        return

    def _refresh_pseudo_families(self, _=None) -> None:
        """Re-query the installed pseudopotential families and update the dropdown."""
        pseudo_family_labels = get_installed_pseudo_family_labels()
        current_value = self.pseudo_family.value
        self.pseudo_family.options = [("Select a pseudopotential family…", "")] + [
            (label, label) for label in pseudo_family_labels
        ]
        self.pseudo_family.value = (
            current_value if current_value in pseudo_family_labels else ""
        )
        self.pseudo_family.disabled = not pseudo_family_labels
        self.pseudo_family_warning.value = _pseudo_family_warning_html(
            pseudo_family_labels
        )
        return

    def _on_magnetic_elements_change(self, change: dict) -> None:
        """Parse the comma-separated magnetic elements field into a list."""
        self.model.magnetic_elements = [
            element.strip() for element in change["new"].split(",") if element.strip()
        ]
        return

    def _on_json_change(self, change: dict, trait_name: str) -> None:
        """Parse a JSON textarea's value into the corresponding model trait."""
        try:
            value = json.loads(change["new"]) if change["new"].strip() else {}
        except json.JSONDecodeError as exc:
            self.json_error.value = (
                f"<p style='color:red;'>Invalid JSON for {trait_name}: {exc}</p>"
            )
            return
        self.json_error.value = ""
        setattr(self.model, trait_name, value)
        return

    def _submit(self, _=None) -> None:
        """Mark the workflow configuration step as complete."""
        if not self.model.validate():
            self.error.value = (
                "<p style='color:red;'>No pseudopotential family selected.</p>"
            )
            return
        self.error.value = ""
        self.submit_btn.disabled = True
        self.submit_btn.description = "Submitted"
        self.state = self.State.SUCCESS
        return
