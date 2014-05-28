import socket
import sys
import threading
import time
import weakref

import carpy

transactions_cache = weakref.WeakValueDictionary()


class Transaction(object):
	def __init__(self, name=None, parent=None):
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

	def add_child(self, transaction):
		if not transaction.parent:
			transaction.parent = self
		self.children.append(transaction)

	def get_all_transactions(self):
		for child in self.children:
			for trans in child.get_all_transactions():
				yield trans

		yield self

	def error(self):
		self.is_error = True

	def sanitize_name(self, name):
		return name.replace('.', '_') if name else ''

	def get_stat_name(self):
		# These are parts of the stat name in reverse order so that we can
		# append them instead of insert them. Premature optimization?
		parts = []

		transaction = self
		while transaction:
			parts.append(self.sanitize_name(transaction.name))
			transaction = transaction.parent
			if transaction:
				parts.append('child')

		parts.extend([
			self.sanitize_name(socket.gethostname()),
			self.sanitize_name(self.app_name),
			'carpy',
		])

		parts.reverse()
		parts.append('err' if self.is_error else 'ok')

		return '.'.join(parts)


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
	''' Returns current transation from cache.
	'''

	return transactions_cache.get(get_thread_id())
