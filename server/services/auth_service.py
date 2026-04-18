import pyotp

from repository.user_repository import load_users, load_executives

def authenticate(email, password):
    users = load_users()

    for user in users:
        if user["email"] == email and user["password"] == password:
            return user
        
    return None

def authenticate_executive(email, password, code):
    executives = load_executives()

    for executive in executives:
        if executive["email"] == email and executive["password"] == password:

            totp = pyotp.TOTP(executive["totp_secret"])

            if totp.verify(code.strip(), valid_window=1):
                return executive

    return None