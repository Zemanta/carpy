# -*- coding: utf-8 -*-
"""
	carpy.config
	~~~~~~~~~~~~

	Based on flask.config

	Implements the configuration related objects.
"""

import imp
import os
import errno
import json


class Config(dict):
	"""Works exactly like a dict but provides ways to fill it from files
	or special dictionaries.  There are two common patterns to populate the
	config.

	Either you can fill the config from a config file::

		carpy.config.from_pyfile('yourconfig.cfg')

	Or alternatively you can define the configuration options in the
	module that calls :meth:`from_object` or provide an import path to
	a module that should be loaded.  It is also possible to tell it to
	use the same module and with that provide the configuration values
	just before the call::

		APPLICATION_NAME = 'App1'
		STATSD_URL = 'url'
		carpy.config.from_object(__name__)

	In both cases (loading from any Python file or loading from modules),
	only uppercase keys are added to the config.  This makes it possible to use
	lowercase values in the config file for temporary values that are not added
	to the config or to define the config keys in the same file that implements
	the application.

	Probably the most interesting way to load configurations is from an
	environment variable pointing to a file::

		carpy.config.from_envvar('YOURAPPLICATION_SETTINGS')

	In this case before launching the application you have to set this
	environment variable to the file you want to use.  On Linux and OS X
	use the export statement::

		export YOURAPPLICATION_SETTINGS='/path/to/config/file'

	On windows use `set` instead.
	"""

	def from_envvar(self, variable_name, silent=False):
		"""Loads a configuration from an environment variable pointing to
		a configuration file.  This is basically just a shortcut with nicer
		error messages for this line of code::

			carpy.config.from_pyfile(os.environ['YOURAPPLICATION_SETTINGS'])

		:param variable_name: name of the environment variable
		:param silent: set to `True` if you want silent failure for missing
					   files.
		:return: bool. `True` if able to load config, `False` otherwise.
		"""
		rv = os.environ.get(variable_name)
		if not rv:
			if silent:
				return False
			raise RuntimeError('The environment variable %r is not set '
							   'and as such configuration could not be '
							   'loaded.  Set this variable and make it '
							   'point to a configuration file' %
							   variable_name)
		return self.from_pyfile(rv, silent=silent)

	def from_pyfile(self, filename, silent=False):
		"""Updates the values in the config from a Python file.  This function
		behaves as if the file was imported as module with the
		:meth:`from_object` function.

		:param filename: the filename of the config.
		:param silent: set to `True` if you want silent failure for missing
					   files.
		"""
		d = imp.new_module('config')
		d.__file__ = filename
		try:
			with open(filename) as config_file:
				exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
		except IOError as e:
			if silent and e.errno in (errno.ENOENT, errno.EISDIR):
				return False
			e.strerror = 'Unable to load configuration file (%s)' % e.strerror
			raise
		self.from_object(d)
		return True

	def from_object(self, obj):
		"""Updates the values from the given object.

		Objects are usually either modules or classes.

		Just the uppercase variables in that object are stored in the config.
		Example usage::

			carpy.config.from_object('yourapplication.default_config')
			from yourapplication import default_config
			carpy.config.from_object(default_config)

		You should not use this function to load the actual configuration but
		rather configuration defaults.  The actual config should be loaded
		with :meth:`from_pyfile` and ideally from a location not within the
		package because the package might be installed system wide.

		:param obj: an import name or object
		"""
		for key in dir(obj):
			if key.isupper():
				self[key] = getattr(obj, key)

	def from_json(self, filename, silent=False):
		"""Updates the values in the config from a JSON file. This function
		behaves as if the JSON object was a dictionary and passed ot the
		:meth:`from_object` function.

		:param filename: the filename of the JSON file.
		:param silent: set to `True` if you want silent failure for missing
					   files.
		"""

		try:
			with open(filename) as json_file:
				obj = json.loads(json_file.read())
		except IOError as e:
			if silent and e.errno in (errno.ENOENT, errno.EISDIR):
				return False
			e.strerror = 'Unable to load configuration file (%s)' % e.strerror
			raise
		for key in obj.keys():
			if key.isupper():
				self[key] = obj[key]
		return True


