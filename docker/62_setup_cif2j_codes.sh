#!/bin/bash

## Setup AiiDA code instances for the Quantum ESPRESSO, Wannier90 and TB2J
## binaries baked into this image (see the Dockerfile and ./codes/*.yml).

for config in /opt/cif2j/codes/*.yml; do
    label=$(grep -m1 "^label:" "$config" | cut -d: -f2 | tr -d ' "')
    if verdi code list | grep -q "${label}@localhost"; then
        echo "Found existing AiiDA code instance '${label}@localhost'..."
    else
        echo "Creating AiiDA code instance '${label}@localhost'..."
        verdi code create core.code.installed --config "$config" --non-interactive
    fi
done
