import os
from dotenv import load_dotenv
from builtins import object

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY&') or 'you-will-never-guess&#39'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:injustice@localhost/flask_mil'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 10
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'flaskypassch@gmail.com'
    MAIL_PASSWORD = 'flask_mil.py'
    LANGUAGES = ['en', 'ru']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')






