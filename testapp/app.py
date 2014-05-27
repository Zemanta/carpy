import time
import random
import sys

from flask import Flask

import carpy


carpy.config['APP_NAME'] = 'TestApp'
carpy.config['STATSD_HOST'] = 'localhost'
carpy.config['STATSD_PORT'] = 8125

app = Flask(__name__)


@app.route('/')
@carpy.wrapper.transaction_trace
def hello_world():
	time.sleep(random.random())

	wait_some_more()
	wait_even_more()

	return 'Hello World!'


@carpy.wrapper.function_trace
def wait_some_more():
	time.sleep(random.random())

def wait_even_more():
	time.sleep(random.random())

carpy.wrapper.function_trace_wrap(sys.modules[__name__], 'wait_even_more')


if __name__ == '__main__':
	app.debug = True
	app.run()
