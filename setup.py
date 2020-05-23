#!/usr/bin/env python

from setuptools import setup

with open('django_taskflow/version.py') as f:
    exec(f.read())

with open('README.md') as f:
    long_description = f.read()

setup(
    name="django-taskflow",
    version=__version__,
    url="https://github.com/GibbsConsulting/django-taskflow",
    description="Django task-based workflow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Gibbs Consulting",
    author_email="django_taskflow@gibbsconsulting.ca",
    license='AGPL',
    packages=[
    'django_taskflow',
    'django_taskflow.migrations',
    'django_taskflow.templatetags',
    ],
    include_package_data=True,
    classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    ],
    keywords='django taskflow workflow',
    project_urls = {
    'Source': "https://github.com/GibbsConsulting/django-taskflow",
    'Tracker': "https://github.com/GibbsConsulting/django-taskflow/issues",
    'Documentation': 'http://django-taskflow.readthedocs.io/',
    },
    install_requires = ['Django>=2',],
    python_requires=">=3.7",
    )

