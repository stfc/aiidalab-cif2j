"""The workflow configuration model for the Wannier90 + TB2J pipeline.

Enum choices mirror the parameters accepted by
``WannierTB2JWorkChain.get_builder_from_protocol``
(``aiida_cif2j.workflows.wannier``). ``SpinType``/``ElectronicType`` are
imported directly from ``aiida-quantumespresso`` (a normal PyPI dependency of
this app). ``WannierProjectionChoice`` is defined locally rather than
importing ``aiida_wannier90_workflows.common.types.WannierProjectionType`` at
module level, since that package is not published on PyPI and must not be a
hard import-time dependency of this module; the submission layer
(``aiidalab_cif2j.process``) resolves a chosen name to the real enum member
with a deferred import.
"""

from enum import Enum

from aiida_quantumespresso.common.types import ElectronicType, SpinType
from traitlets import Bool, Dict, HasTraits, List, Unicode, UseEnum


class Protocol(Enum):
    """Protocol presets forwarded to ``get_builder_from_protocol``."""

    FAST = "fast"
    MODERATE = "moderate"
    PRECISE = "precise"


class WannierProjectionChoice(Enum):
    """Mirrors ``aiida_wannier90_workflows``'s ``WannierProjectionType`` members."""

    ANALYTIC = "analytic"
    SCDM = "scdm"
    ATOMIC_PROJECTORS_QE = "atomic_projectors_qe"
    ATOMIC_PROJECTORS_OPENMX = "atomic_projectors_openmx"


class Cif2JWorkflowModel(HasTraits):
    """Model for the Wannier90 + TB2J workflow parameters."""

    protocol = UseEnum(Protocol, Protocol.MODERATE, allow_none=False)
    spin_type = UseEnum(SpinType, SpinType.COLLINEAR, allow_none=False)
    electronic_type = UseEnum(ElectronicType, ElectronicType.METAL, allow_none=False)
    projection_type = UseEnum(
        WannierProjectionChoice, WannierProjectionChoice.ANALYTIC, allow_none=False
    )

    #: Pseudopotential family forwarded to ``get_builder_from_protocol``, e.g.
    #: ``"SSSP/1.3/PBE/efficiency"``.
    pseudo_family = Unicode("", allow_none=True)

    #: Empty ⇒ let ``WannierTB2JWorkChain`` auto-detect magnetic elements from a
    #: ``MagneticStructureData`` input.
    magnetic_elements = List(trait=Unicode(), default_value=[])

    #: Additional ``tb2j.parameters``/``tb2j.metadata.options`` overrides, edited
    #: as JSON in the wizard's "Advanced" section.
    tb2j_parameters = Dict(default_value={})
    tb2j_options = Dict(default_value={})

    #: Forced serial by default; see ``get_builder_from_protocol``'s own
    #: ``wannier90_withmpi`` docstring for why.
    wannier90_withmpi = Bool(False)

    def validate(self) -> bool:
        """
        Validate the model's inputs.

        Returns
        -------
        bool
            True if a pseudopotential family has been selected, False otherwise.
        """
        if not self.pseudo_family:
            print("ERROR: No pseudopotential family selected.")
            return False
        return True
