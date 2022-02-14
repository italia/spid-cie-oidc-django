#!/bin/bash

autopep8 -r --in-place spid_cie_oidc
autoflake -r --in-place  --remove-unused-variables --expand-star-imports --remove-all-unused-imports spid_cie_oidc

flake8 spid_cie_oidc --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 spid_cie_oidc --max-line-length 120 --count --statistics
