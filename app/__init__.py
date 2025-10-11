from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    mysql.init_app(app)

    # Import and register all controllers
    from app.controllers import register_blueprints
    register_blueprints(app)

    return app
