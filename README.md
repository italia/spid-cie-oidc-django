# SPID/CIE OIDC Federation SDK

![Python version](https://img.shields.io/badge/license-Apache%202-blue.svg)
![py-versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue.svg)

> ⚠️ __This project is a WiP, please wait for the first stable release v0.6.0.__

SPID/CIE OIDC Federation is a suite of Django applications designed to
make it easy to build an [Openid Connect Federation](https://openid.net/specs/openid-connect-federation-1_0.html), 
each of these can be installed separately within a django project.

Table of contents:

- [Features](#features)
- [Setup](#setup)
  - [Dependencies](#dependencies)
  - [Install as Django application](#install-as-django-application)
  - [Install the example project for demo purpose](#install-the-example-project-for-demo-purpose)
* [Usage](#usage)
  - [Endpoints](#endpoints)
    * [.well-known/openid-federation](#well-knownopenid-federation)
    * [/fetch](#fetch)
* [Contribute](#contribute)
  * [as end user](#as-end-user)
  * [as developer](#as-developer)
* [License and Authors](#license-and-authors)


# Features

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
        - trust marks forgery

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

# Setup

This is a Django Framework project built on top of [IdentityPython](https://idpy.org/) 
[oidcmsg](https://github.com/IdentityPython/JWTConnect-Python-OidcMsg) and
[cryptojwt](https://github.com/IdentityPython/JWTConnect-Python-CryptoJWT).

The Database storage engine can be one of which supported by Django, the example project comes with sqlite3.

#### Dependencies
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

#### Install as Django application
Install __spid-cie-oidc__ as python package and use it in your django project
````
pip install spid-cie-oidc

# then include `spid_cie_oidc.{app_name}` in your project settings.INSTALLED_APPS
````

#### Setup the example project for demo purpose

````
git clone https://github.com/peppelinux/spid-cie-oidc
cd spid-cie-oidc
pip install -e .
````

In `examples/` folder you have three demostrations projects:
 - federation_authority
 - relying_party
 - provider

for each of the them you have to create the db and load the example data , as follows:

````
cd examples/$project_name
cp example/settingslocal.py.example example/settingslocal.py
# then customize (optional) example/settingslocal.py

./manage.py migrate

# load the demo configuration
./manage.py loaddata dumps/example.json

# create a super user
./manage.py createsuperuser
````

# Usage

The demo propose a small federation composed by the following entities:

 - Federation Authority, acts as trust anchor and onboarding system. It's available at `http://localhost:8000`
 - OpenID Relying Party, available at `http://localhost:8001`
 - OpenID Provider, available at `http://localhost:8002`

Activate the environment
````
source env/bin/activate
cd examples
````

Then enter in the single applications projects (__federation_authority/__ or __relying_party/__ or __provider/__):
````
# run the web server
./manage.py runserver
````
Point your web browser to `http://localhost:8000/admin` to enter in the management interface.


###  Endpoints

#### .well-known/openid-federation
Where the Entity Configuration is. `?format=json` will release a json for debug purpose.
A prefix can be configured in global settings file with parameter `OIDC_PREFIX`.

Available for trust anchors, providers and relying parties.

Demo examples are:

 - `http://127.0.0.1:8000/.well-known/openid-federation?format=json`
 - `http://127.0.0.1:8000/.well-known/openid-federation`

#### /fetch

Available for trust anchors and intermediates.
Releases an Entity Statement related to a subject (descendant).

Demo examples are:

 - `http://127.0.0.1:8000/fetch/?sub=http://127.0.0.1:8001/&format=json`
 - `http://127.0.0.1:8000/fetch/?sub=http://127.0.0.1:8001/`

#### /list

Available for trust anchors and intermediates.
Lists all the descendant entities.

 - `http://127.0.0.1:8000/list/`
 - `http://127.0.0.1:8000/list/?is_leaf=false`
 - `http://127.0.0.1:8000/list/?is_leaf=true`

# Hints

Backup your demo data

````
# backup your data (upgrade example data)
./manage.py dumpdata -e spid_cie_oidc_accounts -e admin -e auth -e contenttypes -e sessions > dumps/example.json
````


# Contribute

Your contribution is welcome, no question is useless and no answer is obvious, we need you.

#### as end user

Please open an issue if you found any bugs, or if you want to ask some other functionality relating to software design or RFCs/draft/best-practices.

#### as developer

Please open your Pull Requests on the dev branch.


# License and Authors

This software is released under the Apache 2 License by the following authors:

- Giuseppe De Marco <giuseppe.demarco@teamdigitale.governo.it>.

# Note

This project proposes an implementation of the italian OIDC Federation profile with
__automatic_client_registration__ and the adoption of the trust marks as mandatory.

If you're looking for a fully compliant implementation of OIDC Federation 1.0,
with explicit client registration, please look at idpy's [fedservice](https://github.com/rohe/fedservice).
