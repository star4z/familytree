# Django FamilyTree
An application that creates and displays user's family tree written in Django.

## Built With
* <b>Language</b>: Python 3.8
* <b>Framework</b>: Django
* <b>Database</b>: MariaDB
* <b>OS</b>: Ubuntu Server LTS
* <b>IDE</b>: PyCharm (<i>optional</i>)

## Authors
* Ben Philips
* Cynthia Ha
* Tri Minh Duong

## Overview
This web application creates family trees, where users can mangage and edit information on them.

Main features that are currently implemented are:
* There are models for person, name, partnerships, location (birth & death), and users
* Users can create and manage their family trees
* Users can add people and partnerships which will generate trees
* Profiles will be made for each person created
* Admin users can manage users

## Installation
To get this web application working:
1. Set up a Python environment. Recommended to use Python Virtual Environment.
1. Assuming you have Python setup, run the following commands (if you're on Windows you may use `py` or `py -3` instead of `python` to start Python):

 ```
   pip3 install -r requirements.txt
   python3 manage.py makemigrations
   python3 manage.py migrate
   python3 manage.py createsuperuser # Create a superuser
   python3 manage.py runserver
 ```
1. Open a browser to `http://127.0.0.1:8000/admin/` to open the admin site
1. Create a few test objects of each type.
1. Open tab to `http://127.0.0.1:8000` to see the main site, with your new objects.
