# -*- coding: utf-8 -*-

from setuptools import setup

setup(
	name='Carpy',
	version='0.0.1-dev',
	url='http://github.com/Zemanta/carpy/',
	license='Apache 2.0',
	author='Jure Ham, Matic Žgur',
	description='Make your application swim like a fish in the water',
	packages=['carpy', 'carpy.tests'],
	include_package_data=True,
	zip_safe=False,
	platforms='any',
	install_requires=[
		'statsd==3.0',
	],
	test_suite='carpy.tests'
)
