"""Tests for the application's traitlets models.

These avoid instantiating real AiiDA ORM nodes (``StructureData``,
``SinglefileData``), which require a loaded AiiDA profile; CI runs these
tests without one, mirroring ``aiidalab-chemshell``'s profile-free test
suite.
"""

from aiidalab_cif2j.models.resources import MultiCodeResourcesModel
from aiidalab_cif2j.models.structure import StructureInputModel
from aiidalab_cif2j.models.workflow import Cif2JWorkflowModel, Protocol


def test_structure_input_model_defaults():
    """A fresh StructureInputModel has neither a structure nor a file."""
    model = StructureInputModel()
    assert not model.has_structure
    assert not model.has_file


def test_workflow_model_defaults():
    """A fresh Cif2JWorkflowModel has sensible defaults and no magnetic elements."""
    model = Cif2JWorkflowModel()
    assert model.protocol is Protocol.MODERATE
    assert model.magnetic_elements == []
    assert model.tb2j_parameters == {}
    assert model.tb2j_options == {}
    assert model.wannier90_withmpi is False


def test_workflow_model_accepts_magnetic_elements():
    """Setting magnetic_elements stores the given list."""
    model = Cif2JWorkflowModel()
    model.magnetic_elements = ["Fe", "Mn"]
    assert model.magnetic_elements == ["Fe", "Mn"]


def test_workflow_model_requires_pseudo_family():
    """Validation fails until a pseudopotential family is chosen."""
    model = Cif2JWorkflowModel()
    assert model.validate() is False
    model.pseudo_family = "SSSP/1.3/PBE/efficiency"
    assert model.validate() is True


def _resources_model(**codes) -> MultiCodeResourcesModel:
    model = MultiCodeResourcesModel()
    for name, label in codes.items():
        setattr(model, f"{name}_code", label)
    return model


def test_resources_model_requires_all_required_codes():
    """Validation fails if any required code is missing."""
    model = _resources_model(pw="pw@localhost", pw2wannier90="p2w@localhost")
    assert model.validate() is False


def test_resources_model_validates_with_all_required_codes():
    """Validation passes once all required codes are set."""
    model = _resources_model(
        pw="pw@localhost",
        pw2wannier90="p2w@localhost",
        wannier90="w90@localhost",
        tb2j="tb2j@localhost",
    )
    assert model.validate() is True
