# SPID/CIE OIDC Federation SDK

![CI build](https://github.com/peppelinux/spid-cie-oidc-django/workflows/spid_cie_oidc/badge.svg)
[![Test Coverage](https://api.codeclimate.com/v1/badges/dd67eb5a241955b75585/test_coverage)](https://codeclimate.com/github/italia/spid-cie-oidc-django/test_coverage)
![Python version](https://img.shields.io/badge/license-Apache%202-blue.svg)
![py-versions](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue.svg)
[![GitHub issues](https://img.shields.io/github/issues/italia/spid-cie-oidc-django.svg)](https://github.com/italia/spid-cie-oidc-django/issues)
[![Get invited](https://slack.developers.italia.it/badge.svg)](https://slack.developers.italia.it/)
[![Join the #spid openid](https://img.shields.io/badge/Slack%20channel-%23spid%20openid-blue.svg)](https://developersitalia.slack.com/archives/C7E85ED1N/)


> ⚠️ __This project is a WiP, the first stable release for production use will be the v0.6.0.__

SPID/CIE OIDC Federation is a suite of Django applications designed to
make it easy to build an [Openid Connect Federation](https://openid.net/specs/openid-connect-federation-1_0.html), 
each of these can be installed separately within a django project. These are the following:

| Application | Description |
| :--- | --- |
| __spid_cie_oidc.accounts__ | Customizable application that extends the django User model. |
| __spid_cie_oidc.entity__ | Openid Connect Federation django app that implements OIDC Federation 1.0 Entity Statements, metadata discovery, Trust Chain, Trust Marks and Metadata policy. Technical specifications: [__OIDC Federation Entity__](docs/technical_specifications/ENTITY.md) |
| __spid_cie_oidc.authority__ | Openid Connect Federation API and models for __OIDC Federation Authority/Intermediary__, [Technical specifications](docs/technical_specifications/AUTHORITY.md) and [tutorial](docs/CREATE_A_FEDERATION_AUTHORITY.md). 
| __spid_cie_oidc.onboarding__ | [__Openid Connect Federation onboarding demo service__](docs/technical_specifications/ONBOARDING.md) and tools|
| __spid_cie_oidc.relying_party__ | [__Openid Connect Relying Party__](docs/technical_specifications/RELYING_PARTY.md) and test suite for OIDC Providers |
| __spid_cie_oidc.provider__ | [__Openid Connect Provider__](docs/technical_specifications/PROVIDER.md) and test suite for OIDC Relying Parties |

## Summary

* [Features](#features)
* [Setup](#setup)
* [Docker compose](#docker-compose)
* [Usage](#usage)
* [Contribute](#contribute)
    * [Contribute as end user](#contribute-as-end-user)
    * [Contribute as developer](#contribute-as-developer)
* [Implementations notes](#implementation-notes)
* [License and Authors](#license-and-authors)

------------------------------------------------

![RP Auth demo](docs/images/rp_auth_demo_3.gif)
An onboarded Relying Party with a succesful authentication.

## Setup

All the Django apps are available in the folder `spid_cie_oidc/`.
The examples projects are available in the folder `examples/`.

There is a substantial difference between an app and a project.
The app is installed using a common python package manager, such as _poetry_ or _pip_,
and can be used, inherited, and integrated into other projects.

A project is a service configuration that integrates one or more applications.
In this repository we have three example projects:

 - federation_authority
 - relying_party
 - provider

> Federation Authority loads all the applications for development needs, acting as both authority, RP and OP.
This allows us to make a demo by starting a single service. See admin page `http://127.0.0.1:8000/admin/` and user login page `http://127.0.0.1:8000/oidc/rp/landing`.

relying party and provider are examples that only integrate
__spid_cie_oidc.entity__ and __spid_cie_oidc.provider__ or __.relying_party__.

Read the [setup documentation](docs/SETUP.md) to get started.

## Docker compose

> TODO: Not available until v0.6.0 release

## Usage

The demo propose a small federation composed by the following entities:

 - Federation Authority, acts as trust anchor and onboarding system. It's available at `http://127.0.0.1:8000/`
 - OpenID Relying Party, available at `http://127.0.0.1:8001/`
 - OpenID Provider, available at `http://127.0.0.1:8002/`

Examples Users and Passwords:

 - __admin__ __oidcadmin__
 - __user__ __oidcuser__

### Tools

![OIDC Tools](docs/images/onboard_tools_jwt_debug.png)
OIDC tools facilitates the lives of developers and service operators, here a simple interface to decode and verify a JWT.

## Contribute

Your contribution is welcome, no question is useless and no answer is obvious, we need you.

#### Contribute as end user

Please open an issue if you've discoveerd a bug or if you want to ask some features.

#### Contribute as developer

Please open your Pull Requests on the __dev__ branch. 
Please consider the following branches:

 - __main__: where we merge the code before tag a new stable release.
 - __dev__: where we push our code during development.
 - __other-custom-name__: where a new feature/contribution/bugfix will be handled, revisioned and then merged to dev branch.

Backup and share your demo data
````
# backup your data (upgrade example data), -e excludes.
./manage.py dumpdata -e admin -e spid_cie_oidc_relying_party spid_cie_oidc_provider -e spid_cie_oidc_relying_party_test -e auth -e contenttypes -e sessions > dumps/example.json
````

In this project we adopt [Semver](https://semver.org/lang/it/) and
[Conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) specifications.

## Implementation notes

All the operation related to JWT signature and encryption are built on top of [IdentityPython](https://idpy.org/) 
[cryptojwt](https://github.com/IdentityPython/JWTConnect-Python-CryptoJWT)

This project proposes an implementation of the italian OIDC Federation profile with
__automatic_client_registration__ and the adoption of the trust marks as mandatory.

If you're looking for a fully compliant implementation of OIDC Federation 1.0,
with a full support of explicit client registration, please look at idpy's
[fedservice](https://github.com/rohe/fedservice).

#### General Features

- SPID and CIE OpenID Connect Provider
- SPID and CIE OpenID Connect Relying Party
- OIDC Federation onboarding demo service
- OIDC Federation 1.0
  - Trust Anchor and Intermediary
  - Automatic client registration
  - Entity profiles and Trust marks
  - Trust chain storage and discovery
  - Entity statement resolve endpoint
  - Fetch statement endpoing
  - List entities endpoint
  - Federation CLI
    - RP: build trust chains for all the available OPs
    - OP: build trust chains for all the available RPs
- OIDC Federation web tools:
  - Create a JWK
  - Convert a private jwk to PEM certificate/key
  - Convert a public jwk to PEM certificate/key
  - Decode a jwt and verify the signature
  - Resolve entity statement web UI
  - Validating a trust mark web UI
- Multitenancy, a single service can configure many entities like RPs, OP, Trust Anchors and intermediaries
- gettext compliant (i18n)
- Bootstrap Italia Design templates

## License and Authors

This software is released under the Apache 2 License by:

- Giuseppe De Marco <giuseppe.demarco@teamdigitale.governo.it>.

In this project we use the 
[metadata policy code](https://github.com/peppelinux/spid-cie-oidc-django/blob/main/spid_cie_oidc/entity/policy.py)
written by Roland Hedberg and licensed under the same Apache 2 license.
