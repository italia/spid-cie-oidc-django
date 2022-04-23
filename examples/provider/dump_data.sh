#!/bin/bash
./manage.py dumpdata -e admin -e spid_cie_oidc_provider -e auth -e contenttypes -e sessions --indent 2 > dumps/example.json
