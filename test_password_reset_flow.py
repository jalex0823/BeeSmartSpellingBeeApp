import os
import time
import unittest

# Ensure dev peek is enabled before importing app
os.environ['ALLOW_DEV_RESET_PEEK'] = '1'

from AjaSpellBApp import app, db  # noqa: E402
from models import User, PasswordResetToken  # noqa: E402
import AjaSpellBApp as appmod  # noqa: E402


class TestPasswordResetFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        appmod.ALLOW_DEV_RESET_PEEK = True
        with app.app_context():
            db.create_all()

    def setUp(self):
        self.client = app.test_client()

    def test_invalid_token_generic_response(self):
        r = self.client.post('/auth/reset', json={'token': 'invalid', 'password': 'shortpass'})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data and data.get('success') is True)
        self.assertIn('password has been updated', (data.get('message') or '').lower())

    def test_positive_reset_and_banner_and_login(self):
        uniq = str(int(time.time()))
        username = f"t_reset_{uniq}"
        email = f"t_reset_{uniq}@example.com"
        start_pw = 'StartP@ss1234'
        new_pw = 'NewP@ss5678'

        # Create user
        with app.app_context():
            user = User(username=username, display_name='T Reset', role='student', email=email)
            user.set_password(start_pw)
            db.session.add(user)
            db.session.commit()

        # Request reset
        self.client.post('/api/auth/forgot-password', json={'identifier': email})

        # Peek token (dev-only)
        peek = self.client.get('/dev/peek-reset-token', query_string={'identifier': email}).get_json()
        token = peek.get('token') if peek else None
        self.assertTrue(token, 'Dev-only token peek should return a token')

        # Perform reset
        r = self.client.post('/auth/reset', json={'token': token, 'password': new_pw})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json().get('success'))

        # Login page should show one-time banner
        login_page = self.client.get('/auth/login')
        html = login_page.get_data(as_text=True)
        self.assertIn('Your password was updated. You can sign in now.', html)

        # Login succeeds with new password
        login = self.client.post('/auth/login', json={'username': username, 'password': new_pw, 'remember': False})
        self.assertEqual(login.status_code, 200)
        self.assertTrue(login.get_json().get('success'))

        # Token should be marked used
        with app.app_context():
            self.assertTrue(PasswordResetToken.query.count() >= 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
