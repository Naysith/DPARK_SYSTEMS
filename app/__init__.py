from flask import Flask
from flask_mysqldb import MySQL
from app.utils.sesi_auto import generate_auto_sesi
from app.utils.scheduler import start_scheduler
from config import Config

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mysql.init_app(app)

    from app.controllers import register_blueprints
    register_blueprints(app)

    with app.app_context():
        print("🚀 Running initial session generation...")
        generate_auto_sesi()
        print("🕒 Starting daily session generator scheduler...")
        start_scheduler(app)
        
    return app
