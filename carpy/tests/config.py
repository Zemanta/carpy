import os

from unittest import TestCase

import carpy


class ConfigTest(TestCase):

	def setUp(self):
		carpy.config = carpy.Config()

	def test_config_basic(self):
		carpy.config['TEST'] = 1
		self.assertEqual(carpy.config['TEST'], 1)

	def test_config_from_class(self):
		class Base(object):
			TEST_KEY = 'foo'
		class Test(Base):
			SECRET_KEY = 'devkey'

		carpy.config.from_object(Test)

		self.assertEqual(carpy.config['TEST_KEY'], 'foo')
		self.assertEqual(carpy.config['SECRET_KEY'], 'devkey')

	def test_config_from_json(self):
		current_dir = os.path.dirname(os.path.abspath(__file__))
		carpy.config.from_json(os.path.join(current_dir, 'static', 'config.json'))

		self.assertEqual(carpy.config['TEST'], 'yes')

	def test_config_from_pyfile(self):
		current_dir = os.path.dirname(os.path.abspath(__file__))
		carpy.config.from_pyfile(os.path.join(current_dir, 'static', 'config.py'))

		self.assertEqual(carpy.config['TEST'], 'noe')

	def test_config_from_envvar(self):
		env = os.environ
		try:
			os.environ = {}
			try:
				carpy.config.from_envvar('FOO_SETTINGS')
			except RuntimeError as e:
				self.assertTrue("'FOO_SETTINGS' is not set" in str(e))
			else:
				self.assert_true(0, 'expected exception')
			self.assertFalse(carpy.config.from_envvar('FOO_SETTINGS', silent=True))

			current_dir = os.path.dirname(os.path.abspath(__file__))
			os.environ = {'FOO_SETTINGS': os.path.join(current_dir, 'static', 'config.py')}

			self.assertTrue(carpy.config.from_envvar('FOO_SETTINGS'))
			self.assertEqual(carpy.config['TEST'], 'noe')
		finally:
			os.environ = env
