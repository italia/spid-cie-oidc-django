# SPID/CIE OIDC Federation SDK

![Python version](https://img.shields.io/badge/license-Apache%202-blue.svg)
![py-versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue.svg)

__This project is a WiP, please wait for the first stable release v0.6.0.__

SPID/CIE OIDC Federation is a suite of Django applications designed to
make it easy to build an [Openid Connect Federation](https://openid.net/specs/openid-connect-federation-1_0.html), 
each of these can be installed separately within a django project:

1. __OIDC Federation 1.0 Authority/Intermediary__ (spid_cie_oidc.entity) with the following endpoints:
    - entity configuration (.well-known/openid-federation)
    - fetch
    - listing
    - evaluate endpoints

2. __OIDC Federation 1.0 onboarding panel__ (spid_cie_oidc.onboarding):
    - [frontend] not yet in roadmap, [help needed](https://github.com/peppelinux/spid-cie-oidc/issues/1)
    - [backend] Automatic checks on new registered entities (descendats):
        - entity configuration:
            - reachability
            - signature validation
            - best practices checks following AgID and IPZS OIDC Fed guidelines.
        - RP authz check following AgID and IPZS OIDC Fed guidelines.

3. __Openid Connect Provider__ (spid_cie_oidc.provider) with Relying Party test suite  and the following endpoints:
    - entity configuration (.well-known/openid-federation)
    - authorization
    - token
    - introspection
    - token revocation

4. __Openid Connect Relying Party__ (spid_cie_oidc.relying_party) with the following endpoints:
    - entity configuration (.well-known/openid-federation)
    - authorization
    - auth code redirect
    - logout

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

##  Endpoints

### .well-known/openid-federation
Where the Entity Configuration is. `?format=json` will release a json for debug purpose.
A prefix can be configured in global settings file with parameter `OIDC_PREFIX`.

### /fetch
...


# Contribute

Your contribution is welcome, no question is useless and no answer is obvious, we need you.

#### as end user

In the event that some other functionality is required, relating to specific RFCs and draft of these, please open an issue to integrate them as soon as possibile.

#### as developer

Please open your Pull Requests on the dev branch.



# License

Apache 2


# Authors

- Giuseppe De Marco <giuseppe.demarco@teamdigitale.governo.it>
