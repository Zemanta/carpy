import gc
import sys
import threading
import time
from unittest import TestCase

import carpy
import carpy.transaction

try:
	import mock
except ImportError:
	import unittest.mock as mock


class TranscationTest(TestCase):

	@mock.patch('carpy.config')
	@mock.patch('carpy.transaction.time')
	def test_transcation(self, time_mock, config_mock):
		config_mock.dict.in_dict = {'APP_NAME': 'Test App'}

		time_start = time.time()
		time_mock.time.return_value = time_start

		transaction = carpy.transaction.Transaction()
		self.assertEqual(transaction.app_name, config_mock['APP_NAME'])
		self.assertEqual(transaction.start_time, 0.0)
		self.assertEqual(transaction.duration, 0.0)

		transaction.__enter__()
		self.assertEqual(transaction.start_time, time_start)
		self.assertIs(carpy.transaction.transactions_cache[carpy.transaction.get_thread_id()], transaction)

		time_end = time.time() + 5
		time_mock.time.return_value = time_end

		transaction.__exit__()
		self.assertEqual(transaction.duration, time_end - time_start)

		del transaction
		gc.collect()
		self.assertTrue(carpy.transaction.get_thread_id() not in carpy.transaction.transactions_cache)
		self.assertIs(carpy.transaction.transactions_cache.get(carpy.transaction.get_thread_id()), None)

	@mock.patch('carpy.config')
	@mock.patch('carpy.transaction.time')
	def test_child_transaction(self, time_mock, config_mock):
		parent_transaction = carpy.transaction.Transaction().__enter__()
		child_transaction = carpy.transaction.Transaction(parent=parent_transaction).__enter__()

		self.assertIs(parent_transaction.children[0], child_transaction)
		self.assertIs(child_transaction.parent, parent_transaction)

	def test_get_thread_id(self):
		expected_thread_id = threading.current_thread().ident
		self.assertEqual(carpy.transaction.get_thread_id(), expected_thread_id)

	def test_get_greenlet_id(self):
		class FakeObject:
			parent = True

		greenlet_obj = FakeObject()

		class FakeGreenlet(object):
			@staticmethod
			def getcurrent():
				return greenlet_obj

		original_greenlet = sys.modules.get('greenlet')
		sys.modules['greenlet'] = FakeGreenlet

		self.assertEqual(carpy.transaction.get_thread_id(), id(greenlet_obj))

		if original_greenlet:
			sys.modules['greenlet'] = original_greenlet
		else:
			del sys.modules['greenlet']

	@mock.patch('carpy.config')
	def test_get_transaction(self, config_mock):
		config_mock.dict.in_dict = {'APP_NAME': 'Test App'}

		transaction = carpy.transaction.Transaction()
		transaction.__enter__()

		self.assertIs(carpy.transaction.get_transaction(), transaction)
