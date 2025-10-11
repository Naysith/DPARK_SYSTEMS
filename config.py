import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'replace_this_with_a_random_secret')
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'root'
    MYSQL_DB = 'delispark'
    MYSQL_PORT = 3306  # adjust if Laragon uses a different port
