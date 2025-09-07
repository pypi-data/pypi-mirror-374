"""Normalized Django settings system
This module proposes a normalized system to handle Django settings by loading them from the environment. The goal is to normalize the way the settings are provided across different deployment methods.

The process consists in defining the possible environmental values and loading logic for such values in a submodule of your Django app. Then on your site settings, you'll use `normalize_settings` to compile the list of all the settings from your different installed apps and load them.
"""

from base64 import b64decode
from importlib import import_module
from logging import getLogger
from os import environ, getenv
from re import compile as re_compile, search as re_search, IGNORECASE as RE_IGNORECASE
from warnings import warn

from ._tempfile import mkstemp

__version__ = '1.0.0'

LOGGER = getLogger(__name__)
REQUIRED_SECTION_RE = re_compile(r'(:?.+_required)|(:?required_.+)', RE_IGNORECASE)
TRUTH_LOWERCASE_STRING_VALUES = ('true', 't', 'yes', 'y', 'on', '1')


def _decode_setting(django_settings, base_var_name, lowercase=False):
	"""Decode a setting
	Given an environment variable name, find the correct value for the corresponding setting. The setting name would be the base name. The logic is:
	1. if the base_var_name is found, it's returned as is and the "decoded" flag is False
	2. if base_var_name + "_CONTENT" is found (ex: FOO_CONTENT) then the content is returned as is.
	3. if base_var_name + "_BASE64" is found (ex: FOO_BASE64) then the content of the variable is base64 decoded before returning it.
	In every case but #1 the "decoded" flag will be True, meaning that you can use it to identify if this function found the "base_var_name" or a variation of it.
	If you're not interested on the decoding flag and want the decoded value unconditionally, use the "decode_setting" instead.

	:param django_settings: the global variables from the original settings.py file
	:type django_settings: dict
	:param base_var_name: the name of the environment variable to look for
	:type base_var_name: str
	:param lowercase: if the variations suffixes should be lowercase
	:type lowercase: bool
	:return: A tuple of length 2, with the "decoded" flag first and the decoded content of the variable on the 2nd.
	:rtype: tuple
	"""
	
	env_var_variations = {
		'CONTENT': base_var_name + ('_content' if lowercase else '_CONTENT'),
		'BASE64': base_var_name + ('_base64' if lowercase else '_BASE64'),
	}
	
	decoded, content = True, None
	if base_var_name in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		decoded, content = False, django_settings['ENVIRONMENTAL_SETTINGS'][base_var_name]
	elif env_var_variations['CONTENT'] in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		content = django_settings['ENVIRONMENTAL_SETTINGS'][env_var_variations['CONTENT']]
	elif env_var_variations['BASE64'] in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		content = b64decode(django_settings['ENVIRONMENTAL_SETTINGS'][env_var_variations['BASE64']])
	else:
		decoded = False
	
	return decoded, content


decode_setting = lambda django_settings, base_var_name, lowercase=False: _decode_setting(django_settings=django_settings, base_var_name=base_var_name, lowercase=lowercase)[1]


def django_settings_env_capture(**expected_sections):
	"""Capture Django settings
	Parses the current environment and collect variables applicable to the Django site.

	:param expected_sections:
	:type expected_sections:
	:return:
	:rtype:
	"""
	
	known_variations = (
		'_CONTENT',
		'_content',
		'_BASE64',
		'_base64',
	)
	
	required_expected_sections, optional_expected_sections = set(), set()
	for expected_section in expected_sections:
		if re_search(REQUIRED_SECTION_RE, expected_section) is None:
			optional_expected_sections.add(expected_section)
		else:
			required_expected_sections.add(expected_section)
	environmental_settings, missing_setting_from_env = {}, []
	
	for required_section in required_expected_sections:
		for required_setting in expected_sections[required_section]:
			required_setting_found = False
			for known_variation in known_variations:
				required_setting_variation = required_setting + known_variation
				required_setting_value = getenv(required_setting_variation, '')
				if len(required_setting_value):
					environmental_settings[required_setting_variation] = required_setting_value
					required_setting_found = True
			else:
				required_setting_value = getenv(required_setting, '')
				if len(required_setting_value):
					environmental_settings[required_setting] = required_setting_value
					required_setting_found = True
			if not required_setting_found:
				missing_setting_from_env.append(required_setting)
	if len(missing_setting_from_env):
		raise RuntimeError(f'Missing required settings from env: {missing_setting_from_env}')
	
	for optional_section in optional_expected_sections:
		for optional_setting in expected_sections[optional_section]:
			optional_setting_found = False
			for known_variation in known_variations:
				optional_setting_variation = optional_setting + known_variation
				optional_setting_value = getenv(optional_setting_variation, '')
				if len(optional_setting_value):
					environmental_settings[optional_setting_variation] = optional_setting_value
					optional_setting_found = True
			else:
				optional_setting_value = getenv(optional_setting, '')
				if len(optional_setting_value):
					environmental_settings[optional_setting] = optional_setting_value
					optional_setting_found = True
			if not optional_setting_found:
				missing_setting_from_env.append(optional_setting)
	if len(missing_setting_from_env):
		warn(f'Missing optional settings from env: {missing_setting_from_env}', RuntimeWarning)
	for key, value in environ.items():
		if key[:7] == 'DJANGO_':
			environmental_settings[key] = value
	
	return environmental_settings


def normalize_settings(*settings_module_names, django_settings, loose_list=False):
	"""Normalized Django settings system workhorse
	The interface to use the normalized Django settings system. It's usually added as:

	settings_module_names = (
		'devautotools',
		'foo.settings',
		'bar.settings',
	)
	global_state = globals()
	global_state |= normalize_settings(*settings_module_names, django_settings=globals())

	The modules will be processed in the provided order, so value overrides if present will apply in the same order.

	:param settings_module_names: module names to load; each of them could include "EXPECTED_VALUES_FROM_ENV" and "IMPLICIT_ENVIRONMENTAL_SETTINGS" constants and a "common_settings" callable.
	:type settings_module_names: str
	:param django_settings: usually the "globals()" from the calling settings.py
	:type django_settings: Any
	:param loose_list: will not stop execution when it fails to load a "settings_module" if False
	:type loose_list: bool
	"""
	
	settings_modules = []
	for module_name in settings_module_names:
		try:
			if isinstance(module_name, str):
				settings_modules.append(import_module(module_name))
			else:
				settings_modules.append(import_module(*module_name))
		except ImportError:
			if loose_list:
				LOGGER.exception("Couldn't load settings module: %s", module_name)
			else:
				raise
	
	django_settings = django_settings.copy()
	if 'EXPECTED_VALUES_FROM_ENV' not in django_settings:
		django_settings['EXPECTED_VALUES_FROM_ENV'] = {}
	if 'IMPLICIT_ENVIRONMENTAL_SETTINGS' not in django_settings:
		django_settings['IMPLICIT_ENVIRONMENTAL_SETTINGS'] = {}
	for settings_module in settings_modules:
		django_settings['EXPECTED_VALUES_FROM_ENV'] |= getattr(settings_module, 'EXPECTED_VALUES_FROM_ENV', {})
		django_settings['IMPLICIT_ENVIRONMENTAL_SETTINGS'] |= getattr(settings_module, 'IMPLICIT_ENVIRONMENTAL_SETTINGS', {})
	
	if 'ENVIRONMENTAL_SETTINGS' not in django_settings:
		django_settings['ENVIRONMENTAL_SETTINGS'] = {}
	django_settings['ENVIRONMENTAL_SETTINGS'] |= django_settings['IMPLICIT_ENVIRONMENTAL_SETTINGS'].copy() | django_settings_env_capture(**django_settings['EXPECTED_VALUES_FROM_ENV'])
	django_settings['ENVIRONMENTAL_SETTINGS_KEYS'] = frozenset(django_settings['ENVIRONMENTAL_SETTINGS'].keys())
	
	for settings_module in settings_modules:
		if hasattr(settings_module, 'normalized_settings'):
			django_settings = getattr(settings_module, 'normalized_settings')(**django_settings)
	
	return django_settings


def normalize_variable_name(variable_name):
	"""Normalize a variable name
	Given an environmental variable name, return the base name (without "_CONTENT" or "_BASE64" suffixes).

	:param variable_name: the name of the variable
	:type variable_name: str
	:return: the normalized name
	:rtype: str
	"""
	
	variable_name_upper = variable_name.upper()
	if variable_name_upper.endswith('_BASE64'):
		return variable_name[:-7]
	elif variable_name_upper.endswith('_CONTENT'):
		return variable_name[:-8]
	else:
		return variable_name


def path_for_setting(django_settings, base_var_name, lowercase=False):
	"""Path for a setting
	Given an environment variable name, decode the content if applicable, write it into a temporary file and return the path to such file. The "decoding" logic is implemented on the "_decode_setting" function. The file is created using "mkstemp" and any related limitations and security considerations apply. The file is automatically removed when the Python interpreter ends (atexit + os.remove).

	:param django_settings: the global variables from the original settings.py file
	:type django_settings: dict
	:param base_var_name: the name of the environment variable to look for
	:type base_var_name: str
	:param lowercase: if the variations suffixes should be lowercase
	:type lowercase: bool
	:return: The path for the setting
	:rtype: any
	"""
	
	decoded, content = _decode_setting(django_settings=django_settings, base_var_name=base_var_name, lowercase=lowercase)
	if not decoded:
		return content
	
	extra_mode = 't' if isinstance(content, str) else 'b'
	
	file_desc, file_path = mkstemp(text=True, session=True)
	with open(file_path, f'w{extra_mode}') as file_obj:
		file_obj.write(content)
	
	return file_path


def setting_is_true(value):
	"""Setting is True
	Compares the provided string to the known "truth" values. Uses the list in TRUTH_LOWERCASE_STRING_VALUES.

	:param str value: the value to check
	:returns bool: if the string matches a "true" value
	"""
	
	return value.strip().lower() in TRUTH_LOWERCASE_STRING_VALUES
