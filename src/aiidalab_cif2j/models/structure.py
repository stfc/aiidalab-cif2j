"""The structure input model for CIF2J input configuration."""

from aiida.orm import SinglefileData, StructureData
from traitlets import Bool, HasTraits, Instance, observe


class StructureInputModel(HasTraits):
    """Model for structure selection and manipulation.

    The resolved structure is a CIF/MCIF file (``structure_file``) or an
    already-parsed AiiDA ``StructureData``/``MagneticStructureData`` node
    (``structure``) — the two inputs ``WannierTB2JWorkChain.structure`` accepts
    directly.
    """

    structure = Instance(StructureData, allow_none=True)
    structure_file = Instance(SinglefileData, allow_none=True)
    submitted = Bool(False).tag(sync=True)

    @property
    def has_structure(self) -> bool:
        """True if a StructureData object has been attached to the model."""
        return self.structure is not None

    @property
    def has_file(self) -> bool:
        """True if a raw structure file object has been attached to the model."""
        return self.structure_file is not None

    @observe("structure")
    def _update_structure(self, _) -> None:
        """Clear other inputs if a StructureData object is provided."""
        if self.structure is not None:
            self.structure_file = None
        return

    @observe("structure_file")
    def _update_structure_file(self, _) -> None:
        """Clear other inputs if a structure file is provided."""
        if self.structure_file is not None:
            self.structure = None
        return
