#!python
"""Normalized Django settings system
This module proposes a normalized system to handle Django settings by loading them from the environment. The goal is to normalize the way the settings are provided across different deployment methods.

The process consists in defining the possible environmental values and loading logic for such values in a submodule of your Django app. Then on your site settings, you'll use `normalize_settings` to compile the list of all the settings from your different installed apps and load them.

This is the executable script
"""

from simplifiedapp import main

try:
	import normalized_django_settings
except ModuleNotFoundError:
	import __init__ as normalized_django_settings

main(normalized_django_settings)
