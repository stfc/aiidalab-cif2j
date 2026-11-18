FROM aiidalab/full-stack:latest

LABEL maintainer="Dr Benjamin T. Speake <benjamin.speake@stfc.ac.uk>"
LABEL org.opencontainers.image.source="https://github.com/stfc/aiidalab-cif2j"

USER root

ENV AIIDALAB_DEFAULT_APPS="cif2j"

ENV CIF2J_QE_VERSION=7.6
ENV CIF2J_WANNIER90_VERSION=4.0.3
ENV CIF2J_TB2J_VERSION=0.9.22
ENV CIF2J_ENV=${HOME}/.conda/envs/cif2j-${CIF2J_QE_VERSION}

USER ${NB_USER}
WORKDIR ${HOME}

# Install Quantum ESPRESSO and Wannier90 into a shared conda environment.
#
# conda-forge's `qe` package bundles its own internal `bin/wannier90.x` (an
# older copy it links against for `pw2wannier90.x`, reporting itself as
# Wannier90 release 3.1.0) at the exact same path the standalone `wannier90`
# package installs its own (real 4.0.3) `bin/wannier90.x` to. Whichever
# package's transaction links last silently wins that file collision -
# `mamba create` installing both in one transaction has been observed to let
# `qe`'s older copy win, so `wannier90` is force-reinstalled afterwards to
# guarantee its binary ends up on disk, not `qe`'s.
RUN mamba create --yes --override-channels --channel conda-forge \
        --prefix "${CIF2J_ENV}" \
        "qe=${CIF2J_QE_VERSION}" "wannier90=${CIF2J_WANNIER90_VERSION}" \
        "python<3.13" pip && \
    mamba install --yes --override-channels --channel conda-forge \
        --prefix "${CIF2J_ENV}" --force-reinstall \
        "wannier90=${CIF2J_WANNIER90_VERSION}" && \
    mamba clean --all -f -y && \
    "${CIF2J_ENV}/bin/pip" install --no-cache-dir "TB2J==${CIF2J_TB2J_VERSION}"

USER root

# Generate one AiiDA code config per codes/code.yml.template entry (see
# generate_codes.sh), then register them with AiiDA at container startup
# once the profile exists.
COPY codes/code.yml.template generate_code_configs.sh /opt/cif2j/
RUN bash /opt/cif2j/generate_code_configs.sh
COPY 62_setup_cif2j_codes.sh /usr/local/bin/before-notebook.d/

USER ${NB_USER}
WORKDIR ${HOME}
