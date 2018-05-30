import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '4f2FQ7JBefV8BjjT'
