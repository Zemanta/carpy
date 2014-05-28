__all__ = ['transaction_trace', 'function_trace', 'transaction_trace_wrap', 'function_trace_wrap']

from functools import wraps

from .transaction import Transaction, get_transaction


def transaction_trace(func, func_name=None):
	''' Transaction trace decorator.
	Wrap request handler to trace the request.
	'''
	@wraps(func)
	def wrapper(*args, **kwargs):
		new_func_name = func_name or func.__name__
		with Transaction(name=new_func_name):
			return func(*args, **kwargs)
	return wrapper


def function_trace(func, func_name=None):
	''' Function trace decorator.
	Wrap functions or methods you want to trace in a request.
	Transaction has to be started higher in a stack either with
	transaction_trace or transaction_trace_wrap.
	'''
	@wraps(func)
	def wrapper(*args, **kwargs):
		current_transaction = get_transaction()
		if not current_transaction:
			return func(*args, **kwargs)

		new_func_name = func_name or func.__name__
		with Transaction(name=new_func_name, parent=current_transaction):
			return func(*args, **kwargs)
	return wrapper


def transaction_trace_wrap(func_parent, func_name):
	''' Transaction trace wrapper.
	Wrap request handler to trace the request.

	:param func_parent
		Parent module or class of the function
	:param func_name
		Name of the function you want to wrap
	'''
	func = getattr(func_parent, func_name)
	setattr(func_parent, func_name, transaction_trace(func, func_name))


def function_trace_wrap(func_parent, func_name):
	''' Function trace wrapper.
	Wrap functions or methods you want to trace in a request.
	Transaction has to be started higher in a stack either with
	transaction_trace or transaction_trace_wrap.

	:param func_parent
		Parent module or class of the function
	:param func_name
		Name of the function you want to wrap
	'''
	func = getattr(func_parent, func_name)
	setattr(func_parent, func_name, function_trace(func, func_name))

