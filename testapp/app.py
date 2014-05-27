import time
import random

from flask import Flask

import carpy


carpy.config['APP_NAME'] = 'TestApp'
carpy.config['STATSD_HOST'] = 'localhost'
carpy.config['STATSD_PORT'] = 8125

app = Flask(__name__)


@app.route('/')
def hello_world():
	time.sleep(random.random())
	wait_some_more()
	return 'Hello World!'


def wait_some_more():
	time.sleep(random.random())


if __name__ == '__main__':
	app.run()
