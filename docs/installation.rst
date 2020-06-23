.. _installation:

Installation
============

Use ``pip`` to install the package, preferably to a local ``virtualenv``::

    pip install django-taskflow

Then add the package to ``INSTALLED_APPS`` in the ``settings.py`` file.

Run migrations from the project main directory::

   python manage.py migrate

Then add and run workflows.


