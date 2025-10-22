from AjaSpellBApp import app

def main():
    with app.test_client() as c:
        r1 = c.get('/auth/reset?token=abc')
        print('GET /auth/reset ->', r1.status_code, 'len:', len(r1.get_data()))
        r2 = c.post('/auth/reset', json={'token': 'abc', 'password': 'short'})
        print('POST /auth/reset ->', r2.status_code, r2.get_json())

if __name__ == '__main__':
    main()
