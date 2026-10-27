"""Defines the model and view components for the structure setup stage."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw

from aiidalab_cif2j.common.structure_uploader import StructureSelectionWidget
from aiidalab_cif2j.common.utils import add_button_style_class, cif2j_button_style
from aiidalab_cif2j.models.structure import StructureInputModel


class StructureWizardStep(ipw.VBox, awb.WizardAppWidgetStep):
    """
    Wizard for structure selection.

    A step in a wizard based process widget which allows a user to configure
    the CIF/MCIF structure to be used in the Wannier90 + TB2J workflow.
    """

    def __init__(self, model: StructureInputModel, **kwargs):
        """
        StructureWizardStep constructor.

        Parameters
        ----------
        model : StructureInputModel
            A model controlling the data required for the structure step.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(children=[], **kwargs)
        self.rendered = False
        self.model = model

        self.info = ipw.HTML(
            """
                <p>
                    Load in a CIF/MCIF structure to start the workflow.
                </p>
            """
        )

        self.structure_uploader = StructureSelectionWidget()

        ipw.dlink(
            (self.structure_uploader, "structure_file"),
            (self.model, "structure_file"),
        )
        ipw.dlink(
            (self.structure_uploader, "structure_data"), (self.model, "structure")
        )

    def render(self):
        """Render the wizard's contents if not already rendered."""
        if self.rendered:
            return

        self.submit_btn = ipw.Button(
            description="Submit Structure",
            disabled=False,
            button_style="success",
            tooltip="Submit the structure to the workflow",
            icon="check",
            layout={"width": "60%", "height": "30px", "margin": "20px auto 8px"},
        )
        add_button_style_class(self.submit_btn)
        self.submit_btn.on_click(self.submit_structure)
        self.error = ipw.HTML("")

        self._update_children()
        self.rendered = True
        return

    def _update_children(self) -> None:
        self.children = [
            cif2j_button_style(),
            self.info,
            self.structure_uploader,
            self.error,
            self.submit_btn,
        ]
        return

    def submit_structure(self, _):
        """Submit the structure step."""
        self.error.value = ""
        if self.model.has_file or self.model.has_structure:
            self.submit_btn.disabled = True
            self.submit_btn.description = "Submitted"
            self.structure_uploader.disable(True)
            self.model.submitted = True
            # Mark the (collapsed) step as complete via the AWB wizard icon.
            self.state = self.State.SUCCESS
        else:
            self.error.value = "<p style='color:red;'>No structure provided.</p>"
            self.model.submitted = False
        return
