import os
import pyotp
import qrcode

from repository.user_repository import load_executives, save_executives

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QR_FOLDER = os.path.join(BASE_DIR, "qr_codes")

def generate_qr_for_executives():
    executives = load_executives()

    os.makedirs(QR_FOLDER, exist_ok=True)

    for executive in executives:

        if "totp_secret" not in executive or not executive["totp_secret"]:
            executive["totp_secret"] = pyotp.random_base32()
            print(f"[INFO] Secret generado para {executive['email']}")

        secret = executive["totp_secret"]
        totp = pyotp.TOTP(secret)

        uri = totp.provisioning_uri(
            name=executive["email"],
            issuer_name="TC5G Shop"
        )

        img = qrcode.make(uri)

        filename = f"{executive['name'].lower().strip().replace(" ", "_")}.png"
        filepath = os.path.join(QR_FOLDER, filename)

        img.save(filepath)

        print(f"[QR] Generado para {executive['email']} -> {filepath}")

    save_executives(executives)

if __name__ == "__main__":
    generate_qr_for_executives()