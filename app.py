from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_app'
app.config['MYSQL_PORT'] = 3307

mysql = MySQL(app)

# Import routes at the bottom (after mysql is defined)
from routes import *
