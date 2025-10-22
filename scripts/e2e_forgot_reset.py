import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from AjaSpellBApp import app, db
from models import User, PasswordResetToken

USERNAME = 'resetdemo'
EMAIL = 'resetdemo@example.com'
PASSWORD = 'InitialPass123'
NEW_PASSWORD = 'NewPass12345'


def main():
    with app.app_context():
        # Ensure demo user exists
        user = User.query.filter_by(username=USERNAME).first()
        if not user:
            user = User(username=USERNAME, display_name='Reset Demo', role='student', email=EMAIL)
            user.set_password(PASSWORD)
            db.session.add(user)
            db.session.commit()
            print('Created demo user')
        else:
            print('Demo user exists')

    with app.test_client() as c:
        # Request forgot-password
        r = c.post('/api/auth/forgot-password', json={'identifier': EMAIL})
        print('Forgot response:', r.status_code, r.get_json())

        # Grab latest token for the user from DB
        with app.app_context():
            user = User.query.filter_by(username=USERNAME).first()
            prt = (
                PasswordResetToken.query
                .filter_by(user_id=user.id)
                .order_by(PasswordResetToken.created_at.desc())
                .first()
            )
            if not prt:
                print('No token created; check rate-limit or email config. Exiting.')
                return
            # We only have the hash; simulate by reading the rendered reset page.
            # For e2e, we bypass and directly post with a known bad token first, then mark success path by using correct raw token.
            # In real flow, the raw token is only sent via email. For test, we temporarily expose it by fetching the reset URL from dev logs.
            # Here, we cannot retrieve raw token; so we just validate the generic behavior on invalid token:
        r2 = c.post('/auth/reset', json={'token': 'invalid_raw_token', 'password': NEW_PASSWORD})
        print('Reset invalid token ->', r2.status_code, r2.get_json())

        # Note: Full raw-token validation requires capturing the token before hashing (e.g., via a test hook or log capture).
        # This script verifies endpoints are wired and generic behavior is returned without leaking info.

if __name__ == '__main__':
    main()
