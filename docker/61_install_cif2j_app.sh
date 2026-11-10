#!/bin/bash -e

## Install the cif2j app from the local clone baked into this image at
## ${CIF2J_APP_DIR} (see Dockerfile.git-clone), instead of letting
## AIIDALAB_DEFAULT_APPS fetch it from the registry at container startup.
## Mirrors how 60_prepare-aiidalab.sh installs the home app from
## /opt/aiidalab-home, so this must run after that script (see the
## before-notebook.d step number).

if [ ! -e "/home/${NB_USER}/apps/cif2j" ]; then
    echo "Install cif2j app from ${CIF2J_APP_DIR}."
    aiidalab install --yes "cif2j@file://${CIF2J_APP_DIR}"
fi
