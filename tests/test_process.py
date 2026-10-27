"""Tests for the Cif2JProcess builder-construction/submission logic.

``WannierTB2JWorkChain.get_builder_from_protocol``, ``load_code`` and
``aiida.engine.submit`` are all mocked out, so these tests run without a
configured AiiDA profile or the ``aiida-wannier90-workflows`` package (which
is not published on PyPI) installed.
"""

import sys
from enum import Enum
from types import ModuleType, SimpleNamespace
from unittest import mock

from aiidalab_cif2j.models.resources import MultiCodeResourcesModel
from aiidalab_cif2j.models.workflow import Cif2JWorkflowModel
from aiidalab_cif2j.process import Cif2JProcess, MainAppModel


class _FakeWannierProjectionType(Enum):
    ANALYTIC = "analytic"
    SCDM = "scdm"
    ATOMIC_PROJECTORS_QE = "atomic_projectors_qe"
    ATOMIC_PROJECTORS_OPENMX = "atomic_projectors_openmx"


def _install_fake_wannier90_workflows_module():
    """Install a stand-in for the (uninstalled) aiida_wannier90_workflows package."""
    common_types = ModuleType("aiida_wannier90_workflows.common.types")
    common_types.WannierProjectionType = _FakeWannierProjectionType
    package = ModuleType("aiida_wannier90_workflows")
    common = ModuleType("aiida_wannier90_workflows.common")
    sys.modules["aiida_wannier90_workflows"] = package
    sys.modules["aiida_wannier90_workflows.common"] = common
    sys.modules["aiida_wannier90_workflows.common.types"] = common_types


def _fake_main_app_model(structure=None, structure_file=None) -> MainAppModel:
    # A SimpleNamespace stand-in for the structure model avoids triggering
    # ``StructureInputModel``'s ``Instance(StructureData)``/
    # ``Instance(SinglefileData)`` trait validation, which would otherwise
    # require real AiiDA ORM node instances (and therefore a loaded profile).
    return SimpleNamespace(
        structure_model=SimpleNamespace(
            has_structure=structure is not None,
            has_file=structure_file is not None,
            structure=structure,
            structure_file=structure_file,
        ),
        workflow_model=Cif2JWorkflowModel(),
        resources_model=MultiCodeResourcesModel(),
    )


# --- validate_model -------------------------------------------------------


def test_validate_model_requires_structure():
    """Validation fails when neither a structure nor a structure file is set."""
    model = _fake_main_app_model()
    assert Cif2JProcess.validate_model(model) is False


def test_validate_model_passes_with_structure_file():
    """Validation passes when a structure file is provided."""
    model = _fake_main_app_model(structure_file=object())
    assert Cif2JProcess.validate_model(model) is True


# --- submit_process ---------------------------------------------------------


def test_submit_process_builds_and_submits():
    """submit_process resolves codes, builds via get_builder_from_protocol, submits."""
    _install_fake_wannier90_workflows_module()

    model = _fake_main_app_model(structure_file=object())
    model.resources_model.pw_code = "pw@localhost"
    model.resources_model.pw2wannier90_code = "pw2wannier90@localhost"
    model.resources_model.wannier90_code = "wannier90@localhost"
    model.resources_model.tb2j_code = "tb2j@localhost"
    model.resources_model.pseudo_family = "SSSP/1.3/PBE/efficiency"
    model.resources_model.process_label = "my label"
    model.resources_model.process_description = "my description"

    fake_builder = SimpleNamespace()
    fake_workchain = SimpleNamespace(
        get_builder_from_protocol=mock.Mock(return_value=fake_builder)
    )
    fake_node = SimpleNamespace(label="", description="")

    process = Cif2JProcess(model)
    with (
        mock.patch("aiidalab_cif2j.process.load_code", side_effect=lambda label: label),
        mock.patch(
            "aiidalab_cif2j.process.WorkflowFactory", return_value=fake_workchain
        ),
        mock.patch("aiidalab_cif2j.process.submit", return_value=fake_node),
    ):
        process.submit_process()

    assert process.node is fake_node
    assert fake_node.label == "my label"
    assert fake_node.description == "my description"

    call_kwargs = fake_workchain.get_builder_from_protocol.call_args.kwargs
    assert call_kwargs["codes"] == {
        "pw": "pw@localhost",
        "pw2wannier90": "pw2wannier90@localhost",
        "wannier90": "wannier90@localhost",
        "tb2j": "tb2j@localhost",
    }
    assert call_kwargs["pseudo_family"] == "SSSP/1.3/PBE/efficiency"
    assert call_kwargs["protocol"] == "moderate"
    assert "magnetic_elements" not in call_kwargs
