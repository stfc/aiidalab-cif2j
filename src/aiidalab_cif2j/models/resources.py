"""Defines the MVC model for computational resource configuration for AiiDA."""

import traitlets as tl

#: Codes required to run ``WannierTB2JWorkChain.get_builder_from_protocol``.
REQUIRED_CODES = ("pw", "pw2wannier90", "wannier90", "tb2j")

#: Optional codes accepted by ``Wannier90BandsWorkChain``/``get_builder_from_protocol``.
OPTIONAL_CODES = ("projwfc", "open_grid")

#: Codes that actually run under MPI. ``pw``/``pw2wannier90`` resources are
#: computed internally by ``Wannier90BandsWorkChain`` from the protocol/
#: structure (no override exposed, so no MPI controls are shown for them
#: either, see ``aiidalab_cif2j.process`` for how that could be done via an
#: ``overrides`` dict if ever needed). ``tb2j`` (``wann2J.py``) is a
#: single-process Python script; ``aiida-cif2j``'s own README documents
#: setting ``with_mpi: false`` on its ``Code``, so it's excluded here too.
MPI_CAPABLE_CODES = ("wannier90",)


class MultiCodeResourcesModel(tl.HasTraits):
    """Model for the resource setup stage.

    Unlike a single-code app, ``WannierTB2JWorkChain`` chains several codes
    together (Quantum ESPRESSO's ``pw.x``/``pw2wannier90.x``, Wannier90's
    ``wannier90.x`` and TB2J), plus two optional codes
    (``projwfc.x``/``open_grid.x``) used by some Wannier90 projection types.
    Each code label is held as its own trait so the wizard step can render one
    selector row per code.
    """

    pw_code = tl.Unicode("", allow_none=True).tag(sync=True)
    pw2wannier90_code = tl.Unicode("", allow_none=True).tag(sync=True)
    wannier90_code = tl.Unicode("", allow_none=True).tag(sync=True)
    tb2j_code = tl.Unicode("", allow_none=True).tag(sync=True)
    projwfc_code = tl.Unicode("", allow_none=True).tag(sync=True)
    open_grid_code = tl.Unicode("", allow_none=True).tag(sync=True)

    #: MPI settings for the codes in :data:`MPI_CAPABLE_CODES`. ``wannier90``
    #: is forced to single-task resources by ``get_builder_from_protocol``
    #: unless ``wannier90_withmpi`` is set (see ``aiida_cif2j.workflows.wannier``);
    #: ``wannier90_num_mpiprocs`` is not yet forwarded anywhere, since that
    #: workflow only exposes a boolean switch, not a process count.
    wannier90_withmpi = tl.Bool(False).tag(sync=True)
    wannier90_num_mpiprocs = tl.Int(1).tag(sync=True)

    process_label = tl.Unicode("").tag(sync=True)
    process_description = tl.Unicode("").tag(sync=True)
    submitted = tl.Bool(False).tag(sync=True)

    default_guide = """
        <p>
            Configure the computational resources required to run the Wannier90 +
            TB2J workflow. A code must be selected for each of Quantum ESPRESSO's
            <code>pw.x</code> and <code>pw2wannier90.x</code>, Wannier90's
            <code>wannier90.x</code>, and TB2J. <code>projwfc.x</code>/
            <code>open_grid.x</code> are only required for some Wannier90
            projection types. Additionally, you can provide a label and
            description for the AiiDA process that will be created.
        </p>
    """

    def code_label(self, code_name: str) -> str:
        """Return the configured code label for a given code name.

        Parameters
        ----------
        code_name : str
            One of :data:`REQUIRED_CODES`/:data:`OPTIONAL_CODES`.

        Returns
        -------
        str
            The configured ``label@computer`` for the code, or an empty string.
        """
        return getattr(self, f"{code_name}_code", "")

    def code_withmpi(self, code_name: str) -> bool:
        """Return whether MPI is enabled for a given code.

        Parameters
        ----------
        code_name : str
            One of :data:`MPI_CAPABLE_CODES`.

        Returns
        -------
        bool
            The configured MPI flag for the code, or False if it has none.
        """
        return getattr(self, f"{code_name}_withmpi", False)

    def code_num_mpiprocs(self, code_name: str) -> int:
        """Return the configured number of MPI processes for a given code.

        Parameters
        ----------
        code_name : str
            One of :data:`MPI_CAPABLE_CODES`.

        Returns
        -------
        int
            The configured process count for the code, or 1 if it has none.
        """
        return getattr(self, f"{code_name}_num_mpiprocs", 1)

    def validate(self) -> bool:
        """
        Validate the model's inputs.

        Returns
        -------
        bool
            True if all required codes are set, False otherwise.
        """
        missing = [name for name in REQUIRED_CODES if not self.code_label(name)]
        if missing:
            print(f"ERROR: No code selected for: {', '.join(missing)}.")
            return False
        return True
