from app import create_app
import time
from datetime import datetime
from flask import jsonify

app = create_app()

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/_server_time')
def server_time():
    now = datetime.now()
    return jsonify(
        iso = now.isoformat(),
        date = now.strftime('%d %B %Y'),
        time = now.strftime('%H:%M')
    )

@app.context_processor
def inject_version():
    return {'asset_version': int(time.time())}

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)