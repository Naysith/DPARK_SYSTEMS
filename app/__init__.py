from flask import Flask
from flask_mysqldb import MySQL

mysql = MySQL()

def init_database(mysql):
    cur = mysql.connection.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, nama VARCHAR(100));")
    mysql.connection.commit()
    cur.close()

def create_app():
    app = Flask(__name__)

    # ----------------------
    # MySQL Configuration
    # ----------------------
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'flask_app'
    app.config['MYSQL_PORT'] = 3307

    mysql.init_app(app)

    # Import routes (after app is created)
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
