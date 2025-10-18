import sys
import os
PROJECT_ROOT = r"c:\Users\user\Documents\Python programs\SEMESTER 3\DELIS PARK"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from run import app
from datetime import date

app.testing = True
client = app.test_client()

with client.session_transaction() as sess:
    sess['id_pengguna'] = 1
    sess['peran'] = 'pelanggan'

print('Fetching /api/wahana')
resp = client.get('/api/wahana')
print('api/wahana status', resp.status_code)
print(resp.get_data(as_text=True))

data = resp.get_json() or {}
items = data.get('data', [])
if not items:
    print('No wahana available; aborting test')
    sys.exit(0)

first_wahana = items[0]
wid = first_wahana[0]

today = date.today().strftime('%Y-%m-%d')
print(f'Fetching /api/sesi/{wid}/{today}')
resp2 = client.get(f'/api/sesi/{wid}/{today}')
print('api/sesi status', resp2.status_code)
print(resp2.get_data(as_text=True))

sdata = resp2.get_json() or {}
rows = sdata.get('data', [])
if not rows:
    print('No sessions for today; aborting test')
    sys.exit(0)

sesi = rows[0]
sid = sesi[0]

# Now POST reservation
post_data = {'id_sesi': str(sid), 'jumlah_tiket': '1'}
print('POST /reservasi/add', post_data)
post = client.post('/reservasi/add', data=post_data, follow_redirects=True)
print('POST status', post.status_code)
text = post.get_data(as_text=True)
print('Response length', len(text))
print(text[:2000])

# Check via model
from app.models import reservasi_model
with app.app_context():
    res = reservasi_model.get_reservasi_by_user(1)
    print('DB reservations for user 1:', res)
