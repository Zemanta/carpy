__all__ = ['get_statsd_client']

import statsd

import carpy


statsd_client_singleton = None


class StatsDConfigError(AttributeError):
	pass


def _init_statsd_client():
	statsd_host = carpy.config.get('STATSD_HOST')
	if not statsd_host:
		raise StatsDConfigError('Missing STATSD_HOST config')

	statsd_port = carpy.config.get('STATSD_PORT')
	if not statsd_port:
		raise StatsDConfigError('Missing STATSD_PORT config')

	return statsd.StatsClient(statsd_host, statsd_port)

def is_client_initialized():
	''' Returns true if statsd client is initialized.
	Usefull in tests.
	'''
	return bool(statsd_client_singleton)

def get_statsd_client():
	''' Returns an instance of statsd client if STATSD_HOST and STATSD_PORT are configured.
	Throws a StatsDConfigError exception othervwse.
	'''
	global statsd_client_singleton

	if not is_client_initialized():
		statsd_client_singleton = _init_statsd_client()

	return statsd_client_singleton
