.. _resource_management:

Resource Management
=====================

AiiDA relies on *computer* and *code* instances to know where and how to run the
underlying software stack for any given plugin. This page (accessed via the *Setup
Resources* button, see :ref:`getting_started`) lets you configure the *computer* and
*code* instances available within AiiDAlab, controlling which executables the
``WannierTB2JWorkChain`` pipeline has access to: Quantum ESPRESSO's ``pw.x`` and
``pw2wannier90.x``, Wannier90's ``wannier90.x``, TB2J, and optionally ``projwfc.x``/
``open_grid.x`` (used by some Wannier90 projection types). A list of all available codes
is shown at the bottom of the page, with a search bar and the ability to hide codes from
the AiiDAlab interface. The rest of this page covers configuring new *computer* and
*code* instances.

.. _quick_setup_local:

Quick Setup Local
------------------

For users running AiiDAlab on their local machine, the top of the resource setup page
provides three one-click buttons: **Install Quantum ESPRESSO**, **Install Wannier90**
and **Install TB2J**. Together these cover every code the workflow needs, without
having to separately install the `AiiDAlab Quantum ESPRESSO app
<https://github.com/aiidalab/aiidalab-qe>`_ or manually compile Wannier90/TB2J.

.. note::

    This is a convenience for quick local testing. Quantum ESPRESSO in particular can be
    resource intensive, so for production runs it is recommended to use real HPC
    resources via :ref:`quick_setup_recipes`/:ref:`manual_setup` instead.

Each button is independent and can be clicked in any order:

- **Install Quantum ESPRESSO** installs the ``qe`` conda-forge package and creates
  ``pw-7.4``, ``pw2wannier90-7.4``, ``projwfc-7.4`` and ``open_grid-7.4`` codes (the
  version suffix matches whichever Quantum ESPRESSO version is bundled).
- **Install Wannier90** installs the ``wannier90`` conda-forge package and creates a
  ``wannier90-<version>`` code.
- **Install TB2J** installs TB2J via ``pip`` and creates a ``tb2j-<version>`` code.

All three share a single local conda environment, so the buttons are disabled while any
one of them is running to avoid conflicting installs into it. Progress and the final
outcome are reported beneath each button.

Before installing anything, each button first checks whether a suitable code already
exists -- including one set up by the AiiDAlab Quantum ESPRESSO app, a previous Quick
Setup Local run (in this or another AiiDAlab profile), or by hand -- and reuses it
instead of installing a duplicate copy. If, for example, Quantum ESPRESSO is already
available via the QE app, clicking **Install Quantum ESPRESSO** here will simply detect
and reuse it rather than downloading a second copy.

Once a button completes, the corresponding code(s) become available for selection in the
workflow wizard's Computational Resources step (see :ref:`workflows`); click
**Refresh all** there if a code you just installed doesn't appear immediately.

.. _quick_setup_recipes:

Quick Setup
-----------

The *Create New Code* section provides a **Quick setup** utility for configuring *code*
instances on remote machines without entering every field by hand. Rather than
describing a computer and code from scratch, it reads a set of pre-defined *recipes*
from a database file and lets you pick a ready-made combination.

Resource Database Source
~~~~~~~~~~~~~~~~~~~~~~~~~~

The recipes are loaded from the JSON database referenced in the **Source** field at the
top of the section. By default this points at an STFC maintained database of resources,
providing quick access to codes on STFC managed computers such as SCARF:

.. code:: text

    https://raw.githubusercontent.com/stfc/alc-ux/refs/heads/main/resources/remotes.json

To use a different collection of recipes, edit the URL in the **Source** field to point
at your chosen JSON database. An example is the default AiiDA resource registry
database:

.. code:: text

    https://aiidateam.github.io/aiida-resource-registry/database.json

Configuring a Code
~~~~~~~~~~~~~~~~~~

Once a source is selected, configure a new code using the following steps:

1. **Select the domain** of your remote machine.
2. **Select the computer recipe** for the target machine.
3. **Select the code recipe** for the software you wish to run (e.g. Quantum ESPRESSO's
   ``pw.x``).
4. **Complete the remaining fields**. These depend on the combination chosen in steps
   1-3 and typically cover account-specific details such as your remote username.
5. Click **Quick setup**.

This runs the computer and code setup steps in the background for the chosen recipe. The
new code then becomes available for selection in the workflow wizard.

.. note::

    If no suitable recipe exists for your computer/code combination in any available
    database, use :ref:`manual_setup` instead by ticking the *Tick checkbox to setup
    resource step by step* option, or get in touch with your chosen registry's
    maintainers, e.g. the `Ada Lovelace Centre <https://github.com/stfc/alc-ux>`_ for STFC
    managed resources.

.. _manual_setup:

Manual Setup
------------

If your required software stack is not available in a quick setup database, you will
need to configure the different components manually. First tick the box labelled *Tick
checkbox to setup resource step by step* to reveal three tabs for configuring SSH
connections, computer instances and code instances respectively.

SSH Connections
~~~~~~~~~~~~~~~

When connecting to a **remote HPC** machine for the first time, the first step is to set
up SSH communication with it. AiiDA uses SSH key authorisation by default; if you already
have passwordless SSH access configured, you can skip this step.

This tab sets up SSH key authorisation using a provided password. With *Verification
mode* set to *Provide password to remote machine*, enter the hostname/address of the
remote machine along with your username and password, then click **Setup ssh**. AiiDA
runs the setup and tests the resulting connection in the background, notifying you on
success.

.. note::

    Remote resources must support full passwordless SSH key based authorisation. AiiDA
    is incompatible with systems that require password authentication, and while it can
    work with some MFA-based login methods, this is not guaranteed.

Computer Instances
~~~~~~~~~~~~~~~~~~

Once an SSH connection is configured (manually or via the UI above), a **computer**
instance tells AiiDA how to run jobs on the remote machine:

- **Computer name:** the reference name given to the computer in the AiiDA database.
- **Hostname:** the address of the remote machine.
- **Computer description:** a reference description applied to the computer.
- **AiiDA working directory:** the directory on the remote machine where AiiDA jobs run.
- **Mpirun command:** how to run MPI based jobs on the remote machine.
- **#CPU(s) per node:** maximum number of CPUs per node on the remote machine.
- **Memory per node:** maximum memory per node on the remote machine.
- **Transport type:** how to connect to the remote machine (SSH or local).
- **Min. connection interval:** the minimum time between connection requests.
- **Scheduler:** the job scheduler used on the remote system (``core.direct`` if none).
- **Shebang:** the top line of any scripts AiiDA creates, specifying their interpreter.
- **Use login shell:** runs additional user configuration when connecting.
- **Use double quotes to escape...:** use double instead of single quotes for bash
  commands.
- **Prepend text:**/**Append text:** additional commands run before/after the executable.

An example for a remote HPC using the SLURM
scheduler, with remaining fields left as their default values:

.. code:: yaml

    label: "remote1"
    hostname: "remote1.ac.uk"
    transport: "core.ssh"
    scheduler: "core.slurm"
    work_dir: "/home/user/.aiida_run"
    mpirun_command: "srun "
    mpiprocs_per_machine: "32"
    prepend_text: ""

Clicking **Setup computer** runs AiiDA's computer setup and testing routines, reporting
success or failure.

Code Instances
~~~~~~~~~~~~~~

Once AiiDA can connect to a computer, it needs to know how to call the actual software
executable, which is what the Code tab configures:

- **AiiDA code label:** the reference name for the code in the AiiDA database.
- **Select computer:** the computer instance the code runs on.
- **Code plugin:** the AiiDA plugin handling the software (see the list below).
- **Code description:** a reference description for the code.
- **Absolute path to executable:** the path to the software's executable.
- **Use double quotes to escape...:** use double instead of single quotes for bash
  commands.
- **Prepend text:**/**Append text:** additional commands run before/after the executable.

The ``default_calc_job_plugin`` to use for each required code is:

- ``pw.x`` -> ``quantumespresso.pw``
- ``pw2wannier90.x`` -> ``quantumespresso.pw2wannier90``
- ``wannier90.x`` -> ``wannier90.wannier90``
- TB2J -> ``cif2j.wannier_tb2j``
- ``projwfc.x`` -> ``quantumespresso.projwfc``
- ``open_grid.x`` -> ``quantumespresso.open_grid``

TB2J's ``wann2J.py`` script is single-process (not MPI-capable). If configuring it via
``verdi code create`` with a YAML config file rather than this form, set ``with_mpi:
false`` explicitly. An example code configuration for TB2J on a remote machine:

.. code:: yaml

    label: "tb2j"
    description: "Wannier90 -> TB2J"
    computer: "remote1"
    filepath_executable: "wann2J.py"
    default_calc_job_plugin: "cif2j.wannier_tb2j"
    with_mpi: false
    prepend_text: "module load tb2j/0.9"

Clicking **Setup code** runs AiiDA's code setup and testing routines, reporting success
or failure.
