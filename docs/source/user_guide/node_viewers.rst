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

The TB2J calculation step's ``TB2J.pickle`` output is parsed into several structured
AiiDA data nodes, each with its own viewer:

- **Exchange Couplings**: the isotropic exchange coupling for every magnetic-site pair
  TB2J reports, shown with the Array Visualiser above (a sortable table, with a
  "Plot Array" button to chart the coupling strength against distance). A checkbox
  below the table toggles a 3D overlay drawing each coupling as an arrow between the
  two sites on the structure, colour-binned by coupling strength.
- **Magnetic Moments**: the per-atom magnetic moment vectors TB2J used, shown with the
  Array Visualiser.
- **DMI Vectors** and **Anisotropic Exchange**: the Dzyaloshinskii-Moriya interaction
  vectors and anisotropic exchange tensors for each pair, shown with the Array
  Visualiser. These only appear when the underlying TB2J run computed them (e.g. a
  non-collinear/spin-orbit calculation); a run without them simply has no such node in
  the process tree.

The raw ``TB2J.pickle`` file itself remains available as the ``TB2J_pickle_file``
output, viewable with the Folder/File Visualiser above, for analysis outside AiiDAlab.

Single Value/AiiDA Node Viewer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any node without a dedicated viewer above (e.g. a single numeric value, or a node type
not otherwise handled) falls back to a generic view showing its AiiDA database reference
(*type*, *uuid*, *node pk*) and value, where applicable.
