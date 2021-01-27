# Hummus

Hummus aims to be a lightweight, no-nonsense social website for small,
close-knit groups. It is implemented as a
[Django](https://www.djangoproject.com) site and currently includes the
following features:

- A lightweight forum/discussion board with a compact, threaded design,
  designed for sharing news, stories, and ideas
- Optional integration with identity providers through OpenID Connect

The following features are planned:

- Customizable user profiles
- Photo upload/photo sharing

## Usage

In production scenarios, Hummus is intended to be deployed in a
container. For development environments, see the “Development” section
below.

**Note: A `Dockerfile` for production use is not yet available, but will
be added to the repository shortly.**

## Configuration

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
- **To use OpenID Connect for authentication**, set `USE_OIDC` to `true`
  (the default is `false`) and configure the following variables as
  necessary. These are passed directly to the `mozilla-django-oidc`
  library; see its
  [documentation](https://mozilla-django-oidc.readthedocs.io/en/stable/)
  for descriptions of these settings.
  - `OIDC_OP_AUTHORIZATION_ENDPOINT`
  - `OIDC_OP_TOKEN_ENDPOINT`
  - `OIDC_OP_USER_ENDPOINT`
  - `OIDC_RP_CLIENT_ID`
  - `OIDC_RP_CLIENT_SECRET`
  - `OIDC_RP_SIGN_ALGO`
  - If the signing algorithm is `RS256`, one of:
    - `OIDC_OP_JWKS_ENDPOINT`
    - `OIDC_RP_IDP_SIGN_KEY`

The following environment variable is set in the provided `Dockerfile`s,
but must be set manually when using the built-in Django development
server:

- `MEDIA_ROOT`: Absolute path to a filesystem directory in which to
  store uploaded files (passed directly to Django; see the
  [documentation](https://docs.djangoproject.com/en/3.1/ref/settings/#std:setting-MEDIA_ROOT).)

The following environment variable is optional when using the built-in
Django development server:

- `SERVE_MEDIA`: Whether to serve static files from Django itself, as
  opposed to using an external server. This
  defaults to `true` when `DEBUG` is `true`, and is *always* treated as
  `false` when `DEBUG` is `false`.

The following environment variable may be used when `SERVE_MEDIA` is
`false`:

- `MEDIA_X_ACCEL_REDIRECT_URL`: When set, use of the `X-Accel-Redirect`
  HTTP header is enabled, instructing the reverse proxy in front of the
  application to serve the specified media file after the application
  has checked that the user is authenticated. The value specifies the
  base URL for the media on the proxy.

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
export MEDIA_ROOT=$(pwd)/media

# Now run any database migrations or create a super-user, when needed:
./manage.py migrate
./manage.py createsuperuser

# Launch the development server:
./manage.py runserver
```

You can also use a PostgreSQL server instead, by configuring the right
environment variables, as described under “Configuration”.

### `docker-compose` method

This is the easiest way to test in an environment more like a production
environment, with an nginx reverse proxy and PostgreSQL. Note that the
`docker-compose.yml` does enable debugging (`DEBUG` is `true`) and it is
therefore *not suitable for production*.

```bash
docker-compose build
docker-compose up -d

# Now run any database migrations or create a super-user, when needed:
docker-compose run --rm app ./manage.py migrate
docker-compose run --rm app ./manage.py createsuperuser

# Hummus is now available at 127.0.0.1:8000
```
