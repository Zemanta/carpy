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

	def error(self):
		self.is_error = True

	def get_metrics_string(self):
		prefix = 'carpy.{app_name}.{host_name}.{name}.{type}'.format(
			app_name=self.app_name.replace('.', '_'),
			host_name=socket.gethostname().replace('.', '_'),
			name=self.name.replace('.', '_'),
			type='err' if self.is_error else 'ok'
		)

		result = prefix

		return result


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
