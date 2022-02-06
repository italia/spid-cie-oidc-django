# SPID/CIE OIDC Federation SDK

![Python version](https://img.shields.io/badge/license-Apache%202-blue.svg)
![py-versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue.svg)

__This project is a WiP, please wait for the first stable release v0.6.0.__

SPID/CIE OIDC Federation is a suite of Django applications designed to
make it easy to build an [Openid Connect Federation](https://openid.net/specs/openid-connect-federation-1_0.html).

We have 4 applications, which can be installed separately within a django project.

1. OIDC Federation 1.0 onboarding panel (__spid_cie_oidc.onboarding__)
    - [frontend] not yet in roadmap, [help needed](https://github.com/peppelinux/spid-cie-oidc/issues/1)
    - [backend] Automatic checks on new registered entities (descendats):
        - entity configuration:
            - reachability
            - signature validation
            - best practices checks following AgID and IPZS OIDC Fed guidelines.
        - RP authz check following AgID and IPZS OIDC Fed guidelines.

2. OIDC Federation 1.0 Authority (spid_cie_oidc.entity) with the following endpoints:
    - fetch
    - listing
    - evaluate endpoints

3. Openid Connect Provider (spid_cie_oidc.provider) with Relying Party test suite

4. Openid Connect Relying Party (spid_cie_oidc.relying_party)


# Stack

This is a Django Framework project built on top of [IdentityPython](https://idpy.org/) 
[oidcmsg](https://github.com/IdentityPython/JWTConnect-Python-OidcMsg) and
[cryptojwt](https://github.com/IdentityPython/JWTConnect-Python-CryptoJWT).

The Database storage engine can be one of which supported by Django, the example project comes with sqlite3.

# Setup

Dependencies
````
apt install python3-dev python3-pip git
python3 -m pip install --upgrade pip
sudo pip install virtualenv
````

Activate the environment. It's optional and up to you if you want to install 
in a separate env or system wide
````
virtualenv -p python3 --copies env
source env/bin/activate
````

Install __spid-cie-oidc__ as python package and use it in your django project
````
pip install spid-cie-oidc

# then include `spid_cie_oidc.{app_name}` in your project settings.INSTALLED_APPS
````

Install the example project and have a demo

````
git clone https://github.com/peppelinux/spid-cie-oidc
cd spid-cie-oidc
pip install -e .

cd example
cp example/settingslocal.py.example example/settingslocal.py
# then customize (optional) example/settingslocal.py

./manage.py migrate

# load the demo configuration
./manage.py loaddata dumps/example.json

# create a super user
./manage.py createsuperuser

# run the web server
./manage.py runserver
````

# Usage

Point your web browser to `http://localhost:8000/admin` to enter in the management interface.

# Endpoints

### .well-known/openid-federation
Where the Entity Configuration is. `?format=json` will release a json for debug purpose.
A prefix can be configured in global settings file with parameter `OIDC_PREFIX`.

### /fetch
...


# Contribute

as developer
...

as end user
...


# License

Apache 2


# Authors

Giuseppe De Marco <giuseppe.demarco@teamdigitale.governo.it>
