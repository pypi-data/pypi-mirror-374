# django-french-highschool
French high school database with UAI, department and region

## Installation
Install with pip:
```
pip install django-french-highschool
```


## Setup
In order to make `django-french-highschool` works, you need to follow the steps below:

### Settings
First, you need to add the following configuration to your settings:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...,
    'french_highschool',
    ...
]
```


### Migrations
Next, you need to run the migrations in order to update your database schema:
```
python manage.py migrate
```


### Fixtures
This app comes with existing data from french high schools. To load the data in the database run:
```
python manage.py loaddata high_school
```
