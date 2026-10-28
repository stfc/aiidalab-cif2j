"""Defines the MVC model for computational resource configuration for AiiDA."""

import traitlets as tl

#: Codes required to run ``WannierTB2JWorkChain.get_builder_from_protocol``.
REQUIRED_CODES = ("pw", "pw2wannier90", "wannier90", "tb2j")

#: Optional codes accepted by ``Wannier90BandsWorkChain``/``get_builder_from_protocol``.
OPTIONAL_CODES = ("projwfc", "open_grid")


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
