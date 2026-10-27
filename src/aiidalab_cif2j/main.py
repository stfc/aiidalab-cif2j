"""Defines the AiiDAlab CIF2J "New Calculation" application page."""

from datetime import datetime

import ipywidgets as ipw
from IPython.display import display

from aiidalab_cif2j.common.navigation import QuickAccessButtons
from aiidalab_cif2j.common.theme import APP_ROOT_CLASS, cif2j_appbar, cif2j_theme
from aiidalab_cif2j.process import MainAppModel
from aiidalab_cif2j.wizards.main_app import MainWizardWidget


class MainApp:
    """The "New Calculation" AiiDAlab CIF2J application page."""

    def __init__(self):
        """MainApp constructor."""
        self.model = MainAppModel()
        wizard = MainWizardWidget(self.model)
        self.view = AppView(wizard, "Welcome to the ALC's AiiDAlab CIF2J App")
        display(self.view)


class AppView(ipw.VBox):
    """The application view (header, navigation, body wizard, footer)."""

    def __init__(self, wizard: ipw.Widget, subtitle: str, **kwargs):
        """
        AppView constructor.

        Parameters
        ----------
        wizard : ipw.Widget
            The wizard widget rendered as the page body.
        subtitle : str
            The page subtitle displayed beneath the logo.
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        logo = ipw.HTML(
            """
            <div class="app-container logo" style="width: 500px;">
                <img src="../images/cif2j.png" alt="CIF2J Logo" />
            </div>
            """,
            layout={"margin": "auto"},
        )

        subtitle_widget = ipw.HTML(
            f"""
            <h2 id='subtitle' style="text-align: center;">{subtitle}</h2>
            """
        )

        nav_btns = QuickAccessButtons()

        header = cif2j_appbar([logo, nav_btns])

        footer = ipw.HTML(
            f"""
            <footer>
                Copyright (c) {datetime.now().year} Ada Lovelace Centre
                (STFC) <br>
            </footer>
            """,
            layout={"align-content": "right"},
        )

        self.main = wizard

        super().__init__(
            layout={},
            children=[cif2j_theme(), header, subtitle_widget, self.main, footer],
            **kwargs,
        )
        self.add_class(APP_ROOT_CLASS)
