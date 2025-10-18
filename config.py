import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace_this_with_a_random_secret')
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root'
    MYSQL_DB = 'delispark'
    MYSQL_PORT = 3306

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # your email
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # app password