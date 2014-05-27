from functools import wraps

from .transaction import Transaction, get_transaction


def transaction_trace(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		func_name = func.__name__
		with Transaction(name=func_name):
			return func(*args, **kwargs)
	return wrapper


def function_trace(func, func_name=None):
	@wraps(func)
	def wrapper(*args, **kwargs):
		current_transaction = get_transaction()
		if not current_transaction:
			return

		new_func_name = func_name or func.__name__
		with Transaction(parent=current_transaction, name=new_func_name):
			return func(*args, **kwargs)

	return wrapper



def function_trace_wrap(func_parent, func_name):
	func = getattr(func_parent, func_name)
	setattr(func_parent, func_name, function_trace(func, func_name))
