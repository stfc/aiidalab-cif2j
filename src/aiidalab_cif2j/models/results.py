"""Defines the MVC model for holding CIF2J results information."""

from traitlets import Bool

from aiidalab_cif2j.models.process import ProcessModel


class ResultsModel(ProcessModel):
    """MVC results step model."""

    blocked = Bool(True)
