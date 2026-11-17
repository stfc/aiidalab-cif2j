"""Defines a custom AiiDA node visualiser."""

import aiidalab_widgets_base as awb
import ipywidgets as ipw
from aiida.common.links import LinkType
from aiida.orm import Node, ProcessNode
from alc_aiidalab_widgets.viewers import ALC_AIIDA_VIEWER_MAPPING
from IPython.display import clear_output, display
from traitlets import Instance, observe


class CustomAiidaNodeViewWidget(ipw.VBox):
    """
    Custom viewer based on a specific AiiDA node type.

    An extension of the aiidalab_widgets_base.viewers.AiidaNodeViewWidget
    enabling more customisability when registering viewers with nodes
    returned from CIF2J jobs. The main outline is taken from the base
    aiidalab_widgets_base viewer with an extended viewer() method which
    allows handling of node types which the base viewer has no registered
    visualisation widgets.
    """

    node = Instance(Node, allow_none=True)

    def __init__(self, **kwargs):
        """CustomAiidaNodeViewWidget Constructor."""
        self._output = ipw.Output()
        self.node_views = {}
        self.node_view_loading_message = awb.loaders.LoadingWidget("Loading Node View")
        super().__init__(**kwargs)
        self.add_class("aiida-node-view-widget")

    @observe("node")
    def _observe_node(self, change):
        if not ((node := change["new"]) and node != change["old"]):
            return
        if node.uuid in self.node_views:
            self.children = [self.node_views[node.uuid]]
            return
        self.children = [self.node_view_loading_message]
        node_view = self._viewer(node)
        if isinstance(node_view, ipw.DOMWidget):
            self.node_views[node.uuid] = node_view
            self.children = [node_view]
        else:
            with self._output:
                clear_output()
                if change["new"]:
                    display(node_view)
            self.children = [self._output]

    def _viewer(self, node: Node, **kwargs):
        """Create a viewer based on the type of Node being visualised."""
        # First look for ALC developed node viewers
        _viewer = ALC_AIIDA_VIEWER_MAPPING.get(node.node_type)
        if not _viewer:
            # Fall back to default AiiDAlab developed node viewers
            _viewer = awb.viewers.AIIDA_VIEWER_MAPPING.get(node.node_type)
        if isinstance(node, ProcessNode):
            # Allow to register specific viewers based on node.process_type
            _viewer = ALC_AIIDA_VIEWER_MAPPING.get(node.process_type, _viewer)  # type: ignore
            if not _viewer:
                _viewer = awb.viewers.AIIDA_VIEWER_MAPPING.get(
                    node.process_type, _viewer
                )

        # Handle CIF2J specific output nodes
        # incoming_links = node.get_incoming(link_type=LinkType.CREATE).all()
        # if incoming_links:
        #     link = incoming_links[0]

        if _viewer:
            return _viewer(node, **kwargs)
        # No viewer registered for this type, return node itself
        return node
