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

# Clean existing reservations/tickets for this user+session so test can create a new one
with app.app_context():
    from app import mysql
    cur = mysql.connection.cursor()
    try:
        # find reservation ids for this user linked to this session
        cur.execute("""
            SELECT DISTINCT r.id_reservasi FROM reservasi r
            JOIN tiket t ON t.id_reservasi = r.id_reservasi
            WHERE r.id_pengguna = %s AND t.id_sesi = %s
        """, (1, sid))
        rows = cur.fetchall()
        ids = [r[0] for r in rows]
        if ids:
            # delete tickets for those reservations
            cur.execute("DELETE FROM tiket WHERE id_reservasi IN (%s)" % (',').join(['%s']*len(ids)), tuple(ids))
            # delete the reservations
            cur.execute("DELETE FROM reservasi WHERE id_reservasi IN (%s)" % (',').join(['%s']*len(ids)), tuple(ids))
        mysql.connection.commit()
    except Exception as e:
        print('cleanup error', e)
        mysql.connection.rollback()

# post reservation and do not follow redirects
post = client.post('/reservasi/add', data={'id_sesi': str(sid), 'jumlah_tiket': '1'}, follow_redirects=False)
print('status', post.status_code)
print('location', post.headers.get('Location'))

# if redirected, confirm it goes to /pembayaran/<id>
if post.status_code in (301, 302, 303, 307):
    loc = post.headers.get('Location')
    print('redirected to', loc)
else:
    print('no redirect')
