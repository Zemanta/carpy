import sys
from unittest import TestCase

import carpy

try:
	import mock
except ImportError:
	import unittest.mock as mock


def empty_handler_function():
	pass

class WrapperTest(TestCase):

	@mock.patch('carpy.config')
	@mock.patch('carpy.transaction.Transaction.__exit__')
	@mock.patch('carpy.transaction.Transaction.__enter__')
	def test_transaction_decorator(self, mock_trans_enter, mock_trans_exit, config):

		@carpy.wrapper.transaction_trace
		def handler():
			pass

		self.assertFalse(mock_trans_exit.called)
		self.assertFalse(mock_trans_enter.called)

		handler()

		self.assertTrue(mock_trans_exit.called)
		self.assertTrue(mock_trans_enter.called)

	@mock.patch('carpy.config')
	@mock.patch('carpy.transaction.Transaction.__exit__')
	@mock.patch('carpy.transaction.Transaction.__enter__')
	def test_transaction_wrapper(self, mock_trans_enter, mock_trans_exit, config):
		carpy.wrapper.transaction_trace_wrap(sys.modules[__name__], 'empty_handler_function')

		self.assertFalse(mock_trans_exit.called)
		self.assertFalse(mock_trans_enter.called)

		empty_handler_function()

		self.assertEqual(mock_trans_exit.call_count, 1)
		self.assertTrue(mock_trans_enter.call_count, 1)


	@mock.patch('carpy.config')
	@mock.patch('carpy.transaction.Transaction.__exit__')
	@mock.patch('carpy.transaction.Transaction.__enter__')
	@mock.patch('carpy.wrapper.get_transaction', return_value=True)
	def test_function_decorator(self, mock_get_trans, mock_trans_enter, mock_trans_exit, config):
		@carpy.wrapper.function_trace
		def handler():
			pass

		self.assertFalse(mock_trans_exit.called)
		self.assertFalse(mock_trans_enter.called)

		handler()

		self.assertEqual(mock_trans_exit.call_count, 1)
		self.assertTrue(mock_trans_enter.call_count, 1)

	@mock.patch('carpy.config')
	@mock.patch('carpy.transaction.Transaction.__exit__')
	@mock.patch('carpy.transaction.Transaction.__enter__')
	@mock.patch('carpy.wrapper.get_transaction', return_value=True)
	def test_function_wrapper(self, mock_get_trans, mock_trans_enter, mock_trans_exit, config):
		carpy.wrapper.function_trace_wrap(sys.modules[__name__], 'empty_handler_function')

		self.assertFalse(mock_trans_exit.called)
		self.assertFalse(mock_trans_enter.called)

		empty_handler_function()

		self.assertEqual(mock_trans_exit.call_count, 1)
		self.assertTrue(mock_trans_enter.call_count, 1)

