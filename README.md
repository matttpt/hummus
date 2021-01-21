# Hummus

Hummus aims to be a lightweight, no-nonsense social website for small,
close-knit groups. It is implemented as a
[Django](https://www.djangoproject.com) site and currently includes the
following components:

- A lightweight forum/discussion board with a compact, threaded design,
  designed for sharing news, stories, and ideas

The following components are planned:

- Integration with identity providers through OpenID Connect
- Customizable user profiles
- Photo upload/photo sharing

## Usage

In production scenarios, Hummus is intended to be deployed in a
container. For development environments, see the “Development” section
below.

To build a Hummus container image, first customize as desired (see
“Customization” below), adding the `HOME_APP` and `HOME_URLS`
environment variables to the `Dockerfile` if a custom home page is
installed. Then build using the `Dockerfile`.

Run the container with the environment variables described below
set appropriately.

Before you can use Hummus, the database must be initialized.
Furthermore, you should create a Django super-user. To do these things,
run the Django `manage.py` script inside the container:
```bash
./manage.py migrate          # to initialize the database
./manage.py createsuperuser  # to create a super-user; note, requires
                             # interactivity!
```

The Django administration interface is exposed at `/admin/`.

## Environment variables

Hummus is configured through the following environment variables:

- `DEBUG`: Whether to enable Django’s debug mode (`true` or `false`).
  Should be `false` except for development. Defaults to `false`.
- `HOST`: The host/domain name of the site. Django will refuse to serve
  clients asking for any other host/domain name. This must be specified
  when `DEBUG` is `false`, and is ignored when `DEBUG` is `true`.
- `SECRET_KEY`: A [secret key](https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/#secret-key)
  used by Django. It must be large and random, and it must be kept
  secret! If not specified, Hummus will generate a random secret key
  each time it is loaded; this is useful only in a local development
  environment and for running ad-hoc `manage.py` commands.
- **To use SQLite as a database (for development only)**, set
  `USE_SQLITE` to `true`. The SQLite file will be called `db.sqlite3`
  and will be placed in the project root.
- **To use PostgreSQL as a database (default)**, configure the following
  environment variables. You may also set `USE_SQLITE` to `false`, but
  this is the default.
  - `DB_NAME`: Name of the database on the PostgreSQL server. Defaults
    to `hummus`.
  - `DB_USER`: User for accessing the PostgreSQL server. Defaults to
    `hummus`.
  - `DB_PASSWORD`: Password for accessing the PostgreSQL server. Empty
    by default.
  - `DB_HOST`: Hostname of the PostgreSQL server. Defaults to
    `localhost`.
  - `DB_PORT`: Listening port of PostgreSQL server. Defaults to `5432`.

## Customization

Currently, Hummus does not include a home/index page. By default, it
will display a page with the site header but no content at `/`. You can
create a home page tailored to the needs of your community by extending
Hummus’s base template, creating a Django app to display the home page,
and configuring Hummus to use that app.

### The base template

Hummus provides a base template (`base.html`) that you can use to build
custom pages. This template provides the following blocks that you can
override:

- `title`: The title of the page. Defaults to the value of the `title`
  variable, if set.
- `extra_css`: Extra CSS (either `<style>` tags or `<link>` tags) to add
  to the page header. Empty by default.
- `content`: Content placed in the `<main>` tag. Empty by default.
- `scripts`: Scripts to add to the bottom of the HTML `<body>`. Empty by
  default.

### Creating a home page

Create a Django app with a view for your home page and a URL for `/`
pointing to that view. You should name the home page’s URL `home`, so Hummus
can generate links to it. You can also create views and URLs for other
pages, if you so desire.

Then, configure the following environment variables to point Hummus to
your home page app:

- `HOME_APP`: The name of your app’s `AppConfig` class, as you would
  configure in Django’s `INSTALLED_APPS` list
- `HOME_URLS`: The name of your app’s URLconf module

The simplest implementation would be to create a Django app named `home`
with the following:

```python
# home/apps.py
from django.apps import AppConfig
class HomeConfig(AppConfig):
	name = "home"

# home/urls.py
from django.urls import path
from . import views
urlpatterns = [
	path("", views.home, name="home")
]

# home/views.py
from django.shortcuts import render
def home(request):
    return render(request, "home/home.html")
```

Then create the template file `home/home.html` (either in the the global
templates directory as `templates/home/home.html` or in the app’s
template directory as `home/templates/home/home.html`):

```html
{% extends "base.html" %}
{% block title %}Home{% endblock %}
{% block content %}
  <h2>Hello, world!</h2>
{% endblock %}
```

Finally, inform Hummus of the home app by setting the environment
variables `HOME_APP=home.apps.HomeConfig` and `HOME_URLS=home.urls`.

## Development

You can use `pipenv` to easily install all of Hummus’s dependencies into
a Python virtualenv for development.

Python code in this project should be formatted with `black` and `isort`
and linted with `flake8`. (These tools are installed as development
dependencies if you use `pipenv install --dev`.)

You can test Hummus in development either through Django’s `runserver`
command or using `docker-compose`.

### `runserver` method

The easiest thing to do is to use the SQLite database backend, which
will create the database file `db.sqlite3` in the project root. Setting
`SECRET_KEY` is optional, but recommended; otherwise, you’ll have to log
in again every time the development server is reloaded, since the secret
key is regenerated randomly (making prior sessions corrupt).

```bash
pipenv shell    # to enter the virtualenv
pipenv install  # to install dependencies from the Pipfile, if this is
                # your first time using the virtualenv
export DEBUG=true
export SECRET_KEY=topsecretkey
export USE_SQLITE=true

# Now run any database migrations or create a super-user, when needed:
./manage.py migrate
./manage.py createsuperuser

# Launch the development server:
./manage.py runserver
```

You can also use a PostgreSQL server instead, by configuring the right
environment variables, as described under “Usage”.

### `docker-compose` method

This is the easiest way to test with PostgreSQL. Note that the
`docker-compose.yml` creates a development environment (`DEBUG` is
`true`) and is therefore *not suitable for production*.

```bash
docker-compose build
docker-compose up -d

# Now run any database migrations or create a super-user, when needed:
docker-compose run --rm hummus ./manage.py migrate
docker-compose run --rm hummus ./manage.py createsuperuser

# Hummus is now available at 127.0.0.1:8000
```
