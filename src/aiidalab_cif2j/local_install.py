"""Logic for installing QE/Wannier90/TB2J locally and creating AiiDA codes.

This covers the same ground as the AiiDAlab Quantum ESPRESSO app's own
``post_install`` setup (a dedicated conda environment plus ``InstalledCode``
registration, see that app's ``aiidalab_qe.setup.codes``), extended to also
cover ``wannier90.x`` (also on conda-forge) and TB2J's ``wann2J.py`` (on
PyPI), so a user doesn't need to separately install the QE app just to get
all the codes ``WannierTB2JWorkChain`` requires. This is a convenience for
quick local testing; for production runs on real HPC resources, use the
manual/remote code setup instead.

This module contains the pure (non-UI) logic; see
:class:`aiidalab_cif2j.resources.QuickSetupLocalWidget` for the widget that
drives it.
"""

import json
import os
import pathlib
import subprocess

#: Pinned to match the version baked into ``docker/Dockerfile``'s pre-built
#: image, so a local quick-setup install and the Docker image behave
#: identically. TB2J has no equivalent pin to match (not pinned anywhere
#: else in ``aiida-cif2j``), so it's left unpinned.
QE_VERSION = "7.6"

#: Pinned to work around a conda-forge packaging issue: the ``qe`` package
#: bundles its own internal ``bin/wannier90.x`` (an older copy it links
#: against for ``pw2wannier90.x``, reporting itself as release 3.1.0) at the
#: exact same path the standalone ``wannier90`` package installs its own
#: (real) ``bin/wannier90.x`` to. Installing both into the same environment
#: lets whichever package's files get linked last silently win that
#: collision - see ``install_qe_and_wannier90``, which works around this by
#: force-reinstalling ``wannier90`` last. ``docker/Dockerfile`` hit and fixed
#: the identical issue the same way.
WANNIER90_VERSION = "4.0.3"

#: Shared conda environment for all codes below, so `pw2wannier90.x`/
#: `wannier90.x` share the same MPI/BLAS/LAPACK stack.
ENV_NAME = f"cif2j-{QE_VERSION}"

COMPUTER_LABEL = "localhost"

#: Maps each code name to its executable (within the shared env's ``bin/``),
#: the AiiDA calcjob entry point it should be registered under, and whether
#: it runs under MPI. ``tb2j`` (`wann2J.py`) is a single-process Python
#: script; ``aiida-cif2j``'s own README documents setting ``with_mpi: false``
#: on its ``Code``.
CODES = {
    "pw": ("pw.x", "quantumespresso.pw", True),
    "pw2wannier90": ("pw2wannier90.x", "quantumespresso.pw2wannier90", True),
    "projwfc": ("projwfc.x", "quantumespresso.projwfc", True),
    "open_grid": ("open_grid.x", "quantumespresso.open_grid", True),
    "wannier90": ("wannier90.x", "wannier90.wannier90", True),
    "tb2j": ("wann2J.py", "cif2j.wannier_tb2j", False),
}

#: Codes provided by the conda-forge `qe` package.
QE_CODES = ("pw", "pw2wannier90", "projwfc", "open_grid")

#: Codes whose `code_label` is fully determined by a fixed version pin
#: (`QE_VERSION`/`WANNIER90_VERSION`), without anything needing to be
#: installed first. `find_existing_code` matches these by exact label
#: (e.g. `pw-7.6`), not just executable name, so a `pw-7.4` code from an
#: older install does *not* count as already providing `pw` once this
#: module's own pin has moved to 7.6. `tb2j` has no such pin (its label
#: depends on whatever version `pip` happens to install) and is matched by
#: executable name instead, as before.
_PINNED_CODES = (*QE_CODES, "wannier90")

#: For codes without a pinned version (unlike `QE_VERSION`/`WANNIER90_VERSION`),
#: the conda/pip package name to look up the actually-installed version from,
#: for labelling (see `code_label`). `TB2J`'s PyPI name differs in case from
#: its `tb2j` code/calcjob name.
_VERSION_PACKAGE = {
    "tb2j": "TB2J",
}


def get_env() -> pathlib.Path:
    """Return the path to the shared conda environment for the local codes."""
    return pathlib.Path.home() / ".conda" / "envs" / ENV_NAME


def _run_checked(cmd: list[str]) -> subprocess.CompletedProcess:
    """Run `cmd`, raising a `RuntimeError` with its output on a non-zero exit.

    ``subprocess.CalledProcessError``'s own string representation only shows
    the command and exit code, discarding the captured output that actually
    explains the failure (e.g. conda's dependency solver output, or pip's
    build log) -- surface the tail of it instead.
    """
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        output = "\n".join(filter(None, (proc.stdout, proc.stderr))).strip()
        tail = "\n".join(output.splitlines()[-40:])
        raise RuntimeError(
            f"`{' '.join(cmd)}` failed (exit {proc.returncode}):\n{tail}"
        )
    return proc


def _package_version(package_name: str, env: pathlib.Path | None = None) -> str | None:
    """Return the installed version of `package_name` in `env`.

    `conda list` also reports pip-installed packages (e.g. TB2J), so this
    works regardless of whether `package_name` was installed via conda or pip.

    Parameters
    ----------
    package_name : str
        Case-insensitive conda or PyPI package name.
    env : pathlib.Path, optional
        The conda environment to check. Defaults to :func:`get_env`.

    Returns
    -------
    str or None
        The installed version, or None if the environment or package doesn't
        exist.
    """
    if env is None:
        env = get_env()
    if not env.exists():
        return None
    proc = _run_checked(["conda", "list", "--prefix", str(env), "--json"])
    for package in json.loads(proc.stdout):
        if package["name"].lower() == package_name.lower():
            return package["version"]
    return None


def _package_installed(package_name: str) -> bool:
    """Return whether `package_name` is installed in the shared conda env."""
    return _package_version(package_name) is not None


def _qe_app_env_candidates() -> list[pathlib.Path]:
    """Return the env paths the AiiDAlab Quantum ESPRESSO app itself uses.

    Mirrors that app's own ``aiidalab_qe.setup.codes.get_qe_env()``: a
    Docker-image-baked parent directory first, then a user-level fallback.
    Globs for ``quantum-espresso-*`` rather than hardcoding an exact version
    suffix: that app's own pinned QE version is independent of (and has no
    reason to match) this module's own :data:`QE_VERSION` - a previous
    version of this function built the path from ``QE_VERSION`` directly,
    which only ever worked by the two pins coincidentally being equal, and
    silently stopped finding the app's env the moment they diverged.
    """
    parents = (
        pathlib.Path("/opt/conda/envs"),
        pathlib.Path.home() / ".conda" / "envs",
    )
    return [
        env
        for parent in parents
        if parent.is_dir()
        for env in sorted(parent.glob("quantum-espresso-*"))
    ]


def find_qe_env() -> pathlib.Path | None:
    """Return an existing environment with a matching, usable `qe={QE_VERSION}` install.

    Checked in order: this module's own shared environment, then the paths
    the AiiDAlab Quantum ESPRESSO app itself installs into (discovered by
    globbing for `quantum-espresso-*`, not by guessing a version suffix -
    see `_qe_app_env_candidates`). Conda environments aren't scoped to an
    AiiDA profile, so an install done via that app -- in this profile or
    another one entirely -- is reused instead of installing a second copy of
    Quantum ESPRESSO, but only if it has the *exact* `qe={QE_VERSION}` this
    module pins: `find_existing_code` now matches by versioned label (e.g.
    `pw-{QE_VERSION}`), so a code this function backs must actually point at
    binaries of that same version, not an arbitrary other one. Only a
    candidate with every :data:`QE_CODES` executable actually present on
    disk counts as usable.

    Returns
    -------
    pathlib.Path or None
        The first qualifying environment, or None if none qualifies.
    """
    for env in (get_env(), *_qe_app_env_candidates()):
        if _package_version("qe", env) != QE_VERSION:
            continue
        if all((env / "bin" / CODES[name][0]).exists() for name in QE_CODES):
            return env
    return None


def qe_installed() -> bool:
    """Return whether a usable `qe={QE_VERSION}` install already exists.

    Checks not just this module's own shared environment but also the
    AiiDAlab Quantum ESPRESSO app's own (see :func:`find_qe_env`).
    """
    return find_qe_env() is not None


def wannier90_installed() -> bool:
    """Return whether `wannier90` is installed in the shared conda environment."""
    return _package_installed("wannier90")


def code_label(code_name: str) -> str:
    """Return the AiiDA code label to use for `code_name`.

    QE codes get a `{code_name}-{QE_VERSION}` label (matching the naming
    convention the AiiDAlab Quantum ESPRESSO app's own post_install uses),
    and `wannier90` a `{code_name}-{WANNIER90_VERSION}` label, since both are
    pinned. `tb2j` has no equivalent external convention/pinned version to
    match, so its actually-installed version (see `_VERSION_PACKAGE`) is
    looked up dynamically instead, falling back to a plain label if that
    can't be determined (e.g. called before anything is installed).

    Parameters
    ----------
    code_name : str
        One of the keys in :data:`CODES`.
    """
    if code_name in QE_CODES:
        return f"{code_name}-{QE_VERSION}"
    if code_name == "wannier90":
        return f"{code_name}-{WANNIER90_VERSION}"
    package_name = _VERSION_PACKAGE.get(code_name)
    if package_name:
        version = _package_version(package_name)
        if version:
            return f"{code_name}-{version}"
    return code_name


def _install_conda_packages(*package_specs: str, force_reinstall: bool = False) -> None:
    """Install `package_specs` into the shared conda env, creating it if needed."""
    env = get_env()
    action = "install" if env.exists() else "create"
    cmd = [
        "conda",
        action,
        "--yes",
        "--override-channels",
        "--channel",
        "conda-forge",
        "--prefix",
        str(env),
    ]
    if force_reinstall:
        cmd.append("--force-reinstall")
    cmd.extend(package_specs)
    _run_checked(cmd)


def install_qe_and_wannier90() -> None:
    """Install `qe={QE_VERSION}` and `wannier90={WANNIER90_VERSION}` together.

    Installed as a single combined step, not two independent ones (unlike
    `install_tb2j`): `qe`'s own conda-forge package bundles its own internal
    `bin/wannier90.x` at the exact same path the standalone `wannier90`
    package installs its own (real) `bin/wannier90.x` to (see
    `WANNIER90_VERSION`'s docstring). Installing them separately - in either
    order, even across two different quick-setup runs against the same
    shared environment - risks one silently overwriting the other's binary
    at that shared path. `wannier90` is force-reinstalled immediately
    afterwards (a second, separate `conda install`, since `conda create`
    does not support `--force-reinstall`) to guarantee its own binary wins
    regardless of install order.
    """
    _install_conda_packages(f"qe={QE_VERSION}", f"wannier90={WANNIER90_VERSION}")
    _install_conda_packages(
        f"wannier90={WANNIER90_VERSION}", force_reinstall=True
    )


def tb2j_installed() -> bool:
    """Return whether TB2J's `wann2J.py` is installed in the shared env."""
    return (get_env() / "bin" / "wann2J.py").exists()


#: TB2J currently pins `scipy<1.17` however
#: neither conda-forge nor PyPI has a `scipy<1.17` build for Python >=3.13.
#: Pin python to known stable environment based on <3.13.
TB2J_PYTHON_SPEC = "python<3.13"


def install_tb2j() -> None:
    """Install TB2J (providing `wann2J.py`) into the shared conda environment.

    Neither `qe` nor `wannier90` (the other packages that may already share
    this environment) depend on Python, so it isn't necessarily present even
    if the environment already exists; ensure it (and `pip`) are installed
    first, regardless of what else has or hasn't been installed yet.
    """
    if not (get_env() / "bin" / "pip").exists():
        _install_conda_packages(TB2J_PYTHON_SPEC, "pip")
    _run_checked([str(get_env() / "bin" / "pip"), "install", "TB2J"])


def get_localhost_computer():
    """Return the `localhost` AiiDA computer, creating it if necessary.

    In AiiDAlab deployments the `localhost` computer is normally pre-created
    by the base-image startup scripts, so this typically just loads it. If it
    does not exist, a minimal local computer is created and configured as a
    safety fallback.

    Returns
    -------
    aiida.orm.Computer
        The configured `localhost` computer.
    """
    from aiida.common.exceptions import NotExistent
    from aiida.orm import Computer, load_computer

    try:
        return load_computer(COMPUTER_LABEL)
    except NotExistent:
        pass

    computer = Computer(
        label=COMPUTER_LABEL,
        hostname=COMPUTER_LABEL,
        workdir=str(pathlib.Path.home() / "aiida_run"),
        transport_type="core.local",
        scheduler_type="core.direct",
    )
    computer.store()
    computer.set_minimum_job_poll_interval(0)
    computer.set_default_mpiprocs_per_machine(os.cpu_count() or 1)
    computer.configure()
    return computer


def find_existing_code(code_name: str):
    """Return an existing `localhost` code already providing `code_name`, if any.

    For :data:`_PINNED_CODES` (QE codes and `wannier90`), matches by exact
    AiiDA code label (`code_label(code_name)`, e.g. `pw-7.6`) -- this
    distinguishes a code actually built against this module's current
    pinned version from one built against some other version (e.g. an older
    `pw-7.4` from a previous cif2j/QE-app install), so bumping
    `QE_VERSION`/`WANNIER90_VERSION` correctly triggers a fresh install
    rather than silently reusing mismatched binaries.

    Other codes (just `tb2j`, with no fixed version pin) are matched by
    executable basename (e.g. ``wann2J.py``) against *any* code already
    configured on `localhost`, not just one with the exact label this module
    would itself use -- there is no fixed expected label to compare against
    before TB2J is actually installed and its version known.

    Parameters
    ----------
    code_name : str
        One of the keys in :data:`CODES`.

    Returns
    -------
    aiida.orm.AbstractCode or None
        The matching code, or None if no existing code provides it.
    """
    from aiida.orm import ContainerizedCode, InstalledCode, PortableCode, QueryBuilder

    qb = QueryBuilder()
    qb.append((InstalledCode, ContainerizedCode, PortableCode))
    codes_on_localhost = (
        code for (code,) in qb.all() if code.computer.label == COMPUTER_LABEL
    )

    if code_name in _PINNED_CODES:
        expected_label = code_label(code_name)
        return next(
            (code for code in codes_on_localhost if code.label == expected_label),
            None,
        )

    executable_name = CODES[code_name][0].lower()
    for code in codes_on_localhost:
        try:
            found_name = code.get_executable().name.lower()
        except Exception:  # noqa: BLE001 - treat any resolution failure as "no match"
            continue
        if found_name == executable_name:
            return code
    return None


def code_exists(code_name: str) -> bool:
    """Return whether an existing code already provides `code_name`.

    Parameters
    ----------
    code_name : str
        One of the keys in :data:`CODES`.
    """
    return find_existing_code(code_name) is not None


def qe_needed() -> bool:
    """Return whether the `qe` conda package needs installing.

    False if every code it provides (:data:`QE_CODES`) is already covered by
    an existing `localhost` code, e.g. one set up by the AiiDAlab Quantum
    ESPRESSO app.
    """
    return any(not code_exists(name) for name in QE_CODES)


def wannier90_needed() -> bool:
    """Return whether the `wannier90` conda package needs installing."""
    return not code_exists("wannier90")


def tb2j_needed() -> bool:
    """Return whether the TB2J pip package needs installing."""
    return not code_exists("tb2j")


def create_code(code_name: str):
    """Create (or reuse) the AiiDA code for `code_name`.

    If a code already provides `code_name`'s executable (see
    :func:`find_existing_code`), it is returned unchanged. Otherwise a new
    :class:`~aiida.orm.InstalledCode` is created, labelled per
    :func:`code_label`, pointing at whichever environment actually has the
    binary: for :data:`QE_CODES`, :func:`find_qe_env` (so e.g. an install
    done via the AiiDAlab Quantum ESPRESSO app is reused rather than this
    module's own shared environment); every other code uses :func:`get_env`.

    Parameters
    ----------
    code_name : str
        One of the keys in :data:`CODES`.

    Returns
    -------
    aiida.orm.AbstractCode
        The stored (or pre-existing) code.
    """
    from aiida.orm import InstalledCode

    existing = find_existing_code(code_name)
    if existing is not None:
        return existing

    executable, plugin, with_mpi = CODES[code_name]
    env = (find_qe_env() if code_name in QE_CODES else None) or get_env()
    code = InstalledCode(
        computer=get_localhost_computer(),
        label=code_label(code_name),
        description=f"{executable} (local quick setup, {env.name})",
        filepath_executable=str(env / "bin" / executable),
        default_calc_job_plugin=plugin,
        with_mpi=with_mpi,
        prepend_text=(
            'eval "$(conda shell.posix hook)"\n'
            f"conda activate {env}\n"
            "export OMP_NUM_THREADS=1"
        ),
    )
    code.store()
    return code
