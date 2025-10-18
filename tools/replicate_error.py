from run import app

app.testing = True
client = app.test_client()

# simulate logged-in user
with client.session_transaction() as sess:
    sess['id_pengguna'] = 1
    sess['peran'] = 'pelanggan'

paths = ['/user', '/user/reservasi/start', '/reservasi/start', '/reservasi/list']
for p in paths:
    print('\n=== REQUEST:', p)
    resp = client.get(p)
    print('STATUS:', resp.status_code)
    data = resp.get_data(as_text=True)
    print('LENGTH:', len(data))
    # print up to 2000 chars
    print(data[:2000])
    print('--- END RESPONSE ---')
