.. _workflows:

Workflow Configuration
=======================

This is the main page for the AiiDAlab CIF2J app (accessed via *New Calculation*, see
:ref:`getting_started`), and lets you configure and submit a ``WannierTB2JWorkChain`` and
monitor its results. The page is a wizard with four steps, each unlocked once the
previous one is submitted: **Structure**, **Workflow**, **Computational Resources** and
**Results**.

Structure Input
----------------

The first step provides a structure to the workflow, via two tabs:

- **Upload File** accepts a ``.cif`` or ``.mcif`` file; any other extension is rejected
  with an error message. The uploaded file is stored as-is and parsed into a structure at
  submission time.
- **AiiDA Database** searches for structures already present in the AiiDA database
  (either from previous calculations or ones added via the AiiDA command line
  interface), returning previously-uploaded structure files as well as parsed structure
  nodes.

Selecting a structure from one tab clears any selection from the other -- only one
structure can be provided at a time. Once a structure is selected, a preview is rendered
below the tabs.


Workflow Setup
--------------

The second step configures the parameters passed to
``WannierTB2JWorkChain.get_builder_from_protocol``:

- **Protocol:** one of ``FAST``, ``MODERATE`` or ``PRECISE``, controlling the overall
  precision/cost trade-off of the Quantum ESPRESSO and Wannier90 steps.
- **Spin type:** the spin treatment for the calculation
- **Electronic type:** ``METAL`` or ``INSULATOR``.
- **Wannier projection type:** the Wannier90 initial projection method (defaults to
  ``ATOMIC_PROJECTORS_QE``).
- **Pseudopotential family:** the ``aiida-pseudo`` family used for the Quantum
  ESPRESSO/Wannier90 steps, e.g. ``SSSP/1.3/PBE/efficiency``. Two buttons sit beneath the
  dropdown:

  - **Manage** opens a dedicated page for installing new pseudopotential families
    (SSSP, PseudoDojo or a custom archive) and inspecting what's already installed.
  - **Refresh** re-queries the list of installed families.

- **Magnetic elements:** a comma-separated list of chemical symbols to compute exchange
  interactions for (e.g. ``Mn, Fe``). Leave blank to auto-detect magnetic elements from
  the structure's per-kind magnetic moments at submission time.

.. An **Advanced** section provides raw JSON overrides for power users:

.. - ``tb2j.parameters`` -- parameters forwarded to the TB2J calculation (e.g. ``kmesh``,
..   ``rcut``).
.. - ``tb2j.metadata.options`` -- scheduler options for the TB2J calculation (e.g.
..   ``resources``), overriding ``WannierTB2JCalculation``'s own defaults.

.. Invalid JSON in either field is reported inline rather than letting the step be
.. submitted. The step cannot be submitted without a pseudopotential family selected.

Computational Resources
------------------------

The third step selects which AiiDA *code* runs each step of the pipeline. See
:ref:`resource_management` for how to configure codes in the first place --
:ref:`quick_setup_local` in particular can set up every code below with one click each,
for local testing.

A dropdown is shown for each required code -- ``pw.x``, ``pw2wannier90.x``,
``wannier90.x`` and TB2J -- pre-selecting a matching installed code where one exists.
``projwfc.x``/``open_grid.x`` are optional and sit in a collapsed *Optional codes*
section, since they're only needed for some Wannier projection types/settings and are
left unselected by default.

The ``wannier90.x`` row additionally has an **MPI** checkbox and a **# procs** field.
``wannier90.x`` runs single-task by default if you have an MPI compatible version however, ticking **MPI** lets you
request a specific number of MPI processes instead. The other codes don't expose this:
``pw.x``/``pw2wannier90.x``'s resources are determined automatically from the protocol
and structure, and TB2J's ``wann2J.py`` is a single-process script that isn't MPI-capable.

A single **Refresh all** button at the top of the code list re-queries every dropdown at
once.
Below the code selectors, a **Label** and **Description** can be set on the submitted
AiiDA process for easier identification later (see :ref:`history_page`).

The step cannot be submitted until every required code has a selection.

Results
-------

Once the Computational Resources step is submitted, the workflow is submitted to the
AiiDA engine and this final step becomes available. It shows a process tree (the
``WannierTB2JWorkChain`` and its sub-processes) alongside a viewer for whichever node is
selected in the tree -- see :ref:`node_viewers` for what's shown for different node
types. A **Refresh** button updates the tree as the process progresses.

