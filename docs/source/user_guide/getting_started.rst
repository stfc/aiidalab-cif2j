.. _getting_started:

Getting Started
===============

CIF2J
-----

The `aiida-cif2j <https://github.com/stfc/aiida-cif2j>`_ plugin computes magnetic
exchange interactions from a CIF/MCIF structure, via a Quantum ESPRESSO SCF/NSCF
calculation, Wannierisation with Wannier90, and a TB2J calculation.

AiiDAlab
--------

`AiiDAlab <https://www.aiidalab.net/>`_ adapts the `AiiDA <https://www.aiida.net/>`_
workflow management platform to provide a web-based UI for configuring and submitting
computational workflows. See the
`AiiDAlab documentation <https://aiidalab.readthedocs.io/en/latest/usage/access/index.html>`_
for instructions on running AiiDAlab itself.

AiiDAlab CIF2J Plugin
---------------------

When the AiiDAlab application is first opened in a browser it defaults to the AiiDAlab
`home page <https://aiidalab.readthedocs.io/en/latest/usage/home.html>`_, which lists a
start banner for each installed plugin. The CIF2J plugin's banner provides four
navigation buttons:

- **New Calculation** -> the main workflow configuration wizard (:ref:`workflows`).
- **History** -> browse previously submitted calculations (:ref:`history_page`).
- **Setup Resources** -> configure the AiiDA computers/codes the workflow runs on
  (:ref:`resource_management`).
- **Documentation** -> this documentation.

These same four buttons also appear at the top of each of the app's own pages, so you can
jump between them without returning to the home page first. Each page is described in
more detail throughout the rest of this documentation.
