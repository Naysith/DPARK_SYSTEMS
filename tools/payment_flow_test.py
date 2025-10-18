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

# pick a sesi
resp = client.get('/api/wahana')
items = resp.get_json().get('data', [])
if not items:
    print('no wahana')
    sys.exit(1)
wid = items[0][0]
date_str = date.today().strftime('%Y-%m-%d')
resp = client.get(f'/api/sesi/{wid}/{date_str}')
rows = resp.get_json().get('data', [])
if not rows:
    print('no sesi')
    sys.exit(1)
sid = rows[0][0]

# create reservation
post = client.post('/reservasi/add', data={'id_sesi': str(sid), 'jumlah_tiket': '1'}, follow_redirects=False)
print('create status', post.status_code, 'location', post.headers.get('Location'))
if post.status_code in (301,302,303,307):
    loc = post.headers.get('Location')
    # fetch pembayaran form
    r = client.get(loc)
    print('payment form status', r.status_code)
    # simulate paying
    pay = client.post(loc, data={'metode_pembayaran':'BANK', 'jumlah_bayar':'50000'}, follow_redirects=True)
    print('post pay status', pay.status_code)
    print(pay.get_data(as_text=True)[:2000])
else:
    print('did not redirect to payment')
