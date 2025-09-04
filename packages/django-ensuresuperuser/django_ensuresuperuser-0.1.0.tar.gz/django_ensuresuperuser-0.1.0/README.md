# Django Ensure Superuser

A simple Django management command to create a superuser non-interactively if one does not already exist.

This is useful for automating the setup of a Django application, for example, in a Docker container or a deployment script.

## Installation

1. Install the package using pip:

```bash
pip install django-ensuresuperuser
```

2. Add `django_ensuresuperuser` to your `INSTALLED_APPS` setting in your Django project's `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_ensuresuperuser',
]
```

## Usage

Assuming all variables are set, run the management command:

```bash
python manage.py ensuresuperuser
```

### Configuration

The command requires the following environment variables to be set:

*   `DJANGO_SUPERUSER_PASSWORD`: The password for the superuser.
*   `DJANGO_SUPERUSER_EMAIL` (optional): The email for the superuser. Defaults to `admin@example.com`.

The superuser will be created with the username `admin`.
If a user with the username `admin` already exists, the command will do nothing.

### Example

```bash
export DJANGO_SUPERUSER_PASSWORD="mysecretpassword"
export DJANGO_SUPERUSER_EMAIL="admin@mydomain.com"
python manage.py ensuresuperuser
```
