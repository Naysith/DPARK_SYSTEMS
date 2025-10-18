import sys
import os

PROJECT_ROOT = r"c:\Users\user\Documents\Python programs\SEMESTER 3\DELIS PARK"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from run import app
from datetime import date

app.testing = True
client = app.test_client()

print('GET /api/wahana')
resp = client.get('/api/wahana')
print('STATUS', resp.status_code)
print(resp.get_data(as_text=True)[:2000])

try:
    data = resp.get_json()
    items = data.get('data', []) if isinstance(data, dict) else []
    if items:
        first_id = items[0][0]
        today = date.today().strftime('%Y-%m-%d')
        print(f'GET /api/sesi/{first_id}/{today}')
        resp2 = client.get(f'/api/sesi/{first_id}/{today}')
        print('STATUS', resp2.status_code)
        print(resp2.get_data(as_text=True)[:2000])
    else:
        print('No wahana returned')
except Exception as e:
    print('Error parsing /api/wahana response', e)
