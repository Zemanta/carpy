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

	@mock.patch.dict('carpy.config', {'APP_NAME': 'Test App'}, clear=True)
	@mock.patch('carpy.transaction.time')
	def test_transcation(self, time_mock):
		time_start = time.time()
		time_mock.time.return_value = time_start

		transaction = carpy.transaction.Transaction(name='Test')
		self.assertEqual(transaction.app_name, carpy.config['APP_NAME'])
		self.assertEqual(transaction.name, 'Test')
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

	@mock.patch.dict('carpy.config', {'APP_NAME': 'Test App'}, clear=True)
	def test_child_transaction(self):
		parent_transaction = carpy.transaction.Transaction().__enter__()
		child_transaction = carpy.transaction.Transaction(parent=parent_transaction).__enter__()

		self.assertIs(parent_transaction.children[0], child_transaction)
		self.assertIs(child_transaction.parent, parent_transaction)

	@mock.patch.dict('carpy.config', {'APP_NAME': 'Test App'}, clear=True)
	def test_all_transactions(self):
		t1 = carpy.transaction.Transaction().__enter__()
		t2 = carpy.transaction.Transaction(parent=t1).__enter__()
		t21 = carpy.transaction.Transaction(parent=t2).__enter__()
		t22 = carpy.transaction.Transaction(parent=t2).__enter__()
		t221 = carpy.transaction.Transaction(parent=t22).__enter__()
		t222 = carpy.transaction.Transaction(parent=t22).__enter__()
		t3 = carpy.transaction.Transaction(parent=t1).__enter__()
		t31 = carpy.transaction.Transaction(parent=t3).__enter__()

		result = list(t1.get_all_transactions())
		self.assertEqual(len(result), 8)
		self.assertIs(result[0], t21)
		self.assertIs(result[1], t221)
		self.assertIs(result[2], t222)
		self.assertIs(result[3], t22)
		self.assertIs(result[4], t2)
		self.assertIs(result[5], t31)
		self.assertIs(result[6], t3)
		self.assertIs(result[7], t1)

	@mock.patch.dict('carpy.config', {'APP_NAME': 'Test App'}, clear=True)
	@mock.patch('carpy.transaction.socket')
	def test_get_stat_name(self, socket_mock):
		socket_mock.gethostname.return_value = 'test.host.name'

		t1 = carpy.transaction.Transaction(name='test.name').__enter__()
		self.assertEqual(t1.get_stat_name(), 'carpy.Test App.test_host_name.test_name.ok')

		t2 = carpy.transaction.Transaction(name='test.name2', parent=t1).__enter__()
		t3 = carpy.transaction.Transaction(name='test.name3', parent=t2).__enter__()
		self.assertEqual(t3.get_stat_name(), 'carpy.Test App.test_host_name.test_name.child.test_name2.child.test_name3.ok')

		t1.error()
		t2.error()
		self.assertEqual(t1.get_stat_name(), 'carpy.Test App.test_host_name.test_name.err')
		self.assertEqual(t2.get_stat_name(), 'carpy.Test App.test_host_name.test_name.child.test_name2.err')

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

	@mock.patch.dict('carpy.config', {'APP_NAME': 'Test App'}, clear=True)
	def test_get_transaction(self):
		transaction = carpy.transaction.Transaction()
		transaction.__enter__()

		self.assertIs(carpy.transaction.get_transaction(), transaction)
