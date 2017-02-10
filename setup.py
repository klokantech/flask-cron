from setuptools import setup

setup(
    name='Flask-Cron',
    version='1.0',
    description='Periodic task execution for Flask',
    py_modules=['flask_cron'],
    install_requires=[
        'Flask>=0.11',
        'schedule>=0.4',
    ])
