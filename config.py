import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_SUPPRESS_SEND = False
    CELERY_BROKER_URL = 'amqp://localhost//'
    UPLOAD_GALLERY_FOLDER = 'vms/static/img/uploads/gallery'
    UPLOAD_INDEX_FOLDER = 'vms/static/img/uploads/index'
    UPLOAD_BLOG_FOLDER = 'vms/static/img/uploads/blog'
    UPLOAD_STORE_FOLDER = 'vms/static/img/uploads/store'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}


'''
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'gallery_uploads')
'''
