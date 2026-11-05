"""Defines a resource setup widget based on foundations from aiidalab-widgets-base.

Unlike ``aiidalab-chemshell``'s single containerizable code,
``WannierTB2JWorkChain`` chains several HPC-style codes (``pw.x``,
``pw2wannier90.x``, ``wannier90.x``, TB2J). None of them need a container
though (all are plain conda/pip packages), so :class:`QuickSetupLocalWidget`
below provides the same kind of one-click convenience as
``ChemShellContainerSetupWidget``, just via ``local_install`` instead of a
container engine. For production runs on real HPC resources, manual/remote
code setup remains the primary option.
"""

import asyncio
import concurrent.futures
import html
import threading

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from traitlets import HasTraits, Unicode, observe

from aiidalab_cif2j import local_install
from aiidalab_cif2j.common.utils import add_button_style_class, cif2j_button_style


class CodeSetupWidget(ipw.VBox, HasTraits):
    """Widget to setup a new code instance."""

    _database_source = Unicode(
        "",
        allow_none=False,
    )

    def __init__(self, **kwargs):
        self.source = ipw.Text(
            value=self._database_source, description="Source: ", layout={"width": "80%"}
        )
        ipw.dlink((self.source, "value"), (self, "_database_source"))
        self.resource_widget = awb.computational_resources.ResourceSetupBaseWidget()
        self.setup_message = awb.utils.StatusHTML(clear_after=15)
        ipw.dlink(
            (self.resource_widget, "message"),
            (self.setup_message, "message"),
        )

        self.source.value = "https://raw.githubusercontent.com/stfc/alc-ux/refs/heads/main/resources/remotes.json"

        children = [
            ipw.HTML("<hr>"),
            self.source,
            ipw.HTML("<hr>"),
            self.resource_widget,
            self.setup_message,
        ]
        super().__init__(children=children, **kwargs)
        return

    @observe("_database_source")
    def _update_database_source(self, _):
        self.resource_widget.comp_resources_database.database_source = (
            self._database_source
        )
        return


class QuickSetupLocalWidget(ipw.VBox):
    """Widget for one-click local install of QE/Wannier90/TB2J and their codes.

    Each button installs independently (e.g. a user who already has Quantum
    ESPRESSO via the AiiDAlab Quantum ESPRESSO app can install just
    `wannier90` here, without pulling in `qe` too), but all three write into
    the same shared conda environment, so all three buttons are disabled
    while any one is running to avoid concurrent conda/pip operations against
    it.
    """

    _SPINNER = "<i class='fa fa-spinner fa-spin fa-fw'></i>"

    def __init__(self, **kwargs):
        self._buttons: list[ipw.Button] = []

        qe_row, self.qe_status = self._make_row(
            "Install Quantum ESPRESSO",
            "Install Quantum ESPRESSO into a local conda environment and "
            "create pw.x/pw2wannier90.x/projwfc.x/open_grid.x codes",
            self._on_qe_clicked,
        )
        wannier90_row, self.wannier90_status = self._make_row(
            "Install Wannier90",
            "Install Wannier90 into a local conda environment and create a "
            "wannier90.x code",
            self._on_wannier90_clicked,
        )
        tb2j_row, self.tb2j_status = self._make_row(
            "Install TB2J",
            "Install TB2J via pip and create a wann2J.py code",
            self._on_tb2j_clicked,
        )

        children = [
            cif2j_button_style(),
            qe_row,
            wannier90_row,
            tb2j_row,
        ]
        super().__init__(children=children, **kwargs)
        return

    def _make_row(
        self, description: str, tooltip: str, handler
    ) -> tuple[ipw.VBox, ipw.HTML]:
        """Build a `[button, status]` row and register the button for disabling."""
        button = ipw.Button(
            description=description,
            button_style="success",
            tooltip=tooltip,
            icon="download",
            layout={"width": "auto"},
        )
        button.on_click(handler)
        add_button_style_class(button)
        status = ipw.HTML("")
        self._buttons.append(button)
        return ipw.VBox(children=[button, status]), status

    def _set_status(self, status: ipw.HTML, message: str, level: str = "info") -> None:
        """Update `status` with a colour-coded message."""
        colours = {
            "info": "#31708f",
            "success": "#3c763d",
            "error": "#a94442",
            "working": "#8a6d3b",
        }
        colour = colours.get(level, colours["info"])
        status.value = f"<p style='color:{colour};'>{message}</p>"
        return

    @staticmethod
    def _error_html(exc: Exception) -> str:
        """Format an exception's message for safe, readable HTML display.

        `local_install._run_checked` raises errors carrying raw subprocess
        output (conda/pip logs), which may be multi-line and contain
        characters HTML would otherwise interpret as markup.
        """
        return html.escape(str(exc)).replace("\n", "<br>")

    def _set_buttons_disabled(self, disabled: bool) -> None:
        """Disable (or re-enable) every button, to serialise shared-env access."""
        for button in self._buttons:
            button.disabled = disabled
        return

    def _launch(self, target) -> None:
        """Disable all buttons and run `target` on a background thread."""
        self._set_buttons_disabled(True)
        # Capture the notebook's event loop so AiiDA ORM work can be marshalled
        # back onto the main thread (see ``_call_on_loop``).
        self._loop = asyncio.get_event_loop()
        thread = threading.Thread(target=self._run, args=(target,), daemon=True)
        thread.start()
        return

    def _run(self, target) -> None:
        """Run `target`, always re-enabling the buttons afterwards."""
        try:
            target()
        finally:
            self._set_buttons_disabled(False)
        return

    def _call_on_loop(self, func):
        """Run ``func`` on the notebook's event loop and return its result.

        AiiDA's storage session is bound to the (main) thread that loaded the
        profile. ORM operations must therefore run on that thread.
        """
        future: concurrent.futures.Future = concurrent.futures.Future()

        def _wrapper():
            try:
                future.set_result(func())
            except Exception as exc:  # noqa: BLE001 - propagated to the worker
                future.set_exception(exc)

        self._loop.call_soon_threadsafe(_wrapper)
        return future.result()

    def _ensure_qe(self, status: ipw.HTML) -> None:
        """Install `qe` via conda, unless already covered."""
        # ORM lookups (code detection) must run on the main thread.
        need_qe = self._call_on_loop(local_install.qe_needed)

        if not need_qe:
            self._set_status(
                status,
                "Quantum ESPRESSO codes already exist (e.g. from the "
                "AiiDAlab Quantum ESPRESSO app); skipping install.",
                "info",
            )
        elif local_install.qe_installed():
            self._set_status(
                status,
                "Quantum ESPRESSO is already installed; reusing the "
                "existing environment.",
                "info",
            )
        else:
            self._set_status(
                status,
                f"{self._SPINNER} Installing Quantum ESPRESSO via conda "
                "(this can take several minutes) ...",
                "working",
            )
            local_install.install_qe()
        return

    def _ensure_wannier90(self, status: ipw.HTML) -> None:
        """Install `wannier90` via conda, unless already covered."""
        need_wannier90 = self._call_on_loop(local_install.wannier90_needed)

        if not need_wannier90:
            self._set_status(
                status, "A Wannier90 code already exists; skipping install.", "info"
            )
        elif local_install.wannier90_installed():
            self._set_status(
                status,
                "Wannier90 is already installed; reusing the existing environment.",
                "info",
            )
        else:
            self._set_status(
                status,
                f"{self._SPINNER} Installing Wannier90 via conda ...",
                "working",
            )
            local_install.install_wannier90()
        return

    def _ensure_tb2j(self, status: ipw.HTML) -> None:
        """Install TB2J via pip, unless already covered."""
        need_tb2j = self._call_on_loop(local_install.tb2j_needed)

        if not need_tb2j:
            self._set_status(
                status, "A TB2J code already exists; skipping install.", "info"
            )
        elif local_install.tb2j_installed():
            self._set_status(
                status,
                "TB2J is already installed; reusing the existing environment.",
                "info",
            )
        else:
            self._set_status(
                status, f"{self._SPINNER} Installing TB2J via pip ...", "working"
            )
            local_install.install_tb2j()
        return

    def _create_codes(self, code_names, status: ipw.HTML) -> None:
        """Create (or reuse) each of `code_names` and report the outcome."""
        self._set_status(status, f"{self._SPINNER} Creating AiiDA codes ...", "working")
        created = []
        reused = []
        for code_name in code_names:
            existed = self._call_on_loop(
                lambda name=code_name: local_install.code_exists(name)
            )
            self._call_on_loop(lambda name=code_name: local_install.create_code(name))
            (reused if existed else created).append(code_name)

        message = "Codes ready: "
        if created:
            message += f"created {', '.join(created)}"
        if created and reused:
            message += "; "
        if reused:
            message += f"reused {', '.join(reused)}"
        message += '. Click "Refresh all" in the resources step to see them.'
        self._set_status(status, message, "success")
        return

    def _run_qe(self) -> None:
        """Install Quantum ESPRESSO and create its codes (background thread)."""
        from shutil import which

        try:
            if not which("conda"):
                self._set_status(
                    self.qe_status,
                    "Unable to install locally: conda is not available in "
                    "this environment.",
                    "error",
                )
                return
            self._ensure_qe(self.qe_status)
            self._create_codes(local_install.QE_CODES, self.qe_status)
        except Exception as exc:  # noqa: BLE001 - surface any failure in the UI
            self._set_status(
                self.qe_status, f"Unexpected error: {self._error_html(exc)}", "error"
            )
        return

    def _run_wannier90(self) -> None:
        """Install Wannier90 and create its code (background thread)."""
        from shutil import which

        try:
            if not which("conda"):
                self._set_status(
                    self.wannier90_status,
                    "Unable to install locally: conda is not available in "
                    "this environment.",
                    "error",
                )
                return
            self._ensure_wannier90(self.wannier90_status)
            self._create_codes(("wannier90",), self.wannier90_status)
        except Exception as exc:  # noqa: BLE001 - surface any failure in the UI
            self._set_status(
                self.wannier90_status,
                f"Unexpected error: {self._error_html(exc)}",
                "error",
            )
        return

    def _run_tb2j(self) -> None:
        """Install TB2J and create its code (background thread)."""
        try:
            self._ensure_tb2j(self.tb2j_status)
            self._create_codes(("tb2j",), self.tb2j_status)
        except Exception as exc:  # noqa: BLE001 - surface any failure in the UI
            self._set_status(
                self.tb2j_status, f"Unexpected error: {self._error_html(exc)}", "error"
            )
        return

    def _on_qe_clicked(self, _=None) -> None:
        self._launch(self._run_qe)
        return

    def _on_wannier90_clicked(self, _=None) -> None:
        self._launch(self._run_wannier90)
        return

    def _on_tb2j_clicked(self, _=None) -> None:
        self._launch(self._run_tb2j)
        return
