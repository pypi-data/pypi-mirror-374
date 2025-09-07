"""Common setttings submodule
Following the Normalized Django Settings System conventions, the settngs for certain app are loaded from a submodule with this name. Here the code handles basic Django settings for your convenience.
"""

from email.utils import getaddresses as parse_email_addresses
from logging import getLogger
from pathlib import Path
from warnings import warn

from . import normalize_variable_name, path_for_setting, setting_is_true

LOGGER = getLogger(__name__)
POSSIBLE_LOG_LEVELS = ('INFO', 'CRITICAL', 'ERROR', 'WARNING', 'DEBUG')


def normalized_settings(**django_settings):
	"""Common values for Django
	Generates basic values for your Django settings.py file.

	:param django_settings: the current Django settings collection (ultimately the content of globals())
	:type django_settings: Any
	:return: new content for Django settings
	"""

	django_settings['DEBUG'] = setting_is_true(django_settings['ENVIRONMENTAL_SETTINGS'].get('DJANGO_DEBUG', ''))

	django_log_level = django_settings['ENVIRONMENTAL_SETTINGS'].get('DJANGO_LOG_LEVEL', '').upper()
	if django_log_level not in POSSIBLE_LOG_LEVELS:
		django_log_level = POSSIBLE_LOG_LEVELS[0]
	django_settings['LOGGING'] = {
		'version': 1,
		'disable_existing_loggers': False,
		'handlers': {
			'console': {
				'level': 'DEBUG',
				'class': 'logging.StreamHandler',
			},
		},
		'loggers': {
			'': {
				'handlers': ['console'],
				'level': 'DEBUG' if django_settings['DEBUG'] else django_log_level,
				'propagate': True,
			},
		},
	}

	django_settings['STATIC_URL'] = '/static/'
	django_settings['STATIC_ROOT'] = django_settings['BASE_DIR'] / 'storage' / 'staticfiles'
	django_settings['STORAGES'] = {
		'default': {
			'BACKEND': 'django.core.files.storage.FileSystemStorage',
			'OPTIONS': {
				'location': django_settings['BASE_DIR'] / 'storage' / 'media',
			},
		},
		'staticfiles': {
			'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
			'OPTIONS': {
				'location': django_settings['STATIC_ROOT'],
				'base_url': django_settings['STATIC_URL'],
			},
		},
	}
	Path(django_settings['STORAGES']['default']['OPTIONS']['location']).mkdir(parents=True, exist_ok=True)
	Path(django_settings['STORAGES']['staticfiles']['OPTIONS']['location']).mkdir(parents=True, exist_ok=True)

	database_settings, database_options = {}, {}
	for key in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		if key[:24] == 'DJANGO_DATABASE_OPTIONS_':
			base_key = normalize_variable_name(key)
			database_options[base_key[24:]] = path_for_setting(django_settings=django_settings, base_var_name=base_key, lowercase=True)
		elif key[:16] == 'DJANGO_DATABASE_':
			database_settings[key[16:]] = django_settings['ENVIRONMENTAL_SETTINGS'][key]
	if database_settings:
		if database_options:
			database_settings['OPTIONS'] = database_options
		else:
			warn('Potentially missing database SSL options; the connection could be insecure.', RuntimeWarning)
		django_settings['DATABASES'] = {'default' : database_settings}
	else:
		warn('Not enough information to connect to an external database; using the builtin SQLite', RuntimeWarning)

	if 'DJANGO_EMAIL_BACKEND' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_BACKEND'] = django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_BACKEND']
	if 'DJANGO_EMAIL_HOST' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_HOST'] = django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_HOST']
	if 'DJANGO_EMAIL_PORT' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_PORT'] = int(django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_PORT'])
	if 'DJANGO_EMAIL_TIMEOUT' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_TIMEOUT'] = int(django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_TIMEOUT'])
	if 'DJANGO_EMAIL_USE_SSL' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_USE_SSL'] = setting_is_true(django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_USE_SSL'])
	if (('EMAIL_USE_SSL' not in django_settings) or not django_settings['EMAIL_USE_SSL']) and ('DJANGO_EMAIL_USE_TLS' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']):
		django_settings['EMAIL_USE_TLS'] = setting_is_true(django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_USE_TLS'])
	if 'DJANGO_EMAIL_FILE_PATH' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_FILE_PATH'] = django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_FILE_PATH']

	if 'DJANGO_EMAIL_HOST_USER' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_HOST_USER'] = django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_HOST_USER']
	if 'DJANGO_EMAIL_HOST_PASSWORD' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_HOST_PASSWORD'] = django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_HOST_PASSWORD']
	django_email_ssl_certfile = path_for_setting(django_settings=django_settings, base_var_name='DJANGO_EMAIL_SSL_CERTFILE')
	if django_email_ssl_certfile is not None:
		django_settings['EMAIL_SSL_CERTFILE'] = django_email_ssl_certfile
	django_email_ssl_keyfile = path_for_setting(django_settings=django_settings, base_var_name='DJANGO_EMAIL_SSL_KEYFILE')
	if django_email_ssl_keyfile is not None:
		django_settings['EMAIL_SSL_KEYFILE'] = django_email_ssl_keyfile

	server_email = django_settings['ENVIRONMENTAL_SETTINGS'].get('DJANGO_SERVER_EMAIL', '')
	default_from_email = django_settings['ENVIRONMENTAL_SETTINGS'].get('DJANGO_DEFAULT_FROM_EMAIL', '')
	if server_email and default_from_email:
		django_settings['SERVER_EMAIL'] = server_email
		django_settings['DEFAULT_FROM_EMAIL'] = default_from_email
	elif server_email:
		django_settings['SERVER_EMAIL'] = django_settings['DEFAULT_FROM_EMAIL'] = server_email
	elif default_from_email:
		django_settings['SERVER_EMAIL'] = django_settings['DEFAULT_FROM_EMAIL'] = default_from_email
	admin_addresses = parse_email_addresses(django_settings['ENVIRONMENTAL_SETTINGS'].get('DJANGO_ADMINS', ''))
	manager_addresses = parse_email_addresses(django_settings['ENVIRONMENTAL_SETTINGS'].get('DJANGO_MANAGERS', ''))
	if admin_addresses and manager_addresses:
		django_settings['ADMINS'] = admin_addresses
		django_settings['MANAGERS'] = manager_addresses
	elif admin_addresses:
		django_settings['ADMINS'] = django_settings['MANAGERS'] = admin_addresses
	elif manager_addresses:
		django_settings['ADMINS'] = django_settings['MANAGERS'] = manager_addresses

	if 'DJANGO_EMAIL_SUBJECT_PREFIX' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_SUBJECT_PREFIX'] = setting_is_true(django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_SUBJECT_PREFIX'])
	if 'DJANGO_EMAIL_USE_LOCALTIME' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['EMAIL_USE_LOCALTIME'] = setting_is_true(django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_EMAIL_USE_LOCALTIME'])

	if 'DJANGO_ALLOWED_HOSTS' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['ALLOWED_HOSTS'] = django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_ALLOWED_HOSTS'].split(',')
	if 'DJANGO_CSRF_TRUSTED_ORIGINS' in django_settings['ENVIRONMENTAL_SETTINGS_KEYS']:
		django_settings['CSRF_TRUSTED_ORIGINS'] = django_settings['ENVIRONMENTAL_SETTINGS']['DJANGO_CSRF_TRUSTED_ORIGINS'].split(',')

	return django_settings
