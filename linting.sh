#!/bin/bash

autopep8 -r --in-place spid_cie_oidc_entity
autoflake -r --in-place  --remove-unused-variables --expand-star-imports --remove-all-unused-imports spid_cie_oidc_entity

flake8 spid_cie_oidc_entity --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 spid_cie_oidc_entity --max-line-length 120 --count --statistics
