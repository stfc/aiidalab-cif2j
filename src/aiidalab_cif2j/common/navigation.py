"""Module handling navigation controls within the app."""

from functools import partial

import ipywidgets as ipw

from aiidalab_cif2j.common.utils import add_button_style_class, cif2j_button_style
from aiidalab_cif2j.utils import open_link_in_new_tab

_APPS_DIRECTORY = "/apps/apps/"


class QuickAccessButtons(ipw.HBox):
    """Quick access buttons present in the apps header and start banner."""

    def __init__(self, **kwargs):
        """
        QuickAccessButtons constructor.

        Parameters
        ----------
        **kwargs :
            Keyword arguments passed to the `ipywidgets.HBox.__init__()`.
        """
        self.new_calc_link = ipw.Button(
            description="New Calculation",
            disabled=False,
            button_style="success",
            tooltip="Start a new calculation",
            icon="plus",
        )
        self.new_calc_link.on_click(
            partial(
                open_link_in_new_tab,
                _APPS_DIRECTORY + "cif2j/notebooks/main.ipynb",
            )
        )

        self.history_link = ipw.Button(
            description="History",
            disabled=False,
            button_style="primary",
            tooltip="View Calculation History",
            icon="history",
        )
        self.history_link.on_click(
            partial(
                open_link_in_new_tab,
                _APPS_DIRECTORY + "cif2j/notebooks/history.ipynb",
            )
        )

        self.resource_setup_link = ipw.Button(
            description="Setup Resources",
            disabled=False,
            button_style="primary",
            tooltip="Configure Computational Resources",
            icon="cogs",
        )
        self.resource_setup_link.on_click(
            partial(
                open_link_in_new_tab,
                _APPS_DIRECTORY + "cif2j/notebooks/resources.ipynb",
            )
        )

        self.docs_link = ipw.Button(
            description="Documentation",
            disabled=False,
            button_style="info",
            tooltip="Open Documentation",
            icon="book",
        )
        self.docs_link.on_click(
            partial(open_link_in_new_tab, "https://stfc.github.io/aiidalab-cif2j/")
        )

        children = [
            self.new_calc_link,
            self.history_link,
            self.resource_setup_link,
            self.docs_link,
        ]
        add_button_style_class(*children)
        super().__init__(
            children=[cif2j_button_style(), *children],
            layout={"margin": "auto"},
            **kwargs,
        )
        return
