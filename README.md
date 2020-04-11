# Django FamilyTree
![Django CI](https://github.com/star4z/familytree/workflows/Django%20CI/badge.svg)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![GitHub watchers](https://img.shields.io/github/watchers/star4z/familytree?style=social)

An application that creates and displays user's family tree written in Django.

## Built With
* <b>Language</b>: Python 3.8
* <b>Framework</b>: Django
* <b>Database</b>: MariaDB
* <b>OS</b>: Ubuntu Server LTS
* <b>IDE</b>: PyCharm (<i>optional</i>)

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
1. Set up a Python environment. Recommended to use venv.
1. Assuming you have Python setup, run the following commands (if you're on Windows you may use `py` or `py -3` instead of `python` to start Python):

 ```
   pip3 install -r requirements.txt
   python3 manage.py makemigrations
   python3 manage.py migrate
   python3 manage.py createsuperuser # Create a superuser
   python3 manage.py runserver
 ```
1. Open a tab to `http://127.0.0.1:8000/admin/` to open the admin site
1. Open tab to `http://127.0.0.1:8000` to see the main site.

*This is the default Django address. Django is able to run on any IP address and port.*
```
 python3 manage.py runserver <your IP address>:<desired port>
```

If the application does not work, please check to see if there is `migrations` folder inside the `webapp` folder.  
If there isn't, please make a `migrations` folder inside the `webapp` folder.  
Then, create a file called `__init__.py` and place it inside the `migrations` folder.  

## Authors
* Ben Philips
* Cynthia Ha
* Tri Minh Duong

## License
This project is licensed under the GNU General Public License v3.0 License - see the [LICENSE](LICENSE) file for details
