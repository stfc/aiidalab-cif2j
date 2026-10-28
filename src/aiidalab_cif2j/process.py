"""Module for handling AiiDA processes."""

import ipywidgets as ipw
import traitlets as tl
from aiida.engine import submit
from aiida.orm import load_code
from aiida.plugins import WorkflowFactory

from aiidalab_cif2j.models.resources import OPTIONAL_CODES, MultiCodeResourcesModel
from aiidalab_cif2j.models.results import ResultsModel
from aiidalab_cif2j.models.structure import StructureInputModel
from aiidalab_cif2j.models.workflow import Cif2JWorkflowModel


class MainAppModel(tl.HasTraits):
    """The AiiDAlab CIF2J application's "New Calculation" MVC model."""

    block_results = tl.Bool(True, allow_none=False)

    def __init__(self):
        """MainAppModel constructor."""
        super().__init__()
        self.structure_model = StructureInputModel()
        self.workflow_model = Cif2JWorkflowModel()
        self.resources_model = MultiCodeResourcesModel()
        self.results_model = ResultsModel()

        self.resources_model.observe(self._submit_model, "submitted")
        ipw.dlink((self, "block_results"), (self.results_model, "blocked"))

        self.process = None

        return

    def _submit_model(self, _) -> None:
        """Handle the submission of the AiiDA process."""
        if Cif2JProcess.validate_model(self):
            self.process = Cif2JProcess(self)
            self.process.submit_process()
            self.block_results = False
            self.results_model.process_uuid = self.process.node.uuid
        else:
            print("ERROR: Input Validation Failed")
        return


class Cif2JProcess:
    """Class to handle a CIF2J (Wannier90 + TB2J) AiiDA process."""

    def __init__(self, model: MainAppModel):
        """
        Cif2JProcess constructor.

        Parameters
        ----------
        model : MainAppModel
            The application model containing all necessary data.
        """
        self.model = model
        self.node = None
        return

    @classmethod
    def validate_model(cls, model: MainAppModel) -> bool:
        """
        Validate the main application model.

        Parameters
        ----------
        model : MainAppModel
            The application model to validate.

        Returns
        -------
        bool
            True if the model is valid, False otherwise.
        """
        structure_model = model.structure_model
        if not structure_model.has_structure and not structure_model.has_file:
            print("No structure provided.")
            return False
        if not model.workflow_model.validate():
            return False
        return True

    def submit_process(self) -> None:
        """Build and submit the ``WannierTB2JWorkChain``."""
        # Deferred: aiida_cif2j/aiida_wannier90_workflows aren't guaranteed to
        # be importable in every environment that imports this module (e.g.
        # unit tests without the full plugin stack installed).
        from aiida_wannier90_workflows.common.types import WannierProjectionType

        workflow_model = self.model.workflow_model
        resources_model = self.model.resources_model

        codes = {
            name: load_code(resources_model.code_label(name))
            for name in ("pw", "pw2wannier90", "wannier90", "tb2j")
        }
        for name in OPTIONAL_CODES:
            if label := resources_model.code_label(name):
                codes[name] = load_code(label)

        structure = (
            self.model.structure_model.structure_file
            if self.model.structure_model.has_file
            else self.model.structure_model.structure
        )

        builder_kwargs = {
            "codes": codes,
            "structure": structure,
            "pseudo_family": workflow_model.pseudo_family,
            "protocol": workflow_model.protocol.value,
            "spin_type": workflow_model.spin_type,
            "electronic_type": workflow_model.electronic_type,
            "projection_type": getattr(
                WannierProjectionType, workflow_model.projection_type.name
            ),
            "wannier90_withmpi": workflow_model.wannier90_withmpi,
        }
        if workflow_model.magnetic_elements:
            builder_kwargs["magnetic_elements"] = list(workflow_model.magnetic_elements)
        if workflow_model.tb2j_parameters:
            builder_kwargs["tb2j_parameters"] = dict(workflow_model.tb2j_parameters)
        if workflow_model.tb2j_options:
            builder_kwargs["tb2j_options"] = dict(workflow_model.tb2j_options)

        workchain = WorkflowFactory("cif2j.wannier_tb2j")
        # `get_builder_from_protocol` already fills in each sub-process's own
        # `metadata.options.resources` from the protocol/structure (and forces
        # `wannier90.x` serial unless `wannier90_withmpi` is set); per-code
        # resource overrides aren't exposed in this app yet.
        builder = workchain.get_builder_from_protocol(**builder_kwargs)

        self.node = submit(builder)
        self.node.label = resources_model.process_label
        self.node.description = resources_model.process_description
        return
