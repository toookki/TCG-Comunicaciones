"""
Servicio de Autenticación.
Centraliza la lógica para validar credenciales de clientes y la verificación
en dos pasos (2FA) para los ejecutivos, separando esta responsabilidad del
manejo directo de las conexiones.
"""

import pyotp

from server.repository.user_repository import load_users
from server.repository.executive_repository import load_executives

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