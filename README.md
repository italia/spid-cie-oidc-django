# spid-cie-oidc
SPID/CIE OIDC Federation SDK.

This project proposes the following features, divided into separate applications:

1. OIDC Federation 1.0 onboarding
2. OIDC Federation 1.0 Authority with the following endpoints:
    - fetch
    - listing
    - evaluate endpoints
3. Openid Connect Provider
4. Openid Connect Relying Party test suite, disabled for production execution contexts


# Stack

This is a Django Framework project with 
[oidcmsg](https://github.com/IdentityPython/JWTConnect-Python-OidcMsg) and
[cryptojwt](https://github.com/IdentityPython/JWTConnect-Python-CryptoJWT) di [IdentityPython](https://idpy.org/).

the Database storage engine can be one of which supported by Django.

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

# then include `spid_cie_oidc` in your project settings.INSTALLED_APPS
````

Install the example project and have a demo

````
git clone https://github.com/peppelinux/spid-cie-oidc
cd spid-cie-oidc-trust-anchor
pip install -e .

cd example
cp example/settingslocal.py.example example/settingslocal.py
# then customize (optional) example/settingslocal.py

./manage.py migrate

# load the demo configuration
./manage.py loaddata ../dumps/example.json

# create a super user
./manage.py createsuperuser

# run the web server
./manage.py runserver
````

# Usage

Point you webbrowser to `http://localhost:8000/admin` to get management interface.

Other endpoints are:

- `.well-known/openid-federation`
- `/fetch` [WiP]


# Contribute

as developer
...

as end user
...


# License

Apache 2


# Authors

Giuseppe De Marco <giuseppe.demarco@teamdigitale.governo.it>
