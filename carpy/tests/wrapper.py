import sys
from unittest import TestCase

import carpy

try:
	import mock
except ImportError:
	import unittest.mock as mock


def empty_handler_function():
	pass

class SpecificException(Exception):
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

	@mock.patch('carpy.config')
	@mock.patch('carpy.transaction.Transaction.send_stats')
	@mock.patch('carpy.transaction.Transaction.is_error', new_callable=mock.PropertyMock)
	def test_transaction_error_decorator(self, mock_is_error, mock_send_stats, config):

		@carpy.wrapper.transaction_trace
		def handler():
			raise SpecificException()

		self.assertRaises(SpecificException, handler)
		mock_is_error.assert_called_with(True)

	@mock.patch('carpy.config')
	@mock.patch('carpy.wrapper.get_transaction', return_value=True)
	@mock.patch('carpy.transaction.Transaction.send_stats')
	@mock.patch('carpy.transaction.Transaction.__enter__')
	@mock.patch('carpy.transaction.Transaction.is_error', new_callable=mock.PropertyMock)
	def test_function_error_decorator(self, mock_is_error, mock_enter, mock_send_stats, mock_get_trans, config):

		@carpy.wrapper.function_trace
		def handler():
			raise SpecificException()

		self.assertRaises(SpecificException, handler)
		mock_is_error.assert_called_with(True)
