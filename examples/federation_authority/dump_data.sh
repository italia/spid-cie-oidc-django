#!/bin/bash
./manage.py dumpdata -e admin -e spid_cie_oidc_relying_party -e spid_cie_oidc_provider -e spid_cie_oidc_relying_party_test -e auth -e contenttypes -e sessions --indent 2 > dumps/example.json
