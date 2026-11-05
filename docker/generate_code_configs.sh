#!/bin/bash
# Expand code.yml.template into one AiiDA code config per entry below (run at
# image build time; see the Dockerfile). Keeping these in one place, driven
# by the same CIF2J_* env vars the conda/pip install step uses, means the
# version pins only need to change in one place to stay in sync.
set -euo pipefail

#: name -> "executable:default_calc_job_plugin:with_mpi:version"
declare -A CODES=(
    [pw]="pw.x:quantumespresso.pw:true:${CIF2J_QE_VERSION}"
    [pw2wannier90]="pw2wannier90.x:quantumespresso.pw2wannier90:true:${CIF2J_QE_VERSION}"
    [projwfc]="projwfc.x:quantumespresso.projwfc:true:${CIF2J_QE_VERSION}"
    [open_grid]="open_grid.x:quantumespresso.open_grid:true:${CIF2J_QE_VERSION}"
    [wannier90]="wannier90.x:wannier90.wannier90:true:${CIF2J_WANNIER90_VERSION}"
    [tb2j]="wann2J.py:cif2j.wannier_tb2j:false:${CIF2J_TB2J_VERSION}"
)

mkdir -p /opt/cif2j/codes

for name in "${!CODES[@]}"; do
    IFS=":" read -r executable plugin with_mpi version <<< "${CODES[$name]}"
    label="${name}-${version}"
    sed \
        -e "s|__LABEL__|${label}|g" \
        -e "s|__DESCRIPTION__|${executable} (cif2j Docker image)|g" \
        -e "s|__EXECUTABLE__|${executable}|g" \
        -e "s|__PLUGIN__|${plugin}|g" \
        -e "s|__WITH_MPI__|${with_mpi}|g" \
        -e "s|__ENV__|${CIF2J_ENV}|g" \
        /opt/cif2j/code.yml.template > "/opt/cif2j/codes/${name}.yml"
done
