from unittest import TestCase

import carpy
import carpy.statsd_client

try:
	import mock
except ImportError:
	import unittest.mock as mock


class StatsDClientTest(TestCase):

	@mock.patch.dict('carpy.config', {'APP_NAME': 'Test App'}, clear=True)
	@mock.patch('carpy.statsd_client.is_client_initialized', new_callable=mock.PropertyMock, return_value=False)
	@mock.patch('carpy.statsd_client.statsd.StatsClient.__init__', return_value=None)
	@mock.patch('carpy.transaction.time')
	def test_get_statsd_client(self, time_mock, statsd_mock, client_initialized_mock):
		self.assertRaises(carpy.statsd_client.StatsDConfigError, carpy.statsd_client.get_statsd_client)

		carpy.config['STATSD_HOST'] = 'localhost'
		self.assertRaises(carpy.statsd_client.StatsDConfigError, carpy.statsd_client.get_statsd_client)

		carpy.config['STATSD_PORT'] = 1234
		carpy.statsd_client.get_statsd_client()

		client_initialized_mock.return_value = True
		carpy.statsd_client.get_statsd_client()

		self.assertEqual(statsd_mock.call_count, 1)
