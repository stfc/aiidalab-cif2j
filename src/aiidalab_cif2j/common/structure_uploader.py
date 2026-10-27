"""Widget for selecting an input structure from various sources."""

import ipywidgets as ipw
from aiida.orm import SinglefileData, StructureData
from alc_aiidalab_widgets.widgets import (
    AiiDADatabaseQueryWidget,
    FileUploadWidget,
    StructureViewWidget,
)
from traitlets import HasTraits, Instance

#: File extensions accepted by the upload tab. ``parse_magnetic_structure`` in
#: ``aiida_cif2j.calculations.utils`` reads CIF/MCIF files.
_VALID_EXTENSIONS = (".cif", ".mcif")


class StructureSelectionWidget(ipw.VBox, HasTraits):
    """Widget for selecting an input CIF/MCIF structure from various sources."""

    structure_data = Instance(StructureData, allow_none=True)
    structure_file = Instance(SinglefileData, allow_none=True)

    def __init__(self, **kwargs):
        """
        StructureSelectionWidget constructor.

        Parameters
        ----------
        **kwargs :
            Keyword arguments passed to the parent class's constructor.
        """
        super().__init__(**kwargs)
        # upload file
        self.file_input_widget = ipw.VBox()
        self.file_uploader = FileUploadWidget(description="CIF/MCIF file: ")
        self.file_input_widget.children = [
            self.file_uploader,
        ]
        self.file_uploader.observe(self._on_file_upload, "file")
        ipw.dlink((self.file_uploader, "file"), (self, "structure_file"))

        # AiiDA database
        self.database_widget = AiiDADatabaseQueryWidget(
            title="AiiDA Database",
            query=[SinglefileData, StructureData],
        )
        self.database_widget.observe(self._on_database_search, "data_object")

        self.tabs = ipw.Tab()
        self.tabs.children = [self.file_input_widget, self.database_widget]
        self.tabs.set_title(0, "Upload File")
        self.tabs.set_title(1, "AiiDA Database")

        self.error = ipw.HTML("")
        self.viewer = ipw.HTML("<p>No structure found...</p>")

        self.children = [self.tabs, self.error, self.viewer]

        return

    def _on_file_upload(self, change: dict) -> None:
        """When file upload button is pressed."""
        if change["new"] == change["old"]:
            return
        uploaded = self.file_uploader.file
        if uploaded and not uploaded.filename.lower().endswith(_VALID_EXTENSIONS):
            self.error.value = (
                "<p style='color:red;'>Structure input must be a "
                "<code>.cif</code> or <code>.mcif</code> file.</p>"
            )
            self.structure_file = None
            self.viewer = ipw.HTML("<p>No structure found...</p>")
            self._update_children()
            return
        self.error.value = ""
        self.viewer = StructureViewWidget(
            uploaded,
            layout={"margin": "auto"},
        )
        self._update_children()
        return

    def _on_database_search(self, change: dict) -> None:
        """When data is loaded from AiiDA database."""
        if change["new"] == change["old"]:
            return
        self.error.value = ""
        if isinstance(change["new"], SinglefileData):
            if self.structure_data:
                self.structure_data = None
            self.structure_file = change["new"]
        elif isinstance(change["new"], StructureData):
            if self.structure_file:
                self.structure_file = None
            self.structure_data = change["new"]
        self.viewer = StructureViewWidget(
            change["new"],
            layout={"margin": "auto"},
        )
        self._update_children()
        return

    def _update_children(self) -> None:
        self.children = [
            self.tabs,
            self.error,
            self.viewer,
        ]
        return

    def disable(self, val: bool = True) -> None:
        """Disable the widget and all children."""
        for child in self.tabs.children:
            try:
                child.disable(True)
            except AttributeError:
                pass
