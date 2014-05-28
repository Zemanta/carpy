__all__ = ['Transaction', 'get_transaction']

import socket
import sys
import threading
import time
import weakref

import carpy

from .statsd_client import get_statsd_client

transactions_cache = weakref.WeakValueDictionary()


class Transaction(object):
	''' Transaction collects stats during its execution. This stats are sent to
	statsd.

	Transaction is a context manager and is expected to be invoked using the
	with statement although it is also possible to manually call __enter__ and
	__exit__ methods.
	'''

	def __init__(self, name, parent=None):
		self.app_name = carpy.config['APP_NAME']

		self.start_time = 0.0
		self.duration = 0.0

		self.name = name
		self.parent = parent

		self.is_error = False

		self.children = []

	def __enter__(self):
		self.start_time = time.time()

		if self.parent is not None:
			self.parent.add_child(self)
		else:
			transactions_cache[get_thread_id()] = self

		return self

	def __exit__(self, *args, **kwargs):
		self.duration = time.time() - self.start_time

		self.send_stats()

	def add_child(self, transaction):
		''' Adds a child transaction to the transaction.

		:param transaction:
			Transaction which is to be added as a child to the current
			transaction.
		'''
		if not transaction.parent:
			transaction.parent = self
		self.children.append(transaction)

	def get_all_transactions(self):
		''' Generator that yields the tree of all the parent and children
		transactions in no particular order.

		:returns:
			Yields the transaction.
		'''
		for child in self.children:
			for trans in child.get_all_transactions():
				yield trans

		yield self

	def error(self):
		''' Tells the transaction that an error occurred in the code while the
		transation was active.
		'''
		self.is_error = True

	def sanitize_name(self, name):
		''' Sanitizes the component of the stat's name so that it can be
		sent correctly to statsd.

		:param name:
			Part of the stat's name.
		'''
		return name.replace('.', '_') if name else ''

	def get_stat_name(self):
		''' Returns the name of the stat which can be used when sending
		stat to statsd.

		:returns:
			Name of the stat.
		'''

		# These are parts of the stat name in reverse order so that we can
		# append them instead of insert them. Premature optimization?
		parts = []

		transaction = self
		while transaction:
			parts.append(self.sanitize_name(transaction.name))
			transaction = transaction.parent
			if transaction:
				parts.append('children')

		parts.extend([
			self.sanitize_name(socket.gethostname()),
			self.sanitize_name(self.app_name),
			'carpy',
		])

		parts.reverse()
		parts.append('err' if self.is_error else 'ok')

		return '.'.join(parts)

	def send_stats(self):
		''' Sends stats of the complete transaction to statsd'''
		statsd_client = get_statsd_client()

		duration_ms = int(self.duration * 1000)
		statsd_client.timing(self.get_stat_name(), duration_ms)


def get_thread_id():
	''' Returns the thread ID of the current thread or greenlet ID if running
	in greenlet.
	'''
	greenlet = sys.modules.get('greenlet')
	if greenlet:
		current_greenlet = greenlet.getcurrent()
		if current_greenlet is not None and current_greenlet.parent:
			return id(current_greenlet)

	return threading.current_thread().ident


def get_transaction():
	''' Returns current transaction from cache.
	'''

	return transactions_cache.get(get_thread_id())
