.. _history_page:

Process History
================

This page (accessed via *History*, see :ref:`getting_started`) lets you browse
previously submitted ``WannierTB2JWorkChain`` calculations and revisit their results,
without needing to start a new one from :ref:`workflows`.

A database search widget at the top searches specifically for CIF2J processes --
``WannierTB2JWorkChain`` runs and their underlying ``WannierTB2JCalculation`` (TB2J)
steps -- rather than every process in the AiiDA database, so results stay relevant even
on a database shared with other AiiDAlab apps.

Selecting a process from the search results shows the same process tree and node viewer
used by the Results step of the workflow wizard (see :ref:`node_viewers`): expand the
tree to see the sub-processes and output nodes of a run, and click any of them to view it
below. Setting a **Label**/**Description** when submitting a calculation (see
:ref:`workflows`) makes it easier to find again here later.
