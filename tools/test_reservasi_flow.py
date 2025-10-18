from run import app

app.testing = True
client = app.test_client()

print('GET /reservasi/start')
resp = client.get('/reservasi/start')
print(resp.status_code)

# we need an existing wahana id; try to fetch api
print('GET /api/wahana')
resp = client.get('/api/wahana')
print(resp.status_code, resp.json and len(resp.json.get('data', [])))
if resp.json and resp.json.get('data'):
    id_wahana = resp.json['data'][0][0]
    print('Try select_date for', id_wahana)
    resp = client.get(f'/reservasi/select_date/{id_wahana}')
    print('select_date', resp.status_code)
    # choose first day from rendered page? we can't parse easily; just post a sample date
    sample_date = '2025-10-20'
    print('POST /reservasi/select_session')
    resp = client.post('/reservasi/select_session', data={'id_wahana': id_wahana, 'date': sample_date, 'period': 'pagi'})
    print('select_session', resp.status_code)
else:
    print('no wahana found; skipping session tests')
