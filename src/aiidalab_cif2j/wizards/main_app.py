"""Defines the core wizard widget for the AiiDAlab CIF2J application page."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw

from aiidalab_cif2j.process import MainAppModel
from aiidalab_cif2j.wizards.resources import ComputationalResourcesWizardStep
from aiidalab_cif2j.wizards.results import ResultsWizardStep
from aiidalab_cif2j.wizards.structure import StructureWizardStep
from aiidalab_cif2j.wizards.workflow import WorkflowWizardStep


class MainWizardWidget(ipw.VBox):
    """The "New Calculation" application construction wizard."""

    def __init__(self, model: MainAppModel, **kwargs):
        """
        MainWizardWidget constructor.

        Parameters
        ----------
        model : MainAppModel
            The application model backing the wizard.
        **kwargs :
            Keyword arguments passed to the `ipywidgets.VBox.__init__()`.
        """
        self.structure_step = StructureWizardStep(model.structure_model)
        self.workflow_step = WorkflowWizardStep(model.workflow_model)
        self.resources_step = ComputationalResourcesWizardStep(model.resources_model)
        self.results_step = ResultsWizardStep(model.results_model)

        self._wizard_app_widget = awb.WizardAppWidget(
            steps=[
                ("Select Structure", self.structure_step),
                ("Configure Workflow", self.workflow_step),
                ("Configure Computational Resources", self.resources_step),
                ("Results", self.results_step),
            ]
        )

        self._wizard_app_widget.observe(
            self.on_step_change,
            "selected_index",
        )

        self.results_step.disabled = True
        self._model = model
        # Hide the header
        self._wizard_app_widget.children[0].layout.display = "none"

        super().__init__(
            children=[self._wizard_app_widget],
            **kwargs,
        )

        self._wizard_app_widget.selected_index = None

        return

    @property
    def steps(self):
        """Alias to the wizard's steps list."""
        return self._wizard_app_widget.steps

    def on_step_change(self, change):
        """Switch between wizard steps when selected by the user."""
        if (step_index := change["new"]) is not None:
            step = self.steps[step_index][1]
            step.render()
        return
