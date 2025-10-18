from flask import Flask
from flask_mysqldb import MySQL
from app.utils.sesi_auto import generate_auto_sesi
from app.utils.scheduler import start_scheduler
from config import Config
from flask_mail import Mail

mysql = MySQL()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mysql.init_app(app)
    mail.init_app(app)

    from app.controllers import register_blueprints
    register_blueprints(app)
    
    # Template helper: safe column accessor for dict or sequence rows
    def col(row, key):
        """Safe accessor for template rows.
        - If row is dict-like and key is a string: return row.get(key)
        - If row is dict-like and key is numeric: return the Nth value in the dict (preserves SELECT order)
        - If row is sequence-like: return row[key]
        """
        # normalize key: if Jinja passes numbers as strings, try to convert
        try:
            ikey = int(key)
        except Exception:
            ikey = None

        # dict-like row
        if hasattr(row, 'get'):
            # numeric index requested -> return nth value
            if ikey is not None:
                try:
                    vals = list(row.values())
                    return vals[ikey]
                except Exception:
                    return None
            # string key -> normal dict get
            return row.get(key)

        # sequence-like
        try:
            if ikey is not None:
                return row[ikey]
            return row[key]
        except Exception:
            return None

    app.jinja_env.filters['col'] = col
        
    return app
