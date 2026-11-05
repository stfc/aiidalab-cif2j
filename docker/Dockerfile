FROM aiidalab/full-stack:latest

LABEL maintainer="Dr Benjamin T. Speake <benjamin.speake@stfc.ac.uk>"
LABEL org.opencontainers.image.source="https://github.com/stfc/aiidalab-cif2j"

USER root

ENV AIIDALAB_DEFAULT_APPS="cif2j"

ENV CIF2J_QE_VERSION=7.4
ENV CIF2J_WANNIER90_VERSION=3.1.0
ENV CIF2J_TB2J_VERSION=0.9.22
ENV CIF2J_ENV=${HOME}/.conda/envs/cif2j-${CIF2J_QE_VERSION}

USER ${NB_USER}
WORKDIR ${HOME}

# Install Quantum ESPRESSO and Wannier90 into a shared conda environment.
RUN mamba create --yes --override-channels --channel conda-forge \
        --prefix "${CIF2J_ENV}" \
        "qe=${CIF2J_QE_VERSION}" "wannier90=${CIF2J_WANNIER90_VERSION}" \
        "python<3.13" pip && \
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
