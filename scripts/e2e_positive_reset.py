import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AjaSpellBApp import app, db
from models import User

USERNAME = 'positivereset'
EMAIL = 'positivereset@example.com'
PASSWORD = 'StartPass123'
NEW_PASSWORD = 'PositivePass987'


def main():
    with app.app_context():
        user = User.query.filter_by(username=USERNAME).first()
        if not user:
            user = User(username=USERNAME, display_name='Positive Reset', role='student', email=EMAIL)
            user.set_password(PASSWORD)
            db.session.add(user)
            db.session.commit()
            print('Created demo user for positive reset')
        else:
            print('Demo user exists for positive reset')

    with app.test_client() as c:
        # Initiate reset
        c.post('/api/auth/forgot-password', json={'identifier': EMAIL})
        # Peek raw token (dev only)
        peek = c.get('/dev/peek-reset-token', query_string={'identifier': EMAIL}).get_json()
        token = peek.get('token') if peek else None
        print('Peeked token present:', bool(token))
        if not token:
            print('No token available (dev-only). Exiting.')
            return
        # Perform reset
        r = c.post('/auth/reset', json={'token': token, 'password': NEW_PASSWORD})
        print('Reset with real token ->', r.status_code, r.get_json())
        # Check login page banner appears (one-time)
        login_page = c.get('/auth/login')
        html = login_page.get_data(as_text=True)
        print('Login page banner present:', 'Your password was updated. You can sign in now.' in html)
        # Try logging in with new password
        login = c.post('/auth/login', json={'username': USERNAME, 'password': NEW_PASSWORD, 'remember': False})
        print('Login with new password ->', login.status_code, login.get_json())

if __name__ == '__main__':
    main()
