#!python
"""A setuptools based setup module.

ToDo:
- Everything
"""

from setuptools import setup as setuptools_setup

from simplifiedapp import object_metadata

import normalized_django_settings

setuptools_setup(**object_metadata(normalized_django_settings))
