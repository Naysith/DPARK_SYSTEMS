import sys
import os

# Ensure project root is on sys.path so we can import run.py
PROJECT_ROOT = r"c:\Users\user\Documents\Python programs\SEMESTER 3\DELIS PARK"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from run import app

app.testing = True
client = app.test_client()

with client.session_transaction() as sess:
    sess['id_pengguna'] = 1
    sess['peran'] = 'pelanggan'

print('GET /reservasi/add')
resp = client.get('/reservasi/add')
print('STATUS', resp.status_code)
text = resp.get_data(as_text=True)
print('LENGTH', len(text))
print(text[:2000])
