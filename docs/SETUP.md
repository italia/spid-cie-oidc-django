## SPID CIE OIDC Setup

The Database storage engine can be one of which supported by Django, the example project comes with sqlite3.
We can install this SDK in two ways:

 - django application in a preexisting Django project
 - demo projects for example purpose


#### Install as Django application
Install __spid-cie-oidc__ as python package and use it in your django project
````
pip install spid-cie-oidc

# then include `spid_cie_oidc.{app_name}` in your project settings.INSTALLED_APPS
````


#### Configure the example projects

Install enviroment and dependencies
````
apt install python3-dev python3-pip git
python3 -m pip install --upgrade pip
sudo pip install virtualenv
````

Activate the environment. It's optional and up to you if you want to install 
in a separate env or system wide
````
virtualenv -p python3 env
source env/bin/activate
````

Setup the example projects
````
git clone https://github.com/peppelinux/spid-cie-oidc-django
cd spid-cie-oidc
pip install --upgrade pip
pip install -e .
````
# Install Django Bootstrap italia template
````
pip install design-django-theme
````

In `examples/` folder you have three demostrations projects:

 - federation_authority
 - relying_party
 - provider

for each project you have to create the db and load the example data, as follows:

````
cd examples/$project_name
cp $project_name/settingslocal.py.example $project_name/settingslocal.py

# then customize (optional) $project_name/settingslocal.py

./manage.py migrate

# load the demo configuration
./manage.py loaddata dumps/example.json

# create a super user
./manage.py createsuperuser

# run the web server
./manage.py runserver 0.0.0.0:8000
````
Point your web browser to `http://127.0.0.1:8000/admin` to enter in the management interface.
