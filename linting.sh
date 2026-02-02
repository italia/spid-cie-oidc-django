#!/bin/bash
# Lint and auto-fix spid_cie_oidc (uses .flake8 config)

set -e

autopep8 -r --in-place spid_cie_oidc
autoflake -r --in-place --remove-unused-variables --expand-star-imports --remove-all-unused-imports spid_cie_oidc

# Critical errors (syntax, undefined names)
flake8 spid_cie_oidc --count --select=E9,F63,F7,F82 --show-source --statistics
# Full lint (uses max-line-length, ignore, etc. from .flake8)
flake8 spid_cie_oidc --count --statistics
