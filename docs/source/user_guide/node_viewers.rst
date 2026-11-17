.. _node_viewers:

Node Viewers
=============

Both the :ref:`workflows` Results step and the :ref:`history_page` page use the same
node viewer: selecting a node in the process tree renders a view tailored to its type
where one is available, falling back to a generic AiiDA node reference otherwise.

Structure Visualiser
~~~~~~~~~~~~~~~~~~~~

Structure nodes (e.g. the input structure, or any structure produced during the
workflow) are rendered with the same 3D structure viewer used in the Structure Input
step of the wizard.

Array Visualiser
~~~~~~~~~~~~~~~~

Numeric array outputs are shown as a table of values.

Folder/File Visualiser
~~~~~~~~~~~~~~~~~~~~~~

AiiDA calculations typically produce a folder of retrieved files. These can be browsed
and viewed individually via a dropdown.

TB2J Results
~~~~~~~~~~~~

The retrieved files from the TB2J calculation step currently have a dedicated viewer that
lists the retrieved filenames (e.g. the ``TB2J.pickle`` output). It does not yet parse and
display the computed exchange parameters as a table or plot -- for now, use the
Folder/File Visualiser above to inspect the raw retrieved files, or load the
``TB2J_pickle_file`` output node directly for further analysis outside AiiDAlab.

Single Value/AiiDA Node Viewer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any node without a dedicated viewer above (e.g. a single numeric value, or a node type
not otherwise handled) falls back to a generic view showing its AiiDA database reference
(*type*, *uuid*, *node pk*) and value, where applicable.
